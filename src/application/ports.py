from abc import ABC, abstractmethod

class IQueueDispatcher(ABC):
    """異步任務隊列派發介面 (Application Port)"""

    @abstractmethod
    def dispatch(self, job_id_str: str) -> None:
        """派發作業 ID 至佇列"""
        pass
