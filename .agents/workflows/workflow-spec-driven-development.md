---
description: 規格驅動開發全生命週期工作流 (從 Proposal 提案、SDD 架構規格到 Tasks 原子清單與 TDD 實施)
---

# 規格驅動開發全生命週期工作流 (Spec-Driven Development Workflow)

本工作流為專案開發之標準推進流水線。嚴格貫徹 **「規格為唯一真相源（Spec-First）」** 與 **「測試先行（TDD-First）」**，透過四階段推進落盤，保證代碼開發全程受控、可回溯、無痛接關。

---

## 1. 四階段執行流 (4-Phase Pipeline)

### 階段 1：需求提案與邊界鎖定 (Proposal Phase)
1. 調度 `domain-analyst` 梳理核心業務痛點與使用場景。
2. 參考 [proposal-template.md](../skills/spec-driven-lifecycle/templates/proposal-template.md) 建立 `docs/proposals/proposal-YYYYMMDD-<name>.md`。
3. 明確切分 MVP 範圍（In Scope）與留待下期範圍（Out of Scope）。
4. **檢查點**：獲得用戶確認後，推進至階段 2。

### 階段 2：軟體設計規格書定案 (SDD Design Phase)
1. 調度 `system-architect` 進行技術拓撲與 DDD 領域建模。
2. 規劃限界上下文、聚合根、實體、領域事件、防腐層 (ACL)。
3. 明確 API 契約（Schema/Status Codes）與資料庫 DDL 遷移腳本。
4. 參考 [sdd-template.md](../skills/spec-driven-lifecycle/templates/sdd-template.md) 輸出至 `docs/sdd/sdd-<name>.md`。
5. **檢查點**：架構審查通過後，推進至階段 3。

### 階段 3：原子任務分解 (Task Breakdown Phase)
1. 由 `system-architect` 與 `tdd-engineer` 共同編排實施步驟。
2. 參考 [tasks-template.md](../skills/spec-driven-lifecycle/templates/tasks-template.md) 建立 `docs/tasks/tasks-<name>.md`。
3. 每個子項目必須具備 `[ ]` Checkbox，並嚴格將「紅燈測試編寫」排在「業務代碼實作」之前。
4. **檢查點**：任務清單鎖定後，推進至階段 4。

### 階段 4：斷點實施與進度勾選 (Apply & TDD Phase)
1. 調度 `tdd-engineer` 循序執行：
   - 讀取 `docs/tasks/` 中第一個未勾選 `[ ]` 的任務。
   - 先編寫失敗測試（Red），確認測試變紅。
   - 編寫最小實作代碼使測試通過（Green）。
   - 進行代碼結構重構（Refactor）。
   - 將該任務勾選為 `[x]`。
2. 執行驗證腳本：
   `powershell -NoProfile -ExecutionPolicy Bypass -File .agents/skills/spec-driven-lifecycle/scripts/check-task-progress.ps1`
3. 循環推進直至所有項目全數標記為 `[x]`。

---

## 2. 斷點續做說明 (Resume Session)
若對話因長度中斷或切換新對話，使用者只需輸入：
> 「讀取最新的 tasks 檔案並繼續未完成任務」

Agent 將主動解析未完成項立即無縫接軌，無需重複訪談或重新解釋架構。
