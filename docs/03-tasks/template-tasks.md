# 原子實施任務清單 (Tasks): [模組/功能名稱]

- **文件編號**: TASKS-YYYYMMDD-[name]
- **對應規格**: SDD-YYYYMMDD-[name]
- **維護者**: SA / PG / QA
- **執行環境**: 強制 100% Docker 容器內隔離執行

---

## 任務執行與斷點追蹤 (Task Matrix)

### 階段一：Docker 容器環境就緒 (由 QA / PG 驗證)
- [ ] **Task 1.1**: 確認 Dockerfile 與 docker-compose 服務正常啟動 (`docker compose ps`)。
- [ ] **Task 1.2**: 確認容器內部依賴安裝無誤，非 Docker 宿主機嚴禁執行。

### 階段二：QA 紅燈測試先行 (由 QA 執行)
- [ ] **Task 2.1**: 依據 SDD 編寫 BDD 驗收測試案例。
- [ ] **Task 2.2**: 編寫極限邊界測試（併發、逾時、冪等性、回滾）。
- [ ] **Task 2.3**: 在 Docker 容器內運行測試，驗證 100% 變紅（Red Phase），記錄於 `docs/04-testing-qa/`。

### 階段三：PG 綠燈實作與重構 (由 PG 執行)
- [ ] **Task 3.1**: 實現 Domain Layer 純粹實體與值對象（無外部污染）。
- [ ] **Task 3.2**: 實現 Application Layer 服務與介面。
- [ ] **Task 3.3**: 實現 Infrastructure Layer 介面適配器與 Repository。
- [ ] **Task 3.4**: 在 Docker 容器內執行測試，驗證全數轉綠（Green Phase）。
- [ ] **Task 3.5**: 進行依賴倒置重構（Refactor）與壞味道清理。

### 階段四：代碼審查與發布門禁 (由 Reviewer & Ops 執行)
- [ ] **Task 4.1**: 提交 `code-reviewer` 進行 6 大維度唯審查門禁，取得 `APPROVED`。
- [ ] **Task 4.2**: 由 `ops` 審查映像檔、健康雙探針、向前相容遷移與回滾 Runbook。
- [ ] **Task 4.3**: 標記 Git Tag 並發布 Release Note。
