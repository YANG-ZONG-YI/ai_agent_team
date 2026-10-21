import os
import pytest
from src.infrastructure.ai.script_generator import Scene
from src.infrastructure.ai.tts_service import TTSService, TTSResult

def test_tts_service_generation(tmp_path):
    tts = TTSService()
    scenes = [
        Scene(scene_index=1, narration="第一段開場旁白測試", visual_prompt="", duration_seconds=2.0),
        Scene(scene_index=2, narration="第二段核心重點說明", visual_prompt="", duration_seconds=3.0)
    ]
    output_audio = str(tmp_path / "test_voice.wav")
    
    result = tts.synthesize_speech(scenes=scenes, output_audio_path=output_audio)
    
    assert isinstance(result, TTSResult)
    assert os.path.exists(result.audio_path)
    assert os.path.getsize(result.audio_path) > 1000 # 確保真實產生有效音訊數據
    assert result.duration_seconds > 0
    assert len(result.subtitles) == 2
    assert result.subtitles[0].end_seconds <= result.subtitles[1].start_seconds + 0.05
    assert "第一段開場旁白測試" in result.srt_content
    assert "第二段核心重點說明" in result.srt_content

def test_tts_service_fallback_on_error(monkeypatch, tmp_path):
    tts = TTSService()
    
    class MockCommunicate:
        def __init__(self, *args, **kwargs):
            pass
        async def save(self, *args, **kwargs):
            raise ConnectionError("Network unreachable")
        
    import edge_tts
    monkeypatch.setattr(edge_tts, "Communicate", MockCommunicate)
    
    scenes = [
        Scene(scene_index=1, narration="測試斷網降級", visual_prompt="", duration_seconds=2.0)
    ]
    output_audio = str(tmp_path / "fallback_voice.wav")
    result = tts.synthesize_speech(scenes=scenes, output_audio_path=output_audio)
    
    assert os.path.exists(result.audio_path)
    assert result.duration_seconds > 0
    assert len(result.subtitles) == 1
    assert "測試斷網降級" in result.srt_content

