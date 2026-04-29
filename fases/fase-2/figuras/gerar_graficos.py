"""
Gera os quatro gráficos das funções matemáticas do MGPEB para o relatório.

Reproduz fielmente as funções de mgpeb.py com seus parâmetros padrão.
Salva PNGs em figuras/ na resolução adequada para impressão.

Execução:
    python3 figuras/gerar_graficos.py
"""

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Diretório de saída — mesmo do script
OUT_DIR = Path(__file__).parent

# Estilo consistente para todos os gráficos
plt.rcParams.update({
    "font.family": "Helvetica",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
})


# =============================================================================
# 1. Altitude de descida — quadrática
# =============================================================================

def descent_altitude(t, h0=2000.0, v0=80.0, a=3.7):
    return np.maximum(0.0, h0 - v0 * t - 0.5 * a * t ** 2)


def plot_descent():
    # Determina o instante de impacto (raiz positiva da quadrática)
    h0, v0, a = 2000.0, 80.0, 3.7
    t_impact = (-v0 + math.sqrt(v0 ** 2 + 2 * a * h0)) / a

    t = np.linspace(0, t_impact * 1.05, 200)
    h = descent_altitude(t)

    fig, ax = plt.subplots(figsize=(5.5, 3.0))
    ax.plot(t, h, color="#1565C0", linewidth=2.2)
    ax.fill_between(t, 0, h, color="#1565C0", alpha=0.12)
    ax.axvline(t_impact, color="#C62828", linestyle=":", linewidth=1.3)
    ax.annotate(
        f"impacto\nt ≈ {t_impact:.1f} s",
        xy=(t_impact, 0), xytext=(t_impact - 4.2, 350),
        fontsize=10, color="#C62828",
        arrowprops=dict(arrowstyle="->", color="#C62828", lw=1),
    )
    ax.set_xlabel("Tempo desde início da descida $t$ (s)")
    ax.set_ylabel("Altitude $h(t)$ (m)")
    ax.set_title("Altitude de descida sob gravidade marciana")
    ax.set_xlim(0, t_impact * 1.05)
    ax.set_ylim(0, h0 * 1.05)
    fig.savefig(OUT_DIR / "func_altitude.png")
    plt.close(fig)


# =============================================================================
# 2. Consumo de combustível — exponencial
# =============================================================================

def fuel_consumption(v, c0=10.0, k=0.02):
    return c0 * np.exp(k * v)


def plot_fuel():
    v = np.linspace(0, 200, 200)
    c = fuel_consumption(v)

    fig, ax = plt.subplots(figsize=(5.5, 3.0))
    ax.plot(v, c, color="#E65100", linewidth=2.2)
    ax.fill_between(v, 0, c, color="#E65100", alpha=0.12)

    # Anotação de pontos-chave
    for v_ref in (50, 100, 150, 200):
        c_ref = fuel_consumption(v_ref)
        ax.plot(v_ref, c_ref, "o", color="#E65100", markersize=5)
        ax.annotate(f"  {c_ref:.1f}", xy=(v_ref, c_ref),
                    fontsize=9, color="#5D4037", va="center")

    ax.set_xlabel("Velocidade de frenagem $v$ (m/s)")
    ax.set_ylabel("Consumo $C(v)$ (kg/s)")
    ax.set_title("Consumo de combustível em função da velocidade de frenagem")
    ax.set_xlim(0, 200)
    ax.set_ylim(0, fuel_consumption(200) * 1.05)
    fig.savefig(OUT_DIR / "func_combustivel.png")
    plt.close(fig)


# =============================================================================
# 3. Energia solar — parábola invertida
# =============================================================================

def solar_energy(t, a_coeff=15.0, t_mid=12.3, e_max=2200.0):
    return np.maximum(0.0, -a_coeff * (t - t_mid) ** 2 + e_max)


def plot_solar():
    t = np.linspace(0, 24.62, 300)
    e = solar_energy(t)

    fig, ax = plt.subplots(figsize=(5.5, 3.0))
    ax.plot(t, e, color="#F9A825", linewidth=2.2)
    ax.fill_between(t, 0, e, color="#F9A825", alpha=0.18)

    # Marca pico
    t_mid, e_max = 12.3, 2200.0
    ax.plot(t_mid, e_max, "o", color="#F9A825", markersize=7)
    ax.annotate(
        f"pico\n{e_max:.0f} W em t = {t_mid} h",
        xy=(t_mid, e_max), xytext=(t_mid + 1.5, e_max - 350),
        fontsize=10, color="#5D4037",
        arrowprops=dict(arrowstyle="->", color="#5D4037", lw=1),
    )

    ax.set_xlabel("Hora do sol marciano $t$ (h)")
    ax.set_ylabel("Energia gerada $E(t)$ (W)")
    ax.set_title("Geração solar ao longo de um sol marciano (~24,6 h)")
    ax.set_xlim(0, 24.62)
    ax.set_ylim(0, e_max * 1.1)
    fig.savefig(OUT_DIR / "func_solar.png")
    plt.close(fig)


# =============================================================================
# 4. Temperatura superficial — senoidal
# =============================================================================

def surface_temperature(t, t_avg=-60.0, amplitude=40.0, period=24.62, phase=0.0):
    return t_avg + amplitude * np.sin(2 * np.pi * t / period - phase)


def plot_temperature():
    t = np.linspace(0, 24.62, 300)
    T = surface_temperature(t)

    fig, ax = plt.subplots(figsize=(5.5, 3.0))
    ax.plot(t, T, color="#1976D2", linewidth=2.2)
    ax.axhline(-60, color="#5D4037", linestyle="--", linewidth=1, alpha=0.6)
    ax.text(0.3, -58.5, "média = −60 °C", fontsize=9, color="#5D4037")

    # Marca máximo e mínimo
    period = 24.62
    t_max = period / 4               # sin = +1
    t_min = 3 * period / 4           # sin = −1
    ax.plot(t_max, -20, "o", color="#1976D2", markersize=6)
    ax.plot(t_min, -100, "o", color="#1976D2", markersize=6)
    ax.annotate("máx −20 °C", xy=(t_max, -20), xytext=(t_max + 1, -25),
                fontsize=10, color="#5D4037")
    ax.annotate("mín −100 °C", xy=(t_min, -100), xytext=(t_min - 6, -97),
                fontsize=10, color="#5D4037")

    ax.set_xlabel("Hora do sol marciano $t$ (h)")
    ax.set_ylabel("Temperatura $T(t)$ (°C)")
    ax.set_title("Temperatura superficial ao longo de um sol marciano")
    ax.set_xlim(0, period)
    ax.set_ylim(-110, -10)
    fig.savefig(OUT_DIR / "func_temperatura.png")
    plt.close(fig)


if __name__ == "__main__":
    plot_descent()
    plot_fuel()
    plot_solar()
    plot_temperature()
    print(f"Gráficos gerados em {OUT_DIR}/")
