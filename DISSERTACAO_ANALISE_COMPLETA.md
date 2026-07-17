# Análise técnico-econômica de eletropostos rápidos em corredor rodoviário paulista

## Resumo

Este texto-base apresenta uma estrutura de dissertação para avaliação de infraestrutura de recarga rápida de veículos elétricos em rodovias brasileiras. O estudo combina localização de estações, restrições de atendimento, custos de conexão, tarifas horossazonais, geração fotovoltaica e armazenamento estacionário.

## 1. Introdução

A eletrificação veicular altera a demanda por energia em corredores logísticos e turísticos. A implantação de eletropostos rápidos exige compatibilização entre conveniência do usuário, disponibilidade de rede, custos de capital, sinal tarifário e qualidade de energia.

## 2. Metodologia

O problema foi estruturado como planejamento de cobertura em corredor. Cada candidato possui posição quilométrica, demanda diária estimada, distância até a rede e capacidade disponível. A solução de referência seleciona pontos que respeitam espaçamento máximo aproximado e capacidade mínima.

## 3. Dados de entrada

Os dados foram consolidados no arquivo `dados_eletropostos_brasil.dat`, com 15 trechos, 10 candidatos, 6 períodos tarifários e parâmetros técnicos compatíveis com estudos acadêmicos no Brasil.

## 4. Resultados simulados

A execução de `main_execucao.py` gera `resultados_brasil_simulados.json`. A configuração de referência seleciona estações distribuídas ao longo do corredor e estima investimento, pontos de recarga, potência fotovoltaica, bateria e valor presente líquido.

## 5. Discussão

A tarifa de ponta aumenta o valor de estratégias de deslocamento de carga. Sistemas fotovoltaicos e baterias devem ser avaliados conjuntamente, pois a geração ao meio-dia pode ser armazenada para reduzir compras em períodos críticos. A viabilidade é sensível à adoção de veículos elétricos, preço de venda da recarga, custo de capital e disponibilidade de conexão.

## 6. Conformidade e boas práticas

Em dissertações e relatórios técnicos, recomenda-se separar premissas normativas, dados de mercado, estimativas próprias e resultados do modelo. A rastreabilidade é essencial para atender boas práticas de pesquisa, auditoria acadêmica e padrões ABNT.

## 7. Conclusões

O pacote oferece base reprodutível para análises de cenários. A aplicação final deve recalibrar tarifas, fluxos de veículos, custos de equipamentos e restrições de rede para a região e ano de estudo.
