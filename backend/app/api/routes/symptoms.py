"""
Symptom Router API Routes

Endpoints for symptom analysis and specialist routing.
"""

from fastapi import APIRouter, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.schemas.symptoms import SymptomRouteRequest, SymptomRouteResponse
from app.graphs.symptom_workflow import get_symptom_workflow

router = APIRouter()
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("/route", response_model=SymptomRouteResponse)
@limiter.limit("30/minute")  # Rate limit: 30 requests per minute
async def route_symptoms(
    request: Request,
    symptom_request: SymptomRouteRequest
):
    """
    Analyze symptoms and route to appropriate specialist.
    
    Rate limit: 30 requests per minute per IP address.
    
    Uses LangGraph workflow to:
    1. Extract and structure symptoms
    2. Assess urgency and identify red flags
    3. Recommend appropriate specialist
    4. Generate preparation tips and suggestions
    
    Args:
        request: FastAPI request object (for correlation ID)
        symptom_request: Symptom routing request with symptoms and patient context
        
    Returns:
        SymptomRouteResponse: Specialist recommendation with reasoning
        
    Raises:
        HTTPException: If processing fails
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.info(f"Processing symptom routing request - correlation_id: {correlation_id}")
    
    try:
        # Initialize workflow state
        initial_state = {
            "symptoms": symptom_request.symptoms,
            "age": symptom_request.age,
            "sex": symptom_request.sex,
            "duration": symptom_request.duration,
            "existing_conditions": symptom_request.existing_conditions or [],
            "current_medications": symptom_request.current_medications or [],
        }
        
        # Run workflow
        workflow = get_symptom_workflow()
        result = await workflow.run(initial_state)
        
        # Build response
        response = SymptomRouteResponse(
            recommended_specialist=result["recommended_specialist"],
            urgency_level=result["urgency_level"],
            reasoning=result["reasoning"],
            red_flags=result.get("red_flags", []),
            suggested_preparations=result.get("suggested_preparations", []),
            suggested_tests=result.get("suggested_tests", []),
            home_care_tips=result.get("home_care_tips", [])
        )
        
        logger.info(f"Symptom routing completed - correlation_id: {correlation_id}, specialist: {response.recommended_specialist}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error - correlation_id: {correlation_id}, error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error routing symptoms - correlation_id: {correlation_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process symptoms. Please try again."
        )


@router.get("/urgency-levels")
async def get_urgency_levels():
    """
    Get information about urgency level classifications.
    
    Returns:
        dict: Urgency levels with descriptions and response times
    """
    return {
        "urgency_levels": [
            {
                "level": "emergency",
                "description": "Life-threatening condition requiring immediate care",
                "action": "Call 911 or go to Emergency Department immediately",
                "timeframe": "Immediate (minutes)"
            },
            {
                "level": "urgent",
                "description": "Serious condition requiring prompt medical attention",
                "action": "See doctor within 24 hours or visit Urgent Care",
                "timeframe": "Within 24 hours"
            },
            {
                "level": "routine",
                "description": "Non-emergency condition that should be evaluated",
                "action": "Schedule regular appointment with appropriate provider",
                "timeframe": "Within days to weeks"
            },
            {
                "level": "non-urgent",
                "description": "Minor issue that may resolve on its own",
                "action": "Monitor symptoms, schedule appointment if persists",
                "timeframe": "As needed"
            }
        ],
        "important_note": "This is educational guidance only. If you're unsure about your symptoms, always err on the side of caution and seek medical advice."
    }
