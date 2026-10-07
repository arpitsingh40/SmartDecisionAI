"""Tavily handler — web search + deep research via the Tavily API.

Registered as a native handler so the thread engine's tool_calls and the
execution dispatcher can run TAVILY_SEARCH / TAVILY_DEEP_RESEARCH without
any Composio connection.
"""

import time
import logging

from . import register

log = logging.getLogger("execution.handlers.tavily")

TOOLS = [
    {"name": "TAVILY_SEARCH", "description": "Search the live web for current facts, news, competitors, pricing, regulations", "inputSchema": {"query": "string", "max_results": "number"}},
    {"name": "TAVILY_DEEP_RESEARCH", "description": "Run a multi-query research pass over the company's market and store a sourced digest", "inputSchema": {}},
]


@register("TAVILY")
def handle(tool_name: str, args: dict) -> dict:
    t0 = time.time()
    try:
        from deep_research import tavily_search, deep_research
        from db import orgs_col, members_col
    except Exception as e:
        return {"error": f"deep_research import failed: {e}", "successful": False,
                "execution_time_ms": round((time.time() - t0) * 1000)}

    try:
        if tool_name == "TAVILY_SEARCH":
            query = (args.get("query") or "").strip()
            if not query:
                return {"error": "Missing query", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            results = tavily_search(query, max_results=int(args.get("max_results", 6)))
            if not results:
                return {"error": "No results", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            lines = []
            for i, r in enumerate(results, 1):
                lines.append(f"{i}. {r['title']}\n   {r['url']}\n   {r['content'][:600]}")
            return {"result": "\n".join(lines), "successful": True,
                    "execution_time_ms": round((time.time() - t0) * 1000)}

        if tool_name == "TAVILY_DEEP_RESEARCH":
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

        return {"error": f"Unsupported Tavily tool: {tool_name}", "successful": False,
                "execution_time_ms": round((time.time() - t0) * 1000)}
    except Exception as e:
        return {"error": str(e)[:300], "successful": False,
                "execution_time_ms": round((time.time() - t0) * 1000)}


handle.tool_list = TOOLS