"""Run:  python check_gemini.py
Tests your Gemini key against each model the app will try."""
import time

from src import config
from src.ai_explainer import MODELS, _ask_model, numbers_are_grounded
from src.calculator import quote_recipient_first

data = quote_recipient_first(
    50000, 88.0, config.FX_MARKUP, config.PCT_FEE, config.FIXED_FEE_USD
)

for model in MODELS:
    print(f"\n--- {model} ---")
    start = time.time()
    try:
        text = _ask_model(data, model)
    except Exception as e:
        print(f"FAILED after {time.time() - start:.1f}s: "
              f"{type(e).__name__}: {str(e)[:200]}")
        continue

    print(text)
    ok = numbers_are_grounded(text, data)
    print(f"({time.time() - start:.1f}s) Number check:",
          "PASSED" if ok else "FAILED (invented a number)")
