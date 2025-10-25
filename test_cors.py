#!/usr/bin/env python3
"""
Test script to verify CORS configuration for Railway deployment.
Run this after deploying to test CORS headers.
"""

import requests
import json

def test_cors_headers():
    """Test CORS headers on the deployed Railway backend"""
    
    # Test the Railway backend URL
    base_url = "https://surface-scan-backend-production.up.railway.app"
    
    print("🧪 Testing CORS Configuration")
    print("=" * 50)
    
    # Test 1: OPTIONS preflight request
    print("\n1. Testing OPTIONS preflight request...")
    try:
        response = requests.options(
            f"{base_url}/api/scan/",
            headers={
                'Origin': 'https://surface-scan-frontend.vercel.app',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower() or 'cors' in header.lower():
                print(f"     {header}: {value}")
        
        if response.status_code == 200:
            print("   ✅ OPTIONS request successful")
        else:
            print("   ❌ OPTIONS request failed")
            
    except Exception as e:
        print(f"   ❌ Error testing OPTIONS: {e}")
    
    # Test 2: POST request with CORS headers
    print("\n2. Testing POST request with CORS...")
    try:
        response = requests.post(
            f"{base_url}/api/scan/",
            json={"url": "https://example.com"},
            headers={
                'Origin': 'https://surface-scan-frontend.vercel.app',
                'Content-Type': 'application/json'
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        # Check CORS headers in response
        cors_headers = {k: v for k, v in response.headers.items() 
                       if 'access-control' in k.lower()}
        if cors_headers:
            print(f"   CORS Headers in Response:")
            for header, value in cors_headers.items():
                print(f"     {header}: {value}")
        
        if response.status_code in [200, 202]:
            print("   ✅ POST request successful")
        else:
            print("   ❌ POST request failed")
            
    except Exception as e:
        print(f"   ❌ Error testing POST: {e}")
    
    # Test 3: Check if server is responding
    print("\n3. Testing server health...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Server is responding")
        else:
            print("   ⚠️ Server responded with non-200 status")
    except Exception as e:
        print(f"   ❌ Server not responding: {e}")

if __name__ == "__main__":
    test_cors_headers()
