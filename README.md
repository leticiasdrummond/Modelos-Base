# Otimização de BESS para Microgrid Comercial com FV e Eletroposto

Repositório para desenvolvimento, análise e reprodução de modelos de otimização energética (MILP) para um pequeno comércio com geração fotovoltaica (FV), sistema de armazenamento em bateria (BESS) e carga de eletroposto.

## Objetivo

Resolver um modelo MILP para operação de microrrede em eletroposto, com base multiobjetivo (custos, emissões e qualidade de serviço EV), respeitando:
- balanço de energia por hora,
- dinâmica de estado de carga (SOC) da bateria,
- limites operacionais da bateria,
- lógica de não simultaneidade (carga/descarga e compra/exportação),
- compra e exportação de energia para a rede.

## Escopo atual

- Modelos em notebooks Jupyter (caso base e caso modificado)
- Estrutura reprodutível com scripts Python em `src/`
- Configuração de cenários em YAML (`configs/`)
- Documentação de hipóteses, dados e ambiente

## Estrutura de pastas

```text
Modelos-Base/
├── notebooks/                # Notebooks originais
├── src/                      # Código modular executável
├── configs/                  # Cenários de entrada (.yaml)
├── data/
│   ├── raw/                  # Dados brutos
│   ├── interim/              # Dados intermediários
│   └── processed/            # Dados tratados
├── results/                  # Saídas (csv, figuras, logs)
├── docs/                     # Documentação complementar
├── scripts/                  # Scripts utilitários/automação
├── assumptions.md
├── changelog.md
├── data_dictionary.md
├── ENVIRONMENT.md
└── requirements.txt
```

## Execução rápida

1. Crie e ative ambiente virtual.
2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Rode um cenário:

```bash
python src/run_scenario.py --config configs/caso_base.yaml --output results/caso_base
```

## Formulação matemática

- Documento técnico: `docs/formulacao_grupo32.md`
- Implementação da formulação: `src/model.py`

## Versionamento científico

- Mudanças de modelagem: `changelog.md`
- Assunções e limitações: `assumptions.md`
- Dicionário de dados: `data_dictionary.md`
- Metadados de ambiente: `ENVIRONMENT.md`

## Versão

Versão inicial proposta: **v0.1** (caso base com eficiência da bateria).
