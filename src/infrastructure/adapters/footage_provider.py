import os
import glob
import random
import httpx
from typing import Optional, List
from src.domain.footage import FootageAsset, FootageSourceType, IFootageProvider

class LocalFootageAdapter(IFootageProvider):
    """本地預置毛片提供者"""
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    async def fetch_scene_footage(self, keyword: str, min_duration: float = 3.0) -> Optional[FootageAsset]:
        if not os.path.exists(self.storage_dir):
            return None
            
        mp4_files = glob.glob(os.path.join(self.storage_dir, "**", "*.mp4"), recursive=True)
        if not mp4_files:
            return None

        # 優先搜尋關鍵字相符的檔案名稱
        matched = [f for f in mp4_files if keyword.lower() in os.path.basename(f).lower()]
        target_file = random.choice(matched) if matched else random.choice(mp4_files)

        return FootageAsset(
            asset_id=os.path.splitext(os.path.basename(target_file))[0],
            source_type=FootageSourceType.LOCAL_DEFAULT,
            file_path=target_file,
            duration=min_duration,
            tags=[keyword]
        )

class PexelsFootageAdapter(IFootageProvider):
    """Pexels 免費短影音 API 適配器"""
    def __init__(self, api_key: str, cache_dir: str):
        self.api_key = api_key
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    async def fetch_scene_footage(self, keyword: str, min_duration: float = 3.0) -> Optional[FootageAsset]:
        if not self.api_key:
            return None

        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.api_key}
        params = {
            "query": keyword,
            "orientation": "portrait",
            "per_page": 5
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code != 200:
                    return None
                data = resp.json()
                videos = data.get("videos", [])
                if not videos:
                    return None
                
                # 選擇符合 9:16 直式解析度的影片檔
                video = random.choice(videos)
                video_files = video.get("video_files", [])
                target_file_url = None
                for vf in video_files:
                    if vf.get("width", 0) < vf.get("height", 0):
                        target_file_url = vf.get("link")
                        break
                if not target_file_url and video_files:
                    target_file_url = video_files[0].get("link")

                if not target_file_url:
                    return None

                # 下載快取至本地
                asset_id = f"pexels_{video.get('id')}"
                local_path = os.path.join(self.cache_dir, f"{asset_id}.mp4")
                if not os.path.exists(local_path):
                    file_resp = await client.get(target_file_url)
                    if file_resp.status_code == 200:
                        with open(local_path, "wb") as f:
                            f.write(file_resp.content)

                return FootageAsset(
                    asset_id=asset_id,
                    source_type=FootageSourceType.PEXELS,
                    file_path=local_path,
                    duration=video.get("duration", min_duration),
                    tags=[keyword]
                )
        except Exception:
            return None

class MultiTierFootageManager(IFootageProvider):
    """多階分層毛片管理器 (Pexels -> Local -> None/Fallback)"""
    def __init__(self, pexels_api_key: Optional[str] = None, local_footage_dir: Optional[str] = None):
        base_storage = os.getenv("VIDEO_STORAGE_PATH", "/app/storage")
        cache_dir = os.path.join(base_storage, "shared", "footage_cache")
        default_dir = local_footage_dir or os.path.join(base_storage, "shared", "default_footage")

        self.pexels_adapter = PexelsFootageAdapter(
            api_key=pexels_api_key or os.getenv("PEXELS_API_KEY", ""),
            cache_dir=cache_dir
        )
        self.local_adapter = LocalFootageAdapter(
            storage_dir=default_dir
        )

    async def fetch_scene_footage(self, keyword: str, min_duration: float = 3.0) -> Optional[FootageAsset]:
        # 1. 優先嘗試 Pexels API
        asset = await self.pexels_adapter.fetch_scene_footage(keyword, min_duration)
        if asset:
            return asset
            
        # 2. 次要嘗試本機預置素材庫
        asset = await self.local_adapter.fetch_scene_footage(keyword, min_duration)
        if asset:
            return asset

        # 3. 若皆無素材，回傳 None 觸發退化機制
        return None
