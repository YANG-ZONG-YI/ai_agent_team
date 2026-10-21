from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from abc import ABC, abstractmethod

class FootageSourceType(str, Enum):
    PEXELS = "PEXELS"
    LOCAL_DEFAULT = "LOCAL_DEFAULT"
    SYNTHETIC_CARD = "SYNTHETIC_CARD"

@dataclass
class FootageAsset:
    """毛片資產領域值對象"""
    asset_id: str
    source_type: FootageSourceType
    file_path: str
    duration: float = 0.0
    resolution: Tuple[int, int] = (1080, 1920)
    tags: List[str] = field(default_factory=list)

class IFootageProvider(ABC):
    """毛片提供者領域介面 (DIP)"""
    @abstractmethod
    async def fetch_scene_footage(self, keyword: str, min_duration: float = 3.0) -> Optional[FootageAsset]:
        """依分鏡關鍵字檢索匹配之毛片資產"""
        pass
