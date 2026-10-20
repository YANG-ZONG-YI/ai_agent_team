# 系統需求訪談與架構探索框架 (Requirements Discovery & Interview Rubric)

本框架提供身為顧問級商業分析師（Lead BA）與首席架構師（Chief Architect）在面對未知或模糊系統時，進行精準探詢的六階段問題清單。

---

## 階段 1：業務願景與商業目標 (Business Vision & Goals)

> **目標**：確認系統建立的根本原因（Why），錨定核心價值，避免做出無價值的過度工程。

### 探詢維度：
1. **核心痛點與動機**：
   * 目前現行的作業模式（人工、舊系統、試算表）遇到了什麼無法克服的瓶頸？
   * 若此系統成功上線，最關鍵想要改善的單一商業指標（North Star Metric）是什麼？（例如：訂單處理效率提升 300%、退貨爭議率降低 80%）
2. **利害關係人與終端用戶畫像 (Personas)**：
   * 系統有哪些直接使用者（終端客戶、後台營運、倉儲人員、財務審核等）？
   * 各角色在系統中的權限層級與操作頻率為何？
3. **專案範圍界線 (Scope Boundaries)**：
   * 什麼是 **MVP（最小可行性產品）第一期必須包含的**？
   * 什麼是明確**不在第一期範圍內（Out of Scope）** 的？

---

## 階段 2：DDD 業務領域探索與事件風暴 (Domain Exploration & Event Storming)

> **目標**：從業務本質出發，梳理業務流程中的動態事件與靜態實體，提煉統一語言（Ubiquitous Language）。

### 探詢維度：
1. **核心業務事件 (Domain Events - 過去式動詞)**：
   * 在使用流程中，關鍵的「里程碑事件」有哪些？（例如：`OrderPlaced` 訂單已建立、`PaymentAuthorized` 付款已授權、`InventoryReserved` 庫存已保留、`GoodsDispatched` 商品已出貨）
2. **限界上下文劃分 (Bounded Contexts)**：
   * 系統自然可以拆分成哪些獨立的業務子域？
     * **核心域 (Core Domain)**：為業務帶來競爭優勢的核心邏輯（如：定價策略引擎、智能匹配算法）。
     * **支撐域 (Supporting Domain)**：輔助核心業務但無直接競爭優勢（如：庫存履約、發票開立）。
     * **通用域 (Generic Domain)**：市面上有現成解決方案（如：會員身份認證 Auth、簡訊/Email 發送）。
3. **實體與聚合根 (Aggregates & Invariants)**：
   * 哪些業務規則是「永遠不可被破壞」的生命週期約束？（例如：訂單一旦進入「處理中」，商品明細即不可任意刪除；帳戶扣款時餘額不得為負數）。

---

## 階段 3：系統架構邊界與技術約束 (Architecture Boundaries & Constraints)

> **目標**：確立技術選型、系統形態（單體 vs 微服務）與第三方整合邊界。

### 探詢維度：
1. **系統形態與部署拓撲**：
   * 傾向於 **模組化單體（Modular Monolith）** 還是 **微服務架構（Microservices）**？
   * （架構師建議：團隊規模小於 10 人或新業務孵化期，強烈建議模組化單體，待邊界穩定後再行拆分）。
2. **技術棧生態與團隊技能**：
   * 後端偏好：TypeScript/Node.js、Go、Java/Kotlin、C#、Python？
   * 前端/客戶端：React/Next.js、Vue、原生 Mobile (iOS/Android) 或 Cross-platform (Flutter)？
   * 部署環境：AWS、GCP、Azure、Kubernetes 或自建機房？
3. **第三方外部依賴與防腐層 (ACL, Anticorruption Layer)**：
   * 是否需介接既有系統（舊 ERP、CRM、Core-Banking）？
   * 外部 API 服務（金流綠界/Stripe、地圖 Google Maps、簡訊 Twilio 等）的穩定性與限流限制？

---

## 階段 4：非功能性需求深入剖析 (Non-Functional Requirements, NFRs)

> **目標**：確保系統不僅「功能正確」，且在現實世界中具備高可用、彈性與安全性。

### 探詢維度：
1. **性能與負載指標 (SLA & Latency)**：
   * 尖峰流量預估：一般 QPS/TPS 多少？尖峰活動（如秒殺、報稅期）QPS 多少？
   * 延遲要求：API 平均響應時間是否需在 200ms 以內？
2. **資料特徵與持久化需求**：
   * 讀寫比例：是典型的「讀多寫少」（如文章/商品瀏覽 99:1），還是「寫入密集」（如 IoT 上報、日誌收集）？
   * 資料量與歷史保存：首年預期資料量有多大？歷史冷資料是否需要封存？
3. **資料一致性與事務邊界**：
   * 哪些環節必須保證 **強一致性（ACID）**？
   * 哪些場景可接受 **最終一致性（Eventual Consistency）** 搭配補償機制（Saga Pattern）？
4. **安全合規與審計**：
   * 認證與授權機制：OAuth2 / OIDC / JWT / Session？角色權限（RBAC）還是屬性權限（ABAC）？
   * 法規合規：GDPR、個資去識別化、信用卡 PCI-DSS、操作 Audit Log（不可竄改審計日誌）。

---

## 階段 5：功能清單與 BDD 驗收條件 (Feature Breakdown & Acceptance)

> **目標**：將業務語意精煉為工程人員可直接撰寫測試與代碼的具體規格。

### 探詢維度：
1. **Epic 與 Feature 矩陣**：
   * 清晰梳理模組關係樹（Module → Epic → Feature）。
2. **User Stories 與情境驗收**：
   * 格式規範：
     ```gherkin
     場景 (Scenario): 買家使用折價券完成結帳
       假設 (Given) 購物車內有總額 1000 元的有效商品
       並且 (And) 買家擁有一張滿 800 折 100 的優惠券
       當 (When) 買家點選確認使用該優惠券並提交結帳
       那麼 (Then) 訂單應付款金額應為 900 元
       並且 (And) 該優惠券狀態應變更為「已使用」
       並且 (And) 系統應發布 OrderCreated 領域事件
     ```

---

## 階段 6：審核並輸出正式 SDD

> **目標**：完成資訊收斂，嚴格依照標準範本產出軟體設計規格書。
