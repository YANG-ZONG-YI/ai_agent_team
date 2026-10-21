import os
from src.domain.workspace import ProjectWorkspace, slugify

def test_slugify_text():
    assert slugify("AI 時代工程師必備技能") == "ai_時代工程師必備技能"
    assert slugify("Hello World! 2026") == "hello_world_2026"

def test_project_workspace_paths(tmp_path):
    ws = ProjectWorkspace(
        project_id="a1b2c3d4-e5f6-7890-abcd-1234567890ef",
        title="AI 自動化影音",
        base_storage_path=str(tmp_path)
    )
    
    # 驗證專案目錄命名規範包含日期與短 ID
    assert ws.project_key.startswith("proj_")
    assert "a1b2c3d4" in ws.project_key
    
    # 驗證五大子目錄結構
    assert ws.script_dir.endswith("01_script")
    assert ws.footage_dir.endswith("02_footage")
    assert ws.audio_dir.endswith("03_audio")
    assert ws.assets_dir.endswith("04_assets")
    assert ws.output_dir.endswith("05_output")
    assert ws.temp_dir.endswith(".temp")
    
    # 驗證分鏡毛片標準命名
    assert ws.scene_footage_path(1).endswith("scene_01_footage.mp4")
    assert ws.scene_footage_path(10).endswith("scene_10_footage.mp4")
    
    # 建立目錄實體驗證
    ws.ensure_directories()
    assert os.path.exists(ws.script_dir)
    assert os.path.exists(ws.footage_dir)
    assert os.path.exists(ws.output_dir)

def test_project_workspace_with_channel(tmp_path):
    ws = ProjectWorkspace(
        project_id="b2c3d4e5-f6a7-8901-bcde-2345678901fa",
        title="科技快訊 2026",
        channel="Tech News Weekly",
        base_storage_path=str(tmp_path)
    )
    # 驗證多專案依頻道/系列隔離
    assert "tech_news_weekly" in ws.project_root
    assert ws.project_root.endswith(ws.project_key)
    assert ws.scene_audio_path(2).endswith("scene_02_audio.wav")
    assert ws.shared_dir.endswith("shared")

