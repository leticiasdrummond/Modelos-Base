from pyomo.environ import Var, NonNegativeReals, NonNegativeIntegers


def declare_variables(model):
    # Sizing
    model.lambda_pv = Var(within=NonNegativeReals)
    model.lambda_bess = Var(within=NonNegativeReals)
    model.lambda_tg = Var(within=NonNegativeReals)
    model.n_evcs = Var(within=NonNegativeIntegers)

    # Operation per (t,s,c)
    model.p_pv = Var(model.T, model.S, model.C, within=NonNegativeReals)
    model.p_tg = Var(model.T, model.S, model.C, within=NonNegativeReals)
    model.p_bess_c = Var(model.T, model.S, model.C, within=NonNegativeReals)
    model.p_bess_d = Var(model.T, model.S, model.C, within=NonNegativeReals)
    model.e_bess = Var(model.T, model.S, model.C, within=NonNegativeReals)

    model.p_ev_c = Var(model.T, model.S, model.C, model.EV, within=NonNegativeReals)
    model.p_ev_d = Var(model.T, model.S, model.C, model.EV, within=NonNegativeReals)
    model.e_ev = Var(model.T, model.S, model.C, model.EV, within=NonNegativeReals)

    model.p_grid_import = Var(model.T, model.S, model.C, within=NonNegativeReals)
    model.p_grid_export = Var(model.T, model.S, model.C, within=NonNegativeReals)
    model.load_shed = Var(model.T, model.S, model.C, within=NonNegativeReals)
    model.pv_curtailment = Var(model.T, model.S, model.C, within=NonNegativeReals)

    # KPIs
    model.ghg_total = Var(within=NonNegativeReals)
    model.idle_time_total = Var(within=NonNegativeReals)
    model.total_cost = Var(within=NonNegativeReals)
