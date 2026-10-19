"""Parsing e reamostragem de trajetórias completas do πNEUMA.

Ao contrário de `geodensity.parser` (que só precisa da primeira e
última amostra de cada veículo), a construção do grafo geotemporal
precisa da trajetória inteira, reamostrada a 1Hz, para determinar em
qual tile o veículo está a cada instante t.
"""

from __future__ import annotations

from collections.abc import Iterator


def parse_vehicle_trajectory(line: str) -> tuple[str, list[tuple[float, float, float]]]:
    """Retorna (track_id, [(t, lat, lon), ...]) na resolução nativa (~25Hz)."""
    line = line.rstrip("\n")
    parts = line.split(";")
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]

    track_id = parts[0].strip()
    sample_fields = parts[4:]  # pula track_id, type, traveled_d, avg_speed
    if len(sample_fields) % 6 != 0:
        raise ValueError(f"quantidade inesperada de campos de amostra: {len(sample_fields)}")

    samples = []
    for i in range(0, len(sample_fields), 6):
        lat = float(sample_fields[i])
        lon = float(sample_fields[i + 1])
        t = float(sample_fields[i + 5])
        samples.append((t, lat, lon))
    return track_id, samples


def resample_1hz(samples: list[tuple[float, float, float]]) -> Iterator[tuple[int, float, float]]:
    """Reduz amostras a ~25Hz para 1 por segundo inteiro, mantendo a
    primeira amostra observada em cada bucket (t, lat, lon)."""
    last_bucket = None
    for t, lat, lon in samples:
        bucket = int(t)
        if bucket != last_bucket:
            yield bucket, lat, lon
            last_bucket = bucket
