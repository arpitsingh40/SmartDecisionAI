"""AI service for Smart Decision AI.

Uses the Emergent Universal LLM key + emergentintegrations library.
Primary model: Anthropic claude-sonnet-4-5-20250929 (validated in Phase 1 POC).
Falls back to OpenAI gpt-4.1 if primary fails.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, conint, field_validator
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Ensure .env is loaded even if this module is imported before server.py load_dotenv
load_dotenv(Path(__file__).parent / ".env")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
if not EMERGENT_LLM_KEY:
    raise RuntimeError("EMERGENT_LLM_KEY not set in environment")

PRIMARY_PROVIDER = "anthropic"
PRIMARY_MODEL = "claude-sonnet-4-5-20250929"
FALLBACK_PROVIDER = "openai"
FALLBACK_MODEL = "gpt-4.1"


# ---------- Schemas ----------
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


class DecisionOption(BaseModel):
    id: str
    title: str
    description: str
    pros: List[str] = Field(min_length=2, max_length=6)
    cons: List[str] = Field(min_length=2, max_length=6)
    risk_level: Literal["Low", "Medium", "High"]
    short_term_outcome: str
    long_term_outcome: str
    score: conint(ge=0, le=100)


class DecisionResult(BaseModel):
    options: List[DecisionOption] = Field(min_length=3, max_length=5)
    best_option_id: str
    reasoning: str
    confidence: conint(ge=0, le=100)

    @field_validator("best_option_id")
    @classmethod
    def best_exists(cls, v, info):
        opts = info.data.get("options") or []
        ids = {o.id for o in opts}
        if v not in ids:
            raise ValueError(f"best_option_id '{v}' not in option ids {ids}")
        return v


class AnswerItem(BaseModel):
    question: str
    answer: Any
    type: Optional[str] = None


class AnalyzePayload(BaseModel):
    decision: str = Field(min_length=4, max_length=500)
    answers: List[Dict[str, Any]] = Field(default_factory=list)


# ---------- Prompts ----------
FOLLOWUPS_SYSTEM = """You are a world-class decision coach for students and early-career professionals.
Given a user's decision statement, produce 5-7 targeted follow-up questions to clarify their situation.

STRICT RULES:
- Output JSON ONLY, no markdown fences, no prose outside the JSON object.
- Mix question types: "text", "single_choice", "multi_choice", "slider".
- Choice questions MUST have >=3 meaningful, mutually-exclusive options (for single_choice) or complementary options (for multi_choice).
- Slider questions MUST include integer min/max/step and a help_text hinting at scale meaning.
- Keep each question concise (<=140 chars), concrete, and specific to the decision.
- Prefer questions about: current situation, constraints, priorities, risk tolerance, timeline, finances, people-impact.
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

ANALYZE_SYSTEM = """You are an elite decision analyst. Given a user's decision + their answers, produce 3-5 DISTINCT, concrete options
tailored to their specifics. Avoid generic advice. Each option must feel actionable.

STRICT RULES:
- Output JSON ONLY. No markdown fences. No prose outside JSON.
- 3-5 options. Option ids like "opt_1", "opt_2", ...
- Scores 0..100; one option must be clearly best; others must still be plausible (spread scores meaningfully).
- pros/cons: 3-5 items each, concrete and specific to the user's answers. Reference user-provided numbers/context.
- risk_level in {"Low","Medium","High"}.
- short_term_outcome: what happens in weeks/months.
- long_term_outcome: 1-3 years out.
- best_option_id MUST be one of the option ids AND have the highest score (ties broken by reasoning).
- confidence 0..100 reflects certainty given available info.
- reasoning: 2-4 sentences explaining the tradeoff and why the best option wins.

Schema:
{
  "options": [
    {
      "id": "opt_1",
      "title": "Short, specific title",
      "description": "1-2 sentences describing the option",
      "pros": ["...","...","..."],
      "cons": ["...","...","..."],
      "risk_level": "Low|Medium|High",
      "short_term_outcome": "...",
      "long_term_outcome": "...",
      "score": 0
    }
  ],
  "best_option_id": "opt_X",
  "reasoning": "...",
  "confidence": 0
}
"""


# ---------- Helpers ----------
def _extract_json(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


async def _call_llm(system: str, user_text: str, *, provider: str, model: str, session_id: str) -> str:
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system,
    ).with_model(provider, model)
    msg = UserMessage(text=user_text)
    return await chat.send_message(msg)


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


# ---------- Public ----------
async def generate_followups(decision_context: str) -> FollowUpsResponse:
    last_err: Optional[str] = None
    for attempt in range(3):
        user_text = (
            f"DECISION: {decision_context}\n\n"
            "Return the JSON now. JSON only, no prose."
        )
        if last_err:
            user_text += f"\n\nPrevious validation error: {last_err}\nFix the JSON and return JSON only."
        raw = await _try_call_with_fallback(FOLLOWUPS_SYSTEM, user_text, "followups")
        try:
            data = json.loads(_extract_json(raw))
            for i, q in enumerate(data.get("questions", [])):
                q.setdefault("id", f"q{i+1}")
            return FollowUpsResponse(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = str(e)[:400]
            continue
    raise RuntimeError(f"followups failed after retries: {last_err}")


async def analyze_decision(decision_context: str, answers: List[Dict[str, Any]]) -> DecisionResult:
    last_err: Optional[str] = None
    for attempt in range(3):
        user_text = (
            f"DECISION: {decision_context}\n\n"
            f"USER ANSWERS (JSON):\n{json.dumps(answers, indent=2, default=str)}\n\n"
            "Return the JSON now. JSON only, no prose."
        )
        if last_err:
            user_text += f"\n\nPrevious validation error: {last_err}\nFix the JSON and return JSON only."
        raw = await _try_call_with_fallback(ANALYZE_SYSTEM, user_text, "analyze")
        try:
            data = json.loads(_extract_json(raw))
            return DecisionResult(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = str(e)[:400]
            continue
    raise RuntimeError(f"analyze failed after retries: {last_err}")
