# Data Dictionary

## Entidades principais

| Campo | Tipo | Unidade | Descrição | Origem |
|---|---|---:|---|---|
| `horizonte_horas` | int | h | Número de períodos de otimização | Configuração de cenário |
| `demanda_comercio` | list[float] | kWh/h | Demanda horária do comércio | Entrada do cenário |
| `demanda_ev` | list[float] | kWh/h | Demanda horária do eletroposto | Entrada do cenário |
| `geracao_pv` | list[float] | kWh/h | Geração FV horária | Entrada do cenário |
| `tarifa_compra` | list[float] | R$/kWh | Tarifa de compra da rede por hora | Entrada do cenário |
| `tarifa_venda` | list[float] | R$/kWh | Tarifa de exportação por hora | Entrada do cenário |
| `bess_capacidade` | float | kWh | Capacidade nominal da bateria | Entrada do cenário |
| `bess_pot_carga_max` | float | kW | Limite de potência de carga | Entrada do cenário |
| `bess_pot_descarga_max` | float | kW | Limite de potência de descarga | Entrada do cenário |
| `bess_soc_inicial` | float | kWh | SOC no período inicial | Entrada do cenário |
| `bess_soc_min` | float | kWh | Limite mínimo de SOC | Entrada do cenário |
| `bess_soc_max` | float | kWh | Limite máximo de SOC | Entrada do cenário |
| `bess_eficiencia` | float | adim. | Eficiência (0-1) aplicada ao armazenamento | Entrada do cenário |
| `pesos_objetivo.custo` | float | adim. | Peso do componente econômico | Entrada do cenário |
| `pesos_objetivo.emissoes` | float | adim. | Peso do componente ambiental | Entrada do cenário |
| `pesos_objetivo.ociosidade_ev` | float | adim. | Peso do componente de serviço EV (proxy) | Entrada do cenário |
| `fator_emissao_grid` | list[float] | kgCO2/kWh | Fator de emissão horário da energia da rede | Entrada do cenário |
| `penalidade_oportunidade_ev` | float | R$/kWh | Penalidade associada a EV não atendido | Entrada do cenário |
| `grid_big_m` | float | kW | Constante Big-M para lógica import/export | Entrada do cenário |

## Variáveis de decisão (saída do modelo)

| Campo | Tipo | Unidade | Descrição |
|---|---|---:|---|
| `grid_import[t]` | float | kWh/h | Energia importada da rede em `t` |
| `grid_export[t]` | float | kWh/h | Energia exportada para rede em `t` |
| `bess_charge[t]` | float | kWh/h | Carga da bateria em `t` |
| `bess_discharge[t]` | float | kWh/h | Descarga da bateria em `t` |
| `soc[t]` | float | kWh | Estado de carga da bateria em `t` |
| `ev_unserved[t]` | float | kWh/h | Déficit de atendimento de demanda EV (proxy de serviço) |
| `objective_total` | float | adim. | Valor total da função objetivo ponderada |
| `objective_cost` | float | R$ | Componente econômico |
| `objective_ghg` | float | kgCO2 | Componente ambiental |
| `objective_idle` | float | R$ | Componente de serviço EV-proxy |

## Regras de validação recomendadas

1. Comprimento das séries horárias igual a `horizonte_horas`.
2. Valores não negativos para demanda e geração.
3. `0 < bess_eficiencia <= 1`.
4. `bess_soc_min <= bess_soc_inicial <= bess_soc_max`.
5. `bess_soc_max <= bess_capacidade`.
6. Se `pesos_objetivo` existir, deve conter `custo`, `emissoes`, `ociosidade_ev`.
