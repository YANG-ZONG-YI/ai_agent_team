# 顧問級 Grill-Me 需求與架構深度拷問手冊 (Grill-Me Interview Rubric)

本手冊規範在執行系統訪談時，如何如同 `/grill-me` 般沿著決策樹（Design Tree）逐個分支深挖，透過 `ask_question` 工具消弭所有模糊地帶，同時將 Docker 容器化開發環境列為前置不可變量。

---

## 訪談核心鐵律 (Grill-Me Golden Rules)

1. **分支逐一突破（One Branch at a Time）**：解鎖上游決策前，不貿然探討下游細節。
2. **工具調用規範**：向使用者提問時，強制使用 `ask_question` 工具，提供清晰選項並以 `(Recommended)` 標註架構師推薦方案。
3. **代碼庫先行（Codebase First）**：若專案既有程式碼、設定檔或 Dockerfile 已存在解答，直接援引並向用戶確認，不問重複問題。
4. **邊界拷問（Boundary Probing）**：每一個業務流程必須追問：「失敗了怎麼辦？併發了怎麼辦？超時了怎麼辦？權限不足怎麼辦？」

---

## 階段 1：業務願景與商業目標 Grill-Me (Why & Scope)

### 決策樹分支 1.1：核心痛點與北極星指標 (North Star Metric)
* **拷問核心**：現行作業（人工作業、舊系統、試算表）最致命的痛點？上線後最看重的單一量化指標是什麼？
* **`ask_question` 推薦範例**：
  - 問題：「本專案首要解決的核心業務瓶頸與成功驗收指標為何？」
  - 選項：
    - (Recommended) 自動化核心履約流程，降低人工介入錯誤率 80% 以上
    - 提升高併發讀寫吞吐量，支撐尖峰流量並降低延遲至 100ms 內
    - 舊系統架構重構，建立整潔領域模型以縮短未來功能交付週期 50%

### 決策樹分支 1.2：角色矩陣與操作頻率 (Personas & Boundaries)
* **拷問核心**：誰是系統的使用者？有誰能核准？誰只讀？有無多租戶（Multi-tenancy）？
* **拷問邊界**：不同角色跨機構/跨門市能否查看彼此資料？

### 決策樹分支 1.3：MVP 範圍嚴格鎖定 (Scope Lock)
* **拷問核心**：第一期上線「必須具備」與「堅決不做（Out of Scope）」的功能切點在哪？

---

## 階段 2：DDD 領域探索與事件風暴 Grill-Me (Domain & Events)

### 決策樹分支 2.1：過去式領域事件 (Domain Events)
* **拷問核心**：業務主流程包含哪些具備業務意義的過去式動詞事件？
  * 例：`OrderSubmitted` ➔ `PaymentCaptured` ➔ `InventoryAllocated` ➔ `ShipmentDispatched`。
* **邊界拷問**：事件若重複推送（Duplicate Event），業務上是否具備冪等性保證？

### 決策樹分支 2.2：限界上下文劃分 (Bounded Contexts)
* **拷問核心**：如何切分核心域（Core）、支撐域（Supporting）與通用域（Generic）？
* **邊界拷問**：各上下文間如何傳遞訊息？共享內核（Shared Kernel）、顧客-供應商（Customer-Supplier）還是防腐層（ACL）？

### 決策樹分支 2.3：聚合根與業務不變量 (Aggregates & Invariants)
* **拷問核心**：哪一個實體擔任聚合根？聚合內不可破壞的業務鐵律為何？
  * 例：訂單金額計算必須由 Order 聚合根統一處理，外部嚴禁直接修改 OrderItem 單價。

---

## 階段 3：Docker 開發與容器化架構拓撲 (Docker & Infrastructure)

### 決策樹分支 3.1：強制 Docker 開發與運行環境 (Docker-Only Invariant)
* **拷問核心**：專案開發、測試與本機執行必須 100% 於 Docker 容器進行，非 Docker 環境物理終止。
* **`ask_question` 推薦範例**：
  - 問題：「本專案之 Docker 容器化開發環境配置偏好？」
  - 選項：
    - (Recommended) 採用 Docker Compose（包含 App Container + PostgreSQL/MySQL + Redis，程式碼透過 Volume 即時熱重載）
    - 採用輕量單一 Dockerfile（容器內包含執行時與測試環境，指令透過 docker run --rm 執行）
    - 採用 DevContainer 標準規格（.devcontainer 配置，完全在 VSCode/IDE 容器中無縫開發）

### 決策樹分支 3.2：外部依賴與防腐層 (ACL)
* **拷問核心**：串接哪些外部第三方 API？（Stripe/綠界金流、Twilio 簡訊、外部舊 ERP）。
* **邊界拷問**：若第三方服務斷線或超時（Timeout 5s），系統如何處理？（重試、斷路器 Circuit Breaker、落表死信隊列？）

---

## 階段 4：API 契約與資料持久化設計 (Contracts & DDL)

### 決策樹分支 4.1：API 通訊協議與錯誤標準
* **拷問核心**：RESTful JSON 還是 gRPC Protobuf？統一錯誤響應結構（RFC 7807 Problem Details）？
* **邊界拷問**：關鍵寫入 API 是否具備 `Idempotency-Key` 防重機制？

### 決策樹分支 4.2：資料庫模型與事務邊界
* **拷問核心**：關聯式資料庫選型（PostgreSQL / MySQL），聚合根儲存是 3NF 還是 JSONB 混合？
* **邊界拷問**：跨聚合操作是採用資料庫本地事務（Local Transaction），還是領域事件驅動的最終一致性（Outbox Pattern + Saga）？

---

## 階段 5：極限異常流與非功能性需求 (NFRs & Exceptions)

### 決策樹分支 5.1：高併發與資料競態 (Concurrency Control)
* **拷問核心**：面對秒殺、庫存扣減或重複扣款，如何防止超賣？
  * 悲觀鎖（SELECT FOR UPDATE）vs 樂觀鎖（Version Check）vs Redis 分散式鎖？

### 決策樹分支 5.2：安全防護與合規審計
* **拷問核心**：認證授權（JWT Bearer Token / OAuth2）、敏感個資遮蔽（PII Masking）、操作審計日誌（Audit Log）。

---

## 階段 6：SDD 工業級規格書收斂與 TDD 驗收
* 資訊全維度收斂完畢後，產出工業級 `docs/sdd/sdd-<name>.md`。
* 移交 `tdd-engineer` 於 **Docker 容器內部** 啟動紅燈測試實作。

