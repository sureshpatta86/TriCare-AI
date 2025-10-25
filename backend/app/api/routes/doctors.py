"""
Doctor Finder API Routes
"""
import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.schemas.doctors import DoctorSearchRequest, DoctorSearchResponse
from app.services.doctor_finder import DoctorFinderService
from app.database import get_db
from app.utils.auth import get_optional_current_user, get_current_user
from app.models.user import User
from app.models.health_record import FavoriteDoctor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/doctors", tags=["Doctor Finder"])


@router.post("/search", response_model=DoctorSearchResponse)
async def search_doctors(
    request: Request,
    search_request: DoctorSearchRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> DoctorSearchResponse:
    """
    Search for doctors based on PIN code and specialization
    
    Works with or without authentication.
    
    - **pincode**: Postal/PIN code for location search
    - **specialization**: Required medical specialization (e.g., "Cardiologist")
    - **radius_km**: Optional search radius in kilometers (default: 10km, max: 50km)
    
    Returns list of doctors with their locations, ratings, and contact information.
    """
    correlation_id = request.state.correlation_id
    logger.info(f"[{correlation_id}] Doctor search request - "
               f"PIN: {search_request.pincode}, Spec: {search_request.specialization}, authenticated: {current_user is not None}")
    
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


@router.post("/favorites/{doctor_id}")
async def add_favorite_doctor(
    doctor_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a doctor to favorites (requires authentication)
    """
    correlation_id = request.state.correlation_id
    logger.info(f"[{correlation_id}] Adding favorite doctor - user_id: {current_user.id}, doctor_id: {doctor_id}")
    
    # Check if already favorited
    existing = db.query(FavoriteDoctor).filter(
        FavoriteDoctor.user_id == current_user.id,
        FavoriteDoctor.doctor_id == doctor_id
    ).first()
    
    if existing:
        return {"message": "Doctor already in favorites", "doctor_id": doctor_id}
    
    # Add to favorites
    favorite = FavoriteDoctor(
        user_id=current_user.id,
        doctor_id=doctor_id
    )
    db.add(favorite)
    db.commit()
    
    logger.info(f"[{correlation_id}] Doctor added to favorites")
    return {"message": "Doctor added to favorites", "doctor_id": doctor_id}


@router.delete("/favorites/{doctor_id}")
async def remove_favorite_doctor(
    doctor_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a doctor from favorites (requires authentication)
    """
    correlation_id = request.state.correlation_id
    logger.info(f"[{correlation_id}] Removing favorite doctor - user_id: {current_user.id}, doctor_id: {doctor_id}")
    
    favorite = db.query(FavoriteDoctor).filter(
        FavoriteDoctor.user_id == current_user.id,
        FavoriteDoctor.doctor_id == doctor_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Doctor not found in favorites")
    
    db.delete(favorite)
    db.commit()
    
    logger.info(f"[{correlation_id}] Doctor removed from favorites")
    return {"message": "Doctor removed from favorites", "doctor_id": doctor_id}


@router.get("/favorites")
async def get_favorite_doctors(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's favorite doctors (requires authentication)
    """
    correlation_id = request.state.correlation_id
    logger.info(f"[{correlation_id}] Fetching favorite doctors - user_id: {current_user.id}")
    
    favorites = db.query(FavoriteDoctor).filter(
        FavoriteDoctor.user_id == current_user.id
    ).all()
    
    return {
        "favorites": [
            {
                "id": fav.id,
                "doctor_id": fav.doctor_id,
                "added_at": fav.created_at.isoformat()
            }
            for fav in favorites
        ],
        "total": len(favorites)
    }
