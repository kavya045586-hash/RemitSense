import os
import time
import uuid

import requests
from dotenv import load_dotenv

from src import config

load_dotenv()

BASE_URL = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com")

_token_cache = {"token": None, "expires_at": 0.0}


class PayPalError(Exception):
    pass


def _check(response):
    """Raise PayPalError with PayPal's own message if the call failed."""
    if response.ok:
        return response

    try:
        body = response.json()
    except ValueError:
        body = {}

    issues = ", ".join(
        d.get("issue", "") for d in body.get("details", []) if d.get("issue")
    )
    message = body.get("message") or response.text[:200]
    debug_id = body.get("debug_id", "n/a")

    raise PayPalError(
        f"HTTP {response.status_code} {body.get('name', '')} {issues} - "
        f"{message} (debug_id: {debug_id})".replace("  ", " ")
    )


def get_access_token():
    if _token_cache["token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["token"]

    client_id = os.getenv("PAYPAL_CLIENT_ID")
    secret = os.getenv("PAYPAL_SECRET")

    if not client_id or not secret:
        raise PayPalError(
            "PAYPAL_CLIENT_ID / PAYPAL_SECRET are not set in the environment"
        )

    response = requests.post(
        f"{BASE_URL}/v1/oauth2/token",
        auth=(client_id, secret),
        data={"grant_type": "client_credentials"},
        timeout=30
    )

    _check(response)
    data = response.json()

    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 300) - 60

    return _token_cache["token"]


def create_order(amount, description="RemitSense AI transfer"):
    """Create a CAPTURE order that sends the buyer back to this app."""
    token = get_access_token()

    response = requests.post(
        f"{BASE_URL}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "PayPal-Request-Id": str(uuid.uuid4())
        },
        json={
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "description": description[:127],
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{amount:.2f}"
                    }
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "brand_name": "RemitSense AI",
                        "shipping_preference": "NO_SHIPPING",
                        "user_action": "PAY_NOW",
                        "return_url": f"{config.APP_BASE_URL}/?paypal=return",
                        "cancel_url": f"{config.APP_BASE_URL}/?paypal=cancel"
                    }
                }
            }
        },
        timeout=30
    )

    _check(response)

    return response.json()


def get_order(order_id):
    token = get_access_token()

    response = requests.get(
        f"{BASE_URL}/v2/checkout/orders/{order_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    _check(response)

    return response.json()


def capture_order(order_id):
    token = get_access_token()

    response = requests.post(
        f"{BASE_URL}/v2/checkout/orders/{order_id}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "PayPal-Request-Id": f"capture-{order_id}"
        },
        timeout=30
    )

    _check(response)

    return response.json()


def get_approval_url(order):
    # With payment_source.paypal the link rel is "payer-action";
    # the older flow uses "approve". Accept both.
    for link in order.get("links", []):
        if link.get("rel") in ("payer-action", "approve"):
            return link["href"]

    return None


def summarize_order(order, description=None):
    unit = (order.get("purchase_units") or [{}])[0]
    captures = (unit.get("payments") or {}).get("captures") or []
    capture = captures[0] if captures else {}
    amount = capture.get("amount") or unit.get("amount") or {}

    return {
        "order_id": order.get("id"),
        "order_status": order.get("status"),
        "capture_id": capture.get("id"),
        "capture_status": capture.get("status"),
        "amount": amount.get("value"),
        "currency": amount.get("currency_code"),
        "description": description or unit.get("description"),
    }


def finalize_order(order_id):
    """Called when the buyer returns from PayPal.

    Safe to call more than once: an already-completed order is not
    captured again.
    """
    order = get_order(order_id)
    status = order.get("status")
    description = (order.get("purchase_units") or [{}])[0].get("description")

    if status == "APPROVED":
        order = capture_order(order_id)
    elif status != "COMPLETED":
        raise PayPalError(
            f"Order {order_id} is not approved yet (status: {status})."
        )

    return summarize_order(order, description)
