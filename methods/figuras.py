"""Genera las figuras del paper.

Produce los gráficos en formato PDF y PNG en el directorio figures/:
  - 6.1 Mapa de estudio (sitios candidatos y plantas con curtailment)
  - 6.2 Climatología comparada (T_db, HR, T_wb mensuales)
  - 6.3 Coeficientes Etapa 0 (PUE y WUE por sitio × bundle)
  - 6.4 Rankings CAI para d0 ∈ {20, 50, 100} km
  - 6.5 Frontera de Pareto (Costo vs. Agua vs. CAI)
"""

from pathlib import Path
import shutil
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Configurar estilo visual premium
sns.set_theme(style="whitegrid")
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.titlesize": 14,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def plot_mapa():
    """6.1 Mapa de estudio."""
    print("  Generando Figura 6.1: Mapa de estudio...")
    curt = pd.read_csv(DATA_DIR / "curtailment_acumulado.csv").dropna(
        subset=["latitud", "longitud"]
    )
    stat = pd.read_csv(DATA_DIR / "station_catalog.csv")
    # Crucero II se excluye del catálogo (misma ubicación que CRUC; ver sección IV)
    stat = stat[stat["codigo"] != "Crucero2"]

    # Geometrías regionales de Chile (Natural Earth 1:10m, cacheado localmente)
    regiones = gpd.read_file(DATA_DIR / "chile_regiones.geojson")
    regiones_estudio = [
        "Arica y Parinacota",
        "Tarapacá",
        "Antofagasta",
        "Atacama",
        "Coquimbo",
    ]
    reg_norte = regiones[regiones["name"].isin(regiones_estudio)]

    # Límites de la zona de estudio (con margen sobre los datos)
    xmin, xmax = -71.8, -66.6
    ymin, ymax = -31.8, -17.2

    fig, ax = plt.subplots(figsize=(8, 8))

    # Fondo geográfico: polígonos regionales
    regiones.plot(ax=ax, color="#eee9df", edgecolor="#b0a998", linewidth=0.6)
    reg_norte.plot(ax=ax, color="#f7f2e6", edgecolor="#8a8272", linewidth=0.9)

    # Etiquetas de regiones de la zona de estudio
    etiquetas_reg = {
        "Arica y Parinacota": "XV",
        "Tarapacá": "I",
        "Antofagasta": "II",
        "Atacama": "III",
        "Coquimbo": "IV",
    }
    # Posiciones manuales (lon, lat) para evitar colisiones con etiquetas de sitios
    posiciones_reg = {"Tarapacá": (-69.55, -19.5)}  # "I" centrado, sobre PALM
    for _, row in reg_norte.iterrows():
        pt = row["geometry"].representative_point()
        x, y = posiciones_reg.get(row["name"], (pt.x, pt.y))
        ax.annotate(
            etiquetas_reg[row["name"]],
            (x, y),
            color="#8a8272",
            fontsize=11,
            style="italic",
            ha="center",
            alpha=0.8,
        )

    # Graficar plantas con curtailment
    solar = curt[curt["tipo"] == "Solar"]
    wind = curt[curt["tipo"] == "Eólica"]

    ax.scatter(
        solar["longitud"],
        solar["latitud"],
        s=solar["curtailment (MWh)"] / 1000 * 2,  # Escalar tamaño
        color="#f39c12",
        alpha=0.6,
        label="Solar Curtailment",
        edgecolors="none",
    )
    ax.scatter(
        wind["longitud"],
        wind["latitud"],
        s=wind["curtailment (MWh)"] / 1000 * 2,
        color="#2980b9",
        alpha=0.6,
        label="Wind Curtailment",
        edgecolors="none",
    )

    # Graficar estaciones candidatas
    ax.scatter(
        stat["longitud"],
        stat["latitud"],
        marker="^",
        s=100,
        color="#c0392b",
        edgecolors="black",
        linewidths=1.2,
        label="Sitios Candidatos",
        zorder=5,
    )

    # Annotations for candidate sites; CRUC va a la izquierda para no chocar con SLAR
    label_offsets = {"CRUC": ((-7, 2), "right")}
    for _, row in stat.iterrows():
        xytext, ha = label_offsets.get(row["codigo"], ((5, 2), "left"))
        ax.annotate(
            row["codigo"],
            (row["longitud"], row["latitud"]),
            textcoords="offset points",
            xytext=xytext,
            ha=ha,
            fontsize=8,
            weight="bold",
        )

    ax.set_title("Norte de Chile: Sitios Candidatos y Curtailment")
    ax.set_xlabel("Longitud (°W)")
    ax.set_ylabel("Latitud (°S)")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=True)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal", adjustable="box")

    # Inset: Chile continental con la zona de estudio destacada
    axins = fig.add_axes([0.63, 0.13, 0.22, 0.34])
    regiones.plot(ax=axins, color="#e0dacc", edgecolor="#b0a998", linewidth=0.3)
    axins.add_patch(
        plt.Rectangle(
            (xmin, ymin),
            xmax - xmin,
            ymax - ymin,
            fill=False,
            edgecolor="#c0392b",
            linewidth=1.5,
        )
    )
    axins.set_xlim(-76.5, -66.0)  # Chile continental (excluye territorio insular)
    axins.set_ylim(-56.5, -17.0)
    axins.set_xticks([])
    axins.set_yticks([])
    axins.set_title("Chile", fontsize=8)
    for spine in axins.spines.values():
        spine.set_edgecolor("#8a8272")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_6_1_mapa.pdf", format="pdf")
    fig.savefig(FIGURES_DIR / "fig_6_1_mapa.png", dpi=300)
    plt.close(fig)


def plot_climatologia():
    """6.2 Climatología comparada."""
    print("  Generando Figura 6.2: Climatología comparada...")
    solar_df = pd.read_csv(DATA_DIR / "dataset_solar_mensual.csv")
    solar_df["fecha"] = pd.to_datetime(solar_df["fecha"])
    solar_df["mes"] = solar_df["fecha"].dt.month

    # Promedio mensual multianual
    clim = solar_df.groupby(["estacion", "mes"]).mean(numeric_only=True).reset_index()

    # Añadir T_wb aproximada para graficar
    # Formula de Stull
    rh_c = np.clip(clim["humedad_mean_pct"], 5.0, 100.0)
    t_db = clim["temperatura_mean_c"]
    clim["T_wb"] = (
        t_db * np.arctan(0.151977 * np.sqrt(rh_c + 8.313659))
        + np.arctan(t_db + rh_c)
        - np.arctan(rh_c - 1.676331)
        + 0.00391838 * (rh_c**1.5) * np.arctan(0.023101 * rh_c)
        - 4.686035
    )

    # Seleccionar algunas estaciones representativas para no saturar el gráfico
    selected_stations = ["CAMA", "PALM", "CRUC", "SLAR", "ARMA"]

    fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

    # T_db
    sns.lineplot(
        data=clim[clim["estacion"].isin(selected_stations)],
        x="mes",
        y="temperatura_mean_c",
        hue="estacion",
        marker="o",
        ax=axes[0],
    )
    axes[0].axhline(
        20.0, color="r", linestyle="--", alpha=0.7, label="Umbral T_db (20°C)"
    )
    axes[0].set_ylabel("Temperatura DB (°C)")
    axes[0].set_title("Climatología Comparada de Sitios Representativos")
    axes[0].legend(loc="upper right", bbox_to_anchor=(1.15, 1.0))

    # HR
    sns.lineplot(
        data=clim[clim["estacion"].isin(selected_stations)],
        x="mes",
        y="humedad_mean_pct",
        hue="estacion",
        marker="s",
        ax=axes[1],
        legend=False,
    )
    axes[1].axhline(60.0, color="b", linestyle="--", alpha=0.7, label="Umbral HR (60%)")
    axes[1].set_ylabel("Humedad Relativa (%)")

    # T_wb
    sns.lineplot(
        data=clim[clim["estacion"].isin(selected_stations)],
        x="mes",
        y="T_wb",
        hue="estacion",
        marker="^",
        ax=axes[2],
        legend=False,
    )
    axes[2].axhline(
        19.0, color="g", linestyle="--", alpha=0.7, label="Umbral T_wb (19°C)"
    )
    axes[2].set_ylabel("Temperatura WB (°C)")
    axes[2].set_xlabel("Mes del Año")
    axes[2].set_xticks(range(1, 13))

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_6_2_climatologia.pdf", format="pdf")
    fig.savefig(FIGURES_DIR / "fig_6_2_climatologia.png", dpi=300)
    plt.close(fig)


def plot_coeficientes():
    """6.3 Coeficientes de Etapa 0."""
    print("  Generando Figura 6.3: Coeficientes de Etapa 0...")
    coef = pd.read_csv(RESULTS_DIR / "etapa0_coeficientes.csv")
    coef = coef[coef["PUE"] < 90].copy()  # Solo factibles

    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)

    # PUE
    sns.barplot(
        data=coef,
        x="estacion",
        y="PUE",
        hue="bundle",
        ax=axes[0],
        palette="viridis",
    )
    axes[0].set_ylim(1.0, 2.0)
    axes[0].set_ylabel("PUE (Power Usage Effectiveness)")
    axes[0].set_title("PUE por Sitio y Tecnología")
    axes[0].legend(title="Bundle Tecnológico", loc="upper right")

    # WUE
    sns.barplot(
        data=coef,
        x="estacion",
        y="WUE_L_kWh",
        hue="bundle",
        ax=axes[1],
        palette="viridis",
        legend=False,
    )
    axes[1].set_ylabel("WUE (Water Usage Effectiveness, L/kWh)")
    axes[1].set_title("WUE por Sitio y Tecnología")
    axes[1].set_xlabel("Sitio Candidato")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_6_3_coeficientes.pdf", format="pdf")
    fig.savefig(FIGURES_DIR / "fig_6_3_coeficientes.png", dpi=300)
    plt.close(fig)


def plot_cai():
    """6.4 Rankings CAI."""
    print("  Generando Figura 6.4: Curvas de CAI...")
    cai = pd.read_csv(RESULTS_DIR / "cai_por_sitio.csv")

    # Ordenar por CAI d50 para el eje X
    cai = cai.sort_values("CAI_total_d50", ascending=False).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(
        cai["estacion"],
        cai["CAI_total_d20"],
        marker="o",
        linewidth=2,
        label="d0 = 20 km",
        color="#c0392b",
    )
    ax.plot(
        cai["estacion"],
        cai["CAI_total_d50"],
        marker="s",
        linewidth=2,
        label="d0 = 50 km",
        color="#2980b9",
    )
    ax.plot(
        cai["estacion"],
        cai["CAI_total_d100"],
        marker="^",
        linewidth=2,
        label="d0 = 100 km",
        color="#27ae60",
    )

    ax.set_title("Índice CAI por Sitio y Escala de Interconexión (d0)")
    ax.set_xlabel("Estación (Ordenada por CAI d50)")
    ax.set_ylabel("CAI Total (GWh-equivalente)")
    ax.legend(title="Escala de Decaimiento")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_6_4_cai.pdf", format="pdf")
    fig.savefig(FIGURES_DIR / "fig_6_4_cai.png", dpi=300)
    plt.close(fig)


def plot_pareto():
    """6.5 Frontera de Pareto."""
    print("  Generando Figura 6.5: Frontera de Pareto...")
    exp = pd.read_csv(RESULTS_DIR / "experimentos_consolidado.csv")

    # Filtrar corridas core con P=2
    p2_df = exp[(exp["type"] == "core") & (exp["P"] == 2)]

    # Agrupar por run_id para calcular Costo total, Agua total y CAI total del portafolio
    runs = p2_df.groupby("run_id").agg(
        {
            "Cost_usd": "sum",
            "W_m3": "sum",
            "CAI": "sum",
            "alpha": "first",
            "beta": "first",
            "gamma": "first",
        }
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    # Scatter plot: Costo vs. Agua con color representando CAI
    scatter = ax.scatter(
        runs["Cost_usd"] / 1e6,  # En millones de USD
        runs["W_m3"] / 1000,  # En miles de m3
        c=runs["CAI"],
        cmap="viridis",
        s=50,
        alpha=0.8,
        edgecolors="grey",
        linewidths=0.5,
    )

    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("CAI total del Portafolio (GWh-eq)")

    ax.set_title("Frontera de Pareto (Portafolio P=2)")
    ax.set_xlabel("Costo Anualizado del Portafolio (Millones USD)")
    ax.set_ylabel("Consumo de Agua del Portafolio (Miles m³/año)")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_6_5_pareto.pdf", format="pdf")
    fig.savefig(FIGURES_DIR / "fig_6_5_pareto.png", dpi=300)
    plt.close(fig)


def main():
    print("=== Yakhchal DataCenter — Generación de Figuras ===\n")
    plot_mapa()
    plot_climatologia()
    plot_coeficientes()
    plot_cai()
    plot_pareto()
    print("\nTodas las figuras se han guardado exitosamente en /figures/.")

    # Copiar localmente al directorio de Quarto para evitar restricciones de Typst
    paper_fig_dir = ROOT / "docs" / "ieee-paper" / "figures"
    paper_fig_dir.mkdir(parents=True, exist_ok=True)
    for p in FIGURES_DIR.glob("fig_6_*.png"):
        shutil.copy(p, paper_fig_dir / p.name)
    for p in FIGURES_DIR.glob("fig_6_*.pdf"):
        shutil.copy(p, paper_fig_dir / p.name)
    print(
        "Figuras copiadas localmente a docs/ieee-paper/figures/ para la compilación de Typst."
    )


if __name__ == "__main__":
    main()
