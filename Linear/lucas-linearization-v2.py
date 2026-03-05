"""Lucas Linearization v2

Modelo MILP linear para alocação ótima de estações de recarga rápida em uma
rede de transporte em larga escala, com análise de cenários e sensibilidade.

Objetivo principal: permitir que toda a análise de planejamento seja executada
em um único pipeline reproduzível (base + cenários + sensibilidade), inspirado
na formulação típica do problema de localização/capacidade de carregadores.

Requer: pulp (CBC por padrão)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import argparse
import csv
import json


try:
    import pulp
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Dependência ausente: instale 'pulp' para resolver o MILP. "
        "Exemplo: pip install pulp"
    ) from exc


# -------------------------
# Estruturas de dados
# -------------------------


@dataclass(frozen=True)
class Node:
    id: str
    fixed_cost: float
    capacity_per_charger: float
    max_chargers: int


@dataclass(frozen=True)
class PathDemand:
    id: str
    flow: float
    energy_required: float
    penalty_unserved: float


@dataclass(frozen=True)
class Incidence:
    path_id: str
    node_id: str


@dataclass(frozen=True)
class ModelInput:
    nodes: List[Node]
    paths: List[PathDemand]
    incidence: List[Incidence]
    charger_cost: float
    budget: float
    service_level_min: float = 0.0


@dataclass(frozen=True)
class Scenario:
    name: str
    demand_multiplier: float = 1.0
    budget_multiplier: float = 1.0
    charger_cost_multiplier: float = 1.0


# -------------------------
# Leitura de dados
# -------------------------


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_model_input(data_dir: Path) -> ModelInput:
    nodes_rows = _read_csv(data_dir / "nodes.csv")
    paths_rows = _read_csv(data_dir / "paths.csv")
    incidence_rows = _read_csv(data_dir / "incidence.csv")
    params_path = data_dir / "params.json"

    params = json.loads(params_path.read_text(encoding="utf-8"))

    nodes = [
        Node(
            id=row["node_id"],
            fixed_cost=float(row["fixed_cost"]),
            capacity_per_charger=float(row["capacity_per_charger"]),
            max_chargers=int(row["max_chargers"]),
        )
        for row in nodes_rows
    ]

    paths = [
        PathDemand(
            id=row["path_id"],
            flow=float(row["flow"]),
            energy_required=float(row["energy_required"]),
            penalty_unserved=float(row["penalty_unserved"]),
        )
        for row in paths_rows
    ]

    incidence = [
        Incidence(path_id=row["path_id"], node_id=row["node_id"])
        for row in incidence_rows
    ]

    return ModelInput(
        nodes=nodes,
        paths=paths,
        incidence=incidence,
        charger_cost=float(params["charger_cost"]),
        budget=float(params["budget"]),
        service_level_min=float(params.get("service_level_min", 0.0)),
    )


# -------------------------
# Modelo MILP linearizado
# -------------------------


def build_and_solve(model_input: ModelInput, solver_msg: bool = False) -> Dict[str, object]:
    nodes = model_input.nodes
    paths = model_input.paths

    node_ids = [n.id for n in nodes]
    path_ids = [p.id for p in paths]

    node_by_id = {n.id: n for n in nodes}
    path_by_id = {p.id: p for p in paths}

    # A[p, i] = 1 se a rota p passa pelo nó i
    A: Dict[Tuple[str, str], int] = {(p, i): 0 for p in path_ids for i in node_ids}
    for e in model_input.incidence:
        if e.path_id not in path_by_id or e.node_id not in node_by_id:
            continue
        A[(e.path_id, e.node_id)] = 1

    m = pulp.LpProblem("fast_charging_allocation", pulp.LpMinimize)

    # Variáveis
    # y_i: abre estação no nó i
    y = pulp.LpVariable.dicts("open", node_ids, lowBound=0, upBound=1, cat="Binary")
    # z_i: número de carregadores instalados no nó i
    z = pulp.LpVariable.dicts("chargers", node_ids, lowBound=0, cat="Integer")
    # s_p: fração de demanda atendida da rota p (lineariza perda/penalidade)
    s = pulp.LpVariable.dicts("served", path_ids, lowBound=0, upBound=1, cat="Continuous")

    # Objetivo: custo fixo + custo variável de carregadores + penalidade de não atendimento
    fixed = pulp.lpSum(node_by_id[i].fixed_cost * y[i] for i in node_ids)
    chargers = pulp.lpSum(model_input.charger_cost * z[i] for i in node_ids)
    unserved_penalty = pulp.lpSum(
        path_by_id[p].penalty_unserved * path_by_id[p].flow * (1 - s[p]) for p in path_ids
    )
    m += fixed + chargers + unserved_penalty

    # Restrições de ligação y-z (linearização padrão)
    for i in node_ids:
        m += z[i] <= node_by_id[i].max_chargers * y[i], f"max_chargers_if_open_{i}"

    # Restrição de capacidade por nó:
    # energia distribuída pelos fluxos atendidos que passam no nó <= capacidade instalada
    for i in node_ids:
        lhs = pulp.lpSum(
            A[(p, i)] * path_by_id[p].flow * path_by_id[p].energy_required * s[p]
            for p in path_ids
        )
        rhs = node_by_id[i].capacity_per_charger * z[i]
        m += lhs <= rhs, f"node_capacity_{i}"

    # Cada rota só pode ser atendida se existir pelo menos uma estação ativa no caminho.
    # s_p <= sum_i A[p,i] * y_i
    for p in path_ids:
        m += s[p] <= pulp.lpSum(A[(p, i)] * y[i] for i in node_ids), f"route_cover_{p}"

    # Nível de serviço mínimo global (opcional)
    if model_input.service_level_min > 0:
        total_flow = sum(path_by_id[p].flow for p in path_ids)
        served_flow = pulp.lpSum(path_by_id[p].flow * s[p] for p in path_ids)
        m += served_flow >= model_input.service_level_min * total_flow, "service_level_min"

    # Orçamento total
    m += fixed + chargers <= model_input.budget, "budget"

    status = m.solve(pulp.PULP_CBC_CMD(msg=solver_msg))
    status_name = pulp.LpStatus.get(status, "Unknown")

    result = {
        "status": status_name,
        "objective": float(pulp.value(m.objective)) if m.objective is not None else None,
        "opened_nodes": [i for i in node_ids if pulp.value(y[i]) > 0.5],
        "chargers_by_node": {i: int(round(pulp.value(z[i]) or 0.0)) for i in node_ids},
        "served_share_by_path": {p: float(pulp.value(s[p]) or 0.0) for p in path_ids},
        "total_served_flow": float(
            sum(path_by_id[p].flow * (pulp.value(s[p]) or 0.0) for p in path_ids)
        ),
        "total_flow": float(sum(path_by_id[p].flow for p in path_ids)),
    }
    return result


# -------------------------
# Cenários e sensibilidade
# -------------------------


def apply_scenario(base: ModelInput, scenario: Scenario) -> ModelInput:
    return ModelInput(
        nodes=base.nodes,
        paths=[
            PathDemand(
                id=p.id,
                flow=p.flow * scenario.demand_multiplier,
                energy_required=p.energy_required,
                penalty_unserved=p.penalty_unserved,
            )
            for p in base.paths
        ],
        incidence=base.incidence,
        charger_cost=base.charger_cost * scenario.charger_cost_multiplier,
        budget=base.budget * scenario.budget_multiplier,
        service_level_min=base.service_level_min,
    )


def run_scenarios(base_input: ModelInput, scenarios: Sequence[Scenario], solver_msg: bool) -> List[Dict[str, object]]:
    output = []
    for sc in scenarios:
        sc_input = apply_scenario(base_input, sc)
        res = build_and_solve(sc_input, solver_msg=solver_msg)
        res["scenario"] = sc.name
        output.append(res)
    return output


def run_budget_sensitivity(
    base_input: ModelInput,
    multipliers: Iterable[float],
    solver_msg: bool,
) -> List[Dict[str, object]]:
    rows = []
    for k in multipliers:
        sc = Scenario(name=f"budget_x{k:g}", budget_multiplier=k)
        inp = apply_scenario(base_input, sc)
        res = build_and_solve(inp, solver_msg=solver_msg)
        rows.append(
            {
                "scenario": sc.name,
                "budget": inp.budget,
                "status": res["status"],
                "objective": res["objective"],
                "served_ratio": (
                    res["total_served_flow"] / res["total_flow"] if res["total_flow"] > 0 else 0.0
                ),
                "opened_nodes": len(res["opened_nodes"]),
            }
        )
    return rows


# -------------------------
# CLI
# -------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa modelagem linear (MILP) de alocação de estações + análises."
    )
    parser.add_argument("--data-dir", type=Path, required=True, help="Diretório com CSVs e params.json")
    parser.add_argument("--output", type=Path, default=Path("results.json"), help="Arquivo de saída JSON")
    parser.add_argument("--solver-msg", action="store_true", help="Mostra logs do solver")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_input = load_model_input(args.data_dir)

    scenarios = [
        Scenario(name="base"),
        Scenario(name="alta_demanda", demand_multiplier=1.2),
        Scenario(name="baixo_orcamento", budget_multiplier=0.85),
        Scenario(name="capex_alto", charger_cost_multiplier=1.15),
    ]

    scenario_results = run_scenarios(base_input, scenarios, solver_msg=args.solver_msg)
    sensitivity = run_budget_sensitivity(
        base_input,
        multipliers=[0.7, 0.85, 1.0, 1.15, 1.3],
        solver_msg=args.solver_msg,
    )

    payload = {
        "scenario_results": scenario_results,
        "budget_sensitivity": sensitivity,
    }

    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Análise concluída. Resultados em: {args.output}")


if __name__ == "__main__":
    main()
