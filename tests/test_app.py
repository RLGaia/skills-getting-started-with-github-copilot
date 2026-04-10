"""
Unit tests for Mergington High School Activities API using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_all_activities_returns_9_activities(self, client):
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
    
    def test_get_activities_returns_required_fields(self, client):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_details in data.items():
            assert required_fields.issubset(activity_details.keys()), \
                f"Activity '{activity_name}' missing required fields"
    
    def test_get_activities_contains_chess_club(self, client):
        # Arrange
        expected_activity = "Chess Club"
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert expected_activity in data
        assert "michael@mergington.edu" in data[expected_activity]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_participant_successfully(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert activity_name in response.json()["message"]
    
    def test_signup_participant_appears_in_activity_list(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act: Signup participant
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act: Get activities to verify
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert email in data[activity_name]["participants"]
    
    def test_signup_returns_404_for_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_returns_400_for_duplicate_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_increments_participant_count(self, client):
        # Arrange
        activity_name = "Tennis Club"
        email = "newplayer@mergington.edu"
        
        # Act: Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act: Signup new participant
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act: Get updated count
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        
        # Assert
        assert updated_count == initial_count + 1


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_remove_participant_successfully(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert activity_name in response.json()["message"]
    
    def test_remove_participant_appears_removed_in_activity_list(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: Remove participant
        client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Act: Get activities to verify
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert email not in data[activity_name]["participants"]
    
    def test_remove_returns_404_for_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_returns_404_for_nonexistent_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_decrements_participant_count(self, client):
        # Arrange
        activity_name = "Art Studio"
        email = "isabella@mergington.edu"
        
        # Act: Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act: Remove participant
        client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Act: Get updated count
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        
        # Assert
        assert updated_count == initial_count - 1


class TestIntegration:
    """Integration tests for signup and removal workflows."""
    
    def test_signup_then_remove_participant_workflow(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "jane.doe@mergington.edu"
        
        # Act: Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert signup successful
        assert signup_response.status_code == 200
        
        # Act: Verify in list
        get_response = client.get("/activities")
        assert email in get_response.json()[activity_name]["participants"]
        
        # Act: Remove
        delete_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert remove successful
        assert delete_response.status_code == 200
        
        # Act: Verify removed from list
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity_name]["participants"]
