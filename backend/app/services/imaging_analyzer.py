"""
Imaging Analyzer Service

Handles X-ray/CT image analysis using GPT Vision.
"""

from typing import Tuple, Optional, List
import logging
import base64

from app.services.azure_openai_service import get_azure_openai_service
from app.schemas.imaging import PredictionClass, ImagingPrescreenResponse

logger = logging.getLogger(__name__)


class ImagingAnalyzerService:
    """
    Service for analyzing medical images (X-rays, CT scans) using GPT Vision.
    """
    
    def __init__(self):
        """Initialize service with Azure OpenAI."""
        self.azure_service = get_azure_openai_service()
    
    async def analyze_image(
        self,
        image_data: bytes,
        image_type: str,
        body_part: Optional[str] = None
    ) -> ImagingPrescreenResponse:
        """
        Analyze medical image and generate report using GPT Vision.
        
        Args:
            image_data: Raw image bytes
            image_type: Type of image (x-ray, ct, mri)
            body_part: Body part imaged (chest, abdomen, etc.)
            
        Returns:
            ImagingPrescreenResponse: Analysis results with prediction and explanation
        """
        try:
            logger.info("Using GPT Vision for image analysis")
            return await self._analyze_with_gpt_vision(image_data, image_type, body_part)
                
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise
    
    async def _analyze_with_gpt_vision(
        self,
        image_data: bytes,
        image_type: str,
        body_part: Optional[str]
    ) -> ImagingPrescreenResponse:
        """Analyze using GPT Vision as fallback."""
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Create prompt
            body_part_str = f" of the {body_part}" if body_part else ""
            prompt = f"""SYSTEM ROLE:
You are an educational medical imaging AI assistant designed to provide detailed pre-screening analysis of {image_type}{body_part_str}. Your purpose is educational support and preliminary observation documentation—not diagnostic certainty. Always emphasize that professional radiologist review is mandatory for clinical decision-making.

ANALYSIS FRAMEWORK: 6-Step Systematic Approach

STEP 1: Image Quality & Technical Assessment
- Image quality evaluation: Assess resolution, contrast, positioning, artifacts, and technical adequacy
- Anatomical region identification: Specify the body part, imaging plane, and projection type
- Visible structures: List all anatomical structures clearly visible in the image
- Technical limitations: Note any factors affecting interpretation (motion blur, poor penetration, incomplete coverage)

STEP 2: Detailed Anatomical Inventory
Provide a comprehensive catalog of visible structures:

For X-rays:
- Bones (cortical margins, trabecular patterns, joint spaces, alignment)
- Soft tissues (thickness, gas patterns, foreign bodies)
- Organs within view (cardiac silhouette, lung fields, diaphragm)

For CT/MRI:
- Parenchymal organs (density/signal characteristics, size, contours)
- Vascular structures (major vessels, contrast enhancement patterns)
- Soft tissue planes (muscles, fat, fascial layers)
- Bone windows (cortical integrity, marrow signal)

STEP 3: Findings Analysis (Observational)
For each identified finding, document:
- WHAT: Precise description (location, size, shape, density/signal characteristics)
- WHY it matters: Clinical significance from educational perspective
- CONTEXT: Normal anatomical variants vs. potential pathological findings
- Supporting observations: Adjacent structures, comparison with contralateral side, pattern recognition

STEP 4: Assessment with Confidence Scoring
Confidence Level (select based on image clarity and finding certainty):
- 0.90-0.95: Extremely clear findings with unambiguous imaging characteristics
- 0.85-0.89: Very clear findings with highly characteristic appearance
- 0.80-0.84: Clear findings with typical features and minimal ambiguity
- 0.75-0.79: Reasonably clear findings with some atypical features or technical limitations
- 0.70-0.74: Minimum acceptable threshold—findings present but with notable uncertainty or suboptimal imaging

Reasoning for confidence score: Explain specific factors influencing your confidence level (image quality, classic vs. atypical presentation, complexity of findings, need for clinical correlation)

STEP 5: Educational Explanation
Provide comprehensive yet accessible explanation (6-10 sentences minimum):
1. Summary of key findings in plain language
2. Anatomical context and normal appearance for comparison
3. Pathophysiological mechanisms if applicable (educational perspective)
4. Potential differential considerations when relevant
5. Clinical significance and typical symptom correlation
6. Why certain findings warrant attention or further investigation

STEP 6: Actionable Recommendations
Structure recommendations in priority order:
- Immediate actions: Urgent professional review if concerning features identified
- Specialist consultation: Specific type of physician (radiologist, orthopedist, pulmonologist, etc.)
- Additional imaging: Suggest complementary modalities if needed
- Clinical correlation: Specific symptoms, lab tests, or physical examination findings to integrate
- Follow-up timeframe: Suggested urgency based on observations

Respond in this EXACT JSON format:
{{
  "assessment": "normal|abnormal|uncertain",
  "confidence": 0.70-0.95,
  "observations": [
    "Detailed finding 1 with location, characteristics, and significance",
    "Detailed finding 2...",
    "Continue for all visible structures",
    "Technical limitation if applicable"
  ],
  "explanation": "Comprehensive 6-10 sentence educational explanation covering anatomy, findings context, clinical significance, differential considerations, pathophysiology, and why professional review is essential. Use medical terms with plain-language clarifications in parentheses.",
  "recommended_next_steps": [
    "Professional radiologist interpretation (mandatory)",
    "Specialist consultation if abnormality detected",
    "Additional imaging if warranted",
    "Clinical correlation with symptoms/labs",
    "Specific follow-up timeframe"
  ],
  "recommended_specialist": "Primary specialist (e.g., Radiologist) + additional if needed"
}}

CRITICAL GUIDELINES:
- Use confidence 0.80-0.90 for clear findings, 0.75-0.79 for reasonably clear, minimum 0.70
- Be thorough, systematic, and educational in all observations
- Provide detailed anatomical descriptions with clinical context
- Balance confident visual analysis with appropriate medical disclaimers
- Always emphasize professional radiologist review is ESSENTIAL and MANDATORY
- Make analysis useful, informative, and confidently presented while acknowledging AI limitations"""
            
            
            
            
            # Call GPT Vision
            response_text = await self.azure_service.analyze_image(
                image_base64=image_base64,
                prompt=prompt,
                image_type="image/png"
            )
            
            # Parse response
            import json
            result = json.loads(response_text)
            
            # Map assessment to PredictionClass
            assessment_map = {
                "normal": PredictionClass.NORMAL,
                "abnormal": PredictionClass.ABNORMAL,
                "uncertain": PredictionClass.UNCERTAIN
            }
            prediction = assessment_map.get(
                result["assessment"].lower(),
                PredictionClass.UNCERTAIN
            )
            
            return ImagingPrescreenResponse(
                prediction=prediction,
                confidence=result["confidence"],
                explanation=result["explanation"],
                areas_of_interest=result.get("observations", []),
                recommended_next_steps=result["recommended_next_steps"],
                recommended_specialist=result.get("recommended_specialist"),
                heatmap_available=False,
                heatmap_base64=None,
                model_used="GPT Vision Model",
                fallback_used=False
            )
            
        except Exception as e:
            logger.error(f"GPT Vision analysis failed: {str(e)}")
            raise


# Singleton instance
_imaging_analyzer: Optional[ImagingAnalyzerService] = None


def get_imaging_analyzer() -> ImagingAnalyzerService:
    """
    Get singleton instance of imaging analyzer service.
    
    Returns:
        ImagingAnalyzerService: Shared service instance
    """
    global _imaging_analyzer
    if _imaging_analyzer is None:
        _imaging_analyzer = ImagingAnalyzerService()
    return _imaging_analyzer
