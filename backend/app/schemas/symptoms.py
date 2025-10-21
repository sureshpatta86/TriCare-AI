"""
Pydantic schemas for Symptom Router feature.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UrgencyLevel(str, Enum):
    """Urgency classification levels."""
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"
    NON_URGENT = "non-urgent"


class SymptomRouteRequest(BaseModel):
    """Request model for symptom routing."""
    symptoms: str = Field(..., description="Free-text description of symptoms", min_length=10)
    age: Optional[int] = Field(None, ge=0, le=120, description="Patient age")
    sex: Optional[str] = Field(None, description="Patient sex (male/female/other)")
    duration: Optional[str] = Field(None, description="How long symptoms have lasted")
    existing_conditions: Optional[List[str]] = Field(default=[], description="Pre-existing medical conditions")
    current_medications: Optional[List[str]] = Field(default=[], description="Current medications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": "I've had a persistent cough for 2 weeks with yellow mucus and mild fever",
                "age": 35,
                "sex": "female",
                "duration": "2 weeks",
                "existing_conditions": ["asthma"],
                "current_medications": ["albuterol"]
            }
        }


class SymptomRouteResponse(BaseModel):
    """Response model for symptom routing."""
    recommended_specialist: str = Field(..., description="Type of specialist to see")
    urgency_level: UrgencyLevel = Field(..., description="Urgency classification")
    reasoning: str = Field(..., description="Plain language explanation of recommendation")
    red_flags: List[str] = Field(default=[], description="Warning signs to watch for")
    suggested_preparations: List[str] = Field(default=[], description="What to prepare for appointment")
    suggested_tests: Optional[List[str]] = Field(default=[], description="Tests that may be needed")
    home_care_tips: Optional[List[str]] = Field(default=[], description="Self-care measures")
    disclaimer: str = Field(
        default="This is educational guidance only. If you experience severe symptoms or emergency signs, seek immediate medical attention. Always consult a healthcare provider for diagnosis and treatment.",
        description="Medical disclaimer"
    )
    processed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommended_specialist": "Pulmonologist or Primary Care Physician",
                "urgency_level": "urgent",
                "reasoning": "Your persistent cough with colored mucus suggests a possible respiratory infection...",
                "red_flags": [
                    "Difficulty breathing",
                    "Chest pain",
                    "High fever above 103°F"
                ],
                "suggested_preparations": [
                    "List all symptoms and when they started",
                    "Bring your asthma inhaler",
                    "Note any triggers or patterns"
                ],
                "suggested_tests": [
                    "Chest X-ray",
                    "Sputum culture",
                    "Pulmonary function test"
                ]
            }
        }
