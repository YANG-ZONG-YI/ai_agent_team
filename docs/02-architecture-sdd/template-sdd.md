# 軟體設計規格書 (SDD): [模組/系統名稱]

- **文件編號**: SDD-YYYYMMDD-[name]
- **對應需求編號**: REQ-YYYYMMDD-[name] / ISSUE-* / DEBT-*
- **負責架構師**: SA Agent
- **架構風格**: 領域驅動設計 (DDD) + 依賴倒置 (DIP) + Docker 容器隔離

---

## 1. DDD 領域模型與邊界劃分 (Domain Design)
### 1.1 限界上下文與防腐層 (Bounded Context & ACL)
- **核心域**: [核心業務邏輯描述]
- **支撐域 / 通用域**: [外部系統與支撐服務]
- **防腐層 (ACL) 適配器**: [與第三方服務或舊系統轉接方式]

### 1.2 聚合根、實體與值對象 (Aggregates & Value Objects)
- **聚合根 (Aggregate Root)**: `[AggregateName]` (唯一狀態變更入口)
  - **實體 (Entities)**:
  - **值對象 (Value Objects)**:
  - **領域事件 (Domain Events)**:

---

## 2. Docker 隔離環境拓撲 (Docker Topology)
- **基礎映像檔**: `[base-image:tag]` (非 root 運行)
- **Compose 服務定義**:
  - `app`: 應用伺服器
  - `db`: 資料庫
  - `cache`: 快取 (Redis)
- **Volume 映射與環境變數**:

---

## 3. 介面契約規格 (API Contracts)
- **協定類型**: RESTful (JSON) / gRPC
- **端點**: `POST /api/v1/[resource]`
  - **Request Body (JSON Schema)**:
  - **Response 200 (Success)**:
  - **Response 4xx/5xx (Error with ErrorCode & TraceId)**:

---

## 4. 資料庫設計 (3NF DDL Schema)
```sql
-- DDL 腳本 (符合 3NF、外鍵與索引)
CREATE TABLE [table_name] (
    id VARCHAR(36) PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. 極限異常與非功能架構 (NFRs & Edge Cases)
- **併發控制**: [樂觀鎖 / 分散式鎖]
- **重試與冪等**: [Idempotency-Key]
- **逾時與降級熔斷**:
