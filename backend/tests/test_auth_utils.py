"""
Unit tests for authentication utilities
"""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException

from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    authenticate_user,
)
from app.models.user import User
from app.config import get_settings

settings = get_settings()


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_verify_correct_password(self):
        """Test verification with correct password"""
        password = "MyPassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        """Test verification with incorrect password"""
        password = "MyPassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("WrongPassword", hashed) is False
    
    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestTokenGeneration:
    """Test JWT token creation"""
    
    def test_create_access_token_default_expiry(self):
        """Test access token creation with default expiry"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"
        assert "exp" in payload
    
    def test_create_access_token_custom_expiry(self):
        """Test access token with custom expiry"""
        data = {"user_id": 1, "email": "test@example.com"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        
        # Check expiry is approximately 15 minutes from now (use UTC for both)
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc).replace(tzinfo=None)
        expected_time = datetime.utcnow() + expires_delta
        time_diff = abs((exp_time - expected_time).total_seconds())
        assert time_diff < 10  # Within 10 seconds tolerance (increased for CI/slower systems)
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_token_contains_custom_data(self):
        """Test that token contains all provided data"""
        data = {
            "user_id": 42,
            "email": "user@test.com",
            "username": "testuser",
            "custom_field": "custom_value"
        }
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        assert payload["user_id"] == 42
        assert payload["email"] == "user@test.com"
        assert payload["username"] == "testuser"
        assert payload["custom_field"] == "custom_value"


class TestTokenVerification:
    """Test JWT token verification"""
    
    def test_verify_valid_access_token(self):
        """Test verification of valid access token"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        token_data = verify_token(token, token_type="access")
        
        assert token_data.user_id == 1
        assert token_data.email == "test@example.com"
    
    def test_verify_valid_refresh_token(self):
        """Test verification of valid refresh token"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_refresh_token(data)
        
        token_data = verify_token(token, token_type="refresh")
        
        assert token_data.user_id == 1
        assert token_data.email == "test@example.com"
    
    def test_verify_expired_token(self):
        """Test verification of expired token"""
        data = {"user_id": 1, "email": "test@example.com"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token, token_type="access")
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
    
    def test_verify_token_wrong_type(self):
        """Test verification fails when token type doesn't match"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        # Try to verify as refresh token
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token, token_type="refresh")
        
        assert exc_info.value.status_code == 401
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.token.string"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token, token_type="access")
        
        assert exc_info.value.status_code == 401
    
    def test_verify_token_missing_user_id(self):
        """Test verification fails when user_id is missing"""
        # Create token without user_id
        payload = {
            "email": "test@example.com",
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=15)
        }
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token, token_type="access")
        
        assert exc_info.value.status_code == 401
    
    def test_verify_token_missing_email(self):
        """Test verification fails when email is missing"""
        payload = {
            "user_id": 1,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=15)
        }
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token, token_type="access")
        
        assert exc_info.value.status_code == 401
    
    def test_verify_token_tampered(self):
        """Test verification fails for tampered token"""
        data = {"user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        # Tamper with token
        tampered_token = token[:-5] + "XXXXX"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(tampered_token, token_type="access")
        
        assert exc_info.value.status_code == 401


class TestAuthenticateUser:
    """Test user authentication"""
    
    def test_authenticate_valid_user(self, db):
        """Test authentication with valid credentials"""
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        authenticated = authenticate_user(db, "test@example.com", "password123")
        
        assert authenticated is not None
        assert authenticated.id == user.id
        assert authenticated.email == user.email
    
    def test_authenticate_wrong_password(self, db):
        """Test authentication with wrong password"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        authenticated = authenticate_user(db, "test@example.com", "wrongpassword")
        
        assert authenticated is None
    
    def test_authenticate_nonexistent_user(self, db):
        """Test authentication with nonexistent email"""
        authenticated = authenticate_user(db, "notexist@example.com", "password123")
        
        assert authenticated is None
    
    def test_authenticate_inactive_user(self, db):
        """Test authentication returns inactive user (status check should be done elsewhere)"""
        user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password=get_password_hash("password123"),
            is_active=False
        )
        db.add(user)
        db.commit()
        
        authenticated = authenticate_user(db, "inactive@example.com", "password123")
        
        # authenticate_user returns the user even if inactive
        # The is_active check is done in the route handler
        assert authenticated is not None
        assert authenticated.is_active is False


@pytest.fixture
def db():
    """Mock database session fixture"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
