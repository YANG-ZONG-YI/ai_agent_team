# 原子實施計畫 (Work Breakdown Structure & Implementation Plan)
## 專案模組：tech-debt-refactor (自動化影音管線重構)

---

### 1. 任務概要與執行原則
- **執行原則**：
  - 嚴格遵守 TDD 循環與 QA/PG 職責物理分離。
  - 所有建置、測試與程式執行強制於 Docker 容器中進行。
  - 先建立防回歸之黃金驗收測試（Golden Master Tests），再進行代碼重構。
  - 每個 Task 均具備原子性、獨立可測試與明確驗收點。

---

### 2. 原子任務拆解清單 (WBS Tasks)

#### Phase 1: 防回歸黃金測試與基礎設施隔離 (QA & Infrastructure)
- [x] **TASK-01: 建立黃金驗收測試套件 (Golden Master Tests)**
  - **預期產出/修改檔案**：`tests/domain/test_golden_pipeline.py`, `tests/api/test_golden_api.py`
  - **驗證手法**：在 Docker 內執行 `pytest tests/domain/test_golden_pipeline.py`，固化現有輸入輸出與邊界行為。
  - **責任角色**：QA

- [x] **TASK-02: 建立 Domain Repository 介面與 ORM Data Mapper**
  - **預期產出/修改檔案**：
    - `src/domain/repositories.py` (IJobRepository)
    - `src/infrastructure/database/job_repository.py` (SqlAlchemyJobRepository & JobMapper)
  - **驗證手法**：編寫單元測試 `tests/infrastructure/test_job_repository.py` 驗證聚合根與 ORM 模型之雙向映射與狀態持久化。
  - **責任角色**：QA (測試先行) -> PG (實作轉綠)

#### Phase 2: Application Service 抽取與 API 控制器重構 (Decoupling)
- [x] **TASK-03: 實作 CreateVideoJobUseCase 與 SyncPreviewUseCase**
  - **預期產出/修改檔案**：
    - `src/application/use_cases/create_video_job.py`
    - `src/application/use_cases/sync_preview.py`
  - **驗證手法**：編寫單元測試 `tests/application/test_create_video_job.py`，注入 Mock Repository 驗證聚合根工廠與異常處理。
  - **責任角色**：QA -> PG

- [x] **TASK-04: 重構 FastAPI 控制器 (main.py) 依賴倒置化**
  - **預期產出/修改檔案**：`src/main.py`
  - **驗證手法**：執行 API 整合測試 `pytest tests/api/`，驗證 Webhook 與 Poll 路由透過 UseCase 運作正常，移除在路由中直接操作 SessionLocal 的壞味道。
  - **責任角色**：PG

#### Phase 3: 管線拆解為 Step Engine 與中繼檢查點 (Checkpoint Pipeline)
- [x] **TASK-05: 實作管線步驟引擎與檢查點機制 (Pipeline Step Runner)**
  - **預期產出/修改檔案**：
    - `src/infrastructure/pipeline/context.py`
    - `src/infrastructure/pipeline/steps.py` (ScriptStep, AudioStep, VisualStep, RenderStep)
    - `src/infrastructure/pipeline/runner.py`
  - **驗證手法**：編寫單元測試 `tests/infrastructure/test_pipeline_runner.py`，模擬第 4 步失敗後重新執行，驗證能正確自 Checkpoint 恢復而不重複執行 Step 1~2。
  - **責任角色**：QA -> PG

- [x] **TASK-06: Celery Worker 接入模組化管線與絞殺者開關**
  - **預期產出/修改檔案**：`src/infrastructure/queue/tasks.py`
  - **驗證手法**：切換 `FEATURE_MODULAR_PIPELINE=true` 與 `false`，驗證兩條路徑均可順利執行並通過黃金測試。
  - **責任角色**：PG

#### Phase 4: 多平台發布冪等性與可觀測性強化 (Matrix & Observability)
- [x] **TASK-07: 重構 PublishMatrixUseCase 支援單平台冪等分發**
  - **預期產出/修改檔案**：
    - `src/application/use_cases/publish_matrix.py`
    - `src/infrastructure/queue/tasks.py` (run_matrix_publish_sync)
  - **驗證手法**：單元測試驗證單一平台失敗時，重試不影響已發布之平台，且帶有 idempotency 防護。
  - **責任角色**：QA -> PG

- [x] **TASK-08: 結構化 JSON 日誌與 TraceId 全鏈路串接**
  - **預期產出/修改檔案**：
    - `src/infrastructure/observability/logging.py`
    - `src/main.py`、`src/infrastructure/queue/tasks.py`
  - **驗證手法**：發送 Webhook 請求，驗證 Celery 日誌與 API 日誌均攜帶相同 `trace_id`。
  - **責任角色**：PG

#### Phase 5: 資深審查、回滾手冊與驗收交付 (Review & Ops)
- [x] **TASK-09: Code-Reviewer 六大維度唯讀審查簽核**
  - **預期產出/修改檔案**：`docs/05-reviews/tech-debt-refactor/review-20261021-refactor.md`
  - **驗證手法**：唯讀比對 6 大維度（DDD 純粹性、Docker 隔離、測試真實度、代碼品質壞味道、OWASP 安全、維運可觀測性），出具簽核報告。
  - **責任角色**：Code-Reviewer

- [x] **TASK-10: 維運 5 分鐘回滾手冊與發布簽核**
  - **預期產出/修改檔案**：`docs/06-ops/tech-debt-refactor/OPS-rollback-runbook.md`
  - **驗證手法**：驗證雙探針健康檢查 `/healthz`、容器建置與環境變數回退腳本。
  - **責任角色**：Ops
