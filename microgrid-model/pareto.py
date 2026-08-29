import argparse
from pathlib import Path

import pandas as pd
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
    parser.add_argument("--ghg-grid", type=int, default=5)
    parser.add_argument("--idle-grid", type=int, default=5)
    args = parser.parse_args()

    base_data = load_data(Path(args.data))
    ghg_max = float(base_data["epsilon"]["ghg_max"])
    idle_max = float(base_data["epsilon"]["idle_max"])

    ghg_values = [ghg_max * i / max(args.ghg_grid - 1, 1) for i in range(args.ghg_grid)]
    idle_values = [idle_max * i / max(args.idle_grid - 1, 1) for i in range(args.idle_grid)]

    rows = []
    solver = SolverFactory(args.solver)

    for ghg_eps in ghg_values:
        for idle_eps in idle_values:
            data = load_data(Path(args.data))
            data["epsilon"]["ghg_max"] = ghg_eps
            data["epsilon"]["idle_max"] = idle_eps
            model = build_model(data)
            result = solver.solve(model, tee=False)
            rows.append(
                {
                    "eps_ghg": ghg_eps,
                    "eps_idle": idle_eps,
                    "status": str(result.solver.termination_condition),
                    "cost": value(model.total_cost),
                    "ghg": value(model.ghg_total),
                    "idle": value(model.idle_time_total),
                }
            )

    out = pd.DataFrame(rows)
    Path("microgrid-model/results").mkdir(parents=True, exist_ok=True)
    out.to_csv("microgrid-model/results/pareto_points.csv", index=False)
    print(out.head())


if __name__ == "__main__":
    main()
