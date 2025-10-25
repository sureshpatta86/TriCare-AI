"""
Unit tests for authentication API routes
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.models.user import User
from app.utils.auth import get_password_hash, create_refresh_token


class TestRegisterEndpoint:
    """Test user registration endpoint"""
    
    def test_register_new_user_success(self, client, db):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "full_name": "New User"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert "hashed_password" not in data
        assert data["is_active"] is True
        assert data["is_verified"] is False
    
    def test_register_duplicate_email(self, client, db):
        """Test registration with duplicate email"""
        # Create existing user
        existing_user = User(
            email="existing@example.com",
            username="existing",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        db.add(existing_user)
        db.commit()
        
        # Try to register with same email
        user_data = {
            "email": "existing@example.com",
            "username": "newusername",
            "password": "SecurePass123!"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"].lower()
    
    def test_register_duplicate_username(self, client, db):
        """Test registration with duplicate username"""
        existing_user = User(
            email="existing@example.com",
            username="existinguser",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        db.add(existing_user)
        db.commit()
        
        user_data = {
            "email": "newemail@example.com",
            "username": "existinguser",
            "password": "SecurePass123!"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "username already taken" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "SecurePass123!"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields"""
        user_data = {
            "email": "test@example.com"
            # Missing username and password
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422


class TestLoginEndpoint:
    """Test user login endpoint"""
    
    def test_login_success(self, client, db):
        """Test successful login"""
        # Create test user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        credentials = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
    
    def test_login_wrong_password(self, client, db):
        """Test login with wrong password"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        credentials = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent email"""
        credentials = {
            "email": "notexist@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 401
    
    def test_login_updates_last_login(self, client, db):
        """Test that login updates last_login timestamp"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            last_login=None
        )
        db.add(user)
        db.commit()
        user_id = user.id
        
        credentials = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=credentials)
        
        assert response.status_code == 200
        
        # Refresh user from DB
        db.expire(user)
        updated_user = db.query(User).filter(User.id == user_id).first()
        assert updated_user.last_login is not None
        assert isinstance(updated_user.last_login, datetime)


class TestRefreshTokenEndpoint:
    """Test token refresh endpoint"""
    
    def test_refresh_token_success(self, client, db):
        """Test successful token refresh"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # Create refresh token
        refresh_token = create_refresh_token({"user_id": user.id, "email": user.email})
        
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        
        assert response.status_code == 401
    
    def test_refresh_token_inactive_user(self, client, db):
        """Test refresh fails for inactive user"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=False  # Inactive
        )
        db.add(user)
        db.commit()
        
        refresh_token = create_refresh_token({"user_id": user.id, "email": user.email})
        
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 401


class TestGetMeEndpoint:
    """Test get current user endpoint"""
    
    def test_get_me_success(self, client, db, auth_headers):
        """Test getting current user profile"""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "hashed_password" not in data
    
    def test_get_me_unauthorized(self, client):
        """Test get me without authentication"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 403  # No auth header
    
    def test_get_me_invalid_token(self, client):
        """Test get me with invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401


class TestUpdateMeEndpoint:
    """Test update current user endpoint"""
    
    def test_update_profile_success(self, client, db, auth_headers):
        """Test successful profile update"""
        update_data = {
            "full_name": "Updated Name",
            "age": 30,
            "phone": "+1234567890"
        }
        
        response = client.put("/api/auth/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["age"] == 30
        assert data["phone"] == "+1234567890"
    
    def test_update_profile_partial(self, client, auth_headers):
        """Test partial profile update"""
        update_data = {
            "age": 25
        }
        
        response = client.put("/api/auth/me", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["age"] == 25
        assert data["email"] == "test@example.com"  # Unchanged
    
    def test_update_profile_unauthorized(self, client):
        """Test update without authentication"""
        update_data = {"full_name": "New Name"}
        response = client.put("/api/auth/me", json=update_data)
        
        assert response.status_code == 403


class TestDeleteAccountEndpoint:
    """Test account deletion endpoint"""
    
    def test_delete_account_success(self, client, db, auth_headers):
        """Test successful account deactivation"""
        response = client.delete("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deactivated" in response.json()["message"].lower()
        
        # Verify user is deactivated in DB
        user = db.query(User).filter(User.email == "test@example.com").first()
        assert user.is_active is False
    
    def test_delete_account_unauthorized(self, client):
        """Test delete without authentication"""
        response = client.delete("/api/auth/me")
        
        assert response.status_code == 403


class TestForgotPasswordEndpoint:
    """Test forgot password endpoint"""
    
    def test_forgot_password_existing_user(self, client, db):
        """Test forgot password for existing user"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            is_active=True
        )
        db.add(user)
        db.commit()
        user_id = user.id
        
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "reset" in data["message"].lower()
        
        # Verify reset token was created
        db.expire(user)
        updated_user = db.query(User).filter(User.id == user_id).first()
        assert updated_user.reset_token is not None
        assert updated_user.reset_token_expires is not None
    
    def test_forgot_password_nonexistent_user(self, client):
        """Test forgot password for nonexistent user (should still return success)"""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "notexist@example.com"}
        )
        
        # Should return success to prevent email enumeration
        assert response.status_code == 200
        assert "reset" in response.json()["message"].lower()


class TestResetPasswordEndpoint:
    """Test reset password endpoint"""
    
    def test_reset_password_success(self, client, db):
        """Test successful password reset"""
        import secrets
        
        reset_token = secrets.token_urlsafe(32)
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("oldpassword"),
            reset_token=reset_token,
            reset_token_expires=datetime.utcnow() + timedelta(hours=1),
            is_active=True
        )
        db.add(user)
        db.commit()
        user_id = user.id
        
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewSecurePass123!"
            }
        )
        
        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()
        
        # Verify password was changed and token cleared
        db.expire(user)
        updated_user = db.query(User).filter(User.id == user_id).first()
        assert updated_user.reset_token is None
        assert updated_user.reset_token_expires is None
        
        # Verify new password works
        from app.utils.auth import verify_password
        assert verify_password("NewSecurePass123!", updated_user.hashed_password)
    
    def test_reset_password_invalid_token(self, client):
        """Test reset with invalid token"""
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": "invalid_token",
                "new_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    def test_reset_password_expired_token(self, client, db):
        """Test reset with expired token"""
        import secrets
        
        reset_token = secrets.token_urlsafe(32)
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("oldpassword"),
            reset_token=reset_token,
            reset_token_expires=datetime.utcnow() - timedelta(hours=1),  # Expired
            is_active=True
        )
        db.add(user)
        db.commit()
        
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewPassword123!"
            }
        )
        
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()


# Fixtures

@pytest.fixture
def auth_headers(client, db):
    """Fixture to provide authentication headers"""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
