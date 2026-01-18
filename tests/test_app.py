"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Test suite for getting activities"""
    
    def test_get_activities_returns_200(self):
        """Test that getting activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that getting activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self):
        """Test that response contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Test suite for signing up for activities"""
    
    def test_signup_new_participant_returns_200(self):
        """Test that signing up a new participant returns 200"""
        response = client.post(
            "/activities/Soccer Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_new_participant_adds_to_list(self):
        """Test that signing up adds participant to the activity"""
        # Get initial participants count
        response = client.get("/activities")
        initial_count = len(response.json()["Soccer Team"]["participants"])
        
        # Sign up new participant
        client.post(
            "/activities/Soccer Team/signup?email=testnewstudent@mergington.edu"
        )
        
        # Check participant was added
        response = client.get("/activities")
        new_count = len(response.json()["Soccer Team"]["participants"])
        assert new_count == initial_count + 1
        assert "testnewstudent@mergington.edu" in response.json()["Soccer Team"]["participants"]
    
    def test_signup_duplicate_participant_returns_400(self):
        """Test that signing up twice returns 400 error"""
        email = "duplicate@mergington.edu"
        activity = "Basketball Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_response_message(self):
        """Test that signup returns correct message"""
        email = "messagetest@mergington.edu"
        activity = "Drama Club"
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]


class TestUnregister:
    """Test suite for unregistering from activities"""
    
    def test_unregister_participant_returns_200(self):
        """Test that unregistering returns 200"""
        activity = "Chess Club"
        email = "michael@mergington.edu"
        
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
    
    def test_unregister_removes_participant(self):
        """Test that unregistering removes participant from activity"""
        activity = "Programming Class"
        email = "emma@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Unregister
        client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Check participant was removed
        response = client.get("/activities")
        new_count = len(response.json()[activity]["participants"])
        assert new_count == initial_count - 1
        assert email not in response.json()[activity]["participants"]
    
    def test_unregister_nonexistent_participant_returns_400(self):
        """Test that unregistering non-participant returns 400"""
        response = client.post(
            "/activities/Math Olympiad/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregistering from nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_response_message(self):
        """Test that unregister returns correct message"""
        # First sign up
        email = "unregistertest@mergington.edu"
        activity = "Art Workshop"
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]


class TestRoot:
    """Test suite for root endpoint"""
    
    def test_root_redirects(self):
        """Test that root endpoint redirects"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
