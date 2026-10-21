---
trigger: always_on
description: 專案核心架構約束（討論未完禁寫文檔、無計畫禁寫代碼、AI主動三態辨識、DDD純粹、QA/PG分離、Docker物理終止、唯審查權門禁、Subagent自主派工、維運回滾）
---

# 專案架構核心不可變量與工程規範 (Architecture Invariants)

本規範為本專案不可妥協之核心架構約束，在對話與代碼生成過程中常駐生效（always_on）：

## 1. 討論未完禁止落盤任何文檔律 (No Premature Documentation Invariant - Hard Gate)
* **嚴禁未對齊提前落盤**：在使用者與 AI 代理人尚未在對話中徹底完成意圖對齊、架構推導、範疇切刀與技術選型前，**嚴禁在磁碟中新增、覆寫或生成任何規格文件或專案代碼**（包括但不限於 `docs/` 下的所有文檔）。
* **雙階段嚴格推進**：
  1. **第一階段（對話論證）**：所有訪談、架構藍圖、資料結構草案僅在對話中呈現與深入推敲。
  2. **第二階段（用戶授權落盤）**：只有在獲得使用者明確回覆同意（如「確認無誤」、「可以落盤」）後，方可由對應 Subagent 執行檔案寫入。

## 2. 無核准實施計畫嚴禁編寫代碼律 (Plan-First Before Code Invariant - Hard Gate)
* **無計畫嚴禁寫碼**：未經使用者審查與核准原子實施計畫前，**嚴禁編寫任何業務代碼與測試代碼**。
* **原子計畫標準規格**：實施計畫必須由系統架構師（`sa`）產出於 `docs/03-tasks/<module-name>/`，包含明確的 WBS 原子分解、Checkbox `[ ]`、預期修改檔案清單與測試驗證手法。
* **用戶審批放行**：只有在使用者審查並回覆「批准計畫」後，方可建立 Feature 分支，交由 `qa` 與 `pg` 啟動 TDD 循環。

## 3. AI 主動三態需求辨識律 (AI Auto-Classification & Precision Intake)
* **主動特徵研判**：AI（`pm`）在收到使用者輸入時，必須主動探勘語意與代碼庫，自動判定為【新專案/新模組 MVP】、【線上問題/Bug 故障】或【技術債/架構重構】，並回報判定理由與信心度，嚴禁由使用者盲目猜測。
* **MVP 極致技術棧盤點**：若屬 MVP，強制問清前端/後端框架與版本、DB/Cache 引擎、Docker 基礎鏡像、QPS 與 NFRs，並劃定 In-Scope vs Out-of-Scope 切刀。
* **混雜需求阻絕**：若偵測到同時包含 Bug 與新功能，強制要求切刀拆分，禁止混雜推進。

## 4. Subagent 物理工具隔離與自主調度律 (Autonomous Subagent & Scoped Tools Isolation)
* **自主調度總指揮 (Parent Orchestrator)**：主 Agent 擔任生命週期狀態機調度中心，根據 SDLC 各階段主動派遣宣告 `subagent: true` 的專用 Subagent 獨立作戰，完成後自主交接下一棒，徹底減輕主 Agent 上下文負擔。
* **工具物理隔離 (Scoped Tools)**：各 Subagent 必須於 Frontmatter 嚴格限制 `tools` 清單：
  - `pm`：僅具備訪談與需求規格編寫工具（`ask_question`, `view_file`, `write_to_file`）。
  - `sa`：僅具備架構推導與設計清單工具（`view_file`, `write_to_file`）。
  - `qa`：僅限測試代碼與 Docker 測試執行（`view_file`, `write_to_file`, `run_command`），**物理禁止修改業務代碼**。
  - `pg`：業務代碼與 Docker 構建（`view_file`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`, `run_command`），**物理禁止修改測試代碼**。
  - `code-reviewer`：**唯審查權**，僅配置唯讀與報告輸出工具（`view_file`, `grep_search`, `write_to_file`），**物理級沒收代碼修改工具**。
  - `ops`：容器映像檔安全、雙探針與維運手冊工具（`view_file`, `write_to_file`, `run_command`）。

## 5. DDD 分層依賴倒置原則 (Dependency Inversion)
* **Domain Layer 保持純粹**：領域層（Entities、Value Objects、Domain Events）嚴禁依賴任何基礎設施（ORM 註解、資料庫驅動、HTTP Client 或外部框架）。
* **介面定義於內部，實作於外部**：Repository、Notification 等外部介面必須定義在 Domain 或 Application 層，其實作（Implementation）統一置於 Infrastructure 層。

## 6. QA 與 PG 職責物理分離律 (Separation of Testing & Implementation)
* **嚴禁球員兼裁判**：測試代碼與業務實作代碼嚴格由兩個獨立角色分工：
  - **`qa` (測試工程師)**：專職根據 SDD 規格編寫 BDD 驗收測試與極端邊界測試，並確認在無實作時 **100% 變紅（Red Phase）**。QA 嚴禁編寫業務實作。
  - **`pg` (研發工程師)**：專職根據原子任務在 Docker 容器內編寫業務代碼，驅使測試轉綠（Green Phase），並執行依賴倒置重構（Refactor）。
* **無紅燈不寫碼**：未由 QA 確認紅燈測試前，PG 絕對不得開始寫實作代碼。

## 7. 強制 Docker 隔離開發環境律 (Docker-Only Isolation & Hard Stop)
* **宿主環境零污染**：專案之一切套件安裝（npm, pip, go mod, cargo 等）、編譯（build）、測試（test）、執行（run）**一律強制在 Docker 容器內執行**（如 `docker compose exec ...` 或在容器內部隔離運行）。
* **非 Docker 環境物理終止（Hard Stop）**：嚴禁直接在主機宿主系統（Windows / PowerShell / Bash）調用編譯器或運行測試。若目前非處於 Docker 環境或 Docker 容器尚未啟動，**必須立即中止操作（STOP）並提示用戶**。
* **環境準備先行**：所有功能開發任務首要確認 Dockerfile / compose 運行無虞，方可執行後續流程。

## 8. 領域不變量與防腐邊界 (Invariants & Anti-Corruption)
* **聚合根是唯一變更入口**：外部禁止直接更新聚合內部的子實體，必須透過聚合根提供的領域方法操作以確保狀態一致性。
* **外部介接必須設立防腐層 (ACL)**：對接任何第三方服務或舊系統時，必須建立 Adapter / DTO 轉換器，嚴禁讓外部資料模型穿透進內部領域層。

## 9. 高階代碼審查工程師唯審查權門禁 (Senior Review Gate)
* **唯審查權，零修改權（Strict Review-Only）**：`code-reviewer` 具備一票否決權與門禁核准權，**絕對禁止直接新增、編輯或修改任何業務與測試代碼**。
* **六大審查維度強制合規**：DDD 純粹性、Docker 規範、測試邊界真實度、代碼品質壞味道、OWASP 安全性、維運可觀測性。
* **審查報告落盤存證**：審查意見必須落盤為 `docs/05-reviews/<module-name>/review-YYYYMMDD-<name>.md`，標註具體檔案行號與裁決（APPROVED / REQUEST_CHANGES）。

## 10. 維運可觀測性與零停機回滾律 (Ops Observability & Rollback)
* **三位一體可觀測性**：必須包含結構化 JSON 日誌（帶 TraceId）、Prometheus 指標埋點與分散式鏈路追蹤。
* **健康檢查雙探針**：必須公開 `/health/liveness` 與 `/health/readiness` 探針。
* **向前相容與一鍵回滾**：資料庫遷移禁止破壞性直接刪欄位（遵循 Expand-Contract 模式）；生產環境必須備妥 5 分鐘內一鍵容器鏡像回滾與應急 Runbook（落盤於 `docs/06-ops/<module-name>/`）。

## 11. 規格資產模組化拓撲律 (Module-Scoped Documentation Topology)
* 所有文檔與規格必須同時依照「生命週期階段」與「業務模組名稱」歸檔：
  - `docs/01-requirements/<module-name>/`
  - `docs/02-architecture-sdd/<module-name>/`
  - `docs/03-tasks/<module-name>/`
  - `docs/04-testing-qa/<module-name>/`
  - `docs/05-reviews/<module-name>/`
  - `docs/06-ops/<module-name>/`
* 嚴禁在 `docs/` 根目錄或階段目錄下無模組散落文件。
