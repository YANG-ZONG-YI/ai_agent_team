import os
import shutil
from typing import List
from src.infrastructure.pipeline.context import PipelineContext
from src.infrastructure.pipeline.steps import IPipelineStep, ScriptStep, AudioStep, VisualStep, RenderStep
from src.domain.repositories import IJobRepository

class ModularPipelineRunner:
    """管線步驟執行器 (Pipeline Step Engine)"""

    def __init__(
        self,
        repository: IJobRepository,
        steps: List[IPipelineStep] = None,
        base_storage_path: str = "/app/storage"
    ):
        self._repository = repository
        self._steps = steps or [
            ScriptStep(),
            AudioStep(),
            VisualStep(),
            RenderStep()
        ]
        self._base_storage_path = base_storage_path

    def run(self, job_id_str: str) -> dict:
        from uuid import UUID
        job_uuid = UUID(job_id_str)
        job = self._repository.get_by_id(job_uuid)
        if not job:
            raise ValueError(f"Job not found: {job_id_str}")

        context = PipelineContext(job=job, base_storage_path=self._base_storage_path)
        context.workspace.ensure_directories()

        try:
            for step in self._steps:
                step.execute(context)
                # 每步執行後透過 Repository 持久化聚合根狀態 (狀態不變量自動守護)
                self._repository.save(context.job)

            ws = context.workspace
            return {
                "status": "COMPLETED",
                "video_path": context.job.video_path,
                "preview_url": context.job.preview_url,
                "thumbnail_url": ws.thumbnail_url,
                "project_key": ws.project_key,
                "project_root": ws.project_root
            }
        except Exception as e:
            context.job.mark_failed(str(e))
            self._repository.save(context.job)
            raise e
        finally:
            try:
                if os.path.exists(context.workspace.temp_dir):
                    shutil.rmtree(context.workspace.temp_dir, ignore_errors=True)
            except Exception:
                pass
