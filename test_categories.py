"""
Test script to verify category filtering implementation
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_google_trends_with_category():
    """Test Google Trends endpoint with category"""
    print("\n=== Testing Google Trends with Category ===")

    payload = {
        "country_code": "US",
        "category": "science_technology"
    }

    try:
        response = requests.post(f"{BASE_URL}/google-trends", json=payload)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total Trends: {data.get('total_trends')}")
            print(f"Country: {data.get('country')}")
            print("✓ Google Trends with category - SUCCESS")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")


def test_tiktok_with_category():
    """Test TikTok endpoint with category"""
    print("\n=== Testing TikTok with Category ===")

    payload = {
        "country_code": "MY",
        "results_per_page": 5,
        "time_range": "7",
        "category": "gaming"
    }

    try:
        response = requests.post(f"{BASE_URL}/tiktok-trends", json=payload)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total Hashtags: {data.get('total_items', {}).get('hashtags')}")
            print(f"Total Creators: {data.get('total_items', {}).get('creators')}")
            print(f"Country: {data.get('country')}")

            # Show first hashtag industry if available
            if data.get('hashtags'):
                first_hashtag = data['hashtags'][0]
                print(f"First Hashtag Industry: {first_hashtag.get('industryName')}")

            print("✓ TikTok with category - SUCCESS")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")


def test_youtube_with_category():
    """Test YouTube endpoint with category"""
    print("\n=== Testing YouTube with Category ===")

    payload = {
        "country_code": "US",
        "max_results": 5,
        "category": "entertainment"
    }

    try:
        response = requests.post(f"{BASE_URL}/youtube-trends", json=payload)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total Videos: {data.get('total_videos')}")
            print(f"Country: {data.get('country')}")

            # Show category IDs of fetched videos
            if data.get('videos'):
                categories = set(video.get('categoryId') for video in data['videos'])
                print(f"Video Category IDs: {categories}")

            print("✓ YouTube with category - SUCCESS")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")


def test_youtube_without_category():
    """Test YouTube endpoint without category (default behavior)"""
    print("\n=== Testing YouTube without Category ===")

    payload = {
        "country_code": "US",
        "max_results": 5
    }

    try:
        response = requests.post(f"{BASE_URL}/youtube-trends", json=payload)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total Videos: {data.get('total_videos')}")
            print("✓ YouTube without category - SUCCESS")
        else:
            print(f"✗ Error: {response.text}")
    except Exception as e:
        print(f"✗ Exception: {str(e)}")


def test_invalid_category():
    """Test with invalid category"""
    print("\n=== Testing Invalid Category ===")

    payload = {
        "country_code": "US",
        "category": "invalid_category_name"
    }

    try:
        response = requests.post(f"{BASE_URL}/google-trends", json=payload)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 422:
            print("✓ Invalid category rejected - SUCCESS")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")


def list_available_categories():
    """List all available unified categories"""
    print("\n=== Available Unified Categories ===")

    import sys
    import os
    # Add backend directory to path for imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

    from app.constants import UnifiedCategory, CATEGORY_DISPLAY_NAMES

    for category in UnifiedCategory:
        display_name = CATEGORY_DISPLAY_NAMES.get(category, category.value)
        print(f"  - {category.value:25} → {display_name}")


if __name__ == "__main__":
    print("=" * 60)
    print("Category Filtering Test Suite")
    print("=" * 60)

    # List available categories
    list_available_categories()

    # Note: Server must be running for these tests to work
    print("\n⚠️  Make sure the server is running: uvicorn backend.app.main:app --reload")
    print("\nSkipping live API tests (server may not be running)")

    # Uncomment the tests below to run them when server is running:
    # test_google_trends_with_category()
    # test_tiktok_with_category()
    # test_youtube_with_category()
    # test_youtube_without_category()
    # test_invalid_category()

    print("\n" + "=" * 60)
    print("To run live API tests:")
    print("1. Start the server: uvicorn backend.app.main:app --reload")
    print("2. Uncomment the test function calls in this script")
    print("3. Run: python test_categories.py")
    print("=" * 60)
