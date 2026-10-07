"""Zoho unified client — Payments + Books/Invoice share one OAuth token.

Payments: https://payments.zoho.in/api/v1 + ZOHO_ACCOUNT_ID
Books/Invoice: https://www.zohoapis.in/books/v3 or /invoice/v3 + organization_id
Auth: https://accounts.zoho.in/oauth/v2/token (same refresh flow)

Env:
  ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN (required for live)
  ZOHO_ACCOUNT_ID               — Payments account id (payments only)
  ZOHO_API_BASE                 — Payments base (default https://payments.zoho.in/api/v1)
  ZOHO_OAUTH_BASE               — OAuth base (default https://accounts.zoho.in/oauth/v2/token)
  ZOHO_BOOKS_ORG_ID             — Books org id (invoices, contacts, etc); auto-discovered if blank
  ZOHO_INVOICE_ORG_ID           — alias for above (Invoice product)
  ZOHO_BOOKS_API_BASE           — Books base (default https://www.zohoapis.in/books/v3)
  ZOHO_WEBHOOK_SECRET           — webhook HMAC key (payments)
"""
import os
import time
import logging
import requests as http

log = logging.getLogger("zoho_client")

_token_cache = {"token": None, "exp": 0.0}
_books_org_cache = {"id": None, "ts": 0.0}


def zoho_configured() -> bool:
    """True when live Zoho Payments creds are present."""
    return all(os.environ.get(k, "").strip() for k in ("ZOHO_CLIENT_ID", "ZOHO_CLIENT_SECRET", "ZOHO_REFRESH_TOKEN"))


def zoho_books_configured() -> bool:
    """True when Books/Invoice can be called (needs token + org)."""
    return zoho_configured()


def zoho_access_token() -> str:
    if _token_cache["token"] and time.time() < _token_cache["exp"] - 120:
        return _token_cache["token"]
    r = http.post(os.environ.get("ZOHO_OAUTH_BASE", "https://accounts.zoho.in/oauth/v2/token"), data={
        "refresh_token": os.environ["ZOHO_REFRESH_TOKEN"],
        "client_id": os.environ["ZOHO_CLIENT_ID"],
        "client_secret": os.environ["ZOHO_CLIENT_SECRET"],
        "grant_type": "refresh_token",
    }, timeout=15)
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"Zoho OAuth refresh failed: {data}")
    _token_cache["token"] = data["access_token"]
    _token_cache["exp"] = time.time() + int(data.get("expires_in", 3600))
    return _token_cache["token"]


# ----------------------------------------------------------------- Payments (existing)

def zoho_payments_api(method: str, path: str, payload=None) -> dict:
    """Zoho Payments — requires ZOHO_ACCOUNT_ID."""
    base = os.environ.get("ZOHO_API_BASE", "https://payments.zoho.in/api/v1")
    account_id = os.environ.get("ZOHO_ACCOUNT_ID", "").strip()
    if not account_id:
        raise RuntimeError("ZOHO_ACCOUNT_ID not set — required for Payments API")
    token = zoho_access_token()
    headers = {"Authorization": f"Zoho-oauthtoken {token}", "content-type": "application/json"}
    r = http.request(method, f"{base}{path}", params={"account_id": account_id}, json=payload, headers=headers, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"Zoho Payments {path} -> {r.status_code}: {r.text[:400]}")
    return r.json()


# ----------------------------------------------------------------- Books / Invoice

def _books_base() -> str:
    return os.environ.get("ZOHO_BOOKS_API_BASE", "https://www.zohoapis.in/books/v3").rstrip("/")


def _books_org_id() -> str:
    """Resolve Books org id: env first, then auto-discover via /organizations."""
    env_id = (os.environ.get("ZOHO_BOOKS_ORG_ID") or os.environ.get("ZOHO_INVOICE_ORG_ID") or "").strip()
    if env_id:
        return env_id
    # cached discovery (10 min)
    if _books_org_cache["id"] and time.time() - _books_org_cache["ts"] < 600:
        return _books_org_cache["id"]
    try:
        token = zoho_access_token()
        base = _books_base()
        # Zoho Books organizations endpoint lives at same base, not api/v1
        r = http.get(f"{base}/organizations", headers={"Authorization": f"Zoho-oauthtoken {token}"}, timeout=15)
        if r.status_code == 200:
            orgs = (r.json().get("organizations") or [])
            if orgs:
                oid = str(orgs[0].get("organization_id") or orgs[0].get("organizationId") or "")
                if oid:
                    _books_org_cache["id"] = oid
                    _books_org_cache["ts"] = time.time()
                    log.info(f"Zoho Books org auto-discovered: {oid}")
                    return oid
    except Exception as e:
        log.warning(f"Zoho Books org discovery failed: {e}")
    return ""


def zoho_books_api(method: str, path: str, params=None, json_body=None) -> dict:
    """Zoho Books/Invoice — injects organization_id automatically."""
    token = zoho_access_token()
    base = _books_base()
    org_id = _books_org_id()
    if not org_id:
        raise RuntimeError("Zoho Books organization_id not resolved — set ZOHO_BOOKS_ORG_ID or grant ZohoBooks/Invoice scope and retry")
    q = dict(params or {})
    q["organization_id"] = org_id
    headers = {"Authorization": f"Zoho-oauthtoken {token}", "content-type": "application/json"}
    url = f"{base}{path}"
    r = http.request(method, url, params=q, json=json_body, headers=headers, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Zoho Books {path} -> {r.status_code}: {r.text[:600]}")
    return r.json()
