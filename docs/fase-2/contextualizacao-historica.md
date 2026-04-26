# Quando a limitação é o que torna o sinal limpo

*Contextualização histórica e arquitetural do MGPEB*

---

O processador que conduziria o pouso dos módulos da Aurora Siger em Marte seria mais lento que o smartphone de qualquer membro da colônia. O RAD750 — chip *radiation-hardened* (endurecido contra radiação) usado pela NASA em diversas missões até o atual rover [Perseverance](https://mars.nasa.gov/mars2020/) — opera a até 200 MHz, ordem de grandeza abaixo de processadores comerciais modernos. Lê-se aqui, à primeira vista, uma limitação. Mas a leitura precisa girar: o que parece atraso é a manifestação explícita de uma hierarquia de valores que sistemas críticos terrestres já carregam — controle de tráfego aéreo, marca-passos, unidades de controle automotivas — e que o excesso de recurso na Terra disfarça.

Este texto argumenta que a computação tem uma base lógica formal que torna a *função* independente do substrato físico, mas suas *propriedades não-funcionais* — energia, calor, falhas, radiação — permanecem radicalmente acopladas ao substrato. Essa dupla natureza é o que torna possível e necessário hierarquizar valores no projeto de sistemas. Quando o substrato é hostil e o custo de falha é catastrófico, a hierarquia sai do disfarce: confiabilidade verificável vence performance bruta. O MGPEB exemplifica o que a computação se parece quando esse valor é assumido como primário.

---

## Da máquina mecânica à lógica formal

A linhagem que torna o MGPEB possível não começa nem termina em Charles Babbage. A Máquina Analítica (1837) separou pela primeira vez memória, operação e controle — fundação arquitetural reconhecível em qualquer computador moderno —, mas tratava de aritmética automatizada, não de pensamento formalizado. A formalização do raciocínio começa duas décadas depois, com [George Boole](https://www.gutenberg.org/ebooks/15114) e a álgebra do raciocínio dedutivo (1854); avança com Frege ainda no século XIX e com o programa de Hilbert nas décadas seguintes; e atinge o ponto decisivo nos anos 1930, quando Gödel demonstra os limites internos da formalização e [Alonzo Church](https://www.jstor.org/stable/2371045) e [Alan Turing](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf), em 1936, respondem em paralelo ao *Entscheidungsproblem*.

A ponte material entre essas duas tradições — a mecânica de Babbage e a lógica formal de Boole — aparece em 1937. A dissertação de mestrado de [Claude Shannon no MIT](https://dspace.mit.edu/handle/1721.1/11173) demonstrou que circuitos elétricos de chaveamento podem ser descritos pela álgebra booleana sob a abstração liga/desliga. Esse resultado é o que torna o resto da história inteligível. Relés, válvulas, transistores, VLSI e CMOS não são "a mesma chave eletrônica desde sempre" — são realizações materiais distintas de uma estrutura formal comum, e é a estrutura, não o componente, que persiste. As cinco gerações de hardware tradicionalmente descritas não são saltos qualitativos de natureza; são substratos sucessivos de um mesmo formalismo.

## Turing e a dupla natureza

O resultado de Turing costuma ser lido como promessa de liberdade do hardware: uma máquina universal simula qualquer máquina específica. É verdadeiro, e é o que permite que o protótipo do MGPEB rode em Python num *notebook* simulando uma lógica que poderia, em outra realização, rodar embarcada em Marte. Mas a universalidade fala apenas sobre a *função*. O custo físico — energia consumida, calor dissipado, resistência à radiação, probabilidade de falha — é silente na máquina abstrata e ensurdecedor no substrato real.

Daí a tese central. A computação tem uma dupla natureza: a função é desacoplada do substrato — graças ao isomorfismo de Shannon e à universalidade de Turing —, mas as propriedades não-funcionais permanecem nele acopladas. É essa dupla natureza, e não a universalidade pura, que torna possível e necessário hierarquizar valores no projeto. Pode-se escrever a mesma lógica em Python ou em C embarcado; não se pode escolher se ela vai consumir energia, gerar calor ou falhar sob radiação. Isso é decisão do substrato.

## Marte como caso-limite

Marte aplica essa dupla natureza num cenário-limite. A radiação cósmica, na ausência de magnetosfera, provoca *single-event upsets* — bits invertidos espontaneamente em memória ou registradores. O atraso de comunicação Terra-Marte varia de quatro a vinte e quatro minutos por sentido, descartando supervisão humana em fases de pouso que duram poucos minutos. A energia disponível depende de painéis solares vulneráveis a tempestades de poeira — o rover Opportunity foi silenciado por uma em 2018 — ou de geradores termoelétricos de radioisótopos com potência fixa. Cada ciclo de processador pesa.

A resposta da indústria é arquitetural. Processadores como o [RAD750 da BAE Systems](https://www.baesystems.com/en-us/product/radiation-hardened-electronics) são fabricados em processos antigos justamente porque transistores menores são mais sensíveis a radiação, e o ciclo de qualificação contra falhas chega a uma década. O hardware espacial segue a curva de Moore com defasagem institucional de dez a quinze anos — não por incompetência, mas por *garantia*.

Aqui é necessário um contraponto antes que ele seja levantado pelo leitor. Recursos adicionais podem servir à confiabilidade: redundância tripla com votação majoritária, telemetria contínua, simulação de envelope operacional offline. O próprio Perseverance combina o RAD750 com FPGAs e coprocessadores que aceleram visão e navegação. Mas ganhos de desempenho só entram em sistemas críticos quando compatíveis com verificação, redundância e tolerância a falhas. O que se inverte em Marte não é a hierarquia entre escalabilidade e confiabilidade; é a hierarquia de *finalidades*. Velocidade vira meio; confiabilidade permanece como fim.

Essa hierarquia não nasce em Marte. Está presente em qualquer sistema cuja falha custe vidas — o software de um marca-passo, a aviônica de um Boeing, a unidade de controle de um *airbag*. A diferença é que, na Terra, o excesso de recurso embaralha sinais: pode-se cobrir um algoritmo ruim com hardware melhor, e quase ninguém percebe a diferença. Marte impede esse encobrimento. O sinal aparece limpo porque o substrato hostil não comporta a ineficiência de cobrir má engenharia com mais silício.

## O MGPEB como exemplificação

É nesse contexto que as escolhas arquiteturais do MGPEB precisam ser lidas. *Bubble Sort* e *Selection Sort* são defensáveis aqui não por elegância algorítmica, mas porque, com `n = 12`, o pior caso é pequeno, fixo e inspecionável a olho nu — sem alocação dinâmica, sem recursão, sem ramificações imprevisíveis. Busca linear sobre doze módulos não é simplificação pedagógica: é o tamanho real do problema, e o *overhead* de uma estrutura mais sofisticada (*hash table*, árvore balanceada) seria custo não-funcional sem ganho funcional. A expressão booleana que autoriza o pouso, `F AND A AND (L OR E) AND S`, é formalmente inspecionável: qualquer membro da equipe pode demonstrar, por enumeração de tabela-verdade, que o sistema decide exatamente o que sua especificação afirma decidir. Modelos probabilísticos poderiam apoiar percepção ou diagnóstico, mas substituir a regra final de autorização por um classificador opaco trocaria demonstrabilidade por aposta — escolha inadequada para a porta que decide se um módulo desce ou aborta. A pilha de alertas, que registra cada negação de pouso e permite reconstruir a sequência em ordem cronológica reversa, é o primeiro mecanismo de *accountability* auditável que a [reflexão ESG](esg.md) descreve como pré-requisito de governança.

Vale, contudo, não romantizar a simplicidade. O código é protótipo demonstrativo, não sistema embarcado. Confiabilidade real, em sistemas críticos, exige bem mais do que algoritmos previsíveis: invariantes formais provadas, validação rigorosa de estados, registros persistentes resistentes a falhas, análise sistemática de modos de falha, redundância com votação. O MGPEB não tem nada disso. O que ele exemplifica não é a confiabilidade em si; é o *primeiro passo arquitetural* em direção a ela — escolher, deliberadamente, primitivas verificáveis em vez de sofisticadas. A continuidade entre o protótipo no *notebook* e um futuro sistema *flight-ready* não está na possibilidade de transplantar o código Python para Marte — Python e C embarcado divergem em tipos, overflow e gerenciamento de memória —, mas na preservação da especificação funcional sob nova implementação verificada.

## Coda

A máquina em São Paulo executa a mesma regra decisória que executaria em Marte, sobre entradas equivalentes. O que muda é o substrato, e portanto a hierarquia de propriedades não-funcionais que precisam ser otimizadas. Computação como engenharia é, em última instância, sempre uma escolha sobre quais propriedades não-funcionais valem o preço de quais. Marte só faz a escolha aparecer nua.

---

## Referências

- BOOLE, George. **An Investigation of the Laws of Thought**. London: Walton & Maberly, 1854. Disponível em: <https://www.gutenberg.org/ebooks/15114>. Acesso em: 26 abr. 2026.
- CHURCH, Alonzo. An Unsolvable Problem of Elementary Number Theory. **American Journal of Mathematics**, vol. 58, n. 2, p. 345–363, 1936. Disponível em: <https://www.jstor.org/stable/2371045>. Acesso em: 26 abr. 2026.
- SHANNON, Claude E. **A Symbolic Analysis of Relay and Switching Circuits**. Dissertação (Mestrado) — Massachusetts Institute of Technology, 1937. Disponível em: <https://dspace.mit.edu/handle/1721.1/11173>. Acesso em: 26 abr. 2026.
- TURING, Alan M. On Computable Numbers, with an Application to the Entscheidungsproblem. **Proceedings of the London Mathematical Society**, ser. 2, vol. 42, p. 230–265, 1937. Disponível em: <https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf>. Acesso em: 26 abr. 2026.
- BAE SYSTEMS. **RAD750 Radiation-Hardened Single-Board Computer**. Disponível em: <https://www.baesystems.com/en-us/product/radiation-hardened-electronics>. Acesso em: 26 abr. 2026.
- NASA. **Mars 2020 Mission — Perseverance Rover**. Disponível em: <https://mars.nasa.gov/mars2020/>. Acesso em: 26 abr. 2026.
