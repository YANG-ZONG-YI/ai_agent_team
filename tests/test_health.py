from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check_returns_healthy():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "video-automation-pipeline"
