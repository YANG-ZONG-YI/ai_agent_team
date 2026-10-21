# 品質驗收與測試報告 (QA Report): [模組/功能名稱]

- **文件編號**: TEST-YYYYMMDD-[name]
- **對應規格**: SDD-YYYYMMDD-[name] / TASKS-YYYYMMDD-[name]
- **負責 QA**: QA Agent
- **執行環境**: Docker 容器內隔離執行 (`docker compose exec ...`)

---

## 1. 測試案例矩陣 (BDD Test Matrix)
| 案例編號 | 測試層級 (單元/整合/E2E) | 測試場景描述 (Given-When-Then) | 預期結果 |
| :--- | :--- | :--- | :--- |
| TC-01 | Unit | 聚合根狀態變更業務不變量校驗 | 違反規則時丟出 DomainException |
| TC-02 | Integration | 併發競態條件驗證 (樂觀鎖) | 衝突時僅一筆成功，其餘優雅重試 |
| TC-03 | E2E / API | 完整 API 呼叫鏈 (含 TraceId) | 回傳 HTTP 200 與標準 JSON |

---

## 2. 紅燈先行驗證記錄 (Red Phase Log)
- **執行時間**: YYYY-MM-DD HH:MM:SS
- **執行命令**: `docker compose exec app <test-cmd>`
- **變紅狀態**: PASS (確定 100% 變紅)
- **失敗日誌摘要**:
```text
[貼上測試如期失敗的錯誤輸出，證明業務未實作，杜絕假綠燈]
```

---

## 3. 綠燈全數通過確認 (Green Phase Sign-off)
- **執行時間**: YYYY-MM-DD HH:MM:SS
- **執行結果**: 100% 通過 (0 Failed, 0 Skipped, 0 Errors)
- **測試覆蓋率**: 分支覆蓋率 > 85%, 核心領域模型覆蓋率 100%
