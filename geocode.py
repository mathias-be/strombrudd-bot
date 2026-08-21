"""
Slår opp hvilken kommune et koordinat ligger i, via Kartverkets åpne
kommuneinfo-API (gratis, ingen nøkkel). Resultater caches på disk slik at
vi ikke spør på nytt for samme sted.
"""
import json
import os
import requests

from config import GEOCODE_CACHE, HTTP_TIMEOUT, USER_AGENT

KARTVERKET_URL = "https://api.kartverket.no/kommuneinfo/v1/punkt"


def _load_cache() -> dict:
    if os.path.exists(GEOCODE_CACHE):
        try:
            with open(GEOCODE_CACHE, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    os.makedirs(os.path.dirname(GEOCODE_CACHE), exist_ok=True)
    with open(GEOCODE_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=0)


# Cache lastes én gang per kjøring
_cache = _load_cache()


def kommune_for_point(lat: float, lon: float):
    """
    Returnerer (kommunenummer, kommunenavn) for et punkt, eller (None, None).
    Koordinater i WGS84/ETRS89 (praktisk talt identiske i Norge).
    """
    if lat is None or lon is None:
        return None, None

    # Rund av til ~11 m for effektiv caching
    key = f"{round(lat, 4)},{round(lon, 4)}"
    if key in _cache:
        c = _cache[key]
        return c.get("nr"), c.get("navn")

    try:
        r = requests.get(
            KARTVERKET_URL,
            params={"nord": lat, "ost": lon, "koordsys": 4258},
            headers={"User-Agent": USER_AGENT},
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        nr = data.get("kommunenummer")
        navn = data.get("kommunenavn")
    except (requests.RequestException, ValueError):
        # Ved feil: ikke cache, bare returner ukjent for denne runden
        return None, None

    _cache[key] = {"nr": nr, "navn": navn}
    _save_cache(_cache)
    return nr, navn
