from fastapi.testclient import TestClient
import pytest
from app.main import app

@pytest.fixture(scope='session')
def test_client():
    '''Return a Starlette test client for making requests against API.'''
    return TestClient(app)

@pytest.mark.parametrize('address, station', [
    ("55 E Wynnewood Rd, Merion Station, PA 19066", "Overbrook"),
    ("545 West Ct, Bensalem, PA 19020", "Torresdale"),
    ("64 Trewigtown Rd, Chalfont, PA 18914", "Link Belt"),
    ("115 Cricket Ave, Ardmore PA", "Ardmore"),
    ("145 Indian Ln, Media, PA 19063", "Elwyn"),
    ("72 W Johnson St, Philadelphia, PA 19144", "Upsal"),
    ("43 E Park Pl, Newark, DE 19711", "Newark"),
])
def test_address_success(address, station, test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "address",
        "address": address,
    })

    assert response.status_code == 200
    assert "station" in response.json()
    assert "directions" in response.json()
    assert response.json()["station"]["properties"]["name"] == station

@pytest.mark.parametrize('latitude, longitude, station', [
    (39.686459, -75.739656, "Newark"),
    (39.942658, -75.282525, "Lansdowne"),
    (40.096430, -75.131806, "Jenkintown-Wyncote"),
    (40.047733, -75.400476, "Strafford"),
    (39.995051, -75.151673, "North Philadelphia"),
    (40.263211, -74.815808, "West Trenton"),
])
def test_coordinates_success(latitude, longitude, station, test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "coordinates",
        "latitude": latitude,
        "longitude": longitude,
    })

    assert response.status_code == 200
    assert "station" in response.json()
    assert "directions" in response.json()
    assert response.json()["station"]["properties"]["name"] == station

def test_missing_address(test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "address"
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Address must be provided"

def test_missing_coordinates(test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "coordinates"
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Latitude and longitude must be provided"

def test_invalid_latitude(test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "coordinates",
        "latitude": 91,
        "longitude": -75.1652
    })
    
    assert response.status_code == 400
    assert "Latitude must be a valid number between" in response.json()["detail"]

def test_invalid_longitude(test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "coordinates",
        "latitude": 39.9526,
        "longitude": -181
    })
    
    assert response.status_code == 400
    assert "Longitude must be a valid number between" in response.json()["detail"]

@pytest.mark.parametrize('latitude, longitude', [
    (40.140916, -79.417978),
    (41.273492, -73.778543),
    (39.652273, -75.777980),
    (40.405078, -74.774276)
])
def test_coordinates_outside_limit(latitude, longitude, test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "coordinates",
        "latitude": latitude,
        "longitude": longitude
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == f"Sorry, ({latitude}, {longitude}) is too far from any stations to walk. Please try again."

@pytest.mark.parametrize('address', [
    "Pittsburgh, PA",
    "Princeton, NJ",
    "101 Sandy Dr, Newark, DE 19713",
    "76 Model Ave, Hopewell, NJ 08525",
])
def test_address_outside_limit(address, test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "address",
        "address": address,
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == f"Sorry, {address} is too far from any stations to walk. Please try again."

@pytest.mark.parametrize('latitude, longitude', [
    (39.648258, -71.204728),
    (44.500974, 2.006525),
    (32.168415, 115.870479),
])
def test_coordinates_no_viable_route(latitude, longitude, test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "coordinates",
        "latitude": latitude,
        "longitude": longitude
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == f"Sorry, no viable route for walking can be found for ({latitude}, {longitude}). Please try again."

@pytest.mark.parametrize('address', [
    'Nanjing, China',
    'Holzheimer Str. 8, 35428 Langgöns, Germany',
])  
def test_address_no_viable_route(address, test_client: TestClient):
    response = test_client.post("/api", json={
        "location_type": "address",
        "address": address,
    })
    
    assert response.status_code == 400
    assert response.json()["detail"] == f"Sorry, no viable route for walking can be found for {address}. Please try again."