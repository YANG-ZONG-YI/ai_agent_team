---
name: spec-driven-lifecycle
description: >-
  規格驅動開發生命週期管理器 (Spec-Driven Lifecycle Manager)。
  用於管理專案從需求提案 (docs/proposals/)、軟體設計規格書 (docs/sdd/) 到原子任務清單 (docs/tasks/) 的完整生命週期。
  負責四階段流程控制、模板實例化、任務分解與斷點續做（Checkbox 進度追蹤），確保 AI 團隊有條不紊地推進實作。
---

# 規格驅動開發生命週期管理 Skill (Spec-Driven Lifecycle Manager)

本 Skill 專門用於調度與規範 AI Agent 團隊依循 **OpenSpec 理念** 推進研發工作。它確立了「規格為唯一真相源」的執行準則，將所有意圖落盤為文件，杜絕聊天記錄丟失與盲目編程。

---

## 1. 核心規格檔案架構 (File Convention)

所有規格產出物嚴格放置於專案根目錄的 `docs/` 下，與程式碼版本庫同步：

```text
docs/
├── proposals/    # 需求提案 (proposal-YYYYMMDD-<name>.md)
├── sdd/          # 軟體設計規格書 (sdd-<name>.md)
└── tasks/        # 原子實施任務清單 (tasks-<name>.md)
```

---

## 2. 四階段標準作業循環 (The 4-Phase Lifecycle)

```mermaid
graph LR
    P1[1. 提案 Propose<br/>docs/proposals/] --> P2[2. 規格設計 Design<br/>docs/sdd/]
    P2 --> P3[3. 任務拆解 Breakdown<br/>docs/tasks/]
    P3 --> P4[4. 斷點實施 Apply<br/>TDD & [x] 勾選]
```

### 階段一：需求提案 (Propose Phase)
1. **觸發時機**：用戶提出新功能、重大改動或業務重構時。
2. **指派角色**：調度 `domain-analyst`。
3. **執行步驟**：
   - 參考 [proposal-template.md](./templates/proposal-template.md)。
   - 梳理業務問題、MVP 範圍與使用場景。
   - 輸出至 `docs/proposals/proposal-YYYYMMDD-<feature>.md`。
   - 必須經由用戶確認後，方可進入下一階段。

### 階段二：軟體架構設計 (Design Phase)
1. **觸發時機**：提案確認通過後。
2. **指派角色**：調度 `system-architect`。
3. **執行步驟**：
   - 參考 [sdd-template.md](./templates/sdd-template.md)。
   - 進行 DDD 領域建模（聚合根、實體、領域事件、防腐層 ACL）。
   - 規劃 API 契約、資料庫 DDL Schema 與 NFRs。
   - 輸出至 `docs/sdd/sdd-<feature>.md`。
   - 必須經由用戶審閱架構無誤後，方可進入任務拆解。

### 階段三：原子任務拆解 (Task Breakdown Phase)
1. **觸發時機**：SDD 規格定案後。
2. **指派角色**：`system-architect` 與 `tdd-engineer` 共同對齊。
3. **執行步驟**：
   - 參考 [tasks-template.md](./templates/tasks-template.md)。
   - 將實作細節拆解為**原子化、具備明確驗收標準、包含 `[ ]` Checkbox** 的任務清單。
   - 嚴格遵守「紅燈測試先行 (TDD)」的工序編排。
   - 輸出至 `docs/tasks/tasks-<feature>.md`。

### 階段四：斷點實施與進度追蹤 (Apply & Track Phase)
1. **觸發時機**：用戶指示「開始實作」或「繼續任務」時。
2. **指派角色**：調度 `tdd-engineer`。
3. **無縫接關與執行原則**：
   - **Docker 容器硬性門禁（Hard Stop if not in Docker）**：
     - 所有套件安裝、代碼編譯與測試執行**必須 100% 在 Docker 容器內運行**。
     - 嚴禁直接在宿主機（Host）執行 `npm`, `pip`, `go test` 等命令。若 Docker 尚未啟動或環境未就緒，**Agent 必須立即停止（STOP）並提示用戶**。
   - **讀取斷點**：讀取 `docs/tasks/tasks-<feature>.md`，找到**第一個未勾選 `[ ]`** 的任務。
   - **Docker 內 TDD 實作**：先在 Docker 容器內跑失敗測試（Red），再寫最小實作代碼在 Docker 內通過（Green），最後重構（Refactor）。
   - **勾選狀態**：實作通過驗收測試後，**主動將該項修改為 `[x]`**。
   - **進度檢查**：可呼叫輔助腳本查看即時進度：
     `powershell -NoProfile -ExecutionPolicy Bypass -File .agents/skills/spec-driven-lifecycle/scripts/check-task-progress.ps1`
   - **會話中斷重啟**：若對話重新開始，Agent 只要重新讀取 `tasks.md`，在 Docker 環境中立即自未完成的第一項無縫接關，零進度遺失。

---

## 3. 雙 Skill 職責邊界

* **`system-analysis-architect`**：負責「腦力激盪、深層訪談、架構決策與推導（How to analyze）」。
* **`spec-driven-lifecycle`**（本 Skill）：負責「文件資產落地、檔案版本流轉、任務清單勾選與斷點恢復（How to manage lifecycle）」。
