import json
import os
import re

from dotenv import load_dotenv

load_dotenv()

# Tried in order. If one is overloaded (503) or unavailable, the next is used.
# Set GEMINI_MODEL in .env to put your preferred model first.
_DEFAULT_MODELS = [
    "gemini-3.5-flash-lite",   # fast and cheap, plenty for a short explanation
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-flash-latest",     # alias, last resort
]
_preferred = os.getenv("GEMINI_MODEL")
MODELS = ([_preferred] if _preferred else []) + [
    m for m in _DEFAULT_MODELS if m != _preferred
]
MODEL = MODELS[0]

SYSTEM_INSTRUCTION = (
    "You are RemitSense AI, a payment explainer. You receive a JSON "
    "payment breakdown that was already computed by code. Explain it in "
    "plain, friendly English. Never calculate, round, convert or invent "
    "numbers: only repeat numbers that appear in the JSON, exactly as given."
)

_client = None

NUM_RE = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")


def _get_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        from google import genai
        from google.genai import types

        _client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=15000)  # 15 s, in ms
        )

    return _client


def numbers_in(text):
    return [float(m.replace(",", "")) for m in NUM_RE.findall(text)]


def numbers_are_grounded(text, data):
    """True if every number in `text` appears in `data` (within rounding)."""
    allowed = [
        float(v) for v in data.values()
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    ]

    return all(
        any(abs(n - a) <= 0.011 for a in allowed)
        for n in numbers_in(text)
    )


def template_explanation(data):
    """Deterministic fallback used if the AI fails or invents numbers."""
    bigger = (
        "currency conversion"
        if data["fx_loss_inr"] >= data["fee_loss_inr"]
        else "transfer fees"
    )

    return (
        f"To deliver ₹{data['recipient_inr']:,} to your recipient, you pay "
        f"${data['send_usd']:,.2f}. Total deductions are "
        f"₹{data['total_loss_inr']:,}. Currency conversion costs "
        f"₹{data['fx_loss_inr']:,} ({data['fx_share_pct']}% of the "
        f"deductions), from a {data['fx_markup_percent']}% markup on the "
        f"market rate of {data['mid_rate']}. Transfer fees cost "
        f"₹{data['fee_loss_inr']:,} ({data['fee_share_pct']}%): "
        f"{data['pct_fee_percent']}% plus ${data['fixed_fee_usd']:.2f}. "
        f"Most of the cost comes from {bigger}."
    )


def _ask_model(data, model=None):
    from google.genai import types

    prompt = f"""Payment breakdown (JSON, computed by code):

{json.dumps(data, indent=2)}

Write a short, friendly explanation for the sender.
- Start directly; no greeting and no self-introduction.
- 3 to 4 sentences, maximum 80 words, plain text, no markdown or lists.
- Say how much they pay ($) so the recipient gets the INR amount.
- Name the two costs, transfer fees and currency conversion, in ₹, and say
  which is larger and what share of the total deduction it is.
- Do not list every field or rate; only use the numbers that help.
- Use only numbers that appear in the JSON, exactly as given. Never
  calculate, round or invent numbers.
- Use ₹ for INR and $ for USD.
"""

    response = _get_client().models.generate_content(
        model=model or MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            # Only older 2.5 models accept thinking_budget; turning thinking
            # off keeps them fast. Newer models are left at their defaults.
            thinking_config=(
                types.ThinkingConfig(thinking_budget=0)
                if "2.5" in (model or MODEL) else None
            ),
        ),
    )

    return (response.text or "").strip()


def explain_breakdown_with_source(data):
    """Return (text, source). source is "ai" or "fallback".

    The AI text is only used if every number in it matches the computed
    values; otherwise a deterministic template is returned.
    """
    for model in MODELS:
        try:
            text = _ask_model(data, model)
        except Exception as e:
            print(f"[Gemini error] {model}: {type(e).__name__}: {e}", flush=True)
            continue

        if text and numbers_are_grounded(text, data):
            return text, "ai"

        print(f"[Gemini] {model}: reply failed the number check", flush=True)

    return template_explanation(data), "fallback"


def explain_breakdown(data):
    return explain_breakdown_with_source(data)[0]