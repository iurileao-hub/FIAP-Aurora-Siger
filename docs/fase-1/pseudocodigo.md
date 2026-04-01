# Algoritmo de Verificação de Decolagem

```
algoritmo "Verificação de Decolagem Aurora SIGER"

variáveis

    internal_temp, external_temp: real
    structural_integrity, critical_modules: inteiro
    energy: real
    vibration: real
    tank_pressure: real

    telemetria_ok: lógico
    ia_ok: lógico
    autonomia: real

    // Constantes energéticas
    CAPACIDADE_KWH = 18
    PERDAS_PCT = 14
    POTENCIA_LANCAMENTO_KW = 2
    TEMPO_LANCAMENTO_MIN = 9
    POTENCIA_ORBITAL_KW = 1.2
    CARGA_MINIMA_LANCAMENTO = 95

início

    telemetria_ok = VERDADEIRO
    ia_ok = VERDADEIRO

    Escreva "=== SISTEMA AURORA SIGER — VERIFICAÇÃO PRÉ-DECOLAGEM ==="

    // ============================================================
    // ETAPA 1 — Validação de Telemetria
    // ============================================================

    Escreva "Lendo dados de telemetria..."

    Leia internal_temp, external_temp, structural_integrity
    Leia energy, vibration, tank_pressure, critical_modules

    Se internal_temp < 18 OU internal_temp > 26 então
        Escreva "[ALERTA] Temperatura interna fora da faixa segura: ", internal_temp, " °C"
        telemetria_ok = FALSO
    Fim_se

    Se external_temp < -65 OU external_temp > 125 então
        Escreva "[ALERTA] Temperatura externa fora da faixa segura: ", external_temp, " °C"
        telemetria_ok = FALSO
    Fim_se

    Se structural_integrity ≠ 1 então
        Escreva "[ALERTA] Falha na integridade estrutural detectada"
        telemetria_ok = FALSO
    Fim_se

    Se energy < 60 então
        Escreva "[ALERTA] Nível de energia abaixo do mínimo operacional: ", energy, " %"
        telemetria_ok = FALSO
    Fim_se

    Se vibration < 0.1 OU vibration > 0.5 então
        Escreva "[ALERTA] Vibração fora da faixa segura: ", vibration, " g"
        telemetria_ok = FALSO
    Fim_se

    Se tank_pressure < 270 OU tank_pressure > 340 então
        Escreva "[ALERTA] Pressão dos tanques fora da faixa segura: ", tank_pressure, " atm"
        telemetria_ok = FALSO
    Fim_se

    Se critical_modules ≠ 1 então
        Escreva "[ALERTA] Módulos críticos inativos"
        telemetria_ok = FALSO
    Fim_se

    // ============================================================
    // ETAPA 2 — Verificação IA (Isolation Forest)
    // ============================================================

    Escreva "Executando verificação de anomalias por IA..."

    leitura_normalizada = normalizar(leitura, scaler)
    score = modelo.anomaly_score(leitura_normalizada)

    Escreva "Anomaly Score: ", score

    Se score ≥ threshold então
        Escreva "[ALERTA] IA detectou anomalia"
        ia_ok = FALSO
    Senão
        Escreva "IA não detectou anomalias"
    Fim_se

    // ============================================================
    // ETAPA 3 — Análise Energética
    // ============================================================

    Escreva "Calculando autonomia energética..."

    Se energy < CARGA_MINIMA_LANCAMENTO então
        Escreva "[ALERTA] Carga insuficiente para lançamento: ", energy, " % (mínimo: ", CARGA_MINIMA_LANCAMENTO, " %)"
        autonomia = NULO
    Senão
        disponivel = CAPACIDADE_KWH × (energy / 100) × (1 - PERDAS_PCT / 100)
        consumo_lancamento = POTENCIA_LANCAMENTO_KW × (TEMPO_LANCAMENTO_MIN / 60)
        autonomia = (disponivel - consumo_lancamento) / POTENCIA_ORBITAL_KW

        Escreva "Energia disponível: ", disponivel, " kWh"
        Escreva "Consumo no lançamento: ", consumo_lancamento, " kWh"
        Escreva "Autonomia orbital: ", autonomia, " h"
    Fim_se

    // ============================================================
    // DECISÃO FINAL
    // ============================================================

    Se telemetria_ok = VERDADEIRO E ia_ok = VERDADEIRO E autonomia ≠ NULO então
        Escreva ">>> PRONTO PARA DECOLAR <<<"
    Senão
        Escreva ">>> DECOLAGEM ABORTADA <<<"
    Fim_se

Fim
```
