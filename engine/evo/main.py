#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

diegin-evo 统一入口模块

迭进自主生成和维护

"""



import os

import sys

import json

from pathlib import Path

from typing import Dict, List, Any, Optional



sys.path.insert(0, str(Path(__file__).parent))





from rule_engine import (

    RuleEngine,

    InterceptionRule,

    SuccessPattern,

    MetaExperience,

    Precedent,

    get_seed_interceptions,

    init_rules_if_empty

)

from arbiter import ConflictArbiter, ResolutionType, ArbitrationResult

from reviewer import Reviewer, ROIReviewer, ReviewSignal, ReviewResult

from tracker import BehaviorTracker

from war_game import WarGameEngine

from dashboard import HealthDashboard, run_health_check





# ============================================================

# MemPalace 适配层（迭进 ↔ 长期记忆）

# ============================================================



_MEMPALACE_AVAILABLE = False

_MP_SCRIPT = None

_MP_PYTHON = None

_MP_BASE = os.environ.get('MEMPALACE_DIR', os.environ.get('OPENCLAW_HOME', ''))

if _MP_BASE:

    _MP_SCRIPT = Path(_MP_BASE) / 'skills' / 'mempalace-openclaw' / 'scripts' / 'archive.py'

    _MP_PYTHON = Path(_MP_BASE) / 'skills' / 'mempalace-openclaw' / '.venv' / 'Scripts' / 'python.exe'

else:

    # fallback: try common locations

    for _candidate in [

        Path.home() / '.openclaw-迭进',

        Path.home() / '.openclaw',

    ]:

        _mp_script = _candidate / 'skills' / 'mempalace-openclaw' / 'scripts' / 'archive.py'

        _mp_python = _candidate / 'skills' / 'mempalace-openclaw' / '.venv' / 'Scripts' / 'python.exe'

        if _mp_script.exists() and _mp_python.exists():

            _MP_SCRIPT = _mp_script

            _MP_PYTHON = _mp_python

            break

try:

    if _MP_SCRIPT and _MP_PYTHON and _MP_SCRIPT.exists() and _MP_PYTHON.exists():

        _MEMPALACE_AVAILABLE = True

except Exception:

    pass









# ???????????????????????????????????????????????????????????????????
# ?????? ? ???????????????? ????
# ???????????????????????????????????????????????????????????????????
# ????????????????????????
#
# ?????????????????????
# ????????????????????
# ???????????????3???
# ???????????????????
# ???????????????????????????????????????????????????????????????????

import datetime

try:
    from error_detector import ErrorDetector, get as get_detector
    _detector = ErrorDetector()
    
    # ???? tracker?????
    try:
        _tk = None
        _detector._tracker = _tk
    except Exception:
        pass
    
    _detector_active = True
except Exception:
    _detector = None
    _detector_active = False


# ??? ??????????? ???????????????????????????????
def detect_failure(ctx: dict) -> dict:
    """
    ?????????
    ???????????????????????
    ctx = {
        "op": "file_write" | "cmd" | "git_push",
        "path": "...",           # file path (for file_write)
        "data": b"...",          # written content (for file_write)
        "cmd": "...",            # command (for cmd/git_push)
        "exit": 0,               # exit code
        "out": "...",            # stdout
        "err": "...",            # stderr
        "dur": 1234              # duration ms
    }
    ????????dict??????
    """
    if not _detector_active or _detector is None:
        return {}
    return _detector.detect_and_record(ctx) or {}


# ??? ??????????? ???????????????????????????????
_success_log = []   # [(timestamp, context), ...]


def detect_success(ctx: dict) -> dict:
    """
    ?????????
    ??????????????????????????
    ctx = {
        "op": "file_write" | "cmd" | "git_push" | ...,
        "detail": "...",         # ????
        "duration_ms": 1234,     # ????=??
        "retry_count": 0,        # ??????=??
        "result": {...},         # ????
    }
    """
    global _success_log
    
    if not _detector_active:
        return {}
    
    score = 0
    reasons = []
    
    # ??????
    dur = ctx.get("duration_ms", 0)
    if dur > 0 and dur < 10000:
        score += 1
        reasons.append("fast")
    
    # ?????
    retry = ctx.get("retry_count", 0)
    if retry == 0:
        score += 1
        reasons.append("no_retry")
    
    # ???????????
    op = ctx.get("op", "")
    if op in ("git_push", "release", "file_write"):
        if retry == 0 and dur < 60000:
            score += 2
            reasons.append("complex_ops_success")
    
    if score >= 2:
        entry = {
            "time": datetime.datetime.now().isoformat(),
            "op": op,
            "detail": ctx.get("detail", "")[:80],
            "score": score,
            "reasons": reasons
        }
        _success_log.append(entry)
        
        # ?????????????
        if score >= 3:
            try:
                if True:  # lazy import
                    try:
                        from main import _get_tracker as _gt
                        tracker = _gt()
                    except:
                        tracker = None
                if tracker:
                    # ????????????????????
                    pattern_id = f"auto_success_{op}_{len(_success_log)}"
                    detail = f"op={op} score={score} reasons={','.join(reasons)}"
                    # ?????????????????????
                    pattern_key = f"success_pattern_{op}"
                    # ?????????????????? success_pattern ??
                    pass
            except Exception:
                pass
        
        return {"detected": True, "score": score, "reasons": reasons}
    
    return {"detected": False}


# ??? ?????????? ?????????????????????????????????
def ensure_three_strikes(error_type: str, detail: str = "", severity: str = "high") -> dict:
    """
    ????????????
    ??????????????????????
    ????? detect_failure ??????
    
    ??:
        ensure_three_strikes("encoding_write_corruption", "PowerShell??????")
    """
    if not _detector_active or _detector is None:
        return {}
    return _detector.detect_and_record({
        "op": "file_write",
        "path": "",
        "data": b"",
        "force_error": error_type,
        "force_detail": detail
    }) or {}


def get_strike_status(error_type: str = None) -> dict:
    """??????????"""
    try:
        try:
            from main import _get_tracker as _gt
            tracker = _gt()
        except:
            tracker = None
        if tracker is None:
            return {"status": "tracker_not_available"}
        if error_type:
            rule = tracker.rule_engine.get_interception_by_id(f"self_error_{error_type}")
            if rule:
                return {
                    "error_type": error_type,
                    "triggered_count": getattr(rule, "triggered_count", 0),
                    "severity": getattr(rule, "severity", "unknown"),
                    "confidence": getattr(rule, "confidence", 0),
                    "lifecycle": getattr(rule, "lifecycle_status", "unknown")
                }
            return {"error_type": error_type, "status": "never_triggered"}
        # ???????????
        rules = tracker.rule_engine.get_interceptions(active_only=False)
        strikes = []
        for r in rules:
            if getattr(r, "triggered_count", 0) > 0:
                strikes.append({
                    "id": getattr(r, "id", ""),
                    "triggered": getattr(r, "triggered_count", 0),
                    "severity": getattr(r, "severity", ""),
                    "lifecycle": getattr(r, "lifecycle_status", "")
                })
        return {"status": "ok", "strike_rules": strikes}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ??? ????????? ???????????????????????????????????
_last_generalization_check = None

def generalize_rule(new_rule_id: str = None) -> list:
    """
    ??????????????????????
    
    ???
    1. ?????? severity + category
    2. ???????? severity ???
    3. ????????????????????
    4. ????????
    """
    global _last_generalization_check
    
    try:
        try:
            from main import _get_tracker as _gt
            tracker = _gt()
        except:
            tracker = None
        if tracker is None:
            return []
        
        rules = tracker.rule_engine.get_interceptions(active_only=False)
        
        # ? severity + category ??
        groups = {}
        for r in rules:
            cat = getattr(r, "category", "unknown") or "unknown"
            sev = getattr(r, "severity", "medium") or "medium"
            key = f"{sev}/{cat}"
            if key not in groups:
                groups[key] = []
            groups[key].append(getattr(r, "id", ""))
        
        # ?????????????????????
        all_cats = set()
        for key in groups:
            _, cat = key.split("/", 1)
            all_cats.add(cat)
        
        candidates = []
        for key, rule_ids in sorted(groups.items()):
            sev, cat = key.split("/", 1)
            if len(cat) < 2:
                continue
            # ??????? critical ?????????????????
            if sev == "critical":
                for other_cat in all_cats:
                    other_key = f"critical/{other_cat}"
                    if other_key not in groups:
                        # ?????? critical ?? ?
                        # ????? critical ????????
                        for rid in rule_ids[:2]:
                            candidates.append({
                                "source": rid,
                                "source_cat": cat,
                                "target_cat": other_cat,
                                "reason": f"{cat}?{sev}???{other_cat}???????",
                                "action": "review_and_adapt"
                            })
        
        _last_generalization_check = {
            "time": datetime.datetime.now().isoformat(),
            "candidates": candidates,
            "groups": {k: len(v) for k, v in groups.items()}
        }
        
        return candidates
    except Exception as e:
        return []


def get_generalization_status() -> dict:
    """?????????"""
    return {
        "last_check": _last_generalization_check,
        "detector_active": _detector_active,
        "success_log_count": len(_success_log)
    }


# ??? ???????? ????????????????????????????????????
def quad_health() -> dict:
    """?????????????"""
    return {
        "detector": {
            "active": _detector_active,
            "detections": len(_detector._log) if _detector and _detector_active else 0
        },
        "success": {
            "logged": len(_success_log)
        },
        "three_strikes": get_strike_status().get("strike_rules", []),
        "generalization": get_generalization_status()
    }


def mempalace_search(query: str, max_results: int = 5) -> List[Dict]:

    """从 MemPalace 检索历史记忆"""

    if not _MEMPALACE_AVAILABLE:

        return []

    try:

        import subprocess

        result = subprocess.run(

            [str(_MP_PYTHON), str(_MP_SCRIPT), "search", query, "semantic"],

            capture_output=True, text=True, timeout=30

        )

        if result.returncode != 0:

            return []

        lines = result.stdout.strip().split("\n")

        return [{"file": l} for l in lines if l]

    except Exception:

        return []





def dgen_archive(rule_id: str, decision: str, context: Dict):

    """迭进决策后自动归档到MemPalace"""

    from datetime import datetime

    content = f"""# [DGEN ⚡] 迭进决策记录

时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

规则: {rule_id}

决策: {decision}

上下文: {json.dumps(context, ensure_ascii=False)}

"""

    mempalace_archive(content, f"dgen_{rule_id}")





# ============================================================

# 全局单例（懒加载）

# ============================================================



_engine: Optional[RuleEngine] = None

_arbiter: Optional[ConflictArbiter] = None

_reviewer: Optional[Reviewer] = None

_tracker: Optional[BehaviorTracker] = None

_wargame: Optional[WarGameEngine] = None





def _get_engine() -> RuleEngine:

    global _engine

    if _engine is None:

        _engine = RuleEngine()

        init_rules_if_empty(_engine)

    return _engine





def _get_arbiter() -> ConflictArbiter:

    global _arbiter

    if _arbiter is None:

        _arbiter = ConflictArbiter(_get_engine())

    return _arbiter





def _get_reviewer() -> Reviewer:

    global _reviewer

    if _reviewer is None:

        _reviewer = Reviewer(_get_engine())

    return _reviewer





def _get_tracker() -> BehaviorTracker:

    global _tracker

    if _tracker is None:

        _tracker = BehaviorTracker(_get_engine())

    return _tracker





def _get_wargame() -> WarGameEngine:

    global _wargame

    if _wargame is None:

        _wargame = WarGameEngine(_get_engine())

    return _wargame





# ============================================================

# 对外暴露的公共 API

# ============================================================



def get_rules_for_task(task_context: Dict[str, Any]) -> Dict[str, List]:

    """根据任务上下文检索匹配的规则"""

    engine = _get_engine()

    return engine.retrieve_for_task(task_context)





def arbitrate(interceptions: List[InterceptionRule],

              patterns: List[SuccessPattern]) -> Dict[str, Any]:

    """冲突仲裁（自动归档到MemPalace）"""

    import dataclasses

    arbiter = _get_arbiter()

    result = arbiter.resolve(interceptions, patterns)



    response = {

        "decision": result.decision.value,

        "reason": result.reason,

        "winning_rule": None,

        "conflict_set": []

    }



    if result.winning_rule:

        if hasattr(result.winning_rule, '__dataclass_fields__'):

            response["winning_rule"] = dataclasses.asdict(result.winning_rule)

        else:

            response["winning_rule"] = result.winning_rule



    if result.conflict_set:

        response["conflict_set"] = [

            dataclasses.asdict(r) if hasattr(r, '__dataclass_fields__') else r

            for r in result.conflict_set

        ]



    if result.requires_precedent:

        engine = _get_engine()

        precedent = Precedent(

            id="",

            conflict_rules=[r.id for r in result.conflict_set] if result.conflict_set else [],

            resolution="auto_degraded",

            degradation_reason=result.reason,

            winning_rule=response["winning_rule"].get("id", "") if response["winning_rule"] else "",

            winning_rule_type="interception" if response["winning_rule"] and "severity" in response["winning_rule"] else "success_pattern",

            decision_logic=result.reason

        )

        engine.add_precedent(precedent)

        engine.save_all()



    # MemPalace 归档：裁决后自动同步

    if _MEMPALACE_AVAILABLE:

        rid = response.get("winning_rule", {}).get("id", "unknown") if isinstance(response.get("winning_rule"), dict) else "unknown"

        dgen_archive(rid, response["decision"], {"matched": len(interceptions), "reason": result.reason})



    return response





def full_review(task_context: Dict[str, Any],

                task_result: Dict[str, Any]) -> Dict[str, Any]:

    """执行完整的三明治复盘（自动归档到MemPalace）"""

    reviewer = _get_reviewer()

    result = reviewer.full_review(task_context, task_result)



    # MemPalace 归档：复盘后自动同步

    if _MEMPALACE_AVAILABLE:

        dgen_archive("review", "completed", {

            "task_type": task_context.get("task_type", ""),

            "clean": len(result.clean_signals),

            "filtered": len(result.filtered_signals),

            "fused": len(result.fused_outputs)

        })



    return {

        "clean_signals_count": len(result.clean_signals),

        "filtered_signals_count": len(result.filtered_signals),

        "fused_outputs_count": len(result.fused_outputs),

        "meta_insights_count": len(result.meta_insights),

        "anomalies_count": len(result.anomaly_observations),

        "fused_outputs": result.fused_outputs,

        "filtered_signals": result.filtered_signals

    }





def auto_sandwich(positive: List[str], negative: List[str], task_type: str = "general") -> Dict:

    """

    守三攻七自动化：重要工作后自动复盘

    先负向纠错 → 再正向强化

    """

    from datetime import datetime

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    

    tracker = _get_tracker()

    engine = _get_engine()

    

    report_lines = [f"# 守三攻七复盘 | {ts}\n"]

    

    # 负向纠错（守三）

    report_lines.append("## 守三·纠错\n")

    for i, n in enumerate(negative, 1):

        report_lines.append(f"{i}. {n}\n")

        # 为每个负向点创建或加固拦截规则

        error_key = f"auto_{task_type}_error_{i}"

        result = tracker.record_self_error(

            error_type=f"{task_type}_{i}",

            detail=n,

            task_context={"task_type": task_type}

        )

        if result.get("warning"):

            report_lines.append(f"   ⚠️ {result['warning']}\n")

        if result.get("alert"):

            report_lines.append(f"   🔴 {result['alert']}\n")

    

    # 正向强化（攻七）

    report_lines.append("\n## 攻七·强化\n")

    for i, p in enumerate(positive, 1):

        report_lines.append(f"{i}. {p}\n")

        # 为每个正向点尝试提炼成功模式

        pat_id = f"pat_auto_{task_type}_{i}"

        existing = engine.get_pattern_by_id(pat_id)

        if existing:

            # 已存在 → 置信度+0.3

            existing.confidence = min(5.0, existing.confidence + 0.3)

            existing.triggered_count += 1

            engine.update_pattern(pat_id,

                confidence=existing.confidence,

                triggered_count=existing.triggered_count)

            report_lines.append(f"   ✅ 已有模式，置信度+0.3 → {existing.confidence}\n")

        else:

            # 新模式

            from rule_engine import SuccessPattern

            new_pat = SuccessPattern(

                id=pat_id,

                pattern_name=f"auto_{task_type}_{i}",

                trigger_scenario=task_type,

                decision_logic=p,

                micro_template=p[:80],

                logic_score=4.0,

                outcome_score=3.5,

                confidence=3.8,

                source="auto_sandwich",

                lifecycle_status="active",

                created_at=datetime.now().isoformat(),

                triggered_count=1

            )

            engine.add_pattern(new_pat)

            report_lines.append(f"   ✅ 已创建新模式, conf=3.8\n")

    

    engine.save_all()

    report = "".join(report_lines)

    

    # 归档到MemPalace

    if _MEMPALACE_AVAILABLE:

        dgen_archive(f"[守三攻七] {task_type}", report, "auto_review")

    

    return {

        "task_type": task_type,

        "negative_count": len(negative),

        "positive_count": len(positive),

        "report": report

    }





def record_user_feedback(rule_id: str, feedback: str, user_action: str = None) -> Dict[str, Any]:

    """

    用户反馈三态模型

    feedback: 'agree' | 'veto' | 'silent'

    user_action: None | 'consistent' | 'inconsistent'

    """

    tracker = _get_tracker()

    result = tracker.record_user_feedback(rule_id, feedback, user_action)

    

    if _MEMPALACE_AVAILABLE and result.get("action") not in ("not_found",):

        dgen_archive(rule_id, f"user_feedback_{feedback}_{result.get('action', 'unknown')}", {})

    

    return result





def record_behavior(rule_id: str, action: str) -> Dict[str, Any]:

    """记录对规则的隐性行为（触发/无视/覆盖）自动归档到MemPalace"""

    tracker = _get_tracker()

    if action == "ignored":

        result = tracker.record_ignore(rule_id)

    elif action == "override":

        result = tracker.record_override(rule_id)

    elif action == "triggered":

        result = tracker.record_triggered(rule_id)

    else:

        return {"action": "unknown", "error": f"不支持的操作: {action}"}



    # MemPalace 归档

    if _MEMPALACE_AVAILABLE:

        dgen_archive(rule_id, action, {})



    return result





def run_war_game(portfolio: Dict, macro_data: Dict) -> List[Dict]:

    """运行沙盘推演"""

    wargame = _get_wargame()

    return wargame.run_scenarios(portfolio, macro_data)





def health_check(verbose: bool = True) -> Dict[str, Any]:

    """运行健康度检查"""

    engine = _get_engine()

    return run_health_check(engine)





def run_maintenance():

    """执行定期维护（降权/归档/软淘汰）"""

    engine = _get_engine()

    tracker = _get_tracker()



    print("[TOOL] 开始执行定期维护...")



    ignored_rules = tracker.get_ignored_rules(threshold=0.8)

    for item in ignored_rules:

        rule_id = item["id"]

        tracker.record_ignore(rule_id)

        print(f"  [DOWN] 软淘汰: {rule_id} (无视率 {item['ignore_rate']:.1%})")



    for pattern in engine.get_patterns(active_only=False):

        if pattern.lifecycle_status == "cached" and pattern.valid_until:

            from datetime import datetime

            if datetime.now().isoformat() > pattern.valid_until:

                engine.update_pattern(pattern.id, lifecycle_status="archived")

                print(f"  [ARCHIVE] 归档过期缓存: {pattern.id}")



    for rule in engine.get_interceptions(active_only=True):

        if rule.confidence < 2.0:

            engine.update_interception(rule.id, lifecycle_status="deprecating")

            print(f"  [DOWN] 降权: {rule.id} (置信度 {rule.confidence:.2f})")



    engine.save_all()

    print("[OK] 定期维护完成")





_last_work_context: Optional[Dict] = None



def auto_sandwich_trigger(task_type: str, positive: List[str] = None, negative: List[str] = None):

    """

    工作完成后自动钩子：检测是否已完成重要工作，自动触发守三攻七复盘。

    由 call_diegin.py 或外部工具在关键操作完成后调用。

    """

    from datetime import datetime

    global _last_work_context

    

    if positive is None:

        positive = []

    if negative is None:

        negative = []

    

    # 如果没有提供正/负向点，输出提示但不报错（允许空复盘）

    result = auto_sandwich(positive, negative, task_type)

    

    # 归档触发记录

    _last_work_context = {

        "task_type": task_type,

        "triggered_at": datetime.now().isoformat(),

        "positive_count": len(positive),

        "negative_count": len(negative),

        "sandwich_result": result.get("report", "")[:200]

    }

    

    if _MEMPALACE_AVAILABLE:

        dgen_archive(f"[auto_sandwich_trigger] {task_type}", json.dumps(_last_work_context, ensure_ascii=False), "auto")

    

    return result





def self_check() -> bool:

    """系统自检"""

    try:

        engine = _get_engine()

        assert engine is not None

        rules = engine.get_interceptions(active_only=False)

        if len(rules) == 0:

            print("[WARN] 规则库为空，请检查种子规则是否注入")

            return False



        print(f"[OK] 系统就绪：共加载 {len(rules)} 条拦截规则，{len(engine.get_patterns(active_only=False))} 条成功模式")

        return True

    except Exception as e:

        print(f"[ERR] 自检失败: {e}")

        return False





if __name__ == "__main__":

    self_check()

