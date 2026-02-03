"""
Tests for the Mergington High School Activities API

This test suite covers the main endpoints and functionality of the application.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_success(self):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) > 0

    def test_get_activities_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successfully signing up for an activity"""
        # Use a fresh email for this test
        test_email = "newstudent@mergington.edu"
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": test_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data["Chess Club"]["participants"]

    def test_signup_duplicate_registration_failure(self):
        """Test that a student cannot register twice for the same activity"""
        test_email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Programming Class/signup",
            params={"email": test_email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": test_email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_activity_not_found_failure(self):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_with_valid_email_format(self):
        """Test signup with various valid email formats"""
        test_emails = [
            "alice@mergington.edu",
            "bob.smith@mergington.edu",
            "charlie_johnson@mergington.edu"
        ]
        
        for email in test_emails:
            response = client.post(
                "/activities/Art Studio/signup",
                params={"email": email}
            )
            assert response.status_code == 200


class TestRootEndpoint:
    """Test suite for root endpoint"""

    def test_root_redirect(self):
        """Test that root endpoint redirects to static page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestUnregisterEndpoint:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successfully unregistering a participant"""
        test_email = "unregister_test@mergington.edu"
        
        # First, signup
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": test_email}
        )
        
        # Then, unregister
        response = client.delete(
            "/activities/Tennis Club/unregister",
            params={"email": test_email}
        )
        
        assert response.status_code == 200
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email not in activities_data["Tennis Club"]["participants"]

    def test_unregister_not_signed_up_failure(self):
        """Test that unregistering someone not signed up fails"""
        test_email = "not_signed_up@mergington.edu"
        
        response = client.delete(
            "/activities/Debate Team/unregister",
            params={"email": test_email}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_activity_not_found_failure(self):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404