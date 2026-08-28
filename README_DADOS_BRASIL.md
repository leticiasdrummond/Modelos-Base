# Dados brasileiros para otimização de eletropostos rápidos

Este repositório contém um pacote mínimo e reprodutível para estudos acadêmicos de alocação ótima de estações de recarga rápida no corredor Campinas--Ribeirão Preto--Franca--Divisa MG, com parâmetros ajustados ao contexto brasileiro.

## Arquivos principais

- `dados_eletropostos_brasil.dat`: parâmetros em sintaxe compatível com Pyomo/AMPL.
- `REVISAO_DADOS_NORMATIVOS_BRASIL.md`: justificativa técnica, normativa e bibliográfica.
- `modelo_eletropostos.py`: modelo simplificado de planejamento econômico-operacional.
- `main_execucao.py`: rotina de carregamento, simulação determinística e geração de JSON.
- `resultados_brasil_simulados.json`: exemplo de saída validável.
- `DISSERTACAO_ANALISE_COMPLETA.md`: texto-base acadêmico em formato próximo a dissertação.
- `RESUMO_EXECUTIVO.md`: síntese dos resultados.
- `GUIA_ARQUIVOS.md`: mapa de uso dos arquivos.

## Uso rápido

```bash
python main_execucao.py
```

O script não exige solver externo para a simulação de referência. Para modelos completos em Pyomo, use `dados_eletropostos_brasil.dat` como arquivo de dados e substitua o arquivo original no script de otimização:

```python
data_file = "dados_eletropostos_brasil.dat"
```

## Premissas brasileiras adotadas

| Parâmetro | Valor adotado | Observação |
|---|---:|---|
| Carregador DC | 60 kW | Faixa compatível com implantação inicial em rodovias brasileiras. |
| Bateria média VE | 55 kWh | Média conservadora para frota nacional eletrificada. |
| Autonomia operacional | 280 km | Margem para relevo, clima, carga e degradação. |
| Estação com 4 pontos | R$ 600.000 | Inclui equipamento, infraestrutura elétrica, obra civil e automação. |
| Tarifa de ponta | R$ 1,42/kWh | Referência horossazonal para análise de sensibilidade. |

## Checklist acadêmico

- Conferir aderência do problema de pesquisa.
- Atualizar tarifas para a distribuidora e data-base do estudo.
- Validar custos com pelo menos três fornecedores.
- Documentar hipóteses, limites e incertezas.
- Citar normas e fontes conforme ABNT NBR 6023.
