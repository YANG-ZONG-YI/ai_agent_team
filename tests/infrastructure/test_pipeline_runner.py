import pytest
import os
import json
from unittest.mock import MagicMock
from uuid import uuid4
from src.domain.video_job import VideoPipelineJob, JobStatus
from src.infrastructure.pipeline.context import PipelineContext
from src.infrastructure.pipeline.steps import ScriptStep, AudioStep
from src.infrastructure.pipeline.runner import ModularPipelineRunner

class TestModularPipelineRunnerAndCheckpoint:
    """QA 測試：驗證管線步驟化執行與中繼檢查點 (Checkpointing) 斷點續做機制"""

    @pytest.fixture
    def test_job(self, tmp_path):
        job = VideoPipelineJob.create(
            notion_page_id="checkpoint_page_01",
            title="Checkpoint Test Video",
            prompt="Test Prompt",
            target_duration=30
        )
        return job

    def test_checkpoint_skip_when_artifact_already_exists(self, tmp_path, test_job):
        """測試當檢查點產物 (如 storyboard.json) 已存在時，自動跳過該步驟，避免重複調用 AI"""
        context = PipelineContext(job=test_job, base_storage_path=str(tmp_path))
        context.workspace.ensure_directories()

        # 預先寫入已完成的 storyboard 檔案 (模擬先前已完成步驟)
        pre_existing_data = {
            "title": test_job.title,
            "full_narration": "Pre-existing cached narration",
            "scenes": [{"scene_index": 1, "narration": "Pre-existing cached narration", "duration_seconds": 15}]
        }
        with open(context.workspace.storyboard_json_path, "w", encoding="utf-8") as f:
            json.dump(pre_existing_data, f)

        mock_script_gen = MagicMock()
        script_step = ScriptStep(script_generator=mock_script_gen)

        # 執行 ScriptStep
        script_step.execute(context)

        # 驗證：因為存在檢查點檔案，Mock ScriptGenerator 絕對不應被重複調用！
        mock_script_gen.generate_script.assert_not_called()
        assert context.job.script_content == "Pre-existing cached narration"
        assert context.job.status == JobStatus.SCRIPTING

    def test_script_step_executes_and_saves_checkpoint_when_absent(self, tmp_path, test_job):
        """測試當無檢查點時，正常調用生成並建立 checkpoint 檔案"""
        context = PipelineContext(job=test_job, base_storage_path=str(tmp_path))
        context.workspace.ensure_directories()

        mock_script_gen = MagicMock()
        mock_scene = MagicMock()
        mock_scene.scene_index = 1
        mock_scene.narration = "Generated narration"
        mock_scene.visual_prompt = "city view"
        mock_scene.duration_seconds = 15

        mock_script = MagicMock()
        mock_script.full_narration = "Generated narration"
        mock_script.scenes = [mock_scene]
        mock_script_gen.generate_script.return_value = mock_script

        script_step = ScriptStep(script_generator=mock_script_gen)
        script_step.execute(context)

        mock_script_gen.generate_script.assert_called_once()
        assert os.path.exists(context.workspace.storyboard_json_path)
        assert context.job.script_content == "Generated narration"
