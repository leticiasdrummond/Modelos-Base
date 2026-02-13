from __future__ import annotations

import pyomo.environ as pyo


def build_model(cfg: dict) -> pyo.ConcreteModel:
    n = int(cfg["horizonte_horas"])
    T = range(n)

    m = pyo.ConcreteModel()
    m.T = pyo.Set(initialize=T)

    demanda_total = [c + e for c, e in zip(cfg["demanda_comercio"], cfg["demanda_ev"])]
    pv = cfg["geracao_pv"]
    buy = cfg["tarifa_compra"]
    sell = cfg["tarifa_venda"]

    eta = float(cfg["bess_eficiencia"])

    m.P_grid = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.P_export = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.P_charge = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.P_discharge = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.SOC = pyo.Var(m.T, bounds=(cfg["bess_soc_min"], cfg["bess_soc_max"]))

    m.obj = pyo.Objective(
        expr=sum(buy[t] * m.P_grid[t] - sell[t] * m.P_export[t] for t in m.T),
        sense=pyo.minimize,
    )

    def balanco_regra(mm, t):
        return (
            mm.P_grid[t] + pv[t] + mm.P_discharge[t]
            == demanda_total[t] + mm.P_charge[t] + mm.P_export[t]
        )

    m.balanco = pyo.Constraint(m.T, rule=balanco_regra)

    def soc_regra(mm, t):
        if t == 0:
            return mm.SOC[t] == cfg["bess_soc_inicial"] + eta * mm.P_charge[t] - (1 / eta) * mm.P_discharge[t]
        return mm.SOC[t] == mm.SOC[t - 1] + eta * mm.P_charge[t] - (1 / eta) * mm.P_discharge[t]

    m.soc_dinamica = pyo.Constraint(m.T, rule=soc_regra)

    m.charge_limit = pyo.Constraint(m.T, rule=lambda mm, t: mm.P_charge[t] <= cfg["bess_pot_carga_max"])
    m.discharge_limit = pyo.Constraint(m.T, rule=lambda mm, t: mm.P_discharge[t] <= cfg["bess_pot_descarga_max"])

    return m
