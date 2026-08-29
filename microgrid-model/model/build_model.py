from pyomo.environ import ConcreteModel

from .constraints import declare_constraints
from .objective import declare_objective
from .parameters import declare_parameters
from .sets import declare_sets
from .variables import declare_variables


def build_model(data):
    model = ConcreteModel()
    declare_sets(model, data)
    declare_parameters(model, data)
    declare_variables(model)
    declare_constraints(model, data)
    declare_objective(model)
    return model
