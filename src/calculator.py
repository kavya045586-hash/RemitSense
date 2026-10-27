def quote_recipient_first(
    recipient_inr,
    mid_rate,
    fx_markup,
    pct_fee,
    fixed_fee_usd
):
    """USD that must be sent so the recipient receives recipient_inr.

    Every number shown in the app and given to the AI comes from here.
    """
    if recipient_inr <= 0:
        raise ValueError("recipient_inr must be positive")
    if mid_rate <= 0:
        raise ValueError("mid_rate must be positive")
    if not 0 <= fx_markup < 1:
        raise ValueError("fx_markup must be in [0, 1)")
    if not 0 <= pct_fee < 1:
        raise ValueError("pct_fee must be in [0, 1)")
    if fixed_fee_usd < 0:
        raise ValueError("fixed_fee_usd cannot be negative")

    effective_rate = mid_rate * (1 - fx_markup)

    net_usd_needed = recipient_inr / effective_rate

    send_usd = (net_usd_needed + fixed_fee_usd) / (1 - pct_fee)

    fee_usd = send_usd * pct_fee + fixed_fee_usd

    net_usd = send_usd - fee_usd

    fee_loss_inr = fee_usd * mid_rate

    fx_loss_usd = net_usd * fx_markup
    fx_loss_inr = net_usd * mid_rate * fx_markup

    total_loss_usd = fee_usd + fx_loss_usd
    total_loss_inr = fee_loss_inr + fx_loss_inr

    return {
        "send_usd": round(send_usd, 2),
        "fee_usd": round(fee_usd, 2),
        "fee_loss_inr": round(fee_loss_inr),
        "fx_loss_usd": round(fx_loss_usd, 2),
        "fx_loss_inr": round(fx_loss_inr),
        "total_loss_usd": round(total_loss_usd, 2),
        "total_loss_inr": round(total_loss_inr),
        "fee_share_pct": round(100 * fee_loss_inr / total_loss_inr, 1),
        "fx_share_pct": round(100 * fx_loss_inr / total_loss_inr, 1),
        "mid_rate": round(mid_rate, 4),
        "effective_rate": round(effective_rate, 4),
        "pct_fee_percent": round(pct_fee * 100, 2),
        "fx_markup_percent": round(fx_markup * 100, 2),
        "fixed_fee_usd": round(fixed_fee_usd, 2),
        "recipient_inr": round(net_usd * effective_rate)
    }
