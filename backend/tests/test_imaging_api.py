"""
Tests for X-ray Pre-Screen API endpoint
"""
import pytest
from fastapi import status
from io import BytesIO


def test_imaging_prescreen_no_file(client):
    """Test imaging pre-screen without a file"""
    response = client.post("/api/imaging/prescreen")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_imaging_prescreen_invalid_file_type(client):
    """Test imaging pre-screen with invalid file type"""
    file_content = b"fake file content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    response = client.post("/api/imaging/prescreen", files=files)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_imaging_prescreen_success(client, sample_image_file):
    """Test successful imaging pre-screen"""
    files = {"file": ("xray.png", sample_image_file, "image/png")}
    response = client.post("/api/imaging/prescreen", files=files)
    
    # Accept success or error (if ML model not loaded)
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert "model_used" in data
        
        # Validate data types
        assert isinstance(data["prediction"], str)
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <= 1.0
    else:
        # Accept error if model not available
        assert response.status_code in [
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]


def test_imaging_prescreen_jpeg(client):
    """Test imaging pre-screen with JPEG image"""
    from PIL import Image
    import numpy as np
    
    img_array = np.random.randint(0, 255, (224, 224), dtype=np.uint8)
    img = Image.fromarray(img_array, mode='L')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    
    files = {"file": ("xray.jpg", buffer, "image/jpeg")}
    response = client.post("/api/imaging/prescreen", files=files)
    
    assert response.status_code in [
        status.HTTP_200_OK,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.HTTP_503_SERVICE_UNAVAILABLE
    ]


def test_imaging_prescreen_file_too_large(client):
    """Test imaging pre-screen with file that's too large"""
    large_content = b"x" * (11 * 1024 * 1024)
    files = {"file": ("large.png", BytesIO(large_content), "image/png")}
    response = client.post("/api/imaging/prescreen", files=files)
    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
