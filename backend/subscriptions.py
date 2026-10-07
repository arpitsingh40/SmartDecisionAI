"""Subscription management via Zoho Payments UPI Autopay mandates.
Plans:
  - Standard: ₹1,999/mo → 10M tokens
  - Pro: ₹4,999/mo → 10M tokens + ultra thinking
Trial: ₹99 for 3 days (UPI mandate setup + first payment authorisation)
Overage: ₹4,999 for additional 10M tokens (one-time payment session)"""
import os
import uuid
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from db import subscriptions_col, token_usage_col, orders_col
from security import current_user, now_utc
from ledger import inc_stats
from payments import (create_mandate_enrollment, execute_mandate_payment,
                      cancel_mandate)
try:
    from zoho_client import zoho_payments_api as _zoho_api
except ImportError:
    from payments import _zoho_api  # fallback

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
log = logging.getLogger("subscriptions")

# Plans: monthly token budget in tokens, price in INR
PLANS = {
    "standard": {
        "id": "standard", "label": "Standard", "price_inr": 1999,
        "tokens_per_month": 10_000_000, "ultra_enabled": False,
        "model": "standard",
        "features": ["10M tokens per month", "Fast reasoning engine",
                      "File attachments", "UPI autopay monthly billing"],
    },
    "pro": {
        "id": "pro", "label": "Pro", "price_inr": 4999,
        "tokens_per_month": 10_000_000, "ultra_enabled": True,
        "model": "pro",
        "features": ["10M tokens per month", "Premium reasoning engine",
                      "Ultra thinking mode (deep analysis)", "Priority access",
                      "File attachments", "UPI autopay monthly billing"],
    },
}

# Trial and overage pricing constants.
TRIAL_PRICE_INR = 99
TRIAL_DAYS = 3
OVERAGE_PRICE_INR = 4999
OVERAGE_TOKENS = 10_000_000


def get_token_budget(user_id: str) -> dict:
    """Return current month's token budget and usage for a user.
    Also checks and resets if the month has rolled over."""
    now = now_utc()
    month_key = now.strftime("%Y-%m")
    sub = subscriptions_col.find_one({"user_id": user_id, "status": {"$in": ["active", "trial"]}})
    if not sub:
        return {"budget": 0, "used": 0, "remaining": 0, "plan": None, "month": month_key,
                "reset_at": None, "status": "no_subscription"}
    usage = token_usage_col.find_one({"user_id": user_id, "month": month_key})
    used = usage.get("tokens", 0) if usage else 0
    budget = sub.get("token_budget", 0)
    plan = PLANS.get(sub.get("plan_id"))
    return {
        "budget": budget,
        "used": used,
        "remaining": max(0, budget - used),
        "plan": sub.get("plan_id"),
        "model": (plan or {}).get("model", "standard"),
        "month": month_key,
        "reset_at": sub.get("current_period_end"),
        "status": sub.get("status", "inactive"),
        "ultra_enabled": sub.get("ultra_enabled", False),
    }


def deduct_tokens(user_id: str, tokens_in: int, tokens_out: int) -> dict:
    """Deduct actual tokens from the user's monthly budget. Returns remaining.
    Raises HTTPException(402) if budget exhausted."""
    budget = get_token_budget(user_id)
    if budget["budget"] <= 0:
        raise HTTPException(402, "No active subscription. Subscribe to continue using the engine.")
    total = (tokens_in or 0) + (tokens_out or 0)
    if total > budget["remaining"]:
        raise HTTPException(402, f"Monthly token limit reached ({budget['used']}/{budget['budget']} used). Top up for ₹{OVERAGE_PRICE_INR} to add {OVERAGE_TOKENS:,} more tokens.")
    month_key = budget["month"]
    token_usage_col.update_one(
        {"user_id": user_id, "month": month_key},
        {"$inc": {"tokens": total}},
        upsert=True,
    )
    remaining = budget["remaining"] - total
    return {"deducted": total, "remaining": remaining, "used": budget["used"] + total, "budget": budget["budget"]}


def add_token_budget(user_id: str, tokens: int, source: str):
    """Add tokens to the current period's budget (overage top-up or subscription grant)."""
    sub = subscriptions_col.find_one({"user_id": user_id, "status": {"$in": ["active", "trial"]}})
    if not sub:
        return None
    now = now_utc()
    month_key = now.strftime("%Y-%m")
    subscriptions_col.update_one(
        {"user_id": user_id, "status": {"$in": ["active", "trial"]}},
        {"$inc": {"token_budget": tokens}},
    )
    log.info(f"added {tokens} tokens to user {user_id} via {source}")
    return True


def reset_monthly_budget(user_id: str):
    """Reset token budget at the start of a new billing period."""
    sub = subscriptions_col.find_one({"user_id": user_id, "status": "active"})
    if not sub:
        return
    plan = PLANS.get(sub.get("plan_id"))
    if not plan:
        return
    now = now_utc()
    period_end = now + timedelta(days=30)
    subscriptions_col.update_one({"user_id": user_id, "status": "active"}, {
        "$set": {
            "token_budget": plan["tokens_per_month"],
            "current_period_start": now,
            "current_period_end": period_end,
            "ultra_enabled": plan.get("ultra_enabled", False),
        }
    })
    log.info(f"monthly budget reset for user {user_id}: {plan['tokens_per_month']} tokens")


# ----------------------------------------------------------------- endpoints

@router.get("/plans")
def list_plans():
    """Public: list available subscription plans."""
    return {"plans": [{"id": k, **v} for k, v in PLANS.items()],
            "trial_price_inr": TRIAL_PRICE_INR, "trial_days": TRIAL_DAYS,
            "overage_price_inr": OVERAGE_PRICE_INR, "overage_tokens": OVERAGE_TOKENS}


# Request body for creating a subscription.
class CreateSubIn(BaseModel):
    plan_id: str


@router.post("/create")
def create_subscription(body: CreateSubIn, request: Request, user: dict = Depends(current_user)):
    """Start full subscription (no trial): creates UPI mandate, charges plan price."""
    plan = PLANS.get(body.plan_id)
    if not plan:
        raise HTTPException(422, "Unknown plan. Choose 'standard' or 'pro'.")
    existing = subscriptions_col.find_one({"user_id": user["id"], "status": {"$in": ["active", "trial"]}})
    if existing:
        raise HTTPException(400, f"You already have an active subscription ({existing.get('plan_id')}).")
    try:
        resp = create_mandate_enrollment(
            customer_email=user.get("email", ""),
            customer_phone=user.get("phone", ""),
            plan_amount=plan["price_inr"],
            description=f"SmartDecigen {plan['label']} - ₹{plan['price_inr']}/mo",
        )
    except Exception as e:
        log.error(f"mandate enrollment failed for user {user['id']}: {e}")
        raise HTTPException(502, "Could not start the payment setup. Try again.")
    enrollment_id = resp.get("mandate_enrollment_id") or resp.get("data", {}).get("mandate_enrollment_id")
    enrollment_url = resp.get("mandate_enrollment_url") or resp.get("data", {}).get("url", "")
    if not enrollment_id:
        raise HTTPException(502, "Unexpected response from payment gateway.")
    now = now_utc()
    period_end = now + timedelta(days=30)
    sub = {
        "id": str(uuid.uuid4()), "user_id": user["id"], "plan_id": body.plan_id,
        "label": plan["label"], "price_inr": plan["price_inr"],
        "status": "pending_mandate",  # waiting for customer to authorise in UPI app
        "mandate_enrollment_id": enrollment_id,
        "mandate_id": None, "token_budget": 0,
        "current_period_start": now, "current_period_end": period_end,
        "ultra_enabled": plan.get("ultra_enabled", False),
        "trial": False, "created_at": now, "updated_at": now,
    }
    subscriptions_col.insert_one(sub)
    front = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")
    return {"subscription": {"id": sub["id"], "plan_id": body.plan_id, "status": "pending_mandate"},
            "mandate_enrollment_url": enrollment_url,
            "info": "Authorise the mandate in your UPI app to activate your subscription."}


@router.post("/trial")
def start_trial(request: Request, user: dict = Depends(current_user)):
    """Start a ₹99 3-day trial: creates UPI mandate with ₹99 initial charge."""
    existing = subscriptions_col.find_one({"user_id": user["id"], "status": {"$in": ["active", "trial"]}})
    if existing:
        raise HTTPException(400, "You already have an active or trial subscription.")
    try:
        resp = create_mandate_enrollment(
            customer_email=user.get("email", ""),
            customer_phone=user.get("phone", ""),
            plan_amount=TRIAL_PRICE_INR,
            description=f"SmartDecigen Trial - ₹{TRIAL_PRICE_INR} for {TRIAL_DAYS} days",
        )
    except Exception as e:
        log.error(f"trial mandate enrollment failed for user {user['id']}: {e}")
        raise HTTPException(502, "Could not start the trial payment setup. Try again.")
    enrollment_id = resp.get("mandate_enrollment_id") or resp.get("data", {}).get("mandate_enrollment_id")
    enrollment_url = resp.get("mandate_enrollment_url") or resp.get("data", {}).get("url", "")
    if not enrollment_id:
        raise HTTPException(502, "Unexpected response from payment gateway.")
    now = now_utc()
    period_end = now + timedelta(days=TRIAL_DAYS)
    sub = {
        "id": str(uuid.uuid4()), "user_id": user["id"], "plan_id": "trial",
        "label": "Trial", "price_inr": TRIAL_PRICE_INR,
        "status": "pending_mandate",
        "mandate_enrollment_id": enrollment_id,
        "mandate_id": None, "token_budget": 1_000_000,  # 1M tokens for trial
        "current_period_start": now, "current_period_end": period_end,
        "ultra_enabled": True, "trial": True,
        "created_at": now, "updated_at": now,
    }
    subscriptions_col.insert_one(sub)
    front = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")
    return {"subscription": {"id": sub["id"], "plan": "trial", "status": "pending_mandate"},
            "mandate_enrollment_url": enrollment_url,
            "info": f"Pay ₹{TRIAL_PRICE_INR} and authorise the mandate to start your {TRIAL_DAYS}-day trial."}


@router.get("/my")
def my_subscription(user: dict = Depends(current_user)):
    """Current user's subscription status + token usage."""
    sub = subscriptions_col.find_one({"user_id": user["id"], "status": {"$in": ["active", "trial", "pending_mandate"]}})
    budget = get_token_budget(user["id"])
    if not sub:
        return {"subscription": None, "token_usage": budget}
    return {
        "subscription": {
            "id": sub["id"], "plan_id": sub.get("plan_id"), "label": sub.get("label"),
            "status": sub.get("status"), "price_inr": sub.get("price_inr"),
            "trial": sub.get("trial", False),
            "current_period_start": sub.get("current_period_start").isoformat() if sub.get("current_period_start") else None,
            "current_period_end": sub.get("current_period_end").isoformat() if sub.get("current_period_end") else None,
            "created_at": sub.get("created_at").isoformat() if sub.get("created_at") else None,
        },
        "token_usage": budget,
    }


@router.post("/cancel")
def cancel_subscription(user: dict = Depends(current_user)):
    """Cancel current subscription at period end."""
    sub = subscriptions_col.find_one({"user_id": user["id"], "status": {"$in": ["active", "trial"]}})
    if not sub:
        raise HTTPException(404, "No active subscription found.")
    mandate_id = sub.get("mandate_id")
    if mandate_id:
        try:
            cancel_mandate(mandate_id, "User cancelled subscription")
        except Exception as e:
            log.warning(f"mandate cancellation failed for {mandate_id}: {e}")
    subscriptions_col.update_one({"id": sub["id"]}, {
        "$set": {"status": "cancelled", "updated_at": now_utc()}})
    return {"ok": True, "status": "cancelled"}


# Request body for token top-ups.
class TopupIn(BaseModel):
    pass


@router.post("/topup")
def topup_tokens(request: Request, user: dict = Depends(current_user)):
    """Buy additional 10M tokens for ₹4,999 (one-time payment)."""
    front = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")
    try:
        now = now_utc()
        order_id = str(uuid.uuid4())
        order = {
            "order_id": order_id, "user_id": user["id"], "user_email": user["email"],
            "pack_id": "topup_10m", "credits": 0, "tokens": OVERAGE_TOKENS,
            "amount_inr": OVERAGE_PRICE_INR, "currency": "INR",
            "status": "created", "test": False,
            "created_at": now, "updated_at": now,
            "status_history": [{"status": "created", "at": now}],
        }
        orders_col.insert_one(order)
        try:
            resp = _zoho_api("POST", "/paymentsessions", {
                "amount": float(OVERAGE_PRICE_INR),
                "currency": "INR",
                "description": "SmartDecigen top-up: 10M additional tokens",
                "reference_number": order_id[:50],
                "meta_data": [{"key": "order_id", "value": order_id}],
                "configurations": {
                    "hosted_page_parameters": {
                        "description": "10M additional tokens",
                        "success_url": f"{front}/pay/result?order_id={order_id}",
                        "failure_url": f"{front}/pay/result?order_id={order_id}",
                    }
                },
            })
        except Exception as e:
            log.error(f"zoho session for topup failed: {e}")
            raise HTTPException(502, "Could not start the payment.")
        data = resp.get("payments_session") or resp.get("data") or resp
        session_id = data.get("payments_session_id") or data.get("payment_session_id")
        access_key = data.get("access_key")
        if not session_id or not access_key:
            raise RuntimeError(f"unexpected Zoho response: {resp}")
        orders_col.update_one({"order_id": order_id},
                              {"$set": {"zoho_session_id": session_id, "updated_at": now_utc()}})
        host = os.environ.get("ZOHO_API_BASE", "https://payments.zoho.in/api/v1").split("/api/")[0]
        return {"order_id": order_id, "checkout_url": f"{host}/hostedcheckout/{access_key}",
                "tokens": OVERAGE_TOKENS, "amount_inr": OVERAGE_PRICE_INR}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"topup failed: {e}")
        raise HTTPException(502, "Could not process the top-up.")


@router.post("/webhook")
async def subscription_webhook(request: Request):
    """Handle Zoho Payments mandate webhook events + topup payment_success.
    Events: mandate.enrollment_completed, mandate.payment_success, mandate.cancelled, payment.success"""
    raw = await request.body()
    # Verify webhook signature when configured (reuse payments._verify_webhook_signature)
    try:
        secret = os.environ.get("ZOHO_WEBHOOK_SECRET", "").strip()
        if secret:
            from payments import _verify_webhook_signature as _verify_sig
            header = request.headers.get("x-zoho-webhook-signature", request.headers.get("x-webhook-signature", ""))
            if header and not _verify_sig(raw, header, secret):
                log.warning("subscription webhook: invalid signature")
                return {"received": True}
    except Exception:
        pass
    try:
        import json
        payload = json.loads(raw.decode() or "{}")
    except Exception:
        return {"received": True}
    event = (payload.get("event") or payload.get("event_type") or "").lower()
    data = payload.get("data") or payload
    log.info(f"subscription webhook: event={event}")
    # mandate.enrollment_completed → mandate was authorised by customer
    if "enrollment_completed" in event or "mandate_authorized" in event:
        mandate_id = data.get("mandate_id") or data.get("id")
        enrollment_id = data.get("mandate_enrollment_id") or data.get("enrollment_id")
        if not mandate_id:
            return {"received": True}
        sub = subscriptions_col.find_one({"mandate_enrollment_id": enrollment_id})
        if not sub:
            sub = subscriptions_col.find_one({"mandate_enrollment_id": enrollment_id})
        if sub:
            plan = PLANS.get(sub.get("plan_id"))
            is_trial = sub.get("trial", False)
            budget = (plan["tokens_per_month"] if plan else 10_000_000) if not is_trial else 1_000_000
            subscriptions_col.update_one({"id": sub["id"]}, {
                "$set": {
                    "mandate_id": mandate_id, "status": "active" if not is_trial else "trial",
                    "token_budget": budget, "updated_at": now_utc(),
                }
            })
            log.info(f"subscription {sub['id']} activated with mandate {mandate_id}, budget={budget}")
            inc_stats({"subs_active": 1} if not is_trial else {"subs_trial": 1})
            if is_trial:
                plan = PLANS.get(sub.get("plan_id"))
                mrr = plan["price_inr"] if plan else 1999
                inc_stats({"mrr_inr": mrr})
                orders_col.insert_one({
                    "order_id": str(uuid.uuid4()), "user_id": sub["user_id"],
                    "pack_id": "trial", "tokens": budget,
                    "amount_inr": TRIAL_PRICE_INR, "status": "paid",
                    "created_at": now_utc(), "updated_at": now_utc(),
                })
                inc_stats({"revenue_inr": TRIAL_PRICE_INR, "subs_revenue_inr": TRIAL_PRICE_INR, "purchases_count": 1})
    # mandate.payment_success → recurring payment collected (also handles topup-like amount)
    elif "payment_success" in event or "payment.completed" in event:
        mandate_id = data.get("mandate_id") or data.get("id")
        amount = data.get("amount") or data.get("amount_inr") or 0
        if mandate_id:
            sub = subscriptions_col.find_one({"mandate_id": mandate_id, "status": "active"})
            if sub:
                now = now_utc()
                period_end = now + timedelta(days=30)
                plan = PLANS.get(sub.get("plan_id"))
                budget = plan["tokens_per_month"] if plan else 10_000_000
                subscriptions_col.update_one({"id": sub["id"]}, {
                    "$set": {
                        "current_period_start": now, "current_period_end": period_end,
                        "token_budget": budget, "updated_at": now,
                    }
                })
                plan = PLANS.get(sub.get("plan_id"))
                mrr = plan["price_inr"] if plan else int(amount)
                inc_stats({"revenue_inr": int(amount), "subs_revenue_inr": int(amount),
                           "purchases_count": 1, "mrr_inr": mrr})
                log.info(f"recurring payment collected for sub {sub['id']}: ₹{amount}")
            else:
                # May be a one-time payment piggybacking on mandate payload (topup) — fall through
                pass
        # Also treat as possible topup fulfilment (session-based one-time pay)
        if True:
            order_ref = str(data.get("reference_number") or data.get("order_id") or data.get("reference") or "")
            if order_ref:
                order = orders_col.find_one({"order_id": order_ref})
                if order and order.get("pack_id") == "topup_10m" and order.get("status") != "paid":
                    try:
                        from payments import fulfil_order
                        fulfil_order(order["order_id"], "subscription_webhook_topup")
                    except Exception as e:
                        log.warning(f"topup fulfil failed: {e}")
            sess = data.get("payments_session_id") or data.get("payment_session_id") or data.get("session_id")
            if sess:
                order = orders_col.find_one({"zoho_session_id": sess})
                if order and order.get("pack_id") == "topup_10m" and order.get("status") != "paid":
                    try:
                        from payments import fulfil_order
                        fulfil_order(order["order_id"], "subscription_webhook_topup2")
                    except Exception as e:
                        log.warning(f"topup fulfil (session) failed: {e}")
            if mandate_id and amount:
                return {"received": True}
    elif "cancelled" in event or "revoked" in event:
        mandate_id = data.get("mandate_id") or data.get("id")
        if mandate_id:
            subscriptions_col.update_one({"mandate_id": mandate_id},
                                          {"$set": {"status": "cancelled", "updated_at": now_utc()}})
            # Decrement MRR on cancel (best-effort)
            try:
                sub = subscriptions_col.find_one({"mandate_id": mandate_id})
                if sub and sub.get("price_inr"):
                    inc_stats({"mrr_inr": -int(sub["price_inr"]), "subs_active": -1})
            except Exception:
                pass
    # payment.success for one-time topup (pack topup_10m) — fulfil via orders_col
    elif "payment" in event and data:
        order_ref = str(data.get("reference_number") or data.get("order_id") or data.get("reference") or "")
        # Try to match topup/credit orders by session/payment linkage
        if order_ref:
            order = orders_col.find_one({"order_id": order_ref})
            if order and order.get("pack_id") == "topup_10m" and order.get("status") != "paid":
                try:
                    from payments import fulfil_order
                    fulfil_order(order["order_id"], "subscription_webhook_topup")
                except Exception as e:
                    log.warning(f"topup webhook fulfil failed: {e}")
        # Also handle by session_id if present in payload
        sess = data.get("payments_session_id") or data.get("payment_session_id") or data.get("session_id")
        if sess:
            order = orders_col.find_one({"zoho_session_id": sess})
            if order and order.get("pack_id") == "topup_10m" and order.get("status") != "paid":
                try:
                    from payments import fulfil_order
                    fulfil_order(order["order_id"], "subscription_webhook_topup")
                except Exception as e:
                    log.warning(f"topup webhook fulfil (session) failed: {e}")
    return {"received": True}


# ----------------------------------------------------------------- scheduled job helpers

def process_pending_trial_conversions():
    """Daily job: find expired trials, charge via mandate; on success convert to active."""
    now = now_utc()
    expired = list(subscriptions_col.find({
        "status": "trial", "current_period_end": {"$lt": now},
    }))
    for sub in expired:
        mandate_id = sub.get("mandate_id")
        if not mandate_id:
            subscriptions_col.update_one({"id": sub["id"]}, {"$set": {"status": "expired", "updated_at": now}})
            log.info(f"trial {sub['id']} expired (no mandate)")
            continue
        # Determine target plan: prefer explicit plan_id if not 'trial', else default to standard
        plan_id = sub.get("plan_id") if sub.get("plan_id") != "trial" else "standard"
        plan = PLANS.get(plan_id) or PLANS["standard"]
        try:
            resp = execute_mandate_payment(mandate_id, plan["price_inr"],
                                           f"SmartDecigen {plan['label']} — trial conversion")
            log.info(f"trial {sub['id']} conversion charged ₹{plan['price_inr']}: {resp}")
            # Success → convert to active (webhook will also confirm; idempotent)
            subscriptions_col.update_one({"id": sub["id"]}, {"$set": {
                "plan_id": plan_id, "label": plan["label"], "price_inr": plan["price_inr"],
                "status": "active", "trial": False,
                "token_budget": plan["tokens_per_month"],
                "ultra_enabled": plan.get("ultra_enabled", False),
                "current_period_start": now,
                "current_period_end": now + timedelta(days=30),
                "updated_at": now,
            }})
            orders_col.insert_one({
                "order_id": str(uuid.uuid4()), "user_id": sub["user_id"],
                "pack_id": f"trial_conversion_{plan_id}", "tokens": plan["tokens_per_month"],
                "amount_inr": plan["price_inr"], "status": "paid",
                "created_at": now, "updated_at": now,
            })
            inc_stats({"revenue_inr": plan["price_inr"], "subs_revenue_inr": plan["price_inr"],
                        "purchases_count": 1, "subs_active": 1, "mrr_inr": plan["price_inr"]})
        except Exception as e:
            log.warning(f"trial {sub['id']} conversion charge failed: {e} — marking expired")
            subscriptions_col.update_one({"id": sub["id"]}, {"$set": {"status": "expired", "updated_at": now}})


def process_mandate_executions():
    """Daily job: execute mandate payments for subscriptions due for renewal."""
    now = now_utc()
    due = list(subscriptions_col.find({
        "status": "active", "current_period_end": {"$lte": now + timedelta(hours=24)},
        "mandate_id": {"$ne": None, "$exists": True},
    }))
    for sub in due:
        if sub.get("trial"):
            continue
        try:
            resp = execute_mandate_payment(
                sub["mandate_id"], sub["price_inr"],
                f"SmartDecigen {sub.get('label', '')} - monthly renewal",
            )
            log.info(f"mandate execution triggered for {sub['id']}: {resp}")
        except Exception as e:
            log.error(f"mandate execution failed for {sub['id']}: {e}")


def ensure_subscriptions_startup():
    """Idempotent: indexes for subscriptions."""
    subscriptions_col.create_index("id", unique=True)
    subscriptions_col.create_index("user_id", unique=True, partialFilterExpression={"status": {"$in": ["active", "trial"]}})
    subscriptions_col.create_index("mandate_id", sparse=True)
    subscriptions_col.create_index([("status", 1), ("current_period_end", 1)])
    token_usage_col.create_index([("user_id", 1), ("month", 1)], unique=True)