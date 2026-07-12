"""Tests for the /api/meetings endpoints."""
import io


def test_upload_rejects_unsupported_file_type(client):
    fake_file = io.BytesIO(b"not audio")
    response = client.post(
        "/api/meetings",
        files={"file": ("document.pdf", fake_file, "application/pdf")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_get_nonexistent_meeting_returns_404(client):
    response = client.get("/api/meetings/does-not-exist")
    assert response.status_code == 404


def test_list_meetings_returns_array(client):
    response = client.get("/api/meetings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)