# Lista de Tarefas

Acompanhamento do projeto *Estrutura Geográfica e Comportamento Humano como Determinantes de Redes Veiculares* (`plan.md`). Última atualização: 2026-08-26.

Legenda: `[x]` concluído · `[ ]` a fazer · `[~]` em andamento · `[-]` opcional / backlog

---

## Fase 1 — Fundamentação e replicação — ✅ concluída

- [x] Revisão de literatura: mobilidade humana estruturada (González, Song, Schneider, Barbosa) e grafos espaço-temporais em redes veiculares.
- [x] Formalização do grafo geotemporal como abordagem region-centric frente às abordagens node-centric.
- [x] Levantamento do perfil de densidade veicular das 10 regiões do πNEUMA (160 arquivos, 46 GB), a 1 Hz, com área por convex hull em UTM 34N.
- [x] Diagnóstico de duração real dos arquivos (600–1100 s, não os 1800 s nominais) e uso da duração observada como denominador.
- [x] Seleção das regiões de estudo: **d7** (alta densidade, mediana 1780,8 veíc/km²) e **d1** (baixa densidade, 676,4 veíc/km²).
- [x] Replicação do pipeline de construção do grafo geotemporal (`src/geograph/`): H3 res. 11, θ = 1, 1 Hz, 32 arquivos de d1+d7.
- [x] Persistência apenas de $O_t$ em Parquet particionado (`processed/geograph/`), grafo derivado sob demanda — 6,3 M amostras reduzidas a 1,2 MB.
- [x] Checagem de sanidade automática (reconstrução de $\mathcal{G}(t)$ a partir do Parquet).
- [x] `fase1.md` escrito e revisado.

## Fase 2 — Definição operacional das métricas — ✅ concluída

- [x] Definição das métricas estruturais no grafo simples: M1 ocupação, M2 densidade por tile, M3 grau agregado em dois níveis.
- [x] Definição das métricas no grafo de alcançabilidade: M4 alcance por tile-fonte (primária), M5 $SR_\delta$ (secundária); Eq. 4 deliberadamente fora das primárias.
- [x] Definição das métricas de estabilidade: S1 CV de magnitude, S2 Spearman + Wasserstein-1, S3 discriminabilidade $\Lambda$ com teste de permutação.
- [x] Definição do conjunto de comparação de tiles (limiar de atividade ≥ 10%, interseção entre observações).
- [x] Justificativa do alcance físico $\rho = 50$ m em três camadas (empírica NLSS urbana, goodput do artigo, sanity check de densidade).
- [x] Adoção do critério de conexão geométrico existencial, com bracketing $\theta_{eff}-1$ (variante do artigo-base).
- [x] Fundamentação de $\Delta t = 1$ s (duração de contato $\gg \Delta t$) e de $\delta_{min}$ como tempo de travessia em conectividade perfeita.
- [x] Grade de $\delta$ revisada: {5, 10, 15, 20, 30, 45, 60, 120, 300} s, com $\delta^* = 30$ s e dois regimes semânticos.
- [x] Escolha das resoluções H3: {11, 12}, com análise de viabilidade (res. 10 rejeitada por granularidade).
- [x] `fase2.md` escrito e revisado (2 rodadas de discussão incorporadas).

---

## Fase 3 — Construção dos grafos e coleta de dados

### 3.1 Infraestrutura de código

- [ ] Adicionar `shapely` às dependências (`pyproject.toml`).
- [ ] Implementar tabela de distância mínima por anel H3 × resolução (`h3.polygon_to_cells` + distância entre polígonos), pré-computada por resolução.
- [ ] Derivar $\theta_{eff}(res) = \max\{k : \mathrm{dist}_{\min}(k) \leq \rho\}$ da tabela; **verificar empiricamente a fronteira do anel 2 na res. 11** (49,6 m vs. 50 m).
- [ ] Implementar construção de $E_t$ pelo critério geométrico (ocupação + distância mínima ≤ $\rho$), parametrizada por $\theta$.
- [ ] Manter a variante de replicação (proxy de aresta, $\theta=1$) como caminho alternativo de execução.
- [ ] Implementar cálculo de alcançabilidade via perfis de tempo de chegada mais cedo por fonte (curva completa $r_\delta$ sem refazer o custo por $\delta$).
- [ ] Validar contra a checagem de sanidade da Fase 1 (d7, 2018-10-29, janela 09:00–09:30, t = 938 s).

### 3.2 Construção dos grafos

- [ ] Estender o pipeline de `occupied_tiles` para a res. 12 (~7× tiles).
- [ ] Construir as configurações completas do plano: 2 regiões × 2 resoluções × 4 datas × 4 janelas = **64 configurações**.
- [ ] Medir e registrar custo computacional (tempo, memória, tamanho em disco) por configuração — antecipando limitações de infraestrutura.
- [ ] Decidir, com base no custo medido, se o bracketing $\theta_{eff}$ vs. $\theta_{eff}-1$ roda em todas as configurações ou só em subconjunto.

### 3.3 Cálculo das métricas

- [ ] M1 ocupação, M2 densidade por tile, M3 grau (a/b) para as 64 configurações.
- [ ] M4 $r_\delta(u)$ na grade completa de $\delta$; M5 $SR_\delta$ por observação.
- [ ] S1 (CV por região) e S2 (Spearman + Wasserstein-1 par-a-par).
- [ ] Persistir as métricas brutas em `results/` (formato tabular por observação × tile × $\delta$).
- [ ] Definir/implementar o teste de permutação de $\Lambda$ (aplicação fica na Fase 4).

---

## Fase 4 — Análise estatística

- [ ] Comparar métricas entre regiões (densidade × granularidade × alcançabilidade).
- [ ] Rodar S3 ($\Lambda$) com teste de permutação; reportar p-valores por família de métricas e por nível (grafo simples × alcançabilidade).
- [ ] Verificar sensibilidade ao limiar de atividade (10%) do conjunto $\mathcal{V}^*$.
- [ ] Comparar resultados entre resoluções 11 e 12 (robustez à granularidade espacial).
- [ ] Interpretar à luz da pergunta central: geografia/comportamento domina o instante observado?
- [ ] Produzir gráficos e tabelas dos resultados preliminares.

---

## Opcional / backlog

- [-] Estimativa empírica de $\delta_{gap}$ (mediana de fechamento de lacuna) — exige reprocessar CSVs preservando `track_id`.
- [-] Sensibilidade de $\rho \in \{25, 100\}$ m em configuração reduzida (1 data × 1 janela por região).
- [-] Análise secundária com o *time-aggregated reachability error* (Eq. 4) replicando a seleção de fontes do artigo-base.
- [-] Investigar refinamento da derivação de $\theta$ com distância centro-a-centro real (documentado como limitação na Fase 1).

---

## Notas de decisão

Todas as decisões metodológicas fechadas estão registradas em `fase2.md` (Seções 1.5 e 4). Resumo:

| Parâmetro | Valor |
| --- | --- |
| Regiões | d7 (alta densidade) e d1 (baixa densidade) |
| Alcance físico $\rho$ | 50 m |
| Critério de conexão | Geométrico existencial ($\mathrm{dist}_{\min} \leq \rho$) + bracketing $\theta_{eff}-1$ |
| Resoluções H3 | 11 e 12 |
| Granularidade temporal $\Delta t$ | 1 s |
| Grade de $\delta$ | {5, 10, 15, 20, 30, 45, 60, 120, 300} s (primário: 30 s) |
| Limiar de atividade dos tiles | ≥ 10% dos instantes |
