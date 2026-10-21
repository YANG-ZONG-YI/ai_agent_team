# 維運 5 分鐘回滾與故障應急手冊 (5-Minute Rollback Runbook)
## 模組名稱：tech-debt-refactor (自動化影音管線)

---

### 1. 雙探針健康檢查驗證 (Health Check Probes)
- **存活探針 (Liveness)**：
  ```bash
  curl -f http://localhost:8008/healthz
  # 預期返回: {"status":"healthy","service":"video-automation-pipeline","storage":"mounted"}
  ```

---

### 2. 5 分鐘一鍵平滑降級回滾 (Strangler Switch Fallback)
若生產環境發生任何不可預期之管線異常，可直接切換絞殺者功能旗標，零停機秒級回退至原舊版管線：

#### 手法 A：動態環境變數切換 (無須重新編譯鏡像，耗時 < 1 分鐘)
1. 在 `.env` 或 `docker-compose.yml` 中將管線開關設為 `false`：
   ```env
   FEATURE_MODULAR_PIPELINE=false
   ```
2. 重新加載 worker 服務：
   ```bash
   docker compose restart worker app
   ```
3. 驗證服務：
   系統將自動降級至 `_legacy_run_video_pipeline_sync`，管線產物與 Notion 回填維持原樣運作。

#### 手法 B：Git 分支與 Docker 鏡像秒級回滾 (耗時 < 3 分鐘)
1. 回退代碼至重構前 Tag：
   ```bash
   git checkout main
   docker compose up -d --build
   ```

---

### 3. 可觀測性與日誌排查指南
所有日誌均輸出標準結構化 JSON：
```bash
docker compose logs -f app | jq '{timestamp, level, trace_id, message}'
docker compose logs -f worker | jq '{timestamp, level, trace_id, message}'
```
若需定位特定作業失敗，可在日誌中直接過濾 `job_id` 或 `trace_id`。
