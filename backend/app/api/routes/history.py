"""
Health history API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.health_record import (
    ReportHistory, SymptomHistory, ImagingHistory, FavoriteDoctor
)
from app.schemas.history import (
    ReportHistoryCreate, ReportHistoryResponse,
    SymptomHistoryCreate, SymptomHistoryResponse,
    ImagingHistoryCreate, ImagingHistoryResponse,
    FavoriteDoctorCreate, FavoriteDoctorUpdate, FavoriteDoctorResponse,
    DashboardStats
)
from app.utils.auth import get_current_user

router = APIRouter()


# Report History Routes
@router.post("/reports", response_model=ReportHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_report_history(
    report: ReportHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a report analysis to history"""
    new_report = ReportHistory(
        user_id=current_user.id,
        **report.dict()
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


@router.get("/reports", response_model=List[ReportHistoryResponse])
async def get_report_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's report history"""
    reports = db.query(ReportHistory).filter(
        ReportHistory.user_id == current_user.id
    ).order_by(ReportHistory.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.get("/reports/{report_id}", response_model=ReportHistoryResponse)
async def get_report_by_id(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific report by ID"""
    report = db.query(ReportHistory).filter(
        ReportHistory.id == report_id,
        ReportHistory.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a report from history"""
    report = db.query(ReportHistory).filter(
        ReportHistory.id == report_id,
        ReportHistory.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully"}


# Symptom History Routes
@router.post("/symptoms", response_model=SymptomHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_symptom_history(
    symptom: SymptomHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a symptom analysis to history"""
    new_symptom = SymptomHistory(
        user_id=current_user.id,
        **symptom.dict()
    )
    db.add(new_symptom)
    db.commit()
    db.refresh(new_symptom)
    return new_symptom


@router.get("/symptoms", response_model=List[SymptomHistoryResponse])
async def get_symptom_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's symptom history"""
    symptoms = db.query(SymptomHistory).filter(
        SymptomHistory.user_id == current_user.id
    ).order_by(SymptomHistory.created_at.desc()).offset(skip).limit(limit).all()
    return symptoms


@router.get("/symptoms/{symptom_id}", response_model=SymptomHistoryResponse)
async def get_symptom_by_id(
    symptom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific symptom record by ID"""
    symptom = db.query(SymptomHistory).filter(
        SymptomHistory.id == symptom_id,
        SymptomHistory.user_id == current_user.id
    ).first()
    
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom record not found")
    
    return symptom


@router.delete("/symptoms/{symptom_id}")
async def delete_symptom(
    symptom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a symptom record from history"""
    symptom = db.query(SymptomHistory).filter(
        SymptomHistory.id == symptom_id,
        SymptomHistory.user_id == current_user.id
    ).first()
    
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom record not found")
    
    db.delete(symptom)
    db.commit()
    return {"message": "Symptom record deleted successfully"}


# Imaging History Routes
@router.post("/imaging", response_model=ImagingHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_imaging_history(
    imaging: ImagingHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save an imaging analysis to history"""
    new_imaging = ImagingHistory(
        user_id=current_user.id,
        **imaging.dict()
    )
    db.add(new_imaging)
    db.commit()
    db.refresh(new_imaging)
    return new_imaging


@router.get("/imaging", response_model=List[ImagingHistoryResponse])
async def get_imaging_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's imaging history"""
    imaging = db.query(ImagingHistory).filter(
        ImagingHistory.user_id == current_user.id
    ).order_by(ImagingHistory.created_at.desc()).offset(skip).limit(limit).all()
    return imaging


@router.get("/imaging/{imaging_id}", response_model=ImagingHistoryResponse)
async def get_imaging_by_id(
    imaging_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific imaging record by ID"""
    imaging = db.query(ImagingHistory).filter(
        ImagingHistory.id == imaging_id,
        ImagingHistory.user_id == current_user.id
    ).first()
    
    if not imaging:
        raise HTTPException(status_code=404, detail="Imaging record not found")
    
    return imaging


@router.delete("/imaging/{imaging_id}")
async def delete_imaging(
    imaging_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an imaging record from history"""
    imaging = db.query(ImagingHistory).filter(
        ImagingHistory.id == imaging_id,
        ImagingHistory.user_id == current_user.id
    ).first()
    
    if not imaging:
        raise HTTPException(status_code=404, detail="Imaging record not found")
    
    db.delete(imaging)
    db.commit()
    return {"message": "Imaging record deleted successfully"}


# Favorite Doctors Routes
@router.post("/doctors/favorites", response_model=FavoriteDoctorResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite_doctor(
    doctor: FavoriteDoctorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a doctor to favorites"""
    # Check if already favorited
    existing = db.query(FavoriteDoctor).filter(
        FavoriteDoctor.user_id == current_user.id,
        FavoriteDoctor.doctor_id == doctor.doctor_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Doctor already in favorites"
        )
    
    new_favorite = FavoriteDoctor(
        user_id=current_user.id,
        **doctor.dict()
    )
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite


@router.get("/doctors/favorites", response_model=List[FavoriteDoctorResponse])
async def get_favorite_doctors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's favorite doctors"""
    favorites = db.query(FavoriteDoctor).filter(
        FavoriteDoctor.user_id == current_user.id
    ).order_by(FavoriteDoctor.created_at.desc()).all()
    return favorites


@router.put("/doctors/favorites/{favorite_id}", response_model=FavoriteDoctorResponse)
async def update_favorite_doctor(
    favorite_id: int,
    update_data: FavoriteDoctorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update favorite doctor information"""
    favorite = db.query(FavoriteDoctor).filter(
        FavoriteDoctor.id == favorite_id,
        FavoriteDoctor.user_id == current_user.id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite doctor not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(favorite, field, value)
    
    db.commit()
    db.refresh(favorite)
    return favorite


@router.delete("/doctors/favorites/{favorite_id}")
async def remove_favorite_doctor(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a doctor from favorites"""
    favorite = db.query(FavoriteDoctor).filter(
        FavoriteDoctor.id == favorite_id,
        FavoriteDoctor.user_id == current_user.id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite doctor not found")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Doctor removed from favorites"}


# Dashboard Route
@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics and recent activity"""
    # Count totals
    total_reports = db.query(ReportHistory).filter(
        ReportHistory.user_id == current_user.id
    ).count()
    
    total_symptoms = db.query(SymptomHistory).filter(
        SymptomHistory.user_id == current_user.id
    ).count()
    
    total_imaging = db.query(ImagingHistory).filter(
        ImagingHistory.user_id == current_user.id
    ).count()
    
    favorite_doctors_count = db.query(FavoriteDoctor).filter(
        FavoriteDoctor.user_id == current_user.id
    ).count()
    
    # Get recent items (last 5 of each)
    recent_reports = db.query(ReportHistory).filter(
        ReportHistory.user_id == current_user.id
    ).order_by(ReportHistory.created_at.desc()).limit(5).all()
    
    recent_symptoms = db.query(SymptomHistory).filter(
        SymptomHistory.user_id == current_user.id
    ).order_by(SymptomHistory.created_at.desc()).limit(5).all()
    
    recent_imaging = db.query(ImagingHistory).filter(
        ImagingHistory.user_id == current_user.id
    ).order_by(ImagingHistory.created_at.desc()).limit(5).all()
    
    return DashboardStats(
        total_reports=total_reports,
        total_symptoms=total_symptoms,
        total_imaging=total_imaging,
        favorite_doctors_count=favorite_doctors_count,
        recent_reports=recent_reports,
        recent_symptoms=recent_symptoms,
        recent_imaging=recent_imaging
    )
