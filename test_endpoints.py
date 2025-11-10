#!/usr/bin/env python3
"""
Test script for Social Media Trends API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n" + "="*50)
    print("Testing /health endpoint")
    print("="*50)

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_google_trends():
    """Test Google Trends endpoint"""
    print("\n" + "="*50)
    print("Testing /google-trends endpoint")
    print("="*50)

    payload = {"country_code": "LK"}
    response = requests.post(
        f"{BASE_URL}/google-trends",
        json=payload
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Country: {data['country']}")
        print(f"Total Trends: {data['total_trends']}")
        if data['trending_searches']:
            print(f"\nFirst trending search:")
            first = data['trending_searches'][0]
            print(f"  Query: {first.get('query', 'N/A')}")
            print(f"  Search Volume: {first.get('search_volume', 'N/A')}")
            print(f"  Active: {first.get('active', 'N/A')}")
            print(f"  Started: {first.get('started', 'N/A')}")
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200


def test_youtube_trends():
    """Test YouTube Trends endpoint"""
    print("\n" + "="*50)
    print("Testing /youtube-trends endpoint")
    print("="*50)

    payload = {
        "country_code": "US",
        "max_results": 5
    }
    response = requests.post(
        f"{BASE_URL}/youtube-trends",
        json=payload
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Country: {data['country']}")
        print(f"Total Videos: {data['total_videos']}")
        if data['videos']:
            print(f"\nFirst trending video:")
            first = data['videos'][0]
            print(f"  Title: {first.get('title', 'N/A')}")
            print(f"  Channel: {first.get('channelTitle', 'N/A')}")
            print(f"  Views: {first.get('viewCount', 'N/A'):,}")
            print(f"  Likes: {first.get('likeCount', 'N/A'):,}")
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200


def test_root():
    """Test root endpoint"""
    print("\n" + "="*50)
    print("Testing / endpoint")
    print("="*50)

    response = requests.get(BASE_URL)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


if __name__ == "__main__":
    print("Starting API endpoint tests...")

    results = {
        "Root": test_root(),
        "Health": test_health(),
        "YouTube Trends": test_youtube_trends(),
        "Google Trends": test_google_trends(),
    }

    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    print("\n" + "="*50)
    print("Note: TikTok test skipped (requires longer execution time)")
    print("You can test it manually with:")
    print('curl -X POST http://localhost:8000/tiktok-trends \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"country_code": "MY", "results_per_page": 5, "time_range": "7"}\'')
    print("="*50)
