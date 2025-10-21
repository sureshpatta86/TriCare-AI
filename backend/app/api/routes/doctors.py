"""
Doctor Finder API Routes
"""
import logging
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from app.schemas.doctors import DoctorSearchRequest, DoctorSearchResponse
from app.services.doctor_finder import DoctorFinderService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/doctors", tags=["Doctor Finder"])


@router.post("/search", response_model=DoctorSearchResponse)
async def search_doctors(
    request: Request,
    search_request: DoctorSearchRequest
) -> DoctorSearchResponse:
    """
    Search for doctors based on PIN code and specialization
    
    - **pincode**: Postal/PIN code for location search
    - **specialization**: Required medical specialization (e.g., "Cardiologist")
    - **radius_km**: Optional search radius in kilometers (default: 10km, max: 50km)
    
    Returns list of doctors with their locations, ratings, and contact information.
    """
    correlation_id = request.state.correlation_id
    logger.info(f"[{correlation_id}] Doctor search request - "
               f"PIN: {search_request.pincode}, Spec: {search_request.specialization}")
    
    try:
        # Initialize service (fixes __init__ bug by creating fresh instance per request)
        doctor_service = DoctorFinderService()
        
        # Search for doctors
        response = await doctor_service.search_doctors(search_request)
        
        logger.info(f"[{correlation_id}] Found {response.total_doctors_found} doctors")
        return response
        
    except ValueError as e:
        logger.error(f"[{correlation_id}] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[{correlation_id}] Error searching doctors: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to search for doctors. Please try again later."
        )


@router.get("/specializations")
async def get_specializations(request: Request):
    """
    Get list of available medical specializations
    """
    correlation_id = request.state.correlation_id
    logger.info(f"[{correlation_id}] Fetching specializations list")
    
    specializations = [
        "Cardiologist",
        "Neurologist",
        "Orthopedic",
        "Dermatologist",
        "Gastroenterologist",
        "Pulmonologist",
        "Endocrinologist",
        "General Physician",
        "Pediatrician",
        "Gynecologist",
        "Psychiatrist",
        "ENT Specialist",
        "Ophthalmologist",
        "Urologist",
        "Nephrologist"
    ]
    
    return {
        "specializations": sorted(specializations),
        "total": len(specializations)
    }
