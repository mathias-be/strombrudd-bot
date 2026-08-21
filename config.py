"""
Konfigurasjon for strømbrudd-boten.

Alt som er greit å justere samles her. Hemmeligheter (Slack-webhook)
leses fra miljøvariabler, ikke fra denne fila.
"""
import os

# --- Kommuner vi overvåker (offisielle kommunenummer fra 2024) ---
TARGET_KOMMUNER = {
    "3107": "Fredrikstad",
    "3110": "Hvaler",
    "3116": "Råde",
}

# --- Slack ---
# Sett som GitHub Actions secret / miljøvariabel: SLACK_WEBHOOK_URL
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "").strip()

# Skal boten også varsle om PLANLAGTE strømstanser?
# Standard: nei – vi varsler bare faktiske (uplanlagte) brudd.
# Planlagte stanser LOGGES uansett, så statistikken din blir komplett.
NOTIFY_PLANNED = os.environ.get("NOTIFY_PLANNED", "false").lower() == "true"

# --- Tidssone for visning i Slack ---
TIMEZONE = "Europe/Oslo"

# --- Datafiler (lagres i repoet av GitHub Actions) ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
STATE_FILE = os.path.join(DATA_DIR, "state.json")        # aktive brudd akkurat nå (for dedupe)
EVENTS_CSV = os.path.join(DATA_DIR, "events.csv")        # historikk: ett rad per START/END
GEOCODE_CACHE = os.path.join(DATA_DIR, "geocode_cache.json")  # koordinat -> kommune (sparer API-kall)

# --- Nettverk ---
HTTP_TIMEOUT = 25  # sekunder
USER_AGENT = "strombrudd-bot/1.0 (+https://github.com/)"
