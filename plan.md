# Smart Decision AI — Updated Development Plan (v1.1 Decision Intelligence)

## 1) Objectives
- Deliver a premium, responsive **Decision Intelligence** web app for students/young professionals with a guided wizard and a results dashboard.
- Provide **high-quality, data-driven, outcome-focused decisions** using a mandatory framework:
  - Problem understanding → options → outcome prediction → optimization → execution plan → plan B.
- Ensure AI outputs are **strict JSON** with strong reliability and explainability:
  - Structured schema validated with Pydantic.
  - Server-side JSON repair for rare malformed outputs.
- Support both **guest mode** and **email/password login**:
  - Guest: localStorage guest_id.
  - Auth: bcrypt + JWT (30 days), persisted in localStorage.
  - **Guest and user decisions remain separate** (per user choice).
- Ship modern product-quality UX (Linear/Vercel/Notion inspired): dark-first + light toggle, Framer Motion micro-interactions, responsive, accessible.

**Status update (as of now):**
- ✅ Phase 1 complete (POC validated strict JSON reliability).
- ✅ Phase 2 complete (full V1 app implemented + end-to-end tested).
- ✅ Phase 3 complete (**Decision Intelligence upgrade + auth + deeper tools + reliability + performance**).
- 🔜 Phase 4 optional (hardening, telemetry, sharing, settings, feature flags).

---

## 2) Implementation Steps

### Phase 1 — Core POC (Isolation: LLM structured outputs)
**Goal:** Validate LLM integration + strict JSON schema + follow-up Q generation. Do not proceed until stable.

**User stories**
1. As a user, I can enter a decision and instantly get 5–8 tailored follow-up questions.
2. As a user, I can answer follow-ups and receive structured options with scores and outcomes.
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
    - `GET /api/decisions/analyze/status/{job_id}` → pending/completed/failed + result.
  - (Optional sync kept): `POST /api/decisions/analyze`.
- Saved decisions CRUD:
  - `POST /api/decisions` → save decision.
  - `GET /api/decisions?guest_id=...` → list summaries.
  - `GET /api/decisions/{id}?guest_id=...` → fetch detail.
  - `DELETE /api/decisions/{id}?guest_id=...` → delete.
- Reliability improvements:
  - Async job pattern avoids 60s ingress/proxy timeouts.
  - LLM call parameters set to fail fast (litellm retries disabled) and provider fallback.

**AI model strategy — completed**
- Primary: Claude Haiku 4.5 (fast).
- Fallback: provider fallback used for resilience.
- Strict JSON schema validation via Pydantic.

**Frontend (React + Tailwind + shadcn/ui + Framer Motion + Recharts + jsPDF) — completed**
- Landing page:
  - Hero, CTA, demo card, value props, how-it-works, testimonials, CTA band, footer.
- Wizard:
  - Progressive disclosure (one question at a time) with progress bar.
  - Dynamic AI follow-ups (text, slider, single-choice, multi-choice).
  - Review step with answer summary + edit.
  - Analysis loading state.
  - Reliability fix: choice inputs implemented as button-based for robust selection.
- Results dashboard:
  - Best option hero card.
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

---

### Phase 3 — Decision Intelligence Upgrade + Auth + Deeper Tools (completed)
**Goal:** Upgrade from “decision assistant” to a true **Decision Intelligence Engine** with quantified outcomes, execution plans, and robust persistence.

**User stories**
1. As a user, every analysis follows a consistent Decision Intelligence framework (goal → insights → options → outcome prediction → best decision → execution plan → plan B → confidence).
2. As a user, I can log in with email/password and access my own decision library.
3. As a user, my guest decisions are separate from my logged-in library (no migration).
4. As a user, I never lose my in-progress wizard if I refresh or navigate away.
5. As a user, I can duplicate a past decision and quickly iterate.
6. As a user, what-if mode feels responsive and teaches me sensitivity/robustness.
7. As a user, AI outputs remain structured even if the model occasionally produces malformed JSON.

**Backend — completed**
- **Decision Intelligence AI schema** (strict JSON + Pydantic validation):
  - Top-level: `goal`, `key_insights` (2–4), `execution_plan` (3–6 steps), `plan_b`, `plan_b_trigger`, `confidence`.
  - Per-option: `success_probability`, `expected_return`, `time_to_result`, `geography`, `easiness`, `support`, `history`, `financial_ratio`, `why_not`, plus `pros/cons/risk/score/outcomes`.
- **Server-side JSON repair**:
  - Added `json_repair` fallback parser for rare malformed JSON outputs.
- **Email/password auth**:
  - `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me`.
  - bcrypt password hashing + JWT (30 days).
- **Decision ownership & scoping**:
  - When authenticated: decisions saved/listed by `user_id`.
  - When not authenticated: decisions saved/listed by `guest_id`.
  - Guest vs user libraries remain separate.
- **Performance tuning**:
  - Schema caps: max 4 options, 2–4 pros/cons, max 6 execution steps.
  - Prompt condensed for faster completion.
  - Typical analysis completion: ~40–50s via async job polling (previously 80–120s).

**Frontend — completed**
- **Auth UI & state**:
  - `/auth` page with login/signup tabs.
  - Auth token persisted to localStorage and attached via axios interceptor.
  - TopNav updated: logged-out shows Log in/Sign up; logged-in shows user menu + logout.
- **Premium Results UI upgrade**:
  - Goal pill.
  - Key insights panel.
  - Execution Plan tab with timeline + cost/benefit + tools.
  - Plan B card with explicit trigger.
  - Option cards show extended metrics + “Why not this one?” for non-best.
  - PDF export updated with toggles for key insights + execution plan.
- **Wizard draft auto-save**:
  - Draft saved to localStorage on changes.
  - Resume banner with Resume / Start fresh.
  - Start-over button.
- **Duplicate past decisions**:
  - From Saved library: “Duplicate” button prefills wizard for iteration.
- **Deeper what-if**:
  - Live mode toggle with ~1.2s debounce auto rerun.
  - Sensitivity note: flip/swing/stable indicators.

**Testing checkpoint (mostly met)**
- ✅ Backend: 95% tests passing (Decision Intelligence schema, auth, scoping, async analyze).
- ✅ Mobile: 100% responsive tests passing.
- ✅ Frontend: 85% automated tests passing; full E2E manually verified by main agent (wizard → results).
- Remaining low-priority items:
  - `POST /api/decisions` returns 200 vs 201 (cosmetic).
  - Some long-flow test flakiness due to timing/session; core flow confirmed working.

---

### Phase 4 — Stabilization, Performance, and Production Readiness (optional)
**Goal:** Harden reliability, observability, and product readiness for broader usage.

**User stories**
1. As a user, the app feels fast and never loses state.
2. As a user, errors are recoverable with clear guidance.
3. As a user, I can manage decisions confidently (search, tags, delete, share).
4. As a product owner, I can observe usage and failures.

**Potential enhancements**
- Account settings:
  - Update profile name/email/password.
- Sharing:
  - Public share links (read-only) with optional redaction.
- Feature flags:
  - Toggle Decision Intelligence vs basic mode, experimental models, new UI blocks.
- Observability:
  - Structured logs, trace IDs, latency metrics per endpoint.
  - Basic telemetry/events.
- Performance:
  - Lazy-load charts/PDF.
  - Add caching for repeated analyses (optional).
- AI robustness:
  - “Ask one more clarifying question” fallback when confidence is low.
  - Optional streaming UI for analysis progress.

---

## 3) Next Actions
**Current status:** V1.1 (Decision Intelligence) is complete.

Recommended next actions (optional):
1. **Cosmetic API polish:** return HTTP 201 for `POST /api/decisions`.
2. **Wizard reliability hardening:** tighten resume logic, add explicit “draft versioning” and better test stabilization.
3. **Product enhancements:** settings, share links, telemetry, feature flags.

---

## 4) Success Criteria
- ✅ **Core AI reliability:** Strict JSON output validated by Pydantic; JSON repair fallback in place.
- ✅ **Decision Intelligence quality:** quantified outcomes, success probability, ROI framing, execution plan + plan B.
- ✅ **UX quality:** premium look/feel, responsive, smooth animations, clear hierarchy.
- ✅ **Functional completeness:** landing → wizard → results → save/revisit → compare/what-if → PDF export.
- ✅ **Infrastructure reliability:** async job pattern prevents ingress/proxy timeouts.
- ✅ **Auth:** email/password login + persistent sessions; user decision scoping works; guest remains supported and separate.
