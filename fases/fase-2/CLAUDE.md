# MGPEB — Módulo de Gerenciamento de Pouso e Estabilização de Base

## Projeto

Atividade Integradora da Fase 2 do curso de Ciência da Computação (FIAP).
Simula o sistema de gerenciamento de pouso de 12 módulos da colônia Aurora Siger em Marte.

## Equipe

Gabriel Carmona, Carlos Eugênio, Marcio Francisco, Iúri Leão, Maria Sophia

## Como executar

```bash
python3 mgpeb.py
```

Sem dependências externas. Usa apenas `math` da biblioteca padrão.

## Convenções de código

- **Nomes** (variáveis, funções, chaves): inglês
- **Comentários e docstrings**: português (BR)
- **Paradigma**: procedural — funções puras + dicionários (sem classes/OOP)
- **Arquivo único**: `mgpeb.py`

## Estrutura do código

O arquivo é organizado em 8 seções numeradas:

1. **DADOS** — 12 módulos pré-definidos + condições de pouso
2. **ESTRUTURAS LINEARES** — fila (FIFO), pilha (LIFO), operações
3. **REGRAS LÓGICAS** — autorização de pouso com expressões booleanas
4. **BUSCA** — busca linear por tipo, combustível e prioridade
5. **ORDENAÇÃO** — Bubble Sort (prioridade) e Selection Sort (combustível)
6. **FUNÇÕES MATEMÁTICAS** — altitude, consumo, energia solar, temperatura
7. **SIMULAÇÃO** — loop de pouso sequencial
8. **MENU** — interface interativa com o operador

## Prazo de entrega

28/04/2026
