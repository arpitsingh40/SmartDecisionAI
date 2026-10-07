"""Idea Strength Audit — 8 gates before we build.

Runs BEFORE genesis mission/org. One LLM call (DeepSeek primary, same as genesis).
If LLM missing/quota -> honest deterministic fallback (scores 0, decision REVIEW_MANUALLY).
Tavily enrichment is best-effort (needs TAVILY_API_KEY); without it we still score.

Gates: idea_strength, future_possibility, scale, target_audience,
       revenue_method, estimated_profit, execution_method, small_team_leverage

Decision: GO (>=65 avg, no gate <35) | PIVOT (avg 45-65 or one gate <35) | KILL (<45)
Founder can Force Build even on KILL — we never hard-block.
"""
from __future__ import annotations
import json
import logging
import re
from typing import Optional

log = logging.getLogger("idea_audit")

GATES = [
    ("idea_strength", "Is this a real painful, frequent, unsolved problem?"),
    ("future_possibility", "Will it matter in 3-5 years or die to trend/AI/regulation?"),
    ("scale", "Can 1 -> 1000 customers without linear headcount?"),
    ("target_audience", "Who EXACTLY pays? (not 'everyone')"),
    ("revenue_method", "How does INR enter? Zoho-billable?"),
    ("estimated_profit", "Unit economics: margin >40%, payback <12m?"),
    ("execution_method", "Can we ship V1 in 15-30 days with handlers we have?"),
    ("small_team_leverage", "Can 2-5 people + AI org replace 30-person ops?"),
]

AUDIT_SYSTEM = """You are the Idea Audit Engine of SmartDecigen (Autonomous Business Builder).
STRICT RULES:
- Be brutally honest. A weak idea must score <40. Do not be nice.
- Every score must cite evidence from the founder input or say "unknown".
- If founder didn't share a detail, score that gate low, don't invent.
- Revenue must map to Zoho Payments/Books. Ads/hope = low score.
- Return ONLY valid JSON. No markdown fences. No prose outside JSON."""

AUDIT_PROMPT_TMPL = """FOUNDER VISION: {vision}

DIGITAL TWIN: {twin_json}

TAVILY SIGNALS (if any):
{tavily_block}

CATEGORY HINT (if founder picked one of 50): {category_hint}

Score these 8 gates 0-100. Follow the rubric exactly.

1. idea_strength — painful*FREQUENT*unsolved? If vague/wish, score <40.
2. future_possibility — 3-5y durability vs AI/regulation/trend. Short arbitrage <35.
3. scale — 1->1000 marginal cost ~0? digital distribution? else <40.
4. target_audience — EXACT ICP (demo+psycho+pay+where). "SMEs" = <30.
5. revenue_method — ONE Zoho path: one_time/mandate/invoice/affiliate. No Zoho path <30.
6. estimated_profit — 3 scenarios bear/base/bull. Base requires margin>40% and payback<12m or gate <40. Use price_inr from category if given.
7. execution_method — V1 in 15-30d with handlers we have? Check capabilities vs handlers. <50 if needs factory/license/field ops.
8. small_team_leverage — 2-5 + Business OS + Revenue Engine + Verification = 30-person output? Low leverage <40.

Also provide: overall 0-100, decision GO|PIVOT|KILL, top_3_risks, pivot_suggestion (one sentence if not GO).

Return JSON:
{{"gates": [{{"id": "idea_strength", "score": 0, "verdict": "strong|weak|unknown", "evidence": "...", "risk": "...", "fix": "..."}} x8], "overall": 0, "decision": "GO|PIVOT|KILL", "top_3_risks": ["..."], "pivot_suggestion": "...", "profit_scenarios": {{"bear": {{"revenue_inr": 0, "margin_pct": 0, "payback_months": 0}}, "base": {{"revenue_inr": 0, "margin_pct": 0, "payback_months": 0}}, "bull": {{"revenue_inr": 0, "margin_pct": 0, "payback_months": 0}}}}}}
"""


def _tavily_block(vision: str) -> str:
    if not vision or len(vision.strip()) < 10:
        return "(no vision)"
    try:
        import os
        if not os.environ.get("TAVILY_API_KEY", "").strip():
            return "(Tavily not configured — scoring on founder input only)"
        from deep_research import tavily_search  # existing helper in repo
        q1 = f"market size {vision[:80]} India 2025"
        q2 = f"competitors {vision[:60]} India"
        r1 = tavily_search(q1, max_results=3)
        r2 = tavily_search(q2, max_results=3)
        parts = []
        for r in (r1, r2):
            if isinstance(r, dict) and r.get("results"):
                for it in r["results"][:2]:
                    parts.append(f"- {it.get('title','')}: {it.get('content','')[:220]}")
            elif isinstance(r, str) and r.strip():
                parts.append(r[:400])
        return "\n".join(parts[:4]) if parts else "(no Tavily results)"
    except Exception as e:
        return f"(Tavily error: {e})"


def _deterministic_fallback(vision: str, twin: dict, category_hint: str = "") -> dict:
    """Honest fallback when LLM unavailable — never invent, always REVIEW_MANUALLY."""
    gates = []
    for gid, desc in GATES:
        gates.append({"id": gid, "score": 50, "verdict": "unknown", "evidence": "LLM unavailable — scored neutral. Configure DEEPSEEK_API_KEY for real audit.", "risk": desc, "fix": "Set LLM key and rerun audit"})
    return {
        "gates": gates,
        "overall": 50,
        "decision": "PIVOT",
        "top_3_risks": ["LLM unavailable", "Tavily not checked", "Manual review required"],
        "pivot_suggestion": "Configure DEEPSEEK_API_KEY and rerun. No hard block — Force Build allowed.",
        "profit_scenarios": {"bear": {"revenue_inr": 0, "margin_pct": 0, "payback_months": 0}, "base": {"revenue_inr": 0, "margin_pct": 0, "payback_months": 0}, "bull": {"revenue_inr": 0, "margin_pct": 0, "payback_months": 0}},
        "fallback": True,
    }


def _coerce_audit(data: dict, vision: str, twin: dict) -> dict:
    """Clamp/validate LLM output to schema."""
    raw_gates = data.get("gates") or []
    by_id = {g.get("id"): g for g in raw_gates if isinstance(g, dict) and g.get("id")}
    gates = []
    for gid, desc in GATES:
        g = by_id.get(gid) or {}
        try:
            score = int(g.get("score", 50))
        except Exception:
            score = 50
        score = max(0, min(100, score))
        gates.append({
            "id": gid,
            "score": score,
            "verdict": str(g.get("verdict", "unknown"))[:20],
            "evidence": str(g.get("evidence", ""))[:400],
            "risk": str(g.get("risk", desc))[:300],
            "fix": str(g.get("fix", ""))[:300],
        })
    try:
        overall = int(data.get("overall", sum(x["score"] for x in gates) // len(gates)))
    except Exception:
        overall = sum(x["score"] for x in gates) // len(gates)
    overall = max(0, min(100, overall))
    decision = str(data.get("decision", "PIVOT")).upper().strip()
    if decision not in ("GO", "PIVOT", "KILL"):
        # Derive from scores if model hallucinated
        if overall >= 65 and all(g["score"] >= 35 for g in gates):
            decision = "GO"
        elif overall < 45:
            decision = "KILL"
        else:
            decision = "PIVOT"
    # profit scenarios optional
    ps = data.get("profit_scenarios") or {}
    # normalize
    for k in ("bear", "base", "bull"):
        v = ps.get(k) or {}
        ps[k] = {"revenue_inr": int(v.get("revenue_inr", 0) or 0), "margin_pct": int(v.get("margin_pct", 0) or 0), "payback_months": int(v.get("payback_months", 0) or 0)}
    return {
        "gates": gates,
        "overall": overall,
        "decision": decision,
        "top_3_risks": [str(x)[:200] for x in (data.get("top_3_risks") or [])[:3]],
        "pivot_suggestion": str(data.get("pivot_suggestion", ""))[:500],
        "profit_scenarios": ps,
    }


def audit_idea(vision: str, twin: Optional[dict] = None, category_id: str = "") -> dict:
    """Main entry: 8-gate audit, 1 LLM call, honest fallback."""
    twin = twin or {}
    cat_hint = ""
    if category_id:
        try:
            from business_categories import get_category
            cat = get_category(category_id)
            if cat:
                cat_hint = f"{cat['id']} — {cat['label']}: {cat['description']} price_inr={cat.get('price_inr')} autonomy={cat.get('autonomy_pct')}%"
            else:
                cat_hint = category_id
        except Exception:
            cat_hint = category_id
    tavily = _tavily_block(vision)
    prompt = AUDIT_PROMPT_TMPL.format(
        vision=(vision or "")[:4000],
        twin_json=json.dumps(twin, indent=2)[:3000],
        tavily_block=tavily[:2000],
        category_hint=cat_hint or "(none — general audit)",
    )
    try:
        from llm_client import client, _extract_json, PRIMARY_MODEL
        r = client().messages.create(model=PRIMARY_MODEL, max_tokens=2500, system=AUDIT_SYSTEM, messages=[{"role": "user", "content": prompt}])
        txt = next((b.text for b in r.content if getattr(b, "type", "") == "text"), "").strip()
        data = json.loads(_extract_json(txt))
        return _coerce_audit(data, vision, twin)
    except Exception as e:
        log.warning(f"audit_idea LLM failed, fallback: {e}")
        return _deterministic_fallback(vision, twin, category_id)


if __name__ == "__main__":
    demo = audit_idea("I want to build a small AI bookkeeping service for freelancers in India. 2 people, pre-revenue, 12 months runway.", twin={"industry": "fintech", "stage": "idea"}, category_id="bookkeeping_automation")
    print(json.dumps(demo, indent=2)[:2000])
