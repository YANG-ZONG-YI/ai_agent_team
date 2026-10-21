from dataclasses import dataclass
from uuid import UUID
from src.domain.repositories import IJobRepository

class DomainNotFoundError(Exception):
    pass

class DomainValidationError(Exception):
    pass

@dataclass
class SyncPreviewInput:
    job_id: str

@dataclass
class SyncPreviewOutput:
    status: str
    notion_page_id: str
    preview_url: str

class SyncPreviewUseCase:
    """成片預覽 URL 同步至 Notion 應用案例"""

    def __init__(self, repository: IJobRepository, notion_adapter):
        self._repository = repository
        self._notion_adapter = notion_adapter

    async def execute(self, input_dto: SyncPreviewInput) -> SyncPreviewOutput:
        job = self._repository.get_by_id(UUID(input_dto.job_id))
        if not job:
            raise DomainNotFoundError(f"Job not found: {input_dto.job_id}")
        if not job.preview_url:
            raise DomainValidationError("Job has no completed preview URL")

        update_data = self._notion_adapter.build_update_payload(
            status="待發布",
            preview_url=job.preview_url
        )
        await self._notion_adapter.update_page(job.notion_page_id, update_data)

        return SyncPreviewOutput(
            status="SYNCED",
            notion_page_id=job.notion_page_id,
            preview_url=job.preview_url
        )
