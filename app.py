import html as _html
import re

import streamlit as st

from src import config
from src.ai_explainer import explain_breakdown_with_source
from src.calculator import quote_recipient_first
from src.exchange_rate import get_usd_inr_rate_info
from src.paypal_service import create_order, finalize_order, get_approval_url

st.set_page_config(page_title="RemitSense AI", page_icon="💸", layout="centered")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Manrope:wght@400;500;600;700&display=swap');
:root{--ink:#0f1b2d;--mute:#5d6b7e;--line:#dfe4ea;--paper:#fff;--bg:#f2f4f7;--navy:#12315c;--saffron:#e59b12;--ok:#1f8a5b}
html,body,.stApp,[class*="css"]{font-family:'Manrope',system-ui,sans-serif;color:var(--ink)}
.stApp{background:var(--bg)}
#MainMenu,header,footer,[data-testid="stToolbar"]{display:none!important}
.block-container{max-width:780px;padding:2.2rem 1.2rem 4rem}
.brand{font-size:1.35rem;font-weight:700;letter-spacing:-.01em}
.brand b{color:var(--navy)}
.tag{color:var(--mute);font-size:.95rem;margin-top:.15rem}
.steps{display:flex;gap:6px;margin:1.4rem 0 1.8rem}
.steps div{flex:1;font-size:.8rem;color:var(--mute);border-top:3px solid var(--line);padding-top:.4rem}
.steps div.on{border-color:var(--navy);color:var(--ink);font-weight:600}
h2.q{font-size:1.5rem;font-weight:700;letter-spacing:-.02em;margin:0 0 .3rem}
p.sub{color:var(--mute);margin:0 0 1rem}
.stNumberInput label p{font-weight:600;color:var(--ink)}
.stNumberInput div[data-baseweb="input"]{background:#fff;border:1px solid var(--line);border-radius:10px}
.stNumberInput input{font-family:'Fraunces',serif;font-size:1.5rem;color:var(--ink);background:#fff}
.stButton>button,.stLinkButton a{border-radius:10px;font-weight:700;padding:.65rem 1.5rem;border:0;background:var(--navy);color:#fff}
.stButton>button:hover,.stLinkButton a:hover{background:#0c2446;color:#fff}
.st-key-pay .stButton>button,.st-key-pay .stLinkButton a{background:#ffc439;color:#111}
.st-key-pay .stButton>button:hover,.st-key-pay .stLinkButton a:hover{background:#f2b52a;color:#111}
.ticket{background:var(--paper);border:1px solid var(--line);border-radius:16px;margin:1.6rem 0 1.2rem;overflow:hidden}
.top{display:flex}
.side{flex:1;padding:1.6rem 1.6rem 1.3rem}
.side+.side{border-left:2px dashed var(--line)}
.lbl{color:var(--mute);font-size:.9rem;font-weight:600}
.fig{font-family:'Fraunces',serif;font-size:2.6rem;line-height:1.1;margin:.3rem 0;font-variant-numeric:lining-nums}
.note{color:var(--mute);font-size:.85rem}
.bottom{border-top:1px solid var(--line);padding:1.3rem 1.6rem 1.5rem;background:#fafbfc}
.tot{font-weight:700;margin-bottom:.7rem}
.tot small{color:var(--mute);font-weight:500}
.bar{display:flex;height:12px;border-radius:6px;overflow:hidden;background:var(--line);gap:2px}
.bar i{display:block}
.b1{background:var(--navy)}.b2{background:var(--saffron)}
.row{display:flex;align-items:flex-start;gap:.7rem;margin-top:.95rem}
.dot{width:10px;height:10px;border-radius:50%;margin-top:.4rem;flex:none}
.row .n{font-weight:600}.row .s{color:var(--mute);font-size:.85rem}
.row .v{margin-left:auto;text-align:right;font-weight:700}
.row .v small{display:block;color:var(--mute);font-weight:500;font-size:.8rem}
.meta{color:var(--mute);font-size:.82rem;margin:.2rem 0 1.6rem}
.ai{border-left:3px solid var(--navy);padding:.2rem 0 .2rem 1rem;margin:0 0 1.8rem}
.ai .h{font-weight:700;margin-bottom:.35rem}
.ai p{margin:0;line-height:1.6;max-width:62ch}
.ai .f{color:var(--mute);font-size:.8rem;margin-top:.5rem}
.sec{font-weight:700;font-size:1.1rem;margin:0 0 .2rem}
.receipt{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:1.6rem;margin:1.4rem 0}
.ok{color:var(--ok);font-weight:700}
.kv{display:flex;justify-content:space-between;gap:1rem;padding:.6rem 0;border-top:1px solid var(--line);font-size:.92rem}
.kv span:first-child{color:var(--mute)}.kv span:last-child{font-weight:600;word-break:break-all;text-align:right}
.foot{color:var(--mute);font-size:.78rem;margin-top:2.5rem}
@media(max-width:640px){.top{flex-direction:column}.side+.side{border-left:0;border-top:2px dashed var(--line)}.fig{font-size:2.1rem}}
"""
st.markdown("<style>" + re.sub(r"\s*\n\s*", "", CSS) + "</style>", unsafe_allow_html=True)


def ui(markup):
    # One line, and $ escaped so Streamlit doesn't read it as LaTeX.
    st.markdown(re.sub(r"\s*\n\s*", " ", markup.strip()).replace("$", "&#36;"),
                unsafe_allow_html=True)


def esc(x):
    return _html.escape(str(x))


def header(active):
    names = ["Quote", "Review", "Pay", "Done"]
    steps = "".join(f'<div class="{"on" if i <= active else ""}">{n}</div>'
                    for i, n in enumerate(names))
    ui(f'<div class="brand">RemitSense <b>AI</b></div>'
       f'<div class="tag">Tell us what your recipient needs. We tell you what to send.</div>'
       f'<div class="steps">{steps}</div>')


@st.cache_data(ttl=3600)
def cached_rate():
    return get_usd_inr_rate_info()


def start_over():
    st.query_params.clear()
    st.session_state.clear()
    st.rerun()


def handle_paypal_return():
    """Screen shown when PayPal redirects the buyer back to the app."""
    flag = st.query_params.get("paypal")
    order_id = st.query_params.get("token")

    if flag == "cancel":
        header(2)
        st.warning("Payment cancelled. Nothing was charged.")
        if st.button("Start a new quote"):
            start_over()
        st.stop()

    if flag == "return" and order_id:
        header(3)
        key = f"final_{order_id}"
        if key not in st.session_state:
            try:
                with st.spinner("Confirming your payment with PayPal..."):
                    st.session_state[key] = finalize_order(order_id)
            except Exception as e:
                st.session_state[key] = {"error": str(e)}
        out = st.session_state[key]

        if "error" in out:
            st.error(f"Could not confirm payment: {out['error']}")
        else:
            rows = [("Order ID", out["order_id"]), ("Capture ID", out["capture_id"]),
                    ("Status", out["capture_status"] or out["order_status"]),
                    ("Transfer", out["description"])]
            kv = "".join(f'<div class="kv"><span>{k}</span><span>{esc(v)}</span></div>'
                         for k, v in rows if v)
            ui(f'''<div class="receipt"><div class="ok">Payment confirmed</div>
                <div class="fig">{esc(out["currency"])} {esc(out["amount"])}</div>
                <div class="note" style="margin-bottom:1rem">Paid with PayPal Sandbox</div>{kv}</div>
                <div class="note">RemitSense estimates the recipient payout from live rates and a fee
                model. PayPal Sandbox demonstrates the payment flow; no INR is deposited and no real
                money moves.</div>''')
        if st.button("Start a new quote"):
            start_over()
        st.stop()


handle_paypal_return()

quote = st.session_state.get("quote")
header(2 if st.session_state.get("paypal_order") else 1 if quote else 0)

ui('<h2 class="q">How much does your recipient need?</h2>'
   '<p class="sub">Enter the amount in rupees. We work out what you pay in dollars.</p>')

recipient_inr = st.number_input("Recipient needs (INR)", min_value=1000,
                                max_value=10000000, value=50000, step=1000)

if st.button("Get my quote", type="primary"):
    try:
        info = cached_rate()
        if info["stale"]:
            cached_rate.clear()  # retry the live API next time

        result = quote_recipient_first(
            recipient_inr=recipient_inr, mid_rate=info["rate"],
            fx_markup=config.FX_MARKUP, pct_fee=config.PCT_FEE,
            fixed_fee_usd=config.FIXED_FEE_USD)

        with st.spinner("Preparing explanation..."):
            explanation, source = explain_breakdown_with_source(result)

        st.session_state["quote"] = {"rate_info": info, "result": result,
                                     "target": recipient_inr,
                                     "explanation": explanation,
                                     "explanation_source": source}
        st.session_state.pop("paypal_order", None)
        st.rerun()
    except Exception as e:
        st.error(f"Calculation failed: {e}")

if quote:
    info, r = quote["rate_info"], quote["result"]

    if info["stale"]:
        st.warning("Live exchange rate unavailable. Using the last saved rate "
                   f"from {info['fetched_at']} (UTC).")

    def row(color, name, sub, inr, usd, share):
        return (f'<div class="row"><span class="dot" style="background:{color}"></span>'
                f'<div><div class="n">{name}</div><div class="s">{sub}</div></div>'
                f'<div class="v">₹{inr:,}<small>${usd:,.2f} · {share}% of deductions</small></div></div>')

    ui(f'''<div class="ticket"><div class="top">
        <div class="side"><div class="lbl">You send</div>
          <div class="fig">${r["send_usd"]:,.2f}</div><div class="note">US dollars, paid with PayPal</div></div>
        <div class="side"><div class="lbl">They receive</div>
          <div class="fig">₹{r["recipient_inr"]:,}</div><div class="note">Indian rupees, exactly as requested</div></div>
      </div><div class="bottom">
        <div class="tot">₹{r["total_loss_inr"]:,} <small>(${r["total_loss_usd"]:,.2f}) lost to fees and conversion</small></div>
        <div class="bar"><i class="b1" style="width:{r["fee_share_pct"]}%"></i><i class="b2" style="width:{r["fx_share_pct"]}%"></i></div>
        {row("var(--navy)", "Transfer fees", f'{r["pct_fee_percent"]}% plus ${r["fixed_fee_usd"]:.2f} per payment',
             r["fee_loss_inr"], r["fee_usd"], r["fee_share_pct"])}
        {row("var(--saffron)", "Currency conversion", f'{r["fx_markup_percent"]}% above the market rate',
             r["fx_loss_inr"], r["fx_loss_usd"], r["fx_share_pct"])}
      </div></div>
      <div class="meta">Market rate ₹{r["mid_rate"]:.2f} per $1. After markup you get ₹{r["effective_rate"]:.2f}.
        Rate checked {esc(info["fetched_at"][:16].replace("T", " "))} UTC.</div>''')

    fallback = ('<div class="f">Standard explanation shown. The AI answer was unavailable '
                'or failed the number check.</div>' if quote["explanation_source"] == "fallback" else "")
    ui(f'<div class="ai"><div class="h">In plain words</div><p>{esc(quote["explanation"])}</p>{fallback}</div>')

    ui('<div class="sec">Pay with PayPal</div>'
       f'<p class="sub">You will pay ${r["send_usd"]:,.2f} in the PayPal Sandbox. No real money moves.</p>')

    with st.container(key="pay"):
        if st.button("Pay with PayPal"):
            try:
                order = create_order(
                    r["send_usd"],
                    description=f"RemitSense transfer - recipient receives INR {r['recipient_inr']}")
                url = get_approval_url(order)
                if not url:
                    raise RuntimeError("PayPal did not return an approval link")
                st.session_state["paypal_order"] = {"id": order["id"], "approval_url": url}
                st.rerun()
            except Exception as e:
                st.error(f"PayPal error: {e}")

        po = st.session_state.get("paypal_order")
        if po:
            st.link_button("Continue to PayPal checkout", po["approval_url"])
            st.caption(f"Order {po['id']} created. Log in with your sandbox buyer account, "
                       "approve, and you will return here for your receipt.")

ui('<div class="foot">Exchange rates by <a href="https://www.exchangerate-api.com">ExchangeRate-API</a>. '
   'Estimates only; PayPal Sandbox does not deposit INR.</div>')