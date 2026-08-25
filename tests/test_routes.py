from fastapi.testclient import TestClient

from app.main import create_app


def test_dashboard_renders() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Architecture Evolution Analyzer" in response.text


def test_analysis_endpoint_rejects_non_github_url() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/analyses",
            json={
                "repository_url": "https://gitlab.com/openai/openai-python",
                "snapshot_count": 15,
            },
        )

    assert response.status_code == 422
