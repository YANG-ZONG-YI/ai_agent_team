import pytest
from uuid import uuid4
from src.domain.video_job import VideoPipelineJob, JobStatus
from src.domain.repositories import IJobRepository
from src.infrastructure.database.models import SessionLocal, VideoJobModel
from src.infrastructure.database.job_repository import SqlAlchemyJobRepository, JobMapper

class TestJobRepositoryAndMapper:
    """QA 測試：驗證 SqlAlchemyJobRepository 與 JobMapper 之雙向映射與持久化"""

    @pytest.fixture
    def session(self):
        s = SessionLocal()
        yield s
        s.close()

    @pytest.fixture
    def repository(self, session):
        return SqlAlchemyJobRepository(session)

    def test_job_mapper_two_way_conversion(self):
        """測試領域聚合根與 ORM 模型之間的相互轉換純度"""
        # 1. 建立領域實體
        job = VideoPipelineJob.create(
            notion_page_id=f"page_mapper_{uuid4().hex[:8]}",
            title="Mapper Test",
            prompt="Prompt",
            target_duration=45,
            character_id="anchor_01"
        )
        job.start_scripting()
        job.set_script("Test script narration")

        # 2. 轉為 ORM Model
        orm_model = JobMapper.to_model(job)
        assert orm_model.id == job.id
        assert orm_model.notion_page_id == job.notion_page_id
        assert orm_model.status == "SCRIPTING"
        assert orm_model.script_content == "Test script narration"
        assert orm_model.target_duration == 45

        # 3. 再由 ORM Model 轉回 Domain Entity
        converted_job = JobMapper.to_domain(orm_model)
        assert converted_job.id == job.id
        assert converted_job.status == JobStatus.SCRIPTING
        assert converted_job.script_content == "Test script narration"

    def test_repository_save_and_retrieve_roundtrip(self, repository):
        """測試 Repository 的 save、get_by_id 與 get_by_notion_page_id 閉環"""
        page_id = f"page_repo_{uuid4().hex[:8]}"
        job = VideoPipelineJob.create(
            notion_page_id=page_id,
            title="Repository Roundtrip",
            prompt="Roundtrip Prompt",
            target_duration=30
        )

        # 儲存新作業
        saved_job = repository.save(job)
        assert saved_job.id == job.id

        # 依 ID 檢索
        retrieved_by_id = repository.get_by_id(job.id)
        assert retrieved_by_id is not None
        assert retrieved_by_id.notion_page_id == page_id
        assert retrieved_by_id.status == JobStatus.PENDING

        # 更新狀態並保存
        retrieved_by_id.start_scripting()
        retrieved_by_id.set_script("Persisted Script")
        repository.save(retrieved_by_id)

        # 依 Notion Page ID 檢索驗證狀態變更
        retrieved_by_page = repository.get_by_notion_page_id(page_id)
        assert retrieved_by_page is not None
        assert retrieved_by_page.status == JobStatus.SCRIPTING
        assert retrieved_by_page.script_content == "Persisted Script"
