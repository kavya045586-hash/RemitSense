# RemitSense AI

RemitSense AI is a Python application for estimating cross-border payments from USD to INR. Instead of starting with the amount the sender wants to transfer, it starts with the amount the recipient needs to receive.

The application calculates the estimated USD payment, breaks down the fees and currency conversion costs, and provides an explanation of the calculation. It also includes a PayPal Sandbox checkout flow for testing the payment process.

## Features

- Calculate the USD amount required to deliver a target INR amount.
- Show the estimated transaction fee, currency conversion cost, and recipient amount.
- Retrieve the latest available USD-to-INR exchange rate, with caching and a fallback rate.
- Generate plain-language explanations using Google Gemini.
- Validate AI-generated explanations against the calculated results and use a template when the explanation fails validation.
- Create, approve, and capture PayPal Sandbox orders.
- Run automated tests for the calculator, explanation validation, and payment flow.

## How it works

1. Enter the amount you want the recipient to receive in INR.
2. The application retrieves the exchange rate and applies the fee settings defined in `src/config.py`.
3. The calculator estimates the USD amount required and produces a fee breakdown.
4. The application generates an explanation of the result.
5. If you choose PayPal checkout, the app creates a Sandbox order and redirects you to PayPal for approval.
6. After approval, the application captures the order and displays the payment status.

The payment calculation is handled by Python code. Gemini is used only to explain the calculated result, not to determine the payment amounts.

## Technology stack

- **Python** — calculation and application logic
- **Streamlit** — user interface
- **Google Gemini API** — payment explanation
- **PayPal Orders API v2** — Sandbox checkout
- **ExchangeRate-API** — USD-to-INR exchange rates
- **pytest** — automated tests

## Requirements

- Python 3.10 or later
- A Google Gemini API key (optional; a template explanation is used without it)
- PayPal Sandbox REST application credentials for checkout testing

## Installation

Clone the repository and move into the project directory:

```bash
git clone https://github.com/kavya045586-hash/RemitSense.git
cd RemitSense
```

Create and activate a virtual environment.

**Windows:**

```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file by copying the example:

```bash
copy .env.example .env
```

On macOS or Linux, use `cp .env.example .env` instead.

Add the required credentials to `.env`, then start the application:

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Configuration

Set the following environment variables in your local `.env` file or deployment environment.

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key. Optional; the app can use a template explanation instead. |
| `PAYPAL_CLIENT_ID` | PayPal Sandbox application client ID. |
| `PAYPAL_SECRET` | PayPal Sandbox application secret. |
| `APP_BASE_URL` | Base URL used for PayPal return and cancellation redirects. Defaults to `http://localhost:8501`. |
| `GEMINI_MODEL` | Gemini model to use. Defaults to `gemini-flash-latest`. |

Do not commit `.env` or other files containing credentials. The repository includes `.env.example` for documenting the required configuration.

## Running the tests

Run the automated test suite with:

```bash
pytest
```

To check the Gemini API configuration, run:

```bash
python check_gemini.py
```

## Fee calculation

The fee settings are defined in `src/config.py`. The current model uses the following estimates for an Indian merchant receiving an international USD payment:

| Fee component | Configured value |
|---|---:|
| International payment fee | 4.40% |
| Fixed transaction fee | USD 0.30 |
| Currency conversion markup | 3.0% above the base exchange rate |

These values are assumptions used by the application and should be checked against the applicable PayPal fees before relying on a quote. Actual fees can vary by transaction type, account, and applicable terms.

## PayPal Sandbox

The application uses PayPal Sandbox to demonstrate order creation, buyer approval, and payment capture. Use a Sandbox buyer account when testing checkout.

1. Calculate a payment.
2. Select **Pay with PayPal**.
3. Open the PayPal checkout page.
4. Sign in using your Sandbox buyer account.
5. Approve the payment and return to the application.
6. Check the resulting payment status.

Create a test buyer account through the PayPal Developer Dashboard if you do not already have one. Do not put Sandbox passwords or other credentials in this README.

**Limitation:** Sandbox checkout does not transfer INR to a real recipient's bank account. The recipient amount is an estimate based on the exchange rate and configured fee model; the PayPal flow demonstrates payment processing rather than an actual international payout.

## Deployment

The repository includes a `render.yaml` configuration for deployment on Render.

1. Push the project to GitHub.
2. Create a Render service using the repository and its configuration.
3. Add the required environment variables in Render.
4. Set `APP_BASE_URL` to the deployed application's public URL.
5. Test the calculator and PayPal Sandbox flow after deployment.

The service may take some time to respond after periods of inactivity, depending on the selected hosting plan.

## Project structure

```text
RemitSense/
├── app.py                  # Streamlit interface and payment flow
├── src/
│   ├── calculator.py       # Payment and fee calculations
│   ├── config.py           # Fee model and configuration
│   ├── exchange_rate.py    # Exchange rate retrieval and fallback
│   ├── ai_explainer.py     # Gemini explanations and validation
│   └── paypal_service.py   # PayPal order operations
├── tests/                  # Automated tests
├── check_gemini.py         # Gemini configuration check
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment configuration
├── .env.example            # Example environment variables
└── README.md
```

## Exchange rates

Exchange rate data is retrieved from [ExchangeRate-API](https://www.exchangerate-api.com/).

## License

See the [LICENSE](LICENSE) file for licensing information.
