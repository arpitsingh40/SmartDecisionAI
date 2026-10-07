# SmartDecigen — Positioning (canonical, Sept 2026)

> This document is the canonical product story. It supersedes
> `strategy_north_star.md` and `plan.md` (both kept for history only).
> Every landing claim, feature decision, and pricing change is checked against it.

## One-liner
**Type an idea. Get a company.**

Category line: **The autonomous business builder.**

## Who it's for
**Anyone with an idea.** Not founders-only, not teams-only. A person with a
business idea should be able to describe it in plain words and watch a company
get built around it.

## The three pillars (the story)
1. **Builds the company.** Vision in → digital twin → mission (North Star,
   target, deadline, priorities, rules) → organization (divisions, executives,
   culture) → first-week tasks. Real records, created in the database, visible
   in the UI.
2. **Runs it.** Executives and Business OS run cycles through connected tools,
   every decision goes through the approval queue, spend is capped, one kill
   switch stops everything.
3. **Proves it.** Every agent decision, executed action, verified outcome and
   task event lands in the Record Room. Nothing is self-reported; outcomes are
   verified or honestly marked manual.

## What we are NOT
- Not a chatbot (no chat boxes as the product).
- Not a task assistant that does errands for you (that is Instinct-class).
- Not "AI advice" — advice is the input; a running, auditable company is the output.

## Claims policy (no exceptions)
- Every number and claim on any public surface maps to a working surface
  (route, endpoint, record) in this repo. No aspirational counts.
- If a capability only works manually or with a tool connected, say so
  ("tasks go to your manual queue until you connect tools").
- The engine asks before assuming and says "unknown" rather than inventing.

## The demo path (what "demoable" means)
Landing CTA → signup → `/app/build` wizard: describe an idea → answer the
engine's challenge questions → approve mission → approve organization (see the
executives created) → connect tools (or continue without) → launch first-week
tasks → Mission Control approval queue → Record Room. Every step is real; no
mock screens required for the core story.

## Funnel
Landing → auth (`?next=/app/build`) → Builder wizard → Mission Control /
Business OS → Record Room. The builder is the wow moment; the run + proof
loop is the retention.

## Open / deferred (do not let these block the story)
- Pricing: landing still shows credit packs; decision to move to a
  value-priced plan is deferred and tracked separately.
- Genesis LLM calls are not credit-metered yet; metering is deferred.
- Public no-auth interactive demo: deferred; signup-gated wizard first
  (free signup credits make it low-friction).
