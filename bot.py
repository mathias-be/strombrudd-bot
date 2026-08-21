"""
Hovedløkke for strømbrudd-boten.

Kjøres av GitHub Actions hvert ~10. minutt:
  1. Hent alle pågående brudd fra kildene (Norgesnett, Elvia)
  2. Sammenlign med forrige kjøring (state.json)
  3. Varsle Slack om NYE brudd, og om brudd som er GJENOPPRETTET
  4. Logg alt til events.csv (datagrunnlag for statistikk)
"""
from datetime import datetime, timezone

from config import NOTIFY_PLANNED
import slack
import store
from sources import fetch_all


def _duration_min(start_ms, first_seen_iso):
    """Antall minutter et brudd varte, best mulig anslag."""
    now = datetime.now(timezone.utc)
    start = None
    if start_ms:
        try:
            start = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            start = None
    if start is None and first_seen_iso:
        try:
            start = datetime.fromisoformat(first_seen_iso)
        except ValueError:
            start = None
    if start is None:
        return None
    return max(0, round((now - start).total_seconds() / 60))


def should_notify(planned: bool) -> bool:
    return NOTIFY_PLANNED or not planned


def main():
    current = {o.id: o for o in fetch_all()}
    state = store.load_state()

    new_ids = [oid for oid in current if oid not in state]
    cleared_ids = [oid for oid in state if oid not in current]

    # --- Nye brudd ---
    for oid in new_ids:
        o = current[oid]
        store.log_event("START", o.to_dict())
        if should_notify(o.planned):
            slack.notify_new_outage(o)
        d = o.to_dict()
        d["first_seen"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        state[oid] = d

    # --- Fortsatt aktive: oppdater felt (kundeantall kan endre seg) ---
    for oid in current:
        if oid in state:
            first_seen = state[oid].get("first_seen")
            d = current[oid].to_dict()
            d["first_seen"] = first_seen
            state[oid] = d

    # --- Gjenopprettede brudd ---
    for oid in cleared_ids:
        old = state.pop(oid)
        dur = _duration_min(old.get("start_ms"), old.get("first_seen"))
        store.log_event("END", old, duration_min=dur)
        if should_notify(bool(old.get("planned"))):
            # Bygg et lettvekts Outage-lignende objekt for meldingen
            from models import Outage
            o = Outage(**{k: old.get(k) for k in Outage.__dataclass_fields__})
            slack.notify_restored(o, dur)

    store.save_state(state)

    print(f"Kjøring ferdig: {len(current)} aktive brudd, "
          f"{len(new_ids)} nye, {len(cleared_ids)} gjenopprettet.")


if __name__ == "__main__":
    main()
