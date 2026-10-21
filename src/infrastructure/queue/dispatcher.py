from src.application.ports import IQueueDispatcher
from src.infrastructure.queue.tasks import produce_video_task

class CeleryQueueDispatcher(IQueueDispatcher):
    """Celery 任務佇列派發實作 (Infrastructure Adapter)"""

    def dispatch(self, job_id_str: str) -> None:
        produce_video_task.delay(job_id_str)
