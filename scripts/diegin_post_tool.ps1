$dieginHome = "C:\Users\Administrator\.codex"
$auditLog = Join-Path $dieginHome "diegin_audit.log"
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
try { "$time [HOOK:PostToolUse] ACTIVE" | Add-Content -Path $auditLog -ErrorAction SilentlyContinue } catch {}
exit 0
