"""Orquestra o cálculo de densidade veicular por região (Fase 1, item 2
do plano de trabalho): processa os CSVs do πNEUMA, calcula concorrência
instantânea média por arquivo, área por região (convex hull, pooled
entre as 4 datas) e densidade (veíc/km²), salvando uma tabela bruta
(região x data x janela) e um resumo por região.
"""

from __future__ import annotations

import csv
import statistics
import time
from collections import defaultdict
from pathlib import Path

from .concurrency import compute_file_stats
from .geometry import hull_area_km2
from .parser import parse_filename

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT / "dataset"
RESULTS_DIR = REPO_ROOT / "results"

RAW_FIELDS = [
    "region", "date", "window", "n_vehicles", "n_malformed", "duration_s",
    "avg_concurrency", "area_km2", "density_veic_km2",
]
SUMMARY_FIELDS = [
    "region", "area_km2", "n_observations",
    "mean_density", "median_density", "stdev_density", "cv",
]


def run(dataset_dir: Path = DATASET_DIR, results_dir: Path = RESULTS_DIR) -> None:
    results_dir.mkdir(exist_ok=True)
    files = sorted(dataset_dir.glob("*.csv"))
    if not files:
        raise SystemExit(f"nenhum CSV encontrado em {dataset_dir}")

    per_file: list[dict] = []
    region_points: dict[str, list[tuple[float, float]]] = defaultdict(list)

    t_start = time.monotonic()
    for i, path in enumerate(files, 1):
        date, region, window = parse_filename(path)
        t0 = time.monotonic()
        stats = compute_file_stats(path)
        dt = time.monotonic() - t0
        malformed_note = f"  malformed={stats.n_malformed}" if stats.n_malformed else ""
        print(
            f"[{i}/{len(files)}] {path.name}  "
            f"n_vehicles={stats.n_vehicles}  duration={stats.duration_s:.0f}s  "
            f"avg_concurrency={stats.avg_concurrency:.1f}{malformed_note}  ({dt:.1f}s)",
            flush=True,
        )

        region_points[region].extend(stats.boundary_points)
        per_file.append({
            "region": region,
            "date": date,
            "window": window,
            "n_vehicles": stats.n_vehicles,
            "n_malformed": stats.n_malformed,
            "duration_s": stats.duration_s,
            "avg_concurrency": stats.avg_concurrency,
        })

    total_malformed = sum(row["n_malformed"] for row in per_file)
    print(f"\nProcessamento dos {len(files)} arquivos: {time.monotonic() - t_start:.0f}s")
    if total_malformed:
        print(f"Linhas malformadas descartadas no total: {total_malformed}")

    region_area_km2 = {
        region: hull_area_km2(points) for region, points in region_points.items()
    }

    raw_rows = []
    for row in per_file:
        area = region_area_km2[row["region"]]
        density = row["avg_concurrency"] / area
        raw_rows.append({**row, "area_km2": area, "density_veic_km2": density})

    raw_path = results_dir / "density_por_regiao_bruto.csv"
    _write_csv(raw_path, raw_rows, RAW_FIELDS)

    by_region: dict[str, list[float]] = defaultdict(list)
    for row in raw_rows:
        by_region[row["region"]].append(row["density_veic_km2"])

    summary_rows = []
    for region, values in by_region.items():
        mean = statistics.mean(values)
        median = statistics.median(values)
        stdev = statistics.pstdev(values)
        cv = stdev / mean if mean else float("nan")
        summary_rows.append({
            "region": region,
            "area_km2": region_area_km2[region],
            "n_observations": len(values),
            "mean_density": mean,
            "median_density": median,
            "stdev_density": stdev,
            "cv": cv,
        })
    summary_rows.sort(key=lambda r: r["median_density"], reverse=True)

    summary_path = results_dir / "density_por_regiao_resumo.csv"
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDS)

    print(f"\nTabela bruta:  {raw_path}")
    print(f"Resumo:        {summary_path}\n")
    print("Resumo (ordenado por mediana de densidade, desc):")
    for row in summary_rows:
        print(
            f"  {row['region']:>4}  mediana={row['median_density']:8.1f}  "
            f"media={row['mean_density']:8.1f}  cv={row['cv']:6.1%}  "
            f"area={row['area_km2']:.4f} km2  n={row['n_observations']}"
        )


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
