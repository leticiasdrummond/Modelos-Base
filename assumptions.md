# Assumptions (Assunções de Modelagem)

## Escopo temporal e granularidade
- **A1**: Horizonte de otimização de 24 horas com passo de 1 hora.
- **A2**: Todos os perfis de demanda, geração FV e tarifa são determinísticos no horizonte diário.

## Sistema elétrico
- **A3**: O sistema pode importar energia da rede em qualquer hora, limitado apenas por restrições do modelo.
- **A4**: Exportação de energia para rede é permitida e remunerada por tarifa definida no cenário.
- **A5**: Perdas na rede interna do comércio não são modeladas explicitamente.

## BESS
- **A6**: A bateria possui limites fixos de potência de carga/descarga e capacidade energética.
- **A7**: Eficiência de carga/descarga é tratada de forma agregada por parâmetro de eficiência.
- **A8**: SOC inicial e final são definidos por cenário e devem ser fisicamente factíveis.
- **A9**: Degradação da bateria não é modelada explicitamente no objetivo (sem custo de ciclo nesta versão).

## Eletroposto e cargas
- **A10**: A demanda do eletroposto é considerada exógena e deve ser plenamente atendida.
- **A11**: Não há flexibilidade temporal de carga (sem deslocamento de demanda) nesta versão.

## Formulação e solução
- **A12**: Modelo MILP resolvido com CBC (alternativamente HiGHS/Gurobi, quando disponível).
- **A13**: Solução ótima depende da consistência das unidades e dos limites de parâmetros.

## Visualização e análise
- **A14**: Gráficos e tabelas são pós-processamento e não alteram a solução do otimizador.
- **A15**: Resultados são válidos apenas para os cenários de entrada definidos em `configs/`.
