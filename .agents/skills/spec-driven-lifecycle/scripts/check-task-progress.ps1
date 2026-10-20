param (
    [string]$TaskFile = ""
)

if (-not $TaskFile) {
    # 自動尋找最新的 tasks 檔案
    $files = Get-ChildItem -Path "docs/tasks" -Filter "*.md" | Where-Object { $_.Name -notmatch "template" } | Sort-Object LastWriteTime -Descending
    if ($files.Count -eq 0) {
        Write-Host "尚未發現進行中的任務清單檔案（位於 docs/tasks/）。" -ForegroundColor Yellow
        exit 0
    }
    $TaskFile = $files[0].FullName
}

if (-not (Test-Path $TaskFile)) {
    Write-Error "找不到任務清單檔案: $TaskFile"
    exit 1
}

$lines = Get-Content -Path $TaskFile
$totalTasks = 0
$completedTasks = 0
$nextPendingTask = $null

foreach ($line in $lines) {
    if ($line -match "^\s*-\s*\[x\]\s*(.+)$") {
        $totalTasks++
        $completedTasks++
    } elseif ($line -match "^\s*-\s*\[\s\]\s*(.+)$") {
        $totalTasks++
        if (-not $nextPendingTask) {
            $nextPendingTask = $matches[1]
        }
    }
}

$percent = if ($totalTasks -gt 0) { [math]::Round(($completedTasks / $totalTasks) * 100, 1) } else { 0 }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "【規格驅動進度報告】: $(Split-Path $TaskFile -Leaf)" -ForegroundColor Cyan
Write-Host "總計任務: $totalTasks | 已完成: $completedTasks | 未完成: $($totalTasks - $completedTasks)" -ForegroundColor White
Write-Host "當前進度: $percent %" -ForegroundColor Green
if ($nextPendingTask) {
    Write-Host "下一個待辦任務 ➔ $nextPendingTask" -ForegroundColor Yellow
} else {
    Write-Host "恭喜！該清單中所有任務已全數完成！" -ForegroundColor Green
}
Write-Host "========================================" -ForegroundColor Cyan
