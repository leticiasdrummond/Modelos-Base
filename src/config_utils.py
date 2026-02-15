from __future__ import annotations

from typing import Iterable


SERIES_KEYS = (
    "demanda_comercio",
    "demanda_ev",
    "geracao_pv",
    "tarifa_compra",
    "tarifa_venda",
)


def _require_keys(cfg: dict, keys: Iterable[str]) -> None:
    missing = [k for k in keys if k not in cfg]
    if missing:
        raise ValueError(f"Configuração incompleta. Chaves ausentes: {missing}")


def validate_config(cfg: dict) -> None:
    _require_keys(
        cfg,
        [
            "horizonte_horas",
            *SERIES_KEYS,
            "bess_capacidade",
            "bess_pot_carga_max",
            "bess_pot_descarga_max",
            "bess_soc_inicial",
            "bess_soc_min",
            "bess_soc_max",
            "bess_eficiencia",
        ],
    )

    n = int(cfg["horizonte_horas"])
    if n <= 0:
        raise ValueError("'horizonte_horas' deve ser positivo.")

    for key in SERIES_KEYS:
        if len(cfg[key]) != n:
            raise ValueError(f"'{key}' deve ter tamanho {n}.")

    eta = float(cfg["bess_eficiencia"])
    if not (0 < eta <= 1):
        raise ValueError("'bess_eficiencia' deve estar em (0, 1].")

    soc_min = float(cfg["bess_soc_min"])
    soc_ini = float(cfg["bess_soc_inicial"])
    soc_max = float(cfg["bess_soc_max"])
    cap = float(cfg["bess_capacidade"])

    if not (soc_min <= soc_ini <= soc_max):
        raise ValueError("Deve valer: bess_soc_min <= bess_soc_inicial <= bess_soc_max.")
    if soc_max > cap:
        raise ValueError("'bess_soc_max' não pode exceder 'bess_capacidade'.")

    # Bloco opcional: função objetivo multiobjetivo por soma ponderada.
    if "pesos_objetivo" in cfg:
        _require_keys(cfg["pesos_objetivo"], ["custo", "emissoes", "ociosidade_ev"])
