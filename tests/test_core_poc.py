"""
Smart Decision AI — Phase 1 POC
================================
Validates the CORE workflow in isolation before building the full app.

Tests:
 1. Emergent Universal LLM Key works (text generation)
 2. Dynamic follow-up question generation returns valid typed questions
 3. Strict JSON decision analysis — returns schema-valid options, scores, best pick, confidence
 4. Reliability loop (retry + repair on malformed JSON)
 5. Output quality: specific, non-generic, tailored per decision context

Run:  python /app/tests/test_core_poc.py
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, conint, field_validator

# Load environment
BACKEND_ENV = Path("/app/backend/.env")
load_dotenv(BACKEND_ENV)

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
assert EMERGENT_LLM_KEY, "EMERGENT_LLM_KEY missing in /app/backend/.env"

from emergentintegrations.llm.chat import LlmChat, UserMessage  # noqa: E402


# ---------- Schemas ----------
class FollowUpQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    type: Literal["text", "single_choice", "multi_choice", "slider"]
    options: Optional[List[str]] = None  # for single/multi choice
    min: Optional[int] = None  # for slider
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


# ---------- Prompts ----------
FOLLOWUPS_SYSTEM = """You are a world-class decision coach for students and early-career professionals.
Given a user's decision statement, produce 5-7 targeted follow-up questions to clarify their situation.

STRICT RULES:
- Output JSON ONLY, no markdown fences, no prose.
- Mix question types: "text", "single_choice", "multi_choice", "slider".
- Choice questions MUST have >=3 meaningful options.
- Slider questions MUST include integer min/max/step (e.g. min=0,max=10,step=1).
- Keep each question concise, concrete, and specific to the decision.
- Use this schema EXACTLY:
{
  "questions": [
    {"id":"q1","question":"...","type":"single_choice","options":["...","...","..."]},
    {"id":"q2","question":"...","type":"slider","min":0,"max":10,"step":1,"help_text":"..."},
    {"id":"q3","question":"...","type":"text"}
  ]
}
"""

ANALYZE_SYSTEM = """You are an elite decision analyst. Given a user's decision + their answers, produce 3-5 DISTINCT, concrete options
tailored to their specifics. Avoid generic advice. Each option must feel actionable.

STRICT RULES:
- Output JSON ONLY. No markdown fences. No prose outside JSON.
- 3-5 options.
- Scores 0..100; one option must be clearly best; others must still be plausible.
- pros/cons: 3-5 items each, concrete and specific to the user's answers.
- risk_level ∈ {"Low","Medium","High"}.
- short_term_outcome: what happens in weeks/months. long_term_outcome: 1-3 years out.
- best_option_id MUST be one of the option ids.
- confidence 0..100 reflects certainty given available info.

Schema:
{
  "options": [
    {
      "id": "opt_1",
      "title": "...",
      "description": "1-2 sentences",
      "pros": ["...","...","..."],
      "cons": ["...","...","..."],
      "risk_level": "Low|Medium|High",
      "short_term_outcome": "...",
      "long_term_outcome": "...",
      "score": 0-100
    }
  ],
  "best_option_id": "opt_X",
  "reasoning": "Why the best option wins given the user's answers and tradeoffs.",
  "confidence": 0-100
}
"""


# ---------- Helpers ----------
def _extract_json(text: str) -> str:
    """Extract JSON from LLM output. Strips code fences and finds first {...} block."""
    text = text.strip()
    # strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # grab first balanced {...}
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


async def generate_followups(decision_context: str, *, provider: str, model: str) -> FollowUpsResponse:
    """Reliability loop for follow-up generation."""
    last_err: Optional[str] = None
    for attempt in range(3):
        user_text = (
            f"DECISION: {decision_context}\n\n"
            "Return the JSON now. Remember: JSON only, no prose."
        )
        if last_err:
            user_text += f"\n\nYour last response had this validation error: {last_err}\nFix it and return JSON only."
        raw = await _call_llm(
            FOLLOWUPS_SYSTEM,
            user_text,
            provider=provider,
            model=model,
            session_id=f"followups-{uuid.uuid4()}",
        )
        try:
            data = json.loads(_extract_json(raw))
            # ensure each question has an id
            for i, q in enumerate(data.get("questions", [])):
                q.setdefault("id", f"q{i+1}")
            return FollowUpsResponse(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = str(e)[:400]
            continue
    raise RuntimeError(f"followups failed after retries: {last_err}")


async def analyze_decision(
    decision_context: str,
    answers: List[Dict[str, Any]],
    *,
    provider: str,
    model: str,
) -> DecisionResult:
    """Reliability loop for decision analysis."""
    last_err: Optional[str] = None
    for attempt in range(3):
        user_text = (
            f"DECISION: {decision_context}\n\n"
            f"USER ANSWERS:\n{json.dumps(answers, indent=2)}\n\n"
            "Return the JSON now. Remember: JSON only, no prose."
        )
        if last_err:
            user_text += f"\n\nPrevious validation error: {last_err}\nFix and return JSON only."
        raw = await _call_llm(
            ANALYZE_SYSTEM,
            user_text,
            provider=provider,
            model=model,
            session_id=f"analyze-{uuid.uuid4()}",
        )
        try:
            data = json.loads(_extract_json(raw))
            return DecisionResult(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = str(e)[:400]
            continue
    raise RuntimeError(f"analyze failed after retries: {last_err}")


# ---------- Fixtures ----------
FIXTURES: List[Tuple[str, List[Dict[str, Any]]]] = [
    (
        "Should I quit my stable software job at a bank to join an early-stage AI startup?",
        [
            {"q": "How many years of savings do you have?", "a": "14 months of expenses"},
            {"q": "Risk tolerance (0=low, 10=high)?", "a": 7},
            {"q": "Primary motivation?", "a": "Learning cutting-edge AI + equity upside"},
            {"q": "Family dependents?", "a": "No"},
            {"q": "Current compensation vs startup offer?", "a": "Current $140k + bonus; startup $120k base + 0.4% equity"},
        ],
    ),
    (
        "Should I pursue a Master's in Computer Science abroad or start working now with my Bachelor's?",
        [
            {"q": "Top target schools?", "a": ["CMU", "ETH Zurich", "TUM"]},
            {"q": "GPA?", "a": "3.7/4.0"},
            {"q": "Debt tolerance ($)?", "a": 40000},
            {"q": "Career goal in 5 years?", "a": "Senior ML engineer at top-tier product company"},
            {"q": "Current offer?", "a": "Mid-tier SaaS $95k total"},
        ],
    ),
    (
        "Should I move from Bangalore to Bengaluru-like remote setup in a smaller city for better quality of life?",
        [
            {"q": "Current rent + commute hours?", "a": "$700 rent, 2h/day commute"},
            {"q": "Remote policy?", "a": "Fully remote allowed"},
            {"q": "Social ties in Bangalore (0-10)?", "a": 8},
            {"q": "Budget for move?", "a": 3000},
            {"q": "Top criteria?", "a": ["cost of living", "air quality", "travel hub"]},
        ],
    ),
]


# ---------- Runner ----------
async def run_for_model(provider: str, model: str) -> Dict[str, Any]:
    results = {"provider": provider, "model": model, "cases": []}
    for idx, (decision, answers) in enumerate(FIXTURES, 1):
        print(f"\n[{provider}/{model}] Case {idx}: {decision[:80]}...")
        case: Dict[str, Any] = {"decision": decision}
        try:
            fq = await generate_followups(decision, provider=provider, model=model)
            case["followups_count"] = len(fq.questions)
            case["followups_types"] = sorted({q.type for q in fq.questions})
            print(f"  ✓ follow-ups: {len(fq.questions)} ({', '.join(case['followups_types'])})")
        except Exception as e:
            case["followups_error"] = str(e)[:300]
            print(f"  ✗ follow-ups error: {e}")

        try:
            dr = await analyze_decision(decision, answers, provider=provider, model=model)
            case["options"] = [
                {"id": o.id, "title": o.title, "score": o.score, "risk": o.risk_level}
                for o in dr.options
            ]
            case["best_option_id"] = dr.best_option_id
            case["confidence"] = dr.confidence
            # sanity: best has top score (allow tie-breaker by reasoning)
            top_score = max(o.score for o in dr.options)
            best_opt = next(o for o in dr.options if o.id == dr.best_option_id)
            case["best_is_top"] = best_opt.score == top_score
            print(f"  ✓ options={len(dr.options)} best='{best_opt.title}' (score={best_opt.score}) conf={dr.confidence}")
            print(f"    reasoning: {dr.reasoning[:180]}...")
        except Exception as e:
            case["analyze_error"] = str(e)[:300]
            print(f"  ✗ analyze error: {e}")

        results["cases"].append(case)
    return results


def summarize(all_results: List[Dict[str, Any]]) -> bool:
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    overall_pass = True
    for r in all_results:
        label = f"{r['provider']}/{r['model']}"
        n = len(r["cases"])
        fu_ok = sum(1 for c in r["cases"] if "followups_count" in c)
        an_ok = sum(1 for c in r["cases"] if "options" in c)
        print(f"{label}: follow-ups {fu_ok}/{n}, analyze {an_ok}/{n}")
        if fu_ok != n or an_ok != n:
            overall_pass = False
    return overall_pass


async def main():
    providers_to_test = [
        # Provider, Model — try strongest reasoning first (for the app we'll pick the winner)
        ("openai", "gpt-5"),
        ("anthropic", "claude-sonnet-4-5-20250929"),
    ]

    all_results = []
    for provider, model in providers_to_test:
        try:
            r = await run_for_model(provider, model)
            all_results.append(r)
        except Exception as e:
            print(f"\n!! {provider}/{model} hard failure: {e}")
            traceback.print_exc()
            all_results.append({"provider": provider, "model": model, "cases": [], "fatal": str(e)})

    # dump full results
    out_path = Path("/app/tests/test_core_poc_results.json")
    out_path.write_text(json.dumps(all_results, indent=2, default=str))
    print(f"\nFull results written to: {out_path}")

    passed = summarize(all_results)
    print("\nOVERALL:", "PASS ✅" if passed else "FAIL ❌")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
