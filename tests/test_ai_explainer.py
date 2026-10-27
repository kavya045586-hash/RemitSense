from src import ai_explainer, config
from src.calculator import quote_recipient_first

DATA = quote_recipient_first(
    50000, 88.0, config.FX_MARKUP, config.PCT_FEE, config.FIXED_FEE_USD
)


def test_template_is_grounded():
    assert ai_explainer.numbers_are_grounded(
        ai_explainer.template_explanation(DATA), DATA
    )


def test_invented_number_rejected():
    assert not ai_explainer.numbers_are_grounded(
        "You will lose about 7,777 rupees.", DATA
    )


def test_fallback_when_model_invents_numbers(monkeypatch):
    monkeypatch.setattr(ai_explainer, "_ask_model", lambda d, m=None: "You lose 7,777.")
    text, source = ai_explainer.explain_breakdown_with_source(DATA)
    assert source == "fallback"
    assert ai_explainer.numbers_are_grounded(text, DATA)


def test_fallback_when_model_errors(monkeypatch):
    def boom(d, m=None):
        raise RuntimeError("no key")

    monkeypatch.setattr(ai_explainer, "_ask_model", boom)
    assert ai_explainer.explain_breakdown_with_source(DATA)[1] == "fallback"


def test_grounded_ai_text_accepted(monkeypatch):
    good = f"You pay ${DATA['send_usd']:,.2f} so they receive ₹{DATA['recipient_inr']:,}."
    monkeypatch.setattr(ai_explainer, "_ask_model", lambda d, m=None: good)
    assert ai_explainer.explain_breakdown_with_source(DATA) == (good, "ai")
