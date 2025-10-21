"""
Pydantic schemas for Medical Report Simplifier feature.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReportSimplifyRequest(BaseModel):
    """Request model for medical report simplification."""
    text: Optional[str] = Field(None, description="Direct text input of medical report")
    file_name: Optional[str] = Field(None, description="Name of uploaded file")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Patient presents with elevated WBC count of 15,000...",
                "file_name": "lab_report.pdf"
            }
        }


class KeyFinding(BaseModel):
    """Individual key finding from report."""
    category: str = Field(..., description="Category of finding (e.g., 'Lab Result', 'Diagnosis')")
    finding: str = Field(..., description="Plain language description")
    original_term: Optional[str] = Field(None, description="Original medical terminology")
    severity: Optional[str] = Field(None, description="Severity level (normal/abnormal/critical)")


class ReportSimplifyResponse(BaseModel):
    """Response model for simplified medical report."""
    summary: str = Field(..., description="Plain language summary of the report")
    key_findings: List[KeyFinding] = Field(..., description="List of key findings")
    recommended_specialist: Optional[str] = Field(None, description="Specialist to consult")
    next_steps: List[str] = Field(..., description="Recommended next steps")
    disclaimer: str = Field(
        default="This is an educational summary only. Not a diagnostic tool. Always consult a licensed healthcare provider.",
        description="Medical disclaimer"
    )
    processed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": "Your blood test shows some values outside the normal range...",
                "key_findings": [
                    {
                        "category": "Lab Result",
                        "finding": "White blood cell count is elevated",
                        "original_term": "WBC: 15,000/μL",
                        "severity": "abnormal"
                    }
                ],
                "recommended_specialist": "Primary Care Physician or Internist",
                "next_steps": [
                    "Schedule follow-up with your doctor",
                    "Bring the original report to your appointment"
                ]
            }
        }
