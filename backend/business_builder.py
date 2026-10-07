"""Business Builder — the Autonomous Business Builder engine.

Owns: vision -> audit (8 gates) -> blueprint -> lean org -> revenue wiring -> tasks.
Reuses genesis (twin/mission/org), idea_audit (gates), business_taxonomy (50),
revenue_engine (pipelines), execution (tasks/bridge).

Design: small team (2-5) + AI org (Business OS + Revenue Engine + Verification) = 30-person output.
Zoho is deferred per founder: all Zoho calls are honest-skipped when not configured
(Zoho configured after final testing). No test is blocked by missing Zoho.

Persistence: business_builds collection (one per build), business_ideas (optional history).
"""
from __future__ import annotations
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from db import db as _db

log = logging.getLogger("business_builder")

BUILDS_COL = _db.business_builds if _db is not None else None
IDEAS_COL = _db.business_ideas if _db is not None else None

if BUILDS_COL is not None:
    try:
        BUILDS_COL.create_index("id", unique=True)
        BUILDS_COL.create_index([("org_id", 1), ("created_at", -1)])
        BUILDS_COL.create_index([("user_id", 1), ("created_at", -1)])
    except Exception:
        pass
if IDEAS_COL is not None:
    try:
        IDEAS_COL.create_index("id", unique=True)
        IDEAS_COL.create_index([("user_id", 1), ("created_at", -1)])
    except Exception:
        pass


def _now():
    return datetime.now(timezone.utc)


def _now_iso():
    return _now().isoformat()


# ------------------------------------------------------------------
# Step 1: Audit (delegates to idea_audit.py)
# ------------------------------------------------------------------

def run_audit(vision: str, twin: Optional[dict] = None, category_id: str = "") -> dict:
    from idea_audit import audit_idea
    return audit_idea(vision, twin=twin, category_id=category_id)


# ------------------------------------------------------------------
# Step 2: Blueprint — validated strategy from audit + twin + category
# ------------------------------------------------------------------

BLUEPRINT_SYSTEM = """You are the Business Blueprint Engine of SmartDecigen.
You design a lean, Zoho-billable, handler-executable business in one pass.

RULES:
- Be specific to the founder's vision and audit. No generic startup advice.
- Revenue must be Zoho Payments (one_time/mandate) or Books invoice. No Stripe, no ads-only.
- Team is 2-5 humans + AI org (Business OS + Revenue Engine). No 20-person plan.
- Every revenue claim must have a Zoho path.
- Every execution step must map to a handler we have (GMAIL, ZOHO, TAVILY, GITHUB, NOTION, SLACK, FRANKFURTER) or be marked manual.
- Return ONLY valid JSON. No markdown fences."""

BLUEPRINT_PROMPT = """VISION: {vision}
TWIN: {twin_json}
AUDIT: {audit_json}
CATEGORY: {category_json}
CAPABILITIES: {caps_json}

Design the BUSINESS BLUEPRINT. Return JSON:
{{
  "positioning": "1 sentence: who, what, why now",
  "icp": {{"who": "...", "pain": "...", "willing_to_pay_inr": 0, "where_they_hang_out": "..."}},
  "offer": {{"name": "...", "price_inr": 0, "billing": "one_time|mandate|invoice", "what_you_deliver": "...", "zoho_path": "Payments hosted checkout | mandate | Books invoice"}},
  "profit_math": {{"price_inr": 0, "variable_cost_inr": 0, "contribution_margin_pct": 0, "cac_inr": 0, "payback_months": 0, "mrr_at_100_customers_inr": 0, "assumptions": "..."}},
  "execution_plan": {{"v1_days": 14, "milestones": ["..."], "handlers_used": ["GMAIL", "ZOHO"], "manual_gaps": ["..."]}},
  "lean_org": {{"humans_needed": 2, "ai_executives": ["Research", "Product", "Growth"], "why_small_team_works": "..."}},
  "autonomous_loops": ["which revenue_engine pipelines run on cron and what they do"],
  "next_3_actions": ["concrete next 3 actions for the founder"]
}}
"""


def build_blueprint(vision: str, twin: dict, audit: dict, category_id: str = "") -> dict:
    # Category context
    cat_json = "{}"
    caps_json = "[]"
    try:
        from business_categories import get_category
        cat = get_category(category_id) if category_id else None
        if cat:
            cat_json = json.dumps({k: cat[k] for k in ("id", "label", "revenue_method", "price_inr", "autonomy_pct", "description") if k in cat}, indent=2)
    except Exception:
        pass
    try:
        from genesis import map_capabilities
        caps = map_capabilities(twin or {})
        caps_json = json.dumps(caps, indent=2)
    except Exception:
        pass
    prompt = BLUEPRINT_PROMPT.format(
        vision=(vision or "")[:3500],
        twin_json=json.dumps(twin or {}, indent=2)[:2500],
        audit_json=json.dumps(audit or {}, indent=2)[:3500],
        category_json=cat_json[:1500],
        caps_json=caps_json[:2000],
    )
    try:
        from llm_client import client, _extract_json, PRIMARY_MODEL
        r = client().messages.create(model=PRIMARY_MODEL, max_tokens=2500, system=BLUEPRINT_SYSTEM, messages=[{"role": "user", "content": prompt}])
        txt = next((b.text for b in r.content if getattr(b, "type", "") == "text"), "").strip()
        data = json.loads(_extract_json(txt))
        # Minimal validation
        if not isinstance(data.get("positioning"), str) or not data.get("offer"):
            raise ValueError("blueprint missing positioning/offer")
        return data
    except Exception as e:
        log.warning(f"build_blueprint fallback: {e}")
        return {
            "positioning": f"Lean { (twin or {}).get('industry','business')} offer for the ICP in the vision — configure LLM for tailored blueprint.",
            "icp": {"who": "ICP from vision", "pain": "unknown", "willing_to_pay_inr": 999, "where_they_hang_out": "unknown"},
            "offer": {"name": "Starter Offer", "price_inr": 999, "billing": "one_time", "what_you_deliver": "V1 described in vision", "zoho_path": "Payments hosted checkout"},
            "profit_math": {"price_inr": 999, "variable_cost_inr": 50, "contribution_margin_pct": 95, "cac_inr": 0, "payback_months": 0, "mrr_at_100_customers_inr": 0, "assumptions": "LLM unavailable — configure DEEPSEEK_API_KEY for real math"},
            "execution_plan": {"v1_days": 21, "milestones": ["Ship V1"], "handlers_used": ["GMAIL", "ZOHO"], "manual_gaps": []},
            "lean_org": {"humans_needed": 2, "ai_executives": ["Research", "Product", "Growth"], "why_small_team_works": "Business OS + Revenue Engine automate ops"},
            "autonomous_loops": ["invoicing (Zoho Books overdue -> Gmail reminder, 6h cron)"],
            "next_3_actions": ["Validate ICP with 10 conversations", "Create Zoho product + checkout link", "Ship V1 landing page"],
            "fallback": True,
        }


# ------------------------------------------------------------------
# Step 3: Build org (lean, stage-capped) + revenue wiring
# ------------------------------------------------------------------

def _lean_division_cap(twin: dict) -> int:
    stage = (twin or {}).get("stage", "").lower()
    if stage in ("idea", "pre-revenue"):
        return 3
    if stage in ("growth",):
        return 5
    return 7


def create_build_record(user_id: str, org_id: str, vision: str, category_id: str, twin: dict, audit: dict, blueprint: dict, genesis_ref: dict | None = None) -> dict:
    """Persist a build. Returns the doc."""
    doc = {
        "id": f"build_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "org_id": org_id,
        "vision": (vision or "")[:4000],
        "category_id": category_id or None,
        "twin": twin or {},
        "audit": audit or {},
        "blueprint": blueprint or {},
        "genesis": genesis_ref or {},
        "status": "blueprinted",  # audited -> blueprinted -> org_created -> tasks_queued -> running
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    if BUILDS_COL is not None:
        try:
            BUILDS_COL.insert_one(dict(doc))
        except Exception as e:
            log.warning(f"build persist failed: {e}")
    if IDEAS_COL is not None and vision:
        try:
            IDEAS_COL.insert_one({"id": f"idea_{uuid.uuid4().hex[:10]}", "user_id": user_id, "org_id": org_id, "vision": vision[:2000], "category_id": category_id or None, "audit": audit or {}, "created_at": _now_iso()})
        except Exception:
            pass
    return doc


def ensure_builder_startup():
    if BUILDS_COL is not None:
        try:
            BUILDS_COL.create_index("id", unique=True)
            BUILDS_COL.create_index([("org_id", 1), ("created_at", -1)])
        except Exception:
            pass
    if IDEAS_COL is not None:
        try:
            IDEAS_COL.create_index("id", unique=True)
        except Exception:
            pass


if __name__ == "__main__":
    print("OK — business_builder module loaded")
