"""Área de uma região via convex hull dos pontos de entrada/saída dos
veículos, projetados para UTM 34N (zona correta para Atenas) antes do
cálculo de área.
"""

from __future__ import annotations

import numpy as np
from pyproj import Transformer
from scipy.spatial import ConvexHull

_TO_UTM34N = Transformer.from_crs("EPSG:4326", "EPSG:32634", always_xy=True)


def hull_area_km2(points_lat_lon: list[tuple[float, float]]) -> float:
    if len(points_lat_lon) < 3:
        raise ValueError("são necessários ao menos 3 pontos para um convex hull")

    lats = [p[0] for p in points_lat_lon]
    lons = [p[1] for p in points_lat_lon]
    x, y = _TO_UTM34N.transform(lons, lats)
    xy = np.column_stack([x, y])

    hull = ConvexHull(xy)
    return hull.volume / 1e6  # ConvexHull.volume em 2D = área, em m^2
