"""Decision Intelligence AI service.

Upgraded (Phase 3):
  - Decision Intelligence framework (outcomes, probabilities, trade-offs, optimization)
  - Extended option schema (success_probability, expected_return, time_to_result,
    geography, easiness, support, history, financial_ratio)
  - Top-level fields: key_insights, execution_plan (with steps, timelines,
    tools, expenses/benefits), plan_b, why_not_others
  - Server-side JSON repair fallback via json_repair for rare malformed outputs
  - Async job pattern compatible (no architectural change here)
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from dotenv import load_dotenv
from json_repair import repair_json
from pydantic import BaseModel, Field, ValidationError, conint, field_validator
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Ensure .env is loaded even if this module is imported before server.py load_dotenv
load_dotenv(Path(__file__).parent / ".env")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
if not EMERGENT_LLM_KEY:
    raise RuntimeError("EMERGENT_LLM_KEY not set in environment")

# Primary model (fast + high quality, typical 3-10s)
PRIMARY_PROVIDER = "anthropic"
PRIMARY_MODEL = "claude-haiku-4-5-20251001"
# Deeper-reasoning fallback (different provider for resilience)
FALLBACK_PROVIDER = "openai"
FALLBACK_MODEL = "gpt-4.1"

CALL_TIMEOUT_SECONDS = 90.0


# ===================== Schemas =====================
class FollowUpQuestion(BaseModel):
    id: str = Field(default_factory=lambda: f"q_{uuid.uuid4().hex[:8]}")
    question: str
    type: Literal["text", "single_choice", "multi_choice", "slider"]
    options: Optional[List[str]] = None
    min: Optional[int] = None
    max: Optional[int] = None
    step: Optional[int] = None
    help_text: Optional[str] = None

    @field_validator("options")
    @classmethod
    def opts_required(cls, v, info):
        t = info.data.get("type")
        if t in {"single_choice", "multi_choice"} and (not v or len(v) < 2):
            raise ValueError("choice questions must include >=2 options")
        return v


class FollowUpsResponse(BaseModel):
    questions: List[FollowUpQuestion] = Field(min_length=4, max_length=8)


class ExecutionStep(BaseModel):
    step: int
    action: str
    timeline: str  # e.g. "Week 1", "Within 2 weeks", "Day 1-3"
    priority: Literal["High", "Medium", "Low"] = "Medium"
    tools: List[str] = Field(default_factory=list)
    est_cost: Optional[str] = None  # e.g. "$0", "$200", "Free"
    est_benefit: Optional[str] = None


class ExecutionPlan(BaseModel):
    title: str
    total_timeline: str  # e.g. "3 months", "6 weeks"
    steps: List[ExecutionStep] = Field(min_length=3, max_length=6)
    short_term_plan: Optional[str] = None  # summary of quick wins
    moderate_benefits: Optional[str] = None


class DecisionOption(BaseModel):
    id: str
    title: str
    description: str
    pros: List[str] = Field(min_length=2, max_length=4)
    cons: List[str] = Field(min_length=2, max_length=4)
    risk_level: Literal["Low", "Medium", "High"]
    short_term_outcome: str
    long_term_outcome: str
    score: conint(ge=0, le=100)
    # Extended fields (Decision Intelligence)
    success_probability: conint(ge=0, le=100)
    expected_return: str  # financial or value expectation (e.g. "+15-25% growth", "Save $12k")
    time_to_result: str  # e.g. "3-6 months", "~1 year"
    geography: Optional[str] = None  # applicability
    easiness: conint(ge=0, le=100)  # 0=very hard, 100=very easy
    support: Optional[str] = None  # what kind of support the option offers
    history: Optional[str] = None  # track record / past evidence
    financial_ratio: Optional[str] = None  # cost:reward ratio e.g. "1:4"
    why_not: Optional[str] = None  # why this one loses to the best


class DecisionResult(BaseModel):
    # Core (kept for backward compat)
    options: List[DecisionOption] = Field(min_length=3, max_length=4)
    best_option_id: str
    reasoning: str
    confidence: conint(ge=0, le=100)
    # Decision Intelligence additions
    goal: str  # 1-2 sentence restatement of the user's goal
    key_insights: List[str] = Field(min_length=2, max_length=4)
    execution_plan: Optional[ExecutionPlan] = None
    plan_b: Optional[str] = None  # short Plan B description
    plan_b_trigger: Optional[str] = None  # when to activate Plan B

    @field_validator("best_option_id")
    @classmethod
    def best_exists(cls, v, info):
        opts = info.data.get("options") or []
        ids = {o.id for o in opts}
        if v not in ids:
            raise ValueError(f"best_option_id '{v}' not in option ids {ids}")
        return v


class AnalyzePayload(BaseModel):
    decision: str = Field(min_length=4, max_length=500)
    answers: List[Dict[str, Any]] = Field(default_factory=list)


# ===================== Prompts =====================
FOLLOWUPS_SYSTEM = """You are a world-class Decision Intelligence coach.
Given a user's decision statement, produce 5-7 targeted follow-up questions that will help produce
a sharp, outcome-focused recommendation.

COVERAGE (pick what fits the decision):
- Goal clarity and success metrics
- Constraints: time, money, risk tolerance, geography
- Current situation / baseline
- Skill level / experience
- Deadline / urgency
- Support system / dependents
- Preferences and priorities

STRICT RULES:
- Output JSON ONLY, no markdown fences, no prose outside the JSON object.
- Mix question types: "text", "single_choice", "multi_choice", "slider".
- Choice questions MUST have >=3 meaningful, mutually-exclusive options (for single_choice) or complementary options (for multi_choice).
- Slider questions MUST include integer min/max/step and a help_text that explains the scale endpoints.
- Keep each question concise (<=140 chars).
- Use this schema EXACTLY:
{
  "questions": [
    {"id":"q1","question":"...","type":"single_choice","options":["...","...","..."]},
    {"id":"q2","question":"...","type":"slider","min":0,"max":10,"step":1,"help_text":"0=...,10=..."},
    {"id":"q3","question":"...","type":"multi_choice","options":["...","...","..."]},
    {"id":"q4","question":"...","type":"text","help_text":"..."}
  ]
}
"""

ANALYZE_SYSTEM = """You are a DECISION INTELLIGENCE ENGINE. You produce sharp, outcome-focused, quantified decision analyses.

Framework to follow:
1) Problem understanding (goal + constraints)
2) 3-4 distinct, actionable options (include one non-obvious)
3) Quantified outcomes per option (% / $ / time)
4) Decision optimization (best risk-reward; protect user's money + peace)
5) Execution plan (3-6 concrete steps with timelines, tools, cost/benefit)
6) Plan B with a clear trigger
7) Confidence score

RULES:
- Output STRICT JSON only. No markdown fences. No prose outside JSON.
- Never vague. Quantify ($, %, weeks/months).
- Keep strings concise (most under 140 chars).
- pros/cons: 2-4 items each, concrete.
- Reference the user's inputs; don't generalize.

SCHEMA (EXACT, all fields required unless marked optional):
{
  "goal": "1-2 sentence restatement of goal.",
  "key_insights": ["numbered-ish insight 1", "insight 2", "insight 3"],
  "options": [
    {
      "id": "opt_1",
      "title": "Short concrete title",
      "description": "1-2 sentences.",
      "pros": ["...","...","..."],
      "cons": ["...","...","..."],
      "risk_level": "Low|Medium|High",
      "short_term_outcome": "Weeks-months outcome.",
      "long_term_outcome": "1-3 year outcome.",
      "score": 0-100,
      "success_probability": 0-100,
      "expected_return": "e.g. '+$40k TC', '+15-25% growth'",
      "time_to_result": "e.g. '3-6 months'",
      "geography": "Global / US / city",
      "easiness": 0-100,
      "support": "Resources/community/tools that help",
      "history": "Track record / evidence",
      "financial_ratio": "cost:reward, e.g. '1:4'",
      "why_not": "Why loses to best (or 'Best overall.')"
    }
  ],
  "best_option_id": "opt_X",
  "reasoning": "2-3 sentences on why best wins.",
  "confidence": 0-100,
  "execution_plan": {
    "title": "Action plan for best option",
    "total_timeline": "e.g. '90 days'",
    "steps": [
      {"step":1,"action":"Concrete action","timeline":"Week 1","priority":"High","tools":["tool"],"est_cost":"$X","est_benefit":"Y"}
    ],
    "short_term_plan": "Quick wins in 1-2 weeks.",
    "moderate_benefits": "1-3 month gains at moderate effort."
  },
  "plan_b": "1-2 sentence fallback.",
  "plan_b_trigger": "Clear condition to trigger Plan B."
}
"""


# ===================== Helpers =====================
def _extract_json(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def _parse_json_with_repair(raw: str) -> Dict[str, Any]:
    """Parse JSON with a repair fallback for rare malformed outputs."""
    s = _extract_json(raw)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # try json_repair which handles trailing commas, unescaped quotes, missing brackets, etc.
        repaired = repair_json(s, return_objects=False)
        return json.loads(repaired)


async def _call_llm(system: str, user_text: str, *, provider: str, model: str, session_id: str) -> str:
    chat = (
        LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system,
        )
        .with_model(provider, model)
        .with_params(timeout=CALL_TIMEOUT_SECONDS, num_retries=0, max_retries=0)
    )
    msg = UserMessage(text=user_text)
    return await asyncio.wait_for(chat.send_message(msg), timeout=CALL_TIMEOUT_SECONDS + 10)


async def _try_call_with_fallback(system: str, user_text: str, session_prefix: str) -> str:
    providers = [(PRIMARY_PROVIDER, PRIMARY_MODEL), (FALLBACK_PROVIDER, FALLBACK_MODEL)]
    last_err: Optional[Exception] = None
    for provider, model in providers:
        try:
            return await _call_llm(
                system,
                user_text,
                provider=provider,
                model=model,
                session_id=f"{session_prefix}-{uuid.uuid4()}",
            )
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"All LLM providers failed: {last_err}")


# ===================== Public =====================
async def generate_followups(decision_context: str) -> FollowUpsResponse:
    last_err: Optional[str] = None
    for attempt in range(2):
        user_text = f"DECISION: {decision_context}\n\nReturn the JSON now. JSON only, no prose."
        if last_err:
            user_text += f"\n\nPrevious validation error: {last_err}\nFix the JSON and return JSON only."
        raw = await _try_call_with_fallback(FOLLOWUPS_SYSTEM, user_text, "followups")
        try:
            data = _parse_json_with_repair(raw)
            for i, q in enumerate(data.get("questions", [])):
                q.setdefault("id", f"q{i+1}")
            return FollowUpsResponse(**data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_err = str(e)[:400]
            continue
    raise RuntimeError(f"followups failed: {last_err}")


async def analyze_decision(decision_context: str, answers: List[Dict[str, Any]]) -> DecisionResult:
    last_err: Optional[str] = None
    for attempt in range(2):
        user_text = (
            f"DECISION: {decision_context}\n\n"
            f"USER ANSWERS (JSON):\n{json.dumps(answers, indent=2, default=str)}\n\n"
            "Now produce the full Decision Intelligence JSON. JSON only, no prose."
        )
        if last_err:
            user_text += f"\n\nPrevious validation error: {last_err}\nFix the JSON strictly per schema and return JSON only."
        raw = await _try_call_with_fallback(ANALYZE_SYSTEM, user_text, "analyze")
        try:
            data = _parse_json_with_repair(raw)
            return DecisionResult(**data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_err = str(e)[:400]
            continue
    raise RuntimeError(f"analyze failed: {last_err}")
