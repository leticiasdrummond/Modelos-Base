#!/usr/bin/env bash
set -euo pipefail

python src/run_scenario.py --config configs/caso_base.yaml --output results/caso_base
python src/run_scenario.py --config configs/caso_modificado.yaml --output results/caso_modificado

echo "Execução completa. Veja a pasta results/."
