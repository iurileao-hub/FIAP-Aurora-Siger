# Da operação à topologia: a colônia que opera agora se mapeia como rede

> Ensaio reflexivo da Fase 4 do Aurora SIGER. A Fase 3 simulou a operação energética
> da colônia hora a hora; a Fase 4 congela esse tempo e olha para o espaço: os mesmos
> 13 módulos agora como nós de um grafo, suas dependências como arestas, seus fluxos
> como pesos. Este texto argumenta que a passagem da operação à topologia não é uma
> mudança de tema — é uma mudança de pergunta.

## A colônia que o tempo não parava agora ocupa um espaço

Na Fase 3 a pergunta era temporal: *vamos ficar sem energia daqui a quantas horas?*
A simulação corria hora a hora, sol após sol, e o sistema respondia com uma estimativa
de tendência — o `slope` da bateria, a antecipação do déficit. A colônia existia no
tempo; a análise era uma série histórica.

A Fase 4 suspende o relógio e pergunta algo diferente: *se um módulo falhar agora, o
que deixa de ser alcançável?* Não é uma pergunta sobre quanto — é sobre quem depende de
quem. A colônia continua sendo os mesmos 13 módulos, mas o modo de olhar para ela mudou:
de uma sequência temporal para uma rede de dependências simultâneas.

Essa mudança de perspectiva é o que torna a Fase 4 uma fase e não apenas um apêndice
da Fase 3. A operação e a topologia iluminam dimensões diferentes da mesma infraestrutura.

## Por que os mesmos 13 módulos

A decisão de reutilizar exatamente os 13 módulos da Fase 3 não foi inércia — foi uma
decisão de projeto com consequência técnica direta.

Na Fase 3, os módulos carregavam dois atributos que o SIGIC precisa: identidade
(`id`, `name`, `type`) e consumo energético no modo adequado (o $C_0 = 80{,}5\ \text{kW}$
que ancora a modelagem matemática da Fase 4). Criar uma lista paralela de módulos para
a Fase 4 introduziria dois riscos: divergência silenciosa (a lista da Fase 4 e a da
Fase 3 poderiam descrever colônias diferentes sem que o sistema percebesse) e perda de
rastreabilidade narrativa (a colônia que pousou, operou e agora se mapeia deixaria de
ser a mesma colônia).

Manter uma única fonte de verdade (`aurora_siger.operations.MODULES`) é uma decisão de
engenharia com sabor filosófico: a colônia tem continuidade de identidade através das
fases porque o código a garante.

## Por que a criticidade da Fase 3 vira prioridade na Fase 4

A Fase 3 ordenou os módulos em três tiers de criticidade — Vital, Sustento, Expansão —
para guiar o *load shedding* durante escassez de energia. O algoritmo de alocação de carga
percorria a árvore de criticidade de baixo para cima: desligava Expansão antes de tocar
em Sustento, nunca desligava Vital.

A Fase 4 herda essa hierarquia e a transforma em prioridade numérica: Vital → 10,
Sustento → 7, Expansão → 4. Essa tradução serve ao algoritmo de Dijkstra com restrição:
quando se traça uma rota de fornecimento de energia em situação de emergência, módulos
intermediários de baixa prioridade podem ser descartados do caminho — a energia flui
por onde importa.

Mas a herança carrega um risco que a análise de topologia revela: a prioridade operacional
e a criticidade topológica são dimensões distintas, e a Fase 3 não tinha como capturar a segunda.

## O paradoxo do ponto de articulação

O resultado mais revelador da Fase 4 é que o único ponto de articulação da rede — o
único módulo cuja remoção divide o grafo — é o **Armazenamento e Logística** (módulo 9),
classificado como tier Expansão (prioridade 4).

O algoritmo de Tarjan não tem opinião sobre criticidade operacional. Ele percorre a rede
com DFS, calcula os valores de *discovery* e *low* de cada nó, e identifica vértices de
corte pela regra: se um filho $v$ de $u$ não tem back-edge para nenhum ancestral de $u$,
então $u$ é ponto de articulação. O módulo 9 emerge como corte porque é o único elo entre
o Gerador Eólico (módulo 13) e o restante da rede.

O Gerador Eólico, como folha (grau 1), tem centralidade de intermediação zero — nenhum
caminho entre dois módulos distintos passa por ele. Em termos de fluxo de informação e
controle, ele é um terminal, não um nó de passagem. Mas em termos de geração de energia,
ele representa 30 kW de capacidade instalada — 14,3 % do total de 210 kW. Perder o
módulo 9 não apenas cria dois componentes desconexos; corta 14,3 % da geração antes do
horizonte crítico de 7,1 anos.

Esse paradoxo tem implicação de governança: a prioridade operacional (que a Fase 3 define)
e a criticidade topológica (que a Fase 4 descobre) são dimensões **ortogonais**. Um módulo
pode ser "expansão" no sentido de que pode ser temporariamente desligado sem matar a
tripulação, mas "crítico" no sentido topológico de que sua remoção fragmenta a rede. Um
sistema de gestão que opera apenas com a primeira dimensão está administrando um risco que
não enxerga.

## O que a rede revela que a simulação não capturava

A simulação da Fase 3 corria hora a hora e registrava 16 séries temporais — bateria,
geração, consumo, slope, nível de energia. Toda a análise era local no tempo: o que está
acontecendo agora, e o que vai acontecer na próxima hora.

O grafo da Fase 4 é global no espaço: captura a estrutura inteira da rede de uma vez.
BFS revela a distância em saltos entre qualquer par de módulos. DFS encontra caminhos
alternativos. Dijkstra otimiza rotas com restrição de prioridade. Brandes mede quais
nós são intermediários críticos mesmo sem ser pontos de corte.

A centralidade de intermediação do Reator Nuclear (0,2879) e do Controle e Comando
(0,2083) não era visível na simulação temporal — a Fase 3 sabia que eles eram
importantes (consumo alto, criticidade Vital), mas não sabia *por quê* estruturalmente.
A Fase 4 responde: porque a maior parte dos caminhos mais curtos da rede passa por eles.
São nós de passagem, não apenas consumidores ou geradores.

## O que a topologia não resolve

Seria honesto parar aqui. A análise topológica tem limites simétricos aos da simulação temporal.

O grafo da Fase 4 é estático: representa a rede num instante, sem capturar variação de
fluxo ao longo do tempo. Um nó com peso de aresta 2 num sol calmo pode ser mais ou menos
eficiente que um nó de peso 1 durante uma tempestade — o grafo não sabe. A perda energética
modelada por $P_{\text{loss}} = 1 - e^{-d(1-\eta)}$ usa a distância física como proxy do
custo de transmissão, mas não incorpora variação climática nem degradação de componentes.

O ponto de articulação (módulo 9) é um resultado da topologia *atual*. Se um novo módulo
criar uma aresta direta entre o Gerador Eólico e outro nó da rede, o ponto de articulação
desaparece — e a análise de Tarjan, refeita sobre o novo grafo, confirmará isso. O SIGIC
não é uma verdade permanente sobre a colônia: é um espelho da rede no estado em que ela se
encontra. Mudou a rede, muda o espelho.

## Fecho

A Fase 3 perguntava: *a colônia vai resistir ao próximo sol?* A Fase 4 pergunta: *se um
ponto falhar, a rede se mantém?* São perguntas diferentes, e nenhuma é mais importante que
a outra.

O que o SIGIC mostra, ao juntar as duas, é que a Aurora Siger é ao mesmo tempo um sistema
dinâmico (que consome, gera e distribui energia ao longo do tempo) e um sistema estrutural
(cuja topologia de dependências determina o que sobrevive a uma falha pontual). Administrar
apenas a dimensão temporal é reagir. Administrar apenas a dimensão topológica é planejar em
vácuo. O Aurora SIGER, na sua Fase 4, tenta fazer as duas coisas — e ao nomear o paradoxo
do módulo 9, entrega a decisão onde ela pertence: nas mãos de quem governa a colônia.
