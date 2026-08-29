# Modelos-Base

Este repositório contém materiais-base para reconstrução de modelos MILP aplicados a microgrids.

## Novo template executável
- `microgrid-model/`: template em Pyomo para reconstrução incremental (EPSR 2024 + SEGAN 2025), incluindo:
  - sizing de PV/BESS/TG/EVCS,
  - operação estocástica com cenários/contingências,
  - epsilon-constraint para Pareto,
  - pós-processamento de Nash bargaining.

Consulte `microgrid-model/README.md` para instruções de execução.
