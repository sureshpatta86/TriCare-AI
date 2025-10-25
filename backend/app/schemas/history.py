"""
Health history schemas
"""
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from datetime import datetime
import json


class ReportHistoryCreate(BaseModel):
    """Create report history entry"""
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    original_text: Optional[str] = None
    summary: str
    key_findings: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    specialist_needed: Optional[str] = None
    urgency_level: Optional[str] = None
    correlation_id: Optional[str] = None


class ReportHistoryResponse(ReportHistoryCreate):
    """Report history response"""
    id: int
    user_id: int
    created_at: datetime
    
    @field_validator('key_findings', 'recommendations', mode='before')
    @classmethod
    def parse_json_field(cls, v):
        """Parse JSON string fields to lists"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v if v is not None else []
    
    class Config:
        from_attributes = True


class SymptomHistoryCreate(BaseModel):
    """Create symptom history entry"""
    symptoms: str
    duration: Optional[str] = None
    severity: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    chronic_diseases: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    extracted_symptoms: Optional[List[str]] = None
    urgency_level: str
    specialist_recommendation: str
    reasoning: Optional[str] = None
    red_flags: Optional[List[str]] = None
    suggested_tests: Optional[List[str]] = None
    self_care_advice: Optional[List[str]] = None
    correlation_id: Optional[str] = None


class SymptomHistoryResponse(SymptomHistoryCreate):
    """Symptom history response"""
    id: int
    user_id: int
    created_at: datetime
    
    @field_validator('chronic_diseases', 'current_medications', 'extracted_symptoms', 'red_flags', 'suggested_tests', 'self_care_advice', mode='before')
    @classmethod
    def parse_json_field(cls, v):
        """Parse JSON string fields to lists"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v if v is not None else []
    
    class Config:
        from_attributes = True


class ImagingHistoryCreate(BaseModel):
    """Create imaging history entry"""
    file_name: str
    file_type: str
    body_part: Optional[str] = None
    prediction: str
    confidence: float
    findings: Optional[str] = None
    explanation: Optional[str] = None
    recommendations: Optional[List[str]] = None
    original_image: Optional[str] = None
    heatmap_image: Optional[str] = None
    model_used: Optional[str] = None
    correlation_id: Optional[str] = None


class ImagingHistoryResponse(ImagingHistoryCreate):
    """Imaging history response"""
    id: int
    user_id: int
    created_at: datetime
    
    @field_validator('recommendations', mode='before')
    @classmethod
    def parse_json_field(cls, v):
        """Parse JSON string fields to lists"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v if v is not None else []
    
    class Config:
        from_attributes = True


class FavoriteDoctorCreate(BaseModel):
    """Create favorite doctor entry"""
    doctor_id: str
    doctor_name: str
    specialization: str
    clinic_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class FavoriteDoctorUpdate(BaseModel):
    """Update favorite doctor entry"""
    notes: Optional[str] = None
    last_visit: Optional[datetime] = None
    next_appointment: Optional[datetime] = None


class FavoriteDoctorResponse(BaseModel):
    """Favorite doctor response"""
    id: int
    user_id: int
    doctor_id: str
    doctor_name: str
    specialization: str
    clinic_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    last_visit: Optional[datetime] = None
    next_appointment: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_reports: int
    total_symptoms: int
    total_imaging: int
    favorite_doctors_count: int
    recent_reports: List[ReportHistoryResponse]
    recent_symptoms: List[SymptomHistoryResponse]
    recent_imaging: List[ImagingHistoryResponse]
