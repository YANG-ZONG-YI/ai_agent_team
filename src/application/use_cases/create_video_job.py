from dataclasses import dataclass
from typing import Optional
from src.domain.video_job import VideoPipelineJob
from src.domain.repositories import IJobRepository
from src.application.ports import IQueueDispatcher

@dataclass
class CreateVideoJobInput:
    notion_page_id: str
    title: str
    prompt: str
    target_duration: int = 30
    character_id: str = "default_anchor"

@dataclass
class CreateVideoJobOutput:
    status: str
    job_id: str
    title: str

class CreateVideoJobUseCase:
    """建立或排程影音管線作業應用案例 (Use Case)"""

    def __init__(self, repository: IJobRepository, queue_dispatcher: IQueueDispatcher):
        self._repository = repository
        self._queue_dispatcher = queue_dispatcher

    def execute(self, input_dto: CreateVideoJobInput) -> CreateVideoJobOutput:
        # 1. 檢驗是否已有對應 Notion 頁面的既有作業 (冪等處理)
        existing_job = self._repository.get_by_notion_page_id(input_dto.notion_page_id)
        if existing_job:
            target_job = existing_job
        else:
            # 2. 透過領域聚合根工廠方法建立新實體 (包含領域不變量校驗)
            new_job = VideoPipelineJob.create(
                notion_page_id=input_dto.notion_page_id,
                title=input_dto.title,
                prompt=input_dto.prompt,
                target_duration=input_dto.target_duration,
                character_id=input_dto.character_id
            )
            target_job = self._repository.save(new_job)

        # 3. 透過應用抽象介面派發至佇列
        self._queue_dispatcher.dispatch(str(target_job.id))

        return CreateVideoJobOutput(
            status="QUEUED",
            job_id=str(target_job.id),
            title=target_job.title
        )
