# 需求規格書 (Requirement Specification)
## 專案模組：tech-debt-refactor (自動化影音管線技術債根治與架構重構)

---

### 1. 需求背景與目標 (Background & Vision)
- **現況挑戰**：專案自原型階段起快速迭代，雖然具備完整的影音生成流程（FastAPI、Celery、MoviePy、Notion 與多平台分發），但在核心實作上產生嚴重架構腐化：
  1. 領域聚合根 `VideoPipelineJob` 與領域狀態檢查在 `main.py` 與 `tasks.py` 中被直接架空，直接以 SQLAlchemy ORM 進行字段讀寫，使領域層淪為貧血模型。
  2. `tasks.py` 中的 `run_video_pipeline_sync` 是典型的上帝函式（God Function），長達 150+ 行且無 Checkpointing（檢查點中繼斷點續做），中間步驟若中斷則全盤重來，造成算力與 Token 浪費。
  3. 控制器層（FastAPI）直接依賴資料庫連線與 Celery 任務，缺乏 Application Service（Use Cases）與依賴倒置（DIP）。
  4. 同步 Celery 執行緒內混用 `asyncio.run`，潛藏 Event Loop 衝突與連線洩漏風險。
  5. 缺乏完整結構化日誌（TraceId 串接）與可觀測性指標。
- **重構願景**：
  在**不破壞現有對外 API 契約、資料庫結構與產物規格**的前提下，透過絞殺者模式（Strangler Fig Pattern）將系統升級為標準 DDD 乾淨架構，引入黃金測試（Golden Master Tests）、管線中繼斷點快取、依賴倒置防腐層與端到端 TraceId 可觀測性。

---

### 2. 三態需求特徵與重構策略 (Categorization & Refactoring Strategy)
- **需求分類**：【技術債 / 架構重構】（Technical Debt & Architectural Refactoring）
- **核心方針**：
  1. **黃金驗收測試守護（Golden Master Tests First）**：在動工重構前先建立全鏈路測試防護網。
  2. **絞殺者遷移模式（Strangler Fig）**：建立 `src/application/`、`src/domain/repositories/` 與 `src/infrastructure/pipeline/`，逐步替換上帝函式，保留開關平滑切換。
  3. **依賴倒置與介面隔離（DIP & ISP）**：所有外部服務（AI、TTS、Render、Notion、Social）抽象為 Protocol/Interface，業務代碼面向介面編程。
  4. **零破壞性與一鍵回滾**：透過環境變數 `FEATURE_MODULAR_PIPELINE=true/false` 支援秒級回滾至原管線。

---

### 3. 功能性需求與重構範圍 (Functional Scope)

#### 3.1 In-Scope (納入本次重構範圍)
1. **領域層純粹化與聚合根保護**：
   - 定義 `IJobRepository` 介面，阻絕領域層直接依賴 ORM。
   - 所有狀態流轉（PENDING -> SCRIPTING -> RENDERING -> COMPLETED/FAILED）強制透過 `VideoPipelineJob` 領域方法執行。
2. **應用服務層 (Application Layer / Use Cases) 建立**：
   - `CreateVideoJobUseCase`：處理 Notion Webhook/Poll 進入點、重複檢驗、聚合根建立與任務派發。
   - `ExecutePipelineUseCase`：協調整合分步驟的 Pipeline Runner。
   - `PublishMatrixUseCase`：協調各平台矩陣分發，具備獨立狀態更新與冪等防護。
3. **管線分步化與中繼檢查點 (Checkpoint Pipeline Engine)**：
   - 將 150 行上帝函式拆解為獨立 Pipeline Step（ScriptStep, EmbeddingStep, AudioStep, FootageAvatarStep, RenderStep）。
   - 每個步驟產物落盤檢查點（Checkpointing），失敗重試時自動從最新檢查點接續，避免重複生成劇本與語音。
4. **移除同步執行緒中的 `asyncio.run` 危險模式**：
   - 素材提供者與立繪服務重構為符合 Worker 運行模式之安全呼叫防護。
5. **端到端可觀測性強化**：
   - 引入全局 `trace_id` 貫穿 HTTP API -> Celery -> Pipeline 各步驟。

#### 3.2 Out-of-Scope (排除範圍)
1. 不更動對外 HTTP API 路由路徑與請求/回應 JSON Schema（保證 Notion Webhook 相容性）。
2. 不更動資料庫實體表名稱與欄位定義（保證現有 PostgreSQL 資料零遷移風險）。
3. 不更換底層影片合成工具（維持 MoviePy 與現有解析度/幀率設定）。

---

### 4. 非功能性需求 (NFRs)
- **相容性與正確性**：重構後產出的影片格式、縮圖、分鏡 JSON、Notion 回填內容與舊版本 100% 一致。
- **容錯與重試效能**：在渲染步驟失敗並觸發 Celery 重試時，因檢查點機制，重試耗時縮短 60% 以上（免去重複文字生成與 TTS 生成時間）。
- **可測試性**：各 Step 與 UseCase 均具備純粹 Mock 測試能力，單元測試執行速度提升。
- **可觀測性**：所有日誌格式為標準 JSON，帶有 `trace_id`、`job_id`、`step_name`、`duration_ms`。

---

### 5. 驗收標準 (Acceptance Criteria - Gherkin)

```gherkin
Feature: 自動化影音管線技術債重構防護

  Scenario: 領域狀態檢查硬性防護
    Given 一個新建立的 VideoPipelineJob 聚合根處於 PENDING 狀態
    When 嘗試在未編寫劇本的情況下直接調用 start_rendering()
    Then 系統必須拋出 DomainStateError 異常，禁止非法狀態躍遷

  Scenario: 管線檢查點斷點續做機制
    Given 一個作業已完成 ScriptStep 與 AudioStep 並儲存檢查點
    When 該任務在 RenderStep 遭遇異常並重新觸發執行
    Then 系統應識別現有檢查點，直接跳過劇本與語音生成，自素材與渲染步驟接續

  Scenario: API 介面零破壞相容性驗證
    Given 外部發送符合 NotionWebhookPayload 規格之請求
    When 經由重構後的 CreateVideoJobUseCase 處理
    Then 回傳狀態必須為 200 QUEUED 且返回合規之 job_id 與 title
```
