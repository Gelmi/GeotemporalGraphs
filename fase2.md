# Fase 2 — Definição Operacional das Métricas

> Fase 2 do plano de trabalho (`plan.md`): formalizar as métricas a serem usadas (densidade por tile, grau agregado do grafo geotemporal, alcançabilidade), definir a métrica de estabilidade temporal e as resoluções H3 a serem testadas. Entregável: documento de metodologia com todas as métricas formalmente definidas e justificadas.

Este documento cobre os três bullets da fase. As decisões fechadas em discussão estão registradas na Seção 1.5 e nas Seções 2.6 e 3.2; os pontos ainda em aberto estão marcados como **[PENDENTE]** e sumarizados na Seção 4.

## Notação

Segue o artigo-base [20]. Uma **observação** é uma tupla $o = (\text{região}, \text{data}, \text{janela})$ — para cada região ($d1$, baixa densidade; $d7$, alta densidade, selecionadas na Fase 1) há 16 observações (4 datas × 4 janelas de pico matinal). Cada observação tem domínio temporal $\mathcal{T}_o \subset \mathbb{Z}$ em segundos (duração real do arquivo, 600–1100 s — ver limitação documentada na Fase 1, Item 2). $\mathcal{O}_t$ é o conjunto de tiles ocupados no instante $t$ (Eq. 1 do artigo-base, materializado em `processed/geograph/`), $\mathcal{T}_R$ o tiling induzido da região.

**Alcance de comunicação físico**: $\rho = 50\,\text{m}$, invariante entre resoluções e observações. Justificativa em três camadas (Seção 2.6): campanhas empíricas urbanas NLOS medem 45–70 m em interseções e <50 m em canyons urbanos densos [28–30]; âncora de goodput do artigo-base (limiar 10 MB/s a 50 m, ref. [18] do artigo); sanity check de densidade própria — $\lambda\pi\rho^2$ resulta em 5–14 vizinhos médios (d1/d7), colocando as regiões no regime intermediário onde a estrutura espacial discrimina.

**Critério de conexão geométrico (primário)**: dois tiles estão conectados se ocupados **e** a distância mínima entre seus polígonos H3 é ≤ $\rho$. Formalmente:

$$(u,v) \in E_t \;\Longleftrightarrow\; u, v \in \mathcal{O}_t \;\wedge\; \mathrm{dist}_{\min}(u,v) \leq \rho$$

onde $\mathrm{dist}_{\min}(u,v) = \min_{p\in u,\,q\in v} \|p-q\|_2$. O limiar efetivo em saltos $\theta_{eff}$ adapta-se à resolução para preservar o alcance físico por aresta $\approx \rho$ (tabela em Seção 3.2). Variante de fidelidade ao baseline: convenção do artigo-base (proxy de aresta $\theta=1$ na res. 11) preservada como configuração de replicação.

$\mathcal{G}(t) = (V_t, E_t)$ o grafo estático no instante $t$ com $V_t = \mathcal{O}_t$ e arestas pelo critério acima; $\mathcal{R}_\delta$ o grafo de alcançabilidade time-aggregated com tolerância $\delta$.

Todas as métricas abaixo são definidas por observação e são **agnósticas à resolução H3** — a resolução entra apenas como parâmetro das construções (Seção 3).

---

## Item 1 — Métricas estruturais e de estabilidade temporal

Critério de seleção: uma métrica só integra o conjunto se servir diretamente à pergunta central — as propriedades do grafo geotemporal são determinadas pela geografia/comportamento da região (estáveis entre observações da mesma condição) ou pelo estado instantâneo? Isso exige dois níveis: **métricas descritivas** (por observação, nos dois níveis — grafo simples $\mathcal{G}(t)$ e grafo de alcançabilidade $\mathcal{R}_\delta$) e **aparato de comparação** (estabilidade).

### 1.1 Métricas estruturais no grafo simples

#### M1 — Ocupação

$$\phi_o(t) = \frac{|\mathcal{O}_t|}{|\mathcal{T}_R|}$$

Série temporal por observação, resumida por média e CV. Covariável básica — estabilidade em grau/alcançabilidade só interpretável condicionada à ocupação. Custo nulo: $|\mathcal{O}_t|$ já materializado na Fase 1.

#### M2 — Densidade por tile

$$d_i^{(o)} = \frac{1}{|\mathcal{T}_o|} \sum_{t \in \mathcal{T}_o} n_i(t) \qquad \bar{d}(t) = \frac{1}{|\mathcal{T}_R|}\sum_{i} n_i(t)$$

Reproduz Eq. 1 do artigo-base em forma agregada. **Objeto primário: vetor por tile** $\mathbf{d}_o = (d_i)_i$ — análise de estabilidade espacial (Seção 1.3) exige a distribuição espacial completa.

#### M3 — Grau agregado (dois níveis)

**(a) Grau instantâneo médio:**

$$\bar{k}(t) = \frac{2\,|E_t|}{|V_t|} \qquad K_o = \frac{1}{|\mathcal{T}_o|}\sum_{t \in \mathcal{T}_o} \bar{k}(t)$$

Escalar por observação, comunicabilidade direta. Joga fora informação espacial.

**(b) Persistência de adjacência:**

$$p_o(u,v) = \frac{1}{|\mathcal{T}_o|} \sum_{t \in \mathcal{T}_o} \mathbf{1}\big[(u,v) \in E_t\big]$$

Análogo exato de $c(u,v)$ no nível de alcançabilidade — simetria deliberada. **Força de tile:**

$$\sigma_o(u) = \sum_{v \in \mathcal{V}^*} p_o(u,v)$$

Vetor $(\sigma_o(u))_u$ alimenta a estabilidade espacial no grafo simples.

### 1.2 Métricas estruturais no grafo de alcançabilidade

#### M4 — Alcance por tile-fonte (primária)

$$r_\delta(u) = \frac{1}{|\mathcal{V}^*|}\sum_{v \in \mathcal{V}^*} c(u,v)$$

Fração do tempo em que $u$ alcança cada tile dentro de $\delta$. Formaliza "potencial de disseminação" como ranking espacial mensurável (achado central do artigo-base).

#### M5 — Alcançabilidade espaço-agregada (secundária)

$SR_\delta(\{u\}, t)$ (Eq. 5 do artigo-base) como curva temporal por observação. Visão dinâmica complementar.

**Exclusão da Eq. 4 (*reachability error*):** pressupõe conjunto fonte $S$ e alvo "alcançar tudo" — pergunta do artigo-base, não deste projeto. Unidade de análise é o tile individual. Eq. 4 reservada a análise secundária opcional.

### 1.3 Métricas de estabilidade temporal

Dois aspectos exigidos pela hipótese: **magnitude** (valores repetem?) e **estrutura espacial** (padrão de dominação repete?). Estabilidade interna alta não basta — precisa superar separação entre regiões (**discriminabilidade**).

#### S1 — Estabilidade de magnitude

$$CV(m) = \frac{\sigma(m)}{\mu(m)} \quad \text{para } m_o \in \{K_o,\ \bar{d}_o,\ \bar{r}_{\delta,o}\}$$

Sobre as 16 observações da região. Formaliza expectativa de recorrência da literatura de mobilidade (Fase 1, Item 1). Fraco isoladamente.

#### S2 — Estabilidade estrutural (espacial)

Para $\mathbf{x}_o \in \{(\sigma_o(u)),\ (d_i^{(o)}),\ (r_\delta^{(o)}(u))\}$, compara-se pares de observações da mesma região:

- **Correlação de postos de Spearman** $\rho(\mathbf{x}_{o_1}, \mathbf{x}_{o_2})$ sobre $\mathcal{V}^*$: padrão espacial persiste? (consistência de *ranking*).
- **Distância distribucional** — Wasserstein-1 entre distribuições empíricas: forma da distribuição se repete? (concentração vs. homogeneidade).

Ambas reportadas (detectam fenômenos distintos).

#### S3 — Discriminabilidade

$$\Lambda = \frac{\overline{\text{dist}}(\text{obs de regiões distintas})}{\overline{\text{dist}}(\text{obs da mesma região})}$$

Aplicada às três famílias (escalares via S1 normalizado, vetores via S2) e aos dois níveis. Se $\Lambda > 1$ consistentemente, identidade geográfica/comportamental domina sobre instante observado.

**Teste de permutação** (definido aqui, aplicado na Fase 4): $H_0$ = região de origem não importa; rótulos permutáveis entre 32 observações. $p\text{-valor} = \text{frac}(\Lambda_{perm} \geq \Lambda_{obs})$. Sem suposição paramétrica.

### 1.4 Conjunto de comparação de tiles (decisão 3)

- Tile **elegível** em $o$ se ocupado em ≥ 10% dos instantes de $\mathcal{T}_o$;
- Conjunto de comparação: $\mathcal{V}^* = \mathcal{V}^*(o_1) \cap \mathcal{V}^*(o_2)$.

Limiar de 10% declarado; sensibilidade verificada na Fase 4.

### 1.5 Registro de decisões fechadas

| # | Decisão | Escolha |
| --- | --- | --- |
| 1 | Grau agregado | Dois níveis: (a) $K_o$ + (b) $p(u,v)$/$\sigma(u)$ |
| 2 | $\delta$ | Valores absolutos em segundos, idênticos entre observações |
| 3 | Tiles comuns | Limiar ≥10%, interseção entre observações |
| 4 | Eq. 4 | Fora das primárias; reservada a análise secundária |
| 5 | Estabilidade estrutural | Spearman + Wasserstein-1, ambos |
| 6 | Teste de permutação para $\Lambda$ | Definido na Fase 2, aplicado na Fase 4 |

---

## Item 2 — Granularidade temporal ($\Delta t$), alcance físico ($\rho$) e tolerância de atraso ($\delta$)

Esta seção substitui a escolha arbitrária do artigo-base (valores 5–150 s como "boa gradação" sem ancoragem) por fundamentação em: requisitos padronizados, regimes físicos, piso de quantização, e **alcance físico $\rho$ fixo em 50 m**.

### 2.1 Âncora externa: requisitos padronizados

3GPP TS 22.186 (eV2X): latência fim-a-fim 3–100 ms para safety-critical (platooning 10–25 ms; advanced driving, extended sensors 3–100 ms) [26]; TS 22.185: 100 ms para V2X básico [27]. Aplicações não-tempo-real toleram atrasos longos. Espectro V2X: ms a centenas de s — modelo declara qual fatia mede com validade.

### 2.2 Alcance físico $\rho = 50\,\text{m}$: justificativa em três camadas

1. **Empírica urbana NLOS** — campanhas de medição IEEE 802.11p/ITS-G5 em canyons urbanos e interseções [28–30]: PDR > 90% em 45–70 m; canyon denso típico <50 m. O πNEUMA (Atenas centro, pico matinal) é exatamente esse cenário.
2. **Goodput do artigo-base** — limiar 10 MB/s a 50 m (ref. [18] do artigo-base) — âncora complementar orientada a throughput.
3. **Sanity check de densidade própria** — vizinhos médios $\lambda\pi\rho^2$: d7 ≈ 14,4; d1 ≈ 5,3. Regime intermediário (nem fragmentado, nem saturado) onde estrutura espacial discrimina — faixa interessante para a hipótese.

> **Consequência**: resultados condicionais a $\rho$; análise de sensibilidade opcional com $\rho \in \{25, 100\}\,\text{m}$ (Seção 2.6).

### 2.3 Piso de quantização: regime sub-segundo não mensurável

No modelo discreto, cada salto de jornada custa ≥ $\Delta t$ (causalidade: $t_{i+1} - t_i > 0$). Teto implícito de velocidade de propagação por aresta: $\approx \rho$ metros por $\Delta t$ (pelo critério geométrico, o alcance físico por passo é invariante à resolução). Com diâmetro regional $D \approx 520\,\text{m}$:

$$\delta_{min} = \frac{D}{\rho}\cdot\Delta t \approx \frac{520}{50}\cdot 1\,\text{s} \approx 10\,\text{s} \quad (\textbf{invariante entre resoluções})$$

Mesmo conectividade instantânea perfeita aparece como jornada de ~10 s. $\delta < \delta_{min}$ mede artefato de discretização — fora da análise. Delimita domínio de validade: regime de rádio puro (3–100 ms, Seção 2.1) está **fora** — coerente com propósito region-centric (disseminação multi-hop, não balizas single-hop).

Refinamentos Fase 3 (opcionais): (i) $D_{hop}$ do subgrafo ocupado por observação — piso efetivo varia com densidade (maior em d1); (ii) $\delta_{gap}$ empírico (mediana de fechamento de lacuna) via trajetórias brutas com `track_id`.

### 2.4 Os três regimes de propagação

| Regime | $\delta$ | Mecanismo | Status |
| --- | --- | --- | --- |
| Rádio puro | < 1 s (padrões: 3–100 ms) | Eletromagnético multi-hop | Não mensurável ($\delta_{min} \approx 10$ s) |
| **Misto** | **~10–60 s** | Difusão multi-hop + pontes store-carry | **Interesse** — estrutura espacial discrimina |
| Mobilidade pura (DTN) | ≳ 100–200 s | Carregar-e-repassar | Satura; ponto de referência |

No regime misto a mensagem avança por rádio quando há conectividade e atravessa lacunas por mobilidade — regime onde geometria viária e distribuição de tráfego determinam alcançabilidade. No DTN puro converge para "tudo alcança tudo" e perde poder discriminativo (artigo-base observa saturação).

### 2.5 Decisões operacionais para $\delta$

**(a) Grade:** $\delta \in \{10,\, 30,\, 60,\, 120,\, 300\}\,\text{s}$ — absolutos (decisão 2). Interpretação: piso de quantização (controle negativo), centro do regime misto, limite do regime misto, entrada do DTN, referência quasi-DTN (saturação). Teto: $\delta \leq |\mathcal{T}_o|/2$ (≥ ~300 partidas válidas para $c(u,v)$).

**(b) $\delta$ primário = 30 s** para comparações principais (S1–S3), curva completa como sensibilidade. Centro do regime misto, equidistante do piso e saturação; ranking de tiles robusto nessa faixa (artigo-base).

### 2.6 Acoplamento $\Delta t$–$\delta$–$\rho$ e sensibilidade

$\Delta t = 1\,\text{s}$ fixo em todas configurações. Duração típica de contato $\tau_c \approx \rho/v_{rel} \approx 50/(5\text{--}10) \approx 5\text{--}10\,\text{s} \gg \Delta t$ → contatos amostrados várias vezes (Nyquist informal satisfeito). Resolução nativa πNEUMA (~25 Hz) não agrega valor para regime misto e custa 25×.

**Leis de escala documentadas**: aumentar $\Delta t$ suprime contatos transitórios → reduz $r_\delta$; dobrar $\rho$ divide $\delta_{min}$ por 2 e dobra vizinhos médios; resultados sempre reportados condicionais ao par $(\Delta t, \rho)$.

---

## Item 3 — Resoluções H3 a serem testadas

**Decisão fechada:** par de resoluções **{11, 12}** sob critério geométrico (C).

### 3.1 Restrição estruturante e critério adotado

Alcance físico fixo $\rho = 50\,\text{m}$ → limiar efetivo $\theta_{eff}$ adapta-se à resolução para preservar alcance físico por aresta $\approx \rho$. Critério geométrico: $\mathrm{dist}_{\min}(\text{anel } k) \leq \rho$. Tabela de distâncias mínimas por anel H3 pré-computada uma vez por resolução (`h3` + `shapely`); $\theta_{eff} = \max\{k : \mathrm{dist}_{\min}(k) \leq \rho\}$.

| Resolução | $d_{\text{tile}}$ (centro) | $\theta_{eff}$ esperado | Viabilidade |
| --- | ---: | ---: | --- |
| 10 | ~142 m | 0 (nem adjacentes conectam) | Inviável |
| 11 | ~53,5 m | 1–2 (fronteira 49,6 m vs. 50 m) | **Baseline** (comparabilidade com artigo-base) |
| 12 | ~20 m | 3–4 | **Viável**; custo ~7× tiles |

**Consequência do critério (C):** invariância do alcance por passo ($\approx\rho$) → $\delta_{min} \approx 10\,\text{s}$ invariante → comparação entre resoluções mede granularidade espacial, não física de conexão diferente. Convenção do artigo-base (proxy de aresta $\theta=1$ na res. 11) preservada como variante de replicação para quantificar diferença.

Alternativa descartada ({10, 11}): exigiria $\rho \gtrsim 150\,\text{m}$ na res. 10, quebrando ancoragem física e comparabilidade.

### 3.2 Caso de fronteira na res. 11 (sensibilidade explícita)

Distância mínima entre tiles do anel 2 ≈ largura do hexágono intermediário ≈ $\sqrt{3}\,\ell_{\text{aresta}} \approx 49{,}6\,\text{m} \lessapprox \rho = 50\,\text{m}$. Hexágonos H3 não são perfeitamente regulares (distorção icosaédrica) → valor exato decidido empiricamente pela tabela pré-computada. Se $\theta_{eff}=2$ na res. 11, o artigo-base subestima conectividade — diferença documentada como resultado metodológico.

---

## 4. Pontos em aberto (para fechamento em discussão)

1. **Item 2.5** (ainda pendente): grade reduzida $\{10, 60, 300\}\,\text{s}$ vs. $\{10, 30, 60, 120, 300\}\,\text{s}$ (custo Fase 3); estimativa empírica opcional de $\delta_{gap}$.
2. Sensibilidade ao limiar de atividade (10%) — verificação na Fase 4.

Após fechamento do item 1 acima, este documento constitui o entregável da Fase 2.

## Referências

[20] G. Gelmi de Freitas Salvo, B.-M. Bui-Xuan, M. Dias de Amorim. "Geotemporal Graph Modeling for Effective Coverage in Multi-hop Vehicular Networks." Preprint submitted to *Ad Hoc Networks* (2026). [`paper.pdf`, artigo-base]

[26] 3GPP TS 22.186. "Service requirements for enhanced V2X scenarios (Release 16)". Tabela de requisitos sidelink: platooning 10–25 ms, advanced driving 3–100 ms, extended sensors 3–100 ms.

[27] 3GPP TS 22.185. "Service requirements for V2X services (Release 19)". Latência fim-a-fim de 100 ms para serviços V2X básicos.

[28] M. Boban et al. "Observations of 5.9-GHz Radio Propagation and 802.11p Network Performance at Road Junctions." *Radio Science* 54(8), 2019. PDR > 90% em 45–70 m.

[29] T. Schumann et al. "Vehicle-to-Vehicle IEEE 802.11p Performance Measurements at Urban Intersections." 2012. Canyon urbano: <50 m típico.

[30] F. Bai et al. "An Empirical Study on Urban IEEE 802.11p Vehicle-to-Vehicle Communication." *SAHCN* 2016. NLOS dominante em malha densa.
