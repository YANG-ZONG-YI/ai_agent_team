# 系統維運手冊與 5 分鐘回滾方案 (Ops Runbook): [模組/版本]

- **文件編號**: RUNBOOK-YYYYMMDD-[name]
- **版本標籤**: vX.Y.Z
- **負責維運**: Ops Agent
- **SLA 承諾**: 5 分鐘內完成一鍵回滾降級

---

## 1. 部署前安全與健康探針檢核
- [ ] **Docker 映像檔檢核**: 非 root 運行、無高危漏洞。
- [ ] **雙探針檢測**:
  - `curl -f http://localhost:8080/health/liveness` ➔ HTTP 200
  - `curl -f http://localhost:8080/health/readiness` ➔ HTTP 200 (DB & Redis 連線就緒)
- [ ] **資料庫向後相容檢核**: 遵循 Expand-Contract 模式，無破壞性 DDL。

---

## 2. 5 分鐘一鍵回滾程序 (Emergency Rollback)
當線上監控警報觸發（錯誤率 > 1% 或 P99 > 1s）時，立即執行以下命令：

### 步驟 1: 容器映像檔一鍵回退至上一穩定版本
```bash
# 回退應用程式容器映像檔
docker compose stop app
docker compose up -d --no-deps app:v[PREVIOUS_VERSION]
```

### 步驟 2: 資料庫向前相容降級腳本 (若有 DDL 異動)
```bash
# 執行向下相容回退腳本
docker compose exec db psql -U [user] -d [dbname] -f /migrations/rollback.sql
```

### 步驟 3: 降級開關切換 (Feature Flag)
```bash
# 透過 API 關閉新功能開關
curl -X POST http://localhost:8080/admin/features/[feature-key]/disable
```

---

## 3. 發布清單與變更日誌 (Release Changelog)
- **Git Tag**: `vX.Y.Z`
- **變更項目**:
  - [feat]: ...
  - [fix]: ...
- **驗收負責人**: Ops & QA
