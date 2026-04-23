from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
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
from auth_service import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    PublicUser,
    hash_password,
    verify_password,
    create_token,
    get_current_user_optional,
    get_current_user_required,
    new_user_id,
    serialize_user_doc,
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Smart Decision AI", version="1.1.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ===================== Models =====================
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
    guest_id: Optional[str] = None  # may be omitted for authed users
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
    guest_id: Optional[str] = None
    user_id: Optional[str] = None
    title: str
    decision: str
    answers: List[Dict[str, Any]]
    result: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ===================== Helpers =====================
def _strip_mongo(doc: dict) -> dict:
    if not doc:
        return doc
    doc.pop("_id", None)
    for k in ("created_at", "updated_at"):
        if k in doc and isinstance(doc[k], str):
            try:
                doc[k] = datetime.fromisoformat(doc[k])
            except ValueError:
                pass
    return doc


def _owner_filter(user_id: Optional[str], guest_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """Build a Mongo filter for decisions ownership.

    Authed users: only their user_id decisions.
    Guests: only their guest_id decisions (and no user_id set).
    """
    if user_id:
        return {"user_id": user_id}
    if guest_id:
        return {"guest_id": guest_id}
    return None


# ===================== Routes =====================
@api_router.get("/")
async def root():
    return {"message": "Smart Decision AI API is up", "version": "1.1.0"}


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


# ===================== Auth =====================
@api_router.post("/auth/signup", response_model=AuthResponse)
async def signup(payload: SignupRequest):
    email = payload.email.lower().strip()
    existing = await db.users.find_one({"email": email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")
    user_id = new_user_id()
    now = datetime.now(timezone.utc)
    user_doc = {
        "id": user_id,
        "email": email,
        "name": payload.name,
        "password_hash": hash_password(payload.password),
        "created_at": now.isoformat(),
    }
    await db.users.insert_one(user_doc)
    token = create_token(user_id, email)
    return AuthResponse(token=token, user=serialize_user_doc(user_doc))


@api_router.post("/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user["id"], email)
    return AuthResponse(token=token, user=serialize_user_doc(user))


@api_router.get("/auth/me", response_model=PublicUser)
async def me(payload: Dict[str, Any] = Depends(get_current_user_required)):
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_user_doc(user)


# ===================== Guest session =====================
@api_router.post("/guest/session", response_model=GuestSessionResponse)
async def create_guest_session():
    guest_id = f"guest_{uuid.uuid4().hex[:12]}"
    return GuestSessionResponse(guest_id=guest_id)


# ===================== Decision engine (follow-ups + analyze) =====================
@api_router.post("/decisions/followups", response_model=FollowUpsResponse)
async def api_followups(payload: DecisionContextRequest):
    try:
        result = await generate_followups(payload.decision)
        return result
    except Exception as e:
        logger.exception("followups error")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)[:200]}")


# Async analyze job store (in-memory, single-worker safe).
_analyze_jobs: Dict[str, Dict[str, Any]] = {}
_JOB_TTL_SECONDS = 900


def _prune_old_jobs() -> None:
    now = datetime.now(timezone.utc)
    stale = [
        jid
        for jid, j in _analyze_jobs.items()
        if (now - j.get("created_at", now)).total_seconds() > _JOB_TTL_SECONDS
    ]
    for jid in stale:
        _analyze_jobs.pop(jid, None)


async def _run_analyze_job(job_id: str, decision: str, answers: List[Dict[str, Any]]):
    try:
        result = await analyze_decision(decision, answers)
        job = _analyze_jobs.get(job_id)
        if job is None:
            return
        job["status"] = "completed"
        job["result"] = result.model_dump()
        job["completed_at"] = datetime.now(timezone.utc)
    except Exception as e:
        logger.exception("analyze job %s failed", job_id)
        job = _analyze_jobs.get(job_id)
        if job is None:
            return
        job["status"] = "failed"
        job["error"] = str(e)[:400]
        job["completed_at"] = datetime.now(timezone.utc)


@api_router.post("/decisions/analyze")
async def api_analyze(payload: AnalyzePayload):
    """Synchronous analyze — small/quick decisions."""
    try:
        result = await analyze_decision(payload.decision, payload.answers)
        return result
    except Exception as e:
        logger.exception("analyze error")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)[:200]}")


@api_router.post("/decisions/analyze/start")
async def api_analyze_start(payload: AnalyzePayload, background_tasks: BackgroundTasks):
    _prune_old_jobs()
    job_id = str(uuid.uuid4())
    _analyze_jobs[job_id] = {
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
        "decision": payload.decision,
    }
    asyncio.create_task(_run_analyze_job(job_id, payload.decision, payload.answers))
    return {"job_id": job_id, "status": "pending"}


@api_router.get("/decisions/analyze/status/{job_id}")
async def api_analyze_status(job_id: str):
    job = _analyze_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    resp: Dict[str, Any] = {"status": job["status"]}
    if job["status"] == "completed":
        resp["result"] = job.get("result")
    elif job["status"] == "failed":
        resp["error"] = job.get("error", "Unknown error")
    return resp


# ===================== Saved decisions (scoped by user_id OR guest_id) =====================
@api_router.post("/decisions", response_model=DecisionDocument)
async def save_decision(
    payload: SaveDecisionRequest,
    user_payload: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    user_id = user_payload.get("sub") if user_payload else None
    if not user_id and (not payload.guest_id or not payload.guest_id.startswith("guest_")):
        raise HTTPException(status_code=400, detail="Missing owner (auth or guest_id required)")
    now = datetime.now(timezone.utc)
    doc = DecisionDocument(
        id=str(uuid.uuid4()),
        user_id=user_id,
        guest_id=None if user_id else payload.guest_id,
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
async def list_decisions(
    guest_id: Optional[str] = Query(default=None),
    user_payload: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    user_id = user_payload.get("sub") if user_payload else None
    q = _owner_filter(user_id, guest_id)
    if not q:
        return []
    cursor = db.decisions.find(q, {"_id": 0}).sort("created_at", -1).limit(200)
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
async def get_decision(
    decision_id: str,
    guest_id: Optional[str] = Query(default=None),
    user_payload: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    user_id = user_payload.get("sub") if user_payload else None
    q = _owner_filter(user_id, guest_id)
    if not q:
        raise HTTPException(status_code=400, detail="Missing owner (auth or guest_id)")
    q["id"] = decision_id
    doc = await db.decisions.find_one(q, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Decision not found")
    _strip_mongo(doc)
    return DecisionDocument(**doc)


@api_router.delete("/decisions/{decision_id}")
async def delete_decision(
    decision_id: str,
    guest_id: Optional[str] = Query(default=None),
    user_payload: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    user_id = user_payload.get("sub") if user_payload else None
    q = _owner_filter(user_id, guest_id)
    if not q:
        raise HTTPException(status_code=400, detail="Missing owner")
    q["id"] = decision_id
    res = await db.decisions.delete_one(q)
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
