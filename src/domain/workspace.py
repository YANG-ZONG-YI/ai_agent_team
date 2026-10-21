import os
import re
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone

def slugify(text: str) -> str:
    """將標題轉換為安全、簡潔的目錄/檔名標識符"""
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', text)[:32] or "video_job"

@dataclass
class ProjectWorkspace:
    """
    多專案工作區路徑封裝 (Project Workspace Value Object)
    
    每個專案為獨立自成一體之工作單元 (Self-Contained Unit)：
    storage/projects/[{channel}/]{project_key}/
        ├── 01_script/      # 分鏡劇本、Prompt 與結構化數據 (storyboard.json)
        ├── 02_footage/     # 分鏡專屬動態毛片素材 (scene_01_footage.mp4 等)
        ├── 03_audio/       # 配音音軌 (voice_master.wav) 與音頻時間軸
        ├── 04_assets/      # 專案專屬圖標、浮水印、專用貼紙 (watermark.png, cover_art.png)
        ├── 05_output/      # 最終成片 (master.mp4)、封面縮圖 (cover.jpg) 與字幕 (master.srt)
        └── .temp/          # 專案獨立渲染工作暫存 (完成後自動清空)
    """
    project_id: str
    title: str
    base_storage_path: str = "/app/storage"
    channel: Optional[str] = None

    @property
    def project_key(self) -> str:
        """專案目錄標準命名規則: proj_{YYYYMMDD}_{slug}_{short_id}"""
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        slug = slugify(self.title)
        short_id = self.project_id[:8] if len(self.project_id) >= 8 else self.project_id
        return f"proj_{date_str}_{slug}_{short_id}"

    @property
    def project_root(self) -> str:
        if self.channel:
            channel_slug = slugify(self.channel)
            return os.path.join(self.base_storage_path, "projects", channel_slug, self.project_key)
        return os.path.join(self.base_storage_path, "projects", self.project_key)

    @property
    def script_dir(self) -> str:
        return os.path.join(self.project_root, "01_script")

    @property
    def footage_dir(self) -> str:
        return os.path.join(self.project_root, "02_footage")

    @property
    def audio_dir(self) -> str:
        return os.path.join(self.project_root, "03_audio")

    @property
    def assets_dir(self) -> str:
        return os.path.join(self.project_root, "04_assets")

    @property
    def output_dir(self) -> str:
        return os.path.join(self.project_root, "05_output")

    @property
    def temp_dir(self) -> str:
        return os.path.join(self.project_root, ".temp")

    @property
    def preview_url(self) -> str:
        """多專案標準成片預覽 URL (相對於 API 靜態掛載 /projects)"""
        if self.channel:
            return f"/projects/{slugify(self.channel)}/{self.project_key}/05_output/master.mp4"
        return f"/projects/{self.project_key}/05_output/master.mp4"

    @property
    def thumbnail_url(self) -> str:
        """多專案標準封面預覽 URL"""
        if self.channel:
            return f"/projects/{slugify(self.channel)}/{self.project_key}/05_output/cover.jpg"
        return f"/projects/{self.project_key}/05_output/cover.jpg"

    # 全域共享公共資產庫 (Shared Assets Hub)
    @property
    def shared_dir(self) -> str:
        return os.path.join(self.base_storage_path, "shared")

    @property
    def shared_fonts_dir(self) -> str:
        return os.path.join(self.shared_dir, "fonts")

    @property
    def shared_bgm_dir(self) -> str:
        return os.path.join(self.shared_dir, "bgm")

    @property
    def shared_footage_cache_dir(self) -> str:
        return os.path.join(self.shared_dir, "footage_cache")

    @property
    def shared_default_footage_dir(self) -> str:
        return os.path.join(self.shared_dir, "default_footage")

    @property
    def shared_sound_effects_dir(self) -> str:
        return os.path.join(self.shared_dir, "sound_effects")

    # 標準化檔案路徑
    @property
    def storyboard_json_path(self) -> str:
        return os.path.join(self.script_dir, "storyboard.json")

    @property
    def voice_audio_path(self) -> str:
        return os.path.join(self.audio_dir, "voice_master.wav")

    @property
    def master_video_path(self) -> str:
        return os.path.join(self.output_dir, "master.mp4")

    @property
    def thumbnail_path(self) -> str:
        return os.path.join(self.output_dir, "cover.jpg")

    @property
    def srt_path(self) -> str:
        return os.path.join(self.output_dir, "master.srt")

    def scene_footage_path(self, scene_index: int) -> str:
        """分鏡毛片標準命名: scene_{idx:02d}_footage.mp4"""
        return os.path.join(self.footage_dir, f"scene_{scene_index:02d}_footage.mp4")

    def scene_audio_path(self, scene_index: int) -> str:
        """分鏡獨立音軌標準命名: scene_{idx:02d}_audio.wav"""
        return os.path.join(self.audio_dir, f"scene_{scene_index:02d}_audio.wav")

    def ensure_directories(self) -> None:
        """初始化建立完整專案目錄骨架"""
        for d in [self.script_dir, self.footage_dir, self.audio_dir, self.assets_dir, self.output_dir, self.temp_dir]:
            os.makedirs(d, exist_ok=True)
