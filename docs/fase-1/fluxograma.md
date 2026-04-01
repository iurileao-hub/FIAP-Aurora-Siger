# Fluxograma do Algoritmo de Verificação

![Fluxograma de Verificação de Decolagem](../../fases/fase-1/assets/fluxograma_verificacao.png)

O fluxograma acima representa o pipeline de 3 estágios do Aurora SIGER:

1. **Validação de telemetria** — cada sensor comparado com faixas seguras
2. **Verificação por IA** — Isolation Forest analisa combinações de valores
3. **Análise energética** — autonomia orbital calculada

Somente se os três estágios forem aprovados, o sistema emite GO.
