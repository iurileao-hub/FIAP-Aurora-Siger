# Tarefa 5 — Contextualização do MGPEB à Luz da Evolução da Computação

## Enunciado

Produzir uma seção textual relacionando o sistema projetado (MGPEB) com a história e evolução dos computadores, destacando:

- Como os primeiros computadores de propósito geral abriram caminho para sistemas embarcados de alta confiabilidade;
- Quais limitações de hardware seriam típicas de uma missão em Marte (memória, processamento, consumo de energia, tolerância à radiação etc.);
- De que forma essas limitações influenciam as escolhas de algoritmos, estruturas de dados e estratégias de programação adotadas pela equipe.

---

## Provocações para reflexão

As provocações abaixo estão organizadas em três eixos. Não são respostas — são linhas de raciocínio para incubar antes de escrever. A sugestão é explorar pelo menos uma ideia forte de cada eixo e tecer conexões entre elas.

### Eixo 1 — O arco da computação: de máquinas de calcular a sistemas autônomos

O Cap. 7 do material de aula traça a evolução desde as máquinas mecânicas até os processadores modernos. O desafio aqui é construir um arco narrativo que saia desse histórico e chegue ao MGPEB.

- **Babbage como ancestral conceitual.** A Máquina Analítica de Babbage (1837) já possuía os fundamentos de um computador moderno: entrada de dados por cartão perfurado, unidade de memória e programação sequencial de operações. Pense nela não como curiosidade histórica, mas como modelo: o MGPEB é, em essência, um sistema que recebe dados (atributos dos módulos), armazena estado (fila, pilha) e executa sequências de decisão (autorização de pouso). Qual a continuidade conceitual entre os dois?

- **Relés e o princípio que nunca mudou.** O Cap. 7 mostra como arranjos de relés executam somas binárias — o mesmo princípio (chaves eletrônicas organizadas logicamente) que está nos transistores, nos chips e nos processadores atuais. O material conclui: "o computador mantém, desde sua origem, a presença de uma ideia fundamental: chaves eletrônicas organizadas logicamente de modo a permitir a solução de problemas tanto lógicos como aritméticos." Como essa ideia se manifesta na expressão booleana `F AND A AND (L OR E) AND S` que o MGPEB usa para autorizar pousos?

- **Zuse e o Z3 (1941): o primeiro computador binário.** Operava com ponto flutuante, lia programas de fita perfurada, exibia resultados por lâmpadas. Com cerca de 1.400 relés para memória, armazenava apenas 64 números. Mesmo assim, era funcional. Qual paralelo se pode traçar entre a limitação de memória do Z3 (64 números) e a realidade de que o MGPEB gerencia apenas 12 módulos? O que isso diz sobre a relação entre escala do problema e sofisticação do hardware necessário?

- **Turing e a universalidade.** Alan Turing demonstrou (1936) que uma máquina universal pode simular o comportamento de qualquer máquina específica. É por isso que conseguimos prototipar o MGPEB em Python num notebook: a mesma lógica que seria executada por hardware dedicado em Marte pode ser modelada num computador de propósito geral. O que isso revela sobre o valor de um protótipo?

- **ENIAC (1946): escala e energia.** 30 toneladas, 17.840 válvulas, 140 kW de consumo, 180 m². Para executar a lógica booleana do MGPEB, o ENIAC precisaria de uma fração ínfima dos seus recursos — mas as válvulas que falhassem levariam o sistema inteiro. Em Marte, confiabilidade vale mais que velocidade. Essa tensão entre poder e confiabilidade é um fio condutor útil para o arco narrativo.

- **Das válvulas ao microchip — as 5 gerações.** O material organiza a evolução em gerações marcadas pela tecnologia da "chave": relé → válvula → transistor → LSI → VLSI → ULSI. Cada salto reduziu tamanho, consumo e custo, mas aumentou integração. Para o MGPEB, a pergunta é: em qual "geração" de hardware um sistema embarcado marciano provavelmente estaria, e por quê? (Dica: os processadores radiation-hardened usados em Marte hoje são fabricados com tecnologias que seriam consideradas "velhas" pela Lei de Moore terrestre.)

- **Lei de Moore e o paradoxo espacial.** Moore observou (1965) que o número de transistores dobra a cada ~18 meses. Mas processadores espaciais como o RAD750 (usado no rover Perseverance, ~2005) e o RAD5545 ficam "congelados" numa geração por décadas, porque o processo de certificação contra radiação é longo e caro. Marte opera numa versão da Lei de Moore com delay de 10-15 anos. O que isso implica para as decisões de algoritmo?

### Eixo 2 — Limitações de hardware em Marte e suas consequências

Este eixo conecta o conhecimento teórico da aula com o cenário fictício da missão. As limitações abaixo são reais — baseadas nos rovers e sondas marcianas existentes.

- **Radiação cósmica e bit-flips.** Marte não tem magnetosfera. Partículas de alta energia podem inverter bits na memória (single-event upsets). Processadores radiation-hardened (como o RAD750: 200 MHz, 256 MB RAM) são ~10x mais lentos que equivalentes comerciais. Consequência para o MGPEB: algoritmos devem ser simples, determinísticos e verificáveis — exatamente o perfil de um Bubble Sort com n=12 ou uma expressão booleana sem ramificações imprevisíveis.

- **Delay de comunicação.** O sinal Terra-Marte leva de 4 a 24 minutos em cada sentido, dependendo da posição orbital. Em situações de pouso, que acontecem em minutos, não há tempo para consultar a Terra. O MGPEB precisa ser autônomo. Isso muda a natureza do sistema: ele não é apenas uma ferramenta de apoio, é um decisor. Pense em como isso se conecta com a questão da responsabilidade algorítmica (que será explorada na reflexão ESG).

- **Energia como moeda.** Os painéis solares de um módulo como o que projetamos geram ~600 W em condições ideais. Tempestades de poeira podem reduzir isso drasticamente (o rover Spirit morreu por falta de energia solar). Cada ciclo de CPU custa energia. O(n²) com n=12 ≈ 144 operações — trivial. O(n!) com n=12 ≈ 479 milhões — inviável num contexto de energia restrita. A complexidade algorítmica deixa de ser questão acadêmica e se torna questão de sobrevivência.

- **Memória escassa e estruturas de dados.** Dicionários em Python são estruturas ricas que consomem memória significativa (hash tables internas). Num sistema marciano real, os módulos seriam representados por structs compactas em C, com alocação estática. O protótipo em Python simula a lógica, não a restrição de memória — mas vale refletir: a busca linear que escolhemos (em vez de hash tables ou árvores binárias) é, por acidente, mais próxima do que um sistema real usaria.

- **Temperatura extrema e calor computacional.** -120°C a +20°C na superfície. Eletrônica precisa de aquecimento ativo. Num ambiente gelado, o calor gerado por processamento intensivo poderia, paradoxalmente, ser útil. Mas processamento excessivo em momentos de calor seria desperdício. A janela operacional do MGPEB é ditada pela termodinâmica, não apenas pela lógica.

### Eixo 3 — Conexão com as escolhas feitas no protótipo

Este é o eixo mais pessoal: liga a teoria ao código que você escreveu.

- **Por que Bubble Sort e Selection Sort fazem sentido aqui** — não por serem "bons" algoritmos, mas por serem previsíveis. Em sistemas críticos, o importante é que o comportamento seja determinístico: sem alocação dinâmica, sem recursão profunda, sem surpresas no pior caso. Com 12 elementos, a diferença entre O(n log n) e O(n²) é irrelevante; a diferença entre "previsível" e "pode falhar" é tudo.

- **Por que busca linear é a escolha certa para 12 módulos.** Árvores balanceadas ou hash tables têm overhead de memória e implementação. Para 12 itens, busca linear é O(n) = 12 comparações no pior caso. A simplicidade é uma feature, não uma limitação.

- **Por que expressões booleanas para decisões críticas.** `F AND A AND (L OR E) AND S` executa em tempo constante, é determinística, e pode ser auditada por inspeção visual. Em sistemas de segurança, a capacidade de demonstrar formalmente que o algoritmo faz o que deveria fazer é mais valiosa que performance.

- **Fila e pilha com listas — a questão do `pop(0)`.** Em Python, `pop(0)` é O(n) porque desloca todos os elementos. Com n=12, isso é irrelevante. Mas num sistema real em C, a fila seria implementada como buffer circular em memória fixa — O(1) para enqueue e dequeue, sem alocação dinâmica. Vale mencionar essa diferença entre o protótipo e a implementação real.

- **O protótipo como Máquina de Turing aplicada.** Retomando Turing: o fato de que o MGPEB roda no seu notebook prova que a lógica é independente do hardware. O protótipo valida as decisões de engenharia; a implementação final seria outra linguagem, outro processador, outro paradigma — mas a mesma lógica booleana, a mesma fila, a mesma pilha de alertas.
