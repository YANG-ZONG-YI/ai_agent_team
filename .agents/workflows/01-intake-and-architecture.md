---
description: "階段一工作流：需求輸入、AI 主動三態辨識、PM 深度訪談與 SA 系統設計規格 (SDD) / 原子任務分解"
---

# 階段一工作流：需求訪談與架構設計規格 (Intake & Architecture)

本工作流由主調度中心自主派遣 **`pm` (產品經理)** 與 **`sa` (系統架構師)** 協同執行，負責將未結構化的需求轉化為無死角的系統規格與原子實施計畫。

---

## 步驟 1：AI 主動三態辨識 (AI Auto-Classification)
1. **`pm`** 接收使用者輸入，探勘語意與代碼庫現況。
2. 主動研判並宣告類別（附帶信心度與判斷依據）：
   - **【新專案 / 新模組 MVP】**：開拓性功能，轉入 MVP 深度訪談。
   - **【線上問題 / Bug 故障】**：異常報錯，轉入 Bug 根因與影響半徑訪談。
   - **【技術債 / 架構重構】**：結構優化，轉入不變量保護與遷移安全訪談。
3. 若需求混雜（例：同時要求修 Bug 與加新功能），主動提出切刀拆分建議。

---

## 步驟 2：PM 深度分流訪談與【門禁一：討論未完禁寫文檔】
- **對話論證（禁止落盤文件）**：
  - 若為 MVP：調用 `ask_question` 強制釐清核心北極星指標、In-Scope vs Out-of-Scope 切刀、極致技術棧與 NFRs。
  - 若為 Bug：釐清現象 vs 預期、重現步驟、TraceId、錯誤日誌與受損聚合根。
  - 若為技術債：釐清重構動機、黃金驗收測試、遷移路徑與一鍵回退條件。
- **[HARD-GATE 1] 使用者確認放行**：
  - 只有在使用者於對話中明確確認同意方案後，方可由 `pm` 落盤：
    - MVP：`docs/01-requirements/<module-name>/REQ-YYYYMMDD-<name>.md`
    - Bug：`docs/01-requirements/<module-name>/ISSUE-YYYYMMDD-<name>.md`
    - 技術債：`docs/01-requirements/<module-name>/DEBT-YYYYMMDD-<name>.md`

---

## 步驟 3：SA 系統架構設計 (DDD & Docker Topology)
1. 主調度中心自主派遣 **`sa`** 承接需求規格，執行 DDD 領域建模與防腐層（ACL）設計。
2. 規劃 Docker 隔離開發環境（`Dockerfile` 與 `docker-compose.yml` 拓撲）。
3. 制定 API 介面契約（RESTful / gRPC）與 3NF 資料庫 Schema（DDL）。
4. 產出軟體設計規格書：`docs/02-architecture-sdd/<module-name>/SDD-YYYYMMDD-<name>.md`。

---

## 步驟 4：SA 原子實施計畫分解與【門禁二：無核准計畫禁寫碼】
1. **`sa`** 將 SDD 規格分解為粒度明確的原子任務，具備 `[ ]` Checkbox、影響檔案與 Docker 驗證指令。
2. 產出原子實施計畫：`docs/03-tasks/<module-name>/TASKS-YYYYMMDD-<name>.md`。
3. **[HARD-GATE 2] 使用者審批實施計畫**：
   - 將實施計畫呈交使用者審查。
   - **使用者審查核准（回覆「批准計畫」）前，嚴禁建立代碼或進入階段二**。
   - 核准後，建立 Feature 分支，自主交接給階段二工作流（`qa` 與 `pg`）。

