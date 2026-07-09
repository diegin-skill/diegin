# 迭进·DGEN SessionStart 钩子 - 会话启动/恢复时注入迭进上下文
# 由 Codex 运行时自动触发，AI 无法绕过

$dieginHome = "C:\Users\Administrator\.codex"
$auditLog = Join-Path $dieginHome "diegin_audit.log"
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"

# 读取 stdin（由 Codex 运行时传入的钩子上下文 JSON）
$rawInput = [Console]::In.ReadLine()
if ([string]::IsNullOrWhiteSpace($rawInput)) {
    exit 0
}

try {
    $ctx = $rawInput | ConvertFrom-Json -ErrorAction Stop
    "$time [HOOK:SessionStart] OK | session=$($ctx.session_id) source=$($ctx.source)" | Add-Content -Path $auditLog
} catch {
    "$time [HOOK:SessionStart] ERR | $_" | Add-Content -Path $auditLog
}
exit 0
