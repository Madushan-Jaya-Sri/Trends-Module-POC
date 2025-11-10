# Social Media Trends API

A FastAPI backend for fetching trending content from Google Trends, TikTok, and YouTube. This API provides separate endpoints for each platform, making it easy to integrate with any frontend application.

**Note:** This is for POC only. Implementation will be expected in the Momentro Product.

## Features

- **Google Trends**: Fetch trending searches with timestamps and search volumes
- **TikTok Trends**: Get trending hashtags, creators, sounds, and videos
- **YouTube Trends**: Retrieve trending videos with comprehensive metadata

## Project Structure

```
Trends-Module-POC/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI application
│       ├── config.py            # Configuration management
│       ├── models/
│       │   └── schemas.py       # Pydantic models
│       └── services/
│           ├── google_trends_service.py
│           ├── tiktok_service.py
│           └── youtube_service.py
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Trends-Module-POC
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```env
SERPAPI_API_KEY="your_serpapi_key"
APIFY_API_KEY="your_apify_key"
YOUTUBE_API_KEY="your_youtube_key"
```

## Running the Server

### Development Mode
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the provided run script:
```bash
./run.sh
```

### Production Mode
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
**GET** `/health`

Check the health status of the API and its services.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-10T12:00:00.000000Z",
  "services": {
    "google_trends": "initialized",
    "tiktok": "initialized",
    "youtube": "initialized"
  }
}
```

---

### Google Trends

**POST** `/google-trends`

Fetch trending searches from Google Trends.

**Request Body:**
```json
{
  "country_code": "US"
}
```

**Response:**
```json
{
  "country": "US",
  "timestamp": "2025-11-10T12:00:00.000000Z",
  "total_trends": 15,
  "trending_searches": [
    {
      "query": "example search",
      "start_timestamp": 1762698600,
      "active": true,
      "search_volume": 500,
      "increase_percentage": 1000,
      "categories": [{"id": 17, "name": "Sports"}],
      "started": "Nov 09, 03:30 PM UTC",
      "started_ago": "2h 30m",
      "lasted_for": null,
      "serpapi_google_trends_link": "...",
      "news_page_token": "..."
    }
  ]
}
```

---

### TikTok Trends

**POST** `/tiktok-trends`

Get trending data from TikTok including hashtags, creators, sounds, and videos.

**Request Body:**
```json
{
  "country_code": "MY",
  "results_per_page": 10,
  "time_range": "7"
}
```

**Response:**
```json
{
  "country": "MY",
  "timestamp": "2025-11-10T12:00:00.000000Z",
  "hashtags": [
    {
      "name": "example",
      "countryCode": "MY",
      "rank": 1,
      "trendingHistogram": [...],
      "url": "https://www.tiktok.com/tag/example",
      "videoCount": 1000,
      "viewCount": 5000000,
      "industryName": "Entertainment",
      "relatedCreators": [...]
    }
  ],
  "creators": [
    {
      "name": "Creator Name",
      "avatar": "...",
      "followerCount": 1000000,
      "likedCount": 5000000,
      "url": "...",
      "rank": 1,
      "relatedVideos": [...]
    }
  ],
  "sounds": [...],
  "videos": [...],
  "total_items": {
    "hashtags": 10,
    "creators": 10,
    "sounds": 10,
    "videos": 10
  }
}
```

---

### YouTube Trends

**POST** `/youtube-trends`

Fetch trending videos from YouTube.

**Request Body:**
```json
{
  "country_code": "US",
  "max_results": 10
}
```

**Response:**
```json
{
  "country": "US",
  "timestamp": "2025-11-10T12:00:00.000000Z",
  "total_videos": 10,
  "videos": [
    {
      "id": "video_id",
      "title": "Video Title",
      "channelTitle": "Channel Name",
      "publishedAt": "2025-11-09T10:00:00Z",
      "thumbnail_url_standard": "...",
      "description": "...",
      "tags": ["tag1", "tag2"],
      "duration_sec": 300,
      "viewCount": 1000000,
      "likeCount": 50000,
      "commentCount": 1000,
      "categoryId": "10",
      "...": "..."
    }
  ]
}
```

## Testing the API

### Using curl

**Test Health:**
```bash
curl http://localhost:8000/health
```

**Google Trends:**
```bash
curl -X POST http://localhost:8000/google-trends \
  -H "Content-Type: application/json" \
  -d '{"country_code": "US"}'
```

**TikTok Trends:**
```bash
curl -X POST http://localhost:8000/tiktok-trends \
  -H "Content-Type: application/json" \
  -d '{"country_code": "MY", "results_per_page": 10, "time_range": "7"}'
```

**YouTube Trends:**
```bash
curl -X POST http://localhost:8000/youtube-trends \
  -H "Content-Type: application/json" \
  -d '{"country_code": "US", "max_results": 10}'
```

### Using Python requests

```python
import requests

# Google Trends
response = requests.post(
    "http://localhost:8000/google-trends",
    json={"country_code": "US"}
)
print(response.json())

# TikTok Trends
response = requests.post(
    "http://localhost:8000/tiktok-trends",
    json={
        "country_code": "MY",
        "results_per_page": 10,
        "time_range": "7"
    }
)
print(response.json())

# YouTube Trends
response = requests.post(
    "http://localhost:8000/youtube-trends",
    json={
        "country_code": "US",
        "max_results": 10
    }
)
print(response.json())
```

## Country Codes

Use two-letter ISO 3166-1 alpha-2 country codes:
- `US` - United States
- `GB` - United Kingdom
- `CA` - Canada
- `AU` - Australia
- `IN` - India
- `MY` - Malaysia
- `LK` - Sri Lanka
- `DE` - Germany
- `FR` - France
- `JP` - Japan
- And more...

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

All endpoints return structured error responses:

```json
{
  "error": "Error message",
  "status_code": 500,
  "timestamp": "2025-11-10T12:00:00.000000Z"
}
```

## License

This project is a POC (Proof of Concept) for educational purposes.

## API Keys Required

1. **SerpAPI**: For Google Trends data - [Get API Key](https://serpapi.com/)
2. **Apify**: For TikTok data - [Get API Key](https://apify.com/)
3. **YouTube Data API**: For YouTube trends - [Get API Key](https://console.cloud.google.com/)
