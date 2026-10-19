"""Tiling H3 e adjacência de tiles (Seção 2.1 do artigo-base).

Réplica a derivação do artigo para o limiar de distância em saltos θ:
divisão inteira entre o alcance de comunicação e o comprimento médio de
aresta do hexágono H3 na resolução escolhida (o artigo usa esse
comprimento de aresta como proxy da distância entre tiles adjacentes;
replicamos a mesma definição operacional aqui, não uma distância
centro-a-centro medida à parte, para reproduzir fielmente θ=1 na
resolução 11 relatado no artigo).
"""

from __future__ import annotations

import h3

RESOLUTION = 11
CONNECTION_RANGE_M = 50.0


def hop_threshold(resolution: int = RESOLUTION, connection_range_m: float = CONNECTION_RANGE_M) -> int:
    edge_length_m = h3.average_hexagon_edge_length(resolution, unit="m")
    return int(connection_range_m // edge_length_m)


def occupied_edges(cells: set[str], theta: int) -> list[tuple[str, str]]:
    """Arestas (Ti, Tj) do grafo geotemporal em um instante: pares de
    tiles ocupados com distância em saltos <= theta (Definição 1)."""
    edges = []
    seen: set[tuple[str, str]] = set()
    for cell in cells:
        for neighbor in h3.grid_disk(cell, theta):
            if neighbor == cell or neighbor not in cells:
                continue
            key = (cell, neighbor) if cell < neighbor else (neighbor, cell)
            if key not in seen:
                seen.add(key)
                edges.append(key)
    return edges
