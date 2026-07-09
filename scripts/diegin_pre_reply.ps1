# 迭进·DGEN UserPromptSubmit 钩子 - AI 回复前注入迭进上下文
# 标准输出内容会被 Codex 自动添加为 extra developer context
# 这是"不可绕过"的全局覆盖：每次用户提问，迭进指令自动注入

$dieginHome = "C:\Users\Administrator\.codex"
$auditLog = Join-Path $dieginHome "diegin_audit.log"
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"

# 读取 stdin（用户提交的消息上下文）
$rawInput = [Console]::In.ReadLine()
if ([string]::IsNullOrWhiteSpace($rawInput)) {
    exit 0
}

try {
    $ctx = $rawInput | ConvertFrom-Json -ErrorAction Stop
    "$time [HOOK:UserPromptSubmit] OK" | Add-Content -Path $auditLog
    
    # ===== 输出迭进注入内容 =====
    # 这些文本会作为 extra developer context 自动添加到 AI 的上下文中
    # AI 无法跳过或忽略，因为钩子在 AI 处理之前就注入了
@"
[DGEN] 迭进·DGEN 引擎注入 - 全域常驻强制生效
- 守三攻七：回复前自我拆解找不足+提炼成功模式
- 一二不过三：同类错误第3次通知用户
- 举一反三：从当前场景推导跨域通用规则
- 每次回复开头必须输出 [DGEN] 标记
"@
} catch {
    "$time [HOOK:UserPromptSubmit] ERR | $_" | Add-Content -Path $auditLog
}
exit 0
