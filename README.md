# AI Agent Team (ai_agent_team)

Google Antigravity IDE 規格驅動開發（Spec-Driven Development, SDD）與多 Agent 協同架構專案。

---

## 核心架構亮點

1. **專案架構最高憲法 (`.agents/AGENTS.md`)**：
   - **DDD 領域純粹性**：Domain Layer 零污染，強制依賴倒置 (DIP)。
   - **SDD 規格先行**：無規格禁止貿然編程。
   - **TDD 測試先行**：紅綠重構律 (Red-Green-Refactor)。
   - **聚合根與防腐邊界**：外部呼叫必須經由 ACL 防腐層。

2. **雙 Skill 職責分離體系 (`.agents/skills/`)**：
   - **`system-analysis-architect`**（分析腦）：負責顧問級業務訪談、DDD 建模與技術拓撲。
   - **`spec-driven-lifecycle`**（工程手）：負責 `docs/` 下 Proposal ➔ SDD ➔ Tasks 的生命週期管理與 Checkbox 斷點續做。

3. **三專用 Subagents 協同矩陣 (`.agents/agents/`)**：
   - `domain-analyst`：業務願景探索、事件風暴與統一語言提煉。
   - `system-architect`：C4 架構拓撲、API 契約、DDL 與 NFRs 設計。
   - `tdd-engineer`：單元/整合測試編寫與極端邊界覆蓋。

4. **單一真實來源規格庫 (`docs/`)**：
   - `docs/proposals/`：業務需求提案。
   - `docs/sdd/`：軟體設計規格書。
   - `docs/tasks/`：原子實施任務清單（帶 `[ ]` Checkbox 追蹤進度）。

5. **生命週期硬防衛門禁 (`.agents/hooks.json`)**：
   - 支援 PreToolUse / PostToolUse 程式碼攔截，阻止高危操作與確保程式碼品質。

---

## 快速上手

### 1. 啟動需求訪談
在 Antigravity IDE 聊天框中輸入斜線指令：
```text
/workflow-system-analysis-interview
```

### 2. 啟動規格驅動開發流程 (SDD Pipeline)
```text
/workflow-spec-driven-development
```

### 3. 查看當前任務進度
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .agents/skills/spec-driven-lifecycle/scripts/check-task-progress.ps1
```
