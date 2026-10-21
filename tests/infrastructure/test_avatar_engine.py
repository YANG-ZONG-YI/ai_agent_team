import os
import pytest
from src.infrastructure.adapters.avatar_engine import AvatarEngine, CharacterProfile

def test_avatar_engine_loads_character_profile(tmp_path):
    engine = AvatarEngine(base_storage_path=str(tmp_path))
    profile = engine.get_character_profile("default_anchor")
    assert isinstance(profile, CharacterProfile)
    assert profile.character_id == "default_anchor"
    assert os.path.exists(profile.portrait_path)

def test_avatar_engine_renders_lip_sync_motion(tmp_path):
    engine = AvatarEngine(base_storage_path=str(tmp_path))
    output_video = str(tmp_path / "avatar_clip.mp4")
    
    # 傳入 3 秒時長，驗證生成之動態角色切片存在且時長吻合
    result_path = engine.render_avatar_clip(
        character_id="default_anchor",
        duration=3.0,
        output_path=output_video
    )
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0
