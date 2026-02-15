from __future__ import annotations

import pyomo.environ as pyo


def build_model(cfg: dict) -> pyo.ConcreteModel:
    n = int(cfg["horizonte_horas"])

    m = pyo.ConcreteModel()
    m.T = pyo.RangeSet(0, n - 1)

    demanda_total = [c + e for c, e in zip(cfg["demanda_comercio"], cfg["demanda_ev"])]
    pv = cfg["geracao_pv"]
    buy = cfg["tarifa_compra"]
    sell = cfg["tarifa_venda"]
    eta = float(cfg["bess_eficiencia"])

    # Pesos da FO multiobjetivo (soma ponderada).
    weights = cfg.get("pesos_objetivo", {"custo": 1.0, "emissoes": 0.0, "ociosidade_ev": 0.0})
    w_cost = float(weights.get("custo", 1.0))
    w_ghg = float(weights.get("emissoes", 0.0))
    w_idle = float(weights.get("ociosidade_ev", 0.0))

    # Fatores/penalidades para objetivos adicionais.
    fator_emissao = cfg.get("fator_emissao_grid", [0.0] * n)
    penalidade_oportunidade_ev = float(cfg.get("penalidade_oportunidade_ev", 0.0))

    # Variáveis principais.
    m.P_grid = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.P_export = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.P_charge = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.P_discharge = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.SOC = pyo.Var(m.T, bounds=(cfg["bess_soc_min"], cfg["bess_soc_max"]))

    # Variável de déficit (proxy de ociosidade/nível de serviço EV).
    m.P_ev_unserved = pyo.Var(m.T, domain=pyo.NonNegativeReals)

    # Binárias para evitar operação simultânea.
    m.y_bess_charge = pyo.Var(m.T, domain=pyo.Binary)
    m.y_grid_import = pyo.Var(m.T, domain=pyo.Binary)

    m.obj_cost = pyo.Expression(expr=sum(buy[t] * m.P_grid[t] - sell[t] * m.P_export[t] for t in m.T))
    m.obj_ghg = pyo.Expression(expr=sum(fator_emissao[t] * m.P_grid[t] for t in m.T))
    m.obj_idle = pyo.Expression(expr=sum(penalidade_oportunidade_ev * m.P_ev_unserved[t] for t in m.T))

    m.obj = pyo.Objective(expr=w_cost * m.obj_cost + w_ghg * m.obj_ghg + w_idle * m.obj_idle, sense=pyo.minimize)

    def balanco_regra(mm, t):
        return (
            mm.P_grid[t] + pv[t] + mm.P_discharge[t]
            == demanda_total[t] - mm.P_ev_unserved[t] + mm.P_charge[t] + mm.P_export[t]
        )

    m.balanco = pyo.Constraint(m.T, rule=balanco_regra)

    def soc_regra(mm, t):
        if t == 0:
            return mm.SOC[t] == cfg["bess_soc_inicial"] + eta * mm.P_charge[t] - (1 / eta) * mm.P_discharge[t]
        return mm.SOC[t] == mm.SOC[t - 1] + eta * mm.P_charge[t] - (1 / eta) * mm.P_discharge[t]

    m.soc_dinamica = pyo.Constraint(m.T, rule=soc_regra)

    m.charge_limit = pyo.Constraint(m.T, rule=lambda mm, t: mm.P_charge[t] <= cfg["bess_pot_carga_max"])
    m.discharge_limit = pyo.Constraint(m.T, rule=lambda mm, t: mm.P_discharge[t] <= cfg["bess_pot_descarga_max"])

    # Não atender mais carga EV do que a própria demanda EV.
    m.ev_unserved_limit = pyo.Constraint(m.T, rule=lambda mm, t: mm.P_ev_unserved[t] <= cfg["demanda_ev"][t])

    # Evita carga/descarga simultânea do BESS.
    m.bess_charge_logic = pyo.Constraint(
        m.T, rule=lambda mm, t: mm.P_charge[t] <= cfg["bess_pot_carga_max"] * mm.y_bess_charge[t]
    )
    m.bess_discharge_logic = pyo.Constraint(
        m.T, rule=lambda mm, t: mm.P_discharge[t] <= cfg["bess_pot_descarga_max"] * (1 - mm.y_bess_charge[t])
    )

    # Evita compra e exportação simultâneas (Big-M simples).
    grid_big_m = float(cfg.get("grid_big_m", max(demanda_total) + max(cfg["geracao_pv"]) + cfg["bess_pot_descarga_max"]))
    m.grid_import_logic = pyo.Constraint(m.T, rule=lambda mm, t: mm.P_grid[t] <= grid_big_m * mm.y_grid_import[t])
    m.grid_export_logic = pyo.Constraint(m.T, rule=lambda mm, t: mm.P_export[t] <= grid_big_m * (1 - mm.y_grid_import[t]))

    return m
