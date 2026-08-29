from pyomo.environ import Constraint, Objective, minimize


def declare_objective(model):
    def total_cost_rule(m):
        capex_total = (
            m.capex_pv * m.lambda_pv
            + m.capex_bess * m.lambda_bess
            + m.capex_tg * m.lambda_tg
            + m.capex_evcs * m.n_evcs
        )

        opex_total = sum(
            m.pi_s[s]
            * m.pi_c[c]
            * (
                m.price_import[t] * m.p_grid_import[t, s, c]
                - m.price_export[t] * m.p_grid_export[t, s, c]
                + m.om_tg * m.p_tg[t, s, c]
                + m.om_bess * (m.p_bess_c[t, s, c] + m.p_bess_d[t, s, c])
                + m.unserved_load_cost * m.load_shed[t, s, c]
            )
            for t in m.T
            for s in m.S
            for c in m.C
        )

        discount = 1 / ((1 + m.discount_rate) ** (m.years - 1))
        return m.total_cost == capex_total + discount * opex_total

    model.total_cost_balance = Constraint(rule=total_cost_rule)
    model.minimize_cost = Objective(expr=model.total_cost, sense=minimize)
