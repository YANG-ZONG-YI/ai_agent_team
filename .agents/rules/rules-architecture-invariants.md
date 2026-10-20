---
trigger: always_on
description: 專案核心架構約束（DDD 分層純粹、SDD 規格先行、TDD 測試先行、防腐層 ACL）
---

# 專案架構核心不可變量與工程規範 (Architecture Invariants)

本規範為本專案不可妥協之核心架構約束，在對話與代碼生成過程中常駐生效（always_on）：

## 1. DDD 分層依賴倒置原則 (Dependency Inversion)
* **Domain Layer 保持純粹**：領域層（Entities、Value Objects、Domain Events）嚴禁依賴任何基礎設施（ORM、資料庫驅動、HTTP Client 或外部框架）。
* **介面定義於內部，實作於外部**：Repository、Notification 等外部介面必須定義在 Domain 或 Application 層，其實作（Implementation）統一置於 Infrastructure 層。

## 2. SDD 與 TDD 先行原則 (Design & Test First)
* **禁止未定規格逕自寫碼**：任何新增功能或重大架構變更，必須先在 SDD 文件中對齊 API 契約、領域模型與資料表設計。
* **紅燈測試先行**：開發業務邏輯時，必須先具備對應的單元或整合測試（Red Phase），驗證該測試在無實作時失敗，實作後通過（Green Phase）。

## 3. 領域不變量與防腐邊界 (Invariants & Anti-Corruption)
* **聚合根是唯一變更入口**：外部禁止直接更新聚合內部的子實體，必須透過聚合根提供的領域方法操作以確保狀態一致性。
* **外部介接必須設立防腐層 (ACL)**：對接任何第三方服務或舊系統時，必須建立 Adapter / DTO 轉換器，嚴禁讓外部資料模型穿透進內部領域層。
