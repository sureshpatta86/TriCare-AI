"""
User model for authentication
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User account model"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Profile information
    age = Column(Integer, nullable=True)
    sex = Column(String, nullable=True)  # Male, Female, Other
    phone = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)  # ZIP/Postal code for doctor search
    
    # Medical information
    blood_type = Column(String, nullable=True)
    allergies = Column(String, nullable=True)  # JSON string
    chronic_conditions = Column(String, nullable=True)  # JSON string
    current_medications = Column(String, nullable=True)  # JSON string
    emergency_contact = Column(String, nullable=True)  # JSON string
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Password reset
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
