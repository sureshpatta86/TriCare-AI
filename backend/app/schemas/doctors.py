"""
Pydantic schemas for Doctor Finder feature
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class DoctorSearchRequest(BaseModel):
    """Request schema for searching doctors"""
    pincode: str = Field(..., min_length=5, max_length=10, description="Postal/PIN code")
    specialization: Optional[str] = Field(default=None, description="Medical specialization (optional - shows all doctors if not specified)")
    radius_km: Optional[float] = Field(default=10.0, ge=1.0, le=50.0, description="Search radius in kilometers")
    limit: Optional[int] = Field(default=50, ge=1, le=200, description="Maximum number of results to return (default: 50, max: 200)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pincode": "560001",
                "specialization": "Cardiologist",
                "radius_km": 10.0,
                "limit": 50
            }
        }


class DoctorLocation(BaseModel):
    """Location information for a doctor"""
    latitude: float
    longitude: float
    address: str
    city: str
    state: str
    pincode: str


class Doctor(BaseModel):
    """Doctor information"""
    id: str
    name: str
    specialization: str
    qualification: str
    experience_years: int
    rating: float = Field(ge=0.0, le=5.0)
    location: DoctorLocation
    distance_km: float
    phone: str
    email: Optional[str] = None
    clinic_name: str
    consultation_fee: Optional[float] = None
    available_days: List[str]
    available_hours: str
    languages: List[str]


class DoctorSearchResponse(BaseModel):
    """Response schema for doctor search"""
    user_location: dict
    search_radius_km: float
    specialization: Optional[str] = None
    total_doctors_found: int
    doctors: List[Doctor]
    processed_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_location": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "address": "Bangalore, Karnataka"
                },
                "search_radius_km": 10.0,
                "specialization": "Cardiologist",
                "total_doctors_found": 5,
                "doctors": [],
                "processed_at": "2025-10-21T10:30:00Z"
            }
        }
