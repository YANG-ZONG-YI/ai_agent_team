import os
from dataclasses import dataclass
from typing import List, Optional, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ColorClip, ImageClip, CompositeVideoClip, AudioFileClip
from src.infrastructure.ai.script_generator import Scene
from src.infrastructure.ai.tts_service import TTSResult

@dataclass
class RenderConfig:
    width: int = 1080
    height: int = 1920
    fps: int = 30
    title: str = "自動化短影音"
    font_path: Optional[str] = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    dark_overlay_opacity: float = 0.50
    bgm_path: Optional[str] = None
    bgm_volume: float = 0.15
    character_id: Optional[str] = None
    avatar_scale: float = 0.45
    avatar_pos: tuple = ("right", "bottom")

class VideoRenderer:
    """9:16 直式短影音合成渲染器 (支援真實動態毛片、深色蒙版遮罩、透明大字幕與多音軌融合)"""

    def _get_font(self, font_path: Optional[str], size: int) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        candidates = [
            font_path,
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        for p in candidates:
            if p and os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def _create_transparent_subtitle_card(
        self,
        width: int,
        height: int,
        title: str,
        narration: str,
        scene_idx: int,
        font_path: Optional[str]
    ) -> np.ndarray:
        """使用 Pillow 繪製透明背景的現代大字幕與裝飾徽章 (RGBA)"""
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        title_font = self._get_font(font_path, int(width * 0.05))
        subtitle_font = self._get_font(font_path, int(width * 0.038))
        badge_font = self._get_font(font_path, int(width * 0.03))

        # 頂部主題徽章卡片
        badge_text = f"SCENE 0{scene_idx} | {title}"
        draw.text((int(width * 0.08), int(height * 0.06)), badge_text, fill=(240, 240, 255, 240), font=badge_font)

        # 畫面中心主文字區
        max_chars_per_line = 16
        lines = [narration[i:i + max_chars_per_line] for i in range(0, len(narration), max_chars_per_line)]

        y_text = int(height * 0.42)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            line_w = bbox[2] - bbox[0]
            x_text = (width - line_w) // 2
            # 黑色粗陰影確保高對比度
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    draw.text((x_text + dx, y_text + dy), line, fill=(0, 0, 0, 255), font=title_font)
            # 文字主體（高辨識度明亮金黃）
            draw.text((x_text, y_text), line, fill=(255, 235, 59, 255), font=title_font)
            y_text += int(width * 0.08)

        # 底部引導標籤
        cta_text = "▼ 追蹤看更多乾貨"
        bbox_cta = draw.textbbox((0, 0), cta_text, font=subtitle_font)
        x_cta = (width - (bbox_cta[2] - bbox_cta[0])) // 2
        draw.text((x_cta, int(height * 0.85)), cta_text, fill=(200, 210, 230, 220), font=subtitle_font)

        return np.array(img)

    def _create_scene_card_image(
        self,
        width: int,
        height: int,
        title: str,
        narration: str,
        scene_idx: int,
        font_path: Optional[str]
    ) -> np.ndarray:
        """兜底模式：使用 Pillow 繪製帶幾何漸層視覺風格與圓角卡片之分鏡畫布 (RGB)"""
        img = Image.new("RGB", (width, height), (18, 20, 32))
        draw = ImageDraw.Draw(img)
        
        # 繪製深藍紫頂部漸層裝飾條
        for y in range(int(height * 0.12)):
            factor = y / (height * 0.12)
            r = int(79 + factor * (30 - 79))
            g = int(70 + factor * (41 - 70))
            b = int(229 + factor * (59 - 229))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        title_font = self._get_font(font_path, int(width * 0.05))
        subtitle_font = self._get_font(font_path, int(width * 0.038))
        badge_font = self._get_font(font_path, int(width * 0.03))

        # 頂部主題徽章
        badge_text = f"SCENE 0{scene_idx} | {title}"
        draw.text((int(width * 0.08), int(height * 0.06)), badge_text, fill=(240, 240, 255), font=badge_font)

        # 畫面中心主視覺卡片
        card_box = [int(width * 0.08), int(height * 0.28), int(width * 0.92), int(height * 0.75)]
        draw.rounded_rectangle(card_box, radius=40, fill=(28, 32, 48), outline=(60, 68, 96), width=3)

        max_chars_per_line = 16
        lines = [narration[i:i + max_chars_per_line] for i in range(0, len(narration), max_chars_per_line)]
        
        y_text = int(height * 0.40)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            line_w = bbox[2] - bbox[0]
            x_text = (width - line_w) // 2
            draw.text((x_text + 3, y_text + 3), line, fill=(0, 0, 0), font=title_font)
            draw.text((x_text, y_text), line, fill=(255, 235, 59), font=title_font)
            y_text += int(width * 0.08)

        cta_text = "▼ 追蹤看更多乾貨"
        bbox_cta = draw.textbbox((0, 0), cta_text, font=subtitle_font)
        x_cta = (width - (bbox_cta[2] - bbox_cta[0])) // 2
        draw.text((x_cta, int(height * 0.85)), cta_text, fill=(160, 174, 192), font=subtitle_font)

        return np.array(img)

    def render_video(
        self,
        scenes: List[Scene],
        tts_result: TTSResult,
        output_path: str,
        config: Optional[RenderConfig] = None,
        footage_map: Optional[dict[int, str]] = None,
        thumbnail_path: Optional[str] = None,
        avatar_map: Optional[dict[int, str]] = None
    ) -> str:
        """
        合成直式 9:16 短影音成片 (支援動態毛片多圖層、人物畫中畫疊層、BGM 混音、封面縮圖與外掛 SRT)
        """
        from moviepy import VideoFileClip, CompositeAudioClip
        from moviepy.audio.fx import AudioFadeOut, AudioLoop
        import glob
        import random

        cfg = config or RenderConfig()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        total_duration = tts_result.duration_seconds
        scene_clips = []
        footage_map = footage_map or {}
        avatar_map = avatar_map or {}
        
        # 依照 TTS 生成之時間軸組裝各分鏡的視覺片段
        for idx, sub in enumerate(tts_result.subtitles, 1):
            scene_duration = sub.end_seconds - sub.start_seconds
            footage_file = footage_map.get(idx)
            current_scene_layers = []

            if footage_file and os.path.exists(footage_file):
                # 【多圖層模式】：動態毛片底圖 + 半透明深色遮罩 + 大字幕
                try:
                    bg_video = VideoFileClip(footage_file)
                    # 若尺寸不符才進行縮放，避免相同尺寸重複進行雙線性重採樣
                    if (bg_video.w, bg_video.h) != (cfg.width, cfg.height):
                        bg_video = bg_video.resized((cfg.width, cfg.height))
                    else:
                        bg_video = bg_video.subclipped(0, scene_duration)
                    bg_video = bg_video.with_start(sub.start_seconds)

                    # 深色半透明蒙版
                    dark_mask = ColorClip(
                        size=(cfg.width, cfg.height),
                        color=(0, 0, 0)
                    ).with_duration(scene_duration).with_opacity(cfg.dark_overlay_opacity).with_start(sub.start_seconds)

                    # 透明字幕層
                    sub_arr = self._create_transparent_subtitle_card(
                        width=cfg.width,
                        height=cfg.height,
                        title=cfg.title,
                        narration=sub.text,
                        scene_idx=idx,
                        font_path=cfg.font_path
                    )
                    sub_clip = ImageClip(sub_arr, is_mask=False, transparent=True).with_duration(scene_duration).with_start(sub.start_seconds)

                    current_scene_layers.extend([bg_video, dark_mask, sub_clip])
                except Exception:
                    pass # 若毛片讀取失敗自動無縫回退至字卡模式

            if not current_scene_layers:
                # 【退化模式】：高品質幾何字卡
                frame_arr = self._create_scene_card_image(
                    width=cfg.width,
                    height=cfg.height,
                    title=cfg.title,
                    narration=sub.text,
                    scene_idx=idx,
                    font_path=cfg.font_path
                )
                clip = ImageClip(frame_arr).with_duration(scene_duration).with_start(sub.start_seconds)
                current_scene_layers.append(clip)

            # 【中景人物層】：畫中畫零失真人物立繪口型疊層 (置於右下角)
            avatar_file = avatar_map.get(idx)
            if avatar_file and os.path.exists(avatar_file):
                try:
                    av_clip = VideoFileClip(avatar_file)
                    av_h = int(cfg.height * cfg.avatar_scale)
                    av_w = int(av_clip.w * (av_h / av_clip.h))
                    av_clip = av_clip.resized((av_w, av_h))
                    if av_clip.duration > scene_duration:
                        av_clip = av_clip.subclipped(0, scene_duration)
                    pos_x = int(cfg.width - av_w - (cfg.width * 0.04))
                    pos_y = int(cfg.height - av_h - (cfg.height * 0.04))
                    av_clip = av_clip.with_position((pos_x, pos_y)).with_start(sub.start_seconds).with_duration(scene_duration)
                    current_scene_layers.append(av_clip)
                except Exception:
                    pass

            scene_clips.extend(current_scene_layers)
            
        # 組合背景底圖與各分鏡視覺
        composite = CompositeVideoClip(scene_clips, size=(cfg.width, cfg.height))
        composite = composite.with_duration(total_duration)

        # 封面縮圖截取 (擷取中前段畫面)
        if thumbnail_path:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(thumbnail_path)), exist_ok=True)
                thumb_time = min(1.0, total_duration * 0.5) if total_duration > 0 else 0
                thumb_frame = composite.get_frame(thumb_time)
                Image.fromarray(thumb_frame).save(thumbnail_path, quality=90)
            except Exception:
                pass
        
        # 音訊處理：主語音人聲軌
        audio_tracks = []
        voice_audio = None
        if tts_result.audio_path and os.path.exists(tts_result.audio_path):
            voice_audio = AudioFileClip(tts_result.audio_path)
            audio_tracks.append(voice_audio)

        # 背景音樂解析 (優先使用 cfg.bgm_path，次之掃描 storage/shared/bgm)
        target_bgm = cfg.bgm_path
        if not target_bgm or not os.path.exists(target_bgm):
            base_storage = os.getenv("VIDEO_STORAGE_PATH", "/app/storage")
            bgm_dir = os.path.join(base_storage, "shared", "bgm")
            if os.path.exists(bgm_dir):
                candidates = glob.glob(os.path.join(bgm_dir, "*.mp3")) + glob.glob(os.path.join(bgm_dir, "*.wav"))
                if candidates:
                    target_bgm = random.choice(candidates)

        bgm_clip = None
        if target_bgm and os.path.exists(target_bgm):
            try:
                bgm_raw = AudioFileClip(target_bgm)
                fade_dur = min(1.5, total_duration * 0.3)
                
                effects = []
                if bgm_raw.duration < total_duration:
                    effects.append(AudioLoop(duration=total_duration))
                if fade_dur > 0:
                    effects.append(AudioFadeOut(duration=fade_dur))
                    
                if effects:
                    bgm_clip = bgm_raw.with_effects(effects)
                else:
                    bgm_clip = bgm_raw.subclipped(0, total_duration)

                bgm_clip = bgm_clip.with_volume_scaled(cfg.bgm_volume)
                audio_tracks.append(bgm_clip)
            except Exception:
                pass

        if len(audio_tracks) > 1:
            final_audio = CompositeAudioClip(audio_tracks).with_duration(total_duration)
        elif len(audio_tracks) == 1:
            final_audio = audio_tracks[0]
        else:
            final_audio = None

        if final_audio is not None:
            final_video = composite.with_audio(final_audio)
        else:
            final_video = composite
        
        # 輸出標準 MP4 (libx264 影像 + aac 音訊)
        final_video.write_videofile(
            output_path,
            fps=cfg.fps,
            codec="libx264",
            audio_codec="aac" if final_video.audio else None,
            preset="ultrafast",
            logger=None
        )

        # 外掛 SRT 字幕檔案導出 (與 MP4 同檔名)
        if tts_result.srt_content:
            try:
                srt_path = os.path.splitext(output_path)[0] + ".srt"
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(tts_result.srt_content)
            except Exception:
                pass
        
        # 釋放資源
        final_video.close()
        if voice_audio:
            voice_audio.close()
        if bgm_clip:
            bgm_clip.close()
        composite.close()
        
        return output_path
