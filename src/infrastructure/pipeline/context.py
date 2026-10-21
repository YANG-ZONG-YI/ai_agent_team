import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from src.domain.video_job import VideoPipelineJob
from src.domain.workspace import ProjectWorkspace

@dataclass
class PipelineContext:
    """管線步驟執行上下文，提供專案工作區路徑、狀態共享與中繼產物傳遞"""
    job: VideoPipelineJob
    base_storage_path: str = "/app/storage"
    workspace: ProjectWorkspace = field(init=False)
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.workspace = ProjectWorkspace(
            project_id=str(self.job.id),
            title=self.job.title,
            base_storage_path=self.base_storage_path
        )
