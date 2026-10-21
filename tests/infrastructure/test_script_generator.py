import pytest
from src.infrastructure.ai.script_generator import ScriptGenerator, GeneratedScript, Scene

def test_script_generator_structure():
    generator = ScriptGenerator()
    script = generator.generate_script(
        topic="Python 3.12 新功能解析",
        prompt="請以快節奏、吸引人的短影音格式，生成 3 個分鏡的短影音劇本"
    )
    
    assert isinstance(script, GeneratedScript)
    assert len(script.scenes) >= 3
    assert script.total_estimated_duration > 0
    
    first_scene = script.scenes[0]
    assert isinstance(first_scene, Scene)
    assert first_scene.scene_index == 1
    assert len(first_scene.narration) > 0
    assert len(first_scene.visual_prompt) > 0
