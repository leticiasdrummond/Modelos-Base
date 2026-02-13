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

## Variáveis de decisão (saída do modelo)

| Campo | Tipo | Unidade | Descrição |
|---|---|---:|---|
| `grid_import[t]` | float | kWh/h | Energia importada da rede em `t` |
| `grid_export[t]` | float | kWh/h | Energia exportada para rede em `t` |
| `bess_charge[t]` | float | kWh/h | Carga da bateria em `t` |
| `bess_discharge[t]` | float | kWh/h | Descarga da bateria em `t` |
| `soc[t]` | float | kWh | Estado de carga da bateria em `t` |
| `objective_value` | float | R$ | Custo total minimizado no horizonte |

## Regras de validação recomendadas

1. Comprimento das séries horárias igual a `horizonte_horas`.
2. Valores não negativos para demanda e geração.
3. `0 < bess_eficiencia <= 1`.
4. `bess_soc_min <= bess_soc_inicial <= bess_soc_max`.
5. `bess_soc_max <= bess_capacidade`.
