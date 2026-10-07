"""Frankfurter handler — keyless foreign-exchange rates.

Free for commercial use, no API key, no quotas (fair-use rate limit).
Source: 104 central banks and official sources, 208 currencies.
Picked from the public-apis / free-for-dev catalogs — see memory/free_tool_providers.md.
"""

import time
import logging
import httpx

from . import register

log = logging.getLogger("execution.handlers.frankfurter")

BASE = "https://api.frankfurter.app"

# Frankfurter tool definitions
TOOLS = [
    {"name": "FRANKFURTER_RATE", "description": "Get the exchange rate for one currency pair (e.g. USD to INR), optionally convert an amount", "inputSchema": {"base": "string", "quote": "string", "amount": "number"}},
    {"name": "FRANKFURTER_RATES", "description": "Get the latest exchange rates for a base currency, optionally filtered to a few quotes", "inputSchema": {"base": "string", "quotes": "string"}},
]


# Execute a Frankfurter tool call
@register("FRANKFURTER")
def handle(tool_name: str, args: dict) -> dict:
    t0 = time.time()
    try:
        if tool_name == "FRANKFURTER_RATE":
            base = (args.get("base") or args.get("from") or "").strip().upper()
            quote = (args.get("quote") or args.get("to") or "").strip().upper()
            if not base or not quote:
                return {"error": "Missing base or quote currency", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            r = httpx.get(f"{BASE}/latest", params={"from": base, "to": quote}, timeout=20)
            if r.status_code != 200:
                return {"error": f"Frankfurter API {r.status_code}: {r.text[:200]}", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            data = r.json()
            rate = (data.get("rates") or {}).get(quote)
            if not isinstance(rate, (int, float)):
                return {"error": f"No rate for {base}->{quote}", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            text = f"1 {base} = {rate} {quote} (as of {data.get('date', 'latest')})"
            amount = args.get("amount")
            if amount not in (None, "", 1, "1"):
                try:
                    amount_f = float(amount)
                    shown = int(amount_f) if amount_f == int(amount_f) else amount_f
                    text += f" · {shown} {base} = {round(amount_f * rate, 2)} {quote}"
                except (TypeError, ValueError):
                    pass
            return {"result": text, "successful": True,
                    "execution_time_ms": round((time.time() - t0) * 1000)}

        if tool_name == "FRANKFURTER_RATES":
            params = {}
            base = (args.get("base") or "").strip().upper()
            quotes = (args.get("quotes") or args.get("to") or "").strip().upper()
            if base:
                params["from"] = base
            if quotes:
                params["to"] = quotes
            r = httpx.get(f"{BASE}/latest", params=params, timeout=20)
            if r.status_code != 200:
                return {"error": f"Frankfurter API {r.status_code}: {r.text[:200]}", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            data = r.json()
            rates = data.get("rates") or {}
            if not rates:
                return {"error": "No rates returned", "successful": False,
                        "execution_time_ms": round((time.time() - t0) * 1000)}
            lines = [f"1 {data.get('base', base or 'EUR')} = {v} {k}" for k, v in sorted(rates.items())[:15]]
            return {"result": f"Latest rates (as of {data.get('date', 'latest')}):\n" + "\n".join(lines),
                    "successful": True, "execution_time_ms": round((time.time() - t0) * 1000)}

        return {"error": f"Unsupported Frankfurter tool: {tool_name}", "successful": False,
                "execution_time_ms": round((time.time() - t0) * 1000)}
    except httpx.RequestError as e:
        return {"error": str(e)[:300], "successful": False, "execution_time_ms": round((time.time() - t0) * 1000)}


handle.tool_list = TOOLS
