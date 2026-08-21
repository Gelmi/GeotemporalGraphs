# Revisão de Literatura — Mobilidade Humana Estruturada e Grafos Espaço-Temporais em Redes Veiculares

> Fase 1, item 1 do plano de trabalho: revisão da literatura sobre mobilidade humana estruturada e grafos espaço-temporais aplicados a redes veiculares, servindo de fundamentação teórica para a validação do grafo geotemporal como representação estrutural de redes veiculares.

## 1. Objetivo desta revisão

Este projeto testa se a alcançabilidade, o grau agregado e a densidade de um grafo geotemporal são majoritariamente determinados pela geografia e pelo comportamento humano de uma região — e portanto estáveis entre observações do mesmo tipo de condição temporal — ou se dependem do estado instantâneo observado. Essa pergunta se apoia em duas frentes teóricas que precisam estar bem fundamentadas antes da fase de replicação (Fase 1, itens 2–3):

1. **Mobilidade humana estruturada**: existe evidência robusta de que o deslocamento humano (e, por extensão, veicular) não é aleatório, mas fortemente regular no espaço e no tempo?
2. **Grafos espaço-temporais aplicados a redes veiculares**: como a literatura de redes veiculares/DTN representa essa estrutura, e onde a abordagem region-centric do grafo geotemporal se posiciona frente às abordagens node-centric tradicionais?

## 2. Mobilidade humana estruturada

### 2.1 Regularidade e baixa entropia dos deslocamentos

González, Hidalgo e Barabási (2008) [1], analisando trajetórias de ~100 mil usuários de telefonia móvel ao longo de seis meses, mostraram que o deslocamento humano individual é bem aproximado por um passeio aleatório truncado (*truncated random walk*) com forte tendência de retorno a um pequeno número de locais (residência, trabalho). O padrão de Lévy observado agregadamente decorre da heterogeneidade populacional, não de aleatoriedade individual — ou seja, cada indivíduo é altamente previsível, mesmo que a população pareça heterogênea.

Song et al. (2010) [2] quantificaram essa regularidade via entropia da trajetória e encontraram um teto de previsibilidade de ~93% em toda a base de usuários, notavelmente uniforme e quase independente da distância média percorrida por cada indivíduo. Esse resultado é o argumento central para a hipótese deste projeto: se a mobilidade individual já é altamente previsível, é razoável esperar que propriedades agregadas de uma região (densidade, grau, alcançabilidade) herdem essa estabilidade ao longo de instantes comparáveis (mesmo horário, dias úteis distintos).

Schneider et al. (2013) [3] refinaram essa regularidade na escala diária, mostrando que apenas 17 "motifs" (padrões de rede de deslocamento intradiário) bastam para capturar até 90% da população em pesquisas de mobilidade e dados de telefonia de diferentes países — evidência de que o comportamento humano segue um número pequeno de rotinas estruturais recorrentes, e não uma distribuição difusa de trajetos.

Barbosa et al. (2018) [4], em revisão abrangente sobre modelos e aplicações de mobilidade humana, sistematizam essas regularidades (escalas espaciais características, retorno periódico, previsibilidade) e discutem sua aplicação em planejamento urbano, epidemiologia e — de forma mais direta para este projeto — em modelagem de tráfego e redes de transporte.

### 2.2 Implicação para o projeto

A literatura de mobilidade humana converge para um ponto: a estrutura geográfica (localização de pontos de interesse, malha viária) e os ciclos comportamentais (horários de pico, rotina semanal) são os principais determinantes do padrão de deslocamento observado, e essa estrutura é estável através de observações repetidas da mesma condição (mesmo horário/dia da semana). Isso fundamenta teoricamente a expectativa do projeto de que regiões de alta/baixa densidade no πNEUMA devem exibir propriedades de grafo geotemporal (densidade por tile, grau agregado, alcançabilidade) recorrentes entre dias distintos, caso a hipótese da geografia/comportamento como determinante estrutural esteja correta. Uma falha nessa estabilidade sinalizaria que o grafo geotemporal está capturando principalmente ruído do estado instantâneo, e não a estrutura subjacente.

## 3. Grafos espaço-temporais aplicados a redes veiculares

### 3.1 Da rede node-centric ao grafo temporal

A literatura clássica de roteamento em redes veiculares e redes tolerantes a atraso (DTN) trata a rede como uma sequência de grafos estáticos e otimiza a entrega de mensagens a partir de métricas centradas no nó. O Epidemic Routing (Vahdat & Becker, 2000) [5] inunda a rede com cópias da mensagem sempre que dois nós se encontram; PRoPHET (Lindgren et al., 2003) [6] e MaxProp (Burgess et al., 2006) [7] introduzem probabilidades de entrega baseadas no histórico de encontros; Spray-and-Wait (Spyropoulos et al., 2005) [8] limita o número de cópias para conter o overhead. Esses métodos herdam de uma leitura node-centric: a rede é modelada por identidade e histórico de contato dos nós, não pela estrutura espacial que gera esses contatos. Benamar et al. (2014) [9] oferecem um levantamento abrangente dessas estratégias de roteamento em DTN veicular, destacando justamente a lacuna de modelos que incorporem restrição espacial explícita.

Uma segunda linha usa métricas topológicas — centralidade de intermediação (*betweenness*), autovetor — para identificar nós influentes na disseminação (Kitsak et al., 2010) [10], mas opera sobre informação de rede limitada e mantém o foco no nó como unidade de análise, não explorando heterogeneidade espacial ou regularidade da mobilidade.

Um terceiro grupo já reconhece a importância do espaço, mas apenas como fator auxiliar do roteamento node-centric: protocolos como SPread e ASpread combinam localidade geográfica com comunidades sociais para melhorar a eficiência do roteamento (discutido em [11], [12]), e abordagens de roteamento geográfico com informação de dois saltos (Zhu et al., 2021) [13] usam posição apenas como heurística de encaminhamento local. O ganho de desempenho reportado ao incorporar espaço nesses protocolos é o indício central de que a estrutura espacial pode ser, em si, a unidade de análise mais adequada — e não apenas um parâmetro auxiliar de um modelo node-centric.

### 3.2 Grafos espaço-temporais formais

Fora do domínio de redes veiculares, George & Shekhar (2008) [14] formalizam o conceito de *time-aggregated graph*: uma representação em que arestas e vértices carregam séries temporais de atributos, permitindo condensar a evolução de uma rede ao longo do tempo em uma única estrutura anotada, sem perder a informação temporal subjacente. Esse é o antecedente formal direto do *time-aggregated reachability graph* usado no artigo-base deste projeto.

Mais recentemente, redes neurais de grafos espaço-temporais (STGNN) se tornaram o paradigma dominante para previsão de tráfego e mobilidade urbana. Jin et al. (2024) [15] revisam de forma abrangente o uso de STGNNs em computação urbana; Zhao et al. (2023) [16] e Peng et al. (2020) [17] tratam especificamente da previsão de fluxo de tráfego combinando dependência espacial (grafo da malha viária) e temporal (séries de velocidade/densidade); Mao et al. (2024) [18] estendem a ideia a previsão epidemiológica via redes espaço-temporais dinâmicas. Esses trabalhos confirmam que tratar a dimensão espacial e temporal de forma conjunta e explícita — em vez de reduzir tudo a atributos de nó — captura dependências que os modelos node-centric não capturam, mas em geral têm como objetivo *previsão* (forecasting) de fluxo, não a modelagem de alcançabilidade de mensagens em uma rede ad hoc.

Uma linha adicional, mais recente, explora decisões de disseminação orientadas por dados e por intenção: Ahmad et al. (2025) [19] propõem um framework de encaminhamento V2X orientado por IA que adapta decisões a partir de intenções de segurança e fluxo aprendidas, mas ainda opera sob um modelo node-centric e depende de treinamento extensivo, sem generalizar estrutura espacial de forma explícita.

### 3.3 O grafo geotemporal como abordagem region-centric

O artigo-base deste projeto, Salvo, Bui-Xuan & Amorim, *"Geotemporal Graph Modeling for Effective Coverage in Multi-hop Vehicular Networks"* [20] (referência técnica central da Fase 1, item 3), propõe deslocar a unidade de análise do nó para a região geográfica. A rede veicular é particionada em *tiles* (usando o sistema de indexação hexagonal H3 [21]), e a atividade dos veículos é usada para definir, a cada instante, o conjunto de tiles ocupados (Eq. 1 do artigo). Sobre essa tiling, o grafo geotemporal $\mathcal{G} = (\mathcal{G}(t))_{t \in \mathcal{T}_{time}}$ conecta tiles ocupados que estão a até $\theta$ saltos de distância (definido pelo alcance de comunicação), formando uma sequência de grafos estáticos que integra explicitamente restrição espacial e dinâmica temporal.

A partir daí, o artigo define o *time-aggregated reachability graph* $\mathcal{R}_\delta$ (quais regiões se alcançam mutuamente respeitando uma tolerância de atraso $\delta$ e causalidade temporal) e a *time-aggregated reachability function* $c(u,v)$, que resume, ao longo de toda a janela temporal observada, a fração de instantes em que uma região alcança outra. Esse ferramental — junto com o *time-aggregated reachability error* (Eq. 4) e a *space-aggregated reachability* $\mathcal{SR}_\delta$ (Eq. 5) — é exatamente o que a Fase 2 deste projeto reaproveita para formalizar a métrica de alcançabilidade, e o que a Fase 1, item 3 replica como baseline técnico.

Empiricamente, o artigo mostra, usando dados sintéticos (SUMO [22]) e reais (πNEUMA [23]), que um subconjunto pequeno e identificável de regiões consistentemente supera as demais em alcançabilidade — os "tiles candidatos" concentrados nas interseções centrais da malha viária, enquanto "tiles inefetivos" ficam nas margens da região. Esse achado é a primeira evidência direta, na própria literatura-base, de que a alcançabilidade de uma região é fortemente condicionada pela sua posição estrutural na malha viária (geografia), e não apenas pelo instante observado — o que é precisamente a hipótese central que este projeto busca testar de forma controlada, comparando regiões de densidade alta e baixa ao longo de múltiplos dias.

### 3.4 Lacuna identificada

Como o próprio artigo-base aponta em sua seção de trabalhos relacionados, a maior parte da literatura de redes veiculares/DTN prioriza métricas centradas no nó (histórico de contato, centralidade, intenção aprendida), e mesmo os trabalhos que introduzem localidade geográfica o fazem como parâmetro auxiliar de um roteamento ainda node-centric. Os poucos trabalhos que propõem abstrações de tiling ou região raramente incorporam essa estrutura na própria estratégia de disseminação [24, 25]. A lacuna que resta — e que este projeto busca preencher — não é a existência do grafo geotemporal (já proposto e validado empiricamente em um único par de datasets/regiões), mas sim **se suas propriedades agregadas são de fato dominadas pela geografia/comportamento humano da região, de forma estável entre observações repetidas, ou se refletem principalmente o estado instantâneo do tráfego observado**. O artigo-base evidencia o padrão (regiões centrais dominam a alcançabilidade) mas não testa formalmente sua estabilidade temporal entre dias distintos — que é exatamente o objetivo das Fases 2–4 deste projeto.

## 4. Síntese

| Frente | Achado central | Papel no projeto |
|---|---|---|
| Mobilidade humana estruturada [1–4] | Deslocamento humano é regular, previsível (~93%) e redutível a poucos padrões (motifs) recorrentes | Fundamenta a hipótese de que propriedades agregadas de região devem ser estáveis entre dias comparáveis |
| Roteamento node-centric em VANET/DTN [5–10] | Métricas de nó (contato, centralidade) dominam a literatura clássica; espaço é auxiliar quando presente | Justifica por que uma abordagem region-centric é uma contribuição, não uma redundância |
| Grafos espaço-temporais formais e STGNNs [14–19] | Espaço e tempo tratados conjuntamente capturam dependências que modelos node-centric perdem | Dá o arcabouço formal (time-aggregated graphs) do qual o grafo geotemporal deriva |
| Grafo geotemporal [20] | Regiões centrais na malha viária dominam consistentemente a alcançabilidade em um recorte único de dados | Fornece o baseline técnico (Fase 1, item 3) e as métricas a formalizar (Fase 2); motiva a pergunta de estabilidade temporal que este projeto testa |

## Referências

[1] M. C. González, C. A. Hidalgo, A.-L. Barabási. "Understanding individual human mobility patterns." *Nature* 453, 779–782 (2008).

[2] C. Song, Z. Qu, N. Blumm, A.-L. Barabási. "Limits of Predictability in Human Mobility." *Science* 327, 1018–1021 (2010).

[3] C. M. Schneider, V. Belik, T. Couronné, Z. Smoreda, M. C. González. "Unravelling daily human mobility motifs." *Journal of The Royal Society Interface* 10(84), 20130246 (2013).

[4] H. Barbosa et al. "Human mobility: Models and applications." *Physics Reports* 734, 1–74 (2018).

[5] A. Vahdat, D. Becker. "Epidemic routing for partially-connected ad hoc networks." Duke Technical Report CS-2000-06 (2000).

[6] A. Lindgren, A. Doria, O. Schelén. "Probabilistic routing in intermittently connected networks." *ACM SIGMOBILE Mobile Computing and Communications Review* 7(3) (2003).

[7] J. Burgess, G. D. Gallagher, D. Jensen, B. N. Levine. "MaxProp: Routing for vehicle-based disruption-tolerant networks." *IEEE INFOCOM* (2006).

[8] T. Spyropoulos, K. Psounis, C. S. Raghavendra. "Spray and wait: an efficient routing scheme for intermittently connected mobile networks." *ACM SIGCOMM Workshop on Delay-Tolerant Networking (WDTN)* (2005).

[9] N. Benamar, K. D. Singh, M. Benamar, D. El Ouadghiri, J.-M. Bonnin. "Routing protocols in vehicular delay tolerant networks: A comprehensive survey." *Computer Communications* 48, 141–158 (2014).

[10] M. Kitsak, L. K. Gallos, S. Havlin, F. Liljeros, L. Muchnik, H. E. Stanley, H. A. Makse. "Identification of influential spreaders in complex networks." *Nature Physics* 6, 888–893 (2010).

[11] R. Tizvar, M. Abbaspour. "A density-aware probabilistic method for content-centric vehicular networks." *Vehicular Communications* 23, 100216 (2020).

[12] B. Wu, H. Shen, K. Chen. "Spread: Exploiting fractal social community for efficient multi-copy routing in taxi VDTNs." *IEEE Transactions on Network Science and Engineering* 6 (2019).

[13] H. Zhu, Y. Mir, C. L. Hu. "Geographic routing with two-hop movement information in mobile opportunistic networks." *IEEE WOCC* (2021).

[14] B. George, S. Shekhar. "Time-aggregated graphs for modeling spatio-temporal networks." *Lecture Notes in Computer Science*, vol. 5383 (2008).

[15] G. Jin, Y. Liang, Y. Fang, Z. Shao, J. Huang, J. Zhang, Y. Zheng. "Spatio-temporal graph neural networks for predictive learning in urban computing: A survey." *IEEE Transactions on Knowledge and Data Engineering* 36 (2024).

[16] J. Zhao, Y. Wang, X. Dou, X. Wang, M. Guo, R. Zhang, H. Li. "Advances in spatiotemporal graph neural network prediction research." (2023).

[17] H. Peng, H. Wang, B. Du, M. Z. A. Bhuiyan, H. Ma, J. Liu, L. Wang, Z. Yang, L. Du, S. Wang, P. S. Yu. "Spatial temporal incidence dynamic graph neural networks for traffic flow forecasting." *Information Sciences* 521 (2020).

[18] J. Mao, Y. Han, B. Tanaka, B. Wang. "Backbone-based dynamic spatio-temporal graph neural network for epidemic forecasting." *Knowledge-Based Systems* 296 (2024).

[19] W. Ahmad, F. Ali, A. Ali. "Scalable AI-driven intent-based vehicle-to-everything communications for secure, low-latency, energy-efficient smart cities." *Vehicular Communications* 56 (2025).

[20] G. Gelmi de Freitas Salvo, B.-M. Bui-Xuan, M. Dias de Amorim. "Geotemporal Graph Modeling for Effective Coverage in Multi-hop Vehicular Networks." Preprint submitted to *Ad Hoc Networks* (2026). [`paper.pdf`, artigo-base do projeto]

[21] Uber Technologies Inc. "H3: Hexagonal hierarchical geospatial indexing system." https://h3geo.org (2023).

[22] P. A. Lopez et al. "Microscopic traffic simulation using SUMO." *IEEE ITSC* (2018).

[23] E. Barmpounakis, N. Geroliminis. "On the new era of urban traffic monitoring with massive drone data: The pNEUMA large-scale field experiment." *Transportation Research Part C: Emerging Technologies* 111 (2020).

[24] Q. Fang, J. Gao, L. J. Guibas, V. de Silva, L. Zhang. "GLIDER: Gradient landmark-based distributed routing for sensor networks." *IEEE INFOCOM* (2005).

[25] J. Zhao, R. Govindan. "An energy-efficient region-based RPL routing protocol for low-power and lossy networks." *IEEE Internet of Things Journal* 3 (2016).
