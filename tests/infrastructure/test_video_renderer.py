import os
import pytest
from src.infrastructure.ai.script_generator import Scene
from src.infrastructure.ai.tts_service import TTSService
from src.infrastructure.ai.video_renderer import VideoRenderer, RenderConfig

def test_video_renderer_generates_valid_mp4(tmp_path):
    tts = TTSService()
    renderer = VideoRenderer()
    
    # 建立 2 秒微型分鏡供快速驗收測試
    scenes = [
        Scene(scene_index=1, narration="短影音渲染極速驗證", visual_prompt="", duration_seconds=2.0)
    ]
    audio_path = str(tmp_path / "test_audio.wav")
    tts_result = tts.synthesize_speech(scenes, audio_path)
    
    output_mp4 = str(tmp_path / "rendered_output.mp4")
    config = RenderConfig(
        width=1080,
        height=1920,
        fps=15, # 測試環境加速
        title="AI 自動化短影音測試"
    )
    
    rendered_path = renderer.render_video(
        scenes=scenes,
        tts_result=tts_result,
        output_path=output_mp4,
        config=config
    )
    
    assert os.path.exists(rendered_path)
    assert os.path.getsize(rendered_path) > 0
    assert rendered_path.endswith(".mp4")
