# Category Filtering Implementation

## Overview
The Trends Module now supports unified category filtering across all three platforms (Google Trends, TikTok, and YouTube). This allows you to fetch trending content filtered by specific categories using a single, unified category system.

## Unified Categories

The following unified categories are available:

| Unified Category | Value | Google Trends | TikTok | YouTube |
|-----------------|-------|---------------|---------|----------|
| Automotive | `automotive` | ✓ | ✓ | ✓ |
| Beauty & Fashion | `beauty_fashion` | ✓ | ✓ | ✓ |
| Business & Finance | `business_finance` | ✓ | ✓ | ✓ |
| Climate & Environment | `climate_environment` | ✓ | ✗ | ✗ |
| Entertainment | `entertainment` | ✓ | ✓ | ✓ |
| Food & Drink | `food_drink` | ✓ | ✓ | ✓ |
| Gaming | `gaming` | ✓ | ✓ | ✓ |
| Health & Fitness | `health_fitness` | ✓ | ✓ | ✓ |
| Hobbies & Lifestyle | `hobbies_lifestyle` | ✓ | ✓ | ✓ |
| Education & Careers | `education_careers` | ✓ | ✓ | ✓ |
| Law & Politics | `law_politics` | ✓ | ✗ | ✓ |
| Other / Misc | `other_misc` | ✓ | ✗ | ✗ |
| Pets & Animals | `pets_animals` | ✓ | ✓ | ✓ |
| Science & Technology | `science_technology` | ✓ | ✓ | ✓ |
| Shopping | `shopping` | ✓ | ✓ | ✓ |
| Sports | `sports` | ✓ | ✓ | ✓ |
| Travel | `travel` | ✓ | ✓ | ✓ |
| Arts & Media | `arts_media` | ✗ | ✗ | ✓ |

**Note**: ✓ = Supported, ✗ = Not supported (will fetch all trends for that platform)

## API Usage Examples

### 1. Google Trends with Category

**Request:**
```bash
curl -X POST "http://localhost:8000/google-trends" \
  -H "Content-Type: application/json" \
  -d '{
    "country_code": "US",
    "category": "science_technology"
  }'
```

**Response:**
```json
{
  "country": "US",
  "timestamp": "2025-11-10T14:30:00.000Z",
  "total_trends": 15,
  "trending_searches": [
    {
      "query": "ChatGPT update",
      "traffic": "+5,000%",
      "started": "Nov 10, 02:30 PM UTC",
      "started_ago": "2h 15m"
    }
  ]
}
```

### 2. TikTok Trends with Category

**Request:**
```bash
curl -X POST "http://localhost:8000/tiktok-trends" \
  -H "Content-Type: application/json" \
  -d '{
    "country_code": "MY",
    "results_per_page": 10,
    "time_range": "7",
    "category": "gaming"
  }'
```

**Response:**
```json
{
  "country": "MY",
  "timestamp": "2025-11-10T14:30:00.000Z",
  "hashtags": [
    {
      "name": "#mobilelegends",
      "rank": 1,
      "viewCount": 1500000000,
      "industryName": "Games"
    }
  ],
  "creators": [...],
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

### 3. YouTube Trends with Category

**Request:**
```bash
curl -X POST "http://localhost:8000/youtube-trends" \
  -H "Content-Type: application/json" \
  -d '{
    "country_code": "US",
    "max_results": 10,
    "category": "entertainment"
  }'
```

**Response:**
```json
{
  "country": "US",
  "timestamp": "2025-11-10T14:30:00.000Z",
  "total_videos": 10,
  "videos": [
    {
      "id": "dQw4w9WgXcQ",
      "title": "Trending Entertainment Video",
      "channelTitle": "Popular Channel",
      "categoryId": "24",
      "viewCount": 10000000,
      "likeCount": 500000
    }
  ]
}
```

### 4. Without Category (Default Behavior)

All endpoints support optional category filtering. If no category is provided:
- **Google Trends**: Returns all trending searches
- **TikTok**: Defaults to `shopping` category (Apparel & Accessories)
- **YouTube**: Returns all trending videos

**Example (no category):**
```bash
curl -X POST "http://localhost:8000/youtube-trends" \
  -H "Content-Type: application/json" \
  -d '{
    "country_code": "US",
    "max_results": 10
  }'
```

## Frontend Integration

For frontend dropdown implementation, you can fetch the available categories:

```javascript
// Available unified categories for dropdown
const categories = [
  { value: 'automotive', label: 'Automotive' },
  { value: 'beauty_fashion', label: 'Beauty & Fashion' },
  { value: 'business_finance', label: 'Business & Finance' },
  { value: 'climate_environment', label: 'Climate & Environment' },
  { value: 'entertainment', label: 'Entertainment' },
  { value: 'food_drink', label: 'Food & Drink' },
  { value: 'gaming', label: 'Gaming' },
  { value: 'health_fitness', label: 'Health & Fitness' },
  { value: 'hobbies_lifestyle', label: 'Hobbies & Lifestyle' },
  { value: 'education_careers', label: 'Education & Careers' },
  { value: 'law_politics', label: 'Law & Politics' },
  { value: 'other_misc', label: 'Other / Misc' },
  { value: 'pets_animals', label: 'Pets & Animals' },
  { value: 'science_technology', label: 'Science & Technology' },
  { value: 'shopping', label: 'Shopping' },
  { value: 'sports', label: 'Sports' },
  { value: 'travel', label: 'Travel' },
  { value: 'arts_media', label: 'Arts & Media' }
];

// Example API call with category
async function fetchTrends(platform, category) {
  const endpoints = {
    google: '/google-trends',
    tiktok: '/tiktok-trends',
    youtube: '/youtube-trends'
  };

  const response = await fetch(`http://localhost:8000${endpoints[platform]}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      country_code: 'US',
      category: category || null
    })
  });

  return await response.json();
}
```

## Platform-Specific Category Mappings

### Google Trends Categories
The system maps unified categories to Google Trends category IDs (1-20).

### TikTok Categories
Maps to TikTok industry names like:
- "Apparel & Accessories" (Shopping)
- "Games" (Gaming)
- "Tech & Electronics" (Science & Technology)
- etc.

### YouTube Categories
Maps to YouTube category IDs like:
- "24" (Entertainment)
- "20" (Gaming)
- "28" (Science & Technology)
- etc.

Some categories map to multiple YouTube IDs (e.g., Arts & Media maps to Film, Music, Comedy, Movies, etc.)

## Notes

1. **Backward Compatibility**: All endpoints remain backward compatible. Existing API calls without the category parameter will work as before.

2. **Unsupported Categories**: If a category is not supported by a specific platform, the service will log a warning and fetch all trending content for that platform.

3. **TikTok Default**: TikTok previously had a hardcoded category of "Apparel & Accessories". Now it defaults to the `shopping` unified category, which maintains the same behavior but can be changed.

4. **Validation**: The category parameter is validated using Pydantic enums, ensuring only valid categories are accepted.

## File Structure

```
backend/app/
├── constants/
│   ├── __init__.py
│   └── categories.py          # Unified category definitions and mappings
├── models/
│   └── schemas.py             # Updated with category parameter
├── services/
│   ├── google_trends_service.py  # Updated with category support
│   ├── tiktok_service.py         # Updated with category support
│   └── youtube_service.py        # Updated with category support
└── main.py                    # Updated endpoints with category support
```
