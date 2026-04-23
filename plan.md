# Smart Decision AI — Updated Development Plan

## 1) Objectives
- Deliver a premium, responsive decision-making web app for students/young professionals with a guided wizard and a results dashboard.
- Prove the core AI workflow works reliably **before** building the full UI: (a) dynamic follow-up questions, (b) strict-JSON decision analysis (3–5 options + scores + recommendation + confidence).
- Ship V1 with guest mode (localStorage guest ID), saved decisions in MongoDB, what-if + comparison tools, and PDF export.
- Meet quality bar: Linear/Vercel/Notion-inspired UI, dark-first + light toggle, smooth animations, accessible, and fast.

**Status update (as of now):**
- ✅ Phase 1 complete (POC validated strict JSON reliability).
- ✅ Phase 2 complete (full V1 app implemented + end-to-end tested).
- 🔜 Phase 3 optional (polish, edge cases, enhancements) — only if requested.

---

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation: LLM structured outputs)
**Goal:** Validate LLM integration + strict JSON schema + follow-up Q generation. Do not proceed until stable.

**User stories**
1. As a user, I can enter a decision and instantly get 5–8 tailored follow-up questions.
2. As a user, I can answer follow-ups and receive 3–5 concrete options with scores and outcomes.
3. As a user, I can trust the output is consistently structured (no malformed JSON).
4. As a user, I can see a clear best recommendation with a confidence score.
5. As a user, I get actionable, non-generic pros/cons and risk levels.

**Implementation (completed)**
- Defined Pydantic models and strict JSON schema.
- Built POC script with validation + retry loop.
- Validated Emergent Universal LLM integration.

**Results**
- ✅ Claude Sonnet 4.5 passed 3/3 fixtures with schema-valid JSON.
- ✅ Outputs were specific, distinct, and context-aware.

**Exit criteria (met)**
- ✅ Reliable structured JSON with strong output quality.

---

### Phase 2 — V1 App Development (Build around proven core)
**Goal:** Implement landing + wizard + results + saving, using the proven backend endpoints.

**User stories**
1. As a user, I can start from a landing page and begin a decision in one click.
2. As a user, I answer one question at a time with a clear progress indicator.
3. As a user, I can view a beautiful results dashboard with a highlighted recommendation.
4. As a user, I can save my decision automatically (guest mode) and revisit it later.
5. As a user, I can export the results as a PDF report.

**Backend (FastAPI + Motor + emergentintegrations) — completed**
- Data model: DecisionDocument { guest_id, created_at, title, decision, answers, result }.
- Guest mode:
  - `POST /api/guest/session` → guest_id (stored in localStorage).
- Decision flow endpoints:
  - `POST /api/decisions/followups` → dynamic follow-up questions.
  - **Async analyze (added to bypass ingress timeout):**
    - `POST /api/decisions/analyze/start` → returns job_id immediately.
    - `GET /api/decisions/analyze/status/{job_id}` → returns pending/completed/failed + result.
  - (Optional sync endpoint kept): `POST /api/decisions/analyze`.
- Saved decisions CRUD:
  - `POST /api/decisions` → save decision.
  - `GET /api/decisions?guest_id=...` → list summaries.
  - `GET /api/decisions/{id}?guest_id=...` → fetch detail.
  - `DELETE /api/decisions/{id}?guest_id=...` → delete.
- Reliability improvements:
  - Async job pattern avoids 60s ingress/proxy timeouts.
  - LLM call parameters set to fail fast (litellm retries disabled) and use provider fallback.

**AI model strategy — completed**
- Primary: Claude Haiku 4.5 (fast; typical ~5–15s).
- Fallback: Claude Sonnet 4.5 (deeper reasoning).
- Strict JSON schema validation enforced via Pydantic.

**Frontend (React + Tailwind + shadcn/ui + Framer Motion + Recharts + jsPDF) — completed**
- Landing page:
  - Hero, CTA, demo card, value props, how-it-works, testimonials, CTA band, footer.
- Wizard:
  - Progressive disclosure (one question at a time) with progress bar.
  - Dynamic AI follow-ups (text, slider, single-choice, multi-choice).
  - Review step with answer summary + edit.
  - Analysis loading state.
  - **Reliability fix:** replaced single-choice + multi-choice UI with button-based inputs to avoid flaky selection issues.
- Results dashboard:
  - Best option hero card with score, risk, outcomes.
  - Ranked option cards with expand/collapse.
  - Score bar chart (Recharts).
  - Pros/cons comparison table.
  - Confidence meter + reasoning panel.
- Interactive tabs:
  - Compare mode (select up to 3 options side-by-side).
  - What-if mode (edit answers + re-run analysis; show score deltas).
- Saved decisions:
  - List, open, delete, empty state.
- PDF export:
  - Export dialog with include/exclude toggles.
- Theme:
  - Dark-first theme toggle with localStorage persistence.

**Testing checkpoint (met)**
- ✅ Full E2E pass verified:
  - landing → wizard → follow-ups → review → async analyze → results → save → reopen → export dialog.
- Example E2E result:
  - “Should I buy a PS5 or Xbox Series X?” → best: “Buy PS5 now, Xbox later” (score 88, confidence 87%) in ~18s.

---

### Phase 3 — Interactive Tools + UX Polish (optional, on request)
**Goal:** Refine interactivity, performance, and decision exploration depth.

**User stories**
1. As a user, I can adjust importance sliders and rerun analysis as a what-if scenario.
2. As a user, I can compare 2–3 options side-by-side.
3. As a user, I can duplicate a past decision and tweak answers.
4. As a user, I can see clear loading/progress states while AI runs.
5. As a user, I can quickly scan risks and tradeoffs with clearer visuals.

**Current status**
- ✅ What-if and compare are implemented in V1.

**Potential enhancements**
- What-if:
  - debounce + cancel in-flight requests
  - show clearer score deltas (sparklines)
  - “sensitivity insights” (which answers change ranking most)
- Compare:
  - add mobile carousel + sticky headers
  - allow pinning best option
- Decision management:
  - duplicate decision + edit answers
  - tagging, search, filtering
- AI robustness:
  - add JSON-repair step (server-side) for rare malformed outputs
  - add “ask 1 more clarifying question” fallback when confidence is low

**Testing checkpoint**
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

**Current status**
- ✅ V1 is production-ready for guest-mode usage.

**Next hardening steps (if needed)**
- Performance:
  - lazy-load heavy views/components (charts, PDF)
  - optimize bundle and caching
- Reliability:
  - persist wizard draft to localStorage
  - rate limit per guest_id
  - structured logs + monitoring
- Accessibility:
  - tab order validation, ARIA labels audit, contrast review
- Regression testing:
  - repeat fixture decisions on schedule
  - smoke tests for all routes

---

## 3) Next Actions
**V1 is complete.** Next actions are optional depending on desired scope:
1. (Optional) Phase 3 enhancements: deeper what-if + compare polish, duplicate/edit flow.
2. (Optional) Add JSON repair + additional guardrails for rare malformed outputs.
3. (Optional) Add persistence for in-progress wizard drafts.
4. (Optional) Add analytics/events and basic rate limiting.

---

## 4) Success Criteria
- ✅ **Core AI reliability:** Pydantic-valid JSON returned consistently (POC passed).
- ✅ **User value:** tailored 3–5 viable options, clear best recommendation, confidence score.
- ✅ **UX quality:** premium look/feel, responsive, smooth animations, clear hierarchy.
- ✅ **Functional completeness (V1):** landing → wizard → results → save/revisit → what-if/compare → PDF export.
- ✅ **Infrastructure reliability:** async job pattern prevents ingress/proxy timeouts.
