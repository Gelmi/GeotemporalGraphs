"""Visualização animada (Plotly) da construção do grafo geotemporal:
para cada segundo t de um arquivo do πNEUMA, mostra os veículos no
mapa real (pontos) e, embaixo, os tiles H3 ocupados naquele instante
(Definição 1 / Eq. 1 do artigo-base) como contorno.

Uso: PYTHONPATH=src uv run python -m geograph.animate --region d1 --date 20181101 --window 0830_0900
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import h3
import plotly.graph_objects as go

from .tiling import RESOLUTION
from .trajectory import parse_vehicle_trajectory, resample_1hz

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT / "dataset"
RESULTS_DIR = REPO_ROOT / "results"


def load_animation_data(
    path: Path, resolution: int
) -> tuple[dict[int, list[tuple[float, float]]], dict[int, set[str]], tuple[float, float]]:
    """Retorna (pontos de veículo por t, tiles H3 ocupados por t, centro do mapa)."""
    points_by_t: dict[int, list[tuple[float, float]]] = defaultdict(list)
    cells_by_t: dict[int, set[str]] = defaultdict(set)
    lat_sum = lon_sum = 0.0
    n = 0

    with open(path, "r", encoding="utf-8") as f:
        next(f)  # header
        for line in f:
            if not line.strip():
                continue
            try:
                _, samples = parse_vehicle_trajectory(line)
            except (ValueError, IndexError):
                continue
            for t, lat, lon in resample_1hz(samples):
                points_by_t[t].append((lat, lon))
                cells_by_t[t].add(h3.latlng_to_cell(lat, lon, resolution))
                lat_sum += lat
                lon_sum += lon
                n += 1

    center = (lat_sum / n, lon_sum / n)
    return points_by_t, cells_by_t, center


def _hexagon_outline_coords(
    cells: set[str], boundary_lookup: dict[str, tuple[tuple[float, float], ...]]
) -> tuple[list[float | None], list[float | None]]:
    """Concatena o contorno de vários hexágonos em uma única trace de
    linhas, separando cada polígono com (None, None) — a técnica padrão
    do Plotly para desenhar múltiplos polígonos numa Scattermapbox."""
    lats: list[float | None] = []
    lons: list[float | None] = []
    for cell in cells:
        boundary = boundary_lookup[cell]
        for lat, lon in boundary:
            lats.append(lat)
            lons.append(lon)
        lats.append(boundary[0][0])
        lons.append(boundary[0][1])
        lats.append(None)
        lons.append(None)
    return lats, lons


def build_figure(
    region: str,
    date: str,
    window: str,
    resolution: int = RESOLUTION,
    dataset_dir: Path = DATASET_DIR,
    frame_duration_ms: int = 200,
    map_style: str = "carto-positron",
) -> go.Figure:
    path = dataset_dir / f"{date}_{region}_{window}.csv"
    if not path.exists():
        raise SystemExit(f"arquivo não encontrado: {path}")

    points_by_t, cells_by_t, center = load_animation_data(path, resolution)
    ts = sorted(points_by_t.keys())

    all_cells = set().union(*cells_by_t.values())
    boundary_lookup = {cell: h3.cell_to_boundary(cell) for cell in all_cells}

    def title(t: int) -> str:
        return f"{region}  {date}  {window} — t={t}s"

    t0 = ts[0]
    lat0, lon0 = zip(*points_by_t[t0])
    hexlat0, hexlon0 = _hexagon_outline_coords(cells_by_t[t0], boundary_lookup)

    fig = go.Figure()
    # Hexágonos primeiro (fica embaixo), veículos por cima, na mesma trace order = z-order.
    fig.add_trace(
        go.Scattermap(
            lat=hexlat0, lon=hexlon0, mode="lines",
            line=dict(width=1.5, color="#d62728"), name="tiles H3 ocupados",
        )
    )
    fig.add_trace(
        go.Scattermap(
            lat=list(lat0), lon=list(lon0), mode="markers",
            marker=dict(size=6, color="#1f77b4"), name="veículos",
        )
    )

    frames = []
    for t in ts:
        lats, lons = zip(*points_by_t[t])
        hexlat, hexlon = _hexagon_outline_coords(cells_by_t[t], boundary_lookup)
        frames.append(
            go.Frame(
                name=str(t),
                traces=[0, 1],
                data=[
                    go.Scattermap(lat=hexlat, lon=hexlon),
                    go.Scattermap(lat=list(lats), lon=list(lons)),
                ],
                layout=go.Layout(title=dict(text=title(t))),
            )
        )
    fig.frames = frames

    map_settings = dict(style=map_style, center=dict(lat=center[0], lon=center[1]), zoom=16)
    fig.update_layout(
        map=map_settings,
        title=dict(text=title(t0)),
        height=900,
        margin=dict(l=0, r=0, t=70, b=0),
        updatemenus=[
            dict(
                type="buttons", showactive=False, x=0, y=1.06, xanchor="left",
                buttons=[
                    dict(
                        label="▶ Play", method="animate",
                        args=[None, dict(frame=dict(duration=frame_duration_ms, redraw=True), fromcurrent=True, transition=dict(duration=0))],
                    ),
                    dict(
                        label="⏸ Pause", method="animate",
                        args=[[None], dict(mode="immediate", frame=dict(duration=0, redraw=False))],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                active=0,
                x=0, y=0, len=1.0,
                currentvalue=dict(prefix="t = ", suffix="s"),
                steps=[
                    dict(
                        method="animate", label=str(t),
                        args=[[str(t)], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))],
                    )
                    for t in ts
                ],
            )
        ],
    )
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="d1")
    parser.add_argument("--date", default="20181101")
    parser.add_argument("--window", default="0830_0900")
    parser.add_argument("--resolution", type=int, default=RESOLUTION)
    parser.add_argument("--frame-ms", type=int, default=200, help="duração de cada frame no play (ms)")
    parser.add_argument(
        "--style", default="carto-positron",
        choices=["carto-positron", "carto-darkmatter", "open-street-map", "white-bg"],
        help="estilo do mapa base (open-street-map exige Referer e não funciona em HTML local file://)",
    )
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    fig = build_figure(
        args.region, args.date, args.window, args.resolution,
        frame_duration_ms=args.frame_ms, map_style=args.style,
    )

    out = Path(args.out) if args.out else RESULTS_DIR / f"geograph_{args.region}_{args.date}_{args.window}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(out, include_plotlyjs=True)
    print(f"Salvo em {out}  ({out.stat().st_size / 1e6:.1f} MB, {len(fig.frames)} frames)")


if __name__ == "__main__":
    main()
