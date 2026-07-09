# 迭进·DGEN PostToolUse 钩子 - 工具执行后迭进预检

$dieginHome = "C:\Users\Administrator\.codex"
$auditLog = Join-Path $dieginHome "diegin_audit.log"
$stateFile = Join-Path $dieginHome "diegin_state.json"
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"

$rawInput = [Console]::In.ReadLine()
if ([string]::IsNullOrWhiteSpace($rawInput)) {
    exit 0
}

try {
    $ctx = $rawInput | ConvertFrom-Json -ErrorAction Stop
    $tool = if ($ctx.tool_name) { $ctx.tool_name } else { "unknown" }
    "$time [HOOK:PostToolUse] OK | tool=$tool" | Add-Content -Path $auditLog
} catch {
    "$time [HOOK:PostToolUse] ERR | $_" | Add-Content -Path $auditLog
}
exit 0
