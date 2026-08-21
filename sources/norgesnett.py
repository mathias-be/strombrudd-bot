"""
Datakilde: Norgesnett (del av Glitre Nett).
Dekker Fredrikstad (unntatt Onsøy) og Hvaler i vårt område.

Data hentes fra ArcGIS-tjenesten som ligger bak Norgesnetts offentlige
strømstans-kart (norgesnett.no/stromstans/). Lagene gir hvert brudd som
et punkt; vi slår opp kommune fra koordinatet og beholder bare
Fredrikstad / Hvaler / Råde.

Bekreftede felt i tjenesten:
  REFNR, SEKUNDÆRSTASJON, AVGANG, CNT (antall kunder), STATUS,
  BESKRIVELSE, FRA_DATO (epoch ms), TIL_DATO (epoch ms),
  LOGGTYPE ("Planlagt ..." = planlagt), STROMSTANSID (unik id)
"""
from typing import List

import requests

from config import HTTP_TIMEOUT, USER_AGENT, TARGET_KOMMUNER
from geocode import kommune_for_point
from models import Outage

SOURCE = "Norgesnett"

# Lag som viser pågående/påbegynte strømstanser (fra den offentlige web-mappen).
# Vi spør begge og deduperer på STROMSTANSID.
LAYER_URLS = [
    "https://utility.arcgis.com/usrsvcs/servers/d76865927ade4b598be0004b14c5bc93/rest/services/DRS/Stromstans_public/MapServer/1",
    "https://utility.arcgis.com/usrsvcs/servers/56796713bb044a88b5508fe332dba65d/rest/services/DRS/Stromstans_public/MapServer/3",
]


def _query_layer(url: str) -> list:
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "json",
    }
    r = requests.get(
        url + "/query",
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=HTTP_TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"ArcGIS-feil: {data['error']}")
    return data.get("features", [])


def fetch() -> List[Outage]:
    seen_ids = set()
    outages: List[Outage] = []

    for url in LAYER_URLS:
        try:
            features = _query_layer(url)
        except requests.RequestException as e:
            print(f"[ADVARSEL] Norgesnett-lag utilgjengelig: {e}")
            continue

        for feat in features:
            attrs = feat.get("attributes", {})
            geom = feat.get("geometry") or {}
            lon = geom.get("x")
            lat = geom.get("y")

            stroms_id = attrs.get("STROMSTANSID") or attrs.get("REFNR") or attrs.get("OBJECTID")
            uid = f"norgesnett:{stroms_id}"
            if uid in seen_ids:
                continue

            # Kommunefilter via koordinat
            kommunenr, kommunenavn = kommune_for_point(lat, lon)
            if kommunenr not in TARGET_KOMMUNER:
                continue

            seen_ids.add(uid)

            loggtype = (attrs.get("LOGGTYPE") or "").strip()
            planned = loggtype.lower().startswith("planlagt")

            station = (attrs.get("SEKUNDÆRSTASJON") or "").strip()
            avgang = (attrs.get("AVGANG") or "").strip()
            area = " ".join(p for p in (station, avgang) if p) or "Ukjent sted"

            cnt = attrs.get("CNT")
            try:
                customers = int(cnt) if cnt is not None else None
            except (TypeError, ValueError):
                customers = None

            outages.append(Outage(
                id=uid,
                source=SOURCE,
                kommune=TARGET_KOMMUNER[kommunenr],
                kommunenr=kommunenr,
                area=area,
                customers=customers,
                planned=planned,
                status=attrs.get("STATUS"),
                cause=(attrs.get("BESKRIVELSE") or None),
                start_ms=attrs.get("FRA_DATO"),
                end_ms=attrs.get("TIL_DATO"),
                lat=lat,
                lon=lon,
            ))

    return outages
