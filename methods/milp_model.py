"""Etapa 1 — Modelo MILP de localización y selección tecnológica (Gurobi).

Especificación de referencia: secciones 1–6 de docs/Idea_discusion.md

Conjuntos:
  I = sitios candidatos (estaciones solares con z_i = 1)
  H = {H_RAD, H_ECO, H_HYB, H_CONV} — bundles tecnológicos

Variables:
  x_i ∈ {0,1} — 1 si se desarrolla datacenter en sitio i
  y_ih ∈ {0,1} — 1 si sitio i usa bundle h

Función objetivo: min α·Σ Cost_hat·y + β·Σ W_hat·y − γ·Σ CAI_hat·x
  (normalización min-max, pesos α+β+γ=1)

Restricciones R1–R7 (R6, R7 opcionales).

Solver: Gurobi (licencia académica).
"""

import json
from pathlib import Path

import pandas as pd
import gurobipy as gp
from gurobipy import GRB

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN — todos los parámetros de diseño en un solo bloque
# ═══════════════════════════════════════════════════════════════════════════
CONFIG = {
    # --- Carga IT ---
    "L_kW": 1000,  # 1 MW — datacenter modular pequeño (documentado)
    "N_hours": 8760,  # horas por año
    # --- Precios ---
    # Costo marginal zona norte Chile (proxy): ~80 USD/MWh ≈ 0.08 USD/kWh
    # Fuente: CNE, Informe de Precio Nudo promedio (valor ilustrativo declarado)
    "p_energy_usd_kwh": 0.08,
    # Agua industrial norte de Chile: ~2–5 USD/m³ (desalación/industrial)
    # Fuente: valor ilustrativo, rango de tarifas industriales zona norte
    "p_water_usd_m3": 3.0,
    # --- CAPEX por bundle (USD/kW) ---
    # Fuente: PNNL-24904 (Fernandez et al. 2015) — proxy de edificios
    # comerciales, NO datacenters. Declarado explícitamente como proxy.
    "CAPEX": {
        "H_CONV": 500,  # chiller convencional — referencia base
        "H_ECO": 600,  # economizador — costo incremental de IEC
        "H_RAD": 700,  # radiativo — paneles radiantes + respaldo
        "H_HYB": 800,  # híbrido — cascada completa
    },
    # --- Restricciones de diseño ---
    "P": 2,  # número de sitios a desarrollar (caso base)
    "Budget": 2_000_000,  # presupuesto total CAPEX (USD, caso base)
    # --- Pesos del objetivo (caso base) ---
    "alpha": 0.4,  # peso costo
    "beta": 0.3,  # peso agua
    "gamma": 0.3,  # peso CAI (sostenibilidad energética)
    # --- Restricciones opcionales ---
    "enable_R6": False,  # piso mínimo CAI
    "CAI_min": 0,  # valor mínimo si R6 activa
    "enable_R7": False,  # techo de agua por sitio (sin datos DGA)
    "W_max_m3": 1e9,  # placeholder si R7 activa
    # --- CAI ---
    "d0_km": 50,  # distancia característica default para CAI
}


def load_parameters(config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga coeficientes de Etapa 0 y CAI, calcula Cost/W derivados."""
    coef = pd.read_csv(RESULTS_DIR / "etapa0_coeficientes.csv")
    # Filtrar solo sitios con z_i = 1 y bundles factibles (PUE < 90)
    coef = coef[(coef["z_i"] == 1) & (coef["PUE"] < 90)].copy()

    L = config["L_kW"]
    N = config["N_hours"]

    # Consumo anual de energía y agua
    coef["E_kwh"] = coef["PUE"] * L * N  # kWh/año
    coef["W_m3"] = coef["WUE_L_kWh"] * L * N / 1000  # m³/año

    # Costo total anualizado (CAPEX + OPEX energía + OPEX agua)
    coef["CAPEX_usd"] = coef["bundle"].map(config["CAPEX"]) * L
    coef["Cost_usd"] = (
        coef["CAPEX_usd"]
        + config["p_energy_usd_kwh"] * coef["E_kwh"]
        + config["p_water_usd_m3"] * coef["W_m3"]
    )

    # CAI por sitio
    d0 = config["d0_km"]
    cai_file = RESULTS_DIR / "cai_por_sitio.csv"
    if cai_file.exists():
        cai_df = pd.read_csv(cai_file)
        cai_col = f"CAI_total_d{d0}"
        if cai_col not in cai_df.columns:
            print(f"  [WARN] Columna {cai_col} no encontrada, usando CAI_total_d50")
            cai_col = "CAI_total_d50"
        cai_map = dict(zip(cai_df["estacion"], cai_df[cai_col]))
    else:
        print("  [WARN] cai_por_sitio.csv no encontrado, usando CAI=0")
        cai_map = {}

    coef["CAI"] = coef["estacion"].map(cai_map).fillna(0)

    cai_result = pd.DataFrame([{"estacion": k, "CAI": v} for k, v in cai_map.items()])
    return coef, cai_result


def normalize_minmax(series: pd.Series) -> pd.Series:
    """Normalización min-max a [0, 1]."""
    vmin, vmax = series.min(), series.max()
    if vmax == vmin:
        return pd.Series(0.5, index=series.index)
    return (series - vmin) / (vmax - vmin)


def build_and_solve(
    coef: pd.DataFrame,
    config: dict,
    scenario_name: str = "base",
    silent: bool = False,
) -> pd.DataFrame | None:
    """Construye y resuelve el modelo MILP con Gurobi."""
    sites = sorted(coef["estacion"].unique())
    bundles = sorted(coef["bundle"].unique())

    # --- Normalización min-max ---
    coef = coef.copy()
    coef["Cost_hat"] = normalize_minmax(coef["Cost_usd"])
    coef["W_hat"] = normalize_minmax(coef["W_m3"])

    # CAI normalizado sobre los sitios
    cai_vals = coef.groupby("estacion")["CAI"].first()
    cai_norm = normalize_minmax(cai_vals)
    cai_hat = dict(zip(cai_norm.index, cai_norm.values))

    # Lookup rápido para coeficientes
    cost_hat = {}
    w_hat = {}
    capex_usd = {}
    w_m3 = {}
    for _, row in coef.iterrows():
        key = (row["estacion"], row["bundle"])
        cost_hat[key] = row["Cost_hat"]
        w_hat[key] = row["W_hat"]
        capex_usd[key] = row["CAPEX_usd"]
        w_m3[key] = row["W_m3"]

    # Pares (i, h) factibles
    feasible = set(zip(coef["estacion"], coef["bundle"]))

    alpha = config["alpha"]
    beta = config["beta"]
    gamma = config["gamma"]
    P = config["P"]
    Budget = config["Budget"]

    # --- Modelo Gurobi ---
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0 if silent else 1)
    env.start()

    m = gp.Model("Yakhchal_MILP", env=env)

    # Variables binarias
    x = m.addVars(sites, vtype=GRB.BINARY, name="x")
    y = m.addVars(
        [(i, h) for i in sites for h in bundles if (i, h) in feasible],
        vtype=GRB.BINARY,
        name="y",
    )

    # --- Función objetivo ---
    obj = (
        alpha * gp.quicksum(cost_hat[k] * y[k] for k in y)
        + beta * gp.quicksum(w_hat[k] * y[k] for k in y)
        - gamma * gp.quicksum(cai_hat.get(i, 0) * x[i] for i in sites)
    )
    m.setObjective(obj, GRB.MINIMIZE)

    # --- Restricciones ---
    # R1: Asignación tecnológica única por sitio
    for i in sites:
        feasible_h = [h for h in bundles if (i, h) in feasible]
        m.addConstr(
            gp.quicksum(y[i, h] for h in feasible_h) == x[i],
            name=f"R1_{i}",
        )

    # R2: Consistencia y_ih <= x_i
    for i, h in y:
        m.addConstr(y[i, h] <= x[i], name=f"R2_{i}_{h}")

    # R3: Screening climático — implícito (solo z_i=1 en 'sites')

    # R4: Número de sitios
    m.addConstr(gp.quicksum(x[i] for i in sites) == P, name="R4_sites")

    # R5: Presupuesto
    m.addConstr(
        gp.quicksum(capex_usd[k] * y[k] for k in y) <= Budget,
        name="R5_budget",
    )

    # R6: Piso CAI (opcional)
    if config["enable_R6"]:
        m.addConstr(
            gp.quicksum(cai_vals.get(i, 0) * x[i] for i in sites) >= config["CAI_min"],
            name="R6_cai_floor",
        )

    # R7: Techo de agua (opcional, sin datos DGA reales)
    if config["enable_R7"]:
        for i in sites:
            feasible_h = [h for h in bundles if (i, h) in feasible]
            m.addConstr(
                gp.quicksum(w_m3[i, h] * y[i, h] for h in feasible_h)
                <= config["W_max_m3"],
                name=f"R7_{i}",
            )

    # --- Resolver ---
    m.optimize()

    if m.Status == GRB.OPTIMAL:
        if not silent:
            print(f"\n  ✅ Solución óptima encontrada. Obj = {m.ObjVal:.4f}")
            print(f"     Gap = {m.MIPGap:.2%}, Tiempo = {m.Runtime:.2f}s")
    elif m.Status == GRB.INFEASIBLE:
        if not silent:
            print("  ⚠️ Modelo infactible.")
        env.dispose()
        return None
    else:
        if not silent:
            print(f"  ⚠️ Status Gurobi: {m.Status}")
        env.dispose()
        return None

    # --- Extraer solución ---
    results = []
    for i in sites:
        if x[i].X > 0.5:
            for h in bundles:
                if (i, h) in feasible and y[i, h].X > 0.5:
                    row = coef[(coef["estacion"] == i) & (coef["bundle"] == h)].iloc[0]
                    results.append(
                        {
                            "escenario": scenario_name,
                            "estacion": i,
                            "bundle": h,
                            "PUE": row["PUE"],
                            "WUE_L_kWh": row["WUE_L_kWh"],
                            "E_kwh": row["E_kwh"],
                            "W_m3": row["W_m3"],
                            "CAPEX_usd": row["CAPEX_usd"],
                            "Cost_usd": row["Cost_usd"],
                            "CAI": row["CAI"],
                            "Cost_hat": row["Cost_hat"],
                            "W_hat": row["W_hat"],
                            "obj_value": m.ObjVal,
                            "gap": m.MIPGap,
                            "runtime_s": m.Runtime,
                        }
                    )

    sol_df = pd.DataFrame(results)
    sol_path = RESULTS_DIR / f"milp_solucion_{scenario_name}.csv"
    sol_df.to_csv(sol_path, index=False)

    if not silent:
        print(f"\n  Solución ({scenario_name}):")
        for _, r in sol_df.iterrows():
            print(
                f"    {r['estacion']:10s} → {r['bundle']:6s}  "
                f"PUE={r['PUE']:.3f}  WUE={r['WUE_L_kWh']:.3f}  "
                f"Cost=${r['Cost_usd']:,.0f}  CAI={r['CAI']:.0f}"
            )
        print(f"  → {sol_path}")

    env.dispose()
    return sol_df


def run_verification(config):
    """Verificación del modelo (tarea 4.6)."""
    print("\n[VERIFICACIÓN] Ejecutando tests de validación...\n")
    all_passed = True

    # Test 1: P=1, debe seleccionar algún sitio
    print("  Test 1: P=1 → solución trivial")
    cfg1 = {**config, "P": 1, "Budget": 10_000_000}
    coef1, _ = load_parameters(cfg1)
    sol1 = build_and_solve(coef1, cfg1, "test_P1", silent=True)
    if sol1 is not None and len(sol1) == 1:
        print(
            f"    ✅ PASS: seleccionó {sol1.iloc[0]['estacion']} → {sol1.iloc[0]['bundle']}"
        )
    else:
        print("    ❌ FAIL")
        all_passed = False

    # Test 2: α=1 (solo costo)
    print("  Test 2: α=1 (solo costo)")
    cfg2 = {
        **config,
        "alpha": 1.0,
        "beta": 0.0,
        "gamma": 0.0,
        "P": 1,
        "Budget": 10_000_000,
    }
    coef2, _ = load_parameters(cfg2)
    sol2 = build_and_solve(coef2, cfg2, "test_cost", silent=True)
    if sol2 is not None and sol2.iloc[0]["Cost_usd"] == coef2["Cost_usd"].min():
        print(
            f"    ✅ PASS: {sol2.iloc[0]['estacion']} → {sol2.iloc[0]['bundle']} "
            f"(Cost=${sol2.iloc[0]['Cost_usd']:,.0f} = mínimo global)"
        )
    else:
        print("    ❌ FAIL: no eligió la combinación de costo mínimo")
        all_passed = False

    # Test 3: β=1 (solo agua)
    print("  Test 3: β=1 (solo agua)")
    cfg3 = {
        **config,
        "alpha": 0.0,
        "beta": 1.0,
        "gamma": 0.0,
        "P": 1,
        "Budget": 10_000_000,
    }
    coef3, _ = load_parameters(cfg3)
    sol3 = build_and_solve(coef3, cfg3, "test_water", silent=True)
    if sol3 is not None and sol3.iloc[0]["W_m3"] == coef3["W_m3"].min():
        print(
            f"    ✅ PASS: {sol3.iloc[0]['estacion']} → {sol3.iloc[0]['bundle']} "
            f"(WUE={sol3.iloc[0]['WUE_L_kWh']:.3f} = mínimo global)"
        )
    else:
        print("    ❌ FAIL: no eligió la combinación de menor consumo de agua")
        all_passed = False

    # Test 4: γ=1 (solo CAI)
    print("  Test 4: γ=1 (solo CAI)")
    cfg4 = {
        **config,
        "alpha": 0.0,
        "beta": 0.0,
        "gamma": 1.0,
        "P": 1,
        "Budget": 10_000_000,
    }
    coef4, _ = load_parameters(cfg4)
    sol4 = build_and_solve(coef4, cfg4, "test_cai", silent=True)
    if sol4 is not None and sol4.iloc[0]["CAI"] == coef4["CAI"].max():
        print(
            f"    ✅ PASS: {sol4.iloc[0]['estacion']} → {sol4.iloc[0]['bundle']} "
            f"(CAI={sol4.iloc[0]['CAI']:.0f} = máximo global)"
        )
    else:
        print("    ❌ FAIL: no eligió el sitio con mayor CAI")
        all_passed = False

    # Test 5: Budget=0 → infactible
    print("  Test 5: Budget=0 → debe ser infactible")
    cfg5 = {**config, "Budget": 0, "P": 1}
    coef5, _ = load_parameters(cfg5)
    sol5 = build_and_solve(coef5, cfg5, "test_infeasible", silent=True)
    if sol5 is None:
        print("    ✅ PASS: correctamente infactible")
    else:
        print("    ❌ FAIL: debió ser infactible")
        all_passed = False

    return all_passed


def main():
    print("=== Yakhchal DataCenter — Etapa 1: Modelo MILP (Gurobi) ===\n")

    print("[1/4] Cargando parámetros desde Etapa 0 y CAI...")
    coef, cai_df = load_parameters(CONFIG)
    sites = sorted(coef["estacion"].unique())
    bundles = sorted(coef["bundle"].unique())
    print(f"  {len(sites)} sitios factibles, {len(bundles)} bundles")
    print(f"  {len(coef)} combinaciones (sitio, bundle) factibles")

    print("\n  Configuración:")
    print(
        f"    L = {CONFIG['L_kW']} kW, P = {CONFIG['P']}, Budget = ${CONFIG['Budget']:,}"
    )
    print(
        f"    p_energy = {CONFIG['p_energy_usd_kwh']} USD/kWh, p_water = {CONFIG['p_water_usd_m3']} USD/m³"
    )
    print(f"    Pesos: α={CONFIG['alpha']}, β={CONFIG['beta']}, γ={CONFIG['gamma']}")
    print("    Solver: Gurobi (licencia académica)")

    print("\n[2/4] Construyendo y resolviendo modelo MILP...")
    build_and_solve(coef, CONFIG, "base")

    print("\n[3/4] Verificación del modelo...")
    all_passed = run_verification(CONFIG)

    if all_passed:
        print("\n✅ Todos los tests de verificación pasaron.")
    else:
        print("\n⚠️ Algunos tests no pasaron — revisar antes de continuar.")

    # Guardar log de configuración
    log_path = RESULTS_DIR / "milp_solver_log.json"
    with open(log_path, "w") as f_log:
        json.dump(
            {
                "solver": "Gurobi",
                "config": {k: v for k, v in CONFIG.items() if k != "CAPEX"},
                "capex": CONFIG["CAPEX"],
                "sites_used": sites,
                "bundles_used": bundles,
                "n_feasible_combos": len(coef),
            },
            f_log,
            indent=2,
        )
    print(f"\n  Config log → {log_path}")

    print("\nMisión completada, Capitán. Modelo MILP Gurobi operacional.")


if __name__ == "__main__":
    main()
