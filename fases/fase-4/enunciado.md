# 1. Atividade Integradora — Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia (SIGIC)

Nesta fase, cada equipe deverá desenvolver um **Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia (SIGIC)**. O objetivo será representar computacionalmente a infraestrutura da Aurora Siger e otimizar o funcionamento da rede energética e operacional da base.

A atividade deverá utilizar **exclusivamente** os conteúdos estudados até essa fase, como:

- Grafos e algoritmos de redes;
- BFS (Busca em largura);
- DFS (Busca em profundidade);
- Algoritmo de Dijkstra;
- Matrizes e listas de adjacência;
- Estruturas de dados em Python;
- Listas, matrizes, tuplas e dicionários;
- Modelagem matemática;
- Cálculo diferencial aplicado;
- Otimização computacional;
- Armazenamento e distribuição de energia;
- Redes inteligentes (smart grids);
- Sustentabilidade e governança ESG.

## 1.1 Organização da infraestrutura da colônia

Cada equipe deverá definir um conjunto de módulos da base marciana, como:

- **Habitação:** responsável pela acomodação da tripulação e suporte básico à sobrevivência humana;
- **Centro de controle:** responsável pelo monitoramento e gerenciamento das operações da colônia;
- **Armazenamento de energia:** utilizado para armazenar energia produzida pelos sistemas da base;
- **Agricultura:** responsável pela produção de alimentos e suporte à sustentabilidade da colônia;
- **Laboratório científico:** utilizado para pesquisas e análises de materiais e condições marcianas;
- **Comunicação:** responsável pela troca de dados entre módulos e comunicação com a Terra;
- **Suporte médico:** destinado ao atendimento médico e monitoramento da saúde da tripulação;
- **Produção de oxigênio:** responsável pela geração e distribuição de oxigênio para a base.

Cada módulo deverá possuir informações relevantes, como:

- **Consumo energético:** quantidade de energia necessária para o funcionamento do módulo;
- **Prioridade operacional:** nível de importância do módulo para a sobrevivência da colônia;
- **Capacidade de armazenamento:** quantidade de recursos ou energia que o módulo consegue armazenar;
- **Distância entre módulos:** utilizada para calcular rotas e eficiência de distribuição;
- **Necessidade de comunicação:** frequência de troca de informações entre módulos;
- **Status operacional:** situação atual do módulo, como ativo, em manutenção ou em alerta.

## 1.2 Representação da rede utilizando grafos

A infraestrutura deverá ser representada utilizando grafos: os módulos deverão ser tratados como **vértices** e as conexões entre módulos deverão ser representadas como **arestas**.

As equipes deverão:

- Representar visualmente a rede da colônia, criando um mapa computacional das conexões da Aurora Siger;
- Definir pesos para conexões, utilizando valores relacionados à distância, consumo energético ou tempo de transmissão;
- Justificar a estrutura da rede criada, explicando as escolhas realizadas para organização da infraestrutura.

## 1.3 Implementação de algoritmos de redes

As equipes deverão implementar algoritmos capazes de:

- Identificar caminhos mínimos, encontrando as rotas mais eficientes entre módulos;
- Explorar a rede, analisando como os módulos estão conectados;
- Otimizar rotas, reduzindo desperdícios de energia ou tempo de comunicação;
- Detectar conexões críticas, identificando pontos da rede que podem comprometer a infraestrutura;
- Analisar eficiência operacional, avaliando o desempenho da rede criada.

Os algoritmos poderão utilizar **BFS, DFS e Dijkstra** e a implementação deverá ser feita em **Python**.

## 1.4 Estruturas de dados em Python

Os dados da infraestrutura deverão ser organizados utilizando:

- **Listas:** para armazenar conjuntos de módulos ou conexões da rede;
- **Matrizes:** para representar relações entre módulos e conexões;
- **Tuplas:** para armazenar informações fixas relacionadas aos módulos;
- **Dicionários:** para organizar dados utilizando chave e valor.

As equipes deverão justificar a escolha das estruturas utilizadas.

## 1.5 Modelagem matemática e otimização

Cada equipe deverá modelar matematicamente pelo menos um fenômeno relacionado à infraestrutura da colônia. Exemplos:

- Crescimento do consumo energético, analisando como o aumento da infraestrutura impacta o consumo da base;
- Eficiência da distribuição de energia, avaliando a capacidade da rede em distribuir energia de forma equilibrada;
- Perda energética da rede, identificando desperdícios ao longo das conexões entre módulos;
- Comportamento operacional da infraestrutura, analisando o desempenho geral da colônia ao longo do tempo.

A modelagem deverá apresentar:

- **Fórmula utilizada:** representação matemática do fenômeno escolhido;
- **Explicação das variáveis:** significado de cada elemento presente na função;
- **Análise qualitativa da função:** interpretação do comportamento da modelagem;
- **Relação da modelagem com o funcionamento da colônia:** explicando como os resultados impactam a operação da Aurora Siger.

Além disso, os alunos deverão aplicar conceitos de otimização para identificar cenários mais eficientes de operação.

## 1.6 Sustentabilidade e governança da infraestrutura

As equipes deverão elaborar uma análise sobre:

- **Uso sustentável de energia,** propondo formas de reduzir desperdícios energéticos;
- **Expansão organizada da colônia,** planejando o crescimento da infraestrutura de forma eficiente;
- **Priorização de sistemas críticos,** definindo quais módulos devem receber maior atenção operacional;
- **Governança tecnológica,** estabelecendo critérios responsáveis para tomada de decisões computacionais;
- **Redução de desperdícios,** propondo melhorias para aumentar a eficiência da infraestrutura.

---

# 2. Entregáveis

Cada equipe deverá realizar a entrega do projeto por meio de uma pasta compactada (`.zip`) contendo todos os arquivos obrigatórios do trabalho.

## 2.1 Vídeo de apresentação do projeto

Cada equipe deverá gravar um vídeo de **até 5 minutos**, apresentando o projeto e demonstrando o seu funcionamento. Apenas um dos membros da equipe precisa estar no vídeo. Além disso, o vídeo deverá ser publicado no YouTube como **"Não listado"**.

Durante a execução, a equipe deverá apresentar obrigatoriamente:

- Descrição da infraestrutura da colônia;
- Representação da rede utilizando grafos;
- Explicação dos algoritmos utilizados;
- Descrição das estruturas de dados utilizadas;
- Modelagem matemática desenvolvida;
- Reflexão sobre sustentabilidade e governança;
- Demonstração prática do funcionamento do sistema em Python.

## 2.2 Requisitos do sistema desenvolvido

O sistema entregue pela equipe deverá conter:

- Representação computacional da rede;
- Estruturas de dados utilizadas;
- Algoritmos implementados;
- Simulações realizadas;
- Organização e comentários no código.

Além disso, o sistema deverá apresentar:

- Menu simples de navegação no terminal;
- Dados organizados de forma clara;
- Comentários explicando as principais partes do código;
- Exemplos de execução das funcionalidades implementadas;
- Mensagens de entrada e saída compreensíveis para o usuário.

As funcionalidades implementadas deverão permitir:

- Visualizar a rede da colônia;
- Consultar módulos;
- Executar algoritmos de caminhos mínimos;
- Simular situações operacionais da infraestrutura.

> **Exemplo de funcionalidade esperada:** ao selecionar o módulo "Centro Médico", o sistema poderá identificar automaticamente o caminho mais eficiente para envio de energia a partir do módulo "Armazenamento de Energia", utilizando o algoritmo de Dijkstra para calcular a melhor rota da rede.

Durante a apresentação em vídeo, a equipe deverá demonstrar o funcionamento real do sistema.

## 2.3 Arquivos obrigatórios na entrega (`.zip`)

A pasta compactada `.zip` deverá conter, obrigatoriamente, os seguintes arquivos, com os respectivos formatos e nomes padronizados:

- **`codigo_fonte.py`:** arquivo principal do sistema, contendo o código-fonte em Python;
- **`arquivos_auxiliares/`:** pasta com arquivos auxiliares utilizados pelo sistema, caso existam, como bases de dados, arquivos de apoio ou outros recursos necessários para a execução;
- **`rede_colonia.pdf`:** imagem, diagrama ou esquema visual da rede da colônia em um arquivo PDF;
- **`documentacao_complementar.pdf`:** arquivo em PDF com documentação complementar, caso a equipe tenha utilizado;
- **`link_video.txt`:** arquivo de texto contendo o link do vídeo da apresentação publicado no YouTube como "Não listado".

**Importante:**

- Todos os arquivos devem estar organizados de forma clara dentro da pasta `.zip`;
- Caso o projeto possua mais de um arquivo Python, a equipe deverá manter os nomes organizados e intuitivos, deixando evidente qual é o arquivo principal de execução;
- O arquivo principal do sistema deverá estar identificado de forma clara para facilitar a correção.

## 2.4 Regras técnicas

O código deverá ser executado sem a necessidade de bibliotecas avançadas ou frameworks externos, utilizando apenas recursos compatíveis com os conteúdos estudados até essa fase.

---

# 3. Critérios de Avaliação (10 pontos totais)

| Critério | Descrição | Pontuação |
| --- | --- | --- |
| Integração das disciplinas | Capacidade de integrar os conteúdos da fase ao projeto | 2,0 |
| Organização computacional | Estrutura e coerência do sistema desenvolvido | 2,0 |
| Aplicação dos algoritmos | Uso correto de grafos e algoritmos de redes | 2,5 |
| Estruturas de dados | Organização e utilização adequada das estruturas aprendidas em Python | 1,5 |
| Sustentabilidade e governança | Aplicação dos conceitos ESG na infraestrutura da colônia | 2,0 |
| **Total** | | **10,0** |

*Tabela 1 — Critérios de avaliação*
*Fonte: Elaborada pelo autor (2026)*
