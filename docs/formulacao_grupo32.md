# Formulação Matemática — Grupo 32 (Base Implementada + Extensões)

Este documento consolida a formulação adotada no repositório e a alinha ao escopo do Grupo 32: microrredes em eletropostos com PV + BESS + interação com a rede.

## 1) Classe de problema

- Núcleo implementado: **MILP determinístico horário** (24h), com variáveis contínuas de potência/energia e binárias operacionais.
- Extensões documentadas: inclusão de componentes multiobjetivo (custo, emissões e proxy de qualidade de serviço EV) via soma ponderada.

## 2) Função objetivo

A forma geral suportada na implementação é:

\[
\min\; F = \lambda_1 C_{total} + \lambda_2 E_{GEE} + \lambda_3 Q_{idle}
\]

onde:

- \(C_{total} = \sum_t c_t^{buy} P_t^{grid} - \sum_t c_t^{sell} P_t^{export}\)
- \(E_{GEE} = \sum_t \phi_t^{grid} P_t^{grid}\)
- \(Q_{idle} = \sum_t \kappa^{idle} P_{t}^{EV,unserved}\)

Observação: o termo \(Q_{idle}\) é um **proxy linear** para qualidade de serviço de EV quando não há modelagem individual de filas/SOC por veículo.

## 3) Restrições principais

### 3.1 Balanço de potência por período

\[
P_t^{grid} + P_t^{PV} + P_t^{BESS,dis} = (P_t^{dem,com} + P_t^{dem,EV} - P_t^{EV,unserved}) + P_t^{BESS,ch} + P_t^{export}
\]

### 3.2 Dinâmica do SOC do BESS

\[
SOC_t = SOC_{t-1} + \eta^{ch} P_t^{BESS,ch} - \frac{1}{\eta^{dis}} P_t^{BESS,dis}
\]

com limites: \(SOC^{min} \le SOC_t \le SOC^{max}\).

### 3.3 Limites de potência

\[
0 \le P_t^{BESS,ch} \le P^{ch,max},\quad 0 \le P_t^{BESS,dis} \le P^{dis,max}
\]

### 3.4 Lógica binária (MILP)

- Sem carga/descarga simultânea no BESS.
- Sem importação/exportação simultânea na rede (Big-M).

## 4) O que já está no código

- Objetivo ponderado com pesos configuráveis em YAML (`pesos_objetivo`).
- Binárias operacionais para evitar simultaneidades físicas indesejadas.
- Decomposição de objetivo exportada para `summary.txt`.

## 5) Próximas extensões (roadmap técnico)

1. **Estocástico por cenários**: índice \(\omega\), probabilidades \(\pi_\omega\), e forma equivalente determinística.
2. **Dimensionamento (CAPEX)**: variáveis de capacidade (`Cap_PV`, `Cap_BESS`, número de carregadores) e anualização de investimento.
3. **Modelagem EV explícita**: SOC por veículo, janela de conexão, metas de partida e/ou fila de atendimento.
4. **Epsilon-constraint** para frente de Pareto multicritério.

## 6) Referências-base (ABNT simplificada)

- SANTOS, C. *Otimização da Localização e Dimensionamento de Estações de Recarga de Veículos Elétricos*. Tese (Doutorado) — UNICAMP, 2025.
- TERADA, L. Z. et al. Multi-objective optimization for microgrid sizing, electric vehicle scheduling and vehicle-to-grid integration. *Sustainable Energy, Grids and Networks*, v. 43, 2025.
- SANTOS, L. H. S. *Modelagem e Simulação das Microrredes Piloto do Projeto MERGE-UNICAMP*. Dissertação (Mestrado) — UNICAMP, 2022.
- GRUPO 32. *Microrredes em Eletropostos: Garantia de Segurança Energética...* Projeto de Pesquisa, UNICAMP, 2025.
