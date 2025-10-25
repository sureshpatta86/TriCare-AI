"""
Pytest configuration and fixtures for backend tests
"""
import pytest
import os
from sqlalchemy import create_engine, event, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils.auth import get_password_hash, create_access_token


# Test database URL - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

# Global test engine and session maker - shared across all tests in a session
test_engine = None
TestingSessionLocal = None


@pytest.fixture(scope="session")
def db_engine_session():
    """
    Create a test database engine for the entire test session.
    Using StaticPool to ensure all connections share the same in-memory database.
    """
    global test_engine, TestingSessionLocal
    
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Critical: ensures all connections use the same in-memory DB
    )
    
    # Create all tables once for the session
    Base.metadata.create_all(bind=test_engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    yield test_engine
    
    # Drop all tables after all tests
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def db(db_engine_session) -> Generator:
    """
    Create a fresh database session for each test function.
    Clear data between tests but keep the schema.
    """
    connection = db_engine_session.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db) -> TestClient:
    """
    Create a test client with database dependency override.
    Uses the same db session fixture to ensure data consistency.
    """
    def override_get_db():
        """Override the get_db dependency to use the same test db session"""
        yield db
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def test_user(db) -> User:
    """Create a test user in the database"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user) -> str:
    """Generate an authentication token for test user"""
    return create_access_token(
        data={"user_id": test_user.id, "email": test_user.email}
    )


@pytest.fixture
def auth_headers(auth_token) -> dict:
    """Generate authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}


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
    try:
        from reportlab.pdfgen import canvas
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, "Medical Report")
        p.drawString(100, 730, "Patient: John Doe")
        p.drawString(100, 710, "Diagnosis: Test condition")
        p.save()
        buffer.seek(0)
        return buffer
    except ImportError:
        # If reportlab is not available, create a minimal PDF-like structure
        buffer = BytesIO()
        buffer.write(b"%PDF-1.4\nTest PDF content")
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


@pytest.fixture
def sample_dicom_like_file():
    """Create a sample DICOM-like file for testing"""
    from io import BytesIO
    
    buffer = BytesIO()
    # DICOM files start with a 128-byte preamble followed by "DICM"
    buffer.write(b'\x00' * 128)
    buffer.write(b'DICM')
    buffer.write(b'Test DICOM content')
    buffer.seek(0)
    return buffer


@pytest.fixture
def multiple_users(db) -> list:
    """Create multiple test users"""
    users = []
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            username=f"user{i}",
            full_name=f"User {i}",
            hashed_password=get_password_hash(f"password{i}"),
            is_active=True
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    for user in users:
        db.refresh(user)
    
    return users


# Pytest configuration for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for all tests"""
    test_env_vars = {
        "TESTING": "true",  # Flag to skip production database initialization
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "DATABASE_URL": TEST_DATABASE_URL,
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_API_KEY": "test-api-key",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "test-deployment",
        "AZURE_OPENAI_API_VERSION": "2023-05-15",
    }
    
    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)
