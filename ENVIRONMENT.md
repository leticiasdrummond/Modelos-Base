# Environment Metadata

## Sistema
- SO: Linux (container)
- Shell: bash
- Python: 3.10.19

## Solver e modelagem
- Modelagem: Pyomo
- Solver principal: CBC
- Solvers alternativos: HiGHS / Gurobi (quando disponíveis)

## Reprodutibilidade
- Dependências listadas em `requirements.txt`
- Cenários parametrizados em `configs/*.yaml`
- Execução padrão por `src/run_scenario.py`

## Coleta automática recomendada
Para registrar snapshots do ambiente, execute e anexe o resultado em `docs/`:

```bash
python --version
pip freeze > docs/pip_freeze.txt
cbc -stop
```
