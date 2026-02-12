# Guia prático: projeto de dissertação (mestrado) com filosofia **code-first** para MILP em Python (Pyomo + Gurobi)

Este protocolo foi feito para você tocar a pesquisa de forma **robusta, auditável e reproduzível**, sem travar no “perfeccionismo teórico” no início. A lógica é:

1. implementar uma versão funcional do modelo;
2. experimentar e observar comportamento;
3. voltar à literatura para explicar, justificar e refinar decisões.

---

## 1) Gestão de mudanças e rastreabilidade (Change Management)

Em pesquisa aplicada, o escopo muda: base de dados muda, restrição muda, hipótese muda. Isso é normal — o erro é **não registrar**.

### O que registrar (mínimo obrigatório)
Mantenha um `changelog.md` (ou `decision_diary.md`) com uma entrada por mudança:

- **Data** (`YYYY-MM-DD`)
- **Descrição objetiva** da mudança
- **Motivação** (técnica, bibliográfica, limitação de dados, orientação do orientador)
- **Impacto no código** (arquivos, funções, restrições, parâmetros alterados)
- **Impacto esperado nos resultados** (direção e hipóteses)
- **Status de validação** (testado? pendente?)

### Exemplo de entrada
```md
## 2026-03-15 - Troca da série de tarifa horária
- Mudança: substituição de fonte A por fonte B para preços horários.
- Motivação: fonte A estava com lacunas em 8% das horas.
- Impacto no código: `src/data/load_prices.py`, `configs/base.yaml`.
- Impacto esperado: aumento do custo operacional em cenários com pico noturno.
- Validação: checks de completude e unidade executados com sucesso.
```

### Versionamento de código
- Use Git desde o primeiro notebook/script.
- Faça commits pequenos e temáticos (uma ideia por commit).
- **Nunca apague histórico**: a evolução metodológica é evidência científica.
- Marque versões-chave com tags, por exemplo:
  - `v0.1-modelo-base`
  - `v0.4-dados-revisados`
  - `v1.0-resultados-dissertacao`

---

## 2) Pacote de reprodutibilidade

Seu objetivo é que outra pessoa consiga rodar tudo e chegar no mesmo resultado (ou diferença explicável).

## Estrutura mínima do pacote

### a) Entradas (inputs)
- **Dados brutos de série temporal** (sem sobrescrever).
- **Parâmetros financeiros/técnicos** com fonte e data.
- Arquivo de metadados (`data_dictionary.md`) contendo:
  - unidade,
  - frequência temporal,
  - timezone,
  - regra de imputação,
  - referência bibliográfica/documental.

### b) Ambiente computacional
- `requirements.txt` fixando versões (Pyomo, gurobipy, pandas etc.).
- Opcional recomendado: `python --version` em arquivo `ENVIRONMENT.md`.
- Script único de execução (`run_all.sh` ou `make reproduce`) que:
  1. prepara dados,
  2. roda cenários,
  3. gera tabelas/figuras.

### c) Saídas (outputs)
Salve **dados brutos de resultado** (CSV/Parquet), não só gráfico no notebook.

Padronize campos de saída, por exemplo:
- `run_id`
- `scenario_id`
- `timestamp`
- `variable_name`
- `index_1`, `index_2` (quando aplicável)
- `value`
- `unit`
- `objective_value`
- `solver_status`
- `mip_gap`
- `runtime_sec`

Isso permite reanálise, auditoria e comparação automática.

---

## 3) Boas práticas de desenvolvimento do modelo

## Assunções explícitas
Crie `assumptions.md` com assunções numeradas (`A1`, `A2`, ...):
- descrição curta,
- justificativa,
- impacto esperado,
- como é implementada no código (arquivo + função).

Exemplo:
- `A7`: eficiência do sistema constante em 92% ao longo do dia.

## Nomes semânticos e comentários úteis
Evite nomes opacos (`x1`, `x2`). Prefira:
- `energia_compra_rede[t]`
- `estado_carga_bateria[t]`
- `potencia_carga_maxima`

Comente **o porquê**, não só o o quê.

## Validações intermediárias no notebook/script
Inclua checks automáticos (asserts) para sanidade física e lógica:
- balanço de energia fechando por período;
- variáveis não negativas quando esperado;
- limites de potência respeitados;
- custo total = soma dos componentes.

Exemplo:
```python
assert (df_result["soc"] >= -1e-6).all(), "SOC negativo: violação física"
```

## Código + texto explicativo
- Use notebooks com blocos Markdown ou memos de cálculo em `docs/`.
- Para cada bloco importante: “o que foi feito”, “por que foi feito”, “qual evidência suporta”.
- Isso acelera escrita da metodologia e defesa.

---

## 4) Síntese de insights e análise final

Depois de validar o pipeline, foque em transformar saída numérica em evidência científica.

## Matriz comparativa de cenários
Monte uma tabela consolidada com KPIs por cenário:
- valor da função objetivo,
- CAPEX/OPEX,
- energia importada/exportada,
- fator de utilização,
- emissões (se aplicável),
- tempo computacional e gap.

## Sensibilidade de parâmetros
Varie parâmetros críticos (ex.: preço de energia, eficiência, limite de potência, taxa de desconto):
- análise univariada (tornado/spider plot),
- quando viável, grade 2D para interação de parâmetros.

## Conexão com a literatura
Para cada achado principal:
1. compare direção do efeito com estudos anteriores;
2. discuta divergências (dados, contexto, formulação);
3. explicite contribuição da sua modelagem.

Regra prática: cada conclusão relevante deve ter **evidência computacional + ancoragem bibliográfica**.

---

## 5) Organização física de pastas (modelo recomendado)

```text
projeto-dissertacao/
├── README.md
├── requirements.txt
├── run_all.sh
├── changelog.md
├── assumptions.md
├── data_dictionary.md
├── refs/
│   ├── bibliografia.bib
│   └── notas_leitura/
├── data/
│   ├── raw/                # dados originais (imutáveis)
│   ├── interim/            # dados tratados intermediários
│   └── processed/          # dados prontos para modelo
├── configs/
│   ├── base.yaml
│   ├── scenario_A.yaml
│   └── scenario_B.yaml
├── src/
│   ├── data/
│   ├── model/
│   ├── solver/
│   └── analysis/
├── notebooks/
│   ├── 01_exploracao_dados.ipynb
│   ├── 02_validacao_modelo.ipynb
│   └── 03_analise_cenarios.ipynb
├── results/
│   ├── runs/               # outputs brutos por execução
│   ├── tables/
│   └── figures/
└── docs/
    ├── metodologia.md
    ├── decisoes_modelagem.md
    └── roteiro_defesa.md
```

Dica: use nomes de execução com timestamp + hash curto do commit (ex.: `2026-03-20_14-30_a1b2c3`).

---

## 6) Plano de ação estratégico (passo a passo)

### Fase 1 — Modelo funcional mínimo
1. Implemente objetivo + principais restrições físicas/econômicas.
2. Rode com dataset pequeno (1–7 dias) para depuração rápida.
3. Crie checks automáticos de sanidade.

### Fase 2 — Consolidação metodológica
4. Registre assunções e decisões no `assumptions.md` e `changelog.md`.
5. Leia artigos focados nos blocos que geraram dúvida no código.
6. Ajuste formulação com justificativa explícita (código + referência).

### Fase 3 — Escalonamento experimental
7. Congele um baseline (`tag` no Git).
8. Execute cenários comparáveis com configs separadas.
9. Salve outputs brutos padronizados e metadados do solver.

### Fase 4 — Análise e redação
10. Gere matriz de KPIs e análise de sensibilidade.
11. Conecte resultados à literatura (confirma, complementa ou contradiz?).
12. Congele versão final reprodutível (`v1.0`) com script único de reprodução.

---

## Checklist rápido (protocolo de bolso)

Antes de considerar uma rodada “válida” para dissertação:

- [ ] Mudanças registradas com motivação e impacto.
- [ ] Commit limpo e identificável.
- [ ] Dados de entrada versionados e rastreáveis.
- [ ] Ambiente reproduzível (`requirements.txt`).
- [ ] Saídas brutas salvas (não apenas figuras).
- [ ] Checks de sanidade aprovados.
- [ ] Hipóteses e assunções documentadas.
- [ ] Resultado contextualizado com literatura.

Se esse checklist estiver completo de forma consistente, sua pesquisa tende a ficar **mais defensável, transparente e rápida de escrever**.
