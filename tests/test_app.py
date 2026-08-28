from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_seeded_activity_data(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    activity = response.json()[expected_activity]
    assert set(activity) == {
        "description",
        "schedule",
        "max_participants",
        "participants",
    }


def test_signup_adds_participant(client):
    # Arrange
    activity = "Soccer Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{quote(activity)}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity}"
    }
    activity_response = client.get("/activities").json()[activity]
    assert email in activity_response["participants"]


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    activity = "Unknown Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{quote(activity)}/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_duplicate_signup_returns_bad_request(client):
    # Arrange
    activity = "Chess Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{quote(activity)}/signup"
    client.post(endpoint, params={"email": email})

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    participants = client.get("/activities").json()[activity]["participants"]
    assert participants.count(email) == 1


def test_signup_without_email_returns_validation_error(client):
    # Arrange
    endpoint = "/activities/Soccer%20Club/signup"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 422


def test_delete_removes_existing_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    endpoint = f"/activities/{quote(activity)}/participants/{quote(email)}"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from {activity}"
    }
    participants = client.get("/activities").json()[activity]["participants"]
    assert email not in participants


def test_delete_from_unknown_activity_returns_not_found(client):
    # Arrange
    activity = "Unknown Club"
    email = "student@mergington.edu"
    endpoint = f"/activities/{quote(activity)}/participants/{quote(email)}"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_delete_of_missing_participant_returns_not_found(client):
    # Arrange
    activity = "Chess Club"
    email = "missing@mergington.edu"
    endpoint = f"/activities/{quote(activity)}/participants/{quote(email)}"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}


def test_signup_then_delete_handles_activity_names_with_spaces(client):
    # Arrange
    activity = "Programming Class"
    email = "student@mergington.edu"
    signup_endpoint = f"/activities/{quote(activity)}/signup"
    delete_endpoint = f"/activities/{quote(activity)}/participants/{quote(email)}"

    # Act
    signup_response = client.post(signup_endpoint, params={"email": email})
    delete_response = client.delete(delete_endpoint)

    # Assert
    assert signup_response.status_code == 200
    assert delete_response.status_code == 200
    participants = client.get("/activities").json()[activity]["participants"]
    assert email not in participants
