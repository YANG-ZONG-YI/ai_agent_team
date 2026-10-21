import pytest
from uuid import uuid4
from src.domain.video_job import VideoPipelineJob, JobStatus, DomainStateError

def test_create_video_pipeline_job_default_pending():
    job = VideoPipelineJob.create(
        notion_page_id="notion-page-123",
        title="AI 時代工程師必備技能",
        prompt="介紹 AI Agent 開發的核心架構與 TDD 原則"
    )
    assert job.notion_page_id == "notion-page-123"
    assert job.title == "AI 時代工程師必備技能"
    assert job.status == JobStatus.PENDING
    assert job.video_path is None
    assert job.preview_url is None

def test_transition_to_scripting():
    job = VideoPipelineJob.create("page-1", "標題", "提示詞")
    job.start_scripting()
    assert job.status == JobStatus.SCRIPTING

def test_transition_to_rendering_requires_script_content():
    job = VideoPipelineJob.create("page-1", "標題", "提示詞")
    job.start_scripting()
    
    # 未設定腳本直接進入渲染應拋出 DomainStateError
    with pytest.raises(DomainStateError, match="Cannot render without script content"):
        job.start_rendering()
        
    job.set_script("【開場】大家好，今天分享 AI Agent 開發...")
    job.start_rendering()
    assert job.status == JobStatus.RENDERING

def test_transition_to_completed_requires_video_path():
    job = VideoPipelineJob.create("page-1", "標題", "提示詞")
    job.start_scripting()
    job.set_script("腳本內容...")
    job.start_rendering()
    
    job.mark_completed(
        video_path="/app/storage/projects/proj_20261021_ai_test_12345678/05_output/master.mp4",
        preview_url="/projects/proj_20261021_ai_test_12345678/05_output/master.mp4"
    )
    assert job.status == JobStatus.COMPLETED
    assert job.video_path == "/app/storage/projects/proj_20261021_ai_test_12345678/05_output/master.mp4"
    assert job.preview_url == "/projects/proj_20261021_ai_test_12345678/05_output/master.mp4"

def test_cannot_complete_from_pending_directly():
    job = VideoPipelineJob.create("page-1", "標題", "提示詞")
    with pytest.raises(DomainStateError):
        job.mark_completed(video_path="/app/test.mp4", preview_url="/videos/test.mp4")
