from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_blocked_keyword():
    response = client.post("/generate?prompt=password")
    assert response.status_code == 403
