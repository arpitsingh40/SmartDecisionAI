from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timezone

from ai_service import (
    generate_followups,
    analyze_decision,
    AnalyzePayload,
    FollowUpsResponse,
    DecisionResult,
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Smart Decision AI", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ------------------ Models ------------------
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class GuestSessionResponse(BaseModel):
    guest_id: str

class DecisionContextRequest(BaseModel):
    decision: str = Field(min_length=4, max_length=500)

class SaveDecisionRequest(BaseModel):
    guest_id: str
    title: str
    decision: str
    answers: List[Dict[str, Any]] = []
    result: Dict[str, Any]

class DecisionSummary(BaseModel):
    id: str
    title: str
    decision: str
    created_at: datetime
    best_option_title: Optional[str] = None
    best_option_score: Optional[int] = None
    confidence: Optional[int] = None

class DecisionDocument(BaseModel):
    id: str
    guest_id: str
    title: str
    decision: str
    answers: List[Dict[str, Any]]
    result: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ------------------ Helpers ------------------
def _strip_mongo(doc: dict) -> dict:
    if not doc:
        return doc
    doc.pop("_id", None)
    # convert ISO strings back to datetime for Pydantic
    for k in ("created_at", "updated_at"):
        if k in doc and isinstance(doc[k], str):
            try:
                doc[k] = datetime.fromisoformat(doc[k])
            except ValueError:
                pass
    return doc


# ------------------ Routes ------------------
@api_router.get("/")
async def root():
    return {"message": "Smart Decision AI API is up", "version": "1.0.0"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.model_dump())
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks


# ---- Guest session ----
@api_router.post("/guest/session", response_model=GuestSessionResponse)
async def create_guest_session():
    guest_id = f"guest_{uuid.uuid4().hex[:12]}"
    return GuestSessionResponse(guest_id=guest_id)


# ---- Decision engine ----
@api_router.post("/decisions/followups", response_model=FollowUpsResponse)
async def api_followups(payload: DecisionContextRequest):
    try:
        result = await generate_followups(payload.decision)
        return result
    except Exception as e:
        logger.exception("followups error")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)[:200]}")

@api_router.post("/decisions/analyze", response_model=DecisionResult)
async def api_analyze(payload: AnalyzePayload):
    try:
        result = await analyze_decision(payload.decision, payload.answers)
        return result
    except Exception as e:
        logger.exception("analyze error")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)[:200]}")


# ---- Saved decisions CRUD ----
@api_router.post("/decisions", response_model=DecisionDocument)
async def save_decision(payload: SaveDecisionRequest):
    if not payload.guest_id.startswith("guest_"):
        raise HTTPException(status_code=400, detail="Invalid guest_id")
    now = datetime.now(timezone.utc)
    doc = DecisionDocument(
        id=str(uuid.uuid4()),
        guest_id=payload.guest_id,
        title=payload.title or payload.decision[:60],
        decision=payload.decision,
        answers=payload.answers,
        result=payload.result,
        created_at=now,
        updated_at=now,
    )
    mongo_doc = doc.model_dump()
    mongo_doc['created_at'] = now.isoformat()
    mongo_doc['updated_at'] = now.isoformat()
    await db.decisions.insert_one(mongo_doc)
    return doc


@api_router.get("/decisions", response_model=List[DecisionSummary])
async def list_decisions(guest_id: str = Query(..., min_length=8)):
    cursor = db.decisions.find({"guest_id": guest_id}, {"_id": 0}).sort("created_at", -1).limit(200)
    items = await cursor.to_list(200)
    out: List[DecisionSummary] = []
    for it in items:
        _strip_mongo(it)
        result = it.get("result") or {}
        options = result.get("options") or []
        best_id = result.get("best_option_id")
        best = next((o for o in options if o.get("id") == best_id), options[0] if options else None)
        out.append(
            DecisionSummary(
                id=it["id"],
                title=it.get("title") or it.get("decision", "Decision")[:60],
                decision=it.get("decision", ""),
                created_at=it.get("created_at") if isinstance(it.get("created_at"), datetime) else datetime.now(timezone.utc),
                best_option_title=best.get("title") if best else None,
                best_option_score=best.get("score") if best else None,
                confidence=result.get("confidence"),
            )
        )
    return out


@api_router.get("/decisions/{decision_id}", response_model=DecisionDocument)
async def get_decision(decision_id: str, guest_id: str = Query(..., min_length=8)):
    doc = await db.decisions.find_one({"id": decision_id, "guest_id": guest_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Decision not found")
    _strip_mongo(doc)
    return DecisionDocument(**doc)


@api_router.delete("/decisions/{decision_id}")
async def delete_decision(decision_id: str, guest_id: str = Query(..., min_length=8)):
    res = await db.decisions.delete_one({"id": decision_id, "guest_id": guest_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Decision not found")
    return {"ok": True}


# Register routes
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
