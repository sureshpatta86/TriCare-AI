"""
Report Simplifier Service

Uses LangChain and Azure OpenAI to simplify medical reports into plain language
with key findings, specialist recommendations, and next steps.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import logging

from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from app.services.azure_openai_service import get_azure_openai_service
from app.schemas.reports import ReportSimplifyResponse, KeyFinding

logger = logging.getLogger(__name__)


class ReportSimplifierService:
    """
    Service for simplifying medical reports using LangChain and Azure OpenAI.
    
    Takes medical text and converts it to patient-friendly language with
    structured findings and recommendations.
    """
    
    def __init__(self):
        """Initialize service with Azure OpenAI and text splitter."""
        self.azure_service = get_azure_openai_service()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    async def simplify_report(self, medical_text: str) -> ReportSimplifyResponse:
        """
        Simplify a medical report into plain language.
        
        Args:
            medical_text: Raw medical report text
            
        Returns:
            ReportSimplifyResponse: Structured simplified report
            
        Raises:
            ValueError: If text is too short or processing fails
        """
        if len(medical_text.strip()) < 50:
            raise ValueError("Medical report text is too short to process")
        
        try:
            # Split text if too long
            documents = self.text_splitter.create_documents([medical_text])
            
            if len(documents) > 1:
                logger.info(f"Report split into {len(documents)} chunks for processing")
                # Process each chunk and combine results
                simplified_data = await self._process_multi_chunk(documents)
            else:
                # Process single chunk
                simplified_data = await self._process_single_chunk(medical_text)
            
            # Build response
            response = ReportSimplifyResponse(
                summary=simplified_data["summary"],
                key_findings=[
                    KeyFinding(**finding) for finding in simplified_data["key_findings"]
                ],
                recommended_specialist=simplified_data.get("recommended_specialist"),
                next_steps=simplified_data["next_steps"],
                processed_at=datetime.now()
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error simplifying report: {str(e)}")
            raise ValueError(f"Failed to simplify report: {str(e)}")
    
    async def _process_single_chunk(self, text: str) -> Dict[str, Any]:
        """Process a single chunk of medical text."""
        system_prompt = """SYSTEM ROLE:
You are an expert medical communication specialist trained to translate complex medical reports, lab results, and diagnostic documents into clear, patient-accessible language. Your role is to bridge the gap between technical medical terminology and patient understanding while maintaining accuracy and appropriate clinical context.

CORE RESPONSIBILITIES:

1. Comprehensive Report Analysis
- Thoroughly read and parse all sections of the medical report
- Identify the report type (lab results, radiology, pathology, discharge summary, consultation notes)
- Extract all key findings, test results, measurements, and observations
- Note relationships between different findings

2. Information Extraction & Categorization
- Identify all key findings and distinguish primary from incidental observations
- Categorize findings by clinical domain and significance
- Recognize patterns and relationships between findings

3. Plain Language Translation
- Convert medical jargon into everyday language without losing accuracy
- Provide context for what tests measure and why they matter
- Explain normal ranges and what deviations mean
- Use analogies and comparisons when helpful for understanding

4. Severity Assessment & Prioritization
- Classify findings by clinical urgency: normal, abnormal, critical
- Distinguish between minor abnormalities and concerning findings
- Flag critical values that require immediate attention
- Contextualize findings within typical clinical patterns

5. Actionable Guidance
- Recommend appropriate specialists based on findings
- Provide clear, prioritized next steps
- Suggest timeframes for follow-up based on urgency
- Identify questions patients should ask their healthcare provider

COMMUNICATION PRINCIPLES:

Empathy & Tone:
- Use supportive, non-alarming language while respecting the seriousness of findings
- Balance honesty about concerning findings with appropriate reassurance
- Avoid both catastrophizing and minimizing—maintain calibrated, realistic perspective

Clarity & Accessibility:
- Write at an 8th-grade reading level
- Define any medical terms that must be used
- Use short sentences and clear organization
- Organize from most important to least important

Accuracy & Safety:
- Never alter or omit critical medical information
- Preserve numerical values and reference ranges exactly as reported
- Clearly distinguish normal, borderline, and abnormal values
- Maintain clinical context that affects interpretation

Educational Value:
- Explain the "why" behind tests and findings
- Help patients understand how findings relate to their health
- Provide context about common vs. rare findings
- Empower meaningful engagement with healthcare providers

CRITICAL SAFETY GUIDELINES:
- Never provide medical advice or treatment recommendations—only explain what the report says
- Always emphasize: This is educational information; all clinical decisions must be made with healthcare providers
- Flag urgent findings clearly using explicit language
- Avoid diagnostic conclusions: Use "consistent with" or "suggests" rather than definitive statements
- Every summary must guide patients back to their healthcare team"""

        user_message = f"""Please analyze the following medical report and provide a comprehensive, patient-friendly summary. Break down complex terminology, explain the significance of findings, and provide clear guidance on next steps.

MEDICAL REPORT:
{text}

ANALYSIS REQUIREMENTS:

1. SEVERITY CLASSIFICATION:
   - normal: Within reference ranges, no clinical concern
   - borderline: Slightly outside normal, monitoring recommended
   - mildly_abnormal: Outside normal, warrants discussion and possible lifestyle changes
   - moderately_abnormal: Clearly abnormal, likely requires medical intervention
   - severely_abnormal: Significantly outside normal, requires prompt attention
   - critical: Life-threatening values requiring immediate emergency intervention

2. PRIORITY CATEGORIZATION:
   - Critical/Urgent: Values in critical ranges, findings suggesting acute conditions, results requiring immediate intervention
   - Important/Non-Urgent: Moderately abnormal values, findings suggesting chronic conditions needing management
   - Minor/Incidental: Borderline results, common benign findings, incidental observations
   - Normal/Reassuring: Results within normal ranges, findings ruling out suspected conditions

3. LANGUAGE GUIDELINES:
   - For Normal: "Your [test] is within normal range, which is reassuring"
   - For Borderline: "This value is slightly [higher/lower] than typical range"
   - For Abnormal: "This finding indicates [condition] may be present and should be evaluated"
   - For Critical: "This is a significant finding requiring prompt medical attention"

Provide your analysis in JSON format:
{{
  "summary": "COMPREHENSIVE 2-4 paragraph plain-language summary including: (1) What type of report this is and why ordered, (2) Most important findings organized by priority (critical first, then important, minor, normal), (3) How findings relate to each other and potential health conditions, (4) Overall clinical picture, (5) What normal results would look like vs. what was found, (6) Clear bottom-line takeaway. Use empathetic, supportive language. Flag any urgent findings prominently.",
  
  "key_findings": [
    {{
      "category": "Lab Result | Imaging Finding | Vital Sign | Diagnosis | Symptom | Medication | Procedure | Incidental Finding",
      "finding": "DETAILED plain language explanation including: (1) What this finding means and measures, (2) Actual value with normal reference range (e.g., '155 mg/dL [Normal: 70-100]'), (3) Clinical significance and what it suggests about health, (4) Trend if available (improving/stable/worsening), (5) Priority level (critical-urgent/important/minor/normal). Explain in 2-3 clear sentences.",
      "original_term": "Exact medical terminology or value from the report",
      "severity": "normal | borderline | mildly_abnormal | moderately_abnormal | severely_abnormal | critical"
    }}
  ],
  
  "recommended_specialist": "Specific type of specialist (e.g., 'Cardiologist', 'Endocrinologist', 'Primary Care Physician') with urgency level: [ROUTINE/EXPEDITED/URGENT/EMERGENCY]. Include reasoning: 'Recommended because [findings indicate condition requiring this specialist]'",
  
  "next_steps": [
    "IMMEDIATE ACTIONS (if urgent): Contact provider within [timeframe] regarding [specific finding]",
    "FOLLOW-UP APPOINTMENTS: Schedule [specialist] appointment within [timeframe] to discuss [findings]",
    "ADDITIONAL TESTING: [Doctor may recommend X test] to further evaluate [finding] because [reason]",
    "LIFESTYLE/MONITORING: Watch for [symptoms], track [factors], consider [lifestyle modifications]",
    "QUESTIONS FOR DOCTOR: 'What caused [abnormal finding]?', 'What treatment options exist?', 'How often should I retest?'",
    "Include medical terminology glossary items as needed: '[Medical term] means [simple definition] and matters because [clinical relevance]'"
  ]
}}

CRITICAL REMINDERS:
- Maintain all numerical values exactly as in report
- Flag critical/urgent findings prominently using explicit language
- Use empathetic, supportive tone (8th-grade reading level)
- Provide educational context for understanding
- Strong emphasis: All findings must be discussed with healthcare provider
- Include emergency guidance if critical findings present
- Note any interpretation limitations without full clinical context"""

        schema = {
            "summary": "string",
            "key_findings": "array of objects",
            "recommended_specialist": "string or null",
            "next_steps": "array of strings"
        }
        
        result = await self.azure_service.analyze_with_structured_output(
            system_prompt=system_prompt,
            user_message=user_message,
            schema=schema
        )
        
        return result
    
    async def _process_multi_chunk(self, documents: List[Document]) -> Dict[str, Any]:
        """Process multiple chunks and combine results."""
        # Process each chunk
        chunk_results = []
        for i, doc in enumerate(documents):
            logger.info(f"Processing chunk {i+1}/{len(documents)}")
            result = await self._process_single_chunk(doc.page_content)
            chunk_results.append(result)
        
        # Combine results
        combined_summary = "\n\n".join([r["summary"] for r in chunk_results])
        all_findings = []
        for r in chunk_results:
            all_findings.extend(r["key_findings"])
        
        # Deduplicate findings by original_term
        seen_terms = set()
        unique_findings = []
        for finding in all_findings:
            term = finding.get("original_term", finding["finding"])
            if term not in seen_terms:
                seen_terms.add(term)
                unique_findings.append(finding)
        
        # Get specialist recommendation from first chunk
        specialist = chunk_results[0].get("recommended_specialist")
        
        # Combine next steps
        all_next_steps = []
        for r in chunk_results:
            all_next_steps.extend(r.get("next_steps", []))
        unique_next_steps = list(dict.fromkeys(all_next_steps))  # Remove duplicates
        
        return {
            "summary": combined_summary,
            "key_findings": unique_findings,
            "recommended_specialist": specialist,
            "next_steps": unique_next_steps[:5]  # Limit to top 5
        }


# Singleton instance
_report_simplifier: Optional[ReportSimplifierService] = None


def get_report_simplifier() -> ReportSimplifierService:
    """
    Get singleton instance of report simplifier service.
    
    Returns:
        ReportSimplifierService: Shared service instance
    """
    global _report_simplifier
    if _report_simplifier is None:
        _report_simplifier = ReportSimplifierService()
    return _report_simplifier
