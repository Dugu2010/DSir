from unittest.mock import patch

from fastapi.testclient import TestClient


async def test_worker_imports() -> None:
    from src.worker.celery_app import celery_app
    from src.worker.tasks.mastery import apply_decay_all
    from src.worker.tasks.revision import pregenerate_all

    assert celery_app is not None
    assert apply_decay_all is not None
    assert pregenerate_all is not None


def test_trigger_pregenerate_revisions(auth_client: TestClient) -> None:
    with patch("src.api.v1.worker.pregenerate_all") as mock_task:
        response = auth_client.post("/api/v1/worker/pregenerate-revisions")
        assert response.status_code == 202
        assert response.json()["task"] == "pregenerate_all"
        mock_task.delay.assert_called_once()


def test_trigger_apply_decay(auth_client: TestClient) -> None:
    with patch("src.api.v1.worker.apply_decay_all") as mock_task:
        response = auth_client.post("/api/v1/worker/apply-decay")
        assert response.status_code == 202
        assert response.json()["task"] == "apply_decay_all"
        mock_task.delay.assert_called_once()
