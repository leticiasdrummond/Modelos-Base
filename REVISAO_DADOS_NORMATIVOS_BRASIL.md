# Revisão dos dados e aderência normativa brasileira

## 1. Objetivo

Este documento registra as premissas técnicas, econômicas e normativas usadas para atualizar dados de entrada de um modelo de otimização de eletropostos rápidos para infraestrutura brasileira, com foco em uso acadêmico na UNICAMP/FEEC e projetos financiados por agências como a FAPESP.

## 2. Escopo do estudo

O corredor considerado liga Campinas, Ribeirão Preto, Franca e a divisa com Minas Gerais, usando trechos associados às rodovias SP-348 e SP-330. O estudo tem natureza de planejamento e não substitui projeto executivo, orçamento vinculante, parecer de acesso ou aprovação da distribuidora.

## 3. Normas e referências regulatórias

### 3.1 ANEEL

- Resolução Normativa ANEEL nº 1.000/2021: regras gerais de prestação do serviço público de distribuição de energia elétrica.
- PRODIST, Módulo 8: qualidade do fornecimento e faixas de tensão em regime permanente.
- Resolução Normativa ANEEL nº 482/2012 e alterações: referência histórica para micro e minigeração distribuída; recomenda-se verificar o marco legal vigente no ano da aplicação.

### 3.2 ABNT e IEC

- ABNT NBR 5410: instalações elétricas de baixa tensão.
- ABNT NBR IEC 61851: sistema de recarga condutiva para veículos elétricos.
- ABNT NBR IEC 62196: plugues, tomadas e acopladores para veículos elétricos.
- IEC 61851-1 e IEC 61851-23: requisitos gerais e estações de recarga em corrente contínua.

### 3.3 Interconexão e qualidade

Foram mantidos limites operacionais de tensão de 0,93 pu a 1,05 pu como restrição simplificada de qualidade de energia. Em projeto detalhado, devem ser acrescentados estudos de curto-circuito, coordenação de proteção, harmônicos, demanda contratada, fator de potência e impacto na rede.

## 4. Premissas técnicas

A potência nominal por carregador foi ajustada para 60 kW, valor conservador para implantação rápida com menor impacto de conexão em média tensão. A estação típica possui quatro pontos, resultando em 240 kW instalados por local. A bateria média do veículo foi definida em 55 kWh, com ciclo de recarga típico de 20% a 80% do estado de carga.

## 5. Premissas econômicas

Os custos estão em reais de 2024 e representam ordens de grandeza para planejamento: estação completa a R$ 600.000, sistema fotovoltaico a R$ 5.000/kWp, bateria estacionária a R$ 2.600/kWh e conexão elétrica a R$ 85.000/km. Deve-se atualizar a data-base por índice apropriado e cotações reais.

## 6. Tarifa horossazonal

A estrutura tarifária foi representada por seis períodos: madrugada, manhã, meio-dia, ponta, noite e fim da noite. A ponta recebeu maior custo para incentivar estratégias com armazenamento e deslocamento de consumo.

## 7. Conformidade acadêmica e ABNT

Para uso em dissertação, recomenda-se: explicitar hipóteses, informar data-base, diferenciar dado medido de dado estimado, preservar rastreabilidade das fontes e formatar referências segundo ABNT NBR 6023. Tabelas e figuras devem ser numeradas, chamadas no texto e acompanhadas de fonte.

## 8. Limitações

Os dados são adequados para análise de viabilidade, comparação de cenários e desenvolvimento metodológico. Não devem ser usados isoladamente para contratação de obras, especificação final de equipamentos ou aprovação regulatória.

## Referências essenciais

AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA. Resolução Normativa nº 1.000, de 7 de dezembro de 2021. Brasília: ANEEL, 2021.

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. ABNT NBR 5410: Instalações elétricas de baixa tensão. Rio de Janeiro: ABNT.

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. ABNT NBR IEC 61851: Sistema de recarga condutiva para veículos elétricos. Rio de Janeiro: ABNT.

SANTOS, C.; ANDRADE, J. C. G.; OLIVEIRA, W. A.; LYRA, C. Optimal allocation of fast charging stations for large-scale transportation systems. International Journal of Production Research, 2023.
