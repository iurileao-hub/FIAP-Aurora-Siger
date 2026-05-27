# Do reativo ao preditivo: quando o sistema deixa de apenas apagar incêndios

> Ensaio reflexivo da Fase 3 do Aurora SIGER. O enunciado pede que o sistema
> "evolua de uma postura reativa para uma postura preditiva". Este texto
> argumenta que essa evolução não é a troca de uma coisa por outra, mas a
> adição de uma camada de antecipação sobre uma base reativa que continua
> indispensável — e mostra onde, no código, essa antecipação acontece.

## A colônia que pousou agora precisa durar

Nas duas primeiras fases o Aurora SIGER respondia a perguntas pontuais e de
curta janela: *é seguro decolar?* (Fase 1), *este módulo pode pousar agora?*
(Fase 2). Eram decisões instantâneas — um retrato dos sensores, uma tabela-verdade,
um veredito. A Fase 3 muda a natureza do problema. A colônia que pousou agora
**opera**, hora após hora, sol após sol. A pergunta crítica deixa de ser binária
e passa a ter um eixo temporal: *vamos ficar sem energia daqui a quantas horas?*

Essa mudança de regime é o que torna a distinção entre reativo e preditivo
concreta, e não apenas um slogan. Um sistema que só reage decide com base no
agora; um sistema que prevê decide com base numa estimativa do depois. A energia
de uma colônia — bateria que carrega de dia e drena à noite, geração que oscila
com vento e tempestade de poeira — é exatamente o tipo de grandeza em que o
"agora" engana e o "depois" importa.

## O reativo e seus limites honestos

A postura reativa tem uma virtude que não convém menosprezar: ela é simples,
auditável e difícil de quebrar. No Aurora SIGER, ela vive em duas funções.

A primeira é `analyze_balance(generation_kw, consumption_kw)`, que classifica o
instante em `risk`, `balanced` ou `surplus` — o coração do item 1.4. A segunda,
mais operacional, é `allocate_energy()`: o *load shedding* em quatro estágios que
percorre a árvore de criticidade (Vital → Sustento → Expansão) e, quando a oferta
não cobre a demanda, rebaixa modos de baixo para cima, desligando Expansão antes
de tocar em Vital. É controle de contingência no sentido mais literal: dispara
quando o déficit **já existe**.

O limite do reativo puro é estrutural, não de implementação. Ele age depois que o
dano começou. Se a bateria cruza um limiar de segurança, o shedding corta carga —
mas a essa altura a colônia já está no vermelho, e a margem para manobra é a
menor possível. É como um airbag: essencial, e ainda assim um sinal de que algo
deu errado antes. Um operador humano experiente não opera assim. Ele olha a curva
de bateria caindo e age *antes* do limiar, porque reconhece a **tendência**. A
ambição da Fase 3 é dar ao sistema esse mesmo faro.

## O passo preditivo: uma reta que enxerga o futuro próximo

O instrumento da antecipação é deliberadamente modesto: uma regressão linear por
mínimos quadrados, em forma fechada, implementada à mão em `linear_regression()`:

$$a = \frac{\sum (x-\bar{x})(y-\bar{y})}{\sum (x-\bar{x})^2}, \qquad b = \bar{y} - a\bar{x}$$

O que dá poder preditivo a essa reta é onde ela é aplicada. Em `fit_energy_trend()`,
o mesmo estimador é treinado sobre a janela recente dos *deltas* de energia
(geração menos consumo, hora a hora) e devolve dois números: o `slope` — a
inclinação, em kW por hora — e o `predicted_next_delta`, a reta avaliada um passo
à frente dos dados. O `slope` é o sinal antecipatório: não diz onde a bateria
está, diz **para onde ela vai**.

A peça que fecha o raciocínio é `energy_level()`. O rótulo de saída da colônia
(`CRITICAL → LOW → NOMINAL → HIGH → SURPLUS`) não é uma simples função da
porcentagem de bateria. Ele é rebaixado quando o `slope` é suficientemente
negativo. Uma bateria a 60 % com inclinação estável é `NOMINAL`; a mesma bateria a
60 % despencando a −3 kW/h é classificada um degrau abaixo — `LOW` — porque o
sistema projeta que, mantida a tendência, ela cruzará o patamar crítico antes de o
próximo ciclo de carga chegar. O rótulo passa a antecipar o problema em vez de
constatá-lo. Esse é, em uma frase, o salto reativo→preditivo: **o estado deixa de
ser uma leitura e vira uma projeção.**

Vale registrar por que uma reta fechada, e não o gradiente descendente que a
outra branch da equipe usava. A forma fechada é exata: não tem taxa de
aprendizado para ajustar, não diverge, não precisa de *clamp* anti-explosão.
Para uma janela curta de poucas dezenas de pontos, ela é mais barata, mais
previsível e — num sistema que se quer auditável — mais fácil de explicar a quem
audita. Sofisticação aqui seria ruído.

## Duas camadas, uma só filosofia

A síntese da Fase 3 não escolhe entre reagir e prever; ela estratifica as duas
em defesa em profundidade. A primeira camada é o `power_factor()`: conforme a
bateria cai, ele estrangula *suavemente* o alvo de consumo de cada módulo (de
1,0 a 0,2), de forma contínua, sem saltos binários. É uma resposta preventiva e
graduada — começa a economizar cedo, quando ainda é barato. A segunda camada é o
shedding estrutural já descrito, que entra como rede de segurança quando a
atenuação suave não basta.

O cuidado de engenharia aqui foi evitar a dupla-contagem: o `power_factor`
escala os **alvos**, e a alocação então decide os **modos** contra a oferta usando
esses alvos já reduzidos — uma ordem, não duas correções competindo. O preditivo
(o `slope` que informa quão agressivo ser) e o reativo (o shedding que garante que
Vital nunca apaga) operam sobre a mesma grandeza sem se atropelar.

## Os limites do que uma reta pode prometer

Seria desonesto encerrar sem nomear o que a previsão **não** entrega. Uma OLS
linear sobre janela curta extrapola mal sob regime não-estacionário. Quando uma
tempestade de poeira derruba o fator de painel ou uma frente fria dispara o
consumo térmico (`Q = U·A·ΔT`), a tendência recente vira uma péssima
testemunha do futuro imediato — a reta aponta para um lugar onde a física já não
está. A previsão é uma hipótese, não uma certeza, e um sistema maduro a trata
como tal: o `slope` informa a decisão, não a substitui.

É por isso que o reativo permanece. O *load shedding* e o `power_factor` não são
resquícios de uma fase anterior a ser superada; são a fundação sobre a qual a
previsão pode se dar ao luxo de às vezes errar. Esse é o eco direto da reflexão
ética da Fase 1: automação em sistemas críticos amplia o operador, não o aposenta.
A reta antecipa para que o humano decida com mais folga — não para decidir por ele.

## Fecho

Evoluir do reativo ao preditivo, no Aurora SIGER, não foi apagar o reativo. Foi
colocar uma reta de poucos coeficientes a vigiar a tendência, deixar essa reta
rebaixar o rótulo de energia antes de a bateria piorar, e estratificar o controle
em uma camada que previne e outra que socorre. O reativo é a rede de segurança;
o preditivo é o trabalho de precisar dela com menos frequência. Um sistema que
só reage sobrevive a cada hora; um que também prevê começa a ter chance de
planejar o sol seguinte.
