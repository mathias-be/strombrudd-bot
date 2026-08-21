"""
Datakilde: Elvia.
Dekker Råde og Onsøy-delen av Fredrikstad i vårt område.

STATUS: IKKE FERDIG ENNÅ.
Elvias strømbruddskart (strombruddskart.elvia.no) er en JavaScript-app
som henter data fra et API vi ennå ikke har fanget. Endepunktet må
avdekkes ved å inspisere nettverkskallene i nettleseren (DevTools ->
Network, eller la Claude sniffe det via Chrome-verktøyet).

Når endepunktet er kjent, fylles fetch() ut på samme måte som
norgesnett.py: hent data -> for hvert brudd, slå opp kommune fra
koordinat -> behold Fredrikstad/Hvaler/Råde -> returner Outage-objekter.

Inntil da returnerer denne kilden en tom liste, slik at resten av boten
fungerer på Norgesnett-data alene.
"""
from typing import List

from models import Outage

SOURCE = "Elvia"

# TODO: fyll inn når API-endepunktet er fanget.
# ELVIA_API_URL = "https://.../outages"


def fetch() -> List[Outage]:
    # Ikke implementert ennå – se modulnotatet over.
    return []
