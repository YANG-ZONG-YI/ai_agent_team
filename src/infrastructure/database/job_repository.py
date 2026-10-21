from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.video_job import VideoPipelineJob, JobStatus
from src.domain.repositories import IJobRepository
from src.infrastructure.database.models import VideoJobModel

class JobMapper:
    """領域實體與 SQLAlchemy ORM 模型的雙向映射器 (隔離基礎設施)"""

    @staticmethod
    def to_domain(model: VideoJobModel) -> VideoPipelineJob:
        return VideoPipelineJob(
            id=model.id,
            notion_page_id=model.notion_page_id,
            title=model.title,
            prompt=model.prompt,
            status=JobStatus(model.status),
            target_duration=model.target_duration,
            character_id=model.character_id,
            script_content=model.script_content,
            video_path=model.video_path,
            preview_url=model.preview_url,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_model(domain: VideoPipelineJob) -> VideoJobModel:
        return VideoJobModel(
            id=domain.id,
            notion_page_id=domain.notion_page_id,
            title=domain.title,
            prompt=domain.prompt,
            status=domain.status.value,
            target_duration=domain.target_duration,
            character_id=domain.character_id,
            script_content=domain.script_content,
            video_path=domain.video_path,
            preview_url=domain.preview_url,
            error_message=domain.error_message,
            created_at=domain.created_at,
            updated_at=domain.updated_at
        )

    @staticmethod
    def update_model_from_domain(model: VideoJobModel, domain: VideoPipelineJob) -> None:
        model.status = domain.status.value
        model.script_content = domain.script_content
        model.video_path = domain.video_path
        model.preview_url = domain.preview_url
        model.error_message = domain.error_message
        model.updated_at = domain.updated_at

class SqlAlchemyJobRepository(IJobRepository):
    """SQLAlchemy 實作之作業儲存庫 (Infrastructure Adapter)"""

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, job_id: UUID) -> Optional[VideoPipelineJob]:
        model = self._session.query(VideoJobModel).filter_by(id=job_id).first()
        if not model:
            return None
        return JobMapper.to_domain(model)

    def get_by_notion_page_id(self, notion_page_id: str) -> Optional[VideoPipelineJob]:
        model = self._session.query(VideoJobModel).filter_by(notion_page_id=notion_page_id).first()
        if not model:
            return None
        return JobMapper.to_domain(model)

    def save(self, job: VideoPipelineJob) -> VideoPipelineJob:
        existing_model = self._session.query(VideoJobModel).filter_by(id=job.id).first()
        if existing_model:
            JobMapper.update_model_from_domain(existing_model, job)
            self._session.commit()
            self._session.refresh(existing_model)
            return JobMapper.to_domain(existing_model)
        else:
            new_model = JobMapper.to_model(job)
            self._session.add(new_model)
            self._session.commit()
            self._session.refresh(new_model)
            return JobMapper.to_domain(new_model)
