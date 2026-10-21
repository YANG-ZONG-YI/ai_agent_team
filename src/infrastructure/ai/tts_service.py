import os
import wave
import struct
import math
import asyncio
import logging
import tempfile
from dataclasses import dataclass
from typing import List, Optional
from moviepy import AudioFileClip, concatenate_audioclips
import edge_tts
from src.infrastructure.ai.script_generator import Scene

logger = logging.getLogger(__name__)

@dataclass
class SubtitleItem:
    start_seconds: float
    end_seconds: float
    text: str

@dataclass
class TTSResult:
    audio_path: str
    duration_seconds: float
    subtitles: List[SubtitleItem]
    srt_content: str

def format_timestamp(seconds: float) -> str:
    """轉換秒數為 SRT 標準時間戳記 (00:00:00,000)"""
    millis = int((seconds - int(seconds)) * 1000)
    secs = int(seconds) % 60
    mins = (int(seconds) // 60) % 60
    hours = int(seconds) // 3600
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

class TTSService:
    """文字轉語音 (TTS) 與字幕時間軸生成服務 (採用微軟 Edge TTS 自然語音)"""

    def __init__(self, voice: Optional[str] = None):
        # 預設採用微軟高品質台灣繁體中文男聲
        self.default_voice = voice or os.getenv("TTS_VOICE", "zh-TW-YunJheNeural")

    def synthesize_speech(
        self,
        scenes: List[Scene],
        output_audio_path: str,
        voice: Optional[str] = None
    ) -> TTSResult:
        """
        合成各分鏡之真實語音並生成精準對齊之 SRT 字幕時間軸
        若網路或服務異常，自動降級至保底音軌
        """
        chosen_voice = voice or self.default_voice
        try:
            return asyncio.run(self._synthesize_with_edge_tts(scenes, output_audio_path, chosen_voice))
        except Exception as e:
            logger.warning(f"Edge TTS 語音合成異常 ({e})，自動降級至保底音軌: {e}")
            return self._fallback_synthesize(scenes, output_audio_path)

    async def _synthesize_with_edge_tts(
        self,
        scenes: List[Scene],
        output_audio_path: str,
        voice: str
    ) -> TTSResult:
        """非同步透過 Edge TTS 合成分鏡語音並拼接整合"""
        subtitles: List[SubtitleItem] = []
        temp_files: List[str] = []
        audio_clips: List[AudioFileClip] = []
        current_time = 0.0

        os.makedirs(os.path.dirname(os.path.abspath(output_audio_path)), exist_ok=True)

        try:
            for scene in scenes:
                narration = (scene.narration or "").strip()
                if not narration:
                    narration = "..."

                # 為每個分鏡生成單獨之音訊片段
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                    tmp_mp3 = tmp_file.name
                    temp_files.append(tmp_mp3)

                communicate = edge_tts.Communicate(narration, voice)
                await communicate.save(tmp_mp3)

                clip = AudioFileClip(tmp_mp3)
                audio_clips.append(clip)

                scene_duration = clip.duration
                start_t = current_time
                end_t = start_t + scene_duration

                subtitles.append(SubtitleItem(
                    start_seconds=start_t,
                    end_seconds=end_t,
                    text=scene.narration
                ))
                current_time = end_t

            if not audio_clips:
                raise ValueError("未生成任何有效分鏡音訊")

            # 串接所有分鏡之語音軌道
            final_audio = concatenate_audioclips(audio_clips)
            total_duration = current_audio_dur = final_audio.duration

            final_audio.write_audiofile(
                output_audio_path,
                fps=44100,
                logger=None
            )
            final_audio.close()

            # 產生標準 SRT 格式內容
            srt_lines = []
            for idx, sub in enumerate(subtitles, 1):
                srt_lines.append(f"{idx}")
                srt_lines.append(f"{format_timestamp(sub.start_seconds)} --> {format_timestamp(sub.end_seconds)}")
                srt_lines.append(sub.text)
                srt_lines.append("")

            srt_content = "\n".join(srt_lines)

            return TTSResult(
                audio_path=output_audio_path,
                duration_seconds=total_duration,
                subtitles=subtitles,
                srt_content=srt_content
            )

        finally:
            # 關閉並釋放所有 MoviePy AudioFileClip
            for c in audio_clips:
                try:
                    c.close()
                except Exception:
                    pass
            # 清理暫存 mp3 檔案
            for f in temp_files:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except Exception:
                    pass

    def _fallback_synthesize(self, scenes: List[Scene], output_audio_path: str) -> TTSResult:
        """斷網或第三方異常時之確定性保底音訊生成"""
        subtitles: List[SubtitleItem] = []
        current_time = 0.0

        for scene in scenes:
            start_t = current_time
            calc_duration = max(scene.duration_seconds, len(scene.narration) * 0.25)
            end_t = start_t + calc_duration

            subtitles.append(SubtitleItem(
                start_seconds=start_t,
                end_seconds=end_t,
                text=scene.narration
            ))
            current_time = end_t

        total_duration = current_time
        sample_rate = 44100
        total_samples = int(sample_rate * total_duration)

        frames = bytearray()
        for i in range(total_samples):
            t = i / sample_rate
            val = int(500 * math.sin(2 * math.pi * 220 * t))
            frames.extend(struct.pack('<h', val))

        os.makedirs(os.path.dirname(os.path.abspath(output_audio_path)), exist_ok=True)
        with wave.open(output_audio_path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(frames)

        srt_lines = []
        for idx, sub in enumerate(subtitles, 1):
            srt_lines.append(f"{idx}")
            srt_lines.append(f"{format_timestamp(sub.start_seconds)} --> {format_timestamp(sub.end_seconds)}")
            srt_lines.append(sub.text)
            srt_lines.append("")

        return TTSResult(
            audio_path=output_audio_path,
            duration_seconds=total_duration,
            subtitles=subtitles,
            srt_content="\n".join(srt_lines)
        )

