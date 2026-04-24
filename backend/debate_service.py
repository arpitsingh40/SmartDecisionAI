"""Debate & Refinement Mode (Phase 7).

Lets a user challenge a decision. We:
  1) Extract concerns + decide whether we need clarifying Qs (Stage 1)
  2) Optionally receive user's clarifying answers (Stage 1.5)
  3) Re-run the full 6-agent Boardroom with updated context (Stage 2)
     - Falls back to the legacy single-prompt analyzer if the panel fails
  4) Synthesize the "UPDATED OUTPUT" block (Stage 3): what changed,
     updated outcome, strengths/weaknesses, when-original-wins, next action.

The public entrypoints are small on purpose so the FastAPI background-job
worker in server.py can orchestrate the flow.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from ai_service import (
    ConcernExtraction,
    DecisionResult,
    RefinementOutput,
    _parse_json_with_repair,
    _try_call_with_fallback,
    analyze_decision,
)
from multi_agent_service import analyze_decision_multiagent

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stage 1 — Extract concerns + decide whether to ask clarifying Qs
# ---------------------------------------------------------------------------
EXTRACT_SYSTEM = """You are the CONCERN EXTRACTOR for a decision-intelligence tool.
A user just received a structured decision recommendation and is pushing back.
Your job: understand WHY they disagree and decide whether we have enough
information to re-run the analysis, or whether we need 1-3 targeted clarifying
questions first.

BE CRISP. NO PROSE OUTSIDE JSON.

GUIDELINES for needs_clarification:
- If the user's objection is specific and actionable (names a concrete fact,
  constraint, or preference the AI got wrong), set needs_clarification = false.
- If the objection is vague ("this feels off", "I don't like it"), or mentions
  a concern whose impact depends on missing data (numbers, timelines,
  preferences), set needs_clarification = true and produce 1-3 sharp, high-
  impact questions whose answers would materially change the re-analysis.
- Never ask more than 3 questions. Questions must be short and one-concept.

Output STRICT JSON only. No markdown fences.
{
  "summary": "1 sentence what the user is pushing back on",
  "concerns": [
    {"text":"...","category":"risk|feasibility|cost|time|personal|other"}
  ],
  "assumption_gaps": ["assumptions in the previous analysis that may be wrong (2-4 items)"],
  "needs_clarification": true | false,
  "clarifying_questions": [
    {"question":"...","help_text":"why we're asking (optional)"}
  ]
}
"""


async def extract_concerns_and_decide(
    decision: str,
    prior_result: Dict[str, Any],
    objection: str,
) -> ConcernExtraction:
    """Stage 1 — Extract user's concerns and decide if clarification is needed."""
    # Condense the prior result so we don't blow up the context window.
    options_summary = []
    for o in (prior_result.get("options") or [])[:4]:
        options_summary.append({
            "id": o.get("id"),
            "title": o.get("title"),
            "score": o.get("score"),
            "risk_level": o.get("risk_level"),
            "is_do_nothing": o.get("is_do_nothing", False),
        })
    prior_brief = {
        "goal": prior_result.get("goal"),
        "best_option_id": prior_result.get("best_option_id"),
        "reasoning": (prior_result.get("reasoning") or "")[:600],
        "confidence": prior_result.get("confidence"),
        "options": options_summary,
        "assumptions": (prior_result.get("assumptions") or [])[:4],
        "key_insights": (prior_result.get("key_insights") or [])[:3],
    }
    user_text = (
        f"ORIGINAL DECISION:\n{decision}\n\n"
        f"PRIOR ANALYSIS (brief, JSON):\n{json.dumps(prior_brief, indent=2, default=str)}\n\n"
        f"USER OBJECTION:\n{objection}\n\n"
        "Return the JSON now. JSON only."
    )
    last_err: Optional[str] = None
    for attempt in range(2):
        raw = await _try_call_with_fallback(EXTRACT_SYSTEM, user_text, "debate-extract")
        try:
            data = _parse_json_with_repair(raw)
            if isinstance(data.get("clarifying_questions"), list):
                data["clarifying_questions"] = data["clarifying_questions"][:3]
            if isinstance(data.get("concerns"), list):
                data["concerns"] = data["concerns"][:6]
            if isinstance(data.get("assumption_gaps"), list):
                data["assumption_gaps"] = data["assumption_gaps"][:6]
            # If model set needs_clarification=true but gave no questions, flip to false
            if data.get("needs_clarification") and not (data.get("clarifying_questions") or []):
                data["needs_clarification"] = False
            return ConcernExtraction(**data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_err = str(e)[:300]
            user_text += f"\n\nPrevious validation error: {last_err}\nFix strictly and return JSON only."
            continue
    # Last-resort: return a minimal extraction so the flow can still proceed.
    logger.warning("concern extraction failed: %s", last_err)
    return ConcernExtraction(
        summary="Could not parse concerns; proceeding with raw objection.",
        concerns=[],
        assumption_gaps=[],
        needs_clarification=False,
    )


# ---------------------------------------------------------------------------
# Stage 2 — Re-run the full Boardroom with updated context
# ---------------------------------------------------------------------------
async def run_refined_analysis(
    decision: str,
    prior_answers: List[Dict[str, Any]],
    prior_factors: List[Dict[str, Any]],
    objection: str,
    extraction: ConcernExtraction,
    clarifying_answers: List[Dict[str, Any]],
    user_level: str = "intermediate",
) -> tuple[DecisionResult, str]:
    """Run the 6-agent Boardroom with the objection + concerns injected.

    Returns (result, engine_used).
    """
    # Inject debate context as additional pseudo-answers so both multi-agent
    # and legacy analyzers see the new information without schema changes.
    debate_answers: List[Dict[str, Any]] = list(prior_answers)
    debate_answers.append(
        {"question": "User objection to prior analysis", "answer": objection}
    )
    if extraction.concerns:
        debate_answers.append({
            "question": "Specific concerns to address",
            "answer": "; ".join(f"[{c.category}] {c.text}" for c in extraction.concerns),
        })
    if extraction.assumption_gaps:
        debate_answers.append({
            "question": "Assumptions that may be wrong",
            "answer": "; ".join(extraction.assumption_gaps),
        })
    for ans in clarifying_answers or []:
        q = ans.get("question") or "Clarification"
        a = ans.get("answer") or ""
        if a:
            debate_answers.append({"question": f"Clarification — {q}", "answer": a})

    # Primary: Boardroom. Fallback: legacy analyzer.
    try:
        result = await analyze_decision_multiagent(
            decision, debate_answers, factors=prior_factors, user_level=user_level,
        )
        return result, "multi_agent"
    except Exception as e:
        logger.warning("debate multi-agent failed, falling back to legacy: %s", str(e)[:200])
        result = await analyze_decision(
            decision, debate_answers, factors=prior_factors, user_level=user_level,
        )
        return result, "legacy_fallback"


# ---------------------------------------------------------------------------
# Stage 3 — Synthesize the "UPDATED OUTPUT" block
# ---------------------------------------------------------------------------
WHAT_CHANGED_SYSTEM = """You are the DIFF SYNTHESIZER for a decision-intelligence tool.
Given (a) the original decision analysis, (b) the user's objection + concerns,
and (c) a revised decision analysis from the panel, produce a crisp,
user-facing "UPDATED OUTPUT" block in STRICT JSON.

Tone: transparent, honest, concise, actionable. Do NOT defend the original
result blindly — explicitly acknowledge when the revision is meaningfully
different. Always include a clear next action the user can take in 24-48h.

Output STRICT JSON only. No prose outside JSON. No markdown fences.

SCHEMA:
{
  "updated_decision_verdict": "keep" | "modify" | "change",
  "what_changed_summary": "2-3 sentences: what's different and WHY it changed",
  "key_diffs": [
    {"topic":"Best option","before":"...","after":"..."},
    {"topic":"Risk level","before":"...","after":"..."}
  ],
  "updated_outcome": {
    "revenue_or_savings": "e.g. +$1.8k/yr or $300/mo saved",
    "probability_pct": 0-100,
    "timeframe": "e.g. 30-60 days"
  },
  "strengths": ["3-5 reasons the revised plan works better now"],
  "weaknesses": ["2-4 remaining risks or trade-offs"],
  "execution_adjustments": ["2-4 concrete things the user should now do differently"],
  "when_original_wins": "1-2 sentences: under what conditions the original plan would still be better",
  "next_action_24_48h": "1 concrete, bite-sized step the user can take today or tomorrow",
  "confidence_delta": {"old": <0-100>, "new": <0-100>}
}

Verdict rules:
- "keep"    — revision basically agrees with original; the objection didn't materially change the outcome.
- "modify"  — same best option but execution plan / scorecard / risk changed.
- "change"  — the best option itself changed OR confidence dropped >20 pts.
"""


def _brief(result: Dict[str, Any]) -> Dict[str, Any]:
    """Condense a DecisionResult dict into a small brief for the synthesizer."""
    opts = []
    for o in (result.get("options") or [])[:4]:
        opts.append({
            "id": o.get("id"),
            "title": o.get("title"),
            "score": o.get("score"),
            "risk_level": o.get("risk_level"),
            "is_do_nothing": o.get("is_do_nothing", False),
            "factor_ratings": o.get("factor_ratings") or {},
        })
    return {
        "goal": result.get("goal"),
        "best_option_id": result.get("best_option_id"),
        "reasoning": (result.get("reasoning") or "")[:500],
        "confidence": result.get("confidence"),
        "scorecard": result.get("scorecard") or {},
        "options": opts,
        "key_insights": (result.get("key_insights") or [])[:3],
        "assumptions": (result.get("assumptions") or [])[:4],
    }


async def synthesize_what_changed(
    original_result: Dict[str, Any],
    revised_result: Dict[str, Any],
    objection: str,
    extraction: ConcernExtraction,
) -> RefinementOutput:
    payload = {
        "original": _brief(original_result),
        "revised": _brief(revised_result),
        "user_objection": objection,
        "extracted_concerns": [c.model_dump() for c in extraction.concerns],
        "assumption_gaps": extraction.assumption_gaps,
    }
    user_text = (
        "CONTEXT (JSON):\n"
        + json.dumps(payload, indent=2, default=str)
        + "\n\nProduce the UPDATED OUTPUT JSON now. JSON only."
    )
    old_conf = int(original_result.get("confidence") or 0)
    new_conf = int(revised_result.get("confidence") or old_conf)

    last_err: Optional[str] = None
    for attempt in range(2):
        try:
            raw = await _try_call_with_fallback(WHAT_CHANGED_SYSTEM, user_text, "debate-synth")
            data = _parse_json_with_repair(raw)
            # Ensure confidence_delta is present & sensible
            delta = data.get("confidence_delta") or {}
            if not isinstance(delta, dict) or "old" not in delta or "new" not in delta:
                data["confidence_delta"] = {"old": old_conf, "new": new_conf}
            # Trim lists to schema caps
            for k, cap in [
                ("key_diffs", 6), ("strengths", 5), ("weaknesses", 5),
                ("execution_adjustments", 5),
            ]:
                if isinstance(data.get(k), list):
                    data[k] = data[k][:cap]
            return RefinementOutput(**data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_err = str(e)[:300]
            user_text += f"\n\nPrevious validation error: {last_err}\nFix strictly and return JSON only."
            continue

    # Best-effort fallback: compute a minimal diff ourselves so the UI always shows something.
    logger.warning("what-changed synth failed: %s", last_err)
    old_best = original_result.get("best_option_id")
    new_best = revised_result.get("best_option_id")
    verdict = "change" if old_best != new_best else (
        "modify" if abs(new_conf - old_conf) >= 5 else "keep"
    )
    return RefinementOutput(
        updated_decision_verdict=verdict,
        what_changed_summary=(
            "Refined analysis couldn't generate a detailed diff, but here's "
            "the summary: best option " +
            ("changed from " + str(old_best) + " to " + str(new_best)
             if old_best != new_best else "remained the same") +
            f"; confidence {old_conf}% -> {new_conf}%."
        ),
        key_diffs=[],
        updated_outcome=None,
        strengths=[],
        weaknesses=[],
        execution_adjustments=[],
        when_original_wins="",
        next_action_24_48h="Review the updated option above and pick the single first step.",
        confidence_delta={"old": old_conf, "new": new_conf},
    )
