---
description: "階段二工作流：QA 與 PG 職責分離之 Docker 隔離 TDD 實施循環 (Red-Green-Refactor)"
---

# 階段二工作流：測試驅動與實現循環 (QA & PG TDD Cycle)

本工作流由主調度中心自主派遣 **`qa` (測試工程師)** 與 **`pg` (研發工程師)** 嚴格物理分離執行，杜絕球員兼裁判，且所有命令必須在 Docker 容器內運行。

---

## 步驟 1：Docker 隔離環境就緒檢查 (Hard Stop Gate)
1. 檢查目前專案 Docker 容器是否已啟動（如 `docker compose ps`）。
2. **【物理終止律】**：若 Docker 容器未就緒，任何角色必須立即停止執行（STOP）並提示使用者啟動容器，嚴禁在宿主機直接運行！

---

## 步驟 2：QA 紅燈測試編寫與驗證 (Red Phase)
1. 主調度中心自主派遣 **`qa`** 檢閱 `docs/02-architecture-sdd/<module-name>/` 與 `docs/03-tasks/<module-name>/`。
2. 編寫 BDD 驗收測試與極端邊界測試代碼（`tests/<module-name>/`）。
3. 在 Docker 容器內執行測試命令（如 `docker compose exec app <test-cmd>`）。
4. **確認紅燈**：驗證測試如期失敗（100% 變紅），且原因精準為「業務未實作」。
5. 落盤測試記錄：`docs/04-testing-qa/<module-name>/QA-YYYYMMDD-<name>.md`。
6. 自主回報調度中心紅燈確立。

---

## 步驟 3：PG 綠燈實作與任務勾選 (Green Phase)
1. 主調度中心自主派遣 **`pg`** 認領任務，在 Docker 容器內編寫領域實作代碼與基礎設施適配器（`src/<module-name>/`）。
2. 在 Docker 容器內執行測試，持續修訂實作直到測試**全數轉綠（100% 通過）**。
3. 執行 DDD 依賴倒置重構（消除壞味道，確保 Domain 零污染）。
4. 將 `docs/03-tasks/<module-name>/` 中對應的任務 Checkbox 更新為 `[x]`。
5. 提交 Git Commit（如 `git commit -m "feat(module): implement core domain and green tests"`）。

---

## 步驟 4：自主交接代碼審查
1. 確保所有測試在 Docker 容器內無 Warning、無 Error 通過。
2. PG 整理代碼變更清單，自主通知主調度中心啟動階段三（`code-reviewer` 唯審查門禁）。

