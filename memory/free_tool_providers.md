# Free tool providers — the sourcing plan (from public-apis / free-for-dev)

> Sources (catalogs, NOT dependencies — never install or vendor them):
> - https://github.com/public-apis/public-apis — free *data/utility* APIs (keyless or free key)
> - https://github.com/ripienaar/free-for-dev — SaaS/PaaS/IaaS with real free tiers
>
> Rule of use: read the list → pick a provider → check its terms and free limits →
> wire it as a native handler (`backend/execution/handlers/`) or through Composio if it
> needs OAuth. Catalogs are directories; limits and terms change — re-verify before launch.

## Adopted in code

| Provider | What for | Route | Notes |
|---|---|---|---|
| **Frankfurter** (`api.frankfurter.app`) | FX rates for pricing/invoicing | Built-in handler `handlers/frankfurter.py`, tool prefix `FRANKFURTER` | No key, commercial use OK, no quotas. Surfaced as `builtin: ["frankfurter"]` on the invoicing capability in `genesis.py`; shown as "Built in" in the builder Tools step. |
| **ip-api.com** (`/json/{ip}`) | Geo lookup for traffic sessions | Existing use in `backend/admin.py` | Free tier is **non-commercial only**. Keep it internal/admin. Swap before scaling publicly. |
| **Tavily** | Web search + deep research | Existing handler `handlers/tavily.py` (`TAVILY_*`) | Needs `TAVILY_API_KEY`; free monthly credit tier. |

## Rejected after reading terms

| Provider | Why not |
|---|---|
| **Public Nominatim** (`nominatim.openstreetmap.org`) | Usage policy forbids suggestion/auto-generation by no-code/vibe-coding platforms (that is what the builder is), discourages periodic app requests, requires caching/proxy and switch-away ability. Use a paid geocoder or self-hosted Photon/Nominatim instead. |

## Candidate picks per capability (next ones to wire)

| Capability | Free provider | Route | Free tier note |
|---|---|---|---|
| Web search (fallback without Tavily key) | Brave Search API / DuckDuckGo | Key | Brave: monthly free credits (card for verification) |
| News / market signals | NewsAPI / GNews | Key | 100 req/day class; check commercial terms |
| Currency (backup) | Frankfurter self-host | Docker | Zero external dependency |
| Holidays for calendar agent | Nager.Date (`date.nager.at`) | Keyless | Verify terms before bundling |
| PDF for reports/decks (`capabilities.py`) | Browser print / self-hosted Gotenberg | Self-host | Avoids uploading user docs to a third-party API |
| Screenshots / link previews | Microlink free tier | Key | 50 req/day free |
| Email (transactional + re-engagement nudges) | Resend / Brevo / SMTP2GO | Key | Closes the SMTP open item in PRD; free daily/monthly caps |
| Error monitoring | Sentry free tier | Key | Covers `map_capabilities` monitoring need free |
| Hosting / DB for SmartDecigen | MongoDB Atlas M0 / Render / Railway / Fly free | Key | Replace local-only runs; no card tiers exist |
| Static sites the builder deploys | Cloudflare Pages/Workers | Key | 100k requests/day free; replaces Vercel-only path |

## Free-tier defaults in code

- `backend/execution/connections.py` → `FREE_TIER_TOOLKITS` (+ those flagged `free: true` in
  `suggest_tools_for_function`, sorted free-first) and `BUILTIN_BY_FUNCTION`
  (finance → frankfurter).
- When adding a provider: 1) write the handler with `@register("PREFIX")` + `handle.tool_list`;
  2) add its toolkit slug to `FREE_TIER_TOOLKITS` if it has a free tier;
  3) if it needs no connection at all, add it to `genesis.map_capabilities` under `builtin`
  so the builder shows it as "Built in".
