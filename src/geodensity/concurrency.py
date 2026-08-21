"""Reconstrução da concorrência instantânea (veículos simultâneos) por
arquivo, via sweep-line sobre o intervalo [primeira, última] amostra de
cada veículo, discretizado a 1 Hz.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .parser import parse_vehicle_line


@dataclass
class FileStats:
    n_vehicles: int
    n_malformed: int
    duration_s: float
    avg_concurrency: float
    boundary_points: list[tuple[float, float]] = field(repr=False)


def compute_file_stats(path: Path) -> FileStats:
    events: dict[int, int] = {}
    boundary_points: list[tuple[float, float]] = []
    n_vehicles = 0
    n_malformed = 0
    max_tick = 0

    with open(path, "r", encoding="utf-8") as f:
        next(f)  # header
        for line in f:
            if not line.strip():
                continue
            try:
                span = parse_vehicle_line(line)
            except (ValueError, IndexError):
                # O πNEUMA tem linhas ocasionalmente corrompidas (ex: duas
                # trajetórias fundidas sem separador). Descartamos a linha
                # em vez de abortar o arquivo inteiro.
                n_malformed += 1
                continue
            n_vehicles += 1

            t0 = int(span.first_time)
            t1 = int(span.last_time)
            events[t0] = events.get(t0, 0) + 1
            events[t1 + 1] = events.get(t1 + 1, 0) - 1
            max_tick = max(max_tick, t1)

            boundary_points.append((span.first_lat, span.first_lon))
            boundary_points.append((span.last_lat, span.last_lon))

    duration_ticks = max_tick + 1  # ticks 0..max_tick, ambos inclusive
    delta = np.zeros(duration_ticks + 1)
    for tick, d in events.items():
        delta[tick] += d

    concurrency = np.cumsum(delta[:duration_ticks])
    avg_concurrency = float(concurrency.mean()) if duration_ticks > 0 else 0.0

    return FileStats(
        n_vehicles=n_vehicles,
        n_malformed=n_malformed,
        duration_s=float(duration_ticks),
        avg_concurrency=avg_concurrency,
        boundary_points=boundary_points,
    )
