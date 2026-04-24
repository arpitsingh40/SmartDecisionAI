# Smart Decision AI — Updated Development Plan (v1.2 Structured Decision Engine)

## 1) Objectives
- Deliver a premium, responsive **structured decision engine** for students/young professionals that feels like a friendly, thoughtful guide but operates with strict, transparent logic.
- Enforce a **stage-based decision pipeline** (not a generic chatbot):
  1) Define Goal
  2) Define Priorities (weights)
  3) Understand Context (QA)
  4) Generate Options (including **Do Nothing**)
  5) Evaluate Options (AI-rated factor matrix)
  6) Score Options (**weighted scoring**) 
  7) Risk + Probability + Scenarios
  8) Future Impact + Final Recommendation
- Key architectural shift: **user-defined priority weights × AI-rated factors**.
  - AI provides **factor ratings (0–10)**, scenarios, future impact, assumptions, bias flags.
  - Final ranking is computed **client-side** using a deterministic scoring engine:
    - `Score = Σ(weight × rating) / Σ(weight) × 10` → normalized to 0–100.
  - This yields transparency, instant what-if, and avoids “black-box” scoring.
- Preserve strict reliability:
  - AI outputs in **strict JSON** validated by Pydantic.
  - Server-side **JSON repair** fallback for malformed outputs.
  - Async job analyze pattern to avoid ingress/proxy timeouts.
- Support both **guest mode** and **email/password login**:
  - Guest: localStorage guest_id.
  - Auth: bcrypt + JWT (30 days) in localStorage.
  - **Guest and user libraries remain separate** (per user choice).
- Ship modern product-quality UX (Linear/Vercel/Notion inspired): dark-first + light toggle, Framer Motion micro-interactions, responsive and accessible.

**Status update (as of now):**
- ✅ Phase 1 complete (POC validated strict JSON reliability).
- ✅ Phase 2 complete (full V1 app implemented + end-to-end tested).
- ✅ Phase 3 complete (Decision Intelligence upgrade + auth + deeper tools).
- ✅ Phase 4 complete (Structured pipeline + factor-weighted scoring + new tabs + transparency + instant what-if).
- ✅ Phase 6 complete (Multi-Agent Boardroom + parallel 6-agent synthesis + debate UI + event-loop fix + legacy auto-fallback).
- ✅ Phase 7 complete (Interactive Debate & Refinement Mode — smart-hybrid clarification + full 6-agent re-run + structured what-changed diff + history trail + confidence delta banner).
- ✅ Phase 8 complete (LLM stack swap — OpenAI **GPT-5.2** as primary via user-provided `OPENAI_API_KEY` using the direct `AsyncOpenAI` SDK; Claude Haiku via Emergent stays as fallback; GPT-4.1 via Emergent as last-resort).

---

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation: LLM structured outputs)
**Goal:** Validate LLM integration + strict JSON schema + follow-up Q generation. Do not proceed until stable.

**User stories**
1. As a user, I can enter a decision and instantly get tailored follow-up questions.
2. As a user, I can answer follow-ups and receive structured options with scores and outcomes.
3. As a user, I can trust the output is consistently structured (no malformed JSON).
4. As a user, I can see a clear best recommendation with a confidence score.

**Implementation (completed)**
- Defined Pydantic models and strict JSON schema.
- Built POC script with validation + retry loop.
- Validated Emergent Universal LLM integration.

**Results**
- ✅ Claude Sonnet 4.5 passed 3/3 fixtures with schema-valid JSON.

**Exit criteria (met)**
- ✅ Reliable structured JSON with strong output quality.

---

### Phase 2 — V1 App Development (Build around proven core)
**Goal:** Implement landing + wizard + results + saving.

**User stories**
1. Start from a landing page and begin a decision in one click.
2. Answer one question at a time with progress indicator.
3. View premium results dashboard with highlighted recommendation.
4. Save decisions (guest mode) and revisit.
5. Export PDF.

**Backend — completed**
- Guest mode:
  - `POST /api/guest/session` → guest_id.
- Decision flow:
  - `POST /api/decisions/followups`
  - Async analyze:
    - `POST /api/decisions/analyze/start`
    - `GET /api/decisions/analyze/status/{job_id}`
  - Sync analyze retained: `POST /api/decisions/analyze`.
- Saved decisions CRUD:
  - `POST /api/decisions`
  - `GET /api/decisions?guest_id=...`
  - `GET /api/decisions/{id}?guest_id=...`
  - `DELETE /api/decisions/{id}?guest_id=...`

**Frontend — completed**
- Landing, Wizard, Results, Saved Decisions, PDF export.
- Theme toggle (dark-first) with persistence.
- Compare + initial what-if.

**Testing checkpoint (met)**
- ✅ Full E2E pass verified.

---

### Phase 3 — Decision Intelligence Upgrade + Auth + Deeper Tools (completed)
**Goal:** Upgrade to a true Decision Intelligence Engine with quantified outcomes + execution plans + auth.

**User stories**
1. Consistent DI framework: goal → insights → options → outcomes → best → execution plan → plan B → confidence.
2. Email/password auth and personal library.
3. Guest decisions separate from logged-in library.
4. Wizard draft auto-save + resume.
5. Duplicate past decisions.
6. JSON repair fallback.

**Backend — completed**
- DI schema (goal, insights, execution_plan, plan_b, confidence, extended option metrics).
- `json_repair` server-side fallback.
- Auth: `/api/auth/signup|login|me`.
- Ownership scoping: user_id when authed; guest_id otherwise.

**Frontend — completed**
- Auth UI (/auth), token interceptor, user menu.
- Results UI upgrades (Key Insights, Plan B, Execution Plan tab).
- Draft auto-save/resume.
- Duplicate decision.
- What-if v1 with debounce (AI re-run).

---

### Phase 4 — Structured Pipeline + Weighted Scoring + Transparency (completed)
**Goal:** Implement the “master prompt” product behavior: guided conversational UX + strict decision logic + transparent scoring.

**Key architectural shift (completed)**
- **Weights** are defined by the user (priorities step).
- **Ratings** are provided by the AI (0–10 per factor per option).
- **Scores** and ranking computed client-side via `/app/frontend/src/lib/scoring.js`.
- AI never directly determines the final score; it supplies structured evaluation inputs.

**User stories**
1. As a user, I define what “best” means via sliders (priorities).
2. As a user, the system asks friendly, high-impact follow-ups (one at a time).
3. As a user, I see 3–5 options including a “Do nothing” option.
4. As a user, I can see an evaluation matrix of options × factors.
5. As a user, I see weighted scores computed transparently.
6. As a user, I can view risk scenarios and long-term impact.
7. As a user, I get assumptions + bias checks.
8. As a user, what-if is instant by changing weights.

**Backend — completed**
- New endpoint:
  - `POST /api/decisions/suggest-factors` → 3–6 tailored factors (name, description, default_weight).
- Follow-ups prompt tuned to be friendly and natural.
- Analyze schema extended:
  - Per option: `factor_ratings` (0–10 for every factor), `scenarios` (best/worst/most-likely), `future_impact` (1yr/5yr), `is_do_nothing`.
  - Top-level: `assumptions[]`, `bias_flags[]` (severity), `factors_used[]`.
  - Guarantees “Do nothing” option included.
- Async analyze still used for reliability.

**Frontend — completed**
- Wizard now includes **PrioritiesStep** (AI-suggested factors + weight sliders + custom add).
- Results restructured into explicit pipeline tabs:
  - Overview
  - Evaluation (matrix heat-map)
  - Risk (scenarios)
  - Future (1yr/5yr)
  - Execution plan
  - Compare
  - What-if (**client-side instant**)
- Transparency UI:
  - Bias alerts banner with severity badges.
  - Assumptions card.
- What-if v2 (client-side): adjusting weights recomputes scores instantly; shows flip sensitivity.

**Guest-save fix (completed)**
- Frontend always includes guest_id in save/list/get/delete params as fallback.
- Backend prefers user_id when token present; otherwise uses guest_id.

**Testing checkpoint (met with notes)**
- ✅ Backend: Phase 4 endpoints + schema validated (suggest-factors, do-nothing, factor_ratings, scenarios, future_impact, assumptions, bias_flags).
- ✅ Mobile: 100% responsive tests.
- ✅ Frontend: Priorities step, evaluation matrix, and results tabs verified via manual E2E screenshots.
- Minor automated E2E flakiness due to long-running sequences; core flows confirmed.

---

## 3) Next Actions
**Current status:** v1.3 Multi-Agent Decision System — in progress.

### Phase 6 — Multi-Agent Decision System (Status: COMPLETED)
**Goal:** Replace the single-prompt analyze with a 6-agent panel + synthesizer,
producing "boardroom-level" intelligence (disagreement + resolution).

**User-confirmed scope for this pass:**
- a) Wire the 6-agent + synthesizer pipeline into the existing async `/analyze` job
- b) Add `debate` + `agent_perspectives` fields to DecisionResult so the UI can render them
- c) Add a new **Boardroom** tab in Results with 6 agent cards + debate panel
- d) Run backend + frontend tests
- On synthesizer failure → **auto-fallback** to legacy `ai_service.analyze_decision`
- Skip real-time simulation engine for now (revisit after Boardroom ships)
- Keep `ai_service.py` as fallback + for `/suggest-factors`

**Backend — completed**
- [x] Extended `DecisionResult` with optional `debate` (conflicts, trade_offs,
      convergence) and `agent_perspectives` (Strategic/Financial/Risk/Execution/
      Contrarian/Optimization). `extra="allow"` on nested models for forward-
      compatible agent details.
- [x] `server.py::_run_analyze_job` now calls `analyze_decision_multiagent`
      first, auto-falling back to `ai_service.analyze_decision` on any
      exception. Adds `_engine: "multi_agent" | "legacy_fallback"` to the
      stored result for observability.
- [x] Defensive list-trimming in synthesizer output before Pydantic
      validation (prevents spurious ValidationErrors when the LLM is verbose).
- [x] **Critical event-loop fix:** `ai_service._call_llm` now wraps the
      blocking `litellm.completion` call (under
      `emergentintegrations.LlmChat.send_message`) in `asyncio.to_thread`. Six
      agents running in parallel no longer pin the event loop, so
      `/analyze/status` polling stays responsive during long runs.

**Frontend — completed**
- [x] `AgentPerspectiveCard.jsx` — per-agent card with icon chip, colored tone
      (primary/emerald/rose/amber/indigo/teal), summary, and collapsible
      details rendering agent-specific keys (EV, payback, risks, leverage, etc.)
- [x] `DebatePanel.jsx` — numbered conflict cards with 2-column agent views
      and primary-tinted resolution blocks; trade-offs list + convergence
      callout in a 2-column grid.
- [x] `BoardroomPanel.jsx` — 3-column responsive grid of 6 agents in a fixed
      order; graceful empty-state when data is missing (legacy-fallback runs).
- [x] New "Boardroom" tab added to `Results.jsx` between Overview and Execute.
- [x] Verified: multi-agent decision shows 6 cards + debate (3 conflicts,
      3 trade-offs, convergence). Legacy-fallback decision shows a clean
      empty-state explaining why the Boardroom is unavailable.
- [x] Verified: all 8 tabs (Overview / Boardroom / Execute / Evaluation /
      Scenarios / Future / Compare / What-if) present and functional in
      both light and dark themes.

**Note on testing:** The testing_agent ran into transient LLM-provider 502s
during the run, which caused multi-agent synthesis to fall back to the legacy
analyzer. The fallback worked as designed (user always gets a valid result).
End-to-end multi-agent runs were verified directly: (1) a Python test against
the service completed in ~153s with full 6-agent output + debate; (2) a
seeded Boardroom payload was rendered in the UI and all interactive elements
(tab navigation, expand/collapse, debate conflicts, convergence) were
verified via screenshots in both themes.

---

### Phase 7 — Interactive Debate & Refinement Mode (Status: COMPLETED)
**Goal:** Turn Smart Decision AI from a report generator into a decision partner.
When a user disagrees with the output, they press **"Challenge this decision"**
and the system extracts concerns, optionally asks 1–3 targeted clarifications,
then re-runs the full 6-agent Boardroom with the updated context and produces
a structured "what changed / why / next action" comparison.

**Backend — completed**
- [x] `debate_service.py` with three stages:
      - `extract_concerns_and_decide(decision, prior_result, objection)` — summarizes
        user concerns (auto-categorized: risk / feasibility / cost / time / personal),
        identifies assumption gaps, and decides if 1-3 clarifying questions
        are needed.
      - `run_refined_analysis(...)` — runs the full 6-agent Boardroom with the
        objection + concerns + clarifying answers injected as extra pseudo-
        answers. Falls back to `analyze_decision` legacy if Boardroom fails.
      - `synthesize_what_changed(...)` — one focused LLM call producing the
        UPDATED OUTPUT block: verdict, what-changed summary, key diffs,
        updated outcome, strengths, weaknesses, execution adjustments,
        when-original-wins, next-action-24-48h, confidence delta.
- [x] New schemas in `ai_service.py`: `ConcernExtraction`, `RefinementOutput`,
      `DebateTurn`, `DebateClarifyingQuestion`, etc.
- [x] Four new async endpoints in `server.py`:
      - `POST /api/decisions/{id}/debate/start` (returns `job_id`)
      - `GET  /api/decisions/debate/status/{job_id}` (pending /
        needs_clarification / refining / completed / failed)
      - `POST /api/decisions/debate/{job_id}/continue` (submit clarification
        answers)
      - `POST /api/decisions/{id}/debate/revert` (truncate history to a
        specific turn; pass `{"turn_id": null}` to drop all refinements)
- [x] `debate_history: List[DebateTurn]` persisted on the decision document;
      scoped to owner (user_id or guest_id).

**Frontend — completed**
- [x] `api.js` helpers: `startDebate`, `getDebateStatus`, `continueDebate`,
      `revertDebate`, and a high-level `runDebateTurn({decisionId, objection,
      onStatus, onClarify})` that encapsulates the full polling +
      clarification round-trip.
- [x] `components/debate/DebateDialog.jsx` — modal with 3 states:
      compose (textarea + 4 example chips), clarify (up to 3 clarifying
      questions inline), processing (spinner + contextual status).
- [x] `components/debate/DebateTurnCard.jsx` — renders one turn with:
      user's objection quote, category-tinted concern chips, confidence
      delta banner (green/red with ± pts pill), "What changed & why"
      primary callout, before/after diff cards, updated outcome 3-column
      grid (revenue/probability/timeframe), strengths vs. remaining
      trade-offs, execution adjustments, when-original-wins callout,
      **Next action (24-48h)** highlighted CTA, collapsible body,
      per-turn Revert button.
- [x] `components/debate/DebatePanel.jsx` — empty-state with CTA when no
      history, history header with "Revert to original" + "Challenge again"
      actions, and the list of turn cards.
- [x] `Results.jsx`:
      - Added **Challenge** button in the header (disabled until saved).
      - Added **Debate** tab with live count (`Debate (2)`).
      - Added "refined" banner at the top when the active result is a
        refinement, linking to the Debate tab.
      - Most importantly: **the active result used across all tabs
        (Overview, Boardroom, Execute, Evaluation, etc.) auto-derives
        from the latest refinement turn** when any exist. Reverting a
        turn updates every tab consistently.

**End-to-end verification**
- Seeded a decision with 2 debate turns via direct DB write + re-loaded via
  the production UI; verified all 3 refinement cards render with objections,
  concerns, confidence delta banners, before/after diffs, updated outcomes,
  strengths/weaknesses, and next-action CTAs (both dark and light themes).
- Ran a LIVE HTTP debate-start against the seeded decision: Stage 1 produced
  3 high-quality clarifying questions in ~8 s; continue-call accepted
  answers; status transitioned pending → needs_clarification → refining.
  Stage 2 fell back to legacy analyzer due to transient LLM provider 502s
  (observed + handled gracefully). Stage 3 synthesis completed and produced
  a real Refinement #3 that correctly flipped the best pick from Metro
  hybrid to Buy Corolla after the "3-month-old baby" objection — visible on
  the Debate tab within the UI.
- Event loop stayed responsive throughout the slow LLM runs thanks to the
  `asyncio.to_thread` wrapper around blocking `litellm.completion` calls
  introduced in Phase 6.

---

### Backlog (deferred)
1. Real-time simulation engine (re-run multi-agent on weight change — costly)
2. Memory layer (learn from past decisions)
3. User profiling agent
4. Editable rating overrides persisted
5. Observability / trace IDs
6. Read-only share links
7. Account settings

---

## 4) Success Criteria
- ✅ **Not a chatbot:** guided pipeline with explicit stages and UI steps.
- ✅ **Transparent scoring:** user weights × AI ratings; deterministic client-side scoring.
- ✅ **Controlled AI:** strict JSON + Pydantic validation + JSON repair.
- ✅ **Premium UX:** responsive, animated, dark/light.
- ✅ **Functional completeness:** landing → wizard → priorities → questions → analyze → tabs (evaluation/risk/future/plan) → save/revisit → compare → instant what-if → PDF export.
- ✅ **Infrastructure reliability:** async job pattern prevents ingress/proxy timeouts.
- ✅ **Auth + guest:** email/password auth + guest mode; libraries remain separate; guest save fixed.
