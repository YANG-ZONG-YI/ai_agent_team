# 線上問題排查與根因分析單 (Issue RCA): [問題摘要]

- **文件編號**: ISSUE-YYYYMMDD-[name]
- **需求類型**: 【線上問題 / Bug 故障】
- **負責 PM**: PM Agent
- **嚴重等級**: P0 (致命阻斷) / P1 (重大異常) / P2 (一般瑕疵)

---

## 1. 異常現象與預期行為
- **異常現象 (Actual Behavior)**: [具體錯誤描述]
- **預期行為 (Expected Behavior)**: [正確的業務行為]
- **重現頻率**: 100% 必現 / 偶發 (頻率約 __%)

---

## 2. 證據鏈 (Evidence Chain)
- **觸發環境**: Production / Staging
- **關聯 TraceId / RequestId**: [如: `req-9f8a2c1...`]
- **錯誤堆疊 (Error Stack / Logs)**:
```text
[貼上錯誤日誌與關鍵調用鏈]
```

---

## 3. 根本原因分析 (Root Cause Analysis - RCA)
- **根本原因**: [為何會發生？代碼邏輯缺陷？併發競態？網路分區？]
- **影響半徑 (Blast Radius)**:
  - 受影響之聚合根 / 資料表:
  - 受影響之使用者範疇:

---

## 4. 處置與防禦方案
- **短期止血 (Hotfix/Workaround)**: [是否需要降級或配置回退]
- **根本修復 (Fix & Regression Prevention)**: [QA 需補充的反回歸測試案例]
