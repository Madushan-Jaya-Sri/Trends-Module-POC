"""
Test script to verify the Trends API is working correctly
"""

import httpx
import json
from datetime import datetime


def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Social Media Trends API")
    print("=" * 50)
    print()
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = httpx.get(f"{base_url}/health", timeout=10.0)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   Status: {response.json()['status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        print("   Make sure the server is running: uvicorn app.main:app --reload")
        return
    
    print()
    
    # Test 2: Get countries
    print("2. Testing countries endpoint...")
    try:
        response = httpx.get(f"{base_url}/countries", timeout=10.0)
        if response.status_code == 200:
            countries = response.json()
            print(f"   ✅ Found {len(countries['countries'])} supported countries")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 3: Get platform stats
    print("3. Testing platform stats endpoint...")
    try:
        response = httpx.get(f"{base_url}/platforms?country=US", timeout=60.0)
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Platform stats retrieved:")
            for platform, data in stats['platforms'].items():
                print(f"      {platform}: {data['status']} ({data['count']} items)")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    
    # Test 4: Get trends (this will take longest)
    print("4. Testing trends endpoint (this may take 30-60 seconds)...")
    print("   Please wait...")
    try:
        response = httpx.get(
            f"{base_url}/trends?country=US&top_n=5", 
            timeout=120.0  # 2 minutes timeout
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Trends retrieved successfully!")
            print(f"   Country: {data['country']}")
            print(f"   Total trends found: {data['total_trends']}")
            print(f"   Top recommendations: {len(data['recommendations'])}")
            print()
            print("   Top 3 Trending Topics:")
            for i, trend in enumerate(data['recommendations'][:3], 1):
                print(f"      {i}. {trend['topic']}")
                print(f"         Score: {trend['score']}/100")
                print(f"         Platforms: {', '.join(trend['platforms'])}")
                print(f"         {trend['trending_reason']}")
                print()
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except httpx.TimeoutException:
        print("   ⏱️  Request timed out. This is normal for the first request.")
        print("   The scraping process can take 1-2 minutes.")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()
    print("=" * 50)
    print("✅ Testing complete!")
    print()
    print("💡 Tips:")
    print("   - First request may take 30-60 seconds")
    print("   - Open http://localhost:8000/docs for interactive API docs")
    print("   - Open frontend/index.html in your browser to use the UI")


if __name__ == "__main__":
    test_api()