"""Fee model for RemitSense AI.

Source: PayPal India merchant fees page (seller receiving an international
payment from outside India, USD received and converted to INR):
https://www.paypal.com/in/business/paypal-business-fees
(page states "Last Updated: 28 March 2024"; checked 27 Oct 2026)

  - Receiving international transactions: 4.40% + fixed fee
  - Fixed fee for USD:                    0.30 USD
  - Converting payments received into another currency:
                                          3.0% above the base exchange rate

Re-check the page before submitting in case PayPal has changed these.
"""
import os

from dotenv import load_dotenv

load_dotenv()

PCT_FEE = 0.044          # percentage fee on international payments received
FIXED_FEE_USD = 0.30     # fixed fee per transaction when received in USD
FX_MARKUP = 0.03         # markup above the base (mid-market) exchange rate

# Public URL of this app. PayPal redirects the buyer back here after approval.
# Local: http://localhost:8501   Render: https://<your-service>.onrender.com
APP_BASE_URL = "https://remitsense-ai.onrender.com"

