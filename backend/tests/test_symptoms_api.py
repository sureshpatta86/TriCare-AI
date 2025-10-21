"""
Tests for Symptom Router API endpoint
"""
import pytest
from fastapi import status


def test_symptom_route_success(client, sample_symptom_data):
    """Test successful symptom routing"""
    response = client.post("/api/symptoms/route", json=sample_symptom_data)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "specialist" in data
    assert "confidence" in data
    assert "urgency_level" in data
    assert "reasoning" in data
    
    # Validate data types
    assert isinstance(data["specialist"], str)
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["urgency_level"] in ["routine", "urgent", "emergency"]


def test_symptom_route_missing_symptoms(client):
    """Test symptom routing with missing symptoms field"""
    response = client.post("/api/symptoms/route", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_symptom_route_empty_symptoms(client):
    """Test symptom routing with empty symptoms"""
    response = client.post("/api/symptoms/route", json={"symptoms": ""})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_symptom_route_minimal_data(client):
    """Test symptom routing with only symptoms (no age/gender)"""
    response = client.post("/api/symptoms/route", json={
        "symptoms": "chest pain and shortness of breath"
    })
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "specialist" in data


def test_symptom_route_with_age(client):
    """Test symptom routing with age"""
    response = client.post("/api/symptoms/route", json={
        "symptoms": "joint pain and stiffness",
        "age": 65
    })
    assert response.status_code == status.HTTP_200_OK


def test_symptom_route_invalid_age(client):
    """Test symptom routing with invalid age"""
    response = client.post("/api/symptoms/route", json={
        "symptoms": "headache",
        "age": -5
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_symptom_route_invalid_gender(client):
    """Test symptom routing with invalid gender"""
    response = client.post("/api/symptoms/route", json={
        "symptoms": "nausea",
        "gender": "invalid_gender"
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
