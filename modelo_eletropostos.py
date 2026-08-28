"""Modelo simplificado para estudos de eletropostos rápidos no Brasil.

O módulo fornece uma heurística transparente para selecionar estações e estimar
indicadores econômicos. Ele foi criado para documentação acadêmica e testes de
consistência; modelos Pyomo completos podem reutilizar o arquivo .dat.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Candidate:
    code: str
    km: float
    demand_kwh_day: float
    grid_capacity_kw: float
    grid_distance_km: float


@dataclass(frozen=True)
class ProjectParameters:
    charger_power_kw: float = 60.0
    chargers_per_station: int = 4
    station_fixed_cost_rs: float = 600_000.0
    grid_connection_cost_rs_km: float = 85_000.0
    pv_cost_rs_kwp: float = 5_000.0
    battery_cost_rs_kwh: float = 2_600.0
    recharge_price_rs_kwh: float = 2.20
    average_energy_tariff_rs_kwh: float = 0.68
    discount_rate: float = 0.10
    horizon_years: int = 8
    annual_demand_growth: float = 0.12
    annual_om_rate: float = 0.035


def select_stations(candidates: Iterable[Candidate], max_spacing_km: float = 120.0) -> list[Candidate]:
    """Select stations by corridor coverage and minimum grid capacity."""
    ordered = sorted(candidates, key=lambda item: item.km)
    selected: list[Candidate] = []
    last_km = -max_spacing_km
    for candidate in ordered:
        if candidate.grid_capacity_kw < 540:
            continue
        if candidate.km - last_km >= max_spacing_km or not selected:
            selected.append(candidate)
            last_km = candidate.km
    if ordered and selected[-1].code != ordered[-1].code:
        selected.append(ordered[-1])
    return selected


def net_present_value(cash_flows: Iterable[float], discount_rate: float) -> float:
    """Calculate net present value from annual cash flows."""
    return sum(flow / ((1 + discount_rate) ** year) for year, flow in enumerate(cash_flows))


def estimate_project(selected: list[Candidate], params: ProjectParameters) -> dict[str, float]:
    """Estimate investment, revenues and NPV for selected stations."""
    station_investment = sum(
        params.station_fixed_cost_rs + params.grid_connection_cost_rs_km * station.grid_distance_km
        for station in selected
    )
    pv_kwp = min(150.0 * len(selected), 375.0)
    battery_kwh = min(500.0 * max(len(selected) - 5, 0), 1_000.0)
    total_investment = station_investment + pv_kwp * params.pv_cost_rs_kwp + battery_kwh * params.battery_cost_rs_kwh

    base_demand_year = sum(station.demand_kwh_day for station in selected) * 365
    annual_cash_flows = [-total_investment]
    for year in range(1, params.horizon_years + 1):
        demand = base_demand_year * ((1 + params.annual_demand_growth) ** (year - 1))
        gross_margin = demand * (params.recharge_price_rs_kwh - params.average_energy_tariff_rs_kwh)
        annual_om = total_investment * params.annual_om_rate
        annual_cash_flows.append(gross_margin - annual_om)

    vpl = net_present_value(annual_cash_flows, params.discount_rate)
    return {
        "stations": float(len(selected)),
        "charging_points": float(len(selected) * params.chargers_per_station),
        "pv_kwp": pv_kwp,
        "battery_kwh": battery_kwh,
        "total_investment_rs": round(total_investment, 2),
        "npv_rs": round(vpl, 2),
    }
