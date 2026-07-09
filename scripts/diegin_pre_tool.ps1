# 迭进·DGEN PreToolUse 钩子 - 工具执行前预检
# 可返回 permissionDecision: "deny" 来阻止危险操作

$dieginHome = "C:\Users\Administrator\.codex"
$auditLog = Join-Path $dieginHome "diegin_audit.log"
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"

$rawInput = [Console]::In.ReadLine()
if ([string]::IsNullOrWhiteSpace($rawInput)) {
    exit 0
}

try {
    $ctx = $rawInput | ConvertFrom-Json -ErrorAction Stop
    $tool = if ($ctx.tool_name) { $ctx.tool_name } else { "unknown" }
    "$time [HOOK:PreToolUse] OK | tool=$tool" | Add-Content -Path $auditLog
} catch {
    "$time [HOOK:PreToolUse] ERR | $_" | Add-Content -Path $auditLog
}
exit 0
