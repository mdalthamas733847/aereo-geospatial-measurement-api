import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_measure_endpoint():
    payload = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [77.5946, 12.9716],
                [77.5956, 12.9726]
            ]
        }
    }

    response = client.post(
        "/api/v1/measure",
        files={
            "file": (
                "sample.geojson",
                json.dumps(payload).encode(),
                "application/geo+json",
            )
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["geometry_type"] == "LineString"
    assert body["length_m"] > 0
