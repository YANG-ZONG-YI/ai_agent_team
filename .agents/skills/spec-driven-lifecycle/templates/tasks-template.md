# 實施原子任務清單 (Execution Tasks): [功能/模組名稱]

## 1. 任務元數據 (Metadata)
- **關聯規格**：[docs/sdd/sdd-*.md]
- **執行代理**：tdd-engineer
- **執行環境**：Docker 容器隔離環境（非 Docker 環境強制停止 - Hard Stop）
- **進度追蹤**：未完成 [ ] / 已完成 [x]
- **執行原則**：嚴格按編號逐項推進，完成一個並通過容器內測試後才可勾選 `[x]`，不得跳步。

---

## 2. 實施任務步驟 (Atomic Task Pipeline)

### 階段零：Docker 容器環境前置驗收 (Docker Environment Pre-flight)
- [ ] 0.1 驗證 Dockerfile / docker-compose.yml 配置完整性
- [ ] 0.2 啟動開發容器並確認健康檢查通過（如 `docker compose up -d`）
- [ ] 0.3 確認容器內運行時、依賴與測試工具鏈可正常執行（非 Docker 執行物理終止）

### 階段一：領域實體與紅燈測試 (Domain & Unit Tests in Docker)
- [ ] 1.1 在 Docker 容器內編寫領域實體邊界條件與不變量測試（確認測試失敗 - Red Phase）
- [ ] 1.2 實作領域實體與值對象，確保業務邏輯正確性
- [ ] 1.3 在 Docker 容器內運行測試確認全數通過（Green Phase）

### 階段二：持久化與資料庫遷移 (Persistence & DDL in Docker)
- [ ] 2.1 建立資料庫遷移檔與索引定義，於 Docker 容器資料庫執行驗證
- [ ] 2.2 實作 Repository 介面與適配器，於 Docker 容器內執行整合測試

### 階段三：應用層與 API 端點 (Application & API Layer in Docker)
- [ ] 3.1 實作 Application Service / UseCase 邏輯
- [ ] 3.2 串接 API Controller / Route 與輸入校驗 DTO
- [ ] 3.3 在 Docker 容器內執行 API 端對端（E2E）整合測試

### 階段四：架構門禁與驗收回歸 (Verification & Regression in Docker)
- [ ] 4.1 在 Docker 容器內執行靜態代碼檢查與 Linter 格式校驗
- [ ] 4.2 在 Docker 容器內執行完整回歸測試套件
- [ ] 4.3 規格歸檔與完成確認

