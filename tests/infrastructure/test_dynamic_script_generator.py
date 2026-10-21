import pytest
from src.infrastructure.ai.script_generator import ScriptGenerator, GeneratedScript

def test_generate_script_with_custom_duration_30s():
    generator = ScriptGenerator()
    script = generator.generate_script(
        topic="Python 自動化",
        prompt="生成 30 秒實戰教學",
        target_duration=30
    )
    assert isinstance(script, GeneratedScript)
    assert len(script.scenes) >= 5
    assert 25.0 <= script.total_estimated_duration <= 35.0
    for scene in script.scenes:
        assert scene.duration_seconds > 0
        assert len(scene.narration) > 0
        assert len(scene.visual_prompt) > 0

def test_generate_script_with_custom_duration_60s():
    generator = ScriptGenerator()
    script = generator.generate_script(
        topic="AI 深度學習",
        prompt="生成 60 秒深度解說",
        target_duration=60
    )
    assert isinstance(script, GeneratedScript)
    assert len(script.scenes) >= 9
    assert 50.0 <= script.total_estimated_duration <= 70.0

def test_generate_script_with_custom_duration_15s():
    generator = ScriptGenerator()
    script = generator.generate_script(
        topic="極速金句",
        prompt="生成 15 秒開頭爆款",
        target_duration=15
    )
    assert isinstance(script, GeneratedScript)
    assert len(script.scenes) >= 3
    assert 12.0 <= script.total_estimated_duration <= 18.0
