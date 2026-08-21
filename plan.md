# Estrutura Geográfica e Comportamento Humano como Determinantes de Redes Veiculares: Uma Validação via Grafos Geotemporais

##  Descrição do Projeto

A estrutura geográfica urbana e os padrões regulares de comportamento humano são reconhecidamente determinantes da mobilidade veicular. Este projeto investiga como essa influência se manifesta em redes veiculares, mais especificamente nas propriedades de alcançabilidade capturadas por um grafo geotemporal, uma representação proposta para modelar disseminação de mensagens nesse tipo de rede. Selecionamos regiões do dataset πNEUMA com perfis de densidade veicular distintos (alta e baixa) e as representamos em múltiplas resoluções espaciais, medindo densidade por tile, grau agregado do grafo e alcançabilidade ao longo das janelas de pico matinal registradas em diferentes dias úteis. O objetivo é verificar se essas propriedades são majoritariamente determinadas pela geografia e pelo comportamento humano do local, mantendo-se estáveis entre observações distintas dessa mesma condição temporal, ou se dependem primariamente do estado instantâneo observado. A resposta a essa questão valida, ou não, a adequação do grafo geotemporal como representação para capturar características estruturais de redes veiculares, orientando decisões práticas de modelagem em futuras aplicações.

## Plano de trabalho

### Fase 1 — Fundamentação e replicação

- Revisão da literatura sobre mobilidade humana estruturada e grafos espaço-temporais aplicados a redes veiculares.
- Levantar, no πNEUMA, o perfil de densidade veicular por região - disponível no dataset, para selecionar as duas regiões (alta e baixa densidade).
- Replicar o pipeline de construção do grafo geotemporal do artigo anterior como baseline técnico (reaproveitando código já existente).
- Entregável: relatório curto com a fundamentação teórica e a justificativa das regiões escolhidas.

### Fase 2 — Definição operacional das métricas

- Formalizar as métricas a serem usadas: densidade por tile (já definida no artigo, Eq. 1), grau agregado do grafo geotemporal (definir precisamente, ex: grau médio dos nós ativos por instante, ou grau médio ao longo da janela temporal), e alcançabilidade (reaproveitando o time-aggregated reachability error).
- Definir a métrica de estabilidade temporal (ex: coeficiente de variação entre dias/horários, ou correlação entre distribuições em janelas distintas).
- Definir as resoluções H3 a serem testadas (2 níveis, escolhidos por viabilidade computacional).
- Entregável: documento de metodologia com todas as métricas formalmente definidas e justificadas.

### Fase 3 — Construção dos grafos e coleta de dados

- Construir os grafos geotemporais para as duas regiões, nas resoluções escolhidas, para os diferentes horários/dias disponíveis no πNEUMA.
- Monitorar e registrar custo computacional (tempo, memória) de cada configuração, já antecipando possíveis limitações de infraestrutura.
- Entregável (semana 8): base de dados processada (grafos e métricas brutas) pronta para análise.

### Fase 4 — Análise estatística

- Comparar as métricas entre regiões (densidade × granularidade × alcançabilidade).
- Testar estabilidade temporal: as métricas de uma mesma região se mantêm parecidas entre horários/dias, comparadas à variação entre regiões diferentes?
- Interpretar os resultados à luz da pergunta central: a geografia/comportamento domina sobre o instante observado?
- Entregável: resultados preliminares e gráficos/tabelas de análise.