"""
Health records models for storing user medical history
"""
from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class HealthRecord(Base):
    """Base health record model"""
    
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_type = Column(String, nullable=False)  # report, symptom, imaging, vital
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReportHistory(Base):
    """Medical report analysis history"""
    
    __tablename__ = "report_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Original input
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    original_text = Column(Text, nullable=True)
    
    # AI Analysis results
    summary = Column(Text, nullable=False)
    key_findings = Column(JSON, nullable=True)  # List of findings
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    specialist_needed = Column(String, nullable=True)
    urgency_level = Column(String, nullable=True)
    
    # Metadata
    correlation_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SymptomHistory(Base):
    """Symptom analysis history"""
    
    __tablename__ = "symptom_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Input data
    symptoms = Column(Text, nullable=False)
    duration = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    
    # Patient context
    age = Column(Integer, nullable=True)
    sex = Column(String, nullable=True)
    chronic_diseases = Column(JSON, nullable=True)
    current_medications = Column(JSON, nullable=True)
    
    # AI Analysis results
    extracted_symptoms = Column(JSON, nullable=True)
    urgency_level = Column(String, nullable=False)
    specialist_recommendation = Column(String, nullable=False)
    reasoning = Column(Text, nullable=True)
    red_flags = Column(JSON, nullable=True)
    suggested_tests = Column(JSON, nullable=True)
    self_care_advice = Column(JSON, nullable=True)
    
    # Metadata
    correlation_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ImagingHistory(Base):
    """Medical imaging analysis history"""
    
    __tablename__ = "imaging_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Input data
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    body_part = Column(String, nullable=True)
    
    # AI Analysis results
    prediction = Column(String, nullable=False)  # normal, abnormal
    confidence = Column(Float, nullable=False)
    findings = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Image storage (base64 or file path)
    original_image = Column(Text, nullable=True)
    heatmap_image = Column(Text, nullable=True)
    
    # Metadata
    model_used = Column(String, nullable=True)
    correlation_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FavoriteDoctor(Base):
    """Saved/favorite doctors"""
    
    __tablename__ = "favorite_doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Doctor information
    doctor_id = Column(String, nullable=False)
    doctor_name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    clinic_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    last_visit = Column(DateTime(timezone=True), nullable=True)
    next_appointment = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
