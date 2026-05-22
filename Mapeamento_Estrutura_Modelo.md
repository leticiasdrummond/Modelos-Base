# Mapeamento_Estrutura_Modelo


📁 *Códigos de Caso Eletroposto com BESS.md* 

A organização abaixo explicita **qual parte do código responde a cada item metodológico exigido para registro formal, versionamento e fundamentação científica**.

---
# Sumário
Os itens exigidos para registro formal, versionamento e fundamentação científica estão explícitos na estrutura apresentada no arquivo Versionamento_vers1_2.md, que faz a correspondência entre partes do código e os critérios científicos/metodológicos relevantes. Com base no documento, esses itens são:

### 1. Caracterização do Sistema Energético  
- Tipo de sistema (por exemplo: microgrid conectada à rede)

### 2. Horizonte Temporal e Tipo de Operação  
- Definição do horizonte de tempo (ex: operação diária, modelo determinístico)
- Resolução temporal utilizada

### 3. Natureza da Função Objetivo  
- Quais são os critérios de otimização? (ex: minimização de custo, energia importada, etc.)

### 4. Modelagem do BESS (Battery Energy Storage System)  
- Dinâmica do estado de carga (SOC)
- Limites operacionais
- Exclusividade entre carga e descarga
- Modelagem simplificada ou complexa de degradação
- Outros aspectos relevantes para o armazenamento

### 5. Modelagem da Demanda EV (Veículo Elétrico)  
- Como o perfil de demanda é representado? (determinístico, agregado, estocástico, etc.)

### 6. Restrição Contratual de Potência  
- Limites de potência contratada ou fornecida à rede

### 7. Tipo de Formulação Matemática  
- Identificação do tipo de problema (ex: MILP—Mixed Integer Linear Programming)
- Solver utilizado

### 8. Elementos Ausentes (Lacunas para Evolução)  
- Quais aspectos ainda não são tratados/modelados e podem ser evoluídos

### 9. Correspondência Entre Código e Itens Científicos  
- Tabela ou mapa explicitando onde cada item acima está concretamente implementado no código

### 10. Conclusão Técnica  
- Análise se o código atende aos critérios necessários para registro científico e se pode ser versionado formalmente

Esses itens organizam o processo de documentação, facilitando tanto o registro formal do modelo quanto a rastreabilidade das versões e a fundamentação teórico-científica.
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
# ! Dica de uso:

**Explicação de como esse tipo de arquivo se insere em demais repositórios:**

Arquivos como esse servem como “documentação estruturante” do modelo computacional, conectando explicitamente o código às exigências metodológicas de pesquisa científica e registro formal. Eles cumprem funções estratégicas:

- **Registro formal:** Documentam, de forma rastreável e padronizada, a estrutura lógica-matemática do modelo, facilitando auditoria, certificação e reprodutibilidade.
- **Versionamento científico:** Permitem identificar quais trechos do código correspondem a diferentes versões do modelo (ex: v1, v2, v3), facilitando comparação evolutiva e justificando melhorias implementadas.
- **Fundamentação para publicações:** Servem de referência direta para artigos, dissertações, relatórios técnicos e requisitos de projetos de pesquisa.
- **Comunicação interdisciplinar:** Tornam o modelo compreensível por avaliadores, parceiros e revisores independentemente do domínio de especialidade.
- **Integração com outros repositórios:**  
    - Podem ser usados como referência cruzada, mostrando em cada repositório quais elementos do código respondem a cada exigência científica de maneira clara e transferível.
    - Em repositórios derivados/afins (como cenariosEVCS), ajudam a manter o vínculo metodológico e justificar adaptações específicas do modelo base, promovendo transparência na customização.
    - Facilitam a integração e comparação entre repositórios distintos, mostrando de forma clara quais hipóteses/modelagens estão presentes, ausentes ou modificadas em cada caso.

**Resumo:**  
Inclua esse tipo de arquivo na raiz do repositório (ao lado do README), com nome padronizado e referência à versão do modelo. Em projetos derivados, utilize o arquivo para explicitar adaptações, justificativas e manter o elo documental com o repositório base/original. Isso valoriza o rigor metodológico, a rastreabilidade e o potencial reprodutivo/colaborativo do seu trabalho.
