# Microgrid MILP Reconstruction Template (Terada 2024/2025)

Template executável em Pyomo para reconstrução incremental dos modelos dos artigos de 2024 (EPSR) e 2025 (SEGAN).

## Escopo coberto
- Conjuntos: tempo, cenários, contingências, EVs.
- Variáveis de sizing: PV, BESS, TG e número de conectores EVCS.
- Variáveis operacionais: despacho, SOC, compra/venda da rede, curtailment.
- Restrições: balanço de potência, dinâmica BESS/EV, capacidade EVCS e contingência.
- Multiobjetivo via epsilon-constraint (custo minimizado com limites em GHG e idle time).

## Estrutura
```text
microgrid-model/
├── data/
│   └── parameters.yaml
├── model/
│   ├── build_model.py
│   ├── constraints.py
│   ├── objective.py
│   ├── parameters.py
│   ├── sets.py
│   └── variables.py
├── nash_solution.py
├── pareto.py
└── solve.py
```

## Instalação
```bash
pip install pyomo pyyaml pandas numpy
```

Para solver:
- Recomendado: gurobi
- Alternativas: cplex, cbc, glpk

## Execução
Resolver um ponto (com epsilon default do YAML):
```bash
python microgrid-model/solve.py --solver cbc
```

Gerar fronteira Pareto (grid simples):
```bash
python microgrid-model/pareto.py --solver cbc --ghg-grid 4 --idle-grid 4
```

Resolver barganha de Nash a partir de um CSV com utilidades:
```bash
python microgrid-model/nash_solution.py --input microgrid-model/results/pareto_points.csv
```

## Observações
- Este template prioriza reprodutibilidade e legibilidade para dissertação/tese.
- Ajuste `data/parameters.yaml` com os dados reais (CampusGrid e séries horárias) para replicação fiel.
