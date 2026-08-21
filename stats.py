"""
Periodisk statistikk-oppsummering til Slack.

Leser events.csv og oppsummerer hvor det har vært mest strømbrudd.
Kjøres av en egen GitHub Actions-workflow (f.eks. hver mandag morgen).

Bruk:
    python stats.py            # siste 7 dager (standard)
    python stats.py 30         # siste 30 dager
"""
import csv
import os
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta

from config import EVENTS_CSV
import slack


def _read_starts(days: int):
    """Hent START-hendelser nyere enn 'days' dager, som liste av dict."""
    if not os.path.exists(EVENTS_CSV):
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = []
    with open(EVENTS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("event") != "START":
                continue
            try:
                ts = datetime.fromisoformat(row["timestamp_utc"])
            except (ValueError, KeyError):
                continue
            if ts >= cutoff:
                rows.append(row)
    return rows


def build_summary(days: int = 7) -> str:
    rows = _read_starts(days)

    # Skill faktiske brudd fra planlagte
    faktiske = [r for r in rows if str(r.get("planned")).lower() != "true"]
    planlagte = [r for r in rows if str(r.get("planned")).lower() == "true"]

    if not rows:
        return (f"📊 *Strømbrudd-statistikk – siste {days} dager*\n"
                f"Ingen registrerte brudd i perioden. 🎉")

    per_kommune = Counter(r["kommune"] for r in faktiske if r.get("kommune"))
    per_area = Counter(
        f'{r.get("area")} ({r.get("kommune")})'
        for r in faktiske if r.get("area")
    )

    linjer = [f"📊 *Strømbrudd-statistikk – siste {days} dager*", ""]
    linjer.append(f"Faktiske brudd: *{len(faktiske)}*   ·   Planlagte stanser: {len(planlagte)}")
    linjer.append("")

    if per_kommune:
        linjer.append("*Per kommune (faktiske brudd):*")
        for komm, n in per_kommune.most_common():
            linjer.append(f"  • {komm}: {n}")
        linjer.append("")

    if per_area:
        linjer.append("*Mest utsatte steder:*")
        for area, n in per_area.most_common(5):
            linjer.append(f"  • {area}: {n}")

    return "\n".join(linjer)


def main():
    days = 7
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            pass
    summary = build_summary(days)
    print(summary)
    slack.post(summary)


if __name__ == "__main__":
    main()
