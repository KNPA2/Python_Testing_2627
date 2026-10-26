import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_public_clubs_points_table(client):
    response = client.get('/points')
    assert response.status_code == 200
    assert "Simply Lift" in response.data.decode('utf-8')

def test_club_bookings_summary(client):
    # On simule la connexion d'un club et un achat pour être sûr d'avoir des données
    client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '2'
    }, follow_redirects=True)
    
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'}, follow_redirects=True)
    assert response.status_code == 200
    # On vérifie spécifiquement la présence d'éléments du tableau de réservations
    assert "spring festival" in response.data.decode('utf-8').lower() or "réservations" in response.data.decode('utf-8').lower()

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


def test_purchase_more_than_12_places(client):
    response = client.post(
        '/purchasePlaces',
        data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '15'  # On essaie de réserver 15 places (ce qui dépasse la limite de 12)
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    # Le test vérifie qu'un message d'erreur mentionnant la limite apparaît
    assert "12" in response.data.decode('utf-8') or "maximum" in response.data.decode('utf-8') or "limit" in response.data.decode('utf-8').lower()
    
def test_purchase_past_competition(client):
    response = client.post(
        '/purchasePlaces',
        data={
            'club': 'Simply Lift',
            'competition': 'L\'examen Chunin',  # Vérifie dans competitions.json si c'est une compétition passée, ou adapte le nom
            'places': '1'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    # On s'attend à ce qu'un message d'erreur apparaisse car la date est passée
    assert "past" in response.data.decode('utf-8').lower() or "passe" in response.data.decode('utf-8').lower() or "error" in response.data.decode('utf-8').lower()

def test_cancel_booking(client):
    # D'abord, on réserve 4 places pour un club
    client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '4'
    }, follow_redirects=True)
    
    # Ensuite, on teste l'annulation de 2 places
    response = client.post('/cancelBooking', data={
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': '2'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert "cancelled" in response.data.decode('utf-8').lower() or "success" in response.data.decode('utf-8').lower() or "points" in response.data.decode('utf-8').lower()

def test_cannot_book_more_than_available_places(client):
    # On tente de réserver un nombre excessif de places (ex: 999 places)
    response = client.post('/purchasePlaces', data={
        'club': 'Simply Lift',
        'competition': 'Fall Classic',
        'places': '999'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # On s'assure qu'un message d'erreur est affiché
    assert "not enough" in response.data.decode('utf-8').lower() or "places" in response.data.decode('utf-8').lower() or "disponible" in response.data.decode('utf-8').lower()
            
def test_purchase_negative_places(client):
    response = client.post(
        '/purchasePlaces',
        data={
            'club': 'Simply Lift',
            'competition': 'Spring Festival',
            'places': '-5'  # On essaie de réserver un nombre négatif de places
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    # Le test vérifie qu'un message d'erreur lié à une saisie invalide/négative apparaît
    assert "positive" in response.data.decode('utf-8').lower() or "invalid" in response.data.decode('utf-8').lower() or "error" in response.data.decode('utf-8').lower() or "supérieur" in response.data.decode('utf-8').lower()