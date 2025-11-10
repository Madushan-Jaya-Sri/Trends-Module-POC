# How to Start the Server

## Quick Start

### From the `backend` directory:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### From the project root directory:
```bash
cd /Users/jayasri/Documents/Trends-Module-POC
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Access the API

Once the server is running, you can access:

- **API Base URL**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Test the Category Filtering

### Using curl:

**Google Trends with Technology Category:**
```bash
curl -X POST "http://localhost:8000/google-trends" \
  -H "Content-Type: application/json" \
  -d '{"country_code": "US", "category": "science_technology"}'
```

**TikTok with Gaming Category:**
```bash
curl -X POST "http://localhost:8000/tiktok-trends" \
  -H "Content-Type: application/json" \
  -d '{"country_code": "MY", "category": "gaming", "results_per_page": 10, "time_range": "7"}'
```

**YouTube with Entertainment Category:**
```bash
curl -X POST "http://localhost:8000/youtube-trends" \
  -H "Content-Type: application/json" \
  -d '{"country_code": "US", "category": "entertainment", "max_results": 10}'
```

### Using the Python test script:

```bash
# First, uncomment the test function calls in test_categories.py
# Then run:
python test_categories.py
```

## Available Categories

All endpoints support these unified categories:
- `automotive`
- `beauty_fashion`
- `business_finance`
- `climate_environment`
- `entertainment`
- `food_drink`
- `gaming`
- `health_fitness`
- `hobbies_lifestyle`
- `education_careers`
- `law_politics`
- `other_misc`
- `pets_animals`
- `science_technology`
- `shopping`
- `sports`
- `travel`
- `arts_media`

See [CATEGORY_USAGE.md](CATEGORY_USAGE.md) for detailed documentation.

## Troubleshooting

If you encounter import errors:
1. Make sure you're running the command from the correct directory
2. Ensure your virtual environment is activated
3. Verify all dependencies are installed: `pip install -r requirements.txt`

If the server won't start:
1. Check if port 8000 is already in use: `lsof -i :8000`
2. Kill any existing process: `kill -9 <PID>`
3. Or use a different port: `--port 8001`
