from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

API_KEY = "devkey123"
HEADERS = {"X-API-Key": API_KEY}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_auth_required():
    r = client.get("/items")  # no headers
    assert r.status_code == 401


def test_create_and_list_items():
    # Create
    payload = {"name": "Eggs", "quantity": 12, "category": "Dairy"}
    r = client.post("/items", json=payload, headers=HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Eggs"
    assert data["quantity"] == 12
    assert data["category"] == "Dairy"
    assert data["is_purchased"] is False

    # List
    r2 = client.get("/items", headers=HEADERS)
    assert r2.status_code == 200
    items = r2.json()
    assert isinstance(items, list)
    assert any(i["name"] == "Eggs" for i in items)