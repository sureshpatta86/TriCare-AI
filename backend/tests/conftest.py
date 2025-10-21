"""
Pytest configuration and fixtures for backend tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_symptom_data():
    """Sample symptom data for testing"""
    return {
        "symptoms": "headache, fever, and fatigue for 3 days",
        "age": 35,
        "gender": "male"
    }


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    from io import BytesIO
    from reportlab.pdfgen import canvas
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "Medical Report")
    p.drawString(100, 730, "Patient: John Doe")
    p.drawString(100, 710, "Diagnosis: Test condition")
    p.save()
    buffer.seek(0)
    return buffer


@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing"""
    from io import BytesIO
    from PIL import Image
    import numpy as np
    
    # Create a simple grayscale image
    img_array = np.random.randint(0, 255, (224, 224), dtype=np.uint8)
    img = Image.fromarray(img_array, mode='L')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
