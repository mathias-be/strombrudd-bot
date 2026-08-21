"""
Datakilder for strømbrudd. Hver kilde eksponerer fetch() som returnerer
en liste med normaliserte Outage-objekter, allerede filtrert til
kommunene vi bryr oss om.
"""
from typing import List

from models import Outage
from sources import norgesnett, elvia


def fetch_all() -> List[Outage]:
    outages: List[Outage] = []
    for src in (norgesnett, elvia):
        try:
            outages.extend(src.fetch())
        except Exception as e:  # en kilde som feiler skal ikke stoppe resten
            print(f"[ADVARSEL] Kilde {src.__name__} feilet: {e}")
    return outages
