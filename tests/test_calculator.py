import pytest

from src import config
from src.calculator import quote_recipient_first


def quote(amount, rate=88.0):
    return quote_recipient_first(
        recipient_inr=amount,
        mid_rate=rate,
        fx_markup=config.FX_MARKUP,
        pct_fee=config.PCT_FEE,
        fixed_fee_usd=config.FIXED_FEE_USD,
    )


@pytest.mark.parametrize("amount", [1000, 25000, 50000, 123456, 10000000])
@pytest.mark.parametrize("rate", [83.5, 88.0, 91.25])
def test_recipient_gets_requested_amount(amount, rate):
    assert abs(quote(amount, rate)["recipient_inr"] - amount) <= 1


def test_losses_add_up():
    r = quote(50000)
    assert abs(r["total_loss_inr"] - (r["fee_loss_inr"] + r["fx_loss_inr"])) <= 1
    assert abs(r["fee_share_pct"] + r["fx_share_pct"] - 100) <= 0.11


def test_send_exceeds_recipient_value():
    r = quote(50000)
    assert r["send_usd"] * r["mid_rate"] > 50000


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(recipient_inr=0, mid_rate=88, fx_markup=0.03, pct_fee=0.04, fixed_fee_usd=0.5),
        dict(recipient_inr=1000, mid_rate=0, fx_markup=0.03, pct_fee=0.04, fixed_fee_usd=0.5),
        dict(recipient_inr=1000, mid_rate=88, fx_markup=1, pct_fee=0.04, fixed_fee_usd=0.5),
        dict(recipient_inr=1000, mid_rate=88, fx_markup=0.03, pct_fee=1, fixed_fee_usd=0.5),
        dict(recipient_inr=1000, mid_rate=88, fx_markup=0.03, pct_fee=0.04, fixed_fee_usd=-1),
    ],
)
def test_invalid_inputs_rejected(kwargs):
    with pytest.raises(ValueError):
        quote_recipient_first(**kwargs)
