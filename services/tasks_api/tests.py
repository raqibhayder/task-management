import pytest
from fastapi import status
from starlette.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client: TestClient):
    """
    GIVEN a FastAPI application
    WHEN health check endpoint is called with GET method
    THEN respond with status 200 and body OK message
    """
    response = client.get("/api/health-check/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "ok"}
