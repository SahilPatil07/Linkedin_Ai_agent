import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data

def test_analytics_endpoints():
    # Test engagement analytics
    response = client.get("/api/v1/analytics/engagement")
    assert response.status_code in [200, 401]  # 401 if not authenticated
    
    # Test post analytics
    response = client.get("/api/v1/analytics/posts")
    assert response.status_code in [200, 401]  # 401 if not authenticated

def test_linkedin_auth():
    # Test login endpoint
    response = client.get("/api/v1/auth/login")
    assert response.status_code in [200, 302]  # 302 for redirect to LinkedIn

def test_post_creation():
    # Test post creation (requires authentication)
    test_post = {
        "content": "Test post content",
        "visibility": "PUBLIC"
    }
    response = client.post("/api/v1/posts/", json=test_post)
    assert response.status_code in [201, 401]  # 401 if not authenticated

if __name__ == "__main__":
    pytest.main([__file__]) 