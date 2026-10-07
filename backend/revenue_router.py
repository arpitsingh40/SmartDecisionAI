"""Revenue Engine API — autonomous profit pipelines."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional

from security import current_user
from db import members_col

router = APIRouter(prefix="/api/revenue", tags=["revenue"])


def _org_id(user: dict) -> str:
    m = members_col.find_one({"user_id": user["id"], "status": "active"})
    if not m:
        raise HTTPException(403, "Not in an organization")
    return m["org_id"]


def _require_owner(user: dict) -> str:
    m = members_col.find_one({"user_id": user["id"], "status": "active", "role": "owner"})
    if not m:
        raise HTTPException(403, "Only workspace owner can run revenue cycle")
    return m["org_id"]


class RunIn(BaseModel):
    pipelines: Optional[list[str]] = Field(default=None, max_length=10)


@router.get("/status")
def status(user: dict = Depends(current_user)):
    """Revenue dashboard — opportunities, recent runs, leads."""
    org_id = _org_id(user)
    from revenue_engine import revenue_status
    return revenue_status(org_id)


@router.get("/opportunities")
def opportunities(user: dict = Depends(current_user)):
    """Ranked monetization opportunities for this org."""
    org_id = _org_id(user)
    from revenue_engine import score_opportunities
    return {"opportunities": score_opportunities(org_id)}


@router.post("/run")
def run_cycle(body: RunIn, user: dict = Depends(current_user)):
    """Trigger a revenue cycle now (owner only)."""
    org_id = _require_owner(user)
    from revenue_engine import run_revenue_cycle, PIPELINES
    if body.pipelines:
        unknown = [p for p in body.pipelines if p not in PIPELINES]
        if unknown:
            raise HTTPException(422, f"Unknown pipelines: {unknown}. Valid: {list(PIPELINES.keys())}")
    return run_revenue_cycle(org_id, pipelines=body.pipelines)


@router.get("/runs")
def recent_runs(limit: int = 10, user: dict = Depends(current_user)):
    """Recent revenue cycle runs."""
    org_id = _org_id(user)
    from revenue_engine import REVENUE_RUNS_COL
    if REVENUE_RUNS_COL is None:
        return {"runs": []}
    runs = list(REVENUE_RUNS_COL.find({"org_id": org_id}, {"_id": 0}).sort("created_at", -1).limit(min(limit, 20)))
    return {"runs": runs}


@router.get("/leads")
def leads(limit: int = 20, user: dict = Depends(current_user)):
    """Leads discovered by the lead→pay pipeline."""
    org_id = _org_id(user)
    from revenue_engine import REVENUE_LEADS_COL
    if REVENUE_LEADS_COL is None:
        return {"leads": []}
    rows = list(REVENUE_LEADS_COL.find({"org_id": org_id}, {"_id": 0}).sort("updated_at", -1).limit(min(limit, 50)))
    return {"leads": rows}
