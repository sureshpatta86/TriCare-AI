"""
Pydantic schemas for X-ray/CT Pre-Screen feature.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PredictionClass(str, Enum):
    """Image classification results."""
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    UNCERTAIN = "uncertain"


class ImagingPrescreenRequest(BaseModel):
    """Request model for imaging pre-screen."""
    image_type: str = Field(..., description="Type of image (x-ray, ct, mri)")
    body_part: Optional[str] = Field(None, description="Body part imaged (chest, abdomen, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_type": "x-ray",
                "body_part": "chest"
            }
        }


class ImagingPrescreenResponse(BaseModel):
    """Response model for imaging pre-screen."""
    prediction: PredictionClass = Field(..., description="Classification result")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    explanation: str = Field(..., description="Plain language explanation of findings")
    areas_of_interest: List[str] = Field(default=[], description="Specific areas noted in image")
    recommended_next_steps: List[str] = Field(..., description="Suggested actions")
    recommended_specialist: Optional[str] = Field(None, description="Specialist to consult if abnormal")
    heatmap_available: bool = Field(default=False, description="Whether heatmap visualization is available")
    heatmap_base64: Optional[str] = Field(None, description="Base64 encoded heatmap image")
    model_used: str = Field(default="MobileNetV2", description="ML model used for inference")
    fallback_used: bool = Field(default=False, description="Whether GPT Vision fallback was used")
    disclaimer: str = Field(
        default="This is NOT a diagnostic tool. This is an educational pre-screen only. All medical imaging must be reviewed by a qualified radiologist. Do not make medical decisions based on this result.",
        description="Strong medical disclaimer"
    )
    processed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction": "abnormal",
                "confidence": 0.87,
                "explanation": "The image shows a suspicious opacity in the right lower lung field...",
                "areas_of_interest": [
                    "Right lower lobe opacity",
                    "Possible infiltrate"
                ],
                "recommended_next_steps": [
                    "Consult with a radiologist immediately",
                    "Schedule follow-up imaging if recommended",
                    "Bring images to your physician"
                ],
                "recommended_specialist": "Pulmonologist or Radiologist",
                "heatmap_available": True,
                "model_used": "MobileNetV2",
                "fallback_used": False
            }
        }
