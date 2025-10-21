"""
External Doctor API Integration Service
Integrates with NPPES NPI Registry for real-time US doctor data
"""
import logging
import os
import httpx
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ExternalDoctorAPIService:
    """Service for fetching doctor data from NPPES NPI Registry API"""
    
    def __init__(self):
        """Initialize the external API service"""
        self.api_base_url = os.getenv("DOCTORS_API_BASE_URL", "https://npiregistry.cms.hhs.gov/api")
        self.api_version = "2.1"
        self.timeout = 30.0
        
        logger.info("NPPES NPI Registry API service initialized (no API key required)")
    
    async def search_doctors(
        self,
        postal_code: str,
        specialization: str,
        state: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search for doctors using NPPES NPI Registry API
        
        Args:
            postal_code: US postal/ZIP code
            specialization: Medical specialization to search for (will be filtered client-side)
            state: US state abbreviation (e.g., 'CA', 'NY')
            limit: Maximum number of results (max 200)
            
        Returns:
            List of doctor dictionaries with normalized data
        """
        try:
            # Extract first 5 digits from postal code (handles ZIP+4 format)
            # Remove any non-digit characters and take first 5 digits
            clean_zip = ''.join(filter(str.isdigit, postal_code))[:5]
            
            if not clean_zip or len(clean_zip) < 5:
                logger.error(f"Invalid postal code format: {postal_code}")
                return []
            
            logger.info(f"Extracted ZIP code: {clean_zip} from input: {postal_code}")
            
            # Search by 5-digit ZIP code
            params = {
                "version": self.api_version,
                "postal_code": clean_zip,
                "limit": min(limit, 200),  # API max is 200
                "enumeration_type": "NPI-1",  # Individual providers only
                "pretty": "false"
            }
            
            # Add state if provided
            if state:
                params["state"] = state.upper()
            
            # If specialization is provided, also add it to API parameters for better results
            # This helps narrow down results from NPPES itself
            if specialization:
                # Try to map common terms to NPPES taxonomy terms
                taxonomy_param = self._map_to_nppes_taxonomy(specialization)
                if taxonomy_param:
                    params["taxonomy_description"] = taxonomy_param
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Calling NPPES API: {self.api_base_url} with postal_code={clean_zip}")
                response = await client.get(
                    self.api_base_url,
                    params=params
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Normalize the response data
                all_doctors = self._normalize_doctor_data(data)
                result_count = len(all_doctors)
                
                logger.info(f"Found {result_count} doctors in ZIP {clean_zip}")
                
                # Return results only from the exact ZIP code provided
                # No state-wide expansion - if no doctors found, return empty list
                if result_count == 0:
                    logger.info(f"No doctors with specialization '{specialization}' found in ZIP {clean_zip}")
                    return []
                
                logger.info(f"Returning {len(all_doctors)} doctors from ZIP {clean_zip}")
                return all_doctors
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from NPPES API: {e.response.status_code} - {e.response.text}")
            return []
        except httpx.RequestError as e:
            logger.error(f"Request error calling NPPES API: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error calling NPPES API: {str(e)}", exc_info=True)
            return []
    
    async def get_doctor_by_npi(self, npi_number: str) -> Optional[Dict]:
        """
        Get detailed information about a specific doctor by NPI number
        
        Args:
            npi_number: 10-digit National Provider Identifier
            
        Returns:
            Doctor details or None
        """
        try:
            params = {
                "version": self.api_version,
                "number": npi_number
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.api_base_url,
                    params=params
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Normalize single doctor response
                normalized = self._normalize_doctor_data(data)
                return normalized[0] if normalized else None
                
        except Exception as e:
            logger.error(f"Error fetching doctor {npi_number}: {str(e)}")
            return None
    
    def _get_specialty_keywords(self, specialization: str) -> List[str]:
        """
        Map common specialty names to NPPES taxonomy keywords for better matching
        
        Args:
            specialization: User-provided specialty name
            
        Returns:
            List of keywords to search for in NPPES taxonomy descriptions
        """
        spec_lower = specialization.lower()
        
        # Mapping of common specialty names to NPPES taxonomy keywords
        specialty_mappings = {
            "cardiologist": ["cardiovascular", "cardiology", "heart"],
            "heart": ["cardiovascular", "cardiology"],
            "dermatologist": ["dermatology", "skin"],
            "neurologist": ["neurology", "brain"],
            "orthopedic": ["orthop", "musculoskeletal", "sports medicine"],
            "pediatrician": ["pediatric", "child"],
            "psychiatrist": ["psychiatry", "mental health"],
            "gynecologist": ["gynecology", "obstetrics", "women"],
            "ent": ["otolaryngology", "ear", "nose", "throat"],
            "eye": ["ophthalmology", "optometry", "vision"],
            "oncologist": ["oncology", "cancer", "hematology"],
            "endocrinologist": ["endocrinology", "diabetes", "hormone"],
            "gastroenterologist": ["gastroenterology", "digestive"],
            "pulmonologist": ["pulmonology", "pulmonary", "lung", "respiratory"],
            "nephrologist": ["nephrology", "kidney", "renal"],
            "urologist": ["urology", "urinary"],
            "rheumatologist": ["rheumatology", "arthritis"],
            "allergist": ["allergy", "immunology"],
        }
        
        # Check if we have a mapping for this specialty
        for key, keywords in specialty_mappings.items():
            if key in spec_lower:
                return keywords
        
        # If no specific mapping, return the original term
        return [spec_lower]
    
    def _map_to_nppes_taxonomy(self, specialization: str) -> str:
        """
        Map common specialty names to NPPES taxonomy_description parameter values
        These are the exact terms NPPES uses in its taxonomy system
        
        Args:
            specialization: User-provided specialty name
            
        Returns:
            NPPES taxonomy term or empty string if no mapping
        """
        spec_lower = specialization.lower()
        
        # Mapping of common terms to NPPES taxonomy_description values
        # These are partial matches - NPPES will return any taxonomy containing this text
        taxonomy_mappings = {
            # Medical Specialists
            "cardiologist": "Cardiovascular Disease",
            "heart": "Cardiovascular",
            "dermatologist": "Dermatology",
            "neurologist": "Neurology",
            "orthopedic": "Orthopaedic",
            "pediatrician": "Pediatrics",
            "psychiatrist": "Psychiatry",
            "gynecologist": "Obstetrics & Gynecology",
            "obstetrician": "Obstetrics",
            "ent": "Otolaryngology",
            "eye doctor": "Ophthalmology",
            "ophthalmologist": "Ophthalmology",
            "oncologist": "Oncology",
            "endocrinologist": "Endocrinology",
            "gastroenterologist": "Gastroenterology",
            "pulmonologist": "Pulmonary",
            "nephrologist": "Nephrology",
            "urologist": "Urology",
            "rheumatologist": "Rheumatology",
            "allergist": "Allergy",
            "emergency": "Emergency Medicine",
            "surgeon": "Surgery",
            "anesthesiologist": "Anesthesiology",
            "radiologist": "Radiology",
            "pathologist": "Pathology",
            
            # Primary Care
            "family": "Family Medicine",
            "internal medicine": "Internal Medicine",
            "general": "General Practice",
            
            # Allied Health Professionals
            "chiropractor": "Chiropractor",
            "dentist": "Dentist",
            "nurse practitioner": "Nurse Practitioner",
            "occupational therapist": "Occupational Therapist",
            "optometrist": "Optometrist",
            "pharmacist": "Pharmacist",
            "physician assistant": "Physician Assistant",
            "physical therapist": "Physical Therapist",
            "podiatrist": "Podiatrist",
            "psychologist": "Psychologist",
            "social worker": "Social Worker",
            "counselor": "Counselor",
            "speech": "Speech-Language Pathologist",
        }
        
        # Check if we have a mapping for this specialty
        for key, taxonomy_term in taxonomy_mappings.items():
            if key in spec_lower:
                return taxonomy_term
        
        # Return empty string if no mapping found (will search without taxonomy filter)
        return ""
    
    def _normalize_doctor_data(self, api_response: Dict) -> List[Dict]:
        """
        Normalize NPPES API response to match our internal format
        
        NPPES Response structure:
        {
          "result_count": 10,
          "results": [{
            "number": "1234567890",
            "basic": {
              "first_name": "John",
              "last_name": "Smith",
              "credential": "MD",
              "gender": "M"
            },
            "addresses": [
              {
                "address_1": "123 Main St",
                "city": "Los Angeles",
                "state": "CA",
                "postal_code": "90001",
                "telephone_number": "123-456-7890"
              }
            ],
            "taxonomies": [
              {
                "code": "207R00000X",
                "desc": "Internal Medicine",
                "primary": true
              }
            ]
          }]
        }
        
        Args:
            api_response: Raw NPPES API response
            
        Returns:
            List of normalized doctor dictionaries
        """
        doctors = []
        
        # NPPES uses "results" array
        doctor_list = api_response.get("results", [])
        
        for doc in doctor_list:
            try:
                # Extract basic information
                basic = doc.get("basic", {})
                first_name = basic.get("first_name", "")
                last_name = basic.get("last_name", "")
                name = f"Dr. {first_name} {last_name}".strip()
                
                # Get credential (MD, DO, etc.)
                credential = basic.get("credential", "MD")
                
                # Get primary address (first in addresses array is primary practice location)
                addresses = doc.get("addresses", [])
                primary_addr = addresses[0] if addresses else {}
                
                # Extract address components
                address_line = primary_addr.get("address_1", "")
                if primary_addr.get("address_2"):
                    address_line += f", {primary_addr.get('address_2')}"
                
                city = primary_addr.get("city", "")
                state = primary_addr.get("state", "")
                raw_postal_code = primary_addr.get("postal_code", "")
                
                # Format postal code properly (NPPES returns 9 digits without dash)
                # Convert "852187352" to "85218-7352" or keep "85218" as is
                postal_code = self._format_postal_code(raw_postal_code)
                
                phone = primary_addr.get("telephone_number", "")
                
                # Get primary taxonomy (specialty)
                taxonomies = doc.get("taxonomies", [])
                primary_taxonomy = next((t for t in taxonomies if t.get("primary")), taxonomies[0] if taxonomies else {})
                specialization = primary_taxonomy.get("desc", "General Physician")
                
                # Estimate coordinates based on ZIP code (rough approximation)
                # NPPES doesn't provide exact coordinates, so we use ZIP-based estimation
                lat, lon = self._estimate_coordinates_from_zip(postal_code, city, state)
                
                # Build normalized doctor object
                normalized = {
                    "id": str(doc.get("number", "")),  # NPI number
                    "name": name,
                    "specialization": specialization,
                    "qualification": credential,
                    "experience_years": 10,  # Not provided by NPPES
                    "rating": 4.5,  # Not provided by NPPES
                    "location": {
                        "latitude": lat,
                        "longitude": lon,
                        "address": address_line,
                        "city": city,
                        "state": state,
                        "pincode": postal_code
                    },
                    "distance_km": 0.0,  # Will be calculated later
                    "phone": phone,
                    "email": None,  # Not provided by NPPES
                    "clinic_name": basic.get("organization_name", "Private Practice"),
                    "consultation_fee": None,  # Not provided by NPPES
                    "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],  # Default
                    "available_hours": "By Appointment",  # Default
                    "languages": ["English"],  # Default
                    "accepts_new_patients": True,  # Default
                    "insurance_accepted": []  # Not provided by NPPES
                }
                
                doctors.append(normalized)
                
            except Exception as e:
                logger.warning(f"Failed to normalize doctor data: {str(e)}")
                continue
        
        return doctors
    
    def _format_name(self, doc: Dict) -> str:
        """Format doctor name from various possible fields"""
        if "name" in doc:
            return doc["name"]
        
        first = doc.get("first_name", doc.get("firstName", ""))
        last = doc.get("last_name", doc.get("lastName", ""))
        prefix = doc.get("prefix", "Dr.")
        
        if first and last:
            return f"{prefix} {first} {last}"
        
        return doc.get("full_name", "Unknown Doctor")
    
    def _parse_available_days(self, availability: Dict) -> List[str]:
        """Parse available days from availability object"""
        if not availability or not isinstance(availability, dict):
            return ["Mon", "Tue", "Wed", "Thu", "Fri"]
        
        days = []
        day_map = {
            "monday": "Mon",
            "tuesday": "Tue",
            "wednesday": "Wed",
            "thursday": "Thu",
            "friday": "Fri",
            "saturday": "Sat",
            "sunday": "Sun"
        }
        
        for day, available in availability.items():
            if available and day.lower() in day_map:
                days.append(day_map[day.lower()])
        
        return days if days else ["Mon", "Tue", "Wed", "Thu", "Fri"]
    
    @staticmethod
    def _miles_to_km(miles: float) -> float:
        """Convert miles to kilometers"""
        return miles * 1.60934
    
    @staticmethod
    def _format_postal_code(raw_postal_code: str) -> str:
        """
        Format postal code from NPPES API format to standard ZIP or ZIP+4
        NPPES returns postal codes as 9 digits without dash (e.g., "852187352")
        Convert to proper format: "85218-7352" or "85218" if only 5 digits
        
        Args:
            raw_postal_code: Raw postal code from NPPES (e.g., "852187352" or "85218")
            
        Returns:
            Formatted postal code (e.g., "85218-7352" or "85218")
        """
        if not raw_postal_code:
            return ""
        
        # Remove any non-digit characters
        clean = ''.join(filter(str.isdigit, raw_postal_code))
        
        # If 9 digits, format as ZIP+4 (XXXXX-XXXX)
        if len(clean) == 9:
            return f"{clean[:5]}-{clean[5:]}"
        
        # If 5 digits or less, return as is
        if len(clean) <= 5:
            return clean
        
        # If 6-8 digits, take first 5 (malformed ZIP+4)
        return clean[:5]
    
    @staticmethod
    def _estimate_coordinates_from_zip(postal_code: str, city: str = "", state: str = "") -> tuple[float, float]:
        """
        Estimate lat/lon coordinates from ZIP code
        Uses approximate ZIP code centroids for major US regions
        This is a rough approximation since NPPES doesn't provide exact coordinates
        
        Args:
            postal_code: ZIP code (can be "85218" or "85218-7352" format)
            
        Returns:
            Tuple of (latitude, longitude)
        """
        # Extract first 5 digits from ZIP code (handles ZIP+4 format like "85218-7352")
        clean_zip = ''.join(filter(str.isdigit, postal_code))[:5]
        
        # Use first 2 digits for regional lookup
        prefix = clean_zip[:2] if len(clean_zip) >= 2 else "00"
        
        # Rough ZIP code prefix to coordinates mapping (US regions)
        # Format: prefix -> (lat, lon) - approximate centroid
        zip_regions = {
            # Northeast
            "10": (40.7128, -74.0060),  # New York, NY
            "11": (40.6782, -73.9442),  # Brooklyn, NY
            "12": (42.6526, -73.7562),  # Albany, NY
            "01": (42.3601, -71.0589),  # Boston, MA
            "02": (42.3601, -71.0589),  # Boston, MA
            "03": (43.2081, -71.5376),  # Manchester, NH
            "04": (43.6591, -70.2568),  # Portland, ME
            "06": (41.7658, -72.6734),  # Hartford, CT
            "07": (40.7282, -74.0776),  # Newark, NJ
            "08": (40.2206, -74.7597),  # Trenton, NJ
            "19": (39.9526, -75.1652),  # Philadelphia, PA
            
            # Southeast
            "20": (38.9072, -77.0369),  # Washington, DC
            "21": (39.2904, -76.6122),  # Baltimore, MD
            "22": (38.8048, -77.0469),  # Arlington, VA
            "23": (37.5407, -77.4360),  # Richmond, VA
            "27": (35.7796, -78.6382),  # Raleigh, NC
            "28": (35.2271, -80.8431),  # Charlotte, NC
            "29": (32.7765, -79.9311),  # Charleston, SC
            "30": (33.7490, -84.3880),  # Atlanta, GA
            "32": (30.3322, -81.6557),  # Jacksonville, FL
            "33": (25.7617, -80.1918),  # Miami, FL
            "34": (28.5383, -81.3792),  # Orlando, FL
            
            # Midwest
            "43": (39.9612, -82.9988),  # Columbus, OH
            "44": (41.4993, -81.6944),  # Cleveland, OH
            "45": (39.1031, -84.5120),  # Cincinnati, OH
            "46": (39.7684, -86.1581),  # Indianapolis, IN
            "47": (41.5868, -87.3468),  # Gary, IN
            "48": (42.3314, -83.0458),  # Detroit, MI
            "49": (42.9634, -85.6681),  # Grand Rapids, MI
            "50": (41.5868, -93.6250),  # Des Moines, IA
            "51": (41.5868, -93.6250),  # Des Moines, IA (extended)
            "52": (43.5460, -96.7313),  # Sioux Falls, SD
            "53": (43.0389, -87.9065),  # Milwaukee, WI
            "54": (44.5192, -88.0198),  # Green Bay, WI
            "55": (44.9778, -93.2650),  # Minneapolis, MN
            "56": (44.9778, -93.2650),  # Minneapolis, MN (extended)
            "57": (44.3683, -100.3362),  # Pierre, SD
            "58": (46.8772, -100.7844),  # Bismarck, ND
            "59": (47.5515, -101.0020),  # Minot, ND
            "60": (41.8781, -87.6298),  # Chicago, IL
            "61": (41.5236, -90.5776),  # Rock Island, IL
            "62": (38.6270, -90.1994),  # East St. Louis, IL
            "63": (38.6270, -90.1994),  # St. Louis, MO
            "64": (39.0997, -94.5786),  # Kansas City, MO
            "65": (46.5891, -112.0391),  # Helena, MT
            "66": (37.6872, -97.3301),  # Wichita, KS
            "67": (39.1141, -94.6275),  # Kansas City, KS
            "68": (41.2565, -95.9345),  # Omaha, NE
            "69": (40.8136, -96.7026),  # Lincoln, NE
            "70": (29.9511, -90.0715),  # New Orleans, LA
            "71": (32.5252, -92.0819),  # Monroe, LA
            
            # Southwest
            "73": (35.4676, -97.5164),  # Oklahoma City, OK
            "75": (32.7767, -96.7970),  # Dallas, TX
            "77": (29.7604, -95.3698),  # Houston, TX
            "78": (29.4241, -98.4936),  # San Antonio, TX
            "79": (33.0198, -96.6989),  # Fort Worth, TX
            "85": (33.4484, -112.0740),  # Phoenix, AZ
            "86": (35.1983, -111.6513),  # Flagstaff, AZ
            "87": (35.0844, -106.6504),  # Albuquerque, NM
            "88": (31.7619, -106.4850),  # El Paso, TX
            "89": (39.5296, -119.8138),  # Reno, NV
            
            # West
            "80": (39.7392, -104.9903),  # Denver, CO
            "83": (43.6150, -116.2023),  # Boise, ID
            "84": (40.7608, -111.8910),  # Salt Lake City, UT
            "90": (34.0522, -118.2437),  # Los Angeles, CA
            "91": (34.0522, -118.2437),  # Los Angeles, CA
            "92": (32.7157, -117.1611),  # San Diego, CA
            "93": (36.7783, -119.4179),  # Fresno, CA
            "94": (37.7749, -122.4194),  # San Francisco, CA
            "95": (38.5816, -121.4944),  # Sacramento, CA
            "96": (35.3733, -119.0187),  # Bakersfield, CA
            "97": (45.5152, -122.6784),  # Portland, OR
            "98": (47.6062, -122.3321),  # Seattle, WA
            "99": (47.6588, -117.4260),  # Spokane, WA
        }
        
        # Look up coordinates by 2-digit prefix
        if prefix in zip_regions:
            return zip_regions[prefix]
        
        # Default to center of US if ZIP not found
        return (39.8283, -98.5795)  # Geographic center of USA
    
    async def get_doctor_by_id(self, doctor_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific doctor
        
        Args:
            doctor_id: Doctor ID or NPI number
            
        Returns:
            Doctor details or None
        """
        if not self.api_key:
            logger.error("Cannot get doctor details: API key not configured")
            return None
        
        try:
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.get(
                    f"{self.api_base_url}/doctors/{doctor_id}",
                    headers=headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Normalize single doctor response
                normalized = self._normalize_doctor_data({"doctors": [data]})
                return normalized[0] if normalized else None
                
        except Exception as e:
            logger.error(f"Error fetching doctor {doctor_id}: {str(e)}")
            return None
