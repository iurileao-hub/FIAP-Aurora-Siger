# Atividade Integradora – Módulo de Gerenciamento de Pouso e Estabilização de Base (MGPEB)

Nessa fase, as equipes deverão projetar e documentar um **Módulo de Gerenciamento de Pouso e Estabilização de Base (MGPEB)** para a missão Aurora Siger. O objetivo é simular, de forma coerente e tecnicamente fundamentada, como seria o sistema responsável por organizar pousos de módulos da colônia, gerenciar informações principais da operação e estabelecer diretrizes de governança em uma colônia nascente em Marte.

A atividade deverá ser desenvolvida com base exclusivamente nos conteúdos já trabalhados até essa fase, articulando:

- Portas lógicas e funções booleanas;
- Estruturas avançadas de lógica e programação em Python;
- Estruturas lineares (listas, pilhas e filas);
- Algoritmos clássicos de busca e ordenação;
- Modelagem de funções aplicadas;
- Histórico e evolução da computação;
- Princípios de governança ambiental, social e corporativa (ESG).

## Tarefas

Cada equipe deverá:

### 1. Modelar o cenário de pouso e fila de módulos

- Definir, em conjunto, um conjunto de módulos de pouso (por exemplo: habitação, energia, laboratório científico, logística e suporte médico);
- Para cada módulo, descrever atributos básicos que serão utilizados ao longo da atividade, como: prioridade de pouso, nível de combustível, massa, criticidade da carga e horário estimado de chegada à órbita;
- Organizar esses módulos em estruturas de dados lineares adequadas:
  - Uma fila (queue) principal de módulos aguardando autorização de pouso;
  - Listas auxiliares para módulos já pousados, em espera ou em situação de alerta.

### 2. Definir e representar regras de decisão usando portas lógicas

- Especificar condições críticas para autorizar ou bloquear o pouso de um módulo, com base em variáveis como combustível, condições atmosféricas simuladas, disponibilidade da área de pouso e integridade dos sensores;
- Traduzir essas condições em expressões booleanas e representá-las por meio de diagramas com portas lógicas (AND, OR, NOT, entre outras), indicando visualmente como o sistema decide se um pouso será autorizado ou adiado.

### 3. Implementar, em Python, um protótipo do MGPEB

Desenvolver um script em Python que:

- Cadastre os módulos definidos pela equipe em estruturas lineares (listas, filas e pilhas);
- Implemente algoritmos de busca para localizar rapidamente módulos com determinada característica (por exemplo: menor combustível, maior prioridade e determinado tipo de carga);
- Aplique algoritmos de ordenação para reorganizar a fila de pouso conforme os critérios escolhidos;
- Simule a autorização de pouso com base nas regras lógicas definidas, utilizando estruturas condicionais (IF, ELIF e ELSE) que reflitam as funções booleanas modeladas anteriormente.

O código deve ser simples, bem comentado e coerente com os conteúdos vistos até o momento, sem utilização de bibliotecas avançadas além das necessárias para entrada, saída e manipulação básica de dados.

### 4. Modelar funções matemáticas aplicadas ao pouso ou estabilização da base

- Escolher pelo menos um fenômeno físico ou operacional relevante para o pouso ou para a estabilização da base (por exemplo: altura em função do tempo de descida, variação da temperatura externa com o tempo, consumo de combustível em função da velocidade ou geração de energia solar ao longo do dia);
- Representar esse fenômeno por meio de funções matemáticas compatíveis com o conteúdo da disciplina (função linear, quadrática, exponencial etc.), indicando a fórmula utilizada, o significado dos parâmetros e uma análise qualitativa do gráfico (incluindo o que acontece quando as variáveis aumentam ou diminuem);
- Relacionar essa modelagem às decisões de engenharia do MGPEB, argumentando, por exemplo, como a função auxilia na definição do melhor momento para acionar retrofoguetes, abrir paraquedas ou limitar a quantidade de módulos pousando ao mesmo tempo.

### 5. Contextualizar o MGPEB à luz da evolução da computação

Produzir uma seção textual relacionando o sistema projetado com a história e evolução dos computadores, destacando:

- Como os primeiros computadores de propósito geral abriram caminho para sistemas embarcados de alta confiabilidade;
- Quais limitações de hardware seriam típicas de uma missão em Marte (memória, processamento, consumo de energia, tolerância à radiação etc.);
- De que forma essas limitações influenciam as escolhas de algoritmos, estruturas de dados e estratégias de programação adotadas pela equipe.

### 6. Incorporar princípios ESG à concepção da base Aurora

Elaborar uma reflexão sobre como a colônia deverá operar sob uma perspectiva de governança ambiental, social e corporativa, respondendo, entre outras, questões como:

- Que tipo de critérios deveriam orientar a escolha da área de pouso, considerando impactos no ambiente marciano?
- Como a gestão de energia, resíduos, produção e uso de recursos locais poderia ser estruturada de forma sustentável?
- Que mecanismos de governança, transparência e participação poderiam ser adotados para garantir que decisões sobre o uso de tecnologia e recursos sejam éticas e responsáveis, mesmo em um ambiente de fronteira como Marte?

## Entregáveis

Cada equipe deverá entregar:

1. **Relatório técnico em PDF** (5 a 10 páginas), contendo:
   - Descrição do cenário de pouso e dos módulos definidos;
   - Diagrama(s) de portas lógicas com as principais regras de decisão;
   - Modelagem das funções matemáticas escolhidas, com explicações e análises;
   - Seção de contextualização histórica/arquitetural do sistema;
   - Seção de reflexão sobre ESG e governança na base Aurora Siger.
2. **Código fonte em Python** (.py), contendo o protótipo do MGPEB organizado, comentado e executável com exemplos simples.
3. **Anexo de estruturas de dados** (pode ser parte do relatório), descrevendo como listas, filas e pilhas foram utilizadas no projeto, com exemplos concretos.

## Critérios de Avaliação

15 pontos totais, distribuídos entre:

| Critério | Descrição |
|----------|-----------|
| Relatório técnico em PDF | Completude, coerência técnica e qualidade textual |
| Código fonte em Python | Organização, comentários e funcionalidade |
| Anexo de estruturas de dados | Clareza e exemplos concretos |

> *Fonte: Elaborada pelo autor (2026)*
