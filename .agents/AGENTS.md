# [SCOPE: WORKSPACE_PROJECT | DDD_TDD_SDD_ARCHITECTURE]
# 專案架構最高核心憲法 (Project Architecture & Agent Governance Kernel)

本綱領為本專案在 Antigravity IDE 內運行 AI 協同開發、架構訪談與代碼生成的最高不可逾越底線。本設定完全作用於本專案（Workspace-Scoped），不依賴全域設定，確保專案獨立性與版本受控。

---

## 1. 系統不可逾越之核心架構不變量 (Architecture Invariants)

1. **[INVARIANT-1: DDD_DEPENDENCY_INVERSION] 領域層純粹與依賴倒置原則**
   - **Domain Layer 保持零污染**：領域實體（Entities）、值對象（Value Objects）、領域事件（Domain Events）絕對禁止依賴任何外部基礎設施（ORM、DB 驅動、HTTP 框架、第三方 SDK）。
   - **依賴倒置（DIP）**：儲存庫（Repository）與外部介面定義在 Domain/Application 層，其實作統一放置於 Infrastructure 層。

2. **[INVARIANT-2: SDD_SPEC_FIRST & GRILL_ME_PROTOCOL] 規格先行與 Grill-Me 深度訪談律**
   - **無規格嚴禁寫碼**：任何模組或功能開發前，必須先透過如同 `/grill-me` 般的深度需求與架構訪談，產出標準的軟體設計規格書（SDD, Software Design Document）。
   - **Grill-Me 訪談協議**：
     - **決策樹分支逐項攻克**：沿著架構決策樹逐步深挖，逐一解開決策依賴，絕不籠統跳躍或草率結案。
     - **問答互動工具優先**：凡需使用者抉擇或對齊，強制使用 `ask_question` 互動工具，並提供 `(Recommended)` 最佳實踐推薦選項。
     - **Codebase 現狀探勘先行**：若問題可透過檢查工作區代碼或現有配置解答，嚴禁重複提問，以代碼實際現狀為基準。
     - **極限邊界拷問**：深度深挖非快樂路徑（併發競態、超時熔斷、網路分區、補償回滾、安全防禦）。

3. **[INVARIANT-3: TDD_TEST_FIRST] 測試先行與紅綠重構律 (Red-Green-Refactor)**
   - 在編寫具體業務實作代碼前，強制由 `tdd-engineer` 先行編寫捕捉領域不變量與邊界條件的失敗測試（Red Phase）。
   - 確認測試能如期變紅（Red）後，方可進入最小實作使其通過（Green），最後進行架構重構（Refactor）。

4. **[INVARIANT-4: AGGREGATE_BOUNDARY_PROTECTION] 聚合根邊界與防腐層 (ACL)**
   - **聚合根是唯一變更入口**：外部禁止直接修改聚合內部的子實體，必須透過聚合根的方法以保證業務不變量（Business Invariants）。
   - **防腐層 (Anticorruption Layer)**：介接任何外部服務、舊系統或第三方 API 時，強制建立 ACL 轉接適配器，杜絕外部髒資料穿透至內部核心域。

5. **[INVARIANT-5: DOCKER_ISOLATED_ENVIRONMENT] 強制 Docker 隔離開發環境律 (Hard Requirement)**
   - **宿主環境零污染與物理隔離**：專案之套件安裝（npm, pip, go mod, cargo 等）、程式碼建置（build）、測試套件運行（test / pytest / jest）、伺服器啟動（dev server）**必須 100% 在 Docker 容器中執行**。
   - **非 Docker 環境物理終止原則（Hard Stop）**：任何 Agent 嚴禁直接在主機宿主環境（Windows / PowerShell / Host Terminal）調用編譯器、運行時或直接執行專案測試與代碼。若檢測到當前未處於 Docker 容器環境或 Docker 容器尚未啟動，**Agent 必須立即停止執行（STOP）並提示用戶**，絕不允許冒然在 Host 主機直接運行！
   - **Docker 環境就緒先行**：所有實施任務的第一步必須確保專案之 `Dockerfile` / `docker-compose.yml` 正常運作，所有指令一律透過 `docker compose exec ...` 或在容器內部隔離執行。

---

## 2. 專案專用 Subagent 協同矩陣 (Dedicated Subagents)

本專案配置三位專用 Subagent，協同關係如下：

```mermaid
graph TD
    User([用戶 / 需求方]) <-->|/grill-me 深度架構拷問與推導| Orchestrator[主控 Agent]
    Orchestrator -->|業務建模、事件風暴與統一語言| DomainAnalyst[domain-analyst<br/>領域分析師]
    Orchestrator -->|C4拓撲 / API / DDL / Docker 容器規劃| SystemArch[system-architect<br/>系統架構師]
    Orchestrator -->|Docker 內 BDD / 極端邊界紅燈測試| TDDEng[tdd-engineer<br/>測試驅動工程師]
    
    DomainAnalyst -->|領域模型資產| SystemArch
    SystemArch -->|SDD 規格與契約| TDDEng
```

* **`domain-analyst`**：專用 DDD 業務分析師。專精於業務願景探索、Grill-Me 深入探詢業務痛點、事件風暴（Event Storming）、統一語言（Ubiquitous Language）提煉與限界上下文劃分。
* **`system-architect`**：專用首席架構師。專精於 C4 拓撲架構、Docker 容器化開發環境規範、API 契約（REST/gRPC）、資料庫 ER/DDL Schema、分散式事務與 NFRs 設計。
* **`tdd-engineer`**：專用測試工程師。專精於將 SDD 規格轉化為 BDD/Gherkin 與極端邊界測試，**且所有測試必須在 Docker 容器內執行，非 Docker 環境強制停止**。

---

## 3. IDE 流程與雙 Skill 協同架構

* **Agents (Subagents)**：位於 `.agents/agents/`，包含 `domain-analyst.md`、`system-architect.md`、`tdd-engineer.md`。
* **Workflows (斜線工作流)**：位於 `.agents/workflows/`：
  - `/workflow-system-analysis-interview`：啟動顧問級需求與 DDD 架構深度訪談（遵循 Grill-Me 協議）。
  - `/workflow-spec-driven-development`：啟動規格驅動開發全生命週期（Proposal ➔ SDD ➔ Tasks ➔ Docker TDD）。
* **Skills (雙 Skill 職責分離體系)**：位於 `.agents/skills/`：
  - `system-analysis-architect`：負責需求深層訪談（Grill-Me 模式）、DDD 建模與架構決策（分析腦）。
  - `spec-driven-lifecycle`：負責規範檔案流轉、模板實例化、任務 Checkbox 勾選與斷點無縫接關（工程手），維護 Docker 環境守則。
* **Rules**：位於 `.agents/rules/`，於對話中自動常駐載入（`always_on`）。
* **Hooks**：位於 `.agents/hooks.json`，生命週期與非 Docker 環境防護。

---

## 4. 專案規格資產目錄 (Single Source of Truth)

所有工程意圖落盤於專案根目錄之 `docs/` 下，與代碼版本庫同步演進：
* `docs/proposals/`：業務需求提案（鎖定商業痛點與 MVP 範圍）。
* `docs/sdd/`：軟體設計規格書（鎖定領域模型、Docker 環境規範、API 契約與 DDL）。
* `docs/tasks/`：原子任務清單（帶 `[ ]` Checkbox，作為 Agent 斷點續做之唯一依據）。


