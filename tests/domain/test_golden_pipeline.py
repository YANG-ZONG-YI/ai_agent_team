import pytest
from uuid import uuid4
from src.domain.video_job import VideoPipelineJob, JobStatus, DomainStateError

class TestGoldenPipelineDomain:
    """黃金驗收測試：固化領域模型不變量與狀態機流轉規則"""

    def test_job_creation_invariants(self):
        """驗證作業建立時的目標時長邊界不變量"""
        # 合法時長：15 ~ 180 秒
        job = VideoPipelineJob.create(
            notion_page_id="page_123",
            title="Golden Test Title",
            prompt="A testing prompt",
            target_duration=30
        )
        assert job.status == JobStatus.PENDING
        assert job.target_duration == 30
        assert job.script_content is None
        assert job.video_path is None

        # 非法時長：小於 15 秒或大於 180 秒應拋出 DomainStateError
        with pytest.raises(DomainStateError, match="Target duration must be between 15 and 180 seconds"):
            VideoPipelineJob.create(
                notion_page_id="page_124",
                title="Invalid Duration Low",
                prompt="Prompt",
                target_duration=10
            )

        with pytest.raises(DomainStateError, match="Target duration must be between 15 and 180 seconds"):
            VideoPipelineJob.create(
                notion_page_id="page_125",
                title="Invalid Duration High",
                prompt="Prompt",
                target_duration=300
            )

    def test_job_state_transition_lifecycle(self):
        """驗證合法的端到端狀態機流轉：PENDING -> SCRIPTING -> RENDERING -> COMPLETED"""
        job = VideoPipelineJob.create(
            notion_page_id="page_999",
            title="Full Lifecycle",
            prompt="Prompt",
            target_duration=60
        )
        assert job.status == JobStatus.PENDING

        # 1. 開始編劇
        job.start_scripting()
        assert job.status == JobStatus.SCRIPTING

        # 2. 設定劇本
        job.set_script("This is generated script narration.")
        assert job.script_content == "This is generated script narration."

        # 3. 開始渲染
        job.start_rendering()
        assert job.status == JobStatus.RENDERING

        # 4. 標記完成
        job.mark_completed(
            video_path="/app/storage/projects/p_999/05_output/master.mp4",
            preview_url="/projects/p_999/05_output/preview.mp4"
        )
        assert job.status == JobStatus.COMPLETED
        assert job.video_path == "/app/storage/projects/p_999/05_output/master.mp4"
        assert job.preview_url == "/projects/p_999/05_output/preview.mp4"

    def test_illegal_state_transition_prevention(self):
        """驗證非法狀態躍遷必須被領域核心硬性攔截"""
        job = VideoPipelineJob.create(
            notion_page_id="page_err",
            title="Illegal Transition",
            prompt="Prompt"
        )
        # 未經 SCRIPTING 不得直接 RENDERING
        with pytest.raises(DomainStateError, match="Cannot start rendering from state"):
            job.start_rendering()

        # 未經 RENDERING 不得直接 COMPLETED
        with pytest.raises(DomainStateError, match="Cannot mark completed from state"):
            job.mark_completed("/tmp/path.mp4", "/tmp/url")

        # 空劇本不可設定
        job.start_scripting()
        with pytest.raises(DomainStateError, match="Script content cannot be empty"):
            job.set_script("   ")
