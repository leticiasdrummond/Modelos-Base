import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def minmax_normalize(series: pd.Series, reverse: bool = False):
    low, high = series.min(), series.max()
    if np.isclose(high, low):
        return pd.Series(1.0, index=series.index)
    values = (series - low) / (high - low)
    return 1 - values if reverse else values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="microgrid-model/results/pareto_points.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    # Como custo/GHG/idle são objetivos de minimização, utilidade = 1 - normalização.
    df["U_cost"] = minmax_normalize(df["cost"], reverse=True)
    df["U_ghg"] = minmax_normalize(df["ghg"], reverse=True)
    df["U_idle"] = minmax_normalize(df["idle"], reverse=True)

    # Ponto de desacordo: pior utilidade observada.
    u0_cost = df["U_cost"].min()
    u0_ghg = df["U_ghg"].min()
    u0_idle = df["U_idle"].min()

    gains = (
        (df["U_cost"] - u0_cost + 1e-9)
        * (df["U_ghg"] - u0_ghg + 1e-9)
        * (df["U_idle"] - u0_idle + 1e-9)
    )
    df["nash_gain"] = gains

    best = df.loc[df["nash_gain"].idxmax()]

    Path("microgrid-model/results").mkdir(parents=True, exist_ok=True)
    df.to_csv("microgrid-model/results/pareto_with_nash.csv", index=False)
    best.to_frame().T.to_csv("microgrid-model/results/nash_point.csv", index=False)

    print("Nash point:")
    print(best)


if __name__ == "__main__":
    main()
