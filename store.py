"""
Tilstand og historikk.

- state.json:  hvilke brudd som er aktive akkurat nå (for dedupe/varsling)
- events.csv:  append-only historikk. Én rad hver gang et brudd starter
               (event=START) og én når det er over (event=END, med varighet).
               Dette er datagrunnlaget for statistikken.
"""
import csv
import json
import os
from datetime import datetime, timezone

from config import STATE_FILE, EVENTS_CSV, DATA_DIR

CSV_HEADER = [
    "timestamp_utc", "event", "id", "source", "kommune", "kommunenr",
    "area", "customers", "planned", "status", "cause",
    "start_ms", "end_ms", "duration_min",
]


def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_state() -> dict:
    """Returnerer {id: {..outage.., 'first_seen': iso}} for aktive brudd."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _ensure_csv():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_HEADER)


def log_event(event: str, o: dict, duration_min=None) -> None:
    """Skriv en rad til events.csv. o er en outage som dict."""
    _ensure_csv()
    with open(EVENTS_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            _now_iso(), event, o.get("id"), o.get("source"),
            o.get("kommune"), o.get("kommunenr"), o.get("area"),
            o.get("customers"), o.get("planned"), o.get("status"),
            o.get("cause"), o.get("start_ms"), o.get("end_ms"), duration_min,
        ])
