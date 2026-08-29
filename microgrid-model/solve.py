import argparse
import json
from pathlib import Path

import yaml
from pyomo.environ import SolverFactory, value

from model import build_model


def load_data(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="microgrid-model/data/parameters.yaml")
    parser.add_argument("--solver", default="cbc")
    args = parser.parse_args()

    data = load_data(Path(args.data))
    model = build_model(data)

    solver = SolverFactory(args.solver)
    result = solver.solve(model, tee=False)

    out = {
        "solver_status": str(result.solver.status),
        "termination": str(result.solver.termination_condition),
        "total_cost": value(model.total_cost),
        "ghg_total": value(model.ghg_total),
        "idle_time_total": value(model.idle_time_total),
        "lambda_pv": value(model.lambda_pv),
        "lambda_bess": value(model.lambda_bess),
        "lambda_tg": value(model.lambda_tg),
        "n_evcs": value(model.n_evcs),
    }

    Path("microgrid-model/results").mkdir(parents=True, exist_ok=True)
    Path("microgrid-model/results/solve_summary.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
