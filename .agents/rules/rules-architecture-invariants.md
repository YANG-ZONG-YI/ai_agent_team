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

## 4. 強制 Docker 隔離開發環境律 (Docker-Only Isolation & Hard Stop)
* **宿主環境零污染**：專案之一切套件安裝（npm, pip, go mod, cargo）、編譯（build）、測試（test）、執行（run）**一律強制在 Docker 容器內執行**（如 `docker compose exec ...` 或在容器內部隔離運行）。
* **非 Docker 環境物理終止（Hard Stop）**：嚴禁直接在主機宿主系統（Windows / PowerShell / Bash）調用編譯器或運行測試。若目前非處於 Docker 環境或 Docker 容器尚未啟動，**必須立即中止操作（STOP）並提示用戶**。
* **環境準備先行**：所有功能開發任務首要確認 Dockerfile / compose 運行無虞，方可執行後續流程。

## 5. Grill-Me 深度需求訪談協議 (Grill-Me Protocol)
* **沿著決策樹逐項攻克**：不可籠統帶過，必須順著架構決策依賴樹（業務痛點 -> 領域事件 -> 邊界上下文 -> 聚合根 -> API/DDL -> 極限異常與非功能需求）逐一深挖對齊。
* **問答互動工具強制**：凡涉及需求架構抉擇與確認，一律使用 `ask_question` 工具呈現結構化選項，並預設標註 `(Recommended)` 最佳實踐。
* **靜態探勘先行**：若問題可透過檢查工作區代碼或現有配置解答，嚴禁重複提問。

