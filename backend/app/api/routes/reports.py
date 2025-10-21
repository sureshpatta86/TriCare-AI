"""
Report Simplification API Routes

Endpoints for converting complex medical reports into plain language.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.schemas.reports import ReportSimplifyResponse
from app.services.report_simplifier import get_report_simplifier
from app.services.document_processor import DocumentProcessor
from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)


@router.post("/simplify", response_model=ReportSimplifyResponse)
@limiter.limit("20/minute")
async def simplify_report(
    request: Request,
    file: UploadFile = File(...)
):
    """
    Convert a complex medical report into patient-friendly language.
    
    Rate limit: 20 requests per minute per IP address.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.info(f"Report simplify request - correlation_id: {correlation_id}, filename: {file.filename}")
    
    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        logger.warning(f"Report file too large - correlation_id: {correlation_id}, size: {len(contents)}")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 5MB limit. Please upload a smaller document."
        )
    
    # Validate file type
    allowed_extensions = ['.txt', '.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        logger.warning(f"Invalid report file type - correlation_id: {correlation_id}, filename: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Please upload: {', '.join(allowed_extensions)}"
        )
    
    await file.seek(0)
    
    try:
        # Extract text from file
        doc_processor = DocumentProcessor()
        
        if file.filename.lower().endswith('.pdf'):
            text = await doc_processor.extract_text_from_pdf(contents)
        elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            text = await doc_processor.extract_text_from_image(contents)
        elif file.filename.lower().endswith(('.txt', '.doc', '.docx')):
            # For text files, decode directly
            text = contents.decode('utf-8')
        else:
            raise ValueError("Unsupported file type")
        
        # Simplify the extracted text
        simplifier = get_report_simplifier()
        result = await simplifier.simplify_report(text)
        
        logger.info(f"Report simplification successful - correlation_id: {correlation_id}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error - correlation_id: {correlation_id}, error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error simplifying report - correlation_id: {correlation_id}, error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to simplify report. Please try again or contact support."
        )
