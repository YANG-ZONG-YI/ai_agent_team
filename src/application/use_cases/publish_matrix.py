from dataclasses import dataclass
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

@dataclass
class PublishMatrixInput:
    job_id: str
    platforms: List[str]

class PublishMatrixUseCase:
    """多平台矩陣分發應用案例 (具備失敗隔離與單平台冪等性保護)"""

    def __init__(self, job_repository, publish_repository, publisher_factory):
        self._job_repository = job_repository
        self._publish_repository = publish_repository
        self._publisher_factory = publisher_factory

    def execute(self, input_dto: PublishMatrixInput) -> List[Dict[str, Any]]:
        job_uuid = UUID(input_dto.job_id)
        job = self._job_repository.get_by_id(job_uuid)
        if not job:
            raise ValueError(f"Job not found: {input_dto.job_id}")

        results = []
        for p_name in input_dto.platforms:
            platform_str = p_name.upper()
            existing_task = self._publish_repository.get_task(job.id, platform_str)

            # 冪等防護：若該平台已經發布成功，直接返回，不再重複發布避免洗版
            if existing_task and existing_task.status == "PUBLISHED":
                results.append({
                    "platform": platform_str,
                    "status": "PUBLISHED",
                    "platform_video_id": getattr(existing_task, "platform_video_id", None),
                    "error_log": None
                })
                continue

            # 執行發布
            task = self._publish_repository.record_start(job.id, platform_str)
            publisher = self._publisher_factory.get_publisher(platform_str)
            pub_res = publisher.publish_video(
                title=job.title,
                description=getattr(job, "script_content", "") or getattr(job, "prompt", ""),
                video_path=job.video_path
            )

            if pub_res.success:
                task = self._publish_repository.record_success(task, pub_res.platform_video_id)
            else:
                task = self._publish_repository.record_failure(task, pub_res.error_message)

            results.append({
                "platform": platform_str,
                "status": task.status,
                "platform_video_id": getattr(task, "platform_video_id", None),
                "error_log": getattr(task, "error_log", None)
            })

        return results
