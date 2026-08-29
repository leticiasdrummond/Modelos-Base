from pyomo.environ import Set


def declare_sets(model, data):
    model.T = Set(initialize=data["time_periods"], ordered=True)
    model.S = Set(initialize=data["scenarios"], ordered=True)
    model.C = Set(initialize=data["contingencies"], ordered=True)
    model.EV = Set(initialize=data["evs"], ordered=True)
