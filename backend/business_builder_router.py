"""Business Builder API — Autonomous Business Builder.

Flow:
  Vision (text + optional category from 50)
    -> POST /audit       8 gates, GO/PIVOT/KILL (1 LLM call, Tavily best-effort)
    -> POST /blueprint   positioning + ICP + offer + profit math + lean org
    -> POST /build       persists build, optionally triggers Genesis (twin->mission->org)
    -> GET  /            list builds / categories

Zoho is deferred per founder: all money paths are honest-skipped when Zoho not
configured (no test blocked). Autonomous loops run after final testing.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional

from security import current_user
from db import members_col

router = APIRouter(prefix="/api/business-builder", tags=["business-builder"])


def _org_id_for(user: dict) -> Optional[str]:
    m = members_col.find_one({"user_id": user["id"], "status": "active"})
    return m["org_id"] if m else None


# ------------------------------------------------------------------
# Categories
# ------------------------------------------------------------------

@router.get("/categories")
def list_categories(group: Optional[str] = None, user: dict = Depends(current_user)):
    from business_categories import list_categories as _list
    cats = _list(group=group)
    return {"count": len(cats), "categories": cats}


@router.get("/categories/{category_id}")
def get_category(category_id: str, user: dict = Depends(current_user)):
    from business_categories import get_category, autonomy_report
    cat = get_category(category_id)
    if not cat:
        raise HTTPException(404, "Unknown category")
    return {"category": cat, "autonomy": autonomy_report(category_id)}


# ------------------------------------------------------------------
# Audit (8 gates)
# ------------------------------------------------------------------

class AuditIn(BaseModel):
    vision: str = Field(min_length=10, max_length=5000)
    category_id: Optional[str] = Field(default=None, max_length=80)


@router.post("/audit")
def audit(body: AuditIn, user: dict = Depends(current_user)):
    """Score the idea on 8 gates before we build. Honest when LLM/Tavily missing."""
    if body.category_id:
        from business_categories import get_category
        if not get_category(body.category_id):
            raise HTTPException(422, f"Unknown category_id: {body.category_id}")
    # Build twin first (reuses genesis.extract_twin, 1 LLM call) — best-effort
    twin = {}
    try:
        from genesis import extract_twin
        twin = extract_twin(body.vision).get("twin", {})
    except Exception:
        pass
    from business_builder import run_audit
    result = run_audit(body.vision, twin=twin, category_id=body.category_id or "")
    return {"vision": body.vision[:2000], "category_id": body.category_id, "twin": twin, **result}


# ------------------------------------------------------------------
# Blueprint
# ------------------------------------------------------------------

class BlueprintIn(BaseModel):
    vision: str = Field(min_length=10, max_length=5000)
    category_id: Optional[str] = Field(default=None, max_length=80)
    twin: Optional[dict] = None
    audit: Optional[dict] = None


@router.post("/blueprint")
def blueprint(body: BlueprintIn, user: dict = Depends(current_user)):
    """Produce a lean, Zoho-billable blueprint from vision + audit."""
    if body.category_id:
        from business_categories import get_category
        if not get_category(body.category_id):
            raise HTTPException(422, f"Unknown category_id: {body.category_id}")
    twin = body.twin or {}
    if not twin:
        try:
            from genesis import extract_twin
            twin = extract_twin(body.vision).get("twin", {})
        except Exception:
            twin = {}
    audit = body.audit
    if not audit:
        from business_builder import run_audit
        audit = run_audit(body.vision, twin=twin, category_id=body.category_id or "")
    from business_builder import build_blueprint
    bp = build_blueprint(body.vision, twin=twin, audit=audit, category_id=body.category_id or "")
    return {"vision": body.vision[:2000], "category_id": body.category_id, "twin": twin, "audit": audit, "blueprint": bp}


# ------------------------------------------------------------------
# Build (persist + optional genesis)
# ------------------------------------------------------------------

class BuildIn(BaseModel):
    vision: str = Field(min_length=10, max_length=5000)
    category_id: Optional[str] = Field(default=None, max_length=80)
    audit: Optional[dict] = None
    blueprint: Optional[dict] = None
    twin: Optional[dict] = None
    force: bool = False  # allow build even if audit == KILL


@router.post("/build")
def build_business(body: BuildIn, user: dict = Depends(current_user)):
    """Persist a build record (audit + blueprint). Optionally enqueue Genesis tasks."""
    if body.category_id:
        from business_categories import get_category
        if not get_category(body.category_id):
            raise HTTPException(422, f"Unknown category_id: {body.category_id}")
    org_id = _org_id_for(user)
    if not org_id:
        raise HTTPException(403, "Create a workspace first (Team -> Create workspace)")

    twin = body.twin or {}
    if not twin:
        try:
            from genesis import extract_twin
            twin = extract_twin(body.vision).get("twin", {})
        except Exception:
            twin = {}

    audit = body.audit
    if not audit:
        from business_builder import run_audit
        audit = run_audit(body.vision, twin=twin, category_id=body.category_id or "")

    # Soft gate: KILL without force -> 409 with guidance
    if audit.get("decision") == "KILL" and not body.force:
        raise HTTPException(409, detail={"message": "Audit is KILL. Fix top risks or pass force=true to build anyway.", "audit": audit})

    blueprint = body.blueprint
    if not blueprint:
        from business_builder import build_blueprint
        blueprint = build_blueprint(body.vision, twin=twin, audit=audit, category_id=body.category_id or "")

    # Lean cap: idea/pre-revenue -> max 3 divisions when we later trigger Genesis org
    try:
        from business_builder import _lean_division_cap
        cap = _lean_division_cap(twin)
        blueprint["_lean_cap"] = cap
    except Exception:
        pass

    from business_builder import create_build_record
    doc = create_build_record(user_id=user["id"], org_id=org_id, vision=body.vision, category_id=body.category_id or "", twin=twin, audit=audit, blueprint=blueprint)

    # Revenue wiring (Zoho-honest): record opportunity in revenue_engine without requiring Zoho
    # Real Zoho calls happen only inside handlers when configured; this just queues guidance tasks
    try:
        from revenue_engine import score_opportunities
        opps = score_opportunities(org_id)
        doc["opportunities_preview"] = opps[:3]
    except Exception:
        pass

    return {"build": doc, "message": f"Build {doc['id']} blueprinted. Next: run Genesis wizard to create the lean org, then the Business OS + Revenue Engine run autonomously."}


@router.get("/builds")
def list_builds(limit: int = 20, user: dict = Depends(current_user)):
    org_id = _org_id_for(user)
    if not org_id:
        return {"builds": []}
    from business_builder import BUILDS_COL
    if BUILDS_COL is None:
        return {"builds": []}
    rows = list(BUILDS_COL.find({"org_id": org_id}, {"_id": 0}).sort("created_at", -1).limit(min(limit, 50)))
    return {"builds": rows}


@router.get("/builds/{build_id}")
def get_build(build_id: str, user: dict = Depends(current_user)):
    from business_builder import BUILDS_COL
    if BUILDS_COL is None:
        raise HTTPException(404, "Not found")
    doc = BUILDS_COL.find_one({"id": build_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Build not found")
    # Org isolation
    org_id = _org_id_for(user)
    if doc.get("org_id") != org_id:
        raise HTTPException(403, "Not your build")
    return {"build": doc}
