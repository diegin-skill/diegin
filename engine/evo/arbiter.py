#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diegin-evo 冲突仲裁器
迭进自主生成和维护
"""

import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from rule_engine import InterceptionRule, SuccessPattern, RuleEngine


class ResolutionType(Enum):
    IRON_WALL_BLOCK = "iron_wall_block"       # 铁律阻断
    CONFIDENCE_WIN = "confidence_win"          # 置信度胜出
    HUMAN_REQUIRED = "human_required"          # 需人工裁决
    AUTO_DEGRADED = "auto_degraded"            # 自动降级


@dataclass
class ArbitrationResult:
    """仲裁结果"""
    decision: ResolutionType
    winning_rule: Optional[object] = None
    reason: str = ""
    conflict_set: List = field(default_factory=list)
    degradation_type: str = ""
    requires_precedent: bool = False


class ConflictArbiter:
    """冲突仲裁器"""

    def __init__(self, rule_engine: RuleEngine,
                 timeout_minutes: int = 5,
                 max_queue_size: int = 3):
        self.rule_engine = rule_engine
        self.timeout_seconds = timeout_minutes * 60
        self.max_queue_size = max_queue_size
        self.pending_conflicts: List[Dict] = []

    def resolve(self, interceptions: List[InterceptionRule],
                patterns: List[SuccessPattern]) -> ArbitrationResult:
        """
        核心仲裁逻辑
        层级：铁律层 → 置信度层 → 人工兜底/自动降级
        """
        # ── 第一层：铁律层 ──
        for rule in interceptions:
            if rule.severity == "high" and "irreversible" in rule.tags:
                return ArbitrationResult(
                    decision=ResolutionType.IRON_WALL_BLOCK,
                    winning_rule=rule,
                    reason="触及安全铁律：不可逆操作或合规红线"
                )

        # ── 无冲突：按置信度排序 ──
        if not interceptions or not patterns:
            all_rules = interceptions + patterns
            if not all_rules:
                return ArbitrationResult(
                    decision=ResolutionType.CONFIDENCE_WIN,
                    winning_rule=None,
                    reason="无规则触发"
                )
            sorted_rules = sorted(all_rules, key=lambda x: x.confidence, reverse=True)
            return ArbitrationResult(
                decision=ResolutionType.CONFIDENCE_WIN,
                winning_rule=sorted_rules[0],
                reason="无冲突，按最高置信度执行"
            )

        # ── 存在攻守冲突：比较置信度 ──
        best_interception = max(interceptions, key=lambda x: x.confidence)
        best_pattern = max(patterns, key=lambda x: x.confidence)
        confidence_delta = abs(best_interception.confidence - best_pattern.confidence)

        # ── 第三层：置信度接近（< 0.5）──
        if confidence_delta < 0.5:
            conflict_entry = {
                "timestamp": time.time(),
                "interception": best_interception,
                "pattern": best_pattern,
                "delta": confidence_delta,
                "resolved": False
            }
            self.pending_conflicts.append(conflict_entry)

            auto_decision = self._check_degradation()
            if auto_decision:
                return auto_decision

            return ArbitrationResult(
                decision=ResolutionType.HUMAN_REQUIRED,
                conflict_set=[best_interception, best_pattern],
                reason=f"置信度分差在±0.5以内（delta={confidence_delta:.3f}），需人工裁决"
            )

        # 置信度差距足够，直接选高分
        if best_interception.confidence > best_pattern.confidence:
            return ArbitrationResult(
                decision=ResolutionType.CONFIDENCE_WIN,
                winning_rule=best_interception,
                reason="守方置信度更高"
            )
        else:
            return ArbitrationResult(
                decision=ResolutionType.CONFIDENCE_WIN,
                winning_rule=best_pattern,
                reason="攻方置信度更高"
            )

    def _check_degradation(self) -> Optional[ArbitrationResult]:
        """自动降级熔断检查"""
        now = time.time()

        unresolved_timeout = [
            c for c in self.pending_conflicts
            if not c.get("resolved") and (now - c["timestamp"]) > self.timeout_seconds
        ]

        should_degrade = (
            len(unresolved_timeout) > 0
            or len(self.pending_conflicts) >= self.max_queue_size
        )

        if should_degrade:
            latest = self.pending_conflicts[-1]
            latest["resolved"] = True

            safety_first = sorted(
                [latest["interception"], latest["pattern"]],
                key=lambda r: (r.severity == "high", r.logic_score),
                reverse=True
            )[0]

            return ArbitrationResult(
                decision=ResolutionType.AUTO_DEGRADED,
                winning_rule=safety_first,
                reason=f"人工兜底超时/排队超限，自动降级",
                degradation_type="timeout" if unresolved_timeout else "queue_full",
                requires_precedent=True
            )

        return None

    def human_resolve(self, conflict_index: int, chosen_rule) -> ArbitrationResult:
        """人工裁决接口"""
        if conflict_index < len(self.pending_conflicts):
            self.pending_conflicts[conflict_index]["resolved"] = True
            return ArbitrationResult(
                decision=ResolutionType.HUMAN_REQUIRED,
                winning_rule=chosen_rule,
                reason="人工裁决"
            )
        return ArbitrationResult(
            decision=ResolutionType.HUMAN_REQUIRED,
            winning_rule=None,
            reason="未找到对应冲突"
        )
