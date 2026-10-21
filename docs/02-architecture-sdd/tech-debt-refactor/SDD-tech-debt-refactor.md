# 系統設計規格書 (Software Design Description - SDD)
## 專案模組：tech-debt-refactor (自動化影音管線重構)

---

### 1. 系統架構推導與 DDD 領域邊界 (Bounded Context & Layering)

重構後全面遵從 DDD 依賴倒置原則（DIP），嚴格區分為四層架構：

```
+-------------------------------------------------------------------------+
|                        Presentation Layer (FastAPI)                     |
|        - Notion Webhook & Polling Router                                |
|        - DTOs / Request & Response Schemas                              |
+-------------------------------------------------------------------------+
                                    | (調用)
                                    v
+-------------------------------------------------------------------------+
|                         Application Layer (Use Cases)                   |
|        - CreateVideoJobUseCase                                          |
|        - ExecutePipelineUseCase                                         |
|        - PublishMatrixUseCase                                           |
+-------------------------------------------------------------------------+
                     | (依賴抽象)                     | (呼叫領域)
                     v                                v
+---------------------------------------+  +------------------------------+
|     Domain Ports (Protocols / Interfaces) |  |   Domain Model (Pure Python) |
|     - IJobRepository                  |  |   - VideoPipelineJob (Agg)   |
|     - IPublishTaskRepository          |  |   - PublishTask (Agg)        |
|     - IScriptService                  |  |   - JobStatus (Enum)         |
|     - ITTSService                     |  |   - DomainStateError         |
|     - IFootageService                 |  |   - Value Objects & Events   |
|     - IVideoRenderService             |  +------------------------------+
+---------------------------------------+
                     ^
                     | (依賴倒置實作 DIP)
+-------------------------------------------------------------------------+
|                      Infrastructure Layer (Adapters)                    |
|        - SqlAlchemyJobRepository (ORM <-> Domain Entity Mapper)         |
|        - PipelineRunner & Step Checkpointing Engine                     |
|        - AI Service Adapters (ScriptGenerator, TTSService, AvatarEngine)|
|        - NotionAdapter, SocialPublisherFactory                          |
+-------------------------------------------------------------------------+
```

---

### 2. 核心介面與契約設計 (Domain Ports & Contracts)

#### 2.1 Repository 抽象介面 (`src/domain/repositories.py`)
```python
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from src.domain.video_job import VideoPipelineJob

class IJobRepository(ABC):
    @abstractmethod
    def get_by_id(self, job_id: UUID) -> Optional[VideoPipelineJob]:
        """依 UUID 取得領域聚合根"""
        pass

    @abstractmethod
    def get_by_notion_page_id(self, page_id: str) -> Optional[VideoPipelineJob]:
        """依 Notion Page ID 查詢聚合根"""
        pass

    @abstractmethod
    def save(self, job: VideoPipelineJob) -> VideoPipelineJob:
        """保存或更新聚合根狀態 (底層負責 ORM 映射)"""
        pass
```

#### 2.2 檢查點管線引擎架構 (`src/infrastructure/pipeline/`)
每個管線步驟封裝為獨立的 `PipelineStep`，並由 `PipelineContext` 傳遞上下文與產物路徑：
- `ScriptStep`：負責劇本生成、分鏡校準與保存 `storyboard.json`（Checkpoint: Storyboard 完成）。
- `EmbeddingStep`：負責向量特徵儲存與去重檢驗。
- `AudioStep`：負責 TTS 語音合成與字幕時間軸產出（Checkpoint: Audio 完成）。
- `VisualStep`：安全封裝素材下載與立繪口型生成。
- `RenderStep`：調用渲染器合成成片與生成縮圖（Checkpoint: Render 完成）。

---

### 3. 資料映射器設計 (Entity <-> ORM Data Mapper)

建立 `JobMapper`，徹底阻絕 ORM Model 污染領域實體：
```python
class JobMapper:
    @staticmethod
    def to_domain(model: VideoJobModel) -> VideoPipelineJob:
        return VideoPipelineJob(
            id=model.id,
            notion_page_id=model.notion_page_id,
            title=model.title,
            prompt=model.prompt,
            status=JobStatus(model.status),
            target_duration=model.target_duration,
            character_id=model.character_id,
            script_content=model.script_content,
            video_path=model.video_path,
            preview_url=model.preview_url,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def update_model(model: VideoJobModel, domain: VideoPipelineJob) -> None:
        model.status = domain.status.value
        model.script_content = domain.script_content
        model.video_path = domain.video_path
        model.preview_url = domain.preview_url
        model.error_message = domain.error_message
        model.updated_at = domain.updated_at
```

---

### 4. 絞殺者動態切換與安全防護架構

```python
# 透過環境變數無縫掌控
FEATURE_MODULAR_PIPELINE = os.getenv("FEATURE_MODULAR_PIPELINE", "true").lower() == "true"

def run_video_pipeline_sync(job_id_str: str) -> dict:
    if FEATURE_MODULAR_PIPELINE:
        use_case = ExecutePipelineUseCase()
        return use_case.execute(job_id_str)
    else:
        # 既有 Legacy 函式保留，作為 5 分鐘瞬時回滾備案
        return _legacy_run_video_pipeline_sync(job_id_str)
```

---

### 5. 可觀測性架構 (Observability Specification)
- **結構化 JSON 日誌**：使用標準結構包含 `timestamp`、`level`、`trace_id`、`job_id`、`step`、`message`、`elapsed_ms`。
- **雙探針健康檢查**：
  - `/health/liveness`：保證程序存活。
  - `/health/readiness`：保證 DB 連線、Redis 佇列與 Storage 掛載可寫入。
