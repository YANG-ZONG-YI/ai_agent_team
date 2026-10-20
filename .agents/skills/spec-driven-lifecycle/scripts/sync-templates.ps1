# 同步模板至專案 docs/ 目錄
New-Item -ItemType Directory -Force -Path "docs/proposals", "docs/sdd", "docs/tasks" | Out-Null

Copy-Item -Path ".agents/skills/spec-driven-lifecycle/templates/proposal-template.md" -Destination "docs/proposals/proposal-template.md" -Force
Copy-Item -Path ".agents/skills/spec-driven-lifecycle/templates/sdd-template.md" -Destination "docs/sdd/sdd-template.md" -Force
Copy-Item -Path ".agents/skills/spec-driven-lifecycle/templates/tasks-template.md" -Destination "docs/tasks/tasks-template.md" -Force

Write-Host "已成功同步規格標準模板至 docs/proposals/, docs/sdd/, docs/tasks/！" -ForegroundColor Green
