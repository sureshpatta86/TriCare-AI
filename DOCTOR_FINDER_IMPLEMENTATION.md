# Doctor Finder Feature Implementation

## Overview
The Doctor Finder feature allows users to search for nearby doctors based on their PIN code and required medical specialization. It provides an interactive map view and detailed doctor information including ratings, contact details, and availability.

**NEW:** The feature now supports **real-time doctor data integration** with external APIs like DoctorsAPI.com. See [External API Setup Guide](./EXTERNAL_API_SETUP.md) for details.

## Features Implemented

### 1. Backend API (FastAPI)

#### New Files Created:
- `/backend/app/schemas/doctors.py` - Pydantic schemas for doctor search
- `/backend/app/services/doctor_finder.py` - Doctor finder service with geocoding
- `/backend/app/services/external_doctor_api.py` - External API integration service
- `/backend/app/api/routes/doctors.py` - API routes for doctor search

#### API Endpoints:

**POST /api/doctors/search**
- Search for doctors based on PIN code and specialization
- Request Body:
  ```json
  {
    "pincode": "560001",
    "specialization": "Cardiologist",
    "radius_km": 10.0
  }
  ```
- Response includes:
  - User location (lat/long, address)
  - List of doctors with full details
  - Distance from user location
  - Doctor ratings, contact info, availability

**GET /api/doctors/specializations**
- Get list of available medical specializations
- Returns sorted list of 15+ specializations

#### Features:
- ✅ PIN code to coordinates geocoding
- ✅ Distance calculation using Haversine formula
- ✅ Doctor search with specialization filtering
- ✅ Radius-based location search (1-50 km)
- ✅ **External API integration with automatic fallback**
- ✅ **Real-time doctor data from DoctorsAPI.com (optional)**
- ✅ Correlation ID tracking for all requests
- ✅ Rate limiting integration
- ✅ Comprehensive error handling

#### Data Sources:
- **Local Sample Data**: 36 doctors across 15 specializations (default)
- **External API**: Real-time doctor data from DoctorsAPI.com (optional)
- **Automatic Fallback**: If external API fails, uses local data
- See [EXTERNAL_API_SETUP.md](./EXTERNAL_API_SETUP.md) for integration guide

#### Sample Doctor Database:
Includes 36 doctors across specializations:
- Cardiologist (2 doctors)
- Neurologist
- Orthopedic
- Dermatologist
- Gastroenterologist
- Pulmonologist
- Endocrinologist

#### Supported Cities (PIN codes):
- Bangalore: 560001-560005
- Mumbai: 400001-400003
- Delhi: 110001-110003
- Chennai: 600001-600002
- Hyderabad: 500001-500002

### 2. Frontend UI (Next.js + React)

#### New Files Created:
- `/frontend/src/types/doctors.ts` - TypeScript type definitions
- `/frontend/src/app/doctors/page.tsx` - Doctor Finder page component

#### UI Components:

**Search Form:**
- PIN code input with validation
- Specialization dropdown (15+ options)
- Search radius slider (1-50 km)
- Real-time search with loading states

**Doctor List (Left Panel):**
- Card-based list view
- Shows: Name, specialization, rating, distance
- Click to select and view details
- Sorted by distance (nearest first)
- Scrollable list with max 600px height

**Map View (Top Right):**
- Visual representation of doctor locations
- Interactive markers (click to select doctor)
- Shows user location
- Highlights selected doctor
- Distance indicators

**Doctor Details (Bottom Right):**
- Complete doctor profile:
  - Name, specialization, qualification
  - Years of experience
  - Star rating (out of 5)
  - Clinic name and address
  - Distance from user
  - Phone and email (clickable)
  - Available days and hours
  - Languages spoken
  - Consultation fee
- Action buttons:
  - "Book Appointment"
  - "Get Directions"

#### Features:
- ✅ Responsive design (mobile + desktop)
- ✅ Dark mode support
- ✅ Progress indicator during search
- ✅ Error handling with user-friendly messages
- ✅ Correlation ID display for support
- ✅ Interactive doctor selection
- ✅ Star rating visualization
- ✅ Clickable phone/email links

### 3. Navigation Updates

#### Updated Files:
- `/frontend/src/components/shared/Header.tsx` - Added "Find Doctors" nav link
- `/frontend/src/app/page.tsx` - Added Doctor Finder feature card
- `/frontend/src/types/index.ts` - Exported doctor types

#### Changes:
- ✅ Added MapPin icon to navigation
- ✅ Updated feature count (3 → 4 features)
- ✅ Changed grid layout (3-col → 4-col on large screens)
- ✅ Added orange/red gradient for Doctor Finder card

## Integration Points

### 1. Symptom Router → Doctor Finder
When a user gets a specialist recommendation from the Symptom Router, they can:
1. Note the recommended specialization
2. Navigate to Doctor Finder
3. Enter their PIN code
4. Select the recommended specialization
5. Find nearby doctors instantly

### 2. Report Simplifier → Doctor Finder
After simplifying a medical report, users can:
1. Understand their condition
2. Identify required specialist from report
3. Use Doctor Finder to locate specialists
4. Book appointment with relevant doctor

### 3. Imaging Pre-Screen → Doctor Finder
After X-ray analysis, users can:
1. Review preliminary findings
2. Get specialist recommendation
3. Search for radiologists or relevant specialists
4. Schedule follow-up consultations

## Technical Implementation

### Geocoding Service:
```python
def geocode_pincode(pincode: str) -> Tuple[lat, lon, city, state]
```
- Maps PIN codes to geographic coordinates
- Returns city and state for address display
- Falls back to default location if PIN not found

### Distance Calculation:
```python
def calculate_distance(lat1, lon1, lat2, lon2) -> float
```
- Uses Haversine formula for accurate distance
- Returns distance in kilometers
- Accounts for Earth's curvature

### Location Generation:
```python
def generate_doctor_locations(center_lat, center_lon, radius_km, count)
```
- Generates random doctor locations within search radius
- Creates realistic addresses with street names
- Distributes doctors evenly around user location

## Future Enhancements

### Phase 2 (Planned):
1. **Real Map Integration:**
   - Google Maps or Leaflet.js
   - Turn-by-turn directions
   - Street view of clinics

2. **Appointment Booking:**
   - Real-time availability calendar
   - Online booking system
   - Appointment confirmation emails

3. **Reviews & Ratings:**
   - Patient reviews
   - Verified ratings
   - Doctor response to reviews

4. **Advanced Filters:**
   - Insurance acceptance
   - Gender preference
   - Clinic facilities
   - Consultation mode (in-person/video)

5. **Database Integration:**
   - Real doctor database (PostgreSQL/MongoDB)
   - API integration with healthcare directories
   - Live availability updates

6. **Enhanced Geocoding:**
   - Google Geocoding API
   - Reverse geocoding (lat/long → address)
   - Auto-complete for locations

7. **User Features:**
   - Save favorite doctors
   - View booking history
   - Receive appointment reminders

## Usage Example

### User Journey:
1. User enters symptoms → Gets "Cardiologist" recommendation
2. Clicks "Find Doctors" in navigation
3. Enters PIN code: "560001"
4. Selects specialization: "Cardiologist"
5. Clicks "Search Doctors"
6. Views 2 cardiologists on map and list
7. Clicks on "Dr. Arjun Malhotra" (4.9 rating, 3.2 km away)
8. Reviews full profile with contact info
9. Calls clinic or clicks "Book Appointment"

### API Request Flow:
```
User Input → Frontend Validation → API Call
  ↓
POST /api/doctors/search
  ↓
Backend Processing:
  - Geocode PIN code
  - Filter by specialization
  - Calculate distances
  - Sort by proximity
  ↓
JSON Response → Frontend Display
  ↓
Interactive Map + Doctor Cards
```

## Testing

### Backend Tests:
```bash
cd backend
pytest tests/test_doctors_api.py
```

### Frontend Testing:
1. Navigate to http://localhost:3001/doctors
2. Test PIN codes: 560001, 400001, 110001
3. Test specializations: Cardiologist, Neurologist
4. Test radius: 5km, 10km, 20km
5. Click through doctor cards
6. Verify phone/email links work

### Test Cases:
- ✅ Valid PIN code + valid specialization
- ✅ Invalid PIN code (falls back to default)
- ✅ Specialization with no doctors (shows all)
- ✅ Different radius values
- ✅ Dark mode rendering
- ✅ Mobile responsiveness
- ✅ Error handling (network failures)

## Production Checklist

Before deploying to production:
- [ ] Replace sample doctor data with real database
- [ ] Integrate real geocoding API (Google/Mapbox)
- [ ] Add actual map library (Leaflet/Google Maps)
- [ ] Implement real appointment booking system
- [ ] Add authentication for bookings
- [ ] Set up monitoring and analytics
- [ ] Add rate limiting per user (not just IP)
- [ ] Implement caching for frequent searches
- [ ] Add GDPR compliance for user data
- [ ] Set up backup and disaster recovery

## API Documentation

Full API documentation available at:
- Development: http://localhost:8011/api/docs
- Interactive docs: http://localhost:8011/api/redoc

## Support

For issues or questions:
- Check correlation ID in response
- View backend logs for debugging
- Contact support with request ID

---

**Implementation Date:** October 21, 2025  
**Status:** ✅ Complete and Ready for Testing  
**Branch:** `adding-mapping`
