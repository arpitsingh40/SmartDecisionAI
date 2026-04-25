"""Multi-Agent Decision System.

Runs 6 specialized expert agents IN PARALLEL, each focused on one dimension.
Each agent returns a compact structured JSON. A Synthesizer then reconciles
their outputs and produces the final DecisionResult + a "debate" section.

Agents (all return STRICT JSON only):
  1. Strategic     — frame the goal, optimization target, filter noise
  2. Financial     — EV, ROI, payback, opportunity cost
  3. Risk          — failure modes, worst case, probabilities
  4. Execution     — feasibility, bottlenecks, concrete next steps, tools
  5. Contrarian    — objections, weak assumptions, steelman of alternative
  6. Optimization  — leverage, automation, scale plays

Then the Synthesizer produces the final output in the same DecisionResult
schema the UI already renders, plus new `agent_perspectives` and `debate` fields.
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from ai_service import (
    DecisionResult,
    _parse_json_with_repair,
    _try_call_with_fallback,
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Agent system prompts  (short and focused; output STRICT JSON only)
# -----------------------------------------------------------------------------
STRATEGIC_SYSTEM = """You are the STRATEGIC AGENT on a decision-intelligence panel.
Your ONLY job: frame the problem precisely and name what we're truly optimizing for.
Ignore details that don't change the outcome. Call out the real success metric.

Output STRICT JSON only. No prose outside JSON.
{
  "summary": "1 sentence: what are we truly optimizing for?",
  "goal_restated": "1-2 sentences precise restatement of the user's goal",
  "optimize_for": "the single north-star outcome (e.g. 'lifetime ROI', 'time-to-$10k MRR')",
  "noise_filtered": ["things NOT to worry about right now (2-3 items)"],
  "success_metric": "how we'll know the decision worked (1 sentence, quantified)"
}
"""

FINANCIAL_SYSTEM = """You are the FINANCIAL / EV AGENT on a decision-intelligence panel.
Your ONLY job: quantify money. Calculate Expected Value, ROI, payback, opportunity cost.
Always use numbers ($, %, months). If data is missing, state a reasonable assumption.

Output STRICT JSON only. No prose outside JSON.
{
  "summary": "1 sentence money takeaway",
  "expected_value": "EV in $/₹ with a short derivation (e.g. '0.6 × $40k − 0.4 × $5k = $22k')",
  "roi_pct_range": "realistic ROI % range (e.g. '8-22%/yr')",
  "payback_months": "estimated payback period (e.g. '4-9 months')",
  "opportunity_cost": "what you give up (quantified)",
  "money_insights": ["2-3 numeric insights with $ or %"]
}
"""

RISK_SYSTEM = """You are the RISK AGENT on a decision-intelligence panel.
Your ONLY job: find failure modes. Be paranoid. Quantify probability and severity.

Output STRICT JSON only. No prose outside JSON.
{
  "summary": "1 sentence biggest risk",
  "top_risks": [
    {"risk":"...","severity":"Low|Medium|High","probability_pct":0-100,"impact":"..."}
  ],
  "worst_case": "1-2 sentences concrete worst case with $ impact",
  "hidden_failure_modes": ["2-3 non-obvious failure modes"],
  "risk_score_100": 0-100
}
"""

EXECUTION_SYSTEM = """You are the EXECUTION AGENT on a decision-intelligence panel.
Your ONLY job: turn decisions into concrete, feasible actions. Focus on speed + tools.

Output STRICT JSON only. No prose outside JSON.
{
  "summary": "1 sentence feasibility verdict",
  "feasibility_score_100": 0-100,
  "bottlenecks": ["2-3 biggest blockers"],
  "quick_start": "the SINGLE first concrete action the user can take today",
  "tools": ["3-5 real tools/platforms (e.g. Notion, Stripe, Zapier, Calendly)"],
  "time_to_first_result": "e.g. '14 days', '2 weeks'"
}
"""

CONTRARIAN_SYSTEM = """You are the CONTRARIAN AGENT on a decision-intelligence panel.
Your ONLY job: challenge everything. Find flaws in logic. Take the OPPOSITE side.
Be sharp but not rude. Assume the user has a blind spot. Ask "why might this be wrong?"

Output STRICT JSON only. No prose outside JSON.
{
  "summary": "1 sentence: the most uncomfortable truth about this decision",
  "strong_objections": ["3-4 sharpest 'why this might be wrong' arguments"],
  "weak_assumptions": ["2-3 assumptions in the user's framing that may not hold"],
  "devil_advocate_view": "1-2 sentences steelman of doing the OPPOSITE",
  "false_premises": ["up to 2 premises in how the decision is framed that may be wrong"]
}
"""

OPTIMIZATION_SYSTEM = """You are the OPTIMIZATION AGENT on a decision-intelligence panel.
Your ONLY job: find leverage. Automation. Scale plays. How to 10x the upside once the decision is made.

Output STRICT JSON only. No prose outside JSON.
{
  "summary": "1 sentence: biggest leverage point",
  "leverage_ideas": ["3-4 ideas that multiply the outcome (not incremental)"],
  "automation_opportunities": [
    {"area":"...","tool":"Zapier|Make|Notion|Airtable|...","how_it_helps":"1 sentence"}
  ],
  "scale_plays": ["2-3 ways to scale once the core works"],
  "quick_wins_to_10x": "1-2 sentences: smallest change with outsized impact"
}
"""

# -----------------------------------------------------------------------------
# Synthesizer — takes all 6 agent outputs and produces the full DecisionResult
# -----------------------------------------------------------------------------
SYNTHESIZER_SYSTEM = """You are the FINAL SYNTHESIZER on a decision-intelligence panel.
Six specialist agents have just independently analyzed the problem. Your job:

1) Resolve conflicts between agents (debate section).
2) Converge on the best overall decision weighted by EV, risk-adjusted return, and execution feasibility.
3) Produce the full structured Decision Execution output (the same rich JSON the UI already renders)
   PLUS a `debate` section capturing the agents' trade-offs and how you resolved them,
   PLUS an `agent_perspectives` echo of each agent's core summary.

Every numeric claim must reference the agent who made it (e.g. "as the Financial Agent notes, EV ≈ $22k").

You MUST include a "Do nothing" option last (is_do_nothing=true). Include factor_ratings
(0-10) for EACH factor provided. Include all of: key_insights, assumptions, bias_flags,
options, best_option_id, reasoning, confidence, key_reasons, expected_outcome, risks,
execution_plan (with steps including action_button), automation_layer, kpis,
monetization, plan_b, plan_b_trigger, scorecard, debate, agent_perspectives.

Output STRICT JSON only. No markdown fences. No prose outside JSON.

SCHEMA (EXACT — all fields required unless marked optional):
{
  "goal":"...",
  "key_insights":["...","..."],
  "assumptions":["...","..."],
  "bias_flags":[{"title":"...","message":"...","severity":"info|warn|high"}],
  "factors_used":["FactorA","FactorB"],
  "options":[
    {
      "id":"opt_1","title":"...","description":"...","is_do_nothing":false,
      "pros":["...","..."],"cons":["...","..."],
      "risk_level":"Low|Medium|High",
      "short_term_outcome":"...","long_term_outcome":"...",
      "score":0-100,
      "factor_ratings":{"FactorA":0-10,"FactorB":0-10},
      "scenarios":{"best_case":"...","worst_case":"...","most_likely":"..."},
      "future_impact":{"one_year":"...","five_year":"..."},
      "success_probability":0-100,"expected_return":"...","time_to_result":"...",
      "geography":"...","easiness":0-100,"support":"...","history":"...","financial_ratio":"...","why_not":"..."
    }
  ],
  "best_option_id":"opt_X",
  "reasoning":"2-3 sentences grounded in agent perspectives.",
  "key_reasons":["3-4 sharp reasons (cite agents)"],
  "expected_outcome":{
    "revenue_increase":{"realistic_low":"$X","realistic_high":"$Y","best_case":"$Z","note":"..."},
    "cost_savings":{"realistic_low":"$X","realistic_high":"$Y","best_case":"$Z","note":"..."},
    "time_saved":"e.g. 6-10 hrs/week",
    "non_financial":["...","..."]
  },
  "risks":[{"risk":"...","severity":"Low|Medium|High","probability":"Low|Medium|High","mitigation":"..."}],
  "execution_plan":{
    "title":"...","total_timeline":"e.g. 60 days",
    "steps":[
      {
        "step":1,"action":"...","timeline":"Week 1","priority":"High",
        "days":3,"difficulty":"Easy|Medium|Hard",
        "tools":["..."],"est_cost":"$X","est_benefit":"Y",
        "action_button":{"label":"Start Now","tool":"Notion","url":"https://www.notion.so","instruction":"...","automation_shortcut":"..."}
      }
    ],
    "short_term_plan":"...","moderate_benefits":"..."
  },
  "automation_layer":[{"area":"...","tools":["..."],"how_it_helps":"...","plug_and_play":true}],
  "kpis":[{"name":"...","how_to_measure":"...","target":"...","leading_indicator":true}],
  "monetization":{"services":["..."],"products":["..."],"upsells":["..."]},
  "plan_b":"...","plan_b_trigger":"...",
  "scorecard":{
    "score":0-100,"risk_level":"Low|Medium|High",
    "time_to_result":"e.g. 60-90 days","ease_of_execution":0-100,"confidence":0-100
  },
  "confidence":0-100,
  "debate":{
    "conflicts":[
      {"topic":"...","views":[{"agent":"Financial","view":"..."},{"agent":"Risk","view":"..."}],"resolution":"..."}
    ],
    "trade_offs":["..."],
    "convergence":"1 sentence where agents agreed"
  },
  "agent_perspectives":[
    {"agent":"Strategic","summary":"...","details":{...}},
    {"agent":"Financial","summary":"...","details":{...}},
    {"agent":"Risk","summary":"...","details":{...}},
    {"agent":"Execution","summary":"...","details":{...}},
    {"agent":"Contrarian","summary":"...","details":{...}},
    {"agent":"Optimization","summary":"...","details":{...}}
  ]
}
"""


# -----------------------------------------------------------------------------
# Helpers — run a single agent (tolerant to failure; returns empty on error)
# -----------------------------------------------------------------------------
def _clamp_str(s: Any, max_len: int) -> Any:
    """Truncate a string to max_len, preserving non-strings unchanged."""
    if isinstance(s, str) and len(s) > max_len:
        return s[: max_len - 1].rstrip() + "…"
    return s


def _normalize_synth_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clamp known fields that exceed schema limits.

    GPT-5.x reasoning models tend to be verbose and frequently overrun the
    `max_length` constraints we set on RiskItem.mitigation, BiasFlag.message,
    etc. Truncating before Pydantic validates avoids spurious retries.
    """
    # bias_flags: title<=80, message<=280
    for bf in data.get("bias_flags") or []:
        if isinstance(bf, dict):
            bf["title"] = _clamp_str(bf.get("title"), 80)
            bf["message"] = _clamp_str(bf.get("message"), 280)
    # risks: risk<=140, mitigation<=200
    for r in data.get("risks") or []:
        if isinstance(r, dict):
            r["risk"] = _clamp_str(r.get("risk"), 140)
            r["mitigation"] = _clamp_str(r.get("mitigation"), 200)
    # automation_layer: area<=60, how_it_helps<=200, tools list<=6
    for a in data.get("automation_layer") or []:
        if isinstance(a, dict):
            a["area"] = _clamp_str(a.get("area"), 60)
            a["how_it_helps"] = _clamp_str(a.get("how_it_helps"), 200)
            if isinstance(a.get("tools"), list):
                a["tools"] = a["tools"][:6]
    # kpis: name<=60, how_to_measure<=200
    for k in data.get("kpis") or []:
        if isinstance(k, dict):
            k["name"] = _clamp_str(k.get("name"), 60)
            k["how_to_measure"] = _clamp_str(k.get("how_to_measure"), 200)
    # execution_plan.steps[*].action_button.label <= 30
    ep = data.get("execution_plan") or {}
    for step in ep.get("steps") or []:
        ab = (step or {}).get("action_button")
        if isinstance(ab, dict):
            ab["label"] = _clamp_str(ab.get("label"), 30)
    # monetization lists capped at 5
    mon = data.get("monetization") or {}
    if isinstance(mon, dict):
        for k in ("services", "products", "upsells"):
            if isinstance(mon.get(k), list):
                mon[k] = mon[k][:5]
    # options: pros/cons strings (no max but lists capped already), bias-flag-like overruns
    for o in data.get("options") or []:
        if not isinstance(o, dict):
            continue
        # Some agents put long expected_return strings; the schema doesn't cap
        # those but trim absurdly long ones to keep UI clean.
        if isinstance(o.get("expected_return"), str):
            o["expected_return"] = _clamp_str(o["expected_return"], 240)
        if isinstance(o.get("time_to_result"), str):
            o["time_to_result"] = _clamp_str(o["time_to_result"], 80)
    return data


async def _run_agent(name: str, system_prompt: str, user_text: str) -> Dict[str, Any]:
    try:
        raw = await _try_call_with_fallback(system_prompt, user_text, f"agent-{name.lower()}")
        return _parse_json_with_repair(raw)
    except Exception as e:
        logger.warning("agent %s failed: %s", name, str(e)[:200])
        return {"summary": f"{name} agent unavailable", "error": str(e)[:200]}


# -----------------------------------------------------------------------------
# Public entrypoint
# -----------------------------------------------------------------------------
async def analyze_decision_multiagent(
    decision_context: str,
    answers: List[Dict[str, Any]],
    factors: Optional[List[Dict[str, Any]]] = None,
    user_level: str = "intermediate",
) -> DecisionResult:
    """Run the 6-agent panel in parallel, then the synthesizer."""
    factors = factors or []
    factor_names = [f["name"] for f in factors if f.get("name")]
    factor_payload = [
        {"name": f["name"], "weight": f.get("weight", 50)}
        for f in factors
        if f.get("name")
    ]

    # Shared context every agent sees
    context_str = (
        f"DECISION:\n{decision_context}\n\n"
        f"USER ANSWERS (JSON):\n{json.dumps(answers, indent=2, default=str)}\n\n"
        f"FACTORS & WEIGHTS (JSON):\n{json.dumps(factor_payload, indent=2, default=str)}\n\n"
        f"USER_LEVEL: {user_level}\n\n"
        "Return JSON only."
    )

    # Stage 1: run all 6 agents in parallel
    strategic_t = _run_agent("Strategic", STRATEGIC_SYSTEM, context_str)
    financial_t = _run_agent("Financial", FINANCIAL_SYSTEM, context_str)
    risk_t = _run_agent("Risk", RISK_SYSTEM, context_str)
    execution_t = _run_agent("Execution", EXECUTION_SYSTEM, context_str)
    contrarian_t = _run_agent("Contrarian", CONTRARIAN_SYSTEM, context_str)
    optim_t = _run_agent("Optimization", OPTIMIZATION_SYSTEM, context_str)

    strategic, financial, risk, execution, contrarian, optim = await asyncio.gather(
        strategic_t, financial_t, risk_t, execution_t, contrarian_t, optim_t
    )

    # Stage 2: synthesizer
    synth_payload = {
        "decision": decision_context,
        "answers": answers,
        "factors": factor_payload,
        "user_level": user_level,
        "agents": {
            "Strategic": strategic,
            "Financial": financial,
            "Risk": risk,
            "Execution": execution,
            "Contrarian": contrarian,
            "Optimization": optim,
        },
    }
    synth_user_text = (
        "PANEL INPUTS (JSON):\n"
        + json.dumps(synth_payload, indent=2, default=str)
        + "\n\nProduce the final Decision JSON now. JSON only, no prose."
    )

    last_err: Optional[str] = None
    for attempt in range(2):
        try:
            raw = await _try_call_with_fallback(SYNTHESIZER_SYSTEM, synth_user_text, "synth")
            data = _parse_json_with_repair(raw)
            # Backfill factor_ratings if any option missed any factor
            for o in data.get("options", []) or []:
                ratings = o.get("factor_ratings") or {}
                for fn in factor_names:
                    if fn not in ratings:
                        ratings[fn] = 5
                o["factor_ratings"] = ratings
            data.setdefault("factors_used", factor_names)
            # --- Defensive backfills for required fields the LLM may omit ---
            # Different LLM families have different instruction-adherence patterns.
            # GPT-5.x reasoning models sometimes skip scalar fields in favor of
            # richer prose in nested structures. We cover the common misses so
            # one small omission doesn't force a retry (cost + latency hit).
            if "confidence" not in data or data.get("confidence") is None:
                # Derive a reasonable confidence from agent risk_score if available.
                rs = (risk or {}).get("risk_score_100")
                if isinstance(rs, (int, float)):
                    data["confidence"] = max(0, min(100, 100 - int(rs)))
                else:
                    data["confidence"] = 75
            if not data.get("goal"):
                data["goal"] = (strategic or {}).get("goal_restated") or decision_context[:140]
            if not data.get("reasoning"):
                data["reasoning"] = (
                    "Synthesis of the six-agent panel. "
                    + ((strategic or {}).get("summary", "")[:200])
                )
            # --- Defensive normalization to match DecisionResult caps ---
            # These caps match the Pydantic schema in ai_service.py; trimming
            # here prevents spurious ValidationErrors when the LLM is verbose.
            if isinstance(data.get("key_insights"), list):
                data["key_insights"] = data["key_insights"][:3]
            if isinstance(data.get("assumptions"), list):
                data["assumptions"] = data["assumptions"][:4]
            if isinstance(data.get("bias_flags"), list):
                data["bias_flags"] = data["bias_flags"][:3]
            if isinstance(data.get("key_reasons"), list):
                data["key_reasons"] = data["key_reasons"][:4]
            if isinstance(data.get("risks"), list):
                data["risks"] = data["risks"][:4]
            if isinstance(data.get("automation_layer"), list):
                data["automation_layer"] = data["automation_layer"][:3]
            if isinstance(data.get("kpis"), list):
                data["kpis"] = data["kpis"][:4]
            if isinstance(data.get("options"), list):
                # Schema allows 3-4 options; trim extras, let too-few fall through to retry.
                data["options"] = data["options"][:4]
                for o in data["options"]:
                    if isinstance(o.get("pros"), list):
                        o["pros"] = o["pros"][:3]
                    if isinstance(o.get("cons"), list):
                        o["cons"] = o["cons"][:3]
            # Clamp any string fields that GPT-5.2 commonly overruns
            data = _normalize_synth_payload(data)
            # Ensure agent_perspectives is present with the raw agent summaries
            if not data.get("agent_perspectives"):
                data["agent_perspectives"] = [
                    {"agent": "Strategic", "summary": strategic.get("summary", ""), "details": strategic},
                    {"agent": "Financial", "summary": financial.get("summary", ""), "details": financial},
                    {"agent": "Risk", "summary": risk.get("summary", ""), "details": risk},
                    {"agent": "Execution", "summary": execution.get("summary", ""), "details": execution},
                    {"agent": "Contrarian", "summary": contrarian.get("summary", ""), "details": contrarian},
                    {"agent": "Optimization", "summary": optim.get("summary", ""), "details": optim},
                ]
            return DecisionResult(**data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_err = str(e)[:400]
            synth_user_text += f"\n\nPrevious validation error: {last_err}\nFix strictly and return JSON only."
            continue
    raise RuntimeError(f"multi-agent synthesis failed: {last_err}")
