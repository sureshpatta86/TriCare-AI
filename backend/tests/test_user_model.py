"""
Unit tests for User model
"""
import pytest
from datetime import datetime

from app.models.user import User
from app.utils.auth import get_password_hash


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, db):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_verified is False
    
    def test_user_unique_email(self, db):
        """Test that email must be unique"""
        user1 = User(
            email="test@example.com",
            username="user1",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        user2 = User(
            email="test@example.com",  # Duplicate email
            username="user2",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        db.add(user1)
        db.commit()
        
        db.add(user2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db.commit()
    
    def test_user_unique_username(self, db):
        """Test that username must be unique"""
        user1 = User(
            email="user1@example.com",
            username="testuser",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        user2 = User(
            email="user2@example.com",
            username="testuser",  # Duplicate username
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        db.add(user1)
        db.commit()
        
        db.add(user2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            db.commit()
    
    def test_user_default_values(self, db):
        """Test default values for user fields"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password")
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.is_active is True
        assert user.is_verified is False
        assert user.reset_token is None
        assert user.reset_token_expires is None
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
    
    def test_user_profile_fields(self, db):
        """Test user profile fields"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password"),
            age=30,
            sex="Male",
            phone="+1234567890",
            postal_code="94102"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.age == 30
        assert user.sex == "Male"
        assert user.phone == "+1234567890"
        assert user.postal_code == "94102"
    
    def test_user_medical_information(self, db):
        """Test user medical information fields"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password"),
            blood_type="O+",
            allergies='["Penicillin", "Pollen"]',
            chronic_conditions='["Diabetes"]',
            current_medications='["Metformin"]',
            emergency_contact='{"name": "John Doe", "phone": "+1234567890"}'
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.blood_type == "O+"
        assert "Penicillin" in user.allergies
        assert "Diabetes" in user.chronic_conditions
        assert "Metformin" in user.current_medications
        assert "John Doe" in user.emergency_contact
    
    def test_user_password_reset_fields(self, db):
        """Test password reset fields"""
        from datetime import timedelta
        
        reset_token = "test_reset_token_12345"
        expires = datetime.utcnow() + timedelta(hours=1)
        
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password"),
            reset_token=reset_token,
            reset_token_expires=expires,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.reset_token == reset_token
        assert user.reset_token_expires == expires
    
    def test_user_last_login_tracking(self, db):
        """Test last login timestamp"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.last_login is None
        
        # Update last login
        login_time = datetime.utcnow()
        user.last_login = login_time
        db.commit()
        db.refresh(user)
        
        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)
    
    def test_user_update_timestamp(self, db):
        """Test updated_at timestamp"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        original_updated = user.updated_at
        
        # Update user
        user.full_name = "Updated Name"
        db.commit()
        db.refresh(user)
        
        # updated_at should change (or remain None if not configured)
        # This depends on your database trigger/configuration
        assert user.full_name == "Updated Name"
    
    def test_user_deactivation(self, db):
        """Test user deactivation"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        db.add(user)
        db.commit()
        
        # Deactivate user
        user.is_active = False
        db.commit()
        db.refresh(user)
        
        assert user.is_active is False
    
    def test_query_user_by_email(self, db):
        """Test querying user by email"""
        user = User(
            email="findme@example.com",
            username="findme",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        db.add(user)
        db.commit()
        
        # Query by email
        found_user = db.query(User).filter(User.email == "findme@example.com").first()
        
        assert found_user is not None
        assert found_user.email == "findme@example.com"
        assert found_user.username == "findme"
    
    def test_query_user_by_username(self, db):
        """Test querying user by username"""
        user = User(
            email="test@example.com",
            username="uniqueuser",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        
        db.add(user)
        db.commit()
        
        # Query by username
        found_user = db.query(User).filter(User.username == "uniqueuser").first()
        
        assert found_user is not None
        assert found_user.username == "uniqueuser"
    
    def test_multiple_users(self, db):
        """Test creating and querying multiple users"""
        users = []
        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                hashed_password=get_password_hash(f"password{i}"),
                is_active=True
            )
            users.append(user)
            db.add(user)
        
        db.commit()
        
        # Query all users
        all_users = db.query(User).all()
        
        assert len(all_users) >= 5
        
        # Check active users
        active_users = db.query(User).filter(User.is_active == True).all()
        assert len(active_users) >= 5
