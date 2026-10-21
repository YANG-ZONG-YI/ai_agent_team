import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

client = TestClient(app)

class TestGoldenAPI:
    """黃金驗收測試：固化既有 API 契約行為與回傳格式"""

    def test_healthz_contract(self):
        """驗證 /healthz 必須返回 status healthy 與 storage 狀態"""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "video-automation-pipeline"
        assert data["storage"] == "mounted"

    @patch("src.infrastructure.queue.tasks.produce_video_task.delay")
    def test_notion_webhook_contract(self, mock_celery_delay):
        """驗證 Notion Webhook 接收與任務排隊合約"""
        payload = {
            "page_id": "golden_page_001",
            "title": "Golden Webhook Video",
            "prompt": "Create an informative tech news video",
            "target_duration": 45,
            "character_id": "tech_anchor"
        }
        response = client.post("/api/v1/notion/webhook", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "QUEUED"
        assert "job_id" in data
        assert data["title"] == "Golden Webhook Video"
        mock_celery_delay.assert_called_once()
