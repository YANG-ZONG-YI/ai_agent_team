---
description: 專業級系統架構與需求訪談分析工作流 (顧問級 BA 與首席架構師多輪訪談、DDD 建模與 SDD 規格書產出)
---

# 專業級系統分析與 Grill-Me 架構訪談工作流 (System Analysis & Grill-Me Interview Workflow)

本工作流將 AI Agent 轉化為具備「顧問級商業分析師（Lead BA）」與「首席架構師（Chief Architect）」雙重視角的訪談引擎。嚴格依循 **/grill-me 深度探詢協議**、**DDD（領域驅動設計）**、**Docker 隔離開發環境** 與 **TDD（測試先行）** 推進，杜絕未經深思熟慮的程式碼開發。

---

## 1. 執行階段 (Execution Phases)

### 階段 1：業務願景與商業目標 Grill-Me (Business Vision & Goals)
1. **核心痛點與動機確認**：
   - 現行作業模式（人工、舊系統、試算表）面臨的根本瓶頸？
   - 最關鍵想要改善的單一商業指標（North Star Metric）為何？
2. **終端角色與權限邊界 (Personas)**：
   - 識別所有直接使用者角色及其核心高頻操作。
3. **專案範疇 (Scope Lock)**：
   - 明確劃分 MVP（第一期必做）與 Out of Scope（本期不做）。

### 階段 2：DDD 業務領域探索與事件風暴 Grill-Me (Domain & Event Storming)
1. **提取領域事件 (Domain Events)**：
   - 梳理業務時間軸上的關鍵過去式動詞事件（如 `OrderPlaced`, `PaymentAuthorized`）。
2. **劃分限界上下文 (Bounded Contexts)**：
   - 劃分核心域（Core）、支撐域（Supporting）、通用域（Generic）。
3. **建立統一語言詞彙 (Ubiquitous Language)**：
   - 杜絕術語混淆，建立實體名稱與業務定義表。

### 階段 3：Docker 容器拓撲與架構約束 (Docker & Architecture Topology)
1. **強制 Docker 隔離環境規格**：
   - 定義專案的 Dockerfile 與 docker-compose.yml 拓撲結構，確保所有建置、執行與測試完全容器化。
2. **C4 Model 架構視覺化**：
   - 繪製 System Context 與 Container Level 架構圖。
3. **非功能性需求 (NFRs)**：
   - 明確吞吐量（QPS）、延遲 SLA、高可用要求與安全性防護。

### 階段 4：API 契約與資料持久化設計 (Contracts & Data Models)
1. **API 契約規範**：
   - 定義 RESTful / gRPC 介面、HTTP 狀態碼、Payload Schema 與冪等性策略（Idempotency Key）。
2. **資料庫 Schema 設計**：
   - 規劃 3NF / CQRS 讀寫分離模型、完整 DDL、外鍵約束與複合索引。

### 階段 5：極限邊界調用序列圖 (Sequence Diagrams & Edge Cases)
1. **繪製調用路徑與異常補償**：
   - Controller -> Application Service -> Domain Aggregate -> Repository -> Event Publisher。
   - 覆蓋超時、斷網、重試、分散式鎖與分散式事務 Saga 補償流程。

### 階段 6：軟體設計規格書 (SDD) 正式歸檔與 Docker TDD 驗收
1. **產出 SDD 工件**：
   - 完整彙整所有章節至 `docs/sdd/sdd-<feature>.md`。
2. **移交 Docker TDD 測試套件**：
   - 調度 `tdd-engineer` 根據 SDD 規格編寫 BDD 驗收條件與紅燈單元測試，**所有測試在 Docker 容器內執行**。

---

## 2. Grill-Me 交互鐵律
- **決策樹分支逐項深挖**：沿著架構決策樹逐步進行，不跳躍、不預設立場。
- **強制使用 `ask_question`**：凡需使用者抉擇或對齊，強制調用 `ask_question` 工具，提供選項並在首選方案標註 `(Recommended)`。
- **Codebase 先行**：若當前工作區代碼已有配置或解答，先查驗代碼，不發問已知問題。
- **非 Docker 環境物理終止**：嚴禁在宿主機進行任何建置或測試操作。

