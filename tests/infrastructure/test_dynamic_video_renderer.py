import os
import pytest
import numpy as np
from PIL import Image
from moviepy import ColorClip
from src.infrastructure.ai.script_generator import Scene
from src.infrastructure.ai.tts_service import TTSResult, SubtitleItem
from src.infrastructure.ai.video_renderer import VideoRenderer, RenderConfig

@pytest.fixture
def sample_tts_data(tmp_path):
    audio_file = tmp_path / "voice.wav"
    # 建立最小 dummy wav 檔案
    import wave
    with wave.open(str(audio_file), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(24000)
        # 1 秒靜音
        f.writeframes(b"\x00\x00" * 24000)

    subtitles = [
        SubtitleItem(start_seconds=0.0, end_seconds=1.0, text="測試動態短影音毛片")
    ]
    return TTSResult(audio_path=str(audio_file), duration_seconds=1.0, subtitles=subtitles, srt_content="")

def test_renderer_with_fallback_card(sample_tts_data, tmp_path):
    renderer = VideoRenderer()
    output_mp4 = str(tmp_path / "rendered_fallback.mp4")
    scenes = [Scene(scene_index=1, narration="測試動態短影音毛片", visual_prompt="tech background")]
    
    cfg = RenderConfig(width=360, height=640, fps=10) # 快速小尺寸測試
    res = renderer.render_video(
        scenes=scenes,
        tts_result=sample_tts_data,
        output_path=output_mp4,
        config=cfg
    )
    assert os.path.exists(res)
    assert os.path.getsize(res) > 0

def test_renderer_with_overlay_card(sample_tts_data, tmp_path):
    renderer = VideoRenderer()
    # 測試透明分鏡字幕畫布生成
    arr = renderer._create_transparent_subtitle_card(
        width=360,
        height=640,
        title="標題",
        narration="字幕測試",
        scene_idx=1,
        font_path=None
    )
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (640, 360, 4) # RGBA 四通道帶透明度

def test_renderer_with_bgm_and_thumbnail_and_srt(tmp_path):
    import wave
    # 建立 1 秒語音
    voice_wav = tmp_path / "voice.wav"
    with wave.open(str(voice_wav), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(24000)
        f.writeframes(b"\x00\x00" * 24000)

    # 建立 1 秒 BGM
    bgm_wav = tmp_path / "bgm.wav"
    with wave.open(str(bgm_wav), "w") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(b"\x00\x00\x00\x00" * 44100)

    tts_data = TTSResult(
        audio_path=str(voice_wav),
        duration_seconds=1.0,
        subtitles=[SubtitleItem(start_seconds=0.0, end_seconds=1.0, text="BGM 測試")],
        srt_content="1\n00:00:00,000 --> 00:00:01,000\nBGM 測試\n"
    )

    renderer = VideoRenderer()
    output_mp4 = str(tmp_path / "final.mp4")
    thumb_path = str(tmp_path / "thumb.jpg")
    scenes = [Scene(scene_index=1, narration="BGM 測試", visual_prompt="tech")]

    cfg = RenderConfig(
        width=360,
        height=640,
        fps=10,
        bgm_path=str(bgm_wav),
        bgm_volume=0.15
    )

    res = renderer.render_video(
        scenes=scenes,
        tts_result=tts_data,
        output_path=output_mp4,
        config=cfg,
        thumbnail_path=thumb_path
    )

    # 1. 驗證影片產出
    assert os.path.exists(res)
    assert os.path.getsize(res) > 0
    # 2. 驗證縮圖產出
    assert os.path.exists(thumb_path)
    assert os.path.getsize(thumb_path) > 0
    # 3. 驗證同名 SRT 產出
    srt_path = str(tmp_path / "final.srt")
    assert os.path.exists(srt_path)
    with open(srt_path, "r", encoding="utf-8") as f:
        assert "BGM 測試" in f.read()
