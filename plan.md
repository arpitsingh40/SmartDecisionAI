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
**Current status:** v1.2 Structured Decision Engine is complete.

Recommended next actions (optional):
1. **Test stabilization:** reduce timing flakiness in automated E2E by increasing waits around async analyze completion.
2. **Editable rating overrides → persisted:** wire EvaluationMatrix edit-mode to update local state and optionally persist overrides into the saved decision.
3. **Observability:** add trace IDs and endpoint latency metrics.
4. **Sharing:** read-only share links.
5. **Account settings:** change password, update profile.

---

## 4) Success Criteria
- ✅ **Not a chatbot:** guided pipeline with explicit stages and UI steps.
- ✅ **Transparent scoring:** user weights × AI ratings; deterministic client-side scoring.
- ✅ **Controlled AI:** strict JSON + Pydantic validation + JSON repair.
- ✅ **Premium UX:** responsive, animated, dark/light.
- ✅ **Functional completeness:** landing → wizard → priorities → questions → analyze → tabs (evaluation/risk/future/plan) → save/revisit → compare → instant what-if → PDF export.
- ✅ **Infrastructure reliability:** async job pattern prevents ingress/proxy timeouts.
- ✅ **Auth + guest:** email/password auth + guest mode; libraries remain separate; guest save fixed.
