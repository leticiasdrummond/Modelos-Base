# Changelog

Este arquivo registra mudanças relevantes de estrutura, modelagem, dados e reprodutibilidade.

## [v0.2.0] - 2026-02-15

### Added
- Documento técnico `docs/formulacao_grupo32.md` com formulação MILP do Grupo 32, objetivo multiobjetivo e roadmap de extensões (estocástico, CAPEX e EV explícito).
- Validação de configuração extraída para `src/config_utils.py` com checagens de consistência e bloco opcional para pesos de objetivo.
- Novos parâmetros de cenário em `configs/*.yaml`: `pesos_objetivo`, `fator_emissao_grid`, `penalidade_oportunidade_ev`, `grid_big_m`.

### Changed
- `src/model.py` atualizado para:
  - função objetivo ponderada (custo + emissões + proxy de ociosidade EV),
  - variáveis binárias para impedir carga/descarga simultâneas no BESS,
  - variáveis binárias para impedir importação/exportação simultâneas na rede,
  - variável `P_ev_unserved` como proxy linear de qualidade de serviço EV.
- `src/run_scenario.py` atualizado para reaproveitar validação central e exportar decomposição do objetivo no `summary.txt`.

## [v0.1.0] - 2026-02-13

### Added
- Estrutura profissional de pastas (`notebooks`, `src`, `configs`, `data/*`, `results`, `docs`, `scripts`).
- Documentação de base: `README.md`, `assumptions.md`, `data_dictionary.md`, `ENVIRONMENT.md`.
- Cenários YAML iniciais para caso base e caso modificado.
- Script executável standalone para reproduzir cenário (`src/run_scenario.py`).
- Script de execução em lote (`run_all.sh`).
- Dependências fixadas em `requirements.txt`.

### Changed
- Notebooks originais movidos para `notebooks/` para separar prototipação de código de produção.
