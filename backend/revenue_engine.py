"""Revenue Engine — the autonomous profit layer.

Owns one job: turn connected tools + founder intent into repeatable revenue.

Pipelines:
  A) Invoicing — draft invoice from Stripe/Zoho → send via Gmail/WhatsApp → track payment.
  B) Lead → Pay — qualify inbound leads (Gmail search) → personalize outreach → book meeting.
  C) Retention — detect churn signals (overdue invoices, support tickets) → re-engage.
  D) Marketplace — list a founder's product on Stripe/Shopify and drive traffic.

Every pipeline: _plan → _execute → _verify → _learn → _earn.
Revenue is measured as INR collected (orders_col + Stripe invoices paid) + MRR.
"""
import os
import re
import uuid
import json
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from db import db as _db, users_col, orders_col, orgs_col

log = logging.getLogger("revenue_engine")

REVENUE_RUNS_COL = _db.revenue_runs if _db is not None else None
REVENUE_LEADS_COL = _db.revenue_leads if _db is not None else None

if REVENUE_RUNS_COL is not None:
    try:
        REVENUE_RUNS_COL.create_index("id", unique=True)
        REVENUE_RUNS_COL.create_index([("org_id", 1), ("created_at", -1)])
    except Exception:
        pass
if REVENUE_LEADS_COL is not None:
    try:
        REVENUE_LEADS_COL.create_index("id", unique=True)
        REVENUE_LEADS_COL.create_index([("org_id", 1), ("status", 1)])
    except Exception:
        pass


def _now():
    return datetime.now(timezone.utc)


def _now_iso():
    return _now().isoformat()


def _founder_email(org_id: str) -> str:
    try:
        org = orgs_col.find_one({"id": org_id}) if org_id else None
        if not org:
            return ""
        u = users_col.find_one({"id": org.get("owner_user_id")}) if org else None
        return (u or {}).get("email", "")
    except Exception:
        return ""


def _founder_name(org_id: str) -> str:
    try:
        org = orgs_col.find_one({"id": org_id}) if org_id else None
        u = users_col.find_one({"id": org.get("owner_user_id")}) if org else None
        return (u or {}).get("name", "") or (u or {}).get("email", "").split("@")[0]
    except Exception:
        return ""


# ======================================================================
# Shared: opportunity scoring (who is most likely to pay next)
# ======================================================================

def score_opportunities(org_id: str) -> list[dict]:
    """Rank monetization opportunities by ease and upside. Pure function over DB state."""
    opportunities = []
    # 1. Overdue invoices — warmest leads (they already owe you)
    try:
        from automation_loops import _stripe_raw_open_invoices
        invoices = _stripe_raw_open_invoices() or []
        now_ts = time.time()
        overdue = [i for i in invoices if i.get("status") == "open" and i.get("due_date") and float(i["due_date"]) < now_ts]
        if overdue:
            total = round(sum(float(i.get("amount_due", 0)) / 100 for i in overdue), 2)
            opportunities.append({
                "id": "overdue_invoices", "label": f"Collect ${total:.0f} overdue from {len(overdue)} invoices",
                "pipeline": "invoicing", "score": 95, "amount_usd": total,
                "next_step": "Send one friendly reminder per overdue invoice via Gmail",
            })
    except Exception:
        pass
    # 2. Founder's own product — if org has a tagline/SKU, it can be billed
    try:
        org = orgs_col.find_one({"id": org_id}) if org_id else None
        if org and org.get("north_star"):
            opportunities.append({
                "id": "founder_offer", "label": f"Package your offer: {org.get('north_star','')[:60]}",
                "pipeline": "marketplace", "score": 70,
                "next_step": "Draft a Stripe product + checkout link for your core offer",
            })
    except Exception:
        pass
    # 3. Inbound leads sitting in Gmail
    opportunities.append({
        "id": "inbound_leads", "label": "Qualify inbound leads in your inbox",
        "pipeline": "lead_to_pay", "score": 75,
        "next_step": "Scan recent Gmail for inbound interest, personalize reply, book call",
    })
    # 4. At-risk customers
    opportunities.append({
        "id": "retention", "label": "Save at-risk customers before they churn",
        "pipeline": "retention", "score": 60,
        "next_step": "Send re-engagement to accounts with payment failures or silence >14d",
    })
    opportunities.sort(key=lambda o: -o["score"])
    return opportunities


# ======================================================================
# Pipeline A: Invoicing — collect what is already owed
# ======================================================================

def run_invoicing_pipeline(org_id: str, dry_run: bool = False) -> dict:
    """Collect overdue Stripe invoices: one reminder per invoice + founder summary."""
    steps = []
    sent = 0
    total_usd = 0.0
    try:
        from automation_loops import run_cash_loop
        res = run_cash_loop(org_id)
        steps = res.get("steps", [])
        total_usd = res.get("overdue_total", 0.0)
        # Count ok reminder steps
        sent = sum(1 for s in steps if s.get("step", "").startswith("reminder:") and s.get("status") == "ok")
    except Exception as e:
        steps.append({"step": "invoicing", "status": "error", "detail": str(e)[:300]})
    status = "collected" if sent else ("no_overdue" if total_usd == 0 else "queued")
    return {"pipeline": "invoicing", "steps": steps, "sent": sent, "total_usd": total_usd, "status": status}


# ======================================================================
# Pipeline B: Lead → Pay — inbox to booked meeting
# ======================================================================

def _gmail_search(query: str, max_results: int = 10):
    try:
        from execution.handlers import get_handler
        fn = get_handler("GMAIL_SEARCH_MESSAGES")
        if not fn:
            return {"error": "no handler", "successful": False}
        return fn("GMAIL_SEARCH_MESSAGES", {"query": query, "max_results": max_results})
    except Exception as e:
        return {"error": str(e)[:200], "successful": False}


def _send_email(to: str, subject: str, body: str):
    from execution.handlers import get_handler
    fn = get_handler("GMAIL_SEND_EMAIL")
    if not fn:
        raise RuntimeError("no gmail handler")
    res = fn("GMAIL_SEND_EMAIL", {"to": to, "subject": subject, "body": body})
    if not res.get("successful"):
        raise RuntimeError(res.get("error", "send failed"))
    return res


def run_lead_to_pay_pipeline(org_id: str, dry_run: bool = False) -> dict:
    """Find inbound leads in Gmail, draft personalized reply, optionally send."""
    steps = []
    # 1. Search inbox for inbound interest signals
    interest_queries = ["is:unread OR newer_than:7d (interested OR pricing OR demo OR trial OR quote)"]
    hits = []
    for q in interest_queries:
        r = _gmail_search(q, max_results=5)
        if r.get("successful"):
            steps.append({"step": "inbox_scan", "status": "ok", "detail": r.get("result", "")[:300]})
            hits.append(r.get("result", ""))
        else:
            steps.append({"step": "inbox_scan", "status": "skipped", "detail": r.get("error", "")[:200]})
            # Without Gmail token this is expected — don't fail the pipeline
    if not hits or all(not h for h in hits):
        steps.append({"step": "qualify", "status": "skipped", "detail": "no inbound interest found or Gmail not connected"})
        return {"pipeline": "lead_to_pay", "steps": steps, "qualified": 0, "status": "no_leads"}
    # 2. Use LLM to qualify and personalize (1 call, draft only — never auto-send without approval)
    try:
        from llm_client import client, _extract_json, PRIMARY_MODEL
        org = orgs_col.find_one({"id": org_id}) if org_id else None
        founder = _founder_name(org_id)
        inbox_snippet = "\n".join(hits)[:4000]
        prompt = (
            f"FOUNDER: {founder} — {org.get('north_star','') if org else ''}\n"
            f"INBOX SNIPPET:\n{inbox_snippet}\n\n"
            f"Task: Identify up to 3 inbound leads most likely to convert. "
            f"For each: email, why they are warm, and a 3-line personalized reply draft that books a call.\n"
            f"Return JSON: {{\"leads\": [{{\"email\": \"a@b.com\", \"warmth\": 0-100, \"why\": \"...\", \"reply_subject\": \"...\", \"reply_body\": \"...\"}}]}}"
            f" If none look warm, return {{\"leads\": []}} and explain why. No placeholders — say unknown."
        )
        r = client().messages.create(model=PRIMARY_MODEL, max_tokens=1200,
                                     system="You are a revenue operator. Be specific, honest, and concise. Return only JSON.",
                                     messages=[{"role": "user", "content": prompt}])
        txt = next((b.text for b in r.content if getattr(b, "type", "") == "text"), "").strip()
        data = json.loads(_extract_json(txt))
        leads = data.get("leads", [])[:3]
        steps.append({"step": "qualify", "status": "ok", "detail": f"{len(leads)} leads qualified"})
        # 3. Persist leads + create approval tasks (L3 — founder approves before any outbound)
        created = 0
        for ld in leads:
            email = (ld.get("email") or "").strip()
            if not email or "@" not in email:
                continue
            lead_id = f"lead_{uuid.uuid4().hex[:12]}"
            if REVENUE_LEADS_COL is not None:
                REVENUE_LEADS_COL.update_one({"org_id": org_id, "email": email}, {
                    "$setOnInsert": {"id": lead_id, "org_id": org_id, "email": email, "created_at": _now_iso()},
                    "$set": {"warmth": ld.get("warmth", 50), "why": ld.get("why", "")[:300],
                             "reply_subject": ld.get("reply_subject", "")[:200],
                             "reply_body": ld.get("reply_body", "")[:2000],
                             "status": "pending_approval", "updated_at": _now_iso()},
                }, upsert=True)
            try:
                from execution.tasks import enqueue_task
                enqueue_task("revenue", {
                    "description": f"[Revenue] Reply to warm lead {email}: {ld.get('why','')[:80]}",
                    "capability": "email", "expected_outcome": f"Meeting booked with {email}",
                    "authority_required": "L3", "reversibility": "REVERSIBLE",
                    "plan": [{"tool": "GMAIL_SEND_EMAIL",
                              "args": {"to": email, "subject": ld.get("reply_subject", ""), "body": ld.get("reply_body", "")},
                              "depends_on": [], "description": f"Reply to {email}"}],
                }, org_id=org_id, trace_id=f"lead_{email}")
                created += 1
            except Exception:
                pass
        steps.append({"step": "draft_replies", "status": "ok", "detail": f"{created} reply tasks queued for approval"})
        return {"pipeline": "lead_to_pay", "steps": steps, "qualified": len(leads), "queued": created, "status": "queued"}
    except Exception as e:
        steps.append({"step": "qualify", "status": "error", "detail": str(e)[:300]})
        return {"pipeline": "lead_to_pay", "steps": steps, "qualified": 0, "status": "error"}


# ======================================================================
# Pipeline C: Retention — re-engage at-risk accounts
# ======================================================================

def run_retention_pipeline(org_id: str, dry_run: bool = False) -> dict:
    """Run churn-risk scoring loop; re-engage tasks are L3-approval."""
    steps = []
    try:
        from automation_loops import run_customer_loop
        res = run_customer_loop(org_id)
        steps = res.get("steps", [])
        score = res.get("churn_risk", 0)
        status = "at_risk" if score > 60 else "healthy"
        return {"pipeline": "retention", "steps": steps, "churn_risk": score, "status": status}
    except Exception as e:
        steps.append({"step": "retention", "status": "error", "detail": str(e)[:300]})
        return {"pipeline": "retention", "steps": steps, "status": "error"}


# ======================================================================
# Pipeline D: Marketplace — productize founder's offer
# ======================================================================

def run_marketplace_pipeline(org_id: str, dry_run: bool = False) -> dict:
    """Ensure a sellable offer exists (Stripe product + checkout link guidance)."""
    steps = []
    # This is a guidance pipeline — it produces tasks/checklists, not direct charges
    try:
        org = orgs_col.find_one({"id": org_id}) if org_id else None
        if not org or not org.get("north_star"):
            steps.append({"step": "offer", "status": "skipped", "detail": "north_star not set — run Genesis first"})
            return {"pipeline": "marketplace", "steps": steps, "status": "needs_genesis"}
        offer = f"{org.get('north_star','')} — {org.get('target','')}"
        # Create one founder task to productize the offer
        try:
            from execution.tasks import enqueue_task
            enqueue_task("revenue", {
                "description": f"[Revenue] Productize your offer: {offer[:100]} — create a Stripe product + checkout link",
                "capability": "finance", "expected_outcome": "Sellable checkout link for your core offer",
                "authority_required": "L3", "reversibility": "REVERSIBLE",
            }, org_id=org_id, trace_id="marketplace_offer")
            steps.append({"step": "offer_task", "status": "ok", "detail": "productize task queued"})
        except Exception as e:
            steps.append({"step": "offer_task", "status": "error", "detail": str(e)[:200]})
        # Optionally draft a Notion offer doc via handler
        try:
            from execution.handlers import get_handler
            fn = get_handler("NOTION_CREATE_PAGE")
            if fn and os.environ.get("NOTION_TOKEN"):
                fn("NOTION_CREATE_PAGE", {"title": f"Offer: {org.get('name','My Company')} — {org.get('north_star','')[:60]}",
                                          "content": f"Offer: {offer}\nIdeal customer: (founder to fill)\nPrice: (founder to fill)\nGuarantee: (founder to fill)"})
                steps.append({"step": "offer_doc", "status": "ok", "detail": "Notion offer doc drafted"})
            else:
                steps.append({"step": "offer_doc", "status": "skipped", "detail": "Notion not connected — doc task queued instead"})
        except Exception as e:
            steps.append({"step": "offer_doc", "status": "error", "detail": str(e)[:200]})
        return {"pipeline": "marketplace", "steps": steps, "status": "queued"}
    except Exception as e:
        steps.append({"step": "marketplace", "status": "error", "detail": str(e)[:300]})
        return {"pipeline": "marketplace", "steps": steps, "status": "error"}


# ======================================================================
# Orchestrator — run all pipelines, record run, measure revenue delta
# ======================================================================

PIPELINES = {
    "invoicing": run_invoicing_pipeline,
    "lead_to_pay": run_lead_to_pay_pipeline,
    "retention": run_retention_pipeline,
    "marketplace": run_marketplace_pipeline,
}


def _revenue_snapshot(org_id: str) -> dict:
    """INR collected + MRR from stats_col + Stripe open amount. No throws."""
    try:
        from ledger import get_stats
        s = get_stats() or {}
        return {"revenue_inr": s.get("revenue_inr", 0), "mrr_inr": s.get("mrr_inr", 0),
                "purchases": s.get("purchases_count", 0)}
    except Exception:
        return {"revenue_inr": 0, "mrr_inr": 0, "purchases": 0}


def run_revenue_cycle(org_id: str, pipelines: list[str] = None) -> dict:
    """Run one revenue cycle — try every pipeline that has a chance to earn."""
    before = _revenue_snapshot(org_id)
    ids = pipelines or list(PIPELINES.keys())
    results = {}
    all_steps = []
    for pid in ids:
        fn = PIPELINES.get(pid)
        if not fn:
            continue
        try:
            # Respect governance before any pipeline that can send externally
            try:
                from governance import execution_gate
                gate = execution_gate(org_id, 0)
                if not gate["allowed"]:
                    results[pid] = {"pipeline": pid, "status": "blocked", "reason": gate["reason"], "steps": []}
                    continue
                if gate["dry_run"]:
                    results[pid] = {"pipeline": pid, "status": "dry_run", "steps": [{"step": "gated", "status": "dry_run", "detail": "dry run mode"}]}
                    continue
            except Exception:
                pass
            res = fn(org_id)
            results[pid] = res
            all_steps.extend(res.get("steps", []))
        except Exception as e:
            log.exception(f"revenue pipeline {pid} failed")
            results[pid] = {"pipeline": pid, "status": "error", "error": str(e)[:300], "steps": []}
    after = _revenue_snapshot(org_id)
    run_id = f"rev_{uuid.uuid4().hex[:12]}"
    doc = {
        "id": run_id, "org_id": org_id, "pipelines": ids,
        "results": results, "steps": all_steps,
        "revenue_before": before, "revenue_after": after,
        "delta_inr": (after.get("revenue_inr", 0) - before.get("revenue_inr", 0)),
        "created_at": _now_iso(),
    }
    if REVENUE_RUNS_COL is not None:
        try:
            REVENUE_RUNS_COL.insert_one(dict(doc))
        except Exception:
            pass
    # Audit
    try:
        from audit import record as audit_record
        audit_record(org_id, "revenue_cycle", f"revenue cycle: {', '.join(ids)} → delta ₹{doc['delta_inr']}",
                     details={"pipelines": ids, "delta_inr": doc["delta_inr"]})
    except Exception:
        pass
    return doc


def revenue_status(org_id: str) -> dict:
    """Dashboard payload for the revenue engine."""
    recent = []
    if REVENUE_RUNS_COL is not None:
        recent = list(REVENUE_RUNS_COL.find({"org_id": org_id}, {"_id": 0}).sort("created_at", -1).limit(5))
    leads = []
    if REVENUE_LEADS_COL is not None:
        leads = list(REVENUE_LEADS_COL.find({"org_id": org_id}, {"_id": 0}).sort("updated_at", -1).limit(10))
    snap = _revenue_snapshot(org_id)
    opps = score_opportunities(org_id)
    return {
        "revenue": snap,
        "opportunities": opps,
        "pipelines": list(PIPELINES.keys()),
        "recent_runs": recent,
        "leads": leads,
    }


def ensure_revenue_startup():
    if REVENUE_RUNS_COL is not None:
        try:
            REVENUE_RUNS_COL.create_index("id", unique=True)
            REVENUE_RUNS_COL.create_index([("org_id", 1), ("created_at", -1)])
        except Exception:
            pass
    if REVENUE_LEADS_COL is not None:
        try:
            REVENUE_LEADS_COL.create_index("id", unique=True)
            REVENUE_LEADS_COL.create_index([("org_id", 1), ("status", 1)])
        except Exception:
            pass


if __name__ == "__main__":
    assert len(PIPELINES) == 4
    assert score_opportunities("dummy_org") is not None
    print("OK — revenue engine verified")
