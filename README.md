# RemitSense AI

RemitSense AI is a Python application for estimating cross-border payments from USD to INR. Instead of starting with the amount the sender wants to transfer, it starts with the amount the recipient needs to receive.

The application calculates the estimated USD payment, breaks down fees and currency conversion costs, and provides an easy-to-understand explanation of the calculation. It also includes a PayPal Sandbox checkout flow for testing the payment process.

## Live Demo

https://remitsense-ai.onrender.com

## Video Demo

https://youtu.be/3b0Dbv9Htwo

The demo video demonstrates:

- Recipient-first INR payment estimation
- Fee and exchange-rate breakdown
- AI-generated payment explanations using Google Gemini
- PayPal Sandbox checkout flow
- Order approval and payment capture

---

## Features

- Calculate the USD amount required to deliver a target INR amount.
- Show estimated transaction fees, currency conversion costs, and recipient amount.
- Retrieve the latest available USD-to-INR exchange rate with caching and fallback support.
- Generate plain-language payment explanations using Google Gemini.
- Validate AI-generated explanations against calculated results.
- Use a template-based explanation if validation fails.
- Create, approve, and capture PayPal Sandbox orders.
- Run automated tests for calculations, explanations, and payment flow.

---

## Problem Statement

When sending money internationally, users usually know how much the recipient needs to receive, but most payment systems begin with the amount being sent. This makes it difficult to understand fees, exchange rates, and the final amount delivered.

RemitSense AI solves this problem by working backward from the recipient's target INR amount and providing transparency into fees, exchange rates, and payment costs before a payment is made.

---

## How It Works

1. Enter the amount the recipient should receive in INR.
2. The application retrieves the latest USD-INR exchange rate.
3. The calculator applies configurable fees and currency conversion costs.
4. The required USD payment amount is estimated.
5. Google Gemini generates a plain-language explanation of the result.
6. Users can initiate a PayPal Sandbox checkout.
7. After approval, the payment is captured and the status is displayed.

---

## Architecture

```text
User Input (Target INR Amount)
              │
              ▼
     Exchange Rate API
              │
              ▼
     Payment Calculator
              │
              ▼
      Fee Breakdown
              │
              ▼
    Gemini Explanation
              │
              ▼
  PayPal Sandbox Order
              │
              ▼
     Payment Capture
```

---

## Technology Stack

### Core Technologies

- Python
- Streamlit

### AI

- Google Gemini API
- Explanation validation and fallback system

### Payments

- PayPal Orders API v2
- PayPal Sandbox

### Data

- ExchangeRate-API

### Testing

- pytest

---

## AI Usage

Google Gemini is used exclusively to explain calculation results in user-friendly language.

The payment amounts, fees, exchange rates, and recipient values are determined entirely by the application's calculation engine.

If the AI explanation does not match the calculated results, RemitSense AI automatically falls back to a validated template-based explanation. This ensures consistency and reliability.

---

## PayPal Usage

RemitSense AI integrates with PayPal Orders API v2 to:

- Create payment orders
- Redirect buyers to PayPal for approval
- Capture approved payments
- Display payment status

The PayPal Sandbox environment is used for testing and demonstration purposes.

---

## Requirements

- Python 3.10 or later
- Google Gemini API Key (optional)
- PayPal Sandbox REST Application Credentials

---

## Installation

Clone the repository:

```bash
git clone https://github.com/kavya045586-hash/RemitSense.git
cd RemitSense
```

Create and activate a virtual environment.

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create an environment file:

### Windows

```powershell
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Add the required credentials to `.env`.

Run the application:

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

## Configuration

| Variable | Description |
|-----------|------------|
| GEMINI_API_KEY | Google Gemini API Key (optional) |
| PAYPAL_CLIENT_ID | PayPal Sandbox Client ID |
| PAYPAL_SECRET | PayPal Sandbox Secret |
| APP_BASE_URL | URL used for PayPal redirects |
| GEMINI_MODEL | Gemini model name (default: gemini-flash-latest) |

> Never commit secrets or credentials to version control.

---

## Running Tests

Run the automated test suite:

```bash
pytest
```

Check Gemini configuration:

```bash
python check_gemini.py
```

---

## Fee Calculation Model

Fee settings are configurable through `src/config.py`.

Current assumptions:

| Fee Component | Value |
|--------------|--------|
| International Payment Fee | 4.40% |
| Fixed Transaction Fee | USD 0.30 |
| Currency Conversion Markup | 3.0% |

These values are estimates used for demonstration purposes and may differ from actual PayPal fees.

Always verify current pricing before relying on production estimates.

---

## PayPal Sandbox Testing

1. Enter a target INR amount.
2. Review the calculated estimate.
3. Select **Pay with PayPal**.
4. Sign in using a PayPal Sandbox buyer account.
5. Approve the payment.
6. Return to the application.
7. View the captured payment status.

### Limitation

Sandbox payments do not transfer real funds and do not deliver INR to a real recipient.

The recipient amount shown by RemitSense AI is an estimate based on exchange rates and configured fee assumptions. The PayPal Sandbox integration demonstrates payment processing functionality only.

---

## Deployment

The project includes a Render deployment configuration.

Deployment steps:

1. Push the repository to GitHub.
2. Create a Render service.
3. Connect the GitHub repository.
4. Add the required environment variables.
5. Set `APP_BASE_URL` to the deployed application URL.
6. Deploy and test the application.

### Live Application

https://remitsense-ai.onrender.com

---

## Project Structure

```text
RemitSense/
├── app.py
├── src/
│   ├── calculator.py
│   ├── config.py
│   ├── exchange_rate.py
│   ├── ai_explainer.py
│   └── paypal_service.py
├── tests/
├── check_gemini.py
├── requirements.txt
├── render.yaml
├── .env.example
├── LICENSE
└── README.md
```

---

## Exchange Rates

Exchange rate data is retrieved from:

https://www.exchangerate-api.com/

---

## Future Improvements

- Support additional countries and currencies
- Historical exchange-rate analysis
- Exchange-rate alerts
- Fee comparison across providers
- Recipient-side payout simulations
- Enhanced AI-powered payment insights

---

## License

This project is licensed under the MIT License.

See the LICENSE file for details.
