# from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from ..scissorapp.rate_limiter import rate_limiter
from ..scissorapp.database import get_db, Base, test_engine, Test_SessionLocal
from ..main import app


Base.metadata.create_all(bind=test_engine)
def override_get_db():
    db = Test_SessionLocal
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# home route
def test_home_page():
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json() == {"msg": "Welcome to Scissor URL :)"}

def test_shorten_url():
    response = client.post("/shorten-url", json = {"target_url": "https://www.google.com"})

    data = response.json()
    assert response.status_code == 200
    assert data.get("target_url") == "https://www.google.com"
    assert data.get("is_active") == True

# def test_customize_short_url_address():
#     response = client.put("/hi8Ge&new_address=google-homepage")
    
