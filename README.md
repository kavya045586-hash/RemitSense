# RemitSense AI

**Recipient-first cross-border payments.** Most payment flows ask "how much do you
want to send?" RemitSense asks "how much does the recipient need?" It computes the
USD to send so the recipient gets an exact INR amount, shows where every deduction
comes from, explains it in plain English, and finishes with a PayPal Sandbox checkout.

> **Core rule: code calculates, AI explains.** Every number comes from
> deterministic Python (`src/calculator.py`). Gemini only explains those numbers, and
> its text is rejected (replaced by a template) if it contains any number that is not
> in the computed result.

*Built from scratch during the PayPal AI Hackathon 2026 submission period (new project).*

## Features
- Recipient-first calculator (USD to send, fee cost, conversion cost, INR received)
- Fee breakdown in USD and INR, with each part's share of the total deduction
- Live USD→INR rate (cached, with last-good-rate fallback if the API is down)
- AI explanation (Gemini) guarded by a number-verification check
- PayPal Sandbox checkout: create order → buyer approves → app captures → confirmation screen
- 34 unit tests (calculator consistency, AI number guard, PayPal flow)

## Flow
1. Enter the INR amount the recipient needs.
2. App fetches the live exchange rate and applies the fee model in `src/config.py`.
3. Calculator returns the USD to send and the expected INR received.
4. Gemini explains the breakdown in plain language.
5. **Pay with PayPal** creates a Sandbox order; the buyer approves on PayPal and is
   redirected back, where the app captures the order and shows a confirmation.

## Run locally
Requires Python 3.10+.
```bash
python -m venv venv
venv\Scripts\activate            # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp .env.example .env, then fill in the keys
streamlit run app.py
```
Open http://localhost:8501. Run the tests with `pytest`. Check your Gemini key with
`python check_gemini.py`.

### Environment variables
| Name | Purpose |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (without it the app shows a template explanation) |
| `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET` | PayPal **Sandbox** REST app credentials |
| `APP_BASE_URL` | Public URL of the app, used for PayPal return/cancel (default `http://localhost:8501`) |
| `GEMINI_MODEL` | Optional, default `gemini-flash-latest` |

Secrets are never committed (`.env` is git-ignored).

## Test the PayPal checkout (for judges)
Sandbox buyer (use this login on the PayPal checkout page):
- Email: `REPLACE_WITH_SANDBOX_BUYER_EMAIL`
- Password: `REPLACE_WITH_SANDBOX_BUYER_PASSWORD`

Steps: Calculate → **Pay with PayPal** → **Open PayPal Checkout** → log in as the
buyer → **Complete Purchase** → you return to the app and see "Payment confirmed".
Use a private window if your browser is already signed in to a real PayPal account.

**Honest limitation:** PayPal Sandbox cannot deposit INR into a real recipient account.
RemitSense estimates the recipient payout using live exchange rates and a fee model,
while PayPal Sandbox demonstrates the payment workflow.

## Fee model
Values live in `src/config.py` and follow PayPal's India merchant fees page
(https://www.paypal.com/in/business/paypal-business-fees, checked 27 Oct 2026):

| Item | Value |
|---|---|
| International payment received | 4.40% |
| Fixed fee (USD) | 0.30 USD |
| Conversion of payments received into another currency | 3.0% above the base rate |

These are estimates for a seller in India receiving a USD payment from abroad.

## Deploy on Render
1. Push this repo to GitHub and create a Render **Blueprint** or Web Service from it
   (`render.yaml` is included).
2. Set `GEMINI_API_KEY`, `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`.
3. Set `APP_BASE_URL` to your Render URL (for example `https://remitsense-ai.onrender.com`).
   The free tier sleeps when idle, so open the URL once before demoing.

## Project layout
```
app.py                  Streamlit UI and PayPal return handling
src/calculator.py       Recipient-first quote (single source of all numbers)
src/config.py           Fee model
src/exchange_rate.py    Live USD→INR rate with fallback
src/ai_explainer.py     Gemini explanation + number guard + fallback
src/paypal_service.py   PayPal Orders v2: create, get, capture
tests/                  pytest suite
```

Exchange rates by [ExchangeRate-API](https://www.exchangerate-api.com).

## License
MIT. See [LICENSE](LICENSE).
