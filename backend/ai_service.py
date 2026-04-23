"""Decision Intelligence AI service (v2 — factor-weighted structured pipeline).

Pipeline stages (all wrapped in strict JSON):
  1) Factor suggestion (per decision) — /decisions/suggest-factors
  2) Follow-ups (friendly, one-at-a-time, conversational) — /decisions/followups
  3) Analyze (structured) — /decisions/analyze[/start]
     Accepts user-defined factors + weights; returns:
       - goal, key_insights, assumptions, bias_flags
       - options (3-5, INCLUDING a "Do nothing" option), each with:
         * pros, cons, risk_level
         * short_term_outcome, long_term_outcome
         * score (AI's holistic score, used as fallback)
         * factor_ratings: {factor_name: 0-10}
         * scenarios: { best_case, worst_case, most_likely }
         * future_impact: { one_year, five_year }
         * success_probability, expected_return, time_to_result,
           geography, easiness, support, history, financial_ratio, why_not
       - execution_plan (for the best option)
       - plan_b + plan_b_trigger
       - best_option_id, reasoning, confidence (0-100)

Notes:
  - Scoring is typically computed client-side: score = Σ (weight_i × rating_i)
  - AI's numeric score is kept for UIs without access to weights (fallback).
  - JSON repair fallback for rare malformed outputs.
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

load_dotenv(Path(__file__).parent / ".env")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
if not EMERGENT_LLM_KEY:
    raise RuntimeError("EMERGENT_LLM_KEY not set in environment")

# Primary model (fast + high quality, typical 3-10s)
PRIMARY_PROVIDER = "anthropic"
PRIMARY_MODEL = "claude-haiku-4-5-20251001"
# Fallback (different provider for resilience)
FALLBACK_PROVIDER = "openai"
FALLBACK_MODEL = "gpt-4.1"

CALL_TIMEOUT_SECONDS = 90.0


# ====================================================================
# Schemas
# ====================================================================
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
    questions: List[FollowUpQuestion] = Field(min_length=3, max_length=8)


class FactorSuggestion(BaseModel):
    name: str = Field(min_length=2, max_length=28)
    description: str = Field(min_length=4, max_length=140)
    default_weight: conint(ge=0, le=100) = 50


class SuggestFactorsResponse(BaseModel):
    factors: List[FactorSuggestion] = Field(min_length=3, max_length=6)


class ExecutionStep(BaseModel):
    step: int
    action: str
    timeline: str
    priority: Literal["High", "Medium", "Low"] = "Medium"
    tools: List[str] = Field(default_factory=list)
    est_cost: Optional[str] = None
    est_benefit: Optional[str] = None


class ExecutionPlan(BaseModel):
    title: str
    total_timeline: str
    steps: List[ExecutionStep] = Field(min_length=3, max_length=6)
    short_term_plan: Optional[str] = None
    moderate_benefits: Optional[str] = None


class OptionScenarios(BaseModel):
    best_case: str
    worst_case: str
    most_likely: str


class OptionFutureImpact(BaseModel):
    one_year: str
    five_year: str


class DecisionOption(BaseModel):
    id: str
    title: str
    description: str
    is_do_nothing: bool = False
    pros: List[str] = Field(min_length=2, max_length=4)
    cons: List[str] = Field(min_length=2, max_length=4)
    risk_level: Literal["Low", "Medium", "High"]
    short_term_outcome: str
    long_term_outcome: str
    score: conint(ge=0, le=100)  # AI's holistic score (fallback)
    # Weighted-scoring inputs: AI rates each factor 0-10
    factor_ratings: Dict[str, conint(ge=0, le=10)] = Field(default_factory=dict)
    # Risk & future projections per option
    scenarios: Optional[OptionScenarios] = None
    future_impact: Optional[OptionFutureImpact] = None
    # Decision Intelligence extended fields
    success_probability: conint(ge=0, le=100) = 60
    expected_return: str = ""
    time_to_result: str = ""
    geography: Optional[str] = None
    easiness: conint(ge=0, le=100) = 50
    support: Optional[str] = None
    history: Optional[str] = None
    financial_ratio: Optional[str] = None
    why_not: Optional[str] = None


class BiasFlag(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    message: str = Field(min_length=8, max_length=280)
    severity: Literal["info", "warn", "high"] = "warn"


class DecisionResult(BaseModel):
    options: List[DecisionOption] = Field(min_length=3, max_length=5)
    best_option_id: str
    reasoning: str
    confidence: conint(ge=0, le=100)
    goal: str
    key_insights: List[str] = Field(min_length=2, max_length=4)
    assumptions: List[str] = Field(default_factory=list, max_length=6)
    bias_flags: List[BiasFlag] = Field(default_factory=list, max_length=4)
    execution_plan: Optional[ExecutionPlan] = None
    plan_b: Optional[str] = None
    plan_b_trigger: Optional[str] = None
    # Echo back what AI saw (handy for UI)
    factors_used: List[str] = Field(default_factory=list)

    @field_validator("best_option_id")
    @classmethod
    def best_exists(cls, v, info):
        opts = info.data.get("options") or []
        ids = {o.id for o in opts}
        if v not in ids:
            raise ValueError(f"best_option_id '{v}' not in option ids {ids}")
        return v


class FactorWeight(BaseModel):
    name: str
    weight: conint(ge=0, le=100) = 50


class AnalyzePayload(BaseModel):
    decision: str = Field(min_length=4, max_length=500)
    answers: List[Dict[str, Any]] = Field(default_factory=list)
    factors: List[FactorWeight] = Field(default_factory=list)


# ====================================================================
# Prompts
# ====================================================================
FOLLOWUPS_SYSTEM = """You are a warm, thoughtful decision coach. Think "smart friend", not "robotic form".
Given a user's decision, produce 3-6 short, natural-sounding follow-up questions to learn the essentials.

TONE:
- Friendly, human, concise.
- One idea per question. Use everyday words.
- No numbered lists, no "firstly / secondly", no prefacing.

COVERAGE (pick what matters most for THIS decision):
- Goal / desired outcome
- Current situation / baseline
- Constraints (money, time)
- Risk tolerance
- What matters most (priorities)
- Timeline / urgency

STRICT RULES:
- Output JSON ONLY. No markdown fences. No prose outside JSON.
- Mix question types thoughtfully: "text", "single_choice", "multi_choice", "slider".
- Choice questions MUST have >=3 options.
- Slider questions MUST include min/max/step and a help_text naming endpoints.
- Keep each question under 120 chars.
- Don't repeat questions the user already implicitly answered in their decision statement.

SCHEMA:
{
  "questions": [
    {"id":"q1","question":"...","type":"single_choice","options":["...","...","..."]},
    {"id":"q2","question":"...","type":"slider","min":0,"max":10,"step":1,"help_text":"0=low, 10=high"},
    {"id":"q3","question":"...","type":"multi_choice","options":["...","...","..."]},
    {"id":"q4","question":"...","type":"text","help_text":"..."}
  ]
}
"""

SUGGEST_FACTORS_SYSTEM = """You are a decision analyst. Given a user's decision statement, propose 3-5 FACTORS
(criteria) that matter for evaluating options. Factors must be specific to the decision, not generic.

Examples:
- Car buying -> Safety, Price, Reliability, Comfort, Running costs
- Job change -> Compensation, Growth, Stability, Work-life balance, Learning
- City move -> Cost of living, Career opportunity, Social ties, Climate, Healthcare
- Online course -> Quality, Time commitment, Cost, Career ROI, Community support

STRICT RULES:
- Output JSON ONLY. No markdown fences. No prose outside JSON.
- Each factor name <=28 chars.
- Each description <=140 chars, explains what "high rating" means.
- Provide a reasonable default_weight 0-100. Typical distribution sums roughly to 100-300
  (weights will be normalized client-side).

SCHEMA:
{
  "factors": [
    {"name":"Safety","description":"Crashworthiness, airbags, driver assist features.","default_weight":70},
    {"name":"Price","description":"Sticker price + finance cost.","default_weight":60},
    {"name":"Reliability","description":"Brand reliability ratings and long-term durability.","default_weight":65},
    {"name":"Comfort","description":"Ride quality, interior space, noise.","default_weight":40}
  ]
}
"""

ANALYZE_SYSTEM = """You are a DECISION INTELLIGENCE ENGINE — calm, specific, quantified, and honest.

You receive:
- a user DECISION
- a list of ANSWERS to follow-up questions
- a list of FACTORS (criteria names + weights 0-100 reflecting user priority)

You must produce a structured analysis that includes:
1) goal (1-2 sentence restatement)
2) key_insights (2-4 concise, quantified)
3) assumptions (2-4 explicit assumptions you're making where data is missing)
4) bias_flags (0-3 — inconsistencies between stated priorities and constraints, overconfidence signals, sunk-cost hints, etc.)
5) 3-5 options, INCLUDING a "Do nothing" option as the LAST option (is_do_nothing=true)
6) For EVERY option:
   - factor_ratings: an int 0-10 for EACH factor provided in input
   - scenarios: { best_case, worst_case, most_likely }  — each 1-2 sentences, concrete
   - future_impact: { one_year, five_year } — concrete projections
   - pros/cons, risk_level, short_term/long_term outcomes
   - success_probability (0-100), expected_return, time_to_result, easiness (0-100),
     geography, support, history, financial_ratio, why_not
7) execution_plan (for the best option) with 3-6 steps including timeline/priority/tools/cost/benefit
8) plan_b + plan_b_trigger
9) reasoning, confidence (0-100)

RULES:
- Output STRICT JSON only. No markdown fences. No prose outside JSON.
- Every option MUST include factor_ratings for ALL factor names provided.
- Keep strings tight. Under 140 chars each when possible.
- Quantify ($, %, weeks/months). Reference the user's inputs.
- Always include "Do nothing" option (is_do_nothing=true) — rate it honestly; sometimes it's best.
- NEVER invent facts about the user. Capture missing info via assumptions[].

SCHEMA (EXACT):
{
  "goal": "Short restatement of goal.",
  "key_insights": ["Insight 1", "Insight 2"],
  "assumptions": ["Assumption 1", "Assumption 2"],
  "bias_flags": [
    {"title":"...","message":"...","severity":"info|warn|high"}
  ],
  "factors_used": ["FactorA","FactorB","FactorC"],
  "options": [
    {
      "id":"opt_1",
      "title":"Short concrete title",
      "description":"1-2 sentences.",
      "is_do_nothing": false,
      "pros":["...","...","..."],
      "cons":["...","...","..."],
      "risk_level":"Low|Medium|High",
      "short_term_outcome":"Weeks-months outcome.",
      "long_term_outcome":"1-3 year outcome.",
      "score": 0-100,
      "factor_ratings": {"FactorA": 0-10, "FactorB": 0-10, "FactorC": 0-10},
      "scenarios": {
        "best_case": "Concrete best case",
        "worst_case": "Concrete worst case",
        "most_likely": "Concrete expected case"
      },
      "future_impact": {
        "one_year": "What looks like in 1 year",
        "five_year": "What looks like in 5 years"
      },
      "success_probability": 0-100,
      "expected_return": "e.g. +$40k TC",
      "time_to_result": "e.g. 3-6 months",
      "geography": "Global / US / city",
      "easiness": 0-100,
      "support": "Resources that help",
      "history": "Evidence it works",
      "financial_ratio": "e.g. 1:4",
      "why_not": "Why loses (or 'Best overall.')"
    }
  ],
  "best_option_id": "opt_X",
  "reasoning": "2-3 sentences why best wins.",
  "confidence": 0-100,
  "execution_plan": {
    "title": "Plan for best option",
    "total_timeline": "e.g. 90 days",
    "steps": [
      {"step":1,"action":"...","timeline":"Week 1","priority":"High","tools":["tool"],"est_cost":"$X","est_benefit":"Y"}
    ],
    "short_term_plan": "Quick wins 1-2 weeks",
    "moderate_benefits": "1-3 month gains"
  },
  "plan_b": "1-2 sentence fallback.",
  "plan_b_trigger": "Clear condition."
}
"""


# ====================================================================
# Helpers
# ====================================================================
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
    s = _extract_json(raw)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
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


# ====================================================================
# Public
# ====================================================================
async def generate_followups(decision_context: str) -> FollowUpsResponse:
    last_err: Optional[str] = None
    for attempt in range(2):
        user_text = f"DECISION: {decision_context}\n\nReturn the JSON now. JSON only, no prose."
        if last_err:
            user_text += f"\n\nPrevious validation error: {last_err}\nFix and return JSON only."
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


async def suggest_factors(decision_context: str) -> SuggestFactorsResponse:
    last_err: Optional[str] = None
    for attempt in range(2):
        user_text = f"DECISION: {decision_context}\n\nReturn the JSON now. JSON only, no prose."
        if last_err:
            user_text += f"\n\nPrevious validation error: {last_err}\nFix and return JSON only."
        raw = await _try_call_with_fallback(SUGGEST_FACTORS_SYSTEM, user_text, "factors")
        try:
            data = _parse_json_with_repair(raw)
            return SuggestFactorsResponse(**data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_err = str(e)[:400]
            continue
    raise RuntimeError(f"suggest_factors failed: {last_err}")


async def analyze_decision(
    decision_context: str,
    answers: List[Dict[str, Any]],
    factors: Optional[List[Dict[str, Any]]] = None,
) -> DecisionResult:
    factors = factors or []
    factor_names = [f["name"] for f in factors if f.get("name")]
    factor_payload = {
        "factors": [{"name": f["name"], "weight": f.get("weight", 50)} for f in factors if f.get("name")],
    }

    last_err: Optional[str] = None
    for attempt in range(2):
        user_text = (
            f"DECISION: {decision_context}\n\n"
            f"USER ANSWERS (JSON):\n{json.dumps(answers, indent=2, default=str)}\n\n"
            f"FACTORS AND WEIGHTS (JSON):\n{json.dumps(factor_payload, indent=2, default=str)}\n\n"
            "Produce the Decision Intelligence JSON now. JSON only, no prose."
        )
        if last_err:
            user_text += f"\n\nPrevious validation error: {last_err}\nFix strictly and return JSON only."
        raw = await _try_call_with_fallback(ANALYZE_SYSTEM, user_text, "analyze")
        try:
            data = _parse_json_with_repair(raw)
            # Backfill factor_ratings if AI omitted any factor for some option
            opts = data.get("options") or []
            for o in opts:
                ratings = o.get("factor_ratings") or {}
                for fn in factor_names:
                    if fn not in ratings:
                        ratings[fn] = 5  # neutral default
                o["factor_ratings"] = ratings
            # Echo factors_used if missing
            data.setdefault("factors_used", factor_names)
            return DecisionResult(**data)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_err = str(e)[:400]
            continue
    raise RuntimeError(f"analyze failed: {last_err}")
