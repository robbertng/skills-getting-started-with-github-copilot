from copy import deepcopy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict after each test."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Expect known activity keys
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_duplicate():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Sign up should succeed
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Signing up again should return 400
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400


def test_unregister_existing_and_not_found():
    activity = "Chess Club"
    # Use an existing participant from sample data
    existing = "james@mergington.edu"

    # Ensure existing participant is present
    assert existing in activities[activity]["participants"]

    # Unregister should succeed
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": existing})
    assert resp.status_code == 200
    assert existing not in activities[activity]["participants"]

    # Unregistering someone not registered should return 404
    resp2 = client.delete(f"/activities/{activity}/unregister", params={"email": "not@registered.com"})
    assert resp2.status_code == 404
