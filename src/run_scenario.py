from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pyomo.environ as pyo
import yaml

from model import build_model


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_config(cfg: dict) -> None:
    n = int(cfg["horizonte_horas"])
    for key in ["demanda_comercio", "demanda_ev", "geracao_pv", "tarifa_compra", "tarifa_venda"]:
        if len(cfg[key]) != n:
            raise ValueError(f"'{key}' deve ter tamanho {n}.")


def solve(cfg: dict, solver_name: str = "cbc") -> pyo.ConcreteModel:
    model = build_model(cfg)
    solver = pyo.SolverFactory(solver_name)
    result = solver.solve(model, tee=False)
    if result.solver.termination_condition not in [pyo.TerminationCondition.optimal, pyo.TerminationCondition.feasible]:
        raise RuntimeError(f"Solver terminou com status inesperado: {result.solver.termination_condition}")
    return model


def export_results(model: pyo.ConcreteModel, cfg: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "dispatch.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Hora", "Grid", "Export", "Carga_BESS", "Descarga_BESS", "SOC"])
        for t in model.T:
            writer.writerow([
                t,
                pyo.value(model.P_grid[t]),
                pyo.value(model.P_export[t]),
                pyo.value(model.P_charge[t]),
                pyo.value(model.P_discharge[t]),
                pyo.value(model.SOC[t]),
            ])

    summary = out_dir / "summary.txt"
    summary.write_text(
        f"scenario={cfg.get('name','sem_nome')}\nobjective={pyo.value(model.obj):.6f}\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa cenário MILP de microgrid comercial.")
    parser.add_argument("--config", required=True, type=Path, help="Caminho para YAML do cenário.")
    parser.add_argument("--output", required=True, type=Path, help="Diretório de saída para resultados.")
    parser.add_argument("--solver", default="cbc", help="Solver Pyomo (ex.: cbc, highs, gurobi).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    validate_config(cfg)
    model = solve(cfg, solver_name=args.solver)
    export_results(model, cfg, args.output)
    print(f"✅ Cenário '{cfg.get('name', 'sem_nome')}' executado. Resultados em: {args.output}")


if __name__ == "__main__":
    main()
