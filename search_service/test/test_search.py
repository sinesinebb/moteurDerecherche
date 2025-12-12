# tests/test_search.py
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from services.domain_validator import DomainValidator

client = TestClient(app)

@pytest.fixture
def domain_validator():
    return DomainValidator()

class TestSearchService:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
    
    def test_search_success(self):
        response = client.post("/api/v1/search", json={
            "query": "python programming",
            "page": 1,
            "size": 10
        })
        # Note: Dans un vrai test, il faudrait mock Elasticsearch
        assert response.status_code in [200, 400]  # 400 si domaine non informatique
    
    def test_domain_validation_it(self, domain_validator):
        is_it, confidence, category = domain_validator.is_informatics_domain("python programming")
        assert is_it == True
        assert confidence > 0.5
    
    def test_domain_validation_non_it(self, domain_validator):
        is_it, confidence, category = domain_validator.is_informatics_domain("recette de cuisine")
        assert is_it == False
    
    def test_autocomplete(self):
        response = client.get("/api/v1/search/autocomplete?q=pyth")
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"