# Changelog

Este arquivo registra mudanças relevantes de estrutura, modelagem, dados e reprodutibilidade.

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

### Notes
- Próxima etapa: extração incremental de funções dos notebooks para módulos menores (`src/model/`, `src/io/`, `src/plots/`).
