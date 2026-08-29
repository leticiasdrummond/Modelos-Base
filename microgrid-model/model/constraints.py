from pyomo.environ import Constraint, value


def _is_contingency_active(data, c, t):
    start, duration = data["contingency_window"][c]
    return start <= t <= start + duration


def declare_constraints(model, data):
    t_list = sorted(list(model.T.data()))
    t0, tf = t_list[0], t_list[-1]

    def power_balance_rule(m, t, s, c):
        ev_charge = sum(m.p_ev_c[t, s, c, ev] for ev in m.EV)
        ev_discharge = sum(m.p_ev_d[t, s, c, ev] for ev in m.EV)
        return (
            m.p_pv[t, s, c]
            + m.p_tg[t, s, c]
            + m.p_bess_d[t, s, c]
            + ev_discharge
            + m.p_grid_import[t, s, c]
            == m.base_load[t]
            - m.load_shed[t, s, c]
            + m.p_bess_c[t, s, c]
            + ev_charge
            + m.p_grid_export[t, s, c]
        )

    model.power_balance = Constraint(model.T, model.S, model.C, rule=power_balance_rule)

    model.pv_dispatch_limit = Constraint(
        model.T,
        model.S,
        model.C,
        rule=lambda m, t, s, c: m.p_pv[t, s, c] + m.pv_curtailment[t, s, c] == m.lambda_pv * m.pv_factor[t, s],
    )

    model.tg_limit = Constraint(model.T, model.S, model.C, rule=lambda m, t, s, c: m.p_tg[t, s, c] <= m.lambda_tg)

    model.bess_charge_limit = Constraint(
        model.T,
        model.S,
        model.C,
        rule=lambda m, t, s, c: m.p_bess_c[t, s, c] <= m.bess_charge_max,
    )
    model.bess_discharge_limit = Constraint(
        model.T,
        model.S,
        model.C,
        rule=lambda m, t, s, c: m.p_bess_d[t, s, c] <= m.bess_discharge_max,
    )
    model.bess_energy_limit = Constraint(
        model.T,
        model.S,
        model.C,
        rule=lambda m, t, s, c: m.e_bess[t, s, c] <= m.lambda_bess,
    )

    def bess_soc_rule(m, t, s, c):
        idx = t_list.index(t)
        if idx == 0:
            return m.e_bess[t, s, c] == m.initial_bess_soc + m.p_bess_c[t, s, c] - m.p_bess_d[t, s, c]
        t_prev = t_list[idx - 1]
        return m.e_bess[t, s, c] == m.e_bess[t_prev, s, c] + m.p_bess_c[t, s, c] - m.p_bess_d[t, s, c]

    model.bess_soc = Constraint(model.T, model.S, model.C, rule=bess_soc_rule)
    model.bess_cycle = Constraint(model.S, model.C, rule=lambda m, s, c: m.e_bess[tf, s, c] == m.e_bess[t0, s, c])

    def ev_connection_limit_rule(m, t, s, c):
        connected = sum(1 for ev in m.EV if value(m.arrival[ev]) <= t <= value(m.departure[ev]))
        return connected <= m.n_evcs

    model.evcs_limit = Constraint(model.T, model.S, model.C, rule=ev_connection_limit_rule)

    def ev_charge_bound_rule(m, t, s, c, ev):
        if value(m.arrival[ev]) <= t <= value(m.departure[ev]):
            return m.p_ev_c[t, s, c, ev] <= m.ev_pmax_c[ev]
        return m.p_ev_c[t, s, c, ev] == 0

    def ev_discharge_bound_rule(m, t, s, c, ev):
        if value(m.arrival[ev]) <= t <= value(m.departure[ev]):
            return m.p_ev_d[t, s, c, ev] <= m.ev_pmax_d[ev]
        return m.p_ev_d[t, s, c, ev] == 0

    model.ev_charge_bound = Constraint(model.T, model.S, model.C, model.EV, rule=ev_charge_bound_rule)
    model.ev_discharge_bound = Constraint(model.T, model.S, model.C, model.EV, rule=ev_discharge_bound_rule)

    def ev_soc_rule(m, t, s, c, ev):
        idx = t_list.index(t)
        if idx == 0:
            return m.e_ev[t, s, c, ev] == m.ev_soc_init[ev] + m.p_ev_c[t, s, c, ev] - m.p_ev_d[t, s, c, ev]
        t_prev = t_list[idx - 1]
        return m.e_ev[t, s, c, ev] == m.e_ev[t_prev, s, c, ev] + m.p_ev_c[t, s, c, ev] - m.p_ev_d[t, s, c, ev]

    model.ev_soc = Constraint(model.T, model.S, model.C, model.EV, rule=ev_soc_rule)
    model.ev_soc_max = Constraint(
        model.T,
        model.S,
        model.C,
        model.EV,
        rule=lambda m, t, s, c, ev: m.e_ev[t, s, c, ev] <= m.ev_emax[ev],
    )
    model.ev_target_soc = Constraint(
        model.S,
        model.C,
        model.EV,
        rule=lambda m, s, c, ev: m.e_ev[int(value(m.departure[ev])), s, c, ev] >= m.ev_soc_target[ev],
    )

    model.grid_import_limit = Constraint(
        model.T,
        model.S,
        model.C,
        rule=lambda m, t, s, c: m.p_grid_import[t, s, c] <= m.grid_import_max,
    )
    model.grid_export_limit = Constraint(
        model.T,
        model.S,
        model.C,
        rule=lambda m, t, s, c: m.p_grid_export[t, s, c] <= m.grid_export_max,
    )

    def contingency_rule(m, t, s, c):
        if _is_contingency_active(data, c, t):
            return m.p_grid_import[t, s, c] + m.p_grid_export[t, s, c] == 0
        return Constraint.Skip

    model.contingency_islanding = Constraint(model.T, model.S, model.C, rule=contingency_rule)

    def ghg_balance_rule(m):
        return m.ghg_total == sum(
            m.pi_s[s] * m.pi_c[c] * (m.e_grid * m.p_grid_import[t, s, c] + m.e_tg * m.p_tg[t, s, c])
            for t in m.T
            for s in m.S
            for c in m.C
        )

    model.ghg_balance = Constraint(rule=ghg_balance_rule)

    def idle_time_rule(m):
        return m.idle_time_total == sum(
            m.pi_s[s]
            * m.pi_c[c]
            * sum(1 - (m.p_ev_c[t, s, c, ev] + m.p_ev_d[t, s, c, ev]) / (m.ev_pmax_c[ev] + 1e-6) for ev in m.EV)
            for t in m.T
            for s in m.S
            for c in m.C
        )

    model.idle_time_balance = Constraint(rule=idle_time_rule)

    model.epsilon_ghg = Constraint(rule=lambda m: m.ghg_total <= m.eps_ghg_max)
    model.epsilon_idle = Constraint(rule=lambda m: m.idle_time_total <= m.eps_idle_max)
