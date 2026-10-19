# Fase 2 — Definição Operacional das Métricas

> Fase 2 do plano de trabalho (`plan.md`): formalizar as métricas a serem usadas (densidade por tile, grau agregado do grafo geotemporal, alcançabilidade), definir a métrica de estabilidade temporal e as resoluções H3 a serem testadas. Entregável: documento de metodologia com todas as métricas formalmente definidas e justificadas.

Este documento cobre os três bullets da fase. As decisões fechadas estão registradas na Seção 1.5 e na tabela consolidada da Seção 4; os pontos em aberto (todos opcionais) estão listados na Seção 4.

## Notação

Segue o artigo-base [20]. Uma **observação** é uma tupla $o = (\text{região}, \text{data}, \text{janela})$ — para cada região ($d1$, baixa densidade; $d7$, alta densidade, selecionadas na Fase 1) há 16 observações (4 datas × 4 janelas de pico matinal). Cada observação tem domínio temporal $\mathcal{T}_o \subset \mathbb{Z}$ em segundos (duração real do arquivo, 600–1100 s — ver limitação documentada na Fase 1, Item 2). $\mathcal{O}_t$ é o conjunto de tiles ocupados no instante $t$ (Eq. 1 do artigo-base, materializado em `processed/geograph/`), $\mathcal{T}_R$ o tiling induzido da região.

**Alcance de comunicação físico**: $\rho = 50\,\text{m}$, invariante entre resoluções e observações. Justificativa em três camadas (Seção 2.6): campanhas empíricas urbanas NLOS medem 45–70 m em interseções e <50 m em canyons urbanos densos [28–30]; âncora de goodput do artigo-base (limiar 10 MB/s a 50 m, ref. [18] do artigo); sanity check de densidade própria — $\lambda\pi\rho^2$ resulta em 5–14 vizinhos médios (d1/d7), colocando as regiões no regime intermediário onde a estrutura espacial discrimina.

**Critério de conexão geométrico (primário)**: dois tiles estão conectados se ocupados **e** a distância mínima entre seus polígonos H3 é ≤ $\rho$. Formalmente:

$$(u,v) \in E_t \;\Longleftrightarrow\; u, v \in \mathcal{O}_t \;\wedge\; \mathrm{dist}_{\min}(u,v) \leq \rho$$

onde $\mathrm{dist}_{\min}(u,v) = \min_{p\in u,\,q\in v} \|p-q\|_2$.

Leitura do critério: trata-se de **contato possível** — o análogo do grafo de disco unitário (*range graph*) aplicado aos polígonos dos tiles, não de um enlace multi-hop. Se apenas $u$ e $v$ estiverem ocupados e houver um tile vazio entre eles, a conexão representa um salto de rádio **direto** atravessando o vazio (não um relé). O limiar efetivo em saltos $\theta_{eff}$ adapta-se à resolução para preservar o alcance físico por aresta $\approx \rho$ (tabela na Seção 3.1; discussão dos critérios alternativos na Seção 3.3). Variante de fidelidade ao baseline: convenção do artigo-base (proxy de aresta $\theta=1$ na res. 11), que coincide com o **colchete conservador** $\theta_{eff}-1$ nessa resolução — as duas configurações são rodadas em conjunto para delimitar o efeito dos enlaces marginais (Seção 3.3).

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

### 2.3 Tempo de travessia em conectividade perfeita ($\delta_{min}$)

No modelo discreto cada salto de jornada custa ≥ $\Delta t$ (causalidade: $t_{i+1} - t_i > 0$), e cada aresta cobre até $\theta_{eff}$ anéis — logo o deslocamento máximo por passo é $\theta_{eff}\cdot d_{\text{tile}} \gtrsim \rho$. Com diâmetro regional $D \approx 520\,\text{m}$:

$$\delta_{min} = \frac{D}{\theta_{eff}\cdot d_{\text{tile}}}\cdot\Delta t \approx \frac{D}{\rho}\cdot\Delta t \in [5,\,10]\,\text{s}$$

Este é o **tempo mínimo de travessia da região em conectividade perfeita** — o instante em que $r_\delta(u)$ atinge o platô para uma rede idealmente conectada com aquela resolução ($\approx 5$ s com $\theta_{eff}=2$; $\approx 10$ s com $\theta_{eff}=1$).

**Interpretação dos dois lados do limiar** (correção de um enquadramento anterior deste documento, que tratava $\delta < \delta_{min}$ como artefato a excluir):

- $\delta \geq \delta_{min}$: o orçamento temporal excede o necessário para atravessar a região conectada → a métrica lê **tolerância de atraso** no sentido físico habitual.
- $1\,\text{s} \leq \delta < \delta_{min}$: a jornada é limitada por **orçamento de saltos** ($k = \delta/\Delta t$) → a métrica lê **profundidade de conectividade temporal**: quão fragmentada é a rede e quantas pontes a mobilidade precisa fornecer. É quantidade estrutural legítima, e é justamente o trecho da curva em que d1 e d7 — e dias distintos de uma mesma região — mais se discriminam.
- $\delta < 1\,\text{s}$: impossível sequer um salto — fora do modelo.

O efeito de discretização é *common-mode* entre observações da mesma região (mesma geometria, mesmo $\Delta t$), portanto não enviesa as comparações de estabilidade (S1–S3). Além disso o modelo **subestima** a entrega rápida (o rádio real é praticamente instantâneo, enquanto o modelo cobra $\Delta t$ por salto) — a inclusão da faixa $\delta < \delta_{min}$ é, nessa direção, conservadora. O regime de rádio puro dos padrões (3–100 ms, Seção 2.1) permanece **fora** do alcance do modelo, coerente com o propósito region-centric (disseminação multi-hop, não balizas single-hop).

Refinamentos Fase 3 (opcionais): (i) $D$ e $\theta_{eff}$ do subgrafo *ocupado* por observação — o limiar efetivo varia com a densidade (maior em d1); (ii) $\delta_{gap}$ empírico (mediana de fechamento de lacuna) via trajetórias brutas com `track_id`.

### 2.4 Os três regimes de propagação

| Regime | $\delta$ | Mecanismo | Status |
| --- | --- | --- | --- |
| Rádio puro | < 1 s (padrões: 3–100 ms) | Eletromagnético multi-hop | Abaixo do passo de discretização — fora do alcance do modelo |
| Orçamento de saltos | 1 s – $\delta_{min}$ (~5–10 s) | Conectividade parcial em poucos saltos | Mensurável como métrica **estrutural** (fragmentação), não como atraso físico |
| **Misto** | **~10–60 s** | Difusão multi-hop + pontes store-carry | **Interesse** — estrutura espacial discrimina |
| Mobilidade pura (DTN) | ≳ 100–200 s | Carregar-e-repassar | Satura; ponto de referência |

No regime misto a mensagem avança por rádio quando há conectividade e atravessa lacunas por mobilidade — regime onde geometria viária e distribuição de tráfego determinam alcançabilidade. No DTN puro converge para "tudo alcança tudo" e perde poder discriminativo (artigo-base observa saturação).

### 2.5 Decisões operacionais para $\delta$

**(a) Grade:** $\delta \in \{5,\, 10,\, 15,\, 20,\, 30,\, 45,\, 60,\, 120,\, 300\}\,\text{s}$ — valores absolutos (decisão 2), com amostragem fina no regime misto e leitura em dois regimes semânticos (Seção 2.3): $\delta < \delta_{min}$ = cobertura por orçamento de saltos; $\delta \geq \delta_{min}$ = tolerância de atraso. Piso absoluto: $\delta \geq 1$ s. Teto: $\delta \leq |\mathcal{T}_o|/2$ (≥ ~300 partidas válidas para $c(u,v)$).

**(b) Granularidade é escolha de reporte, não de custo:** o custo dominante do cálculo é a malha $|\mathcal{V}|^2$ de pares fonte-alvo, não o número de valores de $\delta$ — a curva completa $r_\delta(u)$ decorre dos tempos de chegada mais cedo por par (perfil temporal) e $c(u,v;\delta)$ é um limiar sobre esse perfil. A Fase 3 valida o custo real.

**(c) $\delta$ primário = 30 s** para comparações principais (S1–S3), curva completa como sensibilidade. Centro do regime misto; ranking de tiles robusto nessa faixa (artigo-base).

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
| 10 | ~142 m | 1 (só adjacentes; anel 2 a ~114 m > $\rho$) | Inviável por **granularidade**: ~12 tiles/região (2–3 de diâmetro) |
| 11 | ~53,5 m | 1–2 (fronteira 49,6 m vs. 50 m) | **Baseline** (comparabilidade com artigo-base) |
| 12 | ~20 m | 3–4 | **Viável**; custo ~7× tiles |

**Consequência do critério (C):** a escala de conexão *estática* fica ancorada em $\rho$ (vizinhança ≈ alcance físico, independente da resolução) → $\delta_{min}$ varia pouco entre resoluções (~5–10 s, Seção 2.3) → a comparação entre resoluções mede granularidade espacial, não uma física de conexão diferente. Convenção do artigo-base (proxy de aresta $\theta=1$ na res. 11) preservada como variante de replicação para quantificar a diferença.

Alternativa descartada ({10, 11}): **não por inviabilidade de $\theta$** — sob o critério geométrico a res. 10 é conectável com $\theta_{eff}=1$, pois tiles adjacentes compartilham aresta (distância mínima 0) — mas por **granularidade insuficiente**: a área de ~0,137 km² cabe em ~12 tiles da res. 10, isto é 2–3 tiles de diâmetro, sem estrutura espacial a analisar e com grafo trivialmente atravessável ($\delta_{min} \approx 4$ s).

### 3.2 Caso de fronteira na res. 11 (sensibilidade explícita)

Distância mínima entre tiles do anel 2 ≈ largura do hexágono intermediário ≈ $\sqrt{3}\,\ell_{\text{aresta}} \approx 49{,}6\,\text{m} \lessapprox \rho = 50\,\text{m}$. Hexágonos H3 não são perfeitamente regulares (distorção icosaédrica) → o valor exato é decidido empiricamente pela tabela pré-computada. Se $\theta_{eff}=2$ na res. 11, o artigo-base **subestima** conectividade nesse anel; a diferença é documentada como resultado metodológico.

### 3.3 Por que o critério geométrico, e não centro-a-centro

Comparação das convenções possíveis na res. 11 ($\rho = 50\,\text{m}$, $d_{\text{tile}} \approx 53{,}5\,\text{m}$):

| Critério | $\theta$ | Consequência |
| --- | ---: | --- |
| Centro-a-centro ($d_{\text{tile}} > \rho$) | 0 | Nenhuma aresta — o modelo colapsa (não é "subestimar", é aniquilar) |
| Conservador estrito ($\mathrm{dist}_{\max} \leq \rho$) | 0 | Cantos opostos de tiles adjacentes distam $2\ell \approx 57{,}3\,\text{m} > \rho$ → também colapsa |
| Adjacência (proxy do artigo, $\theta=1$) | 1 | Conecta adjacentes cujos ocupantes podem estar a 57,3 m (fora de alcance) **e** omite pares a 2 anéis que estão a 49,6 m (em alcance) |
| **Existencial (adotado)** | 1–2 | Liga todo par com ocupantes potencialmente em alcance |

Argumento central: **não existe critério conservador viável nesta granularidade**. Todo $\theta$ fixo sobre- e subestima simultaneamente, porque a abstração descarta a posição intra-tile; o proxy do artigo não é conservador — é apenas diferente, e erra nas duas direções. O critério existencial é o único que (i) mantém o modelo vivo, (ii) tem leitura física limpa — "os ocupantes destes tiles **podem** se comunicar", o modelo padrão de grafo de disco unitário — e (iii) fixa a escala de conexão em $\rho$, tornando a comparação entre resoluções significativa.

Seu viés é **otimista**: pares a 2 anéis cujos ocupantes estão tipicamente a ~107 m entram como conectados, e esse viés cresce com resolução mais fina (na res. 12, $\theta_{eff} \approx 4$ liga pares com distância típica de ~80 m).

**Mitigação**: rodar em conjunto $\theta_{eff}$ (existencial) e $\theta_{eff}-1$ (na res. 11 = $\theta=1$, exatamente a convenção do artigo-base). As duas configurações delimitam o efeito dos enlaces marginais: se $r_\delta$ e as métricas de estabilidade diferirem pouco entre elas, a fronteira 49,6 m vs. 50 m é imaterial; se diferirem, a diferença é ela mesma um resultado a reportar. O bracketing cobre também a sensibilidade a $\rho$ (Seção 2.6).

---

## 4. Decisões fechadas e pontos em aberto

**Consolidação das decisões de parâmetros** (além das seis da Seção 1.5):

| # | Parâmetro / decisão | Escolha |
| --- | --- | --- |
| 7 | Alcance físico $\rho$ | 50 m, justificado em três camadas (Seção 2.2) |
| 8 | Critério de conexão | Geométrico existencial ($\mathrm{dist}_{\min} \leq \rho$), com bracketing $\theta_{eff}-1$ (Seção 3.3) |
| 9 | $\Delta t$ | 1 s, fixo em todas as configurações (Seção 2.6) |
| 10 | Grade de $\delta$ | $\{5, 10, 15, 20, 30, 45, 60, 120, 300\}$ s; $\delta^* = 30$ s; piso 1 s; teto $\lvert\mathcal{T}_o\rvert/2$ (Seção 2.5) |
| 11 | Resoluções H3 | {11, 12} (Seção 3.1) |

**Pontos em aberto** (todos opcionais — não bloqueiam o entregável):

1. Estimativa empírica de $\delta_{gap}$ na Fase 3 (reprocessamento parcial dos CSVs preservando `track_id`).
2. Sensibilidade ao limiar de atividade (10%, Seção 1.4) — verificação na Fase 4.
3. Sensibilidade de $\rho$ ($\{25, 100\}$ m em configuração reduzida), condicionada ao orçamento da Fase 3.

## Referências

[20] G. Gelmi de Freitas Salvo, B.-M. Bui-Xuan, M. Dias de Amorim. "Geotemporal Graph Modeling for Effective Coverage in Multi-hop Vehicular Networks." Preprint submitted to *Ad Hoc Networks* (2026). [`paper.pdf`, artigo-base]

[26] 3GPP TS 22.186. "Service requirements for enhanced V2X scenarios (Release 16)". Tabela de requisitos sidelink: platooning 10–25 ms, advanced driving 3–100 ms, extended sensors 3–100 ms.

[27] 3GPP TS 22.185. "Service requirements for V2X services (Release 19)". Latência fim-a-fim de 100 ms para serviços V2X básicos.

[28] M. Boban et al. "Observations of 5.9-GHz Radio Propagation and 802.11p Network Performance at Road Junctions." *Radio Science* 54(8), 2019. PDR > 90% em 45–70 m.

[29] T. Schumann et al. "Vehicle-to-Vehicle IEEE 802.11p Performance Measurements at Urban Intersections." 2012. Canyon urbano: <50 m típico.

[30] F. Bai et al. "An Empirical Study on Urban IEEE 802.11p Vehicle-to-Vehicle Communication." *SAHCN* 2016. NLOS dominante em malha densa.
