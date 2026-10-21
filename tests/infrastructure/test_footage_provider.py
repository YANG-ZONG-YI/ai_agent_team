import os
import pytest
from unittest.mock import patch, MagicMock
from src.domain.footage import FootageAsset, FootageSourceType
from src.infrastructure.adapters.footage_provider import MultiTierFootageManager, PexelsFootageAdapter, LocalFootageAdapter

def test_footage_asset_creation():
    asset = FootageAsset(
        asset_id="test_01",
        source_type=FootageSourceType.LOCAL_DEFAULT,
        file_path="/app/storage/shared/default_footage/sample.mp4",
        duration=5.0,
        tags=["tech", "ai"]
    )
    assert asset.asset_id == "test_01"
    assert asset.source_type == FootageSourceType.LOCAL_DEFAULT
    assert asset.file_path.endswith("sample.mp4")

@pytest.mark.asyncio
async def test_local_footage_adapter_with_files(tmp_path):
    # 建立臨時毛片檔案
    footage_dir = tmp_path / "footage"
    footage_dir.mkdir()
    sample_mp4 = footage_dir / "tech_video.mp4"
    sample_mp4.write_text("dummy video content")
    
    adapter = LocalFootageAdapter(storage_dir=str(footage_dir))
    asset = await adapter.fetch_scene_footage(keyword="tech")
    
    assert asset is not None
    assert asset.source_type == FootageSourceType.LOCAL_DEFAULT
    assert os.path.exists(asset.file_path)

@pytest.mark.asyncio
async def test_local_footage_adapter_empty_dir(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    adapter = LocalFootageAdapter(storage_dir=str(empty_dir))
    asset = await adapter.fetch_scene_footage(keyword="nature")
    assert asset is None

@pytest.mark.asyncio
async def test_multi_tier_fallback_to_none_when_empty(tmp_path):
    manager = MultiTierFootageManager(
        pexels_api_key="",
        local_footage_dir=str(tmp_path)
    )
    asset = await manager.fetch_scene_footage(keyword="nonexistent")
    assert asset is None
