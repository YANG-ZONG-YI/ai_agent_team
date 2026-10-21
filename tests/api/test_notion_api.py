from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.infrastructure.database.models import SessionLocal, VideoJobModel

client = TestClient(app)

def test_notion_manual_poll_trigger():
    response = client.post("/api/v1/notion/poll")
    assert response.status_code == 200
    data = response.json()
    assert "polled_count" in data

def test_notion_webhook_trigger_job_creation():
    mock_page_id = f"page-webhook-{uuid4()}"
    payload = {
        "page_id": mock_page_id,
        "title": "Webhook 觸發 AI 短影音產製",
        "prompt": "測試 Webhook 自動接收選題並派發管線"
    }
    
    response = client.post("/api/v1/notion/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "QUEUED"
    assert "job_id" in data
    
    # 驗證資料庫已建立 Job 記錄
    session = SessionLocal()
    job = session.query(VideoJobModel).filter_by(notion_page_id=mock_page_id).first()
    assert job is not None
    assert job.title == "Webhook 觸發 AI 短影音產製"
    session.close()
