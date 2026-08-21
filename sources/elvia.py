"""
Datakilde: Elvia.
Dekker Råde og Onsøy-delen av Fredrikstad i vårt område.

Data hentes fra ArcGIS-tjenesten bak Elvias offentlige strømbruddskart
(strombruddskart.elvia.no). I motsetning til Norgesnett inneholder Elvias
data kommunenavn og -nummer direkte, så vi kan filtrere rett på
kommunenummer uten å slå opp koordinater.

Bekreftede felt i tjenesten:
  antallkunder (int), beskrivelse, utkoblingstart (epoch ms),
  utkoblingslutt (epoch ms), strombruddoppdaget, avbruddstype
  ("Planned"/"Unplanned"), statusavbrudd, nettstasjon, poststed,
  postnummer, kommune, kommunenummer, hash (stabil id), OBJECTID
"""
from typing import List

import requests

from config import HTTP_TIMEOUT, USER_AGENT, TARGET_KOMMUNER
from models import Outage

SOURCE = "Elvia"

# Lag 1 = polygoner (samme data kartet bruker). Lag 0 = punkter.
LAYER_URL = (
    "https://services-eu1.arcgis.com/AcdYbPzrkOfBOQDL/arcgis/rest/services/"
    "avbrudd2_offentlig_visning/FeatureServer/1"
)


def _centroid(geom):
    """Grovt midtpunkt (lon, lat) fra polygon-ringene."""
    if not geom:
        return None, None
    rings = geom.get("rings")
    if not rings or not rings[0]:
        return None, None
    pts = rings[0]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def fetch() -> List[Outage]:
    # Filtrer på server-siden til kommunene vi følger
    numre = "','".join(sorted(TARGET_KOMMUNER.keys()))
    where = f"kommunenummer IN ('{numre}')"

    params = {
        "f": "json",
        "where": where,
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "4326",
    }
    r = requests.get(
        LAYER_URL + "/query",
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=HTTP_TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"ArcGIS-feil (Elvia): {data['error']}")

    outages: List[Outage] = []
    for feat in data.get("features", []):
        attrs = feat.get("attributes", {})

        kommunenr = str(attrs.get("kommunenummer") or "").strip()
        if kommunenr not in TARGET_KOMMUNER:   # ekstra sikkerhetsfilter
            continue

        # Stabil id: bruk 'hash' hvis den finnes, ellers OBJECTID
        raw_id = attrs.get("hash") or attrs.get("OBJECTID")
        uid = f"elvia:{raw_id}"

        planned = str(attrs.get("avbruddstype") or "").strip().lower() == "planned"

        station = (attrs.get("nettstasjon") or "").strip()
        poststed = (attrs.get("poststed") or "").strip()
        area = " – ".join(p for p in (station, poststed) if p) or "Ukjent sted"

        cnt = attrs.get("antallkunder")
        try:
            customers = int(cnt) if cnt is not None else None
        except (TypeError, ValueError):
            customers = None

        lon, lat = _centroid(feat.get("geometry"))

        outages.append(Outage(
            id=uid,
            source=SOURCE,
            kommune=(attrs.get("kommune") or TARGET_KOMMUNER[kommunenr]),
            kommunenr=kommunenr,
            area=area,
            customers=customers,
            planned=planned,
            status=attrs.get("statusavbrudd"),
            cause=(attrs.get("beskrivelse") or None),
            start_ms=attrs.get("utkoblingstart"),
            end_ms=attrs.get("utkoblingslutt"),
            lat=lat,
            lon=lon,
        ))

    return outages
