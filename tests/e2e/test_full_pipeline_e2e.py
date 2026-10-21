import os
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.infrastructure.database.models import SessionLocal, VideoJobModel, PublishTaskModel
from src.infrastructure.queue.tasks import run_video_pipeline_sync, run_matrix_publish_sync

client = TestClient(app)

def test_full_video_automation_pipeline_e2e(tmp_path):
    """
    全鏈路端對端驗收測試 (E2E Integration Test)
    涵蓋：Notion Webhook ➔ LLM/TTS/MoviePy 渲染 ➔ 靜態預覽 ➔ 四大社群平台矩陣發布
    """
    notion_page_id = f"e2e-notion-page-{uuid4()}"
    
    # 步驟 1: 模擬 Notion Webhook 派發新選題
    webhook_payload = {
        "page_id": notion_page_id,
        "title": "2026 AI Agent 全自動影音實戰",
        "prompt": "展示從選題到全平台發布的現代自動化管線架構"
    }
    create_resp = client.post("/api/v1/notion/webhook", json=webhook_payload)
    assert create_resp.status_code == 200
    job_data = create_resp.json()
    job_id_str = job_data["job_id"]
    
    # 步驟 2: 執行短影音產製管線 (Script ➔ pgvector ➔ TTS ➔ MoviePy 9:16 MP4)
    produce_result = run_video_pipeline_sync(job_id_str)
    assert produce_result["status"] == "COMPLETED"
    video_path = produce_result["video_path"]
    preview_url = produce_result["preview_url"]
    
    assert os.path.exists(video_path)
    assert os.path.getsize(video_path) > 0
    
    # 步驟 3: 驗證 HTTP 影片靜態預覽服務
    preview_resp = client.get(preview_url)
    assert preview_resp.status_code == 200
    assert "video/mp4" in preview_resp.headers.get("content-type", "")
    
    # 步驟 4: 執行四大多平台矩陣發布 (YouTube, Instagram, Facebook, TikTok)
    platforms = ["YOUTUBE", "INSTAGRAM", "FACEBOOK", "TIKTOK"]
    publish_results = run_matrix_publish_sync(job_id_str, platforms)
    assert len(publish_results) == 4
    for res in publish_results:
        assert res["status"] == "PUBLISHED"
        assert res["platform_video_id"] is not None
        
    # 步驟 5: 驗證成片預覽回填 Notion API 端點
    sync_resp = client.post("/api/v1/notion/sync-preview", json={"job_id": job_id_str})
    assert sync_resp.status_code == 200
    assert sync_resp.json()["status"] == "SYNCED"
    
    # 步驟 6: 驗證資料庫最終狀態一致性
    session = SessionLocal()
    job = session.query(VideoJobModel).filter_by(id=job_id_str).first()
    assert job.status == "COMPLETED"
    assert job.preview_url == preview_url
    
    tasks = session.query(PublishTaskModel).filter_by(job_id=job.id).all()
    assert len(tasks) == 4
    for t in tasks:
        assert t.status == "PUBLISHED"
        assert t.platform_video_id is not None
        
    session.close()
