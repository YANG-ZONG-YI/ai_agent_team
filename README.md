# AI Agent Team (ai_agent_team)

Google Antigravity IDE 規格驅動開發（Spec-Driven Development, SDD）與多 Agent 協同架構專案。

---

## 核心架構亮點

1. **專案架構最高憲法 (`.agents/AGENTS.md`)**：
   - **DDD 領域純粹性**：Domain Layer 零污染，強制依賴倒置 (DIP)。
   - **SDD 規格先行 & Grill-Me 深度訪談**：無規格禁止編程，使用 `/grill-me` 協議與 `ask_question` 逐項攻克決策樹。
   - **TDD 測試先行**：紅綠重構律 (Red-Green-Refactor)。
   - **聚合根與防腐邊界**：外部呼叫必須經由 ACL 防腐層。
   - **Docker 強制隔離開發環境**：套件安裝、編譯、測試與運行 100% 於 Docker 容器內，非 Docker 環境物理終止（Hard Stop）。

2. **雙 Skill 職責分離體系 (`.agents/skills/`)**：
   - **`system-analysis-architect`**（分析腦）：具備 Grill-Me 深度探詢能力，沿著決策樹透過 `ask_question` 梳理 DDD 領域模型與 Docker 容器化拓撲。
   - **`spec-driven-lifecycle`**（工程手）：負責 `docs/` 下 Proposal ➔ SDD ➔ Tasks 的生命週期管理、Docker 環境門禁與 Checkbox 斷點續做。

3. **三專用 Subagents 協同矩陣 (`.agents/agents/`)**：
   - `domain-analyst`：Grill-Me 業務願景深挖、事件風暴與統一語言提煉。
   - `system-architect`：C4 架構拓撲、Docker 容器架構、API 契約、DDL 與 NFRs 設計。
   - `tdd-engineer`：**在 Docker 容器內**執行紅燈單元/整合測試，非 Docker 環境強制停止。

4. **單一真實來源規格庫 (`docs/`)**：
   - `docs/proposals/`：業務需求提案。
   - `docs/sdd/`：軟體設計規格書（包含 Docker 容器規範）。
   - `docs/tasks/`：原子實施任務清單（包含階段 0 Docker 環境預檢與 `[ ]` Checkbox）。

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

---

## 自動化短影音產製與多平台分發管線 (Video Automation Pipeline)

本專案現已完整實作以下核心工業級模組，100% 於 Docker 容器隔離環境運作：

### 1. 服務拓撲與啟動
```bash
# 啟動全套 Docker 服務 (PostgreSQL + pgvector, Redis, FastAPI App, Celery Worker)
docker compose up -d

# 於 Docker 容器內執行全量自動化測試 (單元測試、整合測試、E2E 驗收)
docker compose exec app pytest
```

### 2. 核心架構模組
- **Notion 前端看板雙向適配器 (ACL)**：[`src/infrastructure/adapters/notion_adapter.py`](./src/infrastructure/adapters/notion_adapter.py)
  - 支援定時輪詢 (`POST /api/v1/notion/poll`) 與即時事件接收 (`POST /api/v1/notion/webhook`)。
  - 成片渲染後自動回填預覽 URL 與平台發布狀態至 Notion。
- **PostgreSQL + pgvector 向量去重知識庫**：[`src/infrastructure/database/script_repository.py`](./src/infrastructure/database/script_repository.py)
  - 1536 維度 IVFFlat 餘弦相似度比對，超過 0.85 自動判定為重複內容。
- **三段式短影音生成引擎**：[`src/infrastructure/ai/script_generator.py`](./src/infrastructure/ai/script_generator.py)
- **TTS 語音配音與 SRT 時間軸**：[`src/infrastructure/ai/tts_service.py`](./src/infrastructure/ai/tts_service.py)
- **9:16 (1080x1920) 短影音渲染引擎 (MoviePy + FFmpeg)**：[`src/infrastructure/ai/video_renderer.py`](./src/infrastructure/ai/video_renderer.py)
- **四大多平台發布矩陣 (ACL)**：[`src/infrastructure/adapters/social_publishers.py`](./src/infrastructure/adapters/social_publishers.py)
  - YouTube Shorts, Instagram Reels, Facebook Reels, TikTok 獨立狀態機與 3 次指數退避重試防護。
- **Celery 異步處理管線**：[`src/infrastructure/queue/tasks.py`](./src/infrastructure/queue/tasks.py)

