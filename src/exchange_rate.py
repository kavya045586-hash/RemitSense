import json
from datetime import datetime, timezone
from pathlib import Path

import requests

URL = "https://open.er-api.com/v6/latest/USD"
CACHE_FILE = Path(__file__).resolve().parent.parent / ".rate_cache.json"


def _save_cache(rate, fetched_at):
    try:
        CACHE_FILE.write_text(
            json.dumps({"rate": rate, "fetched_at": fetched_at})
        )
    except OSError:
        pass


def _load_cache():
    try:
        return json.loads(CACHE_FILE.read_text())
    except (OSError, ValueError):
        return None


def get_usd_inr_rate_info():
    """Return {"rate", "fetched_at", "stale"}.

    If the live API fails, falls back to the last good rate saved on disk
    (stale=True) so the demo does not break. Raises only if there is no
    live rate and no saved rate.
    """
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            raise ValueError("Exchange-rate API reported failure")

        rate = float(data["rates"]["INR"])
        if rate <= 0:
            raise ValueError("Invalid INR rate")

        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        _save_cache(rate, fetched_at)

        return {"rate": rate, "fetched_at": fetched_at, "stale": False}

    except Exception:
        cached = _load_cache()
        if cached:
            return {
                "rate": float(cached["rate"]),
                "fetched_at": cached["fetched_at"],
                "stale": True,
            }
        raise


def get_usd_inr_rate():
    return get_usd_inr_rate_info()["rate"]
