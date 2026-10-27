from unittest.mock import MagicMock, patch

import pytest

from src import paypal_service as pp


def test_approval_url_payer_action():
    order = {"links": [{"rel": "self", "href": "x"}, {"rel": "payer-action", "href": "https://pp/approve"}]}
    assert pp.get_approval_url(order) == "https://pp/approve"


def test_approval_url_legacy_approve():
    assert pp.get_approval_url({"links": [{"rel": "approve", "href": "u"}]}) == "u"


def test_approval_url_missing():
    assert pp.get_approval_url({"links": []}) is None


def completed(order_id="O1"):
    return {
        "id": order_id,
        "status": "COMPLETED",
        "purchase_units": [{
            "description": "test",
            "payments": {"captures": [{"id": "C1", "status": "COMPLETED",
                                       "amount": {"value": "10.00", "currency_code": "USD"}}]},
        }],
    }


def test_finalize_captures_when_approved():
    with patch.object(pp, "get_order", return_value={"id": "O1", "status": "APPROVED",
                                                     "purchase_units": [{"description": "test"}]}), \
         patch.object(pp, "capture_order", return_value=completed()) as cap:
        out = pp.finalize_order("O1")
    cap.assert_called_once_with("O1")
    assert out["capture_id"] == "C1" and out["description"] == "test"


def test_finalize_does_not_recapture_completed():
    with patch.object(pp, "get_order", return_value=completed()), \
         patch.object(pp, "capture_order") as cap:
        out = pp.finalize_order("O1")
    cap.assert_not_called()
    assert out["capture_status"] == "COMPLETED"


def test_finalize_rejects_unapproved():
    with patch.object(pp, "get_order", return_value={"id": "O1", "status": "CREATED"}):
        with pytest.raises(pp.PayPalError):
            pp.finalize_order("O1")


def test_create_order_sends_return_urls():
    resp = MagicMock(ok=True)
    resp.json.return_value = {"id": "O1", "links": []}
    with patch.object(pp, "get_access_token", return_value="t"), \
         patch.object(pp.requests, "post", return_value=resp) as post:
        pp.create_order(12.34)
    ctx = post.call_args.kwargs["json"]["payment_source"]["paypal"]["experience_context"]
    assert ctx["return_url"].endswith("?paypal=return")
    assert ctx["cancel_url"].endswith("?paypal=cancel")
    assert post.call_args.kwargs["json"]["purchase_units"][0]["amount"]["value"] == "12.34"
