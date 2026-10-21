from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

class JobStatus(str, Enum):
    PENDING = "PENDING"
    SCRIPTING = "SCRIPTING"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DomainStateError(Exception):
    """領域狀態遷移異常"""
    pass

class VideoPipelineJob:
    """影音管線作業聚合根 (Aggregate Root)"""

    def __init__(
        self,
        id: UUID,
        notion_page_id: str,
        title: str,
        prompt: str,
        status: JobStatus = JobStatus.PENDING,
        target_duration: int = 30,
        character_id: str = "default_anchor",
        script_content: Optional[str] = None,
        video_path: Optional[str] = None,
        preview_url: Optional[str] = None,
        error_message: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.notion_page_id = notion_page_id
        self.title = title
        self.prompt = prompt
        self.status = status
        self.target_duration = target_duration
        self.character_id = character_id
        self.script_content = script_content
        self.video_path = video_path
        self.preview_url = preview_url
        self.error_message = error_message
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    def create(
        cls,
        notion_page_id: str,
        title: str,
        prompt: str,
        target_duration: int = 30,
        character_id: str = "default_anchor"
    ) -> "VideoPipelineJob":
        """工廠方法建立新聚合根 (包含目標時長與角色不變量驗證)"""
        if target_duration < 15 or target_duration > 180:
            raise DomainStateError("Target duration must be between 15 and 180 seconds")
        return cls(
            id=uuid4(),
            notion_page_id=notion_page_id,
            title=title,
            prompt=prompt,
            status=JobStatus.PENDING,
            target_duration=target_duration,
            character_id=character_id
        )

    def start_scripting(self) -> None:
        """開始編寫劇本"""
        if self.status != JobStatus.PENDING:
            raise DomainStateError(f"Cannot start scripting from state: {self.status}")
        self.status = JobStatus.SCRIPTING
        self.updated_at = datetime.now(timezone.utc)

    def set_script(self, script_content: str) -> None:
        """設定已生成的劇本"""
        if not script_content or not script_content.strip():
            raise DomainStateError("Script content cannot be empty")
        self.script_content = script_content
        self.updated_at = datetime.now(timezone.utc)

    def start_rendering(self) -> None:
        """進入影音渲染階段"""
        if self.status != JobStatus.SCRIPTING:
            raise DomainStateError(f"Cannot start rendering from state: {self.status}")
        if not self.script_content:
            raise DomainStateError("Cannot render without script content")
        self.status = JobStatus.RENDERING
        self.updated_at = datetime.now(timezone.utc)

    def mark_completed(self, video_path: str, preview_url: str) -> None:
        """標記影音渲染完成"""
        if self.status != JobStatus.RENDERING:
            raise DomainStateError(f"Cannot mark completed from state: {self.status}")
        if not video_path or not preview_url:
            raise DomainStateError("Completed job must provide valid video_path and preview_url")
        self.video_path = video_path
        self.preview_url = preview_url
        self.status = JobStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self, error_message: str) -> None:
        """標記管線作業失敗"""
        self.error_message = error_message
        self.status = JobStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)
