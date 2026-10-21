# 需求規格書 (MVP 規格書): [模組/功能名稱]

- **文件編號**: REQ-YYYYMMDD-[name]
- **需求類型**: 【新專案 / 新模組 MVP】
- **負責 PM**: PM Agent
- **北極星指標 (North Star Metric)**: [量化核心驗證目標，例：首頁至完成結帳轉換率 > 15%]

---

## 1. 商業背景與價值假說
- **痛點陳述**: [使用者目前遭遇的核心困難]
- **價值假說**: [透過本 MVP 解決什麼問題，帶來什麼價值]

---

## 2. 邊界與範疇切刀 (Scope Cutting)
### 2.1 In-Scope (本次 MVP 必做範圍)
- [P0 核心流程 1]
- [P0 核心流程 2]

### 2.2 Out-of-Scope (第一版絕對不做，嚴格防膨脹)
- [明確排除的項目 1]
- [明確排除的項目 2]

---

## 3. 極致技術棧規格 (Tech Stack Specification)
- **後端運行時與語言**: [例: Node.js 20 LTS / Python 3.11 / Go 1.22]
- **後端框架與版本**: [例: Fastify v4 / FastAPI v0.110 / Gin v1.9]
- **前端框架與 UI**: [例: Next.js 14 App Router / React 18 + Vanilla CSS]
- **資料庫 (DB)**: [例: PostgreSQL 16 (預設 3NF 設計)]
- **快取與訊息佇列**: [例: Redis 7.2 / RabbitMQ 3.12]
- **Docker 基礎映像檔**: [例: node:20-alpine / python:3.11-slim (非 root 運行)]

---

## 4. 使用者故事與驗收條件 (Acceptance Criteria)
### Story 1: [使用者故事名稱]
- **身為** [角色]
- **我想要** [功能行為]
- **以便於** [商業價值]
- **驗收條件 (Given-When-Then)**:
  - **Given**: [前置條件]
  - **When**: [操作觸發]
  - **Then**: [預期結果]

---

## 5. 非功能需求 (NFRs)
- **併發量預估**: [QPS 預期值]
- **延遲要求**: [P99 < 200ms]
- **資安合規**: [OWASP Top 10、敏感欄位遮蔽]
