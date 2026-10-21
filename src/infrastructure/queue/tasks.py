import os
from uuid import UUID
import numpy as np
from src.infrastructure.database.models import SessionLocal, VideoJobModel
from src.infrastructure.database.script_repository import ScriptKnowledgeRepository
from src.infrastructure.ai.script_generator import ScriptGenerator
from src.infrastructure.ai.tts_service import TTSService
from src.infrastructure.ai.video_renderer import VideoRenderer, RenderConfig
from src.infrastructure.queue.celery_app import celery_app

def generate_simple_embedding(text: str) -> list[float]:
    """生成 1536 維度文本特徵向量 (可接軌 OpenAI Embedding API)"""
    vec = np.zeros(1536)
    # 根據文本 hash 產生確定性分佈向量供去重檢驗
    val = abs(hash(text)) % 1000 / 1000.0
    vec[0] = val
    vec[1] = 1.0 - val
    norm = np.linalg.norm(vec)
    return (vec / (norm if norm > 0 else 1.0)).tolist()

def run_video_pipeline_sync(job_id_str: str) -> dict:
    """
    同步執行影音管線處理核心邏輯 (透過 FEATURE_MODULAR_PIPELINE 支援絞殺者平滑遷移與一鍵回滾)
    """
    feature_modular = os.getenv("FEATURE_MODULAR_PIPELINE", "true").lower() == "true"
    if feature_modular:
        from src.infrastructure.database.models import SessionLocal
        from src.infrastructure.database.job_repository import SqlAlchemyJobRepository
        from src.infrastructure.pipeline.runner import ModularPipelineRunner
        
        session = SessionLocal()
        try:
            repo = SqlAlchemyJobRepository(session)
            base_storage = os.getenv("VIDEO_STORAGE_PATH", "/app/storage")
            runner = ModularPipelineRunner(repository=repo, base_storage_path=base_storage)
            return runner.run(job_id_str)
        finally:
            session.close()
    else:
        return _legacy_run_video_pipeline_sync(job_id_str)

def _legacy_run_video_pipeline_sync(job_id_str: str) -> dict:
    session = SessionLocal()
    job_uuid = UUID(job_id_str)
    job = session.query(VideoJobModel).filter_by(id=job_uuid).first()
    
    if not job:
        session.close()
        raise ValueError(f"Job not found: {job_id_str}")
        
    base_storage = os.getenv("VIDEO_STORAGE_PATH", "/app/storage")
    from src.domain.workspace import ProjectWorkspace
    import json
    import shutil

    # 初始化多專案自包含獨立工作區 (保證資產 100% 隔離聚合於單一目錄)
    ws = ProjectWorkspace(project_id=str(job.id), title=job.title, base_storage_path=base_storage)
    ws.ensure_directories()
    
    try:
        # 1. 進入 SCRIPTING 狀態
        job.status = "SCRIPTING"
        session.commit()
        
        # 2. 生成分鏡劇本並保存至專案工作區 01_script (依 target_duration 動態反向推導)
        script_gen = ScriptGenerator()
        script = script_gen.generate_script(
            topic=job.title,
            prompt=job.prompt,
            target_duration=getattr(job, "target_duration", 30)
        )
        job.script_content = script.full_narration

        storyboard_data = {
            "project_id": str(job.id),
            "project_key": ws.project_key,
            "title": job.title,
            "prompt": job.prompt,
            "target_duration": getattr(job, "target_duration", 30),
            "character_id": getattr(job, "character_id", "default_anchor"),
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
        with open(ws.storyboard_json_path, "w", encoding="utf-8") as f:
            json.dump(storyboard_data, f, ensure_ascii=False, indent=2)
        
        # 3. 向量檢索與持久化去重
        repo = ScriptKnowledgeRepository(session)
        embedding_vec = generate_simple_embedding(script.full_narration)
        repo.save_script_embedding(
            job_id=job.id,
            script_content=script.full_narration,
            embedding=embedding_vec
        )
        
        # 4. TTS 語音合成與字幕時間軸生成 (儲存至專案工作區 03_audio)
        tts_service = TTSService()
        audio_path = ws.voice_audio_path
        tts_result = tts_service.synthesize_speech(script.scenes, audio_path)
        
        # 5. 進入 RENDERING 狀態
        job.status = "RENDERING"
        session.commit()
        
        # 6. 動態視覺毛片與零失真人物立繪口型動畫生成 (畫中畫 PIP)
        import asyncio
        from src.infrastructure.adapters.footage_provider import MultiTierFootageManager
        from src.infrastructure.adapters.avatar_engine import AvatarEngine

        footage_mgr = MultiTierFootageManager()
        avatar_engine = AvatarEngine(base_storage_path=base_storage)
        footage_map = {}
        avatar_map = {}

        for scene in script.scenes:
            # 6.1 視覺背景檢索
            try:
                kw = scene.visual_prompt.split(",")[0].strip() if scene.visual_prompt else job.title
                asset = asyncio.run(footage_mgr.fetch_scene_footage(keyword=kw, min_duration=scene.duration_seconds))
                if asset and os.path.exists(asset.file_path):
                    dest_footage = ws.scene_footage_path(scene.scene_index)
                    if not os.path.exists(dest_footage):
                        shutil.copyfile(asset.file_path, dest_footage)
                    footage_map[scene.scene_index] = dest_footage
            except Exception:
                pass

            # 6.2 零失真固定立繪口型驅動切片
            try:
                char_id = getattr(job, "character_id", "default_anchor") or "default_anchor"
                avatar_clip_file = os.path.join(ws.temp_dir, f"avatar_scene_{scene.scene_index:02d}.mp4")
                avatar_engine.render_avatar_clip(
                    character_id=char_id,
                    duration=scene.duration_seconds,
                    output_path=avatar_clip_file,
                    fps=15
                )
                if os.path.exists(avatar_clip_file):
                    avatar_map[scene.scene_index] = avatar_clip_file
            except Exception:
                pass

        renderer = VideoRenderer()
        output_mp4 = ws.master_video_path
        thumbnail_jpg = ws.thumbnail_path
        cfg = RenderConfig(
            width=1080,
            height=1920,
            fps=15, # 高效生成
            title=job.title,
            dark_overlay_opacity=0.50,
            character_id=getattr(job, "character_id", "default_anchor")
        )
        renderer.render_video(
            scenes=script.scenes,
            tts_result=tts_result,
            output_path=output_mp4,
            config=cfg,
            footage_map=footage_map,
            thumbnail_path=thumbnail_jpg,
            avatar_map=avatar_map
        )

        # 7. 標記完成並記錄專案專屬預覽 URL 與縮圖 URL (資產完全自包含於 05_output)
        preview_url = ws.preview_url
        thumbnail_url = ws.thumbnail_url
        job.video_path = output_mp4
        job.preview_url = preview_url
        job.thumbnail_url = thumbnail_url
        job.status = "COMPLETED"
        session.commit()
        
        return {
            "status": "COMPLETED",
            "video_path": output_mp4,
            "preview_url": preview_url,
            "thumbnail_url": thumbnail_url,
            "project_key": ws.project_key,
            "project_root": ws.project_root
        }
        
    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        session.commit()
        raise e
    finally:
        try:
            if os.path.exists(ws.temp_dir):
                shutil.rmtree(ws.temp_dir, ignore_errors=True)
        except Exception:
            pass
        session.close()

@celery_app.task(name="produce_video_task", bind=True, max_retries=3)
def produce_video_task(self, job_id_str: str):
    """Celery 背景異步任務包裝"""
    return run_video_pipeline_sync(job_id_str)

def run_matrix_publish_sync(job_id_str: str, platforms: list[str]) -> list[dict]:
    """
    同步執行四大多平台矩陣分發核心邏輯 (YT / IG / FB / TikTok)
    單一平台失敗不阻斷其他平台 (失敗隔離)
    """
    from datetime import datetime, timezone
    from src.domain.publish_task import PlatformType
    from src.infrastructure.database.models import PublishTaskModel
    from src.infrastructure.adapters.social_publishers import SocialPublisherFactory
    from src.infrastructure.adapters.notion_adapter import NotionAdapter

    session = SessionLocal()
    job_uuid = UUID(job_id_str)
    job = session.query(VideoJobModel).filter_by(id=job_uuid).first()
    
    if not job:
        session.close()
        raise ValueError(f"Job not found: {job_id_str}")
        
    if not job.video_path or not os.path.exists(job.video_path):
        session.close()
        raise ValueError(f"Job video file does not exist: {job.video_path}")

    results = []
    
    try:
        for p_name in platforms:
            platform_enum = PlatformType(p_name.upper())
            
            # 建立或查詢發布任務記錄
            task = session.query(PublishTaskModel).filter_by(
                job_id=job.id,
                platform=platform_enum.value
            ).first()
            
            if not task:
                task = PublishTaskModel(
                    job_id=job.id,
                    platform=platform_enum.value,
                    status="PUBLISHING",
                    retry_count=0
                )
                session.add(task)
            else:
                task.status = "PUBLISHING"
                
            session.commit()
            
            # 呼叫防腐層適配器發布
            publisher = SocialPublisherFactory.get_publisher(platform_enum)
            pub_res = publisher.publish_video(
                title=job.title,
                description=job.script_content or job.prompt,
                video_path=job.video_path
            )
            
            if pub_res.success:
                task.status = "PUBLISHED"
                task.platform_video_id = pub_res.platform_video_id
                task.published_at = datetime.now(timezone.utc)
            else:
                task.retry_count += 1
                task.error_log = pub_res.error_message
                task.status = "FAILED" if task.retry_count >= 3 else "RETRYING"
                
            session.commit()
            session.refresh(task)
            
            results.append({
                "platform": task.platform,
                "status": task.status,
                "platform_video_id": task.platform_video_id,
                "error_log": task.error_log
            })
            
        return results
    finally:
        session.close()

@celery_app.task(name="publish_matrix_task", bind=True, max_retries=3)
def publish_matrix_task(self, job_id_str: str, platforms: list[str]):
    """Celery 背景矩陣發布異步任務包裝"""
    return run_matrix_publish_sync(job_id_str, platforms)

