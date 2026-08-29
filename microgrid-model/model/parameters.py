from pyomo.environ import Param, NonNegativeReals


def _lookup(table, key):
    return table[key] if key in table else table[str(key)]


def _nested_lookup(table, k1, k2):
    t1 = _lookup(table, k1)
    return _lookup(t1, k2)


def declare_parameters(model, data):
    model.discount_rate = Param(initialize=float(data["discount_rate"]))
    model.years = Param(initialize=int(data["years"]))

    model.pi_s = Param(model.S, initialize=lambda m, s: float(_lookup(data["probability_s"], s)), within=NonNegativeReals)
    model.pi_c = Param(model.C, initialize=lambda m, c: float(_lookup(data["probability_c"], c)), within=NonNegativeReals)

    model.base_load = Param(model.T, initialize=lambda m, t: float(_lookup(data["base_load"], t)), within=NonNegativeReals)
    model.pv_factor = Param(
        model.T,
        model.S,
        initialize=lambda m, t, s: float(_nested_lookup(data["pv_factor"], s, t)),
        within=NonNegativeReals,
    )

    model.price_import = Param(model.T, initialize=lambda m, t: float(_lookup(data["price_import"], t)))
    model.price_export = Param(model.T, initialize=lambda m, t: float(_lookup(data["price_export"], t)))

    capex = data["capex"]
    model.capex_pv = Param(initialize=float(capex["pv_per_kw"]))
    model.capex_bess = Param(initialize=float(capex["bess_per_kwh"]))
    model.capex_tg = Param(initialize=float(capex["tg_per_kw"]))
    model.capex_evcs = Param(initialize=float(capex["evcs_per_unit"]))

    om = data["om"]
    model.om_tg = Param(initialize=float(om["tg_per_kwh"]))
    model.om_bess = Param(initialize=float(om["bess_cycle_per_kwh"]))

    emissions = data["emissions"]
    model.e_grid = Param(initialize=float(emissions["grid_per_kwh"]))
    model.e_tg = Param(initialize=float(emissions["tg_per_kwh"]))

    ev = data["ev"]
    model.arrival = Param(model.EV, initialize=lambda m, ev_id: int(_lookup(ev["arrival"], ev_id)))
    model.departure = Param(model.EV, initialize=lambda m, ev_id: int(_lookup(ev["departure"], ev_id)))
    model.ev_soc_init = Param(model.EV, initialize=lambda m, ev_id: float(_lookup(ev["soc_init"], ev_id)))
    model.ev_soc_target = Param(model.EV, initialize=lambda m, ev_id: float(_lookup(ev["soc_target"], ev_id)))
    model.ev_emax = Param(model.EV, initialize=lambda m, ev_id: float(_lookup(ev["emax"], ev_id)))
    model.ev_pmax_c = Param(model.EV, initialize=lambda m, ev_id: float(_lookup(ev["pmax_charge"], ev_id)))
    model.ev_pmax_d = Param(model.EV, initialize=lambda m, ev_id: float(_lookup(ev["pmax_discharge"], ev_id)))

    lim = data["limits"]
    model.tg_max = Param(initialize=float(lim["tg_max"]))
    model.bess_charge_max = Param(initialize=float(lim["bess_charge_max"]))
    model.bess_discharge_max = Param(initialize=float(lim["bess_discharge_max"]))
    model.bess_emax_max = Param(initialize=float(lim["bess_emax_max"]))
    model.grid_import_max = Param(initialize=float(lim["grid_import_max"]))
    model.grid_export_max = Param(initialize=float(lim["grid_export_max"]))
    model.unserved_load_cost = Param(initialize=float(lim["unserved_load_cost"]))

    model.initial_bess_soc = Param(initialize=float(data["initial_states"]["bess_soc"]))

    model.eps_ghg_max = Param(initialize=float(data["epsilon"]["ghg_max"]))
    model.eps_idle_max = Param(initialize=float(data["epsilon"]["idle_max"]))
