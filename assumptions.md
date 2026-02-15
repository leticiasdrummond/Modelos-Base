# Assumptions (Assunções de Modelagem)

## Escopo temporal e granularidade
- **A1**: Horizonte de otimização de 24 horas com passo de 1 hora.
- **A2**: Todos os perfis de demanda, geração FV e tarifa são determinísticos no horizonte diário.

## Sistema elétrico
- **A3**: O sistema pode importar energia da rede em qualquer hora, limitado por restrições do modelo.
- **A4**: Exportação de energia para rede é permitida e remunerada por tarifa definida no cenário.
- **A5**: Perdas na rede interna do comércio não são modeladas explicitamente.

## BESS
- **A6**: A bateria possui limites fixos de potência de carga/descarga e capacidade energética.
- **A7**: Eficiência de carga/descarga é tratada de forma agregada por parâmetro de eficiência.
- **A8**: SOC inicial é definido por cenário e deve ser fisicamente factível.
- **A9**: Degradação da bateria não é modelada explicitamente no objetivo (sem custo de ciclo nesta versão).
- **A10**: Não é permitido carregar e descarregar o BESS simultaneamente (binária operacional).

## Eletroposto e cargas
- **A11**: A demanda do eletroposto é exógena por hora.
- **A12**: A qualidade de serviço EV é aproximada por uma variável de déficit (`EV_Unserved`) penalizada no objetivo.

## Formulação e solução
- **A13**: Modelo MILP resolvido com CBC (alternativamente HiGHS/Gurobi, quando disponíveis).
- **A14**: Objetivo pode ser multiobjetivo por soma ponderada (custo, emissões, ociosidade EV-proxy).
- **A15**: Não é permitida importação e exportação simultâneas na rede (binária operacional).

## Limites da versão atual
- **A16**: Não há indexação por cenários estocásticos nesta implementação base (apenas determinístico).
- **A17**: Não há dimensionamento de CAPEX endógeno de PV/BESS/carregadores nesta implementação base.
