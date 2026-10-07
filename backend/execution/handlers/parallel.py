"""Parallel (PWS) handler — objective-based web search + full-page extraction.

Registered as a native handler so the thread engine's tool_calls and the
execution dispatcher can run PARALLEL_SEARCH / PARALLEL_EXTRACT / PARALLEL_DEEP_RESEARCH
without any Composio connection.

Parallel is the premium research engine: one call takes a natural-language objective
plus keyword queries and returns dense LLM-optimized excerpts. Extract converts any
public URL (including JS-heavy pages and PDFs) into clean markdown. Tavily remains the
cheap fallback for quick keyword lookups.
"""

import time
import logging

from . import register

log = logging.getLogger("execution.handlers.parallel")

TOOLS = [
    {"name": "PARALLEL_SEARCH", "description": "Objective-based web search returning dense LLM-optimized excerpts. Pass an objective plus 2-3 keyword queries. Use for market research, competitor pricing, news, regulations.", "inputSchema": {"objective": "string", "search_queries": "list", "max_results": "number"}},
    {"name": "PARALLEL_EXTRACT", "description": "Fetch full clean markdown of public URLs (competitor pages, pricing pages, PDFs, JS-heavy sites) to ground a decision in the actual source text.", "inputSchema": {"urls": "list", "objective": "string"}},
    {"name": "PARALLEL_DEEP_RESEARCH", "description": "Run a full multi-query research pass over the company's market via Parallel (Tavily fallback) and store a sourced digest on the org", "inputSchema": {}},
]


@register("PARALLEL")
def handle(tool_name: str, args: dict) -> dict:
    t0 = time.time()
    try:
        from deep_research import parallel_search, parallel_extract, deep_research
        from db import orgs_col, members_col
    except Exception as e:
        return {"error": f"deep_research import failed: {e}", "successful": False,
                "execution_time_ms": round((time.time() - t0) * 1000)}

    try:
        if tool_name == "PARALLEL_SEARCH":
            objective = (args.get("objective") or "").strip()
            queries = args.get("search_queries") or []
            if not queries and objective:
                queries = [objective]
            if not objective and not queries:
                return {"error": "Missing objective or search_queries", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            results = parallel_search(objective or queries[0], queries,
                                      max_results=int(args.get("max_results", 6)))
            if not results:
                return {"error": "No results", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            lines = []
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. {r['title']}\n   {r['url']}\n   {r['content'][:800]}")
            return {"result": "\n\n".join(lines), "successful": True,
                    "execution_time_ms": round((time.time() - t0) * 1000)}

        if tool_name == "PARALLEL_EXTRACT":
            urls = args.get("urls") or []
            if not urls:
                return {"error": "Missing urls", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            results = parallel_extract(urls, args.get("objective") or "")
            if not results:
                return {"error": "No extracted content", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            lines = []
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. {r['title']} — {r['url']}\n{r['content'][:3000]}")
            return {"result": "\n\n".join(lines), "successful": True,
                    "execution_time_ms": round((time.time() - t0) * 1000)}

        if tool_name == "PARALLEL_DEEP_RESEARCH":
            org_id = args.get("org_id", "")
            if org_id:
                org = orgs_col.find_one({"id": org_id})
            else:
                m = members_col.find_one({"status": "active", "role": "owner"}) if members_col else None
                org = orgs_col.find_one({"id": m["org_id"]}) if m and m.get("org_id") else None
            if not org:
                return {"error": "No org to research", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            stored = deep_research(org)
            digest = (stored.get("digest") or "").strip()
            if not digest:
                return {"error": "Research produced no digest", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            cites = "; ".join(c["url"] for c in stored.get("citations", [])[:3])
            return {"result": f"{digest[:1500]}\nSources: {cites}", "successful": True,
                    "execution_time_ms": round((time.time() - t0) * 1000)}

        return {"error": f"Unsupported Parallel tool: {tool_name}", "successful": False,
                "execution_time_ms": round((time.time() - t0) * 1000)}
    except Exception as e:
        return {"error": str(e)[:300], "successful": False,
                "execution_time_ms": round((time.time() - t0) * 1000)}


handle.tool_list = TOOLS