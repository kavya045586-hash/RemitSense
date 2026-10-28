
import os

from dotenv import load_dotenv

load_dotenv()

PCT_FEE = 0.044          # percentage fee on international payments received
FIXED_FEE_USD = 0.30     # fixed fee per transaction when received in USD
FX_MARKUP = 0.03         # markup above the base (mid-market) exchange rate

# Public URL of this app. PayPal redirects the buyer back here after approval.
# Local: http://localhost:8501   Render: https://<your-service>.onrender.com
APP_BASE_URL = "https://remitsense-ai.onrender.com"

