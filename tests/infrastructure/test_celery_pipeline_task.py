import os
from uuid import uuid4
import pytest
from src.infrastructure.database.models import SessionLocal, VideoJobModel
from src.infrastructure.queue.tasks import run_video_pipeline_sync

def test_celery_produce_video_pipeline_sync(tmp_path):
    session = SessionLocal()
    
    # 建立測試 Job
    job = VideoJobModel(
        notion_page_id=f"notion-{uuid4()}",
        title="Celery 異步端到端渲染管線測試",
        prompt="驗證 Celery Worker 執行 LLM + TTS + MoviePy 影音合成"
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    job_id = str(job.id)
    session.close()
    
    # 執行管線任務
    result = run_video_pipeline_sync(job_id)
    
    assert result["status"] == "COMPLETED"
    assert result["preview_url"] is not None
    assert os.path.exists(result["video_path"])
    
    # 驗證資料庫狀態已同步轉為 COMPLETED
    verify_session = SessionLocal()
    updated_job = verify_session.query(VideoJobModel).filter_by(id=job.id).first()
    assert updated_job.status == "COMPLETED"
    assert updated_job.video_path == result["video_path"]
    assert updated_job.preview_url == result["preview_url"]
    verify_session.close()
