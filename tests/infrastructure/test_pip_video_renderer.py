import os
import pytest
from src.infrastructure.ai.script_generator import Scene
from src.infrastructure.ai.tts_service import TTSResult, SubtitleItem
from src.infrastructure.ai.video_renderer import VideoRenderer, RenderConfig
from src.infrastructure.adapters.avatar_engine import AvatarEngine

def test_render_video_with_pip_avatar_overlay(tmp_path):
    renderer = VideoRenderer()
    avatar_engine = AvatarEngine(base_storage_path=str(tmp_path))
    
    # 準備 1 個 2 秒分鏡
    scenes = [
        Scene(scene_index=1, narration="歡迎來到 AI 影片產製系統", visual_prompt="科技藍背景", duration_seconds=2.0)
    ]
    # 建立 2 秒測試音訊
    import wave, struct
    audio_wav_path = str(tmp_path / "voice_master.wav")
    with wave.open(audio_wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        data = struct.pack("<" + ("h" * 32000), *([0] * 32000))
        wf.writeframes(data)

    tts_result = TTSResult(
        audio_path=audio_wav_path,
        duration_seconds=2.0,
        subtitles=[SubtitleItem(start_seconds=0.0, end_seconds=2.0, text="歡迎來到 AI 影片產製系統")],
        srt_content="1\n00:00:00,000 --> 00:00:02,000\n歡迎來到 AI 影片產製系統\n"
    )
    
    # 生成人物口型切片
    avatar_clip_path = str(tmp_path / "avatar_s1.mp4")
    avatar_engine.render_avatar_clip("default_anchor", duration=2.0, output_path=avatar_clip_path)
    
    output_video = str(tmp_path / "output_master.mp4")
    cfg = RenderConfig(
        width=540,
        height=960,
        fps=24,
        character_id="default_anchor"
    )
    
    res = renderer.render_video(
        scenes=scenes,
        tts_result=tts_result,
        output_path=output_video,
        config=cfg,
        avatar_map={1: avatar_clip_path}
    )
    
    assert os.path.exists(res)
    assert os.path.getsize(res) > 0
