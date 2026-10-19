"""Constrói o grafo geotemporal (Fase 1, item 3): para cada arquivo do
πNEUMA das regiões selecionadas (d1 baixa densidade, d7 alta
densidade), reamostra as trajetórias a 1Hz, mapeia cada amostra para
um tile H3 e persiste o conjunto de tiles ocupados por instante O_t
(Eq. 1 do artigo-base) em Parquet.

O grafo em si (vértices = tiles ocupados, arestas = pares a distância
em saltos <= theta) não é persistido: é derivado sob demanda de O_t via
`geograph.tiling.occupied_edges`, evitando armazenar uma explosão
combinatória de arestas que é, de qualquer forma, recalculável em
O(|O_t|) a partir do tile ocupado.
"""

from __future__ import annotations

import time
from pathlib import Path

import duckdb
import h3
import pandas as pd

from geodensity.parser import parse_filename

from .tiling import RESOLUTION, hop_threshold, occupied_edges
from .trajectory import parse_vehicle_trajectory, resample_1hz

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT / "dataset"
PROCESSED_DIR = REPO_ROOT / "processed" / "geograph"

REGIONS = ("d1", "d7")


def process_file(path: Path, resolution: int = RESOLUTION) -> tuple[pd.DataFrame, int]:
    """Retorna (df[t, h3, track_id], n_malformed) com a trajetória do
    arquivo inteiro reamostrada a 1Hz e mapeada para tiles H3."""
    rows: list[tuple[int, str, str]] = []
    n_malformed = 0

    with open(path, "r", encoding="utf-8") as f:
        next(f)  # header
        for line in f:
            if not line.strip():
                continue
            try:
                track_id, samples = parse_vehicle_trajectory(line)
            except (ValueError, IndexError):
                n_malformed += 1
                continue
            for t, lat, lon in resample_1hz(samples):
                cell = h3.latlng_to_cell(lat, lon, resolution)
                rows.append((t, cell, track_id))

    df = pd.DataFrame(rows, columns=["t", "h3", "track_id"])
    return df, n_malformed


def run(dataset_dir: Path = DATASET_DIR, processed_dir: Path = PROCESSED_DIR) -> None:
    files = sorted(
        p for p in dataset_dir.glob("*.csv") if parse_filename(p)[1] in REGIONS
    )
    if not files:
        raise SystemExit(f"nenhum CSV de {REGIONS} encontrado em {dataset_dir}")

    theta = hop_threshold()
    print(f"resolução H3={RESOLUTION}  theta(hop)={theta}\n")

    t_start = time.monotonic()
    for i, path in enumerate(files, 1):
        date, region, window = parse_filename(path)
        t0 = time.monotonic()
        df, n_malformed = process_file(path)

        out_dir = processed_dir / f"region={region}" / f"date={date}" / f"window={window}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "occupied_tiles.parquet"

        duckdb.sql(f"""
            COPY (
                SELECT t, h3, count(DISTINCT track_id) AS n_vehicles
                FROM df
                GROUP BY t, h3
                ORDER BY t, h3
            ) TO '{out_path.as_posix()}' (FORMAT PARQUET)
        """)

        dt = time.monotonic() - t0
        malformed_note = f"  malformed={n_malformed}" if n_malformed else ""
        print(
            f"[{i}/{len(files)}] {path.name}  samples={len(df)}{malformed_note}  ({dt:.1f}s)",
            flush=True,
        )

    print(f"\nProcessamento dos {len(files)} arquivos: {time.monotonic() - t_start:.0f}s")
    print(f"Saída: {processed_dir}\n")

    _sanity_check(processed_dir, theta)


def _sanity_check(processed_dir: Path, theta: int) -> None:
    """Valida a construção do grafo geotemporal G(t) num instante de
    amostra: carrega O_t de um arquivo processado e deriva as arestas
    (Definição 1), reportando |V_t| e |E_t| como checagem de sanidade."""
    glob_pattern = (processed_dir / "**" / "*.parquet").as_posix()
    sample = duckdb.sql(f"""
        SELECT region, "date", "window", t
        FROM read_parquet('{glob_pattern}', hive_partitioning=true)
        GROUP BY region, "date", "window", t
        ORDER BY count(*) DESC
        LIMIT 1
    """).fetchone()
    if sample is None:
        return
    region, date, window, t = sample

    cells = duckdb.sql(f"""
        SELECT h3
        FROM read_parquet('{glob_pattern}', hive_partitioning=true)
        WHERE region = '{region}' AND "date" = '{date}' AND "window" = '{window}' AND t = {t}
    """).fetchall()
    occupied = {row[0] for row in cells}
    edges = occupied_edges(occupied, theta)

    print("Checagem de sanidade — G(t) reconstruído de O_t:")
    print(f"  {region}  {date}  {window}  t={t}s")
    print(f"  |V_t| (tiles ocupados) = {len(occupied)}")
    print(f"  |E_t| (arestas, theta={theta}) = {len(edges)}")
