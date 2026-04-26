# Design — Contextualização histórica/arquitetural (Fase 2, MGPEB)

**Entregável:** `docs/fase-2/contextualizacao-historica.md`, ~1200 palavras.
**Cumpre:** Tarefa 5 do enunciado (`fases/fase-2/enunciado-contextualizacao-historica.md`).
**Posição no relatório PDF:** seção textual paralela à ESG (`docs/fase-2/esg.md`), cobrindo a evolução da computação e suas restrições aplicadas ao MGPEB.

## Tese

A computação tem uma base lógica formal — Boole (1854) → Shannon (1937) → Turing (1936) — que torna a *função* independente do substrato físico. Mas as *propriedades não-funcionais* (energia, tempo, falhas, radiação) permanecem radicalmente acopladas ao substrato. Essa dupla natureza — lógica desacoplada, físico acoplado — é o que torna possível e necessário hierarquizar valores no projeto de sistemas. Em ambientes onde o substrato é hostil e o custo de falha é catastrófico (Marte), a hierarquia se explicita: confiabilidade verificável vence performance bruta. O MGPEB exemplifica essa hierarquia em código.

## Inversão argumentativa central

Marte não expõe limitação computacional. *Explicita* uma hierarquia que sistemas críticos terrestres já carregam (controle aéreo, marca-passos, ECUs) mas que o excesso de recurso na Terra disfarça. O hostil é o que torna o sinal limpo.

## Estrutura — 4 movimentos + coda

### Movimento 1 — Da máquina mecânica à lógica formal
- Babbage (1837) como antecedente *mecânico* (memória/operação/controle), não como formalizador do pensamento.
- Boole (1854) — álgebra do raciocínio dedutivo.
- Frege/Hilbert/Gödel/Church (1930s) — formalização da computabilidade (mencionar como linhagem, sem aprofundar).
- Shannon (1937) — pivô material: isomorfismo entre circuitos elétricos e álgebra booleana.
- **Conclusão do movimento:** a invariância está no isomorfismo formal entre lógica e circuito, não numa metáfora histórica. Relés, válvulas, transistores, CMOS são realizações materiais desse isomorfismo.

### Movimento 2 — Turing e a dupla natureza
- Turing (1936): universalidade computacional — qualquer máquina suficientemente expressiva simula qualquer outra.
- **Mas:** Turing fala sobre a *função*. Tempo, energia, calor, falhas, radiação são silentes na máquina abstrata e ensurdecedores no substrato real.
- A **dupla natureza** (função desacoplada, propriedades não-funcionais acopladas) é o pivô que sustenta o resto do texto — permite o protótipo, força a hierarquização de valores.

### Movimento 3 — Marte como caso-limite
- Substrato hostil concreto: radiação cósmica (single-event upsets), delay 4–24 min, energia escassa, RAD750 (~2005) no Perseverance — radiation-hardened, ~10× mais lento que equivalentes comerciais, certificação de uma década.
- **Contraponto vacinal (1–2 frases):** escalabilidade pode servir confiabilidade — redundância tripla, votação majoritária, telemetria. Mas isso muda hierarquia de finalidades, não de valores: escalabilidade vira meio, confiabilidade permanece fim.
- Por que precisamos de Marte pra ver: na Terra, recurso abundante embaralha sinais — algoritmo ruim se cobre com hardware melhor. Em Marte, isso é impossível.
- Marte não revela verdade metafísica nova; explicita hierarquia que sistemas críticos terrestres já carregam.

### Movimento 4 — O MGPEB como exemplificação (não romantização)
- O que torna o código demonstrativo **não é simplicidade** — é **verificabilidade por inspeção**:
  - `F AND A AND (L OR E) AND S` é formalmente demonstrável; ML não é.
  - Bubble/Selection — determinísticos, sem alocação dinâmica, sem recursão.
  - Busca linear sobre n=12 — tamanho real do problema.
  - Pilha de alertas — accountability auditável (continuidade com ESG).
- **Reconhecer o que falta** pra ser flight-ready: invariantes formais, testes, validação de estados, logs persistentes, análise sistemática de falhas. O MGPEB é protótipo demonstrativo, não sistema embarcado.

### Coda (1 parágrafo curto)
A máquina em São Paulo executa exatamente a mesma função que executaria em Marte — não é simulação, é a função. O que muda é o substrato, e portanto a hierarquia de propriedades não-funcionais a otimizar. Computação como engenharia é sempre uma escolha sobre quais propriedades não-funcionais valem o preço de quais. Marte só faz a escolha aparecer nua.

## Estilo

**Referência primária:** `docs/fase-2/esg.md` (mesma fase, mesmo PDF — coerência interna).
- Voz institucional/acadêmica, não jornalística-ensaística (a fase-1 `etica.md` tem voz mais cinematográfica; aqui não cabe).
- Frases longas com pausas curtas como pontuação rítmica.
- Termos técnicos em inglês glosados em PT na primeira ocorrência (single-event upset, radiation-hardened).
- Ancoragem em fontes formais com hyperlink inline (autor, ano).

**Referências previstas (a citar inline + listar ao final em ABNT-ish):**
- BOOLE, G. *An Investigation of the Laws of Thought* (1854)
- SHANNON, C. E. *A Symbolic Analysis of Relay and Switching Circuits* (1937, MIT Master's thesis)
- TURING, A. M. *On Computable Numbers, with an Application to the Entscheidungsproblem* (1936)
- BABBAGE, C. — referência historiográfica (Swade ou similar)
- MOORE, G. *Cramming more components onto integrated circuits* (1965)
- BAE Systems — datasheet/documentação RAD750 (público, web)
- NASA Mars 2020 / Perseverance — fonte oficial pra confirmar uso do RAD750
- Possível: VON NEUMANN, J. *First Draft of a Report on the EDVAC* (1945) — se couber

## Restrições

- **Tamanho-alvo:** ~1200 palavras (vs ~1800 do esg.md).
- **Não pode** romantizar simplicidade algorítmica como sinônimo de confiabilidade (vulnerabilidade #6 da crítica).
- **Não pode** apresentar Babbage como formalizador do pensamento (vulnerabilidade #1).
- **Não pode** apresentar Turing como provando "desacoplamento ontológico" sem qualificar a dupla natureza (vulnerabilidade #3).
- **Deve** incluir contraponto explícito sobre escalabilidade servindo confiabilidade (vulnerabilidade #4).
- **Deve** justificar por que Marte explicita o que estaria embaralhado na Terra (vulnerabilidade #5).
- **Deve** citar código real do `mgpeb.py` (expressão booleana, sorts, busca, pilha de alertas) — continuidade com a ESG.

## Próximos passos pós-aprovação

1. Iúri revisa este spec — sinaliza se algum movimento precisa ajustar antes de redigir.
2. Redação do ensaio em `docs/fase-2/contextualizacao-historica.md`.
3. Revisão crítica do texto redigido (eu + codex, mesmo padrão).
4. Iúri refina a redação final na voz dele.
5. Commit isolado da seção pra rastreabilidade do PDF.
