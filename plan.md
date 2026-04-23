# Smart Decision AI — Development Plan

## 1) Objectives
- Deliver a premium, responsive decision-making web app for students/young professionals with a guided wizard and a results dashboard.
- Prove the core AI workflow works reliably **before** building the full UI: (a) dynamic follow-up questions, (b) strict-JSON decision analysis (3–5 options + scores + recommendation + confidence).
- Ship V1 with guest mode (localStorage guest ID), saved decisions in MongoDB, what-if + comparison tools, and PDF export.
- Meet quality bar: Linear/Vercel/Notion-inspired UI, dark-first + light toggle, smooth animations, accessible, and fast (<2s initial load on typical broadband).

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation: LLM structured outputs) 
**Goal:** Validate LLM integration + strict JSON schema + follow-up Q generation. Do not proceed until stable.

**User stories**
1. As a user, I can enter a decision and instantly get 5–8 tailored follow-up questions.
2. As a user, I can answer follow-ups and receive 3–5 concrete options with scores and outcomes.
3. As a user, I can trust the output is consistently structured (no malformed JSON).
4. As a user, I can see a clear best recommendation with a confidence score.
5. As a user, I get actionable, non-generic pros/cons and risk levels.

**Steps**
- Web research: best practices for “strict JSON” LLM prompting (schemas, retries, JSON repair, temperature settings).
- Define final Pydantic models (FollowUpQuestion, DecisionRequest, DecisionResult) and a single source-of-truth JSON schema.
- Create minimal Python script(s) to call Emergent Universal LLM:
  - `generate_followups(decision_context)` → list of questions (typed: text/slider/multi-choice).
  - `analyze_decision(decision_context, answers)` → DecisionResult JSON.
- Implement reliability loop:
  - low temperature + explicit JSON-only instruction
  - validate with Pydantic; on failure: reprompt with validation errors; final fallback: JSON repair.
- Add test fixtures (3–5 realistic decisions) and assert:
  - schema-valid JSON, 3–5 options, scores 0–100, best_option_id exists, confidence 0–100.

**Exit criteria (must pass)**
- 0% of fixture runs return Pydantic-valid JSON within max 2 retries.
- Output quality: options are distinct, non-trivial, and tailored to the provided context.

---

### Phase 2 — V1 App Development (Build around proven core)
**Goal:** Implement landing + wizard + results + saving, using the proven backend endpoints.

**User stories**
1. As a user, I can start from a landing page and begin a decision in one click.
2. As a user, I answer one question at a time with a clear progress indicator.
3. As a user, I can view a beautiful results dashboard with a highlighted recommendation.
4. As a user, I can save my decision automatically (guest mode) and revisit it later.
5. As a user, I can export the results as a PDF report.

**Backend (FastAPI + Motor + emergentintegrations)**
- Data model: DecisionDocument { guest_id, created_at, title, context, answers, result_json }.
- Endpoints:
  - `POST /api/guest/session` → returns/accepts guest_id (frontend stores in localStorage).
  - `POST /api/decisions/followups` → follow-up questions.
  - `POST /api/decisions/analyze` → returns DecisionResult.
  - `GET /api/decisions` (by guest_id) → list summaries.
  - `GET /api/decisions/{id}` → full decision.
  - `DELETE /api/decisions/{id}` → remove saved item.
- Guardrails: input length limits, timeouts, structured validation, consistent error shapes.

**Frontend (React + Tailwind + shadcn/ui + Framer Motion + Recharts + jsPDF)**
- App structure:
  - Landing page (hero, value props, “Try it” CTA, subtle motion demo).
  - Decision Wizard (stepper + question cards; supports text/slider/multi-choice; autosave draft in state).
  - Results Dashboard:
    - Best option hero card + score
    - ranked option cards
    - charts (score bars/radar), pros/cons table, confidence meter
  - Saved Decisions (history list + detail view).
  - PDF Export button (client-side render to PDF).
- Design system:
  - Inter font, dark-first palette + light toggle, soft shadows, glass panels, skeleton loaders.
  - Keyboard accessible components, focus states.

**Testing checkpoint (end of Phase 2)**
- One full E2E pass: landing → wizard → results → save → reopen → export PDF.

---

### Phase 3 — Interactive Tools + UX Polish
**Goal:** Add “what-if” + comparisons with fast iteration, plus stronger UX states.

**User stories**
1. As a user, I can adjust importance sliders and rerun analysis as a what-if scenario.
2. As a user, I can compare 2–3 options side-by-side.
3. As a user, I can duplicate a past decision and tweak answers.
4. As a user, I can see clear loading/progress states while AI runs.
5. As a user, I can quickly scan risks and tradeoffs with clear visuals.

**Steps**
- What-if mode:
  - lightweight re-analysis call with updated answers; debounce + cancel in-flight requests.
  - show “delta” changes in scores.
- Side-by-side comparison view (selected options → comparison table/cards).
- UX hardening:
  - empty states, error states, retry UI
  - skeletons, optimistic save status
  - polish motion and transitions (Framer Motion).

**Testing checkpoint (end of Phase 3)**
- E2E pass focused on what-if + comparison + saved decision flows.

---

### Phase 4 — Stabilization, Performance, and Production Readiness
**Goal:** Make it robust and fast; ensure no regressions.

**User stories**
1. As a user, the app feels fast with smooth transitions and minimal waiting confusion.
2. As a user, I never lose my work if I refresh mid-wizard.
3. As a user, errors are recoverable with clear guidance.
4. As a user, the app works well on mobile.
5. As a user, I can manage my saved decisions (view/delete) confidently.

**Steps**
- Performance: lazy-load heavy views, optimize bundle, cache decision list, compress assets.
- Reliability: structured logging, stricter validation, rate-limit per guest_id (basic).
- Accessibility: tab order, ARIA labels, contrast checks.
- Regression tests: repeat fixture decisions and UI smoke tests.

## 3) Next Actions
1. Implement Phase 1 POC scripts + Pydantic schema + retry/repair loop.
2. Confirm model choice within Emergent key (default to best-available reasoning model) and settle the exact follow-up question types.
3. Once Phase 1 exit criteria passes, scaffold backend endpoints and minimal React wizard UI.
4. Build results dashboard + saving (MongoDB + guest_id) and run one E2E test.

## 4) Success Criteria
- **Core AI reliability:** Pydantic-valid JSON returned consistently (fixtures pass; 0% within max 2 retries).
- **User value:** outputs are specific, provide 3–5 viable options, and a clear best recommendation with confidence.
- **UX quality:** premium look/feel, responsive, smooth animations, clear hierarchy, accessible controls.
- **Functional completeness (V1):** landing → wizard → results → save/revisit → what-if/compare → PDF export.
- **Performance:** initial load perceived fast; no blocking UI; <2s typical first contentful load target.