"""
Document Processor Service

Handles extraction of text from various document formats including PDF,
images (via OCR), and plain text.
"""

import PyPDF2
import pytesseract
from PIL import Image
from io import BytesIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Service for extracting text from various document formats.
    
    Supports:
    - PDF files (text extraction)
    - Images (OCR via Tesseract)
    - Plain text
    """
    
    @staticmethod
    async def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_content: Raw PDF file bytes
            
        Returns:
            str: Extracted text
            
        Raises:
            ValueError: If PDF is invalid or empty
        """
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            if len(pdf_reader.pages) == 0:
                raise ValueError("PDF file is empty")
            
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                raise ValueError("No text found in PDF. File may be scanned or image-based.")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    @staticmethod
    async def extract_text_from_image(file_content: bytes) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            file_content: Raw image file bytes
            
        Returns:
            str: Extracted text via OCR
            
        Raises:
            ValueError: If OCR fails or no text found
        """
        try:
            image = Image.open(BytesIO(file_content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                raise ValueError("No text detected in image")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise ValueError(f"Failed to perform OCR: {str(e)}")
    
    @staticmethod
    async def process_document(
        file_content: bytes,
        filename: str,
        content_type: str
    ) -> str:
        """
        Process document based on file type and extract text.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            content_type: MIME type
            
        Returns:
            str: Extracted text
            
        Raises:
            ValueError: If file type not supported or processing fails
        """
        try:
            # Determine file type and route to appropriate processor
            if content_type == "application/pdf" or filename.lower().endswith('.pdf'):
                return await DocumentProcessor.extract_text_from_pdf(file_content)
            
            elif content_type.startswith("image/") or filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                return await DocumentProcessor.extract_text_from_image(file_content)
            
            elif content_type == "text/plain" or filename.lower().endswith('.txt'):
                return file_content.decode('utf-8')
            
            else:
                raise ValueError(f"Unsupported file type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise


# Singleton instance
_document_processor: Optional[DocumentProcessor] = None


def get_document_processor() -> DocumentProcessor:
    """
    Get singleton instance of document processor.
    
    Returns:
        DocumentProcessor: Shared service instance
    """
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
