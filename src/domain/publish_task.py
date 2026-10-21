from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

class PlatformType(str, Enum):
    YOUTUBE = "YOUTUBE"
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    TIKTOK = "TIKTOK"

class PublishStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    RETRYING = "RETRYING"
    FAILED = "FAILED"

class MaxRetriesExceededError(Exception):
    """已超過最大重試次數"""
    pass

class PublishTask:
    """社交平台發布任務聚合根 (Aggregate Root)"""

    MAX_RETRIES = 3

    def __init__(
        self,
        id: UUID,
        job_id: UUID,
        platform: PlatformType,
        status: PublishStatus = PublishStatus.SCHEDULED,
        retry_count: int = 0,
        platform_video_id: Optional[str] = None,
        error_log: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        published_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.job_id = job_id
        self.platform = platform
        self.status = status
        self.retry_count = retry_count
        self.platform_video_id = platform_video_id
        self.error_log = error_log
        self.scheduled_at = scheduled_at or datetime.now(timezone.utc)
        self.published_at = published_at
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    def create(cls, job_id: UUID, platform: PlatformType) -> "PublishTask":
        return cls(
            id=uuid4(),
            job_id=job_id,
            platform=platform,
            status=PublishStatus.SCHEDULED,
            retry_count=0
        )

    def mark_publishing(self) -> None:
        self.status = PublishStatus.PUBLISHING
        self.updated_at = datetime.now(timezone.utc)

    def mark_published(self, platform_video_id: str) -> None:
        self.platform_video_id = platform_video_id
        self.status = PublishStatus.PUBLISHED
        self.published_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def record_failure(self, error_message: str) -> None:
        if self.status == PublishStatus.FAILED:
            raise MaxRetriesExceededError(f"Task already failed after {self.MAX_RETRIES} attempts")
        
        self.retry_count += 1
        self.error_log = error_message
        
        if self.retry_count >= self.MAX_RETRIES:
            self.status = PublishStatus.FAILED
        else:
            self.status = PublishStatus.RETRYING
            
        self.updated_at = datetime.now(timezone.utc)
