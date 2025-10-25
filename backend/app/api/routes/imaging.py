"""
Imaging Pre-Screen API Routes

Endpoints for X-ray/CT image analysis and pre-screening.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from typing import Optional
import logging
import json

from app.schemas.imaging import ImagingPrescreenRequest, ImagingPrescreenResponse
from app.services.imaging_analyzer import get_imaging_analyzer
from app.config import get_settings
from app.database import get_db
from app.utils.auth import get_optional_current_user
from app.models.user import User
from app.models.health_record import ImagingHistory

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)


@router.post("/prescreen", response_model=ImagingPrescreenResponse)
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute
async def prescreen_medical_image(
    request: Request,
    file: UploadFile = File(...),
    image_type: str = Form(...),
    body_part: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze medical image (X-ray, CT, MRI) and provide preliminary findings.
    
    Rate limit: 10 requests per minute per IP address.
    Works with or without authentication. If authenticated, saves to history.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.info(f"Imaging prescreen request - correlation_id: {correlation_id}, image_type: {image_type}, authenticated: {current_user is not None}")
    
    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB
        logger.warning(f"File too large - correlation_id: {correlation_id}, size: {len(contents)}")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit. Please upload a smaller image."
        )
    
    # Validate file type using file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.dcm', '.dicom']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        logger.warning(f"Invalid file type - correlation_id: {correlation_id}, filename: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Please upload: {', '.join(allowed_extensions)}"
        )
    
    # Reset file pointer for processing
    await file.seek(0)
    # Validate image type
    valid_types = ["x-ray", "ct", "mri"]
    if image_type.lower() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Validate file type
    allowed_extensions = [".png", ".jpg", ".jpeg", ".dcm", ".dicom"]
    file_ext = f".{file.filename.split('.')[-1].lower()}"
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        # Validate file size
        if file_size_mb > settings.max_file_size_mb:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {settings.max_file_size_mb}MB limit"
            )
        
        logger.info(
            f"Processing medical image: {file.filename}, "
            f"type: {image_type}, body_part: {body_part}"
        )
        
        # Handle DICOM files
        if file_ext in [".dcm", ".dicom"]:
            file_content = await _convert_dicom_to_png(file_content)
        
        # Analyze image
        analyzer = get_imaging_analyzer()
        result = await analyzer.analyze_image(
            image_data=file_content,
            image_type=image_type,
            body_part=body_part
        )
        
        # Save to history if user is authenticated
        if current_user:
            try:
                # Convert areas_of_interest list to text
                findings_text = "\n".join(result.areas_of_interest) if result.areas_of_interest else None
                
                history_entry = ImagingHistory(
                    user_id=current_user.id,
                    file_name=file.filename,
                    file_type=image_type,
                    body_part=body_part,
                    prediction=result.prediction.value,
                    confidence=result.confidence,
                    findings=findings_text,
                    explanation=result.explanation,
                    recommendations=json.dumps(result.recommended_next_steps),
                    model_used=result.model_used,
                    correlation_id=correlation_id
                )
                db.add(history_entry)
                db.commit()
                logger.info(f"Saved imaging to history - user_id: {current_user.id}, correlation_id: {correlation_id}")
            except Exception as e:
                logger.error(f"Failed to save imaging history: {str(e)}")
                # Don't fail the request if history save fails
                db.rollback()
        
        logger.info(
            f"Image analysis complete: {result.prediction.value} "
            f"(confidence: {result.confidence:.2%})"
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process medical image. Please try again."
        )


@router.get("/supported-formats")
async def get_supported_image_formats():
    """
    Get list of supported image formats and types.
    
    Returns:
        dict: Supported formats, types, and file size limits
    """
    return {
        "supported_file_formats": [
            "PNG (.png)",
            "JPEG (.jpg, .jpeg)",
            "DICOM (.dcm, .dicom)"
        ],
        "supported_imaging_types": [
            {
                "type": "x-ray",
                "description": "Chest X-rays, extremity X-rays",
                "ml_model_available": True
            },
            {
                "type": "ct",
                "description": "CT scans (computed tomography)",
                "ml_model_available": False,
                "note": "Uses GPT Vision analysis"
            },
            {
                "type": "mri",
                "description": "MRI scans (magnetic resonance imaging)",
                "ml_model_available": False,
                "note": "Uses GPT Vision analysis"
            }
        ],
        "max_file_size_mb": settings.max_file_size_mb,
        "important_disclaimer": "This is NOT a diagnostic tool. Educational use only. Always consult a radiologist."
    }


async def _convert_dicom_to_png(dicom_data: bytes) -> bytes:
    """
    Convert DICOM file to PNG format.
    
    Args:
        dicom_data: Raw DICOM file bytes
        
    Returns:
        bytes: PNG image bytes
    """
    try:
        import pydicom
        from PIL import Image
        import numpy as np
        import io
        
        # Read DICOM
        dicom = pydicom.dcmread(io.BytesIO(dicom_data))
        
        # Get pixel array
        pixel_array = dicom.pixel_array
        
        # Normalize to 0-255
        pixel_array = pixel_array.astype(float)
        pixel_array = ((pixel_array - pixel_array.min()) / 
                      (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
        
        # Convert to PIL Image
        image = Image.fromarray(pixel_array)
        
        # Convert to RGB if grayscale
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save as PNG
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        
        return buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Error converting DICOM: {str(e)}")
        raise ValueError(f"Failed to process DICOM file: {str(e)}")
