# 迭进·DGEN — AI 全域常驻自我迭代进化系统

> 场景无关 · 开箱即用 · 可随需扩展

---

## 一句话

**迭进是 AI Agent 的操作系统级进化层。** 每次回复前自动预检—拦截错误—强化成功—自主进化。不绑定模型、平台或业务场景。

---

## 核心四原则

| 守三 | 攻七 | 一二不过三 | 举一反三 |
|:---|:---|:---|:---|
| 负向纠错 | 正向强化 | 第 3 次通知用户 | 跨域泛化 |

---

## 快速开始

### 方式 A：纯 Markdown（推荐 · 零依赖 · 30 秒生效）

告诉你的 AI：

```
请读取 SKILL.md，之后所有回复执行迭进预检，输出 [DGEN] 标记。
```

适用于 **Codex / Claude / ChatGPT / 任何 AI Agent**。

### 方式 B：Python 引擎

```bash
cd engine && uv run python call_diegin.py activate
uv run python call_diegin.py check   # 每次回复前
```

### 方式 C：自动化引擎

```bash
python scripts/dgen_evolve.py   # 创建健康度基线，开始自动闭环
```

---

## 自动化闭环

迭进不是"手动定规则"，而是自动进化：

```
dgen_evolve.py → 自动观察 → 自动提议 → 用户确认 → 写入规则 → trail 归档
```

首次启动：
```bash
python scripts/dgen_evolve.py
```

---

## 添加新领域

在 `engine/evo/rules/domain_rules/` 下创建 JSON 文件，引擎自动发现。

---

## 目录

```
diegin-skill/
├── SKILL.md               ⭐ 核心技能定义
├── README.md              本文件
├── engine/                Python 迭进引擎
│   └── evo/rules/
│       ├── interception_rules.json  10 条系统级规则
│       ├── success_patterns.json     6 条系统级模式
│       └── domain_rules/            你的领域规则包
├── scripts/               自动化引擎
├── workspace/             运行时模板
├── plugin/                OpenClaw 插件
└── config/                配置文档
```

---

## 许可

MIT — 自由使用、修改、分发。