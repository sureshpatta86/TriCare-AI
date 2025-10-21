"""
LangGraph Symptom Analysis Workflow

Implements a multi-step reasoning workflow for symptom analysis and specialist routing
using LangGraph state machine.
"""

from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import logging

from app.config import get_settings
from app.schemas.symptoms import UrgencyLevel

logger = logging.getLogger(__name__)
settings = get_settings()


class SymptomState(TypedDict):
    """State definition for symptom analysis workflow."""
    # Input
    symptoms: str
    age: Optional[int]
    sex: Optional[str]
    duration: Optional[str]
    existing_conditions: List[str]
    current_medications: List[str]
    
    # Intermediate state
    extracted_symptoms: List[str]
    urgency_assessment: str
    urgency_level: UrgencyLevel
    red_flags: List[str]
    
    # Output
    recommended_specialist: str
    reasoning: str
    suggested_preparations: List[str]
    suggested_tests: List[str]
    home_care_tips: List[str]


class SymptomWorkflow:
    """
    LangGraph workflow for symptom analysis and specialist routing.
    
    Implements a multi-step reasoning process:
    1. Extract and structure symptoms
    2. Assess urgency and identify red flags
    3. Determine appropriate specialist
    4. Generate recommendations and preparation tips
    """
    
    def __init__(self):
        """Initialize workflow with Azure OpenAI model."""
        self.chat_model = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=settings.azure_openai_deployment_name,
            temperature=0.3,
            max_tokens=2000,
        )
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(SymptomState)
        
        # Add nodes
        workflow.add_node("extract_symptoms", self._extract_symptoms)
        workflow.add_node("assess_urgency", self._assess_urgency)
        workflow.add_node("route_specialist", self._route_specialist)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        
        # Define edges
        workflow.set_entry_point("extract_symptoms")
        workflow.add_edge("extract_symptoms", "assess_urgency")
        workflow.add_edge("assess_urgency", "route_specialist")
        workflow.add_edge("route_specialist", "generate_recommendations")
        workflow.add_edge("generate_recommendations", END)
        
        return workflow.compile()
    
    async def _extract_symptoms(self, state: SymptomState) -> SymptomState:
        """Extract and structure symptoms from user input."""
        logger.info("Step 1: Extracting symptoms")
        
        system_prompt = """You are a medical triage assistant. Extract key symptoms from the patient's description.

List distinct, specific symptoms mentioned. Be thorough but concise.

IMPORTANT: Respond ONLY with valid JSON, no additional text."""

        patient_context = self._build_patient_context(state)
        user_message = f"""{patient_context}

Symptoms described: {state['symptoms']}

Extract a list of distinct symptoms. Respond in JSON format:
{{
  "extracted_symptoms": ["symptom 1", "symptom 2", ...]
}}"""

        response = await self.chat_model.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        # Parse response with error handling
        import json
        import re
        
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse response directly, attempting to extract JSON")
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                logger.error(f"Could not extract JSON from response: {response.content}")
                raise ValueError("Failed to parse symptom extraction response")
        
        state["extracted_symptoms"] = result.get("extracted_symptoms", [])
        logger.info(f"Extracted {len(state['extracted_symptoms'])} symptoms")
        
        return state
    
    async def _assess_urgency(self, state: SymptomState) -> SymptomState:
        """Assess urgency level and identify red flags."""
        logger.info("Step 2: Assessing urgency")
        
        system_prompt = """You are a medical triage expert. Assess the urgency of the patient's condition and identify any red flag symptoms that require immediate attention.

Urgency levels:
- emergency: Life-threatening, needs 911/ER immediately
- urgent: Needs medical attention within 24 hours
- routine: Schedule regular appointment within days/weeks
- non-urgent: Minor issue, can wait or self-manage

Red flags are symptoms that suggest serious conditions requiring immediate care.

IMPORTANT: Respond ONLY with valid JSON, no additional text."""

        patient_context = self._build_patient_context(state)
        symptoms_list = ", ".join(state["extracted_symptoms"])
        
        user_message = f"""{patient_context}

Symptoms: {symptoms_list}
Duration: {state.get('duration', 'not specified')}

Assess urgency and identify red flags. Respond in JSON:
{{
  "urgency_level": "emergency|urgent|routine|non-urgent",
  "urgency_assessment": "Brief explanation of urgency decision",
  "red_flags": ["red flag 1", "red flag 2", ...] or []
}}"""

        response = await self.chat_model.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        # Parse response with error handling
        import json
        import re
        
        try:
            # Try direct parse first
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            logger.warning("Failed to parse response directly, attempting to extract JSON")
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                logger.error(f"Could not extract JSON from response: {response.content}")
                raise ValueError("Failed to parse urgency assessment response")
        
        state["urgency_level"] = UrgencyLevel(result["urgency_level"])
        state["urgency_assessment"] = result["urgency_assessment"]
        state["red_flags"] = result.get("red_flags", [])
        
        logger.info(f"Urgency assessed: {state['urgency_level']}")
        
        return state
    
    async def _route_specialist(self, state: SymptomState) -> SymptomState:
        """Determine appropriate specialist."""
        logger.info("Step 3: Routing to specialist")
        
        system_prompt = """You are a medical routing expert. Based on symptoms and urgency, recommend the most appropriate type of healthcare provider or specialist.

Options include:
- Emergency Department (for emergencies)
- Primary Care Physician/Family Doctor
- Specialists (Cardiologist, Pulmonologist, Neurologist, Orthopedist, Dermatologist, etc.)
- Urgent Care Clinic

Provide clear reasoning for your recommendation.

IMPORTANT: Respond ONLY with valid JSON, no additional text."""

        patient_context = self._build_patient_context(state)
        symptoms_list = ", ".join(state["extracted_symptoms"])
        
        user_message = f"""{patient_context}

Symptoms: {symptoms_list}
Urgency: {state['urgency_level']}
{f"Red flags: {', '.join(state['red_flags'])}" if state['red_flags'] else "No red flags identified"}

Recommend specialist and explain why. Respond in JSON:
{{
  "recommended_specialist": "Type of specialist or provider",
  "reasoning": "Clear explanation of why this specialist is appropriate"
}}"""

        response = await self.chat_model.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        # Parse response with error handling
        import json
        import re
        
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse response directly, attempting to extract JSON")
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                logger.error(f"Could not extract JSON from response: {response.content}")
                raise ValueError("Failed to parse specialist routing response")
        
        state["recommended_specialist"] = result["recommended_specialist"]
        state["reasoning"] = result["reasoning"]
        
        logger.info(f"Specialist recommended: {state['recommended_specialist']}")
        
        return state
    
    async def _generate_recommendations(self, state: SymptomState) -> SymptomState:
        """Generate preparation tips, suggested tests, and home care advice."""
        logger.info("Step 4: Generating recommendations")
        
        system_prompt = """You are a patient care advisor. Provide practical guidance for the patient's visit and self-care.

Include:
1. What to prepare/bring to the appointment
2. Tests the doctor might order
3. Safe home care measures (if applicable)

Be specific and actionable.

IMPORTANT: Respond ONLY with valid JSON, no additional text."""

        patient_context = self._build_patient_context(state)
        symptoms_list = ", ".join(state["extracted_symptoms"])
        
        user_message = f"""{patient_context}

Symptoms: {symptoms_list}
Specialist: {state['recommended_specialist']}
Urgency: {state['urgency_level']}

Provide practical guidance. Respond in JSON:
{{
  "suggested_preparations": ["preparation 1", "preparation 2", ...],
  "suggested_tests": ["test 1", "test 2", ...],
  "home_care_tips": ["tip 1", "tip 2", ...] or []
}}"""

        response = await self.chat_model.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        # Parse response with error handling
        import json
        import re
        
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse response directly, attempting to extract JSON")
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                logger.error(f"Could not extract JSON from response: {response.content}")
                raise ValueError("Failed to parse recommendations response")
        
        state["suggested_preparations"] = result.get("suggested_preparations", [])
        state["suggested_tests"] = result.get("suggested_tests", [])
        state["home_care_tips"] = result.get("home_care_tips", [])
        
        logger.info("Recommendations generated")
        
        return state
    
    def _build_patient_context(self, state: SymptomState) -> str:
        """Build patient context string for prompts."""
        context_parts = []
        
        if state.get("age"):
            context_parts.append(f"Age: {state['age']}")
        
        if state.get("sex"):
            context_parts.append(f"Sex: {state['sex']}")
        
        if state.get("existing_conditions"):
            conditions = ", ".join(state["existing_conditions"])
            context_parts.append(f"Existing conditions: {conditions}")
        
        if state.get("current_medications"):
            meds = ", ".join(state["current_medications"])
            context_parts.append(f"Current medications: {meds}")
        
        return "Patient context:\n" + "\n".join(context_parts) if context_parts else "No additional patient context provided."
    
    async def run(self, state: SymptomState) -> SymptomState:
        """
        Execute the complete workflow.
        
        Args:
            state: Initial symptom state
            
        Returns:
            SymptomState: Final state with recommendations
        """
        logger.info("Starting symptom analysis workflow")
        result = await self.workflow.ainvoke(state)
        logger.info("Workflow completed successfully")
        return result


# Singleton instance
_symptom_workflow: Optional[SymptomWorkflow] = None


def get_symptom_workflow() -> SymptomWorkflow:
    """
    Get singleton instance of symptom workflow.
    
    Returns:
        SymptomWorkflow: Shared workflow instance
    """
    global _symptom_workflow
    if _symptom_workflow is None:
        _symptom_workflow = SymptomWorkflow()
    return _symptom_workflow
