# 迭进·DGEN Stop 钩子 - 轮次结束时生成合规报告

$dieginHome = "C:\Users\Administrator\.codex"
$auditLog = Join-Path $dieginHome "diegin_audit.log"
$reportFile = Join-Path $dieginHome "diegen_compliance.json"
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"

# 读取审计日志统计本次会话数据
$violations = 0
$hookCalls = 0
if (Test-Path $auditLog) {
    $lines = Get-Content $auditLog
    $sessionLines = $lines[-50..-1]
    $violations = ($sessionLines | Where-Object { $_ -match 'BLOCKED' }).Count
    $hookCalls = ($sessionLines | Where-Object { $_ -match '\[HOOK\]' }).Count
}

$report = @{
    session_end = $time
    date = Get-Date -Format "yyyy-MM-dd"
    hook_calls = $hookCalls
    violations = $violations
    compliance_rate = if ($hookCalls -gt 0) { [Math]::Round(($hookCalls - $violations) / $hookCalls * 100, 1) } else { 100 }
    status = if ($violations -eq 0) { "clean" } elseif ($violations -le 2) { "warning" } else { "violation" }
}

$report | ConvertTo-Json -Compress | Out-File -FilePath $reportFile -Encoding UTF8 -Force

if ($violations -gt 0) {
    "$time [HOOK:STOP] 违规 $violations 次 | 合规率 $($report.compliance_rate)%" | Add-Content -Path $auditLog
}
exit 0
