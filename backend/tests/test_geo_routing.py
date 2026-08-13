import pytest
from uuid import uuid4
from app.services.geo_routing_service import GeoRoutingService

def test_find_nearest_branch_gps():
    service = GeoRoutingService()
    branches = [
        {"id": uuid4(), "name": "Baku Center (28 May)", "latitude": 40.3798, "longitude": 49.8475, "address": "28 May str. 12"},
        {"id": uuid4(), "name": "Gənclik Mall Branch", "latitude": 40.4002, "longitude": 49.8517, "address": "Gənclik Mall 3rd floor"},
    ]

    # Location near 28 May
    result = service.find_nearest_branch(branches=branches, lat=40.3800, lng=49.8480)
    assert result is not None
    assert result.branch_name == "Baku Center (28 May)"
    assert result.is_nearest is True
    assert result.distance_km < 1.0

def test_find_nearest_branch_landmark_text():
    service = GeoRoutingService()
    branches = [
        {"id": uuid4(), "name": "28 May Branch", "latitude": 40.3798, "longitude": 49.8475, "address": "28 May str."},
        {"id": uuid4(), "name": "Gənclik Branch", "latitude": 40.4002, "longitude": 49.8517, "address": "Gənclik Mall"},
    ]

    result = service.find_nearest_branch(branches=branches, location_text="I am near Gənclik station")
    assert result is not None
    assert result.branch_name == "Gənclik Branch"
    assert result.is_nearest is True
