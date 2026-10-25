import pytest
from server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_purchase_more_than_available_points(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Spring Festival",
            "places": "100",  # On demande 100 places alors que le club n'a pas autant de points
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    # On vérifie qu'un message d'erreur lié aux points est bien affiché
    assert (
        "points" in response.data.decode("utf-8").lower()
        or "not enough" in response.data.decode("utf-8").lower()
        or "pas assez" in response.data.decode("utf-8").lower()
    )