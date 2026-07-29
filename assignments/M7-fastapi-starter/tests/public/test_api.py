from fastapi.testclient import TestClient

from m7_api.main import app


client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_prediction_validation() -> None:
    assert client.post("/predict", json={"value": 2}).status_code == 422
    response = client.post("/predict", json={"value": 0.8})
    assert response.status_code == 200
    assert response.json()["label"] == "высокий"
