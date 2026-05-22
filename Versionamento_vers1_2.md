A seguir é apresentada a **compilação estruturada do código do anexo**, organizada conforme os itens necessários para caracterização científica, seleção bibliográfica e evolução do modelo.

O conteúdo foi extraído do arquivo:

📁 *Códigos de Caso Eletroposto com BESS.md* 

A organização abaixo explicita **qual parte do código responde a cada item metodológico exigido para registro formal, versionamento e fundamentação científica**.

---

# 1. Caracterização do Sistema Energético

## 1.1 Tipo de Sistema (Microgrid Conectada à Rede)

Trecho que define a natureza grid-connected:

```python
model.P_grid = pyo.Var(model.T, domain=pyo.NonNegativeReals)
model.P_export = pyo.Var(model.T, domain=pyo.NonNegativeReals)
```

O balanço energético confirma operação conectada:

```python
def energy_balance_rule(m, t):
    demanda_total = demanda_comercio[t] + demanda_ev[t]
    return (
        m.P_grid[t]
        + geracao_pv[t]
        + m.P_discharge[t]
        ==
        demanda_total
        + m.P_charge[t]
        + m.P_export[t]
    )
```

**Conclusão metodológica:**
Sistema modelado como microgrid híbrida conectada à rede, com possibilidade de exportação.

---

# 2. Horizonte Temporal e Tipo de Operação

## 2.1 Horizonte Determinístico de Curto Prazo

```python
HORIZONTE = 24
T = range(HORIZONTE)
```

**Caracterização científica:**

* Operação diária
* Modelo determinístico
* Resolução horária

Isso define que a base bibliográfica deve ser de **energy management systems de curto prazo**, não planejamento de expansão anual.

---

# 3. Natureza da Função Objetivo

## 3.1 Modelo v1.0 – Minimização de Custo

```python
def objective_rule(m):
    custo_energia = sum(custo_compra * m.P_grid[t] for t in m.T)
    receita_export = sum(preco_venda * m.P_export[t] for t in m.T)
    custo_deg = sum(custo_degradacao *
                    (m.P_charge[t] + m.P_discharge[t])
                    for t in m.T)
    return custo_energia + custo_deg - receita_export

model.OBJ = pyo.Objective(rule=objective_rule, sense=pyo.minimize)
```

Características:

* Arbitragem energética
* Considera receita de exportação
* Considera custo de degradação simplificado

---

## 3.2 Modelo v2.0 – Minimização de Energia Importada

```python
def obj_rule(model):
    return sum(model.P_grid[t] for t in T)

model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)
```

Caracterização:

* Critério energético puro
* Não considera preços
* Foco em autonomia energética

---

# 4. Modelagem do BESS

## 4.1 Dinâmica do Estado de Carga (SOC)

```python
def soc_rule(m, t):
    if t == 0:
        return m.SOC[t] == (
            soc_inicial
            + eta_c * m.P_charge[t]
            - (m.P_discharge[t] / eta_d)
        )
    return m.SOC[t] == (
        m.SOC[t-1]
        + eta_c * m.P_charge[t]
        - (m.P_discharge[t] / eta_d)
    )
```

## 4.2 Limites Operacionais

```python
model.soc_min = pyo.Constraint(model.T,
    rule=lambda m, t: m.SOC[t] >= soc_min)

model.soc_max = pyo.Constraint(model.T,
    rule=lambda m, t: m.SOC[t] <= soc_max)
```

## 4.3 Exclusividade Carga/Descarga

```python
model.u_charge = pyo.Var(model.T, domain=pyo.Binary)
model.u_discharge = pyo.Var(model.T, domain=pyo.Binary)

model.no_simultaneous = pyo.Constraint(
    model.T,
    rule=lambda m, t:
        m.u_charge[t] + m.u_discharge[t] <= 1
)
```

Classificação científica:

* MILP linear
* Modelo simplificado de degradação
* Sem modelagem eletroquímica
* Sem rampa

---

# 5. Modelagem da Demanda EV

## 5.1 Perfil Determinístico Agregado

```python
demanda_ev = [
   0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0,
   72, 96, 72, 0, 0, 0,
   76, 100, 76, 0, 0, 0
]
```

Características:

* Dois carregadores de 50 kW
* Pico agregado de 100 kW
* Não modela chegada estocástica
* Não modela fila
* Não modela controle individual

---

# 6. Restrição Contratual de Potência

## 6.1 Inclusão de Limite de Demanda

Versão inicial:

```python
demanda_contratada = 75

model.limite_demanda = pyo.Constraint(
    model.T,
    rule=lambda m, t: m.P_grid[t] <= demanda_contratada
)
```

Versão ajustada para viabilidade:

```python
def grid_limit_rule(model, t):
    return model.P_grid[t] <= 130.0

model.grid_limit = pyo.Constraint(T, rule=grid_limit_rule)
```

Interpretação científica:

* Teste de viabilidade estrutural
* Avaliação de adequação do contrato
* Diagnóstico de insuficiência do BESS

---

# 7. Tipo de Formulação Matemática

Identificação no código:

* Variáveis contínuas: `NonNegativeReals`
* Variáveis binárias: `Binary`
* Funções lineares
* Restrições lineares

Classificação:

→ MILP (Mixed Integer Linear Programming)

Solver utilizado:

```python
solver = pyo.SolverFactory("cbc")
```

---

# 8. Elementos Ausentes (Lacunas para Evolução)

Com base no código compilado, NÃO estão modelados:

* Degradação dependente de profundidade de descarga
* Modelagem estocástica da demanda EV
* Tarifação por demanda máxima mensal
* Dimensionamento ótimo do BESS
* CAPEX
* Emissões de carbono
* Formulação multiobjetivo

Esses pontos definem a direção de busca bibliográfica para evolução do modelo.

---

# 9. Correspondência entre Código e Itens de Compilação Científica

| Item Necessário      | Evidência no Código         |
| -------------------- | --------------------------- |
| Tipo de sistema      | Variáveis P_grid e P_export |
| Horizonte temporal   | HORIZONTE = 24              |
| Natureza da operação | Modelo determinístico       |
| Objetivo econômico   | objective_rule              |
| Objetivo energético  | obj_rule                    |
| BESS simplificado    | soc_rule + binárias         |
| Demanda EV agregada  | vetor demanda_ev            |
| Restrição contratual | grid_limit_rule             |
| Tipo matemático      | MILP                        |
| Solver               | CBC                         |

---

# 10. Conclusão Técnica

O código do anexo já fornece base clara para:

* Classificação do problema científico;
* Definição de escopo da literatura necessária;
* Versionamento estruturado (v1 custo, v2 energia, v3 contrato);
* Identificação objetiva das lacunas para publicação.

---

Se desejar, posso agora:

* Mapear cada lacuna a grupos específicos de artigos recomendados;
* Propor versão v3.0 com dimensionamento do BESS;
* Estruturar matriz formal “Melhoria → Fundamentação → Alteração matemática → Impacto esperado”.
