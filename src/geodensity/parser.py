"""Parsing das linhas do formato de trajetórias do πNEUMA.

Cada linha do CSV representa um veículo, com 4 campos fixos
(track_id, type, traveled_d, avg_speed) seguidos por grupos repetidos de
6 campos por amostra (lat, lon, speed, lon_acc, lat_acc, time), a ~25 Hz.
Extraímos apenas a primeira e a última amostra de cada veículo — o
suficiente para a densidade de concorrência instantânea (sweep-line) e
para o convex hull da área da região.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

FILENAME_RE = re.compile(r"^(?P<date>\d{8})_(?P<region>d\d+)_(?P<window>\d{4}_\d{4})\.csv$")


@dataclass(frozen=True)
class VehicleSpan:
    track_id: str
    vtype: str
    first_lat: float
    first_lon: float
    first_time: float
    last_lat: float
    last_lon: float
    last_time: float


def parse_vehicle_line(line: str) -> VehicleSpan:
    line = line.rstrip("\n")

    # Primeiros 10 campos (track_id..time da 1a amostra) — split limitado
    # a partir do início, custo independente do comprimento da linha.
    head = line.split(";", 10)
    first_time = float(head[9])

    # Últimos campos (última amostra) — rsplit limitado a partir do fim.
    # O dataset tem um separador ';' sobrando no fim da linha, produzindo
    # um campo vazio à direita que precisa ser descartado.
    tail = line.rsplit(";", 7)[1:]
    if tail and tail[-1].strip() == "":
        tail = tail[:-1]

    return VehicleSpan(
        track_id=head[0].strip(),
        vtype=head[1].strip(),
        first_lat=float(head[4]),
        first_lon=float(head[5]),
        first_time=first_time,
        last_lat=float(tail[-6]),
        last_lon=float(tail[-5]),
        last_time=float(tail[-1]),
    )


def parse_filename(path: Path) -> tuple[str, str, str]:
    match = FILENAME_RE.match(path.name)
    if not match:
        raise ValueError(f"nome de arquivo inesperado no dataset πNEUMA: {path.name}")
    return match["date"], match["region"], match["window"]
