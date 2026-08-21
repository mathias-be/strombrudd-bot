"""
Sender meldinger til Slack via en Incoming Webhook.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from config import SLACK_WEBHOOK_URL, TIMEZONE, HTTP_TIMEOUT, USER_AGENT
from models import Outage

_TZ = ZoneInfo(TIMEZONE)


def _fmt_time(ms):
    if not ms:
        return "ukjent"
    try:
        dt = datetime.fromtimestamp(ms / 1000, tz=_TZ)
        return dt.strftime("%d.%m %H:%M")
    except (ValueError, OSError, OverflowError):
        return "ukjent"


def post(text: str, blocks=None) -> bool:
    """Sender en melding. Returnerer True ved suksess."""
    if not SLACK_WEBHOOK_URL:
        print("[ADVARSEL] SLACK_WEBHOOK_URL er ikke satt – hopper over Slack.")
        print("  Melding som ville blitt sendt:\n" + text)
        return False
    payload = {"text": text}
    if blocks:
        payload["blocks"] = blocks
    try:
        r = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            headers={"User-Agent": USER_AGENT},
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[FEIL] Klarte ikke sende til Slack: {e}")
        return False


def notify_new_outage(o: Outage) -> bool:
    tittel = "⚡ Strømbrudd" if not o.planned else "🔧 Planlagt strømstans"
    kunder = f"{o.customers} kunder" if o.customers is not None else "ukjent antall kunder"
    linjer = [
        f"*{tittel} – {o.kommune}*",
        f"📍 {o.area}   ·   👥 {kunder}",
        f"🕐 Start: {_fmt_time(o.start_ms)}   ·   Forventet tilbake: {_fmt_time(o.end_ms)}",
    ]
    if o.cause:
        linjer.append(f"ℹ️ {o.cause}")
    linjer.append(f"_Kilde: {o.source}_")
    text = "\n".join(linjer)
    return post(text)


def notify_restored(o: Outage, duration_min) -> bool:
    varighet = f"{duration_min} min" if duration_min is not None else "ukjent varighet"
    text = (
        f"✅ *Strøm tilbake – {o.kommune}*\n"
        f"📍 {o.area}   ·   ⏱️ Varte ca. {varighet}\n"
        f"_Kilde: {o.source}_"
    )
    return post(text)
