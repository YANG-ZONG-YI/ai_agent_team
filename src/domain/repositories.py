from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from src.domain.video_job import VideoPipelineJob

class IJobRepository(ABC):
    """領域層作業儲存庫抽象介面 (Domain Port / Dependency Inversion)"""

    @abstractmethod
    def get_by_id(self, job_id: UUID) -> Optional[VideoPipelineJob]:
        """依作業 ID 檢索領域聚合根"""
        pass

    @abstractmethod
    def get_by_notion_page_id(self, notion_page_id: str) -> Optional[VideoPipelineJob]:
        """依 Notion Page ID 檢索領域聚合根"""
        pass

    @abstractmethod
    def save(self, job: VideoPipelineJob) -> VideoPipelineJob:
        """保存或更新聚合根狀態"""
        pass
