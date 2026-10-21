import pytest
from uuid import uuid4
from src.domain.video_job import VideoPipelineJob, JobStatus, DomainStateError

def test_create_job_with_valid_duration_and_character():
    job = VideoPipelineJob.create(
        notion_page_id="page-123",
        title="AI 趨勢解析",
        prompt="生成 60 秒科技趨勢影片",
        target_duration=60,
        character_id="host_cyber"
    )
    assert job.target_duration == 60
    assert job.character_id == "host_cyber"
    assert job.status == JobStatus.PENDING

def test_create_job_with_default_duration():
    job = VideoPipelineJob.create(
        notion_page_id="page-456",
        title="預設長度影片",
        prompt="預設主題"
    )
    assert job.target_duration == 30
    assert job.character_id == "default_anchor"

def test_create_job_with_invalid_duration_too_short():
    with pytest.raises(DomainStateError, match="Target duration must be between 15 and 180 seconds"):
        VideoPipelineJob.create(
            notion_page_id="page-789",
            title="太短影片",
            prompt="5秒",
            target_duration=10
        )

def test_create_job_with_invalid_duration_too_long():
    with pytest.raises(DomainStateError, match="Target duration must be between 15 and 180 seconds"):
        VideoPipelineJob.create(
            notion_page_id="page-999",
            title="太長影片",
            prompt="300秒",
            target_duration=300
        )
