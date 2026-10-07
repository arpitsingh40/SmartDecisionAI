"""Deep Research — Parallel (PWS) + Tavily web research for the decision brain.

Runs a small multi-query research pass around the company's market, synthesizes the
findings into a sourced digest with an LLM, and stores it on the org as
`industry_research = {digest, citations, generated_at, queries}`.

Parallel (primary): objective-based search returning dense LLM-optimized excerpts, plus
Extract for full-page markdown. Tavily (fallback): cheap per-query keyword search used
when Parallel is unavailable or returns nothing.

The digest is consumed by decision_brain._industry_block (INDUSTRY_RESEARCH) and the
thread engine, so every grounded reply can cite current, real market data.
"""
import os
import json
import time
import logging
from datetime import datetime, timezone

import requests

log = logging.getLogger("deep_research")

TAVILY_API_KEY = (os.environ.get("TAVILY_API_KEY") or "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").strip()
TAVILY_URL = "https://api.tavily.com/search"

PARALLEL_API_KEY = (os.environ.get("PARALLEL_API_KEY") or "VA7cam8P_kqPitxYHVSjVFs45f_z1qa-KQrWgouB").strip()
PARALLEL_URL = "https://api.parallel.ai/v1"

MAX_RESULTS = 6
RESEARCH_TTL_DAYS = int(os.environ.get("RESEARCH_TTL_DAYS", "7"))


def parallel_search(objective: str, search_queries: list, max_results: int = MAX_RESULTS,
                    mode: str = "advanced", max_chars_per_result: int = 4000) -> list:
    """Run one Parallel search. Returns [{title, url, content, publish_date, score}]."""
    if not PARALLEL_API_KEY:
        log.warning("Parallel API key missing — skipping Parallel search")
        return []
    queries = [q for q in (search_queries or []) if q and isinstance(q, str)][:5]
    if not queries:
        queries = [objective[:200]]
    body = {
        "objective": (objective or "")[:5000],
        "search_queries": queries,
        "mode": mode if mode in ("turbo", "basic", "advanced") else "advanced",
    }
    if max_results:
        body["advanced_settings"] = {"max_results": max_results,
                                     "excerpt_settings": {"max_chars_per_result": max_chars_per_result}}
    try:
        r = requests.post(f"{PARALLEL_URL}/search", json=body, timeout=60,
                          headers={"x-api-key": PARALLEL_API_KEY, "Content-Type": "application/json"})
        if r.status_code != 200:
            log.warning(f"parallel {r.status_code}: {r.text[:300]}")
            return []
        data = r.json()
        out = []
        for res in data.get("results", []):
            excerpts = res.get("excerpts") or []
            content = "\n\n".join(e[:max_chars_per_result] for e in excerpts)[:max_chars_per_result * 2]
            out.append({
                "title": (res.get("title") or "")[:200],
                "url": (res.get("url") or "")[:400],
                "content": content,
                "publish_date": res.get("publish_date") or "",
                "score": 1,
            })
        return out
    except Exception as e:
        log.warning(f"parallel search failed: {e}")
        return []


def parallel_extract(urls: list, objective: str = "") -> list:
    """Convert public URLs into clean LLM-optimized markdown via Parallel Extract.
    Returns [{title, url, content}]."""
    if not PARALLEL_API_KEY:
        return []
    urls = [u for u in (urls or []) if u and isinstance(u, str)][:5]
    if not urls:
        return []
    body = {"urls": urls, "objective": (objective or "")[:2000]}
    try:
        r = requests.post(f"{PARALLEL_URL}/extract", json=body, timeout=90,
                          headers={"x-api-key": PARALLEL_API_KEY, "Content-Type": "application/json"})
        if r.status_code != 200:
            log.warning(f"parallel extract {r.status_code}: {r.text[:300]}")
            return []
        data = r.json()
        out = []
        for res in data.get("results", []):
            excerpts = res.get("excerpts") or []
            content = "\n\n".join(str(e) for e in excerpts)[:20000]
            out.append({
                "title": (res.get("title") or "")[:200],
                "url": (res.get("url") or "")[:400],
                "content": content,
                "publish_date": res.get("publish_date") or "",
                "score": 1,
            })
        return out
    except Exception as e:
        log.warning(f"parallel extract failed: {e}")
        return []


def tavily_search(query: str, max_results: int = MAX_RESULTS, search_depth: str = "advanced",
                  max_chars: int = 4000) -> list:
    """Run one Tavily search. Returns [{title, url, content, score}]."""
    if not TAVILY_API_KEY:
        return []
    try:
        r = requests.post(TAVILY_URL, json={
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
        }, timeout=45)
        if r.status_code != 200:
            log.warning(f"tavily {r.status_code}: {r.text[:300]}")
            return []
        data = r.json()
        out = []
        for res in data.get("results", []):
            content = (res.get("content") or "")[:max_chars]
            if not content.strip():
                content = (res.get("raw_content") or "")[:max_chars]
            out.append({
                "title": (res.get("title") or "")[:200],
                "url": (res.get("url") or "")[:400],
                "content": content,
                "score": res.get("score", 0),
            })
        return out
    except Exception as e:
        log.warning(f"tavily search failed: {e}")
        return []


def _org_queries(org: dict) -> list:
    """Build 3-5 focused research queries from the org's market + strategy fields."""
    ind = org.get("industry")
    if isinstance(ind, dict):
        bits = [ind.get("industry"), ind.get("segment"), ind.get("geography"), ind.get("model")]
        bits = [b.strip() for b in bits if isinstance(b, str) and b.strip()]
        market = " ".join(bits)
    elif isinstance(ind, str) and ind.strip():
        market = ind.strip()
    else:
        market = ""
    market = market or (org.get("name") or "")
    ns = (org.get("north_star") or "").strip()
    target = (org.get("target") or "").strip()
    queries = []
    if market:
        queries.append(f"{market} market size growth 2026 trends")
        queries.append(f"{market} top competitors pricing comparison")
        queries.append(f"{market} regulations funding opportunities")
    if ns:
        queries.append(f"{ns} {market}")
    if not queries:
        queries.append("startup founder market research 2026")
    return queries[:5]


def _synthesize_digest(org: dict, results: list) -> dict:
    """Synthesize search results into a sourced digest via LLM.
    Returns {digest, citations}."""
    if not results:
        return {"digest": "", "citations": []}
    from llm_client import client, _extract_json, PRIMARY_MODEL

    payload = []
    for res in results[:12]:
        payload.append(f"[{res['title']}] ({res['url']})\n{res['content'][:2500]}")
    prompt = (
        "You are a research analyst. Below are real web search results about the company's market.\n"
        "Synthesize them into a sharp INDUSTRY DIGEST for a founder: current market state, growth, "
        "competitors, pricing, risks, and opportunities. Be specific, cite facts from the results, "
        "never invent numbers. Output STRICT JSON only: "
        '{"digest": "<8-14 sentences, plain text, no markdown>", '
        '"citations": [{"title": "...", "url": "..."}]} (3-6 citations actually used).\n\n'
        f"Company: {(org.get('name') or 'unknown')}\n\nSEARCH RESULTS:\n" + "\n\n".join(payload)
    )
    try:
        r = client().messages.create(model=PRIMARY_MODEL, max_tokens=2500,
                                     system=[{"type": "text", "text":
                                              "Return ONLY valid JSON, no markdown fences."}],
                                     thinking={"type": "disabled"},
                                     messages=[{"role": "user", "content": prompt}])
        txt = next((b.text for b in r.content if getattr(b, "type", "") == "text"), "").strip()
        out = json.loads(_extract_json(txt))
        digest = (out.get("digest") or "").strip()
        cits = out.get("citations") or []
        citations = [{"title": str(c.get("title", ""))[:200], "url": str(c.get("url", ""))[:400]}
                     for c in cits if isinstance(c, dict) and c.get("url")]
        return {"digest": digest, "citations": citations[:8]}
    except Exception as e:
        log.warning(f"digest synthesis failed: {e}")
        lines = [f"- {r['title']}: {r['content'][:200]}" for r in results[:6]]
        return {"digest": " ".join(lines), "citations": [{"title": r["title"], "url": r["url"]} for r in results[:6]]}


def deep_research(org: dict) -> dict:
    """Run the full research pass for an org and store industry_research on it.
    Parallel is the primary search engine (objective-based, LLM-optimized excerpts);
    Tavily is the fallback when Parallel returns nothing. Returns the stored
    {digest, citations, generated_at, queries}."""
    from db import orgs_col
    queries = _org_queries(org)
    objective = (
        f"Research {org.get('name') or 'this company'}'s market: {queries[0] if queries else ''} "
        "Focus on current market state, growth, competitors, pricing, regulations, and opportunities. "
        "Prefer recent and India-relevant sources where applicable."
    )
    all_results = parallel_search(objective, queries)
    engine = "parallel"
    if not all_results:
        log.info("Parallel returned nothing — falling back to Tavily")
        engine = "tavily"
        for q in queries:
            res = tavily_search(q)
            all_results.extend(res)
            time.sleep(0.3)
    # Dedupe by URL
    seen, unique = set(), []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)
    syn = _synthesize_digest(org, unique)
    stored = {
        "digest": syn["digest"],
        "citations": syn["citations"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queries": queries,
        "results_count": len(unique),
        "engine": engine,
    }
    try:
        orgs_col.update_one({"id": org["id"]}, {"$set": {"industry_research": stored}})
    except Exception as e:
        log.warning(f"deep_research store failed: {e}")
    return stored


def is_fresh(org: dict, max_age_days: int = RESEARCH_TTL_DAYS) -> bool:
    """True when the org already has a research digest generated within the TTL."""
    research = org.get("industry_research") or {}
    gen = research.get("generated_at")
    if not (isinstance(research, dict) and (research.get("digest") or "").strip() and gen):
        return False
    try:
        from datetime import datetime, timezone
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(gen)).total_seconds()
        return 0 <= age <= max_age_days * 86400
    except Exception:
        return False