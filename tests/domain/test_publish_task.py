import pytest
from uuid import uuid4
from src.domain.publish_task import PublishTask, PlatformType, PublishStatus, MaxRetriesExceededError

def test_create_publish_task_defaults():
    job_id = uuid4()
    task = PublishTask.create(job_id=job_id, platform=PlatformType.YOUTUBE)
    assert task.job_id == job_id
    assert task.platform == PlatformType.YOUTUBE
    assert task.status == PublishStatus.SCHEDULED
    assert task.retry_count == 0
    assert task.platform_video_id is None

def test_publish_success_flow():
    task = PublishTask.create(uuid4(), PlatformType.TIKTOK)
    task.mark_published(platform_video_id="tiktok-vid-8888")
    assert task.status == PublishStatus.PUBLISHED
    assert task.platform_video_id == "tiktok-vid-8888"

def test_publish_retry_and_exceed_limit():
    task = PublishTask.create(uuid4(), PlatformType.INSTAGRAM)
    
    # 第 1 次失敗
    task.record_failure("429 Too Many Requests")
    assert task.status == PublishStatus.RETRYING
    assert task.retry_count == 1
    
    # 第 2 次失敗
    task.record_failure("Timeout waiting for Instagram Graph API")
    assert task.status == PublishStatus.RETRYING
    assert task.retry_count == 2
    
    # 第 3 次失敗 -> 達到上限，轉為 FAILED
    task.record_failure("Quota exceeded")
    assert task.status == PublishStatus.FAILED
    assert task.retry_count == 3
    
    # 超過 3 次再嘗試記錄失敗應拋出異常
    with pytest.raises(MaxRetriesExceededError):
        task.record_failure("Another failure")
