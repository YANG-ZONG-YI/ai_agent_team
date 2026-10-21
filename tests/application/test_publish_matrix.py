import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from src.domain.publish_task import PlatformType
from src.application.use_cases.publish_matrix import PublishMatrixUseCase, PublishMatrixInput

class TestPublishMatrixUseCase:
    """QA 測試：驗證多平台矩陣分發冪等性與失敗隔離"""

    def test_publish_matrix_skips_already_published_platform(self):
        """測試已完成發布的平台不會重複發布 (冪等保護)"""
        mock_job = MagicMock()
        mock_job.id = uuid4()
        mock_job.title = "Test Video"
        mock_job.video_path = "/tmp/video.mp4"

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = mock_job

        mock_task_repo = MagicMock()
        # 模擬 YOUTUBE 已經 PUBLISHED
        existing_task = MagicMock()
        existing_task.platform = "YOUTUBE"
        existing_task.status = "PUBLISHED"
        mock_task_repo.get_task.return_value = existing_task

        mock_publisher = MagicMock()

        use_case = PublishMatrixUseCase(
            job_repository=mock_repo,
            publish_repository=mock_task_repo,
            publisher_factory=mock_publisher
        )

        input_dto = PublishMatrixInput(job_id=str(mock_job.id), platforms=["YOUTUBE"])
        results = use_case.execute(input_dto)

        assert len(results) == 1
        assert results[0]["platform"] == "YOUTUBE"
        assert results[0]["status"] == "PUBLISHED"
        # 驗證絕對沒有重複調用第三方發布 API！
        mock_publisher.get_publisher.assert_not_called()
