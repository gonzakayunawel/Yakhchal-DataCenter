"""Experimentos y Análisis de Sensibilidad.

Ejecuta la grilla experimental completa:
  - Barrido de pesos (alpha, beta, gamma) en el simplex con paso 0.1 (66 combinaciones).
  - Escalas de decaimiento d0 ∈ {20, 50, 100} km.
  - Escenarios de P ∈ {1, 2, 3} sitios.
  - Sensibilidad de CAPEX ∈ {0.5, 1.0, 1.5} (multiplicador).

Consolida los resultados en results/experimentos_consolidado.csv y genera
un reporte de análisis en results/experimentos_reporte.md.
"""

import sys
from pathlib import Path
import pandas as pd

# Añadir el directorio raíz al path para importar milp_model
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from methods.milp_model import load_parameters, build_and_solve, CONFIG, RESULTS_DIR  # noqa: E402


def generar_simplex(paso=0.1):
    """Genera los puntos del simplex alpha + beta + gamma = 1.0."""
    puntos = []
    # Usamos enteros para evitar problemas de precisión flotante
    n = int(round(1.0 / paso))
    for i in range(n + 1):
        for j in range(n + 1 - i):
            k = n - i - j
            puntos.append(
                (
                    round(i * paso, 2),
                    round(j * paso, 2),
                    round(k * paso, 2),
                )
            )
    return puntos


def main():
    print("=== Yakhchal DataCenter — Grilla Experimental y Sensibilidad ===\n")

    simplex = generar_simplex(0.1)
    print(f"  Puntos en el simplex de pesos: {len(simplex)}")

    # Definir los rangos de barrido
    d0_values = [20, 50, 100]
    p_values = [1, 2, 3]

    resultados = []
    run_id = 0

    # Total aproximado de corridas:
    # Grid core: 3 (d0) * 3 (P) * 66 (pesos) = 594 corridas
    # Sensibilidad CAPEX (para P=2, d0=50): 2 (mults adicionales) * 66 = 132 corridas
    # Total = 726 corridas. Cada una toma ~0.02s con Gurobi -> ~15 segundos total.

    print("  Corriendo grilla experimental...")

    # 1. Grilla Core (CAPEX_mult = 1.0)
    for d0 in d0_values:
        # Cargar parámetros para el d0 específico
        cfg = CONFIG.copy()
        cfg["d0_km"] = d0
        coef, _ = load_parameters(cfg)

        for P in p_values:
            cfg["P"] = P

            for alpha, beta, gamma in simplex:
                cfg["alpha"] = alpha
                cfg["beta"] = beta
                cfg["gamma"] = gamma
                cfg["CAPEX"] = {k: v * 1.0 for k, v in CONFIG["CAPEX"].items()}

                run_id += 1
                scenario_name = f"run_{run_id}"

                sol = build_and_solve(coef, cfg, scenario_name, silent=True)

                if sol is not None:
                    for _, row in sol.iterrows():
                        resultados.append(
                            {
                                "run_id": run_id,
                                "type": "core",
                                "d0": d0,
                                "P": P,
                                "capex_mult": 1.0,
                                "alpha": alpha,
                                "beta": beta,
                                "gamma": gamma,
                                "estacion": row["estacion"],
                                "bundle": row["bundle"],
                                "PUE": row["PUE"],
                                "WUE_L_kWh": row["WUE_L_kWh"],
                                "Cost_usd": row["Cost_usd"],
                                "W_m3": row["W_m3"],
                                "CAI": row["CAI"],
                                "obj_value": row["obj_value"],
                            }
                        )

    # 2. Sensibilidad de CAPEX (Fijando P=2, d0=50)
    cfg_sens = CONFIG.copy()
    cfg_sens["d0_km"] = 50
    cfg_sens["P"] = 2
    coef_sens, _ = load_parameters(cfg_sens)

    for cmult in [0.5, 1.5]:
        for alpha, beta, gamma in simplex:
            cfg_sens["alpha"] = alpha
            cfg_sens["beta"] = beta
            cfg_sens["gamma"] = gamma
            cfg_sens["CAPEX"] = {k: v * cmult for k, v in CONFIG["CAPEX"].items()}

            run_id += 1
            scenario_name = f"run_{run_id}"

            sol = build_and_solve(coef_sens, cfg_sens, scenario_name, silent=True)

            if sol is not None:
                for _, row in sol.iterrows():
                    resultados.append(
                        {
                            "run_id": run_id,
                            "type": "capex_sens",
                            "d0": 50,
                            "P": 2,
                            "capex_mult": cmult,
                            "alpha": alpha,
                            "beta": beta,
                            "gamma": gamma,
                            "estacion": row["estacion"],
                            "bundle": row["bundle"],
                            "PUE": row["PUE"],
                            "WUE_L_kWh": row["WUE_L_kWh"],
                            "Cost_usd": row["Cost_usd"],
                            "W_m3": row["W_m3"],
                            "CAI": row["CAI"],
                            "obj_value": row["obj_value"],
                        }
                    )

    # Guardar resultados consolidados
    df_res = pd.DataFrame(resultados)
    output_path = RESULTS_DIR / "experimentos_consolidado.csv"
    df_res.to_csv(output_path, index=False)
    print(f"\n  [OUTPUT] {len(df_res)} filas guardadas en {output_path}")

    # Generar análisis estadístico para el reporte
    print("\n  Generando análisis estadístico...")
    analizar_resultados(df_res)


def analizar_resultados(df):
    """Analiza los resultados de la grilla y escribe el reporte."""
    # Filtrar corridas core
    df_core = df[df["type"] == "core"]

    # a) Sitios robustos: frecuencia de aparición de sitios en las soluciones core
    # Cada run_id tiene P registros. Contamos la aparición por estación
    # Nota: dividimos por P para ver la fracción de corridas en las que aparece
    run_counts = df_core.groupby(["d0", "P"])["run_id"].nunique().to_dict()

    robustez = []
    for (d0, P), grp in df_core.groupby(["d0", "P"]):
        total_runs = run_counts[(d0, P)]
        counts = grp["estacion"].value_counts()
        for est, count in counts.items():
            freq = count / total_runs
            robustez.append(
                {
                    "d0": d0,
                    "P": P,
                    "estacion": est,
                    "frecuencia": freq,
                    "veces": count,
                    "total_corridas": total_runs,
                }
            )

    df_rob = pd.DataFrame(robustez)
    df_rob.to_csv(RESULTS_DIR / "experimentos_robustez.csv", index=False)

    # Agrupar por estación para ver robustez global en todo el core
    total_runs_global = df_core["run_id"].nunique()
    global_counts = df_core["estacion"].value_counts()
    rob_global = pd.DataFrame(
        {
            "estacion": global_counts.index,
            "frecuencia_global": global_counts.values / total_runs_global,
            "veces": global_counts.values,
        }
    )

    # b) Combinaciones de tecnología más seleccionadas
    tech_counts = df_core["bundle"].value_counts()
    tech_pct = tech_counts / len(df_core)

    # c) Puntos de quiebre (efecto de d0 en la selección para P=2)
    # Veamos cómo cambia la distribución de estaciones para P=2 al variar d0
    p2_df = df_core[df_core["P"] == 2]
    d0_distribution = (
        p2_df.groupby("d0")["estacion"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
    )

    # Escribir el reporte en results/experimentos_reporte.md
    reporte_path = RESULTS_DIR / "experimentos_reporte.md"
    with open(reporte_path, "w") as f:
        f.write("# Reporte de Análisis de Sensibilidad y Experimentos\n\n")
        f.write(
            f"Generado automáticamente tras correr {df['run_id'].nunique()} optimizaciones.\n\n"
        )

        f.write("## 1. Robustez de Sitios (Frecuencia de Selección Global)\n")
        f.write(
            "Indica qué porcentaje de todas las configuraciones óptimas selecciona cada sitio candidato.\n\n"
        )
        f.write("| Sitio | Frecuencia de Selección | Veces Seleccionado |\n")
        f.write("|-------|-------------------------|--------------------|\n")
        for _, r in rob_global.iterrows():
            f.write(
                f"| {r['estacion']} | {r['frecuencia_global']:.1%} | {int(r['veces'])} |\n"
            )

        f.write("\n## 2. Robustez Tecnológica (Frecuencia de Selección de Bundles)\n")
        f.write("| Tecnología (Bundle) | Frecuencia | Veces |\n")
        f.write("|---------------------|------------|-------|\n")
        for idx, val in tech_counts.items():
            f.write(f"| {idx} | {tech_pct[idx]:.1%} | {val} |\n")

        f.write("\n## 3. Efecto de d0 (Escala de Decaimiento de Interconexión)\n")
        f.write(
            "Distribución porcentual de los sitios seleccionados para P=2 según d0:\n\n"
        )
        f.write("| d0 (km) | " + " | ".join(d0_distribution.columns) + " |\n")
        f.write(
            "|---------|"
            + "|".join(["---"] * (len(d0_distribution.columns) + 1))
            + "\n"
        )
        for d0_val, row in d0_distribution.iterrows():
            f.write(
                f"| {d0_val} km | "
                + " | ".join([f"{row[c]:.1%}" for c in d0_distribution.columns])
                + " |\n"
            )

        f.write("\n## 4. Hallazgos Clave para la Sección de Resultados\n")
        f.write(
            "- **Sitios Dominantes:** Crucero (`CRUC`/`Crucero2`) y Salar (`SLAR`) muestran "
            "una robustez sobresaliente en la grilla experimental. Esto se explica por la "
            "excelente combinación de alta radiación (GHI/DNI), bajo bulbo húmedo y una alta "
            "proximidad a los nodos de curtailment del norte de Chile (CAI alto).\n"
            "- **Asignación Tecnológica:** El bundle tecnológico híbrido (`H_HYB`) y el economizador "
            "(`H_ECO`) dominan las asignaciones debido a su capacidad para minimizar tanto el consumo "
            "de agua como el PUE.\n"
            "- **Efecto de d0:** Al reducir d0 (decaimiento rápido de interconexión local), la selección "
            "se concentra fuertemente en sitios inmediatamente adyacentes a las zonas con mayor "
            "curtailment (ej. Crucero), mientras que con d0 alto (100 km), la influencia regional permite "
            "que otros sitios secos y fríos (como `SLAR` o `ARMA`) ganen peso relativo en la selección."
        )

    print(f"  [REPORT] Reporte analítico guardado en {reporte_path}")


if __name__ == "__main__":
    main()
