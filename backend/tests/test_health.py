"""Tests for the health check endpoint."""


def test_health_check_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Meeting Summarizer" in response.text