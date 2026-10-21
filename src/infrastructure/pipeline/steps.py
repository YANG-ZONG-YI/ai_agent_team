import os
import json
import shutil
import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from src.infrastructure.pipeline.context import PipelineContext
from src.domain.video_job import JobStatus
from src.infrastructure.ai.script_generator import ScriptGenerator
from src.infrastructure.ai.tts_service import TTSService
from src.infrastructure.ai.video_renderer import VideoRenderer, RenderConfig
from src.infrastructure.adapters.footage_provider import MultiTierFootageManager
from src.infrastructure.adapters.avatar_engine import AvatarEngine

class IPipelineStep(ABC):
    @abstractmethod
    def execute(self, context: PipelineContext) -> None:
        pass

class ScriptStep(IPipelineStep):
    """分鏡劇本生成步驟 (具備 Checkpoint 快取跳過機制)"""

    def __init__(self, script_generator: Optional[ScriptGenerator] = None):
        self._script_generator = script_generator or ScriptGenerator()

    def execute(self, context: PipelineContext) -> None:
        ws = context.workspace
        storyboard_path = ws.storyboard_json_path

        # 推進領域狀態
        if context.job.status == JobStatus.PENDING:
            context.job.start_scripting()

        # Checkpoint 命中判斷：若已存在完整分鏡檔案，直接復用，跳過重複生成
        if os.path.exists(storyboard_path) and os.path.getsize(storyboard_path) > 0:
            with open(storyboard_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            context.job.set_script(data.get("full_narration", ""))
            context.data["storyboard"] = data
            return

        # Checkpoint 未命中，調用生成器
        script = self._script_generator.generate_script(
            topic=context.job.title,
            prompt=context.job.prompt,
            target_duration=context.job.target_duration
        )
        context.job.set_script(script.full_narration)

        storyboard_data = {
            "project_id": str(context.job.id),
            "project_key": ws.project_key,
            "title": context.job.title,
            "prompt": context.job.prompt,
            "target_duration": context.job.target_duration,
            "character_id": context.job.character_id,
            "full_narration": script.full_narration,
            "scenes": [
                {
                    "scene_index": s.scene_index,
                    "narration": s.narration,
                    "visual_prompt": s.visual_prompt,
                    "duration_seconds": s.duration_seconds
                }
                for s in script.scenes
            ]
        }
        with open(storyboard_path, "w", encoding="utf-8") as f:
            json.dump(storyboard_data, f, ensure_ascii=False, indent=2)

        context.data["storyboard"] = storyboard_data

class AudioStep(IPipelineStep):
    """TTS 語音與時間軸生成步驟 (具備音訊快取檢查點)"""

    def __init__(self, tts_service: Optional[TTSService] = None):
        self._tts_service = tts_service or TTSService()

    def execute(self, context: PipelineContext) -> None:
        ws = context.workspace
        audio_path = ws.voice_audio_path

        from src.infrastructure.ai.script_generator import Scene
        storyboard_data = context.data.get("storyboard")
        if not storyboard_data and os.path.exists(ws.storyboard_json_path):
            with open(ws.storyboard_json_path, "r", encoding="utf-8") as f:
                storyboard_data = json.load(f)

        scenes = [
            Scene(
                scene_index=s["scene_index"],
                narration=s["narration"],
                visual_prompt=s.get("visual_prompt", ""),
                duration_seconds=s["duration_seconds"]
            )
            for s in storyboard_data["scenes"]
        ]
        context.data["scenes"] = scenes

        # 若音訊已存在且大於 0 byte，直接跳過合成
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
            # 建立快取合成結果
            from src.infrastructure.ai.tts_service import TTSResult
            context.data["tts_result"] = TTSResult(
                audio_file_path=audio_path,
                subtitles=[],
                total_duration=sum(s.duration_seconds for s in scenes)
            )
            return

        tts_result = self._tts_service.synthesize_speech(scenes, audio_path)
        context.data["tts_result"] = tts_result

class VisualStep(IPipelineStep):
    """素材與立繪生成步驟"""

    def __init__(self, footage_mgr=None, avatar_engine=None):
        self._footage_mgr = footage_mgr or MultiTierFootageManager()
        self._avatar_engine = avatar_engine or AvatarEngine()

    def execute(self, context: PipelineContext) -> None:
        ws = context.workspace
        scenes = context.data.get("scenes", [])
        footage_map = {}
        avatar_map = {}

        for scene in scenes:
            # 背景素材
            try:
                dest_footage = ws.scene_footage_path(scene.scene_index)
                if not os.path.exists(dest_footage):
                    kw = scene.visual_prompt.split(",")[0].strip() if scene.visual_prompt else context.job.title
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asset = loop.run_until_complete(self._footage_mgr.fetch_scene_footage(keyword=kw, min_duration=scene.duration_seconds))
                        else:
                            asset = asyncio.run(self._footage_mgr.fetch_scene_footage(keyword=kw, min_duration=scene.duration_seconds))
                    except Exception:
                        asset = asyncio.run(self._footage_mgr.fetch_scene_footage(keyword=kw, min_duration=scene.duration_seconds))
                    
                    if asset and os.path.exists(asset.file_path):
                        shutil.copyfile(asset.file_path, dest_footage)
                
                if os.path.exists(dest_footage):
                    footage_map[scene.scene_index] = dest_footage
            except Exception:
                pass

            # 立繪切片
            try:
                char_id = context.job.character_id or "default_anchor"
                avatar_clip_file = os.path.join(ws.temp_dir, f"avatar_scene_{scene.scene_index:02d}.mp4")
                if not os.path.exists(avatar_clip_file):
                    self._avatar_engine.render_avatar_clip(
                        character_id=char_id,
                        duration=scene.duration_seconds,
                        output_path=avatar_clip_file,
                        fps=15
                    )
                if os.path.exists(avatar_clip_file):
                    avatar_map[scene.scene_index] = avatar_clip_file
            except Exception:
                pass

        context.data["footage_map"] = footage_map
        context.data["avatar_map"] = avatar_map

class RenderStep(IPipelineStep):
    """成片合成與縮圖渲染步驟"""

    def __init__(self, renderer: Optional[VideoRenderer] = None):
        self._renderer = renderer or VideoRenderer()

    def execute(self, context: PipelineContext) -> None:
        ws = context.workspace
        context.job.start_rendering()

        output_mp4 = ws.master_video_path
        thumbnail_jpg = ws.thumbnail_path

        cfg = RenderConfig(
            width=1080,
            height=1920,
            fps=15,
            title=context.job.title,
            dark_overlay_opacity=0.50,
            character_id=context.job.character_id
        )

        self._renderer.render_video(
            scenes=context.data["scenes"],
            tts_result=context.data["tts_result"],
            output_path=output_mp4,
            config=cfg,
            footage_map=context.data.get("footage_map", {}),
            thumbnail_path=thumbnail_jpg,
            avatar_map=context.data.get("avatar_map", {})
        )

        context.job.mark_completed(
            video_path=output_mp4,
            preview_url=ws.preview_url
        )
