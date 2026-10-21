---
description: "階段三工作流：Code-Reviewer 唯審查門禁簽核、Ops 映像檔安全/雙探針驗證、5分鐘回滾 Runbook 與版本發布 (Git Tag)"
---

# 階段三工作流：審查門禁與維運發布 (Review & Ops Release)

本工作流由主調度中心自主派遣 **`code-reviewer` (高階審查員)** 與 **`ops` (維運工程師)** 協同執行，落實物理唯讀審查、一票否決與生產零停機回滾保證。

---

## 步驟 1：Code-Reviewer 唯審查門禁 (Review Gate)
1. 主調度中心自主派遣 **`code-reviewer`** 啟動 6 大維度審查（**物理級沒收改碼工具，嚴禁修改任何代碼**）：
   - DDD 領域純粹性與 DIP 依賴倒置
   - Docker 隔離環境與宿主零污染
   - 測試真實性與極端邊界覆蓋
   - Clean Code 設計模式與無代碼壞味道
   - OWASP 資安漏洞（注入、越權、金鑰洩漏）
   - 維運可觀測性（結構化日誌、TraceId、指標埋點）
2. 產出審查報告至：`docs/05-reviews/<module-name>/review-YYYYMMDD-<name>.md`。
3. **裁決判定**：
   - 若為 `REQUEST_CHANGES`：自主駁回給 `pg` 修訂，重新進入審查。
   - 若為 `APPROVED`：簽署放行，主調度中心自主派遣 `ops`。

---

## 步驟 2：Ops 發布前安全與雙探針檢驗
1. 主調度中心自主派遣 **`ops`** 檢核 Dockerfile 映像檔安全性（非 Root 運行、最小攻擊面）。
2. 驗證服務 `/health/liveness` 與 `/health/readiness` 探針連通性。
3. 檢核資料庫 DDL 遷移腳本是否符合 Expand-Contract（嚴禁破壞性直接刪欄位）。

---

## 步驟 3：5 分鐘一鍵回滾 Runbook 落盤
1. **`ops`** 編寫緊急事故應變手冊：`docs/06-ops/<module-name>/RUNBOOK-YYYYMMDD-<name>.md`。
2. 載明：一鍵鏡像降級指令、DB Rollback 腳本、降級熔斷開關。

---

## 步驟 4：版本控制發布與 Git Tag
1. 產出發布清單：`docs/06-ops/<module-name>/RELEASE-YYYYMMDD-<version>.md`。
2. 標記生產版本 Git Tag（例：`v1.0.0`），發布 Release Note。
3. 主調度中心完成全生命週期閉環，正式向使用者匯報交付成果！

