"""
Unit tests for Doctor Finder Service
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import math

from app.services.doctor_finder import DoctorFinderService
from app.schemas.doctors import DoctorSearchRequest


class TestDoctorFinderInitialization:
    """Test service initialization"""
    
    def test_service_initializes_successfully(self):
        """Test that service initializes"""
        service = DoctorFinderService()
        assert service is not None
        assert service.external_api is not None


class TestGeocoding:
    """Test geocoding functionality"""
    
    def test_guess_state_from_zip_california(self):
        """Test ZIP code to state mapping for California"""
        service = DoctorFinderService()
        
        assert service._guess_state_from_zip("94102") == "CA"
        assert service._guess_state_from_zip("90001") == "CA"
        assert service._guess_state_from_zip("92101") == "CA"
    
    def test_guess_state_from_zip_new_york(self):
        """Test ZIP code to state mapping for New York"""
        service = DoctorFinderService()
        
        assert service._guess_state_from_zip("10001") == "NY"
        assert service._guess_state_from_zip("11201") == "NY"
    
    def test_guess_state_from_zip_texas(self):
        """Test ZIP code to state mapping for Texas"""
        service = DoctorFinderService()
        
        assert service._guess_state_from_zip("75001") == "TX"
        assert service._guess_state_from_zip("77001") == "TX"
        assert service._guess_state_from_zip("78701") == "TX"
    
    def test_guess_state_from_zip_florida(self):
        """Test ZIP code to state mapping for Florida"""
        service = DoctorFinderService()
        
        assert service._guess_state_from_zip("33101") == "FL"
        assert service._guess_state_from_zip("32801") == "FL"
    
    def test_guess_state_from_zip_invalid(self):
        """Test invalid ZIP code defaults to CA"""
        service = DoctorFinderService()
        
        assert service._guess_state_from_zip("") == "CA"
        assert service._guess_state_from_zip("X") == "CA"
        # 99999 is actually in the WA range (98-99)
        assert service._guess_state_from_zip("99999") == "WA"


class TestDistanceCalculation:
    """Test distance calculation using Haversine formula"""
    
    def test_calculate_distance_same_point(self):
        """Test distance between same coordinates is 0"""
        distance = DoctorFinderService.calculate_distance(
            37.7749, -122.4194,  # San Francisco
            37.7749, -122.4194   # Same point
        )
        assert distance == 0.0
    
    def test_calculate_distance_known_cities(self):
        """Test distance between known cities"""
        # San Francisco to Los Angeles (approximate)
        distance = DoctorFinderService.calculate_distance(
            37.7749, -122.4194,  # San Francisco
            34.0522, -118.2437   # Los Angeles
        )
        
        # Should be approximately 559 km
        assert 550 < distance < 570
    
    def test_calculate_distance_new_york_boston(self):
        """Test distance between New York and Boston"""
        distance = DoctorFinderService.calculate_distance(
            40.7128, -74.0060,   # New York
            42.3601, -71.0589    # Boston
        )
        
        # Should be approximately 306 km
        assert 300 < distance < 315
    
    def test_calculate_distance_symmetry(self):
        """Test that distance is symmetric"""
        dist1 = DoctorFinderService.calculate_distance(
            37.7749, -122.4194,
            34.0522, -118.2437
        )
        dist2 = DoctorFinderService.calculate_distance(
            34.0522, -118.2437,
            37.7749, -122.4194
        )
        
        assert abs(dist1 - dist2) < 0.001
    
    def test_calculate_distance_returns_positive(self):
        """Test that distance is always positive"""
        distance = DoctorFinderService.calculate_distance(
            40.7128, -74.0060,
            34.0522, -118.2437
        )
        
        assert distance > 0


class TestLocationGeneration:
    """Test doctor location generation"""
    
    def test_generate_locations_count(self):
        """Test that correct number of locations are generated"""
        service = DoctorFinderService()
        
        locations = service.generate_doctor_locations(
            center_lat=37.7749,
            center_lon=-122.4194,
            city="San Francisco",
            state="CA",
            radius_km=10.0,
            count=5
        )
        
        assert len(locations) == 5
    
    def test_generate_locations_within_radius(self):
        """Test that generated locations are within specified radius"""
        service = DoctorFinderService()
        center_lat, center_lon = 37.7749, -122.4194
        radius_km = 10.0
        
        locations = service.generate_doctor_locations(
            center_lat=center_lat,
            center_lon=center_lon,
            city="San Francisco",
            state="CA",
            radius_km=radius_km,
            count=10
        )
        
        for lat, lon, address in locations:
            distance = service.calculate_distance(
                center_lat, center_lon, lat, lon
            )
            assert distance <= radius_km
    
    def test_generate_locations_structure(self):
        """Test that generated locations have correct structure"""
        service = DoctorFinderService()
        
        locations = service.generate_doctor_locations(
            center_lat=37.7749,
            center_lon=-122.4194,
            city="San Francisco",
            state="CA",
            radius_km=5.0,
            count=3
        )
        
        for location in locations:
            assert len(location) == 3
            lat, lon, address = location
            assert isinstance(lat, float)
            assert isinstance(lon, float)
            assert isinstance(address, str)
            assert len(address) > 0


class TestSearchDoctors:
    """Test doctor search functionality"""
    
    @pytest.mark.asyncio
    async def test_search_doctors_basic(self):
        """Test basic doctor search"""
        service = DoctorFinderService()
        
        # Mock external API response
        mock_doctor_data = [{
            "id": "1234567890",
            "name": "Dr. John Smith",
            "specialization": "Cardiology",
            "qualification": "MD",
            "experience_years": 15,
            "rating": 4.5,
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "address": "123 Medical Center Dr",
                "city": "San Francisco",
                "state": "CA",
                "pincode": "94102"
            },
            "phone": "+1-415-555-0100",
            "email": "dr.smith@example.com",
            "clinic_name": "Heart Care Clinic",
            "consultation_fee": 200.0,
            "available_days": ["Monday", "Wednesday", "Friday"],
            "available_hours": "9:00 AM - 5:00 PM",
            "languages": ["English", "Spanish"]
        }]
        
        with patch.object(service.external_api, 'search_doctors', new=AsyncMock(return_value=mock_doctor_data)):
            request = DoctorSearchRequest(
                pincode="94102",
                specialization="Cardiology",
                radius_km=10.0,
                limit=10
            )
            
            response = await service.search_doctors(request)
            
            assert response is not None
            assert response.total_doctors_found == 1
            assert len(response.doctors) == 1
            assert response.doctors[0].name == "Dr. John Smith"
            assert response.specialization == "Cardiology"
    
    @pytest.mark.asyncio
    async def test_search_doctors_with_specialization(self):
        """Test doctor search with specific specialization"""
        service = DoctorFinderService()
        
        mock_doctor_data = [{
            "id": "1234567890",
            "name": "Dr. Sarah Johnson",
            "specialization": "Pediatrics",
            "qualification": "MD",
            "experience_years": 10,
            "rating": 4.8,
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "456 Children's Hospital",
                "city": "New York",
                "state": "NY",
                "pincode": "10001"
            },
            "phone": "+1-212-555-0200",
            "clinic_name": "Kids Care Center",
            "consultation_fee": 150.0,
            "available_days": ["Tuesday", "Thursday"],
            "available_hours": "10:00 AM - 6:00 PM",
            "languages": ["English"]
        }]
        
        with patch.object(service.external_api, 'search_doctors', new=AsyncMock(return_value=mock_doctor_data)):
            request = DoctorSearchRequest(
                pincode="10001",
                specialization="Pediatrics",
                radius_km=15.0
            )
            
            response = await service.search_doctors(request)
            
            assert response.doctors[0].specialization == "Pediatrics"
            assert response.specialization == "Pediatrics"
    
    @pytest.mark.asyncio
    async def test_search_doctors_no_results(self):
        """Test doctor search with no results"""
        service = DoctorFinderService()
        
        with patch.object(service.external_api, 'search_doctors', new=AsyncMock(return_value=[])):
            request = DoctorSearchRequest(
                pincode="99999",
                specialization="Neurology"
            )
            
            response = await service.search_doctors(request)
            
            assert response.total_doctors_found == 0
            assert len(response.doctors) == 0
    
    @pytest.mark.asyncio
    async def test_search_doctors_respects_limit(self):
        """Test that search respects the limit parameter"""
        service = DoctorFinderService()
        
        # Create 10 mock doctors
        mock_doctor_data = []
        for i in range(10):
            mock_doctor_data.append({
                "id": f"123456789{i}",
                "name": f"Dr. Test {i}",
                "specialization": "General Practice",
                "qualification": "MD",
                "experience_years": 5,
                "rating": 4.0,
                "location": {
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                    "address": f"{i} Test St",
                    "city": "San Francisco",
                    "state": "CA",
                    "pincode": "94102"
                },
                "phone": f"+1-415-555-010{i}",
                "clinic_name": "Test Clinic",
                "consultation_fee": 100.0,
                "available_days": ["Monday"],
                "available_hours": "9 AM - 5 PM",
                "languages": ["English"]
            })
        
        with patch.object(service.external_api, 'search_doctors', new=AsyncMock(return_value=mock_doctor_data)):
            request = DoctorSearchRequest(
                pincode="94102",
                specialization="General Practice",
                limit=5
            )
            
            response = await service.search_doctors(request)
            
            assert len(response.doctors) <= 5
    
    @pytest.mark.asyncio
    async def test_search_doctors_distance_calculation(self):
        """Test that distances are calculated correctly"""
        service = DoctorFinderService()
        
        mock_doctor_data = [{
            "id": "1234567890",
            "name": "Dr. Test",
            "specialization": "General Practice",
            "qualification": "MD",
            "experience_years": 5,
            "rating": 4.0,
            "location": {
                "latitude": 37.8,  # Slightly different from center
                "longitude": -122.4,
                "address": "123 Test St",
                "city": "San Francisco",
                "state": "CA",
                "pincode": "94102"
            },
            "phone": "+1-415-555-0100",
            "clinic_name": "Test Clinic",
            "consultation_fee": 100.0,
            "available_days": ["Monday"],
            "available_hours": "9 AM - 5 PM",
            "languages": ["English"]
        }]
        
        with patch.object(service.external_api, 'search_doctors', new=AsyncMock(return_value=mock_doctor_data)):
            request = DoctorSearchRequest(
                pincode="94102",
                specialization="General Practice"
            )
            
            response = await service.search_doctors(request)
            
            assert response.doctors[0].distance_km >= 0
            assert isinstance(response.doctors[0].distance_km, float)


class TestUserLocationHandling:
    """Test user location data handling"""
    
    @pytest.mark.asyncio
    async def test_user_location_in_response(self):
        """Test that user location is included in response"""
        service = DoctorFinderService()
        
        with patch.object(service.external_api, 'search_doctors', new=AsyncMock(return_value=[])):
            request = DoctorSearchRequest(
                pincode="94102",
                specialization="Cardiology"
            )
            
            response = await service.search_doctors(request)
            
            assert response.user_location is not None
            assert "latitude" in response.user_location
            assert "longitude" in response.user_location
            assert "address" in response.user_location
            assert response.user_location["pincode"] == "94102"
    
    @pytest.mark.asyncio
    async def test_search_radius_in_response(self):
        """Test that search radius is included in response"""
        service = DoctorFinderService()
        
        with patch.object(service.external_api, 'search_doctors', new=AsyncMock(return_value=[])):
            request = DoctorSearchRequest(
                pincode="94102",
                specialization="Cardiology",
                radius_km=20.0
            )
            
            response = await service.search_doctors(request)
            
            assert response.search_radius_km == 20.0
    
    @pytest.mark.asyncio
    async def test_processed_timestamp_in_response(self):
        """Test that processed timestamp is included"""
        service = DoctorFinderService()
        
        with patch.object(service.external_api, 'search_doctors', new=AsyncMock(return_value=[])):
            request = DoctorSearchRequest(
                pincode="94102",
                specialization="Cardiology"
            )
            
            response = await service.search_doctors(request)
            
            assert response.processed_at is not None
            assert isinstance(response.processed_at, str)
            assert "Z" in response.processed_at  # ISO format with UTC marker
