# 系統維運手冊與應急運維 Runbook (Operations Runbook)

> **系統名稱**: [系統/服務名稱]  
> **維護人員**: 系統架構師與維運小組  
> **關聯 SDD**: [sdd-XXXXX.md](../sdd/sdd-XXXXX.md)  
> **生效版本**: v1.0.0  

---

## 1. 服務拓撲與容器健康狀態 (Service Topology & Probes)

### 容器與服務組件
- **核心容器**: `app` (Docker Compose / K8s Pod)
- **資料庫容器**: `postgres` (Port: 5432)
- **快取容器**: `redis` (Port: 6379)

### 健康檢查雙探針 (Health Probes)
- **存活探針 (Liveness)**: `GET /health/liveness` (返回 200 表示 Process 存活)
- **就緒探針 (Readiness)**: `GET /health/readiness` (檢測 DB/Redis 連線池，返回 200 表示可接收流量)

---

## 2. 三位一體可觀測性指標 (Observability & SLOs)

### 關鍵度量指標 (Golden Signals)
- **延遲 (Latency)**: API P99 < 200ms, P95 < 100ms
- **流量 (Traffic)**: 正常峰值 QPS [數值]，限流閥值 [數值]
- **錯誤率 (Errors)**: HTTP 5xx 比例 < 0.1%
- **飽和度 (Saturation)**: 容器 CPU 使用率 < 70%，記憶體使用率 < 75%

### 告警與通知規則
- **P1 嚴重告警 (SMS/語音即時通知)**: 服務連續 1 分鐘 5xx 錯誤率 > 2% 或 DB 連線斷開。
- **P2 次要告警 (Slack/Webhook 通知)**: P99 延遲連續 5 分鐘超標或磁碟空間低於 20%。

---

## 3. 日常維運與備份策略 (Routine Ops & Backup)

- **自動化備份**: 每日 03:00 UTC 執行全量 DB 邏輯備份，保留 30 天。
- **日誌輪轉**: 應用程式日誌採用 JSON 結構化輸出，容器日誌單檔上限 100MB，保留 5 份。
- **資料庫遷移策略**: 採用 Expand-Contract 零停機向前相容模式，嚴禁執行破壞性直接刪欄位腳本。

---

## 4. 事故應急響應與零停機回滾 (Incident Response & Rollback)

### 一鍵緊急回滾標準程序 (Emergency Rollback)
1. **容器映像回滾**:
   ```bash
   # 切換至穩定前一版本映像
   docker compose down app
   IMAGE_TAG=v-previous docker compose up -d app
   ```
2. **資料庫遷移向下回滾**:
   ```bash
   # 透過 Docker 容器執行向後相容遷移
   docker compose exec app python -m alembic downgrade -1
   ```
3. **健康檢查確認**:
   確認 `curl -f http://localhost:8000/health/readiness` 回傳狀態碼 200。

### 降級與熔斷應急手冊 (Degradation & Fallbacks)
- **第三方服務故障**: 自動觸發防腐層 (ACL) 熔斷機制，返回降級快取資料或異步佇列重試。
- **高流量高峰過載**: 開啟全域限流 (Rate Limiter)，優先保障核心交易鏈路。
