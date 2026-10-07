"""Zoho handler — native Books + Invoice ops without Composio.

All money is Zoho. No Stripe.

Reads ZOHO_* from env via zoho_client (single OAuth). Honest when not configured.
"""
import os
import time
import logging

from . import register

log = logging.getLogger("execution.handlers.zoho")

TOOLS = [
    {"name": "ZOHO_LIST_INVOICES", "description": "List Zoho Books invoices (open/overdue)", "inputSchema": {"status": "string", "limit": "integer"}},
    {"name": "ZOHO_CREATE_INVOICE", "description": "Create a Zoho Books invoice for a contact", "inputSchema": {"customer_name": "string", "customer_email": "string", "items": "array", "due_days": "integer"}},
    {"name": "ZOHO_LIST_CONTACTS", "description": "List Zoho Books contacts/customers", "inputSchema": {"limit": "integer"}},
    {"name": "ZOHO_GET_INVOICE", "description": "Fetch one Zoho invoice by id", "inputSchema": {"invoice_id": "string"}},
]


def _fmt_invoices(invoices):
    lines = []
    for inv in (invoices or [])[:20]:
        num = inv.get("invoice_number") or inv.get("invoice_id", "?")
        status = inv.get("status", "")
        total = inv.get("total") or inv.get("total_formatted") or ""
        cust = (inv.get("customer_name") or inv.get("customer_id") or "")[:30]
        due = inv.get("due_date") or ""
        lines.append(f"- {num}: {total} [{status}] {cust} due:{due}")
    return "\n".join(lines) if lines else "No invoices"


def _ensure_contact(name: str, email: str) -> str:
    """Find or create contact, return contact_id."""
    from zoho_client import zoho_books_api
    name = (name or (email.split("@")[0] if email else "Customer")).strip()[:80] or "Customer"
    # Search by email/name
    try:
        if email:
            res = zoho_books_api("GET", "/contacts", params={"email": email})
            contacts = res.get("contacts") or []
            for c in contacts:
                if (c.get("email") or "").lower() == email.lower():
                    return c.get("contact_id")
    except Exception:
        pass
    # Create
    payload = {"contact_name": name}
    if email:
        payload["email"] = email
    res = zoho_books_api("POST", "/contacts", json_body=payload)
    contact = res.get("contact") or res.get("data") or {}
    return contact.get("contact_id") or contact.get("contactId") or ""


@register("ZOHO")
def handle(tool_name: str, args: dict) -> dict:
    # Honest gate
    try:
        from zoho_client import zoho_configured
        if not zoho_configured():
            return {"error": "Zoho not configured — set ZOHO_CLIENT_ID/SECRET/REFRESH_TOKEN (+ ZOHO_BOOKS_ORG_ID for Books)", "successful": False}
    except Exception:
        pass
    t0 = time.time()

    try:
        from zoho_client import zoho_books_api

        if tool_name == "ZOHO_LIST_INVOICES":
            status = (args.get("status") or "").strip().lower()
            params = {}
            if status:
                params["status"] = status
            # paginate a bit
            res = zoho_books_api("GET", "/invoices", params=params)
            invoices = res.get("invoices") or res.get("data") or []
            text = _fmt_invoices(invoices)
            # expose structured too for automation_loops
            return {"result": text, "successful": True, "data": invoices, "execution_time_ms": round((time.time() - t0) * 1000)}

        if tool_name == "ZOHO_LIST_CONTACTS":
            res = zoho_books_api("GET", "/contacts")
            contacts = res.get("contacts") or []
            lines = [f"- {c.get('contact_name','?')} <{c.get('email','')}> ({c.get('contact_id','')})" for c in contacts[:15]]
            return {"result": "\n".join(lines) if lines else "No contacts", "successful": True, "data": contacts, "execution_time_ms": round((time.time() - t0) * 1000)}

        if tool_name == "ZOHO_GET_INVOICE":
            inv_id = (args.get("invoice_id") or "").strip()
            if not inv_id:
                return {"error": "invoice_id required", "successful": False, "execution_time_ms": round((time.time() - t0) * 1000)}
            res = zoho_books_api("GET", f"/invoices/{inv_id}")
            inv = res.get("invoice") or res
            return {"result": str(inv)[:2000], "successful": True, "data": inv, "execution_time_ms": round((time.time() - t0) * 1000)}

        if tool_name == "ZOHO_CREATE_INVOICE":
            customer_name = (args.get("customer_name") or "").strip()
            customer_email = (args.get("customer_email") or "").strip()
            items = args.get("items") or []
            # Normalize items: [{name, quantity, rate}] -> Zoho line_items
            line_items = []
            for it in items[:10]:
                if isinstance(it, dict):
                    line_items.append({
                        "name": it.get("name") or it.get("description") or "Item",
                        "quantity": int(it.get("quantity") or 1),
                        "rate": float(it.get("rate") or it.get("amount") or 0),
                    })
                elif isinstance(it, str):
                    line_items.append({"name": it[:80], "quantity": 1, "rate": 0})
            if not line_items:
                # Default single line so Zoho validates
                line_items = [{"name": "Services", "quantity": 1, "rate": float(args.get("amount") or args.get("rate") or 0) or 1000}]

            contact_id = _ensure_contact(customer_name, customer_email)
            if not contact_id:
                return {"error": "Could not resolve/create Zoho contact", "successful": False, "execution_time_ms": round((time.time() - t0) * 1000)}

            payload = {
                "customer_id": contact_id,
                "line_items": line_items,
            }
            due_days = int(args.get("due_days") or 15)
            if due_days:
                from datetime import datetime, timedelta, timezone
                due = (datetime.now(timezone.utc) + timedelta(days=due_days)).date().isoformat()
                payload["due_date"] = due

            res = zoho_books_api("POST", "/invoices", json_body=payload)
            inv = res.get("invoice") or res
            inv_id = inv.get("invoice_id") or inv.get("invoiceId") or ""
            inv_num = inv.get("invoice_number") or inv_id
            return {"result": f"Invoice {inv_num} created ({inv_id})", "successful": True, "data": inv, "execution_time_ms": round((time.time() - t0) * 1000)}

        return {"error": f"Unsupported Zoho tool: {tool_name}", "successful": False, "execution_time_ms": round((time.time() - t0) * 1000)}

    except Exception as e:
        msg = str(e)[:400]
        return {"error": msg, "successful": False, "execution_time_ms": round((time.time() - t0) * 1000)}


handle.tool_list = TOOLS
