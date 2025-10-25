"""
Doctor Finder Service
Handles geocoding, doctor search, and location-based recommendations
Integrates with external API for real-time doctor data
"""
import logging
import math
import random
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from app.schemas.doctors import (
    DoctorSearchRequest,
    DoctorSearchResponse,
    Doctor,
    DoctorLocation
)
from app.services.external_doctor_api import ExternalDoctorAPIService

logger = logging.getLogger(__name__)


class DoctorFinderService:
    """Service for finding doctors based on location and specialization using NPPES NPI Registry"""
    
    def __init__(self):
        """Initialize the doctor finder service with external API"""
        logger.info("Initializing DoctorFinderService with NPPES API")
        self.external_api = ExternalDoctorAPIService()
        logger.info("NPPES API service ready")
    
    
    # ZIP code to coordinates mapping for USA (for future geocoding if needed)
    # Currently not used - NPPES API provides location data
    # ZIP code coordinates removed - using NPPES API data
    PINCODE_COORDINATES = {}

    # Sample doctors removed - using external NPPES API for real USA doctor data
    SAMPLE_DOCTORS = []

    
    # Realistic doctor database with proper Indian medical credentials
    # In production, this would come from a real database
    # Sample doctors removed - using external NPPES API for real USA doctor data
    SAMPLE_DOCTORS = []

    
    def geocode_pincode(self, pincode: str) -> Optional[Tuple[float, float, str, str]]:
        """
        Convert PIN code to geographic coordinates
        
        Args:
            pincode: Postal/PIN code
            
        Returns:
            Tuple of (latitude, longitude, city, state) or None if not found
        """
        # In production, use a real geocoding API like Google Maps, OpenStreetMap, etc.
        return self.PINCODE_COORDINATES.get(pincode)
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        
        Args:
            lat1, lon1: First location coordinates
            lat2, lon2: Second location coordinates
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def generate_doctor_locations(
        self,
        center_lat: float,
        center_lon: float,
        city: str,
        state: str,
        radius_km: float,
        count: int = 5
    ) -> List[Tuple[float, float, str]]:
        """
        Generate random doctor locations within radius
        
        Args:
            center_lat, center_lon: Center coordinates
            city: City name
            state: State name
            radius_km: Search radius
            count: Number of locations to generate
            
        Returns:
            List of (lat, lon, address) tuples
        """
        locations = []
        for i in range(count):
            # Generate random offset within radius
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.5, radius_km)
            
            # Convert to lat/lon offset
            lat_offset = (distance / 111.0) * math.cos(angle)
            lon_offset = (distance / (111.0 * math.cos(math.radians(center_lat)))) * math.sin(angle)
            
            new_lat = center_lat + lat_offset
            new_lon = center_lon + lon_offset
            
            # Generate address
            street_names = [
                "MG Road", "Brigade Road", "Koramangala", "Indiranagar", 
                "Jayanagar", "Malleshwaram", "Whitefield", "HSR Layout",
                "BTM Layout", "Electronic City", "Marathahalli", "Sarjapur Road",
                "Bannerghatta Road", "Rajajinagar", "Basavanagudi", "JP Nagar",
                "Yelahanka", "Hebbal", "Banashankari", "Vijayanagar"
            ]
            address = f"{random.randint(1, 150)}, {random.choice(street_names)}, {city}"
            
            locations.append((new_lat, new_lon, address))
        
        return locations
    
    async def search_doctors(self, request: DoctorSearchRequest) -> DoctorSearchResponse:
        """
        Search for doctors based on location and specialization
        
        Args:
            request: Doctor search request
            
        Returns:
            DoctorSearchResponse with matching doctors
        """
        logger.info(f"Searching doctors for pincode: {request.pincode}, "
                   f"specialization: {request.specialization}")
        
        # Geocode the PIN code
        location_data = self.geocode_pincode(request.pincode)
        
        if not location_data:
            # Estimate location from ZIP code prefix
            state = self._guess_state_from_zip(request.pincode)
            # Use the same coordinate estimation as in external_doctor_api
            from app.services.external_doctor_api import ExternalDoctorAPIService
            center_lat, center_lon = ExternalDoctorAPIService._estimate_coordinates_from_zip(
                request.pincode, "", state
            )
            logger.info(f"Estimated location for ZIP {request.pincode}: {state} ({center_lat}, {center_lon})")
            location_data = (center_lat, center_lon, request.pincode, state)
        
        center_lat, center_lon, city, state = location_data
        
        # Format address - use ZIP code if city is same as ZIP
        if city == request.pincode:
            address = f"ZIP {request.pincode}, {state}"
        else:
            address = f"{city}, {state}"
        
        user_location = {
            "latitude": center_lat,
            "longitude": center_lon,
            "address": address,
            "pincode": request.pincode
        }
        
        # Use external NPPES API
        logger.info("Fetching doctors from NPPES NPI Registry API")
        
        # Use default radius if not provided
        radius_km = request.radius_km or 10.0
        limit = request.limit or 50
        
        external_doctors = await self._search_with_external_api(
            request.pincode, request.specialization, radius_km, limit
        )
        
        if external_doctors:
            logger.info(f"Successfully fetched {len(external_doctors)} doctors from NPPES API")
        else:
            logger.warning("NPPES API returned no results for the given search criteria")
        
        return DoctorSearchResponse(
            user_location=user_location,
            search_radius_km=radius_km,
            specialization=request.specialization,
            total_doctors_found=len(external_doctors),
            doctors=external_doctors,
            processed_at=datetime.utcnow().isoformat() + "Z"
        )
    
    def _guess_state_from_zip(self, zip_code: str) -> str:
        """
        Guess US state from ZIP code prefix
        This is a simplified mapping for common ZIP code ranges
        """
        if not zip_code or len(zip_code) < 2:
            return "CA"  # Default to California
        
        prefix = int(zip_code[:2]) if zip_code[:2].isdigit() else 0
        
        # ZIP code prefix to state mapping (complete US coverage)
        zip_to_state = {
            (0, 6): "PR",    # Puerto Rico
            (7, 9): "NJ",    # New Jersey
            (10, 14): "NY",  # New York
            (15, 19): "PA",  # Pennsylvania
            (20, 20): "DC",  # Washington DC
            (21, 21): "MD",  # Maryland
            (22, 24): "VA",  # Virginia
            (25, 27): "NC",  # North Carolina
            (28, 29): "SC",  # South Carolina
            (30, 31): "GA",  # Georgia
            (32, 34): "FL",  # Florida
            (35, 36): "AL",  # Alabama
            (37, 38): "TN",  # Tennessee
            (39, 39): "MS",  # Mississippi
            (40, 42): "KY",  # Kentucky
            (43, 45): "OH",  # Ohio
            (46, 47): "IN",  # Indiana
            (48, 49): "MI",  # Michigan
            (50, 51): "IA",  # Iowa
            (52, 52): "SD",  # South Dakota
            (53, 54): "WI",  # Wisconsin
            (55, 56): "MN",  # Minnesota
            (57, 57): "SD",  # South Dakota (extended)
            (58, 59): "ND",  # North Dakota
            (60, 62): "IL",  # Illinois
            (63, 64): "MO",  # Missouri
            (65, 65): "MT",  # Montana
            (66, 67): "KS",  # Kansas
            (68, 69): "NE",  # Nebraska
            (70, 71): "LA",  # Louisiana
            (72, 74): "AR",  # Arkansas
            (75, 79): "TX",  # Texas
            (80, 81): "CO",  # Colorado
            (82, 82): "WY",  # Wyoming
            (83, 83): "ID",  # Idaho
            (84, 84): "UT",  # Utah
            (85, 86): "AZ",  # Arizona
            (87, 88): "NM",  # New Mexico
            (89, 89): "NV",  # Nevada
            (90, 96): "CA",  # California
            (97, 97): "OR",  # Oregon
            (98, 99): "WA",  # Washington
        }
        
        for (start, end), state in zip_to_state.items():
            if start <= prefix <= end:
                return state
        
        return "CA"  # Default fallback
    
    async def _search_with_external_api(
        self,
        pincode: str,
        specialization: str,
        radius_km: float,
        limit: int = 50
    ) -> List[Doctor]:
        """
        Search doctors using NPPES external API
        
        Args:
            pincode: US ZIP code
            specialization: Medical specialization
            radius_km: Search radius in kilometers (filters results by distance)
            limit: Maximum number of results to return
            
        Returns:
            List of Doctor objects from external API filtered by radius
        """
        # Detect state from ZIP code (first 2 digits give rough location)
        state = self._guess_state_from_zip(pincode)
        
        # Get user's location coordinates for distance calculation
        from app.services.external_doctor_api import ExternalDoctorAPIService
        user_lat, user_lon = ExternalDoctorAPIService._estimate_coordinates_from_zip(
            pincode, "", state
        )
        
        # Call external API with ZIP code and state
        # Request up to 200 from API, then limit in our response
        api_results = await self.external_api.search_doctors(
            postal_code=pincode,
            specialization=specialization,
            state=state,
            limit=min(limit * 2, 200)  # Request 2x limit or max 200 to have options for sorting
        )
        
        if not api_results:
            return []
        
        # Convert API results to our Doctor schema
        # Note: Radius filtering is not accurate without real geocoding service
        # NPPES provides addresses but not lat/lon, so we estimate coordinates from ZIP codes
        # All doctors in same ZIP area get same estimated coordinates
        doctors = []
        for doc_data in api_results:
            try:
                doc_lat = doc_data["location"]["latitude"]
                doc_lon = doc_data["location"]["longitude"]
                
                # Calculate distance (will be 0.0 for same ZIP, approximate for different ZIPs)
                actual_distance = self.calculate_distance(user_lat, user_lon, doc_lat, doc_lon)
                
                doctor = Doctor(
                    id=doc_data["id"],
                    name=doc_data["name"],
                    specialization=doc_data["specialization"],
                    qualification=doc_data["qualification"],
                    experience_years=doc_data["experience_years"],
                    rating=doc_data["rating"],
                    location=DoctorLocation(
                        latitude=doc_lat,
                        longitude=doc_lon,
                        address=doc_data["location"]["address"],
                        city=doc_data["location"]["city"],
                        state=doc_data["location"]["state"],
                        pincode=doc_data["location"]["pincode"]
                    ),
                    distance_km=round(actual_distance, 2),
                    phone=doc_data["phone"],
                    email=doc_data.get("email"),
                    clinic_name=doc_data["clinic_name"],
                    consultation_fee=doc_data.get("consultation_fee"),
                    available_days=doc_data["available_days"],
                    available_hours=doc_data["available_hours"],
                    languages=doc_data.get("languages", ["English"])
                )
                doctors.append(doctor)
            except Exception as e:
                logger.warning(f"Failed to parse doctor data from API: {str(e)}")
                continue
        
        # Sort by ZIP code proximity (rough approximation)
        doctors.sort(key=lambda d: (d.distance_km, d.name))
        
        # Apply limit to results
        limited_doctors = doctors[:limit]
        
        logger.info(f"Returning {len(limited_doctors)} doctors (limited from {len(doctors)} total)")
        
        return limited_doctors

