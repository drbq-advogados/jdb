"""
Regenerates `cache_results.json` by calling `app.orchestrate(force=True)`.
Use: .\.venv\Scripts\python.exe regen_cache.py
"""
import json
import os
from datetime import datetime

CACHE_FILE = os.path.abspath("cache_results.json")


def _normalize_fetched_at(cache_path: str) -> None:
    """Ensure `fetched_at` fields in cache are numeric epoch seconds.

    This prevents TypeError when other modules subtract against `now`.
    """
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return

    changed = False

    def _convert(val):
        if isinstance(val, (int, float)):
            return float(val), False
        if isinstance(val, str):
            # try parse numeric string first, then ISO datetime
            try:
                return float(val), False
            except Exception:
                pass
            try:
                dt = datetime.fromisoformat(val)
                return dt.timestamp(), True
            except Exception:
                return 0.0, True
        return 0.0, False

    # top-level
    if "fetched_at" in data:
        new_val, changed_flag = _convert(data.get("fetched_at"))
        if not isinstance(data.get("fetched_at"), float):
            data["fetched_at"] = new_val
            changed = changed or changed_flag

    # payload.fetched_at
    payload = data.get("payload")
    if isinstance(payload, dict) and "fetched_at" in payload:
        new_val, changed_flag = _convert(payload.get("fetched_at"))
        if not isinstance(payload.get("fetched_at"), float):
            payload["fetched_at"] = new_val
            data["payload"] = payload
            changed = changed or changed_flag

    if changed:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    # Normalize cache before importing app to avoid import-time errors
    _normalize_fetched_at(CACHE_FILE)

    # Now import and call orchestrate
    from app import orchestrate

    print('Calling app.orchestrate(force=True) to regenerate cache_results.json...')
    from_cache, payload = orchestrate(force=True, ttl_min=0, proxies=[])
    print('Regeneration done. from_cache:', from_cache)
    if payload:
        print('Payload fetched_at:', payload.get('fetched_at'))

    # Some code paths (app.orchestrate) persist ISO timestamps inside payload; ensure
    # the saved cache contains numeric epoch seconds everywhere.
    _normalize_fetched_at(CACHE_FILE)
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            final = json.load(f)
            print('Final cache fetched_at (top-level):', type(final.get('fetched_at')),
                  final.get('fetched_at'))
            payload_final = final.get('payload') or {}
            print('Final payload.fetched_at type:', type(payload_final.get('fetched_at')),
                  payload_final.get('fetched_at'))
    except Exception:
        pass


if __name__ == '__main__':
    main()
