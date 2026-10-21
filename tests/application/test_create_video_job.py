import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from src.domain.video_job import VideoPipelineJob, JobStatus, DomainStateError
from src.application.use_cases.create_video_job import CreateVideoJobUseCase, CreateVideoJobInput

class TestCreateVideoJobUseCase:
    """QA 測試：驗證 CreateVideoJobUseCase 應用服務的建立與排程邏輯"""

    def test_create_new_job_successfully(self):
        """測試全新 Notion Page 正常建立聚合根並派發任務"""
        mock_repo = MagicMock()
        mock_repo.get_by_notion_page_id.return_value = None
        
        saved_mock_job = VideoPipelineJob.create(
            notion_page_id="page_uc_01",
            title="UC Test Title",
            prompt="UC Prompt",
            target_duration=30,
            character_id="default_anchor"
        )
        mock_repo.save.return_value = saved_mock_job

        mock_queue = MagicMock()

        use_case = CreateVideoJobUseCase(repository=mock_repo, queue_dispatcher=mock_queue)
        input_dto = CreateVideoJobInput(
            notion_page_id="page_uc_01",
            title="UC Test Title",
            prompt="UC Prompt",
            target_duration=30,
            character_id="default_anchor"
        )

        output = use_case.execute(input_dto)

        assert output.status == "QUEUED"
        assert output.job_id == str(saved_mock_job.id)
        assert output.title == "UC Test Title"
        mock_repo.save.assert_called_once()
        mock_queue.dispatch.assert_called_once_with(str(saved_mock_job.id))

    def test_existing_job_idempotent_queue(self):
        """測試若 Notion Page 已存在，具備冪等性直接重新觸發佇列而不建立重複實體"""
        mock_repo = MagicMock()
        existing_job = VideoPipelineJob.create(
            notion_page_id="page_uc_exists",
            title="Existing Job",
            prompt="Existing Prompt"
        )
        mock_repo.get_by_notion_page_id.return_value = existing_job

        mock_queue = MagicMock()

        use_case = CreateVideoJobUseCase(repository=mock_repo, queue_dispatcher=mock_queue)
        input_dto = CreateVideoJobInput(
            notion_page_id="page_uc_exists",
            title="Existing Job",
            prompt="Existing Prompt"
        )

        output = use_case.execute(input_dto)
        assert output.job_id == str(existing_job.id)
        # 不應重複 save 新實體
        mock_repo.save.assert_not_called()
        mock_queue.dispatch.assert_called_once_with(str(existing_job.id))
