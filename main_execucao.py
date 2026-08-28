"""Executa uma simulação de referência para o pacote de eletropostos Brasil."""
from __future__ import annotations

import json
from pathlib import Path

from modelo_eletropostos import Candidate, ProjectParameters, estimate_project, select_stations


CANDIDATES = [
    Candidate("C01", 0, 860, 950, 2.0),
    Candidate("C02", 55, 810, 900, 3.5),
    Candidate("C03", 110, 760, 850, 4.0),
    Candidate("C04", 170, 700, 780, 2.8),
    Candidate("C05", 230, 640, 720, 5.0),
    Candidate("C06", 310, 590, 700, 3.0),
    Candidate("C07", 390, 540, 650, 4.8),
    Candidate("C08", 475, 500, 620, 3.7),
    Candidate("C09", 585, 450, 580, 4.2),
    Candidate("C10", 700, 410, 540, 5.5),
]


def main() -> None:
    selected = select_stations(CANDIDATES)
    results = estimate_project(selected, ProjectParameters())
    results["selected_station_codes"] = [station.code for station in selected]
    Path("resultados_brasil_simulados.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
