# External Doctor API Integration Guide

This document explains how to integrate the TriCare AI application with the DoctorsAPI.com service for real-time doctor data.

## Overview

The application now supports both **local sample data** (default) and **external API integration** (optional). This allows you to:
- Start quickly with demo data
- Upgrade to real doctor data when ready
- Automatically fallback to local data if API fails

## Quick Start

### Option 1: Use Sample Data (Default)
No configuration needed. The application works out-of-the-box with 36 sample doctors.

### Option 2: Enable External API

1. **Sign up for DoctorsAPI.com**
   - Visit https://doctorsapi.com
   - Create an account
   - Get your API key from the dashboard

2. **Configure Environment Variables**
   
   Add to `backend/.env`:
   ```bash
   # External Doctor API Configuration
   USE_EXTERNAL_DOCTOR_API=true
   DOCTORS_API_KEY=your_api_key_here
   DOCTORS_API_BASE_URL=https://api.doctorsapi.com/v1
   ```

3. **Restart Backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8011
   ```

4. **Verify Integration**
   Check the logs for:
   ```
   INFO: External Doctor API integration enabled
   INFO: Successfully fetched X doctors from external API
   ```

## API Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_EXTERNAL_DOCTOR_API` | No | `false` | Enable external API (`true`/`false`) |
| `DOCTORS_API_KEY` | Yes* | - | Your DoctorsAPI.com API key |
| `DOCTORS_API_BASE_URL` | No | `https://api.doctorsapi.com/v1` | API base URL |

*Required only if `USE_EXTERNAL_DOCTOR_API=true`

### Example Configuration

```bash
# Development (.env)
USE_EXTERNAL_DOCTOR_API=true
DOCTORS_API_KEY=sk_test_abc123xyz789
DOCTORS_API_BASE_URL=https://api.doctorsapi.com/v1

# Production (.env.production)
USE_EXTERNAL_DOCTOR_API=true
DOCTORS_API_KEY=sk_live_xyz789abc123
DOCTORS_API_BASE_URL=https://api.doctorsapi.com/v1
```

## API Integration Details

### Data Normalization

The external API response is automatically normalized to match our internal schema. The service handles various response formats:

**Supported Field Mappings:**
```python
# Name fields
name, first_name + last_name, full_name

# Location fields
lat/latitude, lon/longitude
address/street_address
zip/postal_code/pincode

# Specialty fields
specialty, specialization

# Rating fields
rating, average_rating

# Distance fields
distance, distance_miles (auto-converted to km)
```

### Automatic Fallback

If the external API fails for any reason, the system automatically falls back to local sample data:

```
INFO: Attempting to fetch doctors from external API
WARNING: External API failed, falling back to local data
INFO: Using local sample doctor data
```

**Fallback triggers:**
- API key missing/invalid
- Network timeout (30 seconds)
- API returns error status
- No results found
- Data parsing error

## Testing

### Test Local Data
```bash
# Ensure external API is disabled
export USE_EXTERNAL_DOCTOR_API=false

# Run tests
cd backend
pytest tests/test_doctors_api.py -v
```

### Test External API
```bash
# Enable external API
export USE_EXTERNAL_DOCTOR_API=true
export DOCTORS_API_KEY=your_test_key

# Run tests
pytest tests/test_doctors_api.py -v
```

### Manual Testing

**Test search endpoint:**
```bash
curl -X POST "http://localhost:8011/api/doctors/search" \
  -H "Content-Type: application/json" \
  -d '{
    "pincode": "560001",
    "specialization": "Cardiology",
    "radius_km": 10
  }'
```

## API Response Format

The external API should return data in one of these formats:

**Format 1: Doctors array**
```json
{
  "doctors": [
    {
      "id": "12345",
      "name": "Dr. John Smith",
      "specialty": "Cardiology",
      "lat": 12.9716,
      "lon": 77.5946,
      ...
    }
  ]
}
```

**Format 2: Data array**
```json
{
  "data": [
    {
      "npi": "1234567890",
      "first_name": "John",
      "last_name": "Smith",
      "credentials": "MD",
      ...
    }
  ]
}
```

## Monitoring

### Logs

Check logs for API integration status:

```bash
# Success
INFO: External Doctor API integration enabled
INFO: Calling external API: https://api.doctorsapi.com/v1/doctors/search
INFO: Fetched 15 doctors from external API

# Fallback
WARNING: External API returned no results, falling back to local data

# Errors
ERROR: HTTP error from external API: 401 - Unauthorized
ERROR: Cannot search doctors: API key not configured
```

### Health Check

The API includes detailed logging with correlation IDs for tracking requests:

```
INFO: [CID: abc-123] Searching doctors for pincode: 560001
INFO: [CID: abc-123] Attempting to fetch doctors from external API
INFO: [CID: abc-123] Successfully fetched 12 doctors from external API
```

## Troubleshooting

### Issue: "Cannot search doctors: API key not configured"

**Solution:**
```bash
# Add to backend/.env
DOCTORS_API_KEY=your_api_key_here
USE_EXTERNAL_DOCTOR_API=true

# Restart server
```

### Issue: "HTTP error from external API: 401 - Unauthorized"

**Causes:**
- Invalid API key
- Expired API key
- API key not activated

**Solution:**
1. Verify API key in DoctorsAPI.com dashboard
2. Check key is correctly set in .env
3. Ensure no extra spaces in .env file

### Issue: "Request error calling external API"

**Causes:**
- Network connectivity issues
- API endpoint down
- Firewall blocking requests

**Solution:**
1. Check internet connection
2. Test API directly: `curl https://api.doctorsapi.com/v1/health`
3. Check firewall settings

### Issue: External API returns no doctors

**Causes:**
- No doctors in search radius
- Wrong specialty name
- Geographic limitations

**Solution:**
- Increase search radius
- Check specialty spelling (use `/api/doctors/specializations`)
- Verify API covers your geographic region

## Alternative APIs

If DoctorsAPI.com doesn't meet your needs, the integration is designed to work with any similar doctor directory API. To use a different API:

1. **Update ExternalDoctorAPIService** (`backend/app/services/external_doctor_api.py`)
   - Modify authentication method
   - Update API endpoints
   - Adjust response normalization

2. **Update environment variables**
   ```bash
   DOCTORS_API_BASE_URL=https://api.alternative-provider.com/v2
   ```

## Cost Considerations

- **Free Tier**: Most APIs offer free tier (100-1000 requests/month)
- **Caching**: Implement Redis caching to reduce API calls
- **Rate Limiting**: Backend includes rate limiting to prevent quota exhaustion

**Recommended caching strategy:**
```python
# Cache doctor search results for 5 minutes
# Cache location data for 24 hours
# Cache specializations list for 7 days
```

## Security Best Practices

1. **Never commit API keys**
   ```bash
   # .gitignore already includes:
   .env
   .env.*
   ```

2. **Use environment-specific keys**
   - Development: Use test/sandbox keys
   - Production: Use live keys with IP restrictions

3. **Rotate keys regularly**
   - Set up key rotation every 90 days
   - Monitor for unauthorized usage

4. **Limit API key scope**
   - Only grant read permissions
   - Restrict to necessary endpoints

## Support

For issues with:
- **DoctorsAPI.com**: Contact support@doctorsapi.com
- **TriCare AI Integration**: Open GitHub issue at https://github.com/sureshpatta86/TriCare-AI/issues

## Future Enhancements

Planned improvements:
- [ ] Redis caching for API responses
- [ ] Rate limiting per user
- [ ] Multiple API provider support
- [ ] Offline mode with cached data
- [ ] Real-time availability checking
- [ ] Appointment booking integration
- [ ] Doctor profile photos
- [ ] Patient reviews integration
