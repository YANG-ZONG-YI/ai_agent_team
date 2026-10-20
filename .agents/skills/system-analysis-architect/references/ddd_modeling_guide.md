# 領域驅動設計 (DDD) 實踐指引

本指引旨在協助架構師在進行系統分析時，落實戰略設計（Strategic Design）與戰術設計（Tactical Design），確保代碼架構與業務領域高度對齊。

---

## 一、戰略設計 (Strategic Design)

### 1. 統一語言 (Ubiquitous Language)
在需求訪談過程中，必須建立專屬的名詞辭典，禁止業務端與技術端使用不同術語：
* ❌ 混淆例子：「用戶」、「客戶」、「會員」、「帳號」在不同模組指稱同一事物。
* ✅ DDD 規範：
  * 在「認證上下文」稱作 `Account`（帳號、憑證）
  * 在「商城上下文」稱作 `Customer`（顧客、收件地址）
  * 在「行銷上下文」稱作 `Member`（會員等級、紅利點數）

### 2. 限界上下文映射 (Context Mapping)
限界上下文之間的溝通模式必須在 SDD 中明確定義：
* **Shared Kernel（共享核心）**：雙方共用小部分領域模型與資料庫（謹慎使用）。
* **Customer/Supplier（客戶/供應商）**：下游依賴上游的產出。
* **Anticorruption Layer（防腐層, ACL）**：下游建立轉換適配器，防止上游混亂的資料模型污染自己的核心領域。
* **Open Host Service / Published Language (OHS/PL)**：上游提供標準 API（如 REST / GraphQL）與協議格式。

---

## 二、戰術設計 (Tactical Design)

### 1. 領域構件標準

| 構件 | 定義 | 特徵與約束 |
| :--- | :--- | :--- |
| **Entity (實體)** | 具備唯一識別碼（ID）的對象 | 物件的屬性可能會改變，但透過 ID 追蹤其生命週期（如 `Order`、`User`）。 |
| **Value Object (值對象)** | 無識別碼，以屬性值代表其本質 | **不可變性（Immutable）**，相等性由屬性決定（如 `Money(amount, currency)`、`Address`）。 |
| **Aggregate Root (聚合根)** | 一組緊密相關實體與值對象的門面入口 | 外部物件**只能**透過聚合根進行狀態變更，內部子實體禁止被外部直接存取，用以守護領域不變量（Invariants）。 |
| **Domain Service (領域服務)** | 不自然屬於任何單一實體的無狀態業務邏輯 | 處理跨多個聚合根的協同計算（如：`TransferMoneyService`）。 |
| **Domain Event (領域事件)** | 領域內已經發生的關鍵業務事實 | 命名採用**過去式動詞**（如 `OrderPaidEvent`），用於解耦上下文之間的狀態連動。 |
| **Repository (倉儲介面)** | 提供聚合根持久化與檢索的純介面 | 領域層只定義 Interface，實作（SQL/ORM）下放到 Infrastructure 層。 |

### 2. 經典四層架構 (Clean / Onion / Hexagonal Architecture)

```
┌────────────────────────────────────────────────────────┐
│  Interfaces / Presentation Layer (Controllers, CLI)     │
└───────────────────────────┬────────────────────────────┘
                            │ (調用 Command / Query)
┌───────────────────────────▼────────────────────────────┐
│  Application Layer (Use Cases, DTOs, Event Handlers)   │
└───────────────────────────┬────────────────────────────┘
                            │ (協同聚合根與領域服務)
┌───────────────────────────▼────────────────────────────┐
│  Domain Layer (Entities, Value Objects, Domain Events)  │  <-- 零外部依賴，純業務邏輯
└───────────────────────────▲────────────────────────────┘
                            │ (依賴反轉 Inversion of Control)
┌───────────────────────────┴────────────────────────────┐
│  Infrastructure Layer (Database, ORM, HTTP Client, MQ) │
└────────────────────────────────────────────────────────┘
```
