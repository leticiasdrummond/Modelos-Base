# Estado da Arte: Modelagem de Microrredes para Eletropostos Rodoviários no Brasil

> **Objetivo deste documento**: consolidar o estado da arte e orientar a metodologia de modelagem/otimização de microrredes para eletropostos rodoviários no Brasil, com foco em **atendimento elétrico confiável, seguro e contínuo** por meio de **mix PV, BESS e rede elétrica** em cenários de **sistema isolado**, **rede limitada a 75 kW**, e **falhas de rede por dias**.

---

## 1. Contexto e motivação

Eletropostos em rodovias apresentam **alta demanda de potência** e **variabilidade** (sessões rápidas e imprevisíveis), ao mesmo tempo em que enfrentam **restrições de conexão** e **baixa confiabilidade** em áreas remotas. Isso torna necessária a adoção de **microrredes híbridas** com fontes renováveis e armazenamento, capazes de garantir **continuidade de serviço** mesmo sob falhas prolongadas de rede.

A otimização matemática (LP/MILP/MIQP) é a abordagem mais apropriada para lidar simultaneamente com:
- decisões contínuas (fluxos de potência, SOC),
- decisões discretas (modo ilhado, priorização de carga),
- restrições operacionais (limites de potência, SOC mínimo),
- e objetivos múltiplos (custo, confiabilidade, qualidade do atendimento).

---

## 2. Estado da arte (organizado por eixos)

### 2.1 Modelos de microrredes e eletromobilidade
A literatura sobre microrredes para EV charging foca em:
- limitação de potência de rede (demanda contratada),
- integração PV + BESS,
- atendimento de cargas críticas sob restrições,
- modos **grid-connected** e **islanded**.

**Lacuna específica para o contexto brasileiro rodoviário**:
- interrupções longas (multi-dia),
- limitação severa de rede (ex.: 75 kW),
- necessidade explícita de **serviço mínimo** em cenários críticos.

### 2.2 Otimização de operação (scheduling)
A abordagem dominante é MILP, com:
- balanço de potência,
- dinâmica de SOC,
- limite de potência,
- eficiência,
- curtailment de PV,
- load shedding controlado.

### 2.3 Confiabilidade e continuidade
A confiabilidade costuma ser modelada por:
- **ENS (Energy Not Supplied)**,
- penalização de load shedding,
- restrições de atendimento mínimo.

Aplicado ao eletroposto: traduz-se em **energia de recarga não atendida**, **sessões não atendidas** e **nível mínimo de serviço** durante contingências.

### 2.4 Incerteza (PV, demanda EV e falhas de rede)
Estratégias mais comuns:
- otimização estocástica por cenários,
- robust optimization,
- chance constraints.

No caso do eletroposto:
- PV é variável (meteorologia),
- demanda EV é aleatória,
- falhas longas da rede são eventos críticos com grande impacto.

### 2.5 Degradação de bateria (custo de ciclo)
Modelagens usuais:
- custo linear por throughput (simples e robusto),
- custo por ciclos equivalentes,
- modelos não lineares (DoD, SOC).

Para manter o modelo tratável, recomenda-se começar com **custo linear**, e depois introduzir **piecewise linear** se necessário.

---

## 3. Metodologia (encadeamento Gurobi → microrrede)

A metodologia evolui em **modelos incrementais**, inspirados nos exemplos de *Battery Scheduling* da Gurobi, mas compatibilizados com a realidade de eletropostos.

### Modelo 1 — Rede limitada (baseline)
- **Cenário**: somente rede (sem PV/BESS)
- **Restrição**: 0 ≤ P_grid,t ≤ 75 kW
- **Saídas**: ENS, atendimento mínimo

### Modelo 2 — PV + rede limitada
- adiciona geração PV com curtailment
- avalia redução de ENS

### Modelo 3 — PV + BESS + rede
- inclui dinâmica SOC, eficiência, limites de potência
- permite arbitragem tarifária e suporte à carga EV

### Modelo 4 — Falhas multi-dia (modo ilhado)
- P_grid,t = 0 em janelas de falha
- avaliação de autonomia e atendimento mínimo

---

## 4. Métricas de avaliação técnica

- **ENS (Energy Not Supplied)** [kWh]
- **Taxa de atendimento** = 1 − (ENS / demanda total)
- **PNS máximo** [kW]
- **Autonomia em modo ilhado** (horas/dias)
- **Uso do BESS** (throughput, DoD médio)
- **Dependência da rede** (energia comprada e pico)

---

## 5. Compatibilização com dados reais (tabela de mapeamento)

| Variável do Modelo | Unidade | Fonte de dados típica | Ajuste para realidade brasileira |
|---|---|---|---|
| P_load,t (demanda EV) | kW | Logs de carregamento, concessionárias, estudos ANEEL | Converter sessões em perfil horário | 
| P_pv,t (geração PV) | kW | PVGIS, INPE, dados meteorológicos locais | Aplicar performance ratio e perdas | 
| P_grid,max | kW | Contrato de demanda / limites do alimentador | Fixar em 75 kW (cenário) | 
| SOC_min / SOC_max | % | Datasheet BESS | Usar limites de garantia (ex. 10–90%) | 
| η_c, η_d | - | Datasheet BESS/inversor | Ajustar por condições reais | 
| Falhas de rede | horas/dias | Histórico local de interrupções | Modelar janelas multi-dia | 
| Tarifa energia | R$/kWh | ANEEL ou distribuidora local | Aplicar horários de ponta | 

---

## 6. Encadeamento com publicações e exemplos Gurobi

- **Modeling Examples**: referência base para formulação MILP e gurobipy.
- **Battery Scheduling**: base para dinâmica SOC, arbitragem e custo.
- **Energy Storage/Power Flow examples**: úteis para extensão com PV e limites de rede.

**Metáforas corretas**:
- “Load” no exemplo Gurobi = **demanda total do eletroposto** (EV + carga base).
- “Arbitrage” = **otimização econômica + garantia de atendimento**.
- “Battery degradation” = custo por throughput (aproximação linear).
- “Grid” = rede com limite e falhas de disponibilidade.

---

## 7. Estrutura recomendada para o capítulo de dissertação

1. **Introdução**
2. **Estado da Arte**
3. **Metodologia** (modelos 1–4)
4. **Estudo de Caso**
5. **Resultados e Discussão**
6. **Conclusões e Trabalhos Futuros**

---

## 8. Observações finais

Este documento é um ponto de partida para organizar a revisão de literatura e a metodologia do projeto. A próxima etapa recomendada é **refinar o Modelo 3 e Modelo 4 com dados reais**, incluindo:
- curva horária de recargas,
- perfil PV local,
- histórico de falhas,
- e dimensionamento preliminar do BESS.

Caso deseje, posso:
- inserir referências bibliográficas formais (ABNT/IEEE),
- adicionar figuras de fluxograma do modelo,
- ou preparar os modelos matemáticos em LaTeX.
