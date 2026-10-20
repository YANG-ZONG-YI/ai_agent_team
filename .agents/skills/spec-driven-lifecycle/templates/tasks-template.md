# 實施原子任務清單 (Execution Tasks): [功能/模組名稱]

## 1. 任務元數據 (Metadata)
- **關聯規格**：[docs/sdd/sdd-*.md]
- **執行代理**：tdd-engineer
- **進度追蹤**：未完成 [ ] / 已完成 [x]
- **執行原則**：嚴格按編號逐項推進，完成一個並通過測試後才可勾選 `[x]`，不得跳步。

---

## 2. 實施任務步驟 (Atomic Task Pipeline)

### 階段一：領域實體與紅燈測試 (Domain & Unit Tests)
- [ ] 1.1 編寫領域實體邊界條件與不變量測試（確認測試失敗 - Red Phase）
- [ ] 1.2 實作領域實體與值對象，確保業務邏輯正確性
- [ ] 1.3 運行測試確認全數通過（Green Phase）

### 階段二：持久化與資料庫遷移 (Persistence & DDL)
- [ ] 2.1 建立資料庫遷移檔與索引定義
- [ ] 2.2 實作 Repository 介面與適配器整合測試

### 階段三：應用層與 API 端點 (Application & API Layer)
- [ ] 3.1 實作 Application Service / UseCase 邏輯
- [ ] 3.2 串接 API Controller / Route 與輸入校驗 DTO
- [ ] 3.3 執行 API 端對端（E2E）整合測試

### 階段四：架構門禁與驗收回歸 (Verification & Regression)
- [ ] 4.1 執行靜態代碼檢查與 Linter 格式校驗
- [ ] 4.2 執行完整回歸測試套件
- [ ] 4.3 規格歸檔與完成確認
