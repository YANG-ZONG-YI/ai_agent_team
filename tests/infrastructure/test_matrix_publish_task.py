import os
from uuid import uuid4
import pytest
from src.infrastructure.database.models import SessionLocal, VideoJobModel, PublishTaskModel
from src.infrastructure.queue.tasks import run_matrix_publish_sync

def test_run_matrix_publish_sync_all_platforms(tmp_path):
    session = SessionLocal()
    
    # 建立一個成片已渲染完成的 Job
    mock_video = tmp_path / "completed_video.mp4"
    mock_video.write_bytes(b"mock mp4 binary")
    
    job = VideoJobModel(
        notion_page_id=f"notion-pub-{uuid4()}",
        title="AI 自動化短影音矩陣發布測試",
        prompt="測試 YouTube, IG, FB, TikTok 矩陣並行發布",
        status="COMPLETED",
        video_path=str(mock_video),
        preview_url="/videos/completed_video.mp4"
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    job_id = str(job.id)
    session.close()
    
    # 執行四大平台矩陣發布
    results = run_matrix_publish_sync(job_id, ["YOUTUBE", "INSTAGRAM", "FACEBOOK", "TIKTOK"])
    
    assert len(results) == 4
    for res in results:
        assert res["status"] == "PUBLISHED"
        assert res["platform_video_id"] is not None
        
    # 驗證資料庫中的 PublishTaskModel 狀態
    verify_session = SessionLocal()
    tasks = verify_session.query(PublishTaskModel).filter_by(job_id=job.id).all()
    assert len(tasks) == 4
    for task in tasks:
        assert task.status == "PUBLISHED"
        assert task.platform_video_id is not None
    verify_session.close()
