# JWT Authentication Integration Guide

## Overview

This trends module now supports JWT token authentication using AWS Cognito. Each user's data is isolated, ensuring that users only see their own trending data.

## Architecture

```
Main Platform (Frontend)
    ↓
[JWT Token from Cognito]
    ↓
Trends Module API (with JWT verification)
    ↓
MongoDB (user-specific data)
```

## Setup Instructions

### 1. Configure Environment Variables

Add these to your `.env` file:

```bash
# AWS Cognito Configuration
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=your_app_client_id_here
```

**How to get these values:**
1. Go to AWS Console → Cognito
2. Select your User Pool
3. **COGNITO_REGION**: e.g., `us-east-1`
4. **COGNITO_USER_POOL_ID**: Found in "User pool overview" (format: `region_XXXXXXXXX`)
5. **COGNITO_CLIENT_ID**: Go to "App integration" tab → "App clients" → Copy the "Client ID"

### 2. Frontend Integration

#### JavaScript/TypeScript Example

```javascript
// After user logs in to your main platform, you'll have a JWT token
const jwtToken = localStorage.getItem('auth_token'); // or from your auth state

// Call trends API with Bearer token
const response = await fetch('https://your-trends-api.com/unified-trends', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    country_code: 'US',
    category: 'technology',
    time_range: '7d',
    max_results_per_platform: 10,
    limit: 25
  })
});

const trendsData = await response.json();
```

#### React Example with Axios

```javascript
import axios from 'axios';

// Create axios instance with auth interceptor
const trendsAPI = axios.create({
  baseURL: 'https://your-trends-api.com',
});

// Add auth token to every request
trendsAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Use it
const fetchUnifiedTrends = async () => {
  try {
    const response = await trendsAPI.post('/unified-trends', {
      country_code: 'US',
      category: 'technology',
      time_range: '7d'
    });
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      console.error('Authentication failed');
    }
    throw error;
  }
};
```

### 3. How Authentication Works

1. **User logs into your main platform** (Google Sign-In or email/password)
2. **Main platform issues JWT token** from AWS Cognito
3. **Frontend stores JWT token** (localStorage, sessionStorage, or state management)
4. **Frontend makes API calls to trends module** with token in `Authorization: Bearer <token>` header
5. **Trends module verifies token** using Cognito's JWKS (public keys)
6. **Trends module extracts user_id** from token (`sub` claim)
7. **All data saved to MongoDB includes user_id** for isolation

### 4. JWT Token Structure

The JWT token from Cognito contains:

```json
{
  "sub": "user-uuid-here",  // ← This becomes user_id
  "cognito:username": "john.doe",
  "email": "john@example.com",
  "given_name": "John",
  "family_name": "Doe",
  "cognito:groups": ["admin"],
  "exp": 1234567890,  // Expiration timestamp
  "iat": 1234567890   // Issued at timestamp
}
```

### 5. Data Isolation

All MongoDB collections now include `user_id` field:

**Before (shared data):**
```json
{
  "_id": "uuid",
  "query": "AI trends",
  "country_code": "US",
  "search_volume": 100000
}
```

**After (user-specific data):**
```json
{
  "_id": "uuid",
  "user_id": "cognito-user-uuid",  // ← New field
  "query": "AI trends",
  "country_code": "US",
  "search_volume": 100000,
  "created_at": "2025-01-14T10:00:00Z"
}
```

### 6. API Endpoints (All require authentication)

All POST endpoints now require the `Authorization: Bearer <token>` header:

- `POST /google-trends` - Get Google Trends data
- `POST /youtube-trends` - Get YouTube trending videos
- `POST /tiktok-trends` - Get TikTok trending data
- `POST /unified-trends` - Get unified scores across all platforms
- `POST /google-trends/details` - Get detailed Google Trends analysis
- `POST /youtube/details` - Get detailed YouTube video info
- `POST /tiktok/details` - Get detailed TikTok item info

**Public endpoints (no auth required):**
- `GET /` - Root endpoint
- `GET /health` - Health check

### 7. Error Handling

**401 Unauthorized:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

Causes:
- Missing Authorization header
- Invalid JWT token
- Expired token
- Token from different Cognito pool

**503 Service Unavailable:**
```json
{
  "detail": "Authentication service not configured"
}
```

Causes:
- Missing Cognito environment variables

### 8. Testing Authentication

#### Test with cURL:

```bash
# Replace YOUR_JWT_TOKEN with actual token
curl -X POST https://your-trends-api.com/unified-trends \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "country_code": "US",
    "category": "technology",
    "time_range": "7d"
  }'
```

#### Decode JWT Token (for debugging):

Go to https://jwt.io/ and paste your token to see the decoded payload.

### 9. Security Best Practices

1. **Always use HTTPS** in production
2. **Never log JWT tokens** in production
3. **Store tokens securely** in frontend (httpOnly cookies preferred over localStorage)
4. **Handle token expiration** gracefully (refresh tokens if available)
5. **Update CORS settings** to only allow your frontend domain:

```python
# In main.py, update CORS middleware:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-main-platform.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 10. Deployment Checklist

- [ ] Set Cognito environment variables on hosting platform
- [ ] Update CORS to allow your frontend domain
- [ ] Ensure MongoDB connection string is set
- [ ] Test authentication with real JWT token from your main platform
- [ ] Verify data isolation (users can only see their own data)
- [ ] Set up SSL/HTTPS certificate
- [ ] Monitor authentication errors in logs

## Troubleshooting

### Problem: "Invalid authentication credentials"
**Solution:**
- Verify token is from the correct Cognito User Pool
- Check `COGNITO_USER_POOL_ID` and `COGNITO_CLIENT_ID` are correct
- Ensure token hasn't expired

### Problem: "Unable to verify authentication" (503)
**Solution:**
- Check network connectivity to Cognito JWKS endpoint
- Verify `COGNITO_REGION` is correct

### Problem: Users see each other's data
**Solution:**
- Ensure all storage calls include `user_id`
- Check MongoDB queries include `user_id` filter
- Verify JWT token is being properly decoded

## Support

For issues or questions:
1. Check server logs for detailed error messages
2. Verify environment variables are set correctly
3. Test JWT token at https://jwt.io/
4. Ensure Cognito User Pool allows your Client ID
