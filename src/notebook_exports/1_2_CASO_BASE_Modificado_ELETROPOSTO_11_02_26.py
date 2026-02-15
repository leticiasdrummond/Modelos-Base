"""Arquivo extraído automaticamente do notebook para rastreabilidade.
NÃO editável manualmente sem sincronização com o notebook de origem.
"""


# %%

# =========================================================

T = range(24) # horizonte horário
'''
# =========================================================
# Caso Base - 1 : Verificado com o Gui em 11/02/2026
# =========================================================

# Demanda do comércio (kWh)
demanda_comercio = [
    6, 6, 6, 6, 7, 8, 10, 12, 14, 15, 16, 17,
    18, 18, 17, 16, 15, 14, 12, 10, 9, 8, 7, 6
]

# Demanda do eletroposto (kWh)
demanda_ev = [
    0, 0, 0, 0, 0, 0,
    5, 8, 10, 6, 4, 2,
    0, 0, 0, 2, 4, 6,
    8, 6, 4, 2, 0, 0
]

# Geração fotovoltaica (kWh)
geracao_pv = [
    0, 0, 0, 0, 0, 0,
    2, 5, 8, 12, 15, 18,
    20, 18, 15, 10, 6, 3,
    1, 0, 0, 0, 0, 0
]
'''
# ============================================================
# DADOS DE ENTRADA CORRIGIDOS (24 HORAS)
# ============================================================

# Demanda do comércio (kW)
# Ajustado para que a soma seja 720 (Média exata = 30 kW)
demanda_comercio = [
    5, 5, 5, 5, 5, 8,            # 00h - 05h (Madrugada baixa)
    12, 25, 40, 50, 60, 65,      # 06h - 11h (Subida manhã)
    65, 60, 55, 50, 45, 40,      # 12h - 17h (Tarde alta)
    35, 30, 25, 15, 10, 5        # 18h - 23h (Descida noite)
]

# Demanda do eletroposto (kW)
# Considera 2 carregadores de 50kW (Max 100kW) com dois picos de uso
demanda_ev = [
    0, 0, 0, 0, 0, 0,            # 00h - 05h
    10, 40, 80, 95, 70, 40,      # 06h - 11h (Pico Manhã ~09h)
    20, 20, 30, 50, 80, 100,     # 12h - 17h (Carga leve tarde -> Início Pico)
    90, 60, 30, 10, 0, 0         # 18h - 23h (Pico Noite ~18h e fim)
]

# Geração fotovoltaica (kW)
# Compatível com sistema de 50 kWp (Pico ao meio-dia)
geracao_pv = [
    0, 0, 0, 0, 0, 0,            # 00h - 05h (Sem sol)
    2, 12, 28, 42, 48, 50,       # 06h - 11h (Amanhecer até pico)
    50, 48, 42, 28, 12, 2,       # 12h - 17h (Pico até anoitecer)
    0, 0, 0, 0, 0, 0             # 18h - 23h (Sem sol)
]

# Custos (R$/kWh)
custo_compra = 0.75
preco_venda = 0.40

# Parâmetros da bateria
capacidade_bess = 50.0      # kWh
potencia_max_bess = 15.0    # kW
soc_min = 0.20 * capacidade_bess
soc_max = 0.95 * capacidade_bess
soc_inicial = 0.50 * capacidade_bess


eta_c = 0.955  # eficiência de carga
eta_d = 0.955  # eficiência de descarga

# Custo de degradação (R$/kWh throughput)
custo_degradacao = 0.08

# %%
# =========================================================
# 2. CRIAÇÃO DO MODELO
# =========================================================

model = pyo.ConcreteModel()

model.T = pyo.Set(initialize=T)

# =========================================================
# 3. VARIÁVEIS DE DECISÃO
# =========================================================

model.P_grid = pyo.Var(model.T, domain=pyo.NonNegativeReals)        # compra da rede
model.P_export = pyo.Var(model.T, domain=pyo.NonNegativeReals)      # venda à rede

model.P_charge = pyo.Var(model.T, domain=pyo.NonNegativeReals)      # carga da bateria
model.P_discharge = pyo.Var(model.T, domain=pyo.NonNegativeReals)  # descarga da bateria

model.SOC = pyo.Var(model.T, domain=pyo.NonNegativeReals)

# Variáveis binárias (bloqueio simultâneo)
model.u_charge = pyo.Var(model.T, domain=pyo.Binary)
model.u_discharge = pyo.Var(model.T, domain=pyo.Binary)

# =========================================================
# 4. FUNÇÃO OBJETIVO
# =========================================================

def objective_rule(m):
    custo_energia = sum(custo_compra * m.P_grid[t] for t in m.T)
    receita_venda = sum(preco_venda * m.P_export[t] for t in m.T)
    custo_deg = sum(
        custo_degradacao * (m.P_charge[t] + m.P_discharge[t])
        for t in m.T
    )
    return custo_energia + custo_deg - receita_venda

model.OBJ = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

# =========================================================
# 5. RESTRIÇÕES
# =========================================================

# 5.1 Balanço de energia
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

model.energy_balance = pyo.Constraint(model.T, rule=energy_balance_rule)


# Implementação da Restrição 4.2: Dinâmica do SOC, com perdas explicitadas
def soc_rule(m, t):
    # Losses associated with charging
    charge_losses_kW = (1 - eta_c) * m.P_charge[t]
    # Losses associated with discharging
    # Power drawn from storage is P_discharge / eta_d
    # So discharge losses are (P_discharge / eta_d) - P_discharge
    discharge_losses_kW = (1/eta_d - 1) * m.P_discharge[t]

    # Net change in SOC = (Energy_Charged_Gross - Charge_Losses) - (Energy_Discharged_Gross + Discharge_Losses)
    # This is equivalent to: (eta_c * P_charge) - (P_discharge / eta_d)

    if t == 0:
        # SOC[t] = soc_inicial + RECARGA_BRUTA - PERDAS_CARGA - (DESCARGA_BRUTA + PERDAS_DESCARGA)
        return m.SOC[t] == soc_inicial + (m.P_charge[t] - charge_losses_kW) - (m.P_discharge[t] + discharge_losses_kW)

    # SOC[t] = SOC[t-1] + RECARGA_BRUTA - PERDAS_CARGA - (DESCARGA_BRUTA + PERDAS_DESCARGA)
    return m.SOC[t] == m.SOC[t-1] + (m.P_charge[t] - charge_losses_kW) - (m.P_discharge[t] + discharge_losses_kW)

# Reatribuindo (ou criando, se não existisse) a restrição soc_dyn no modelo
# O Pyomo pode emitir um WARNING se a restrição já existir, indicando que ela está sendo substituída.
model.soc_dyn = pyo.Constraint(model.T, rule=soc_rule)
# 5.3 Limites de SOC
model.soc_min = pyo.Constraint(model.T, rule=lambda m, t: m.SOC[t] >= soc_min)
model.soc_max = pyo.Constraint(model.T, rule=lambda m, t: m.SOC[t] <= soc_max)
model.soc_amanha = pyo.Constraint(expr= model.SOC[23] >= soc_inicial) #incluido junto do Guilherme para garantir que o BESS esteja minimamente carregado no final das 24h
# 5.4 Limites de potência com binárias
model.charge_limit = pyo.Constraint(
    model.T, rule=lambda m, t: m.P_charge[t] <= potencia_max_bess * m.u_charge[t]
)

model.discharge_limit = pyo.Constraint(
    model.T, rule=lambda m, t: m.P_discharge[t] <= potencia_max_bess * m.u_discharge[t]
)

# 5.5 Bloqueio de carga e descarga simultâneas
model.no_simultaneous = pyo.Constraint(
    model.T, rule=lambda m, t: m.u_charge[t] + m.u_discharge[t] <= 1
)



# =========================================================
# 6. RESOLUÇÃO
# =========================================================

solver = pyo.SolverFactory("cbc")
results = solver.solve(model, tee=False)

# =========================================================
# 7. RESULTADOS
# =========================================================

# Define column names explicitly to avoid hidden character issues
col_demanda_comercio = "Demanda_Comercio".strip()
col_demanda_ev = "Demanda_EV".strip()
col_pv = "PV".strip()
col_grid = "Grid".strip()
col_export = "Export".strip()
col_carga_bess = "Carga_BESS".strip()
col_descarga_bess = "Descarga_BESS".strip()
col_soc = "SOC".strip()
col_hora = "Hora".strip()

df = pd.DataFrame({
    col_hora: list(T),
    col_demanda_comercio: demanda_comercio,
    col_demanda_ev: demanda_ev,
    col_pv: geracao_pv,
    col_grid: [pyo.value(model.P_grid[t]) for t in T],
    col_export: [pyo.value(model.P_export[t]) for t in T],
    col_carga_bess: [pyo.value(model.P_charge[t]) for t in T],
    col_descarga_bess: [pyo.value(model.P_discharge[t]) for t in T],
    col_soc: [pyo.value(model.SOC[t]) for t in T]
})

print(df)
print("Custo total (R$):", pyo.value(model.OBJ))

print(f"Valor da Função Objetivo (Custo Total): R$ {pyo.value(model.OBJ):.2f}")

# %%

# =========================================================
# 8. GRÁFICOS
# =========================================================

plt.figure()
plt.plot(df[col_hora], df[col_soc])
plt.xlabel("Hora")
plt.ylabel("SOC (kWh)")
plt.title("Estado de Carga da Bateria")
plt.grid()
plt.show()

# %%
# Define column names explicitly to avoid hidden character issues
col_demanda_comercio = "Demanda_Comercio".strip()
col_demanda_ev = "Demanda_EV".strip()
col_pv = "PV".strip()
col_grid = "Grid".strip()
col_export = "Export".strip()
col_carga_bess = "Carga_BESS".strip()
col_descarga_bess = "Descarga_BESS".strip()
col_soc = "SOC".strip()
col_hora = "Hora".strip()

plt.figure(figsize=(14, 8))

# Plotando a demanda total
df['Demanda_Total'] = df[col_demanda_comercio] + df[col_demanda_ev]
plt.plot(df[col_hora], df['Demanda_Total'], label='Demanda Total', color='red', linestyle='--', linewidth=2)

# Plotando as fontes de energia
plt.plot(df[col_hora], df[col_pv], label='Geração Fotovoltaica (PV)', color='green', marker='o', markersize=4)
plt.plot(df[col_hora], df[col_grid], label='Compra da Rede', color='blue', marker='x', markersize=4)
plt.plot(df[col_hora], df[col_descarga_bess], label='Descarga da Bateria', color='purple', marker='^', markersize=4)
plt.plot(df[col_hora], df[col_carga_bess], label='Carga da Bateria', color='orange', marker='v', markersize=4)
plt.plot(df[col_hora], df[col_export], label='Venda para a Rede', color='cyan', marker='s', markersize=4)

plt.xlabel('Hora do Dia')
plt.ylabel('Potência (kW)')
plt.title('Fluxo de Carga do Sistema de Energia')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.7)
plt.xticks(df[col_hora])
plt.tight_layout()
plt.show()

# %%
import matplotlib.pyplot as plt
import pandas as pd
from pyomo.environ import *

# Definição do modelo
model = ConcreteModel()
model.T = RangeSet(0, 23) # 24 horas

# Parâmetros
battery_power_max = 5 # potência máxima da bateria (kW)
price_tou = {t: preco for t, preco in enumerate([0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45])}

# Variáveis
model.E_ch = Var(model.T, domain=NonNegativeReals) # energia carregada
model.E_dis = Var(model.T, domain=NonNegativeReals) # energia descarregada

# Variáveis binárias para impedir carga e descarga simultâneas
model.y_ch  = Var(model.T, domain=Binary)
model.y_dis = Var(model.T, domain=Binary)

# Restrições para ligar variáveis contínuas às binárias
model.ChargeLogic = Constraint(model.T, rule=lambda m, t: m.E_ch[t] <= battery_power_max * m.y_ch[t])
model.DischargeLogic = Constraint(model.T, rule=lambda m, t: m.E_dis[t] <= battery_power_max * m.y_dis[t])
model.ExclusiveCharge = Constraint(model.T, rule=lambda m, t: m.y_ch[t] + m.y_dis[t] <= 1)

# Função objetivo: minimizar custo total considerando TOU
model.obj = Objective(expr=sum(price_tou[t] * model.E_ch[t] for t in model.T), sense=minimize)

# Solver
solver = SolverFactory('glpk')
result = solver.solve(model)

# Extrair resultados
hours = list(model.T)
charge = [value(model.E_ch[t]) for t in model.T]
discharge = [value(model.E_dis[t]) for t in model.T]

# Criar DataFrame para visualização
df = pd.DataFrame({'Hora': hours, 'Carga (kW)': charge, 'Descarga (kW)': discharge, 'Preço TOU ($/kWh)': [price_tou[t] for t in hours]})

print(df)

# Gráficos
plt.figure(figsize=(12,6))
plt.plot(df['Hora'], df['Carga (kW)'], label='Carga (kW)', marker='o')
plt.plot(df['Hora'], df['Descarga (kW)'], label='Descarga (kW)', marker='x')
plt.bar(df['Hora'], df['Preço TOU ($/kWh)'], alpha=0.3, label='Preço TOU ($/kWh)')
plt.xlabel('Hora do Dia')
plt.ylabel('Potência / Preço')
plt.title('Carga, Descarga e Preço TOU ao longo do dia')
plt.legend()
plt.grid(True)
plt.show()
