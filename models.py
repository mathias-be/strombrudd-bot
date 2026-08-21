"""
Felles datamodell for et strømbrudd, uavhengig av hvilket nettselskap
det kom fra. Alle kilder (Norgesnett, Elvia, ...) normaliserer til denne.
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Outage:
    id: str                      # unik, f.eks. "norgesnett:V-70908-1"
    source: str                  # "Norgesnett" | "Elvia"
    kommune: str                 # "Fredrikstad"
    kommunenr: str               # "3107"
    area: str                    # menneskevennlig sted, f.eks. "NYSTUEN L7"
    customers: Optional[int]     # antall berørte kunder (kan være None)
    planned: bool                # True = planlagt stans, False = faktisk brudd
    status: Optional[str]        # selskapets statustekst
    cause: Optional[str]         # årsak/beskrivelse hvis oppgitt
    start_ms: Optional[int]      # starttidspunkt (epoch ms)
    end_ms: Optional[int]        # forventet gjenoppretting (epoch ms)
    lat: Optional[float]
    lon: Optional[float]

    def to_dict(self) -> dict:
        return asdict(self)
