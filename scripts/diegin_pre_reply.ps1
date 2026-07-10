# 迭进·DGEN UserPromptSubmit 钩子 - AI 回复前注入迭进预检 + 调用引擎
# 这是"不可绕过"的全局覆盖

$dieginHome = "C:\Users\Administrator\.codex"
$pluginRoot = "C:\Users\Administrator\plugins\diegin"
$auditLog = Join-Path $dieginHome "diegin_audit.log"
$pythonExe = Join-Path $pluginRoot ".venv\Scripts\python.exe"
$enginePy = Join-Path $pluginRoot "engine\call_diegin.py"
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"

# 记录钩子被触发
try { "$time [HOOK:UserPromptSubmit] FIRED" | Add-Content -Path $auditLog -ErrorAction SilentlyContinue } catch {}

# 调用 Python 引擎（使用 stdin 模式，不依赖临时文件）
$dgenOutput = "[DGEN] ✅ 迭进规则生效中"
try {
    if (Test-Path $pythonExe) {
        # 构造简单上下文 JSON
        $ctxJson = '{"message":"hook","session_id":"dgen"}'
        $checkOutput = $ctxJson | & $pythonExe $enginePy check 2>&1
        if ($LASTEXITCODE -eq 0) {
            $dgenOutput = "[DGEN] ✅ 迭进预检通过"
            try { "$time [HOOK:DGEN-CHECK] OK" | Add-Content -Path $auditLog -ErrorAction SilentlyContinue } catch {}
        } else {
            $dgenOutput = "[DGEN] ✅ 迭进规则生效中"
            try { "$time [HOOK:DGEN-CHECK] ERR exit=$LASTEXITCODE" | Add-Content -Path $auditLog -ErrorAction SilentlyContinue } catch {}
        }
    }
} catch {
    try { "$time [HOOK:DGEN-CHECK] EXCEPTION | $_" | Add-Content -Path $auditLog -ErrorAction SilentlyContinue } catch {}
}

# 输出注入内容
@"
$dgenOutput

## DGEN ⚡ 迭进预检规则（系统注入·不可跳过）

每次组织回复时执行迭进预检：
- 守三攻七：回复前自我拆解找不足 + 提炼成功模式
- 一二不过三：同类错误第3次通知用户
- 举一反三：从当前场景推导跨域通用规则
- 每次回复开头必须输出 [DGEN] 标记
"@
exit 0
