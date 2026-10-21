from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Scene:
    """單一分鏡規格"""
    scene_index: int
    narration: str
    visual_prompt: str
    duration_seconds: float = 4.0

@dataclass
class GeneratedScript:
    """完整短影音劇本結構"""
    topic: str
    scenes: List[Scene] = field(default_factory=list)

    @property
    def full_narration(self) -> str:
        """合併所有分鏡之完整旁白文本"""
        return " ".join(scene.narration for scene in self.scenes)

    @property
    def total_estimated_duration(self) -> float:
        """總預估秒數"""
        return sum(scene.duration_seconds for scene in self.scenes)

class ScriptGenerator:
    """LLM 短影音分鏡腳本生成器 (具備 Mock 與 LLM API 介接擴充能力)"""

    def generate_script(self, topic: str, prompt: str, target_duration: Optional[int] = None) -> GeneratedScript:
        """
        根據主題與提示詞生成結構化分鏡腳本
        若指定 target_duration (秒數)，將依據黃金架構動態反向推導分鏡數量與時長分配
        遵循短影音「黃金 3 秒開場 (Hook) ➔ 核心痛點/知識點 (Value) ➔ 行動呼籲 (CTA)」三段式爆款架構
        """
        if target_duration is None:
            # 向前相容預設 3 鏡分鏡 (約 11 秒)
            scenes = [
                Scene(
                    scene_index=1,
                    narration=f"你知道嗎？關於{topic}，很多人都踩過這個致命誤區！",
                    visual_prompt=f"震撼開場畫面，醒目的紅色警告文字，主題聚焦在：{topic}",
                    duration_seconds=3.5
                ),
                Scene(
                    scene_index=2,
                    narration=f"其實核心關鍵只有一個，就是掌握核心方法並結合自動化工具，效率直接翻倍！",
                    visual_prompt="現代科技工作流動畫，數據圖表高速攀升",
                    duration_seconds=4.5
                ),
                Scene(
                    scene_index=3,
                    narration=f"追蹤我們，帶你解鎖更多{topic}的實戰技巧，我們下期見！",
                    visual_prompt="清晰的點贊關注動畫，品牌 Logo 浮現",
                    duration_seconds=3.0
                )
            ]
            return GeneratedScript(topic=topic, scenes=scenes)

        # 動態分鏡推導演算法
        hook_duration = 3.5
        cta_duration = 3.5
        remaining_duration = max(5.0, float(target_duration) - hook_duration - cta_duration)
        
        # 核心內容每鏡約 4.0~5.0 秒
        body_count = max(1, round(remaining_duration / 4.5))
        body_step_duration = round(remaining_duration / body_count, 1)

        scenes: List[Scene] = []
        idx = 1
        # 1. Hook 開場
        scenes.append(
            Scene(
                scene_index=idx,
                narration=f"你知道嗎？關於{topic}，很多人都踩過這個致命誤區！",
                visual_prompt=f"震撼開場畫面，醒目的科技粒子動畫與動態標題：{topic}",
                duration_seconds=hook_duration
            )
        )
        idx += 1

        # 2. Body 核心內容動態生成
        topic_insights = [
            f"首先，傳統作法耗時費力，而最新 AI 驅動的{topic}工作流已顛覆以往認知。",
            f"其次，掌握數據流與模組化架構，能讓整體系統穩定度提升十倍以上。",
            f"接著，透過自動化任務管線與背景非同步處理，徹底擺脫手動重複作業。",
            f"最後，結合即時監控與高確定性驗證，確保每一次交付都零失真、高品質。",
            f"深入細節來看，底層演算法能依據具體約束自動微調，達到最佳動態平衡。",
            f"同時，多圖層混流技術為視覺效果注入豐富動態層次與生動表現力。"
        ]

        visual_insights = [
            "現代科技工作流動畫，數據圖表高速攀升與藍色能量流動",
            "清晰的流程架構動態展開圖，節點發光連線",
            "自動化流水線齒輪與代碼終端視窗動畫",
            "品質監控儀表板，成功率指標達 100% 脈衝動畫",
            "神經網路特徵權重動態分佈圖，立體幾何旋轉",
            "多圖層畫中畫疊加渲染動畫，微粒子光斑閃爍"
        ]

        for i in range(body_count):
            insight_text = topic_insights[i % len(topic_insights)]
            visual_text = visual_insights[i % len(visual_insights)]
            scenes.append(
                Scene(
                    scene_index=idx,
                    narration=insight_text,
                    visual_prompt=visual_text,
                    duration_seconds=body_step_duration
                )
            )
            idx += 1

        # 3. CTA 結尾
        scenes.append(
            Scene(
                scene_index=idx,
                narration=f"追蹤我們，帶你解鎖更多{topic}的實戰技巧，我們下期見！",
                visual_prompt="清晰的點贊關注動畫，品牌 Logo 浮現，訂閱按鈕微動態彈出",
                duration_seconds=cta_duration
            )
        )

        return GeneratedScript(topic=topic, scenes=scenes)
