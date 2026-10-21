import os
from dataclasses import dataclass
from typing import Optional
from PIL import Image, ImageDraw

@dataclass
class CharacterProfile:
    """角色形象資產規格 (保持 100% 確定性錨點，杜絕 AI 變臉)"""
    character_id: str
    name: str
    portrait_path: str
    description: str = "專業科技主播"

class AvatarEngine:
    """零失真人物立繪與口型動畫驅動引擎"""

    def __init__(self, base_storage_path: Optional[str] = None):
        if not base_storage_path:
            base_storage_path = os.getenv("VIDEO_STORAGE_PATH", "/app/storage")
        self.base_storage_path = base_storage_path
        self.characters_root = os.path.join(self.base_storage_path, "shared", "characters")
        os.makedirs(self.characters_root, exist_ok=True)

    def _ensure_default_portrait(self, char_dir: str, portrait_path: str):
        """若無立繪，自動生成高清專業角色立繪底圖 (固定外貌特徵)"""
        if os.path.exists(portrait_path):
            return

        os.makedirs(char_dir, exist_ok=True)
        # 生成 720x1080 帶透明通道之科技風格主播立繪底圖
        img = Image.new("RGBA", (720, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 軀幹/西裝 (深海軍藍)
        draw.polygon([(180, 1080), (540, 1080), (480, 650), (240, 650)], fill=(28, 38, 62, 255))
        # 襯衫領口
        draw.polygon([(320, 650), (400, 650), (360, 750)], fill=(245, 245, 250, 255))
        # 領帶 (科技青藍)
        draw.polygon([(350, 700), (370, 700), (365, 950), (355, 950)], fill=(0, 180, 216, 255))

        # 脖子
        draw.rectangle([330, 560, 390, 650], fill=(255, 218, 185, 255))
        # 臉部外觀 (固定鵝蛋臉型)
        draw.ellipse([270, 320, 450, 580], fill=(255, 224, 189, 255))
        # 頭髮 (深棕黑)
        draw.ellipse([260, 280, 460, 440], fill=(35, 30, 30, 255))

        # 雙眼 (確定性瞳孔，不變量)
        draw.ellipse([310, 430, 335, 455], fill=(30, 30, 30, 255))
        draw.ellipse([385, 430, 410, 455], fill=(30, 30, 30, 255))
        draw.ellipse([325, 435, 332, 442], fill=(255, 255, 255, 255))
        draw.ellipse([400, 435, 407, 442], fill=(255, 255, 255, 255))

        # 嘴唇基底
        draw.ellipse([340, 515, 380, 530], fill=(215, 90, 90, 255))

        img.save(portrait_path, "PNG")

    def get_character_profile(self, character_id: str = "default_anchor") -> CharacterProfile:
        """獲取指定角色的錨點立繪規格"""
        char_dir = os.path.join(self.characters_root, character_id)
        portrait_path = os.path.join(char_dir, "portrait.png")
        self._ensure_default_portrait(char_dir, portrait_path)

        return CharacterProfile(
            character_id=character_id,
            name="AI 首席播報員" if character_id == "default_anchor" else character_id,
            portrait_path=portrait_path
        )

    def render_avatar_clip(
        self,
        character_id: str,
        duration: float,
        output_path: str,
        fps: int = 24
    ) -> str:
        """
        基於固定立繪生成口型動畫切片 (音頻/時長驅動，維持 100% 臉部五官不變量)
        """
        import numpy as np
        from moviepy import VideoClip

        profile = self.get_character_profile(character_id)
        base_img = Image.open(profile.portrait_path).convert("RGBA")
        base_w, base_h = base_img.size

        # 嘴唇張合狀態 (使用固定底圖局部驅動嘴部開合，不變異面部五官)
        lip_open_img = base_img.copy()
        draw_open = ImageDraw.Draw(lip_open_img)
        # 嘴巴自然微張 (保持嘴型邊緣自然)
        draw_open.ellipse([335, 510, 385, 535], fill=(160, 40, 40, 255))
        draw_open.ellipse([345, 518, 375, 528], fill=(60, 10, 10, 255))

        base_np = np.array(base_img.convert("RGB"))
        open_np = np.array(lip_open_img.convert("RGB"))

        def make_frame(t):
            # 依據時間 t 產生自然口型開合節奏 (每秒 3~4 次微調張合)
            cycle = (t * 4.0) % 1.0
            if cycle > 0.4:
                return open_np
            return base_np

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        clip = VideoClip(make_frame, duration=duration)
        clip.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            preset="ultrafast",
            logger=None
        )
        clip.close()
        return output_path
