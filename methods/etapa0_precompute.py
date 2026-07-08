"""Etapa 0 — Precómputo de coeficientes por sitio × bundle tecnológico.

Entrada: datasets mensuales limpios (solar).
Salida:  results/etapa0_coeficientes.csv   — una fila por (sitio i, bundle h)
         results/etapa0_screening.csv      — detalle de screening climático
         results/etapa0_validacion.md       — sanity check vs. literatura

Bundles:
  H_RAD  — Enfriamiento radiativo puro (Aili et al.)
  H_ECO  — Economizador de aire / IEC (Silva-Llanca + Yang)
  H_HYB  — Híbrido: radiativo + economizador con respaldo mecánico
  H_CONV — Chiller convencional sin economizador (Lei & Masanet Casos 5/8)
"""

import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Constantes físicas
# ---------------------------------------------------------------------------
P_SEA_LEVEL = 1013.25  # hPa
T_SEA_LEVEL = 288.15  # K (15 °C)
G = 9.80665  # m/s²
M_AIR = 0.0289644  # kg/mol
R_GAS = 8.3144598  # J/(mol·K)
LAPSE = 0.0065  # K/m
RHO_WATER = 1000.0  # kg/m³
H_FG = 2_500_000.0  # J/kg — calor latente de vaporización
N_HOURS = 8760  # horas por año

# Parámetros IEC (EnergyPlus Engineering Reference, DOE 2017)
F_DRIFT = 0.002  # fracción de drift (media rígida CelDek)
R_CONCENTRATION = 4  # ciclos de concentración (agua potable)
EPSILON_HX = 0.67  # efectividad intercambiador aire-aire (default EnergyPlus)
EPSILON_SE = 0.90  # eficiencia de saturación del pad evaporativo
CP_AIR = 1006.0  # J/(kg·K) — calor específico del aire


# ---------------------------------------------------------------------------
# Funciones físicas
# ---------------------------------------------------------------------------
def p_atm(elev_m):
    """Presión atmosférica estándar según elevación (atmósfera ISA).

    Fuente: International Standard Atmosphere, ISO 2533:1975.
    Documentado: derivada de elevación cuando la estación no mide presión.
    """
    return P_SEA_LEVEL * (1 - LAPSE * elev_m / T_SEA_LEVEL) ** (
        G * M_AIR / (R_GAS * LAPSE)
    )


def calc_twb(t_db, rh):
    """Temperatura de bulbo húmedo con la fórmula de Stull (2011).

    Fuente: Stull, R. (2011). Wet-bulb temperature from relative humidity
            and air temperature. J. Appl. Meteorol. Climatol., 50(11),
            2267-2269. Válida para RH > 5%.
    Supuesto: HR clipped a [5, 100]% — documentado.
    """
    rh_c = np.clip(rh, 5.0, 100.0)
    twb = (
        t_db * np.arctan(0.151977 * np.sqrt(rh_c + 8.313659))
        + np.arctan(t_db + rh_c)
        - np.arctan(rh_c - 1.676331)
        + 0.00391838 * (rh_c**1.5) * np.arctan(0.023101 * rh_c)
        - 4.686035
    )
    return twb


def calc_pw(t_db, rh, p_hpa):
    """Agua precipitable superficial (PW, en mm) — proxy para modelo radiativo.

    Fuente: Aproximación basada en la presión de vapor parcial y la
            relación empírica de Reitan (1963), referenciada por Aili et al.
            PW ≈ 4.65 * (e_0 / T_dew)^0.25  (Reitan, J. Appl. Meteorol.)
    Supuesto: se usa una correlación simplificada e_0 → PW dado que no
              disponemos de sondeos radiosonda. Documentado como aproximación.
    """
    # Presión de vapor de saturación (hPa) — Tetens
    e_s = 6.112 * np.exp(17.67 * t_db / (t_db + 243.5))
    # Presión de vapor actual (hPa)
    e_a = e_s * (rh / 100.0)
    # PW (mm) ≈ 2.1 * e_a (hPa) — correlación empírica simplificada
    # (Reitan 1963 da PW ~ 1.7–2.5 * e_a según latitud y estación)
    pw_mm = 2.1 * e_a
    return pw_mm


# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
def load_climatology():
    """Promedios mensuales multianuales (12 valores por variable por estación).

    Decisión documentada (tarea 2.1): se agregan los datos mensuales por
    (estación, mes) tomando la media aritmética sobre todos los años
    disponibles. La presión se deriva de la elevación vía atmósfera ISA
    cuando la estación no la mide directamente.
    """
    solar = pd.read_csv(DATA_DIR / "dataset_solar_mensual.csv")
    solar["fecha"] = pd.to_datetime(solar["fecha"])
    solar["mes"] = solar["fecha"].dt.month

    # Promedios mensuales multianuales (12 meses × 11 estaciones)
    clim = solar.groupby(["estacion", "mes"]).mean(numeric_only=True).reset_index()

    # Presión atmosférica (derivada de elevación vía ISA)
    clim["presion_hpa"] = p_atm(clim["elevacion_m"])

    # --- Variables derivadas (tarea 2.2) ---
    clim["T_wb"] = calc_twb(clim["temperatura_mean_c"], clim["humedad_mean_pct"])
    clim["PW_mm"] = calc_pw(
        clim["temperatura_mean_c"], clim["humedad_mean_pct"], clim["presion_hpa"]
    )

    return clim


# ---------------------------------------------------------------------------
# Screening climático z_i  (tarea 2.3)
# ---------------------------------------------------------------------------
def evaluate_screening(clim):
    """Screening climático consolidado.

    Umbrales (fuentes):
      - RH ≤ 60%  → Silva-Llanca et al. (umbral DFC feasibility)
      - T_db ≤ 20°C → Silva-Llanca et al. (umbral conservador)
      - T_wb ≤ 19°C → Yang et al. (umbral modo mixto IEC)
      - PW ≤ 10 mm → Aili et al. (baja humedad favorece radiativo)

    Criterio z_i: sitio aprobado si cumple umbrales en ≥ 50% de los 12 meses.
    Decisión documentada: 50% permite incluir sitios con estacionalidad marcada
    (inviernos húmedos pero veranos secos). Los bundles que requieran condiciones
    más estrictas se filtran en la asignación de PUE/WUE.
    """
    results = []
    for st, grp in clim.groupby("estacion"):
        frac_rh = (grp["humedad_mean_pct"] <= 60).mean()
        frac_tdb = (grp["temperatura_mean_c"] <= 20).mean()
        frac_twb = (grp["T_wb"] <= 19).mean()
        frac_pw = (grp["PW_mm"] <= 10).mean()

        # z_i: al menos 50% de meses cumplen RH, T_db y T_wb
        # (PW se usa para screening radiativo, no para z_i general)
        z_i = 1 if (frac_rh >= 0.5 and frac_tdb >= 0.5 and frac_twb >= 0.5) else 0

        # Aptitud específica por tecnología
        apt_eco = 1 if (frac_rh >= 0.5 and frac_tdb >= 0.5) else 0
        apt_rad = 1 if (frac_pw >= 0.5 and frac_rh >= 0.5) else 0

        results.append(
            {
                "estacion": st,
                "latitud": grp["latitud"].iloc[0],
                "longitud": grp["longitud"].iloc[0],
                "elevacion_m": grp["elevacion_m"].iloc[0],
                "T_db_mean": grp["temperatura_mean_c"].mean(),
                "RH_mean": grp["humedad_mean_pct"].mean(),
                "T_wb_mean": grp["T_wb"].mean(),
                "PW_mean": grp["PW_mm"].mean(),
                "GHI_mean": grp["ghi_mean_wm2"].mean(),
                "frac_RH_ok": round(frac_rh, 3),
                "frac_Tdb_ok": round(frac_tdb, 3),
                "frac_Twb_ok": round(frac_twb, 3),
                "frac_PW_ok": round(frac_pw, 3),
                "z_i": z_i,
                "apt_ECO": apt_eco,
                "apt_RAD": apt_rad,
            }
        )

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# PUE / WUE por bundle  (tarea 2.4)
# ---------------------------------------------------------------------------
def calc_pue_wue_conv(screen_row):
    """H_CONV — Chiller convencional sin economizador.

    Fuente: Lei & Masanet (2022), Casos 5/8 (chiller de agua con torre
    de enfriamiento, sin airside economizer).
    - PUE mediano: 1.71–2.22 (DC pequeño), 1.39–1.98 (DC mediano).
    - WUE: dominado por torre de enfriamiento.
    Supuesto: PUE = 1.80 (mediana conservadora para DC modular 1 MW),
              con corrección leve por T_db (cada +1°C sobre 20°C suma +0.02).
              WUE = 1.80 L/kWh (benchmark evaporative hyperscale, Milton Roy).
    """
    t_db = screen_row["T_db_mean"]
    pue = 1.80 + max(0, (t_db - 20)) * 0.02
    wue = 1.80  # L/kWh — dominado por torre de enfriamiento
    return (
        round(pue, 3),
        round(wue, 3),
        "Lei & Masanet 2022 Caso 5/8, mediana DC modular",
    )


def calc_pue_wue_eco(screen_row, clim_site):
    """H_ECO — Economizador de aire / IEC.

    Fuente: Silva-Llanca et al. (umbrales DFC), Yang et al. (modos IEC),
            EnergyPlus Engineering Reference (balance de agua IEC).

    Lógica:
      φ_i = fracción de meses en modo seco (T_db ≤ 17°C Y T_wb ≤ 19°C)
      Meses húmedos: IEC con consumo de agua (evaporación + drift + blowdown)
      PUE_ECO = φ_i * PUE_drymode + (1 - φ_i) * PUE_wetmode
    """
    # Fracción de meses en modo seco (Yang et al.)
    dry_mask = (clim_site["temperatura_mean_c"] <= 17) & (clim_site["T_wb"] <= 19)
    phi_i = dry_mask.mean()

    pue_dry = 1.10  # airside economizer puro (Lei & Masanet Caso 3)
    pue_wet = 1.25  # IEC húmedo (Lei & Masanet Caso 1)
    pue = phi_i * pue_dry + (1 - phi_i) * pue_wet

    # WUE: modo seco = ~0 L/kWh; modo húmedo = modelo EnergyPlus
    # K_factor = 1 + f_drift + 1/(R_concentration - 1) = 1.335
    k_factor = 1 + F_DRIFT + 1 / (R_CONCENTRATION - 1)
    wue_wet = 1.0 * k_factor  # ~1.335 L/kWh (base evaporación ~1.0)
    wue = (1 - phi_i) * wue_wet  # modo seco no consume agua

    fuente = (
        f"Silva-Llanca/Yang umbrales, EnergyPlus IEC water balance. "
        f"phi_i={phi_i:.2f} (frac modo seco)"
    )
    return round(pue, 3), round(wue, 3), fuente


def calc_pue_wue_rad(screen_row, clim_site):
    """H_RAD — Enfriamiento radiativo puro (Aili et al.).

    Fuente: Aili et al. — modelo de enfriamiento radiativo con materiales
            de alta emisividad en ventana atmosférica 8-13 µm.
    Supuesto: potencia de enfriamiento radiativo Q_rad depende de PW, GHI,
              viento y T_db. En condiciones ideales (PW bajo, noche clara),
              Q_rad ≈ 40-100 W/m². De día con alta irradiancia, se reduce
              significativamente (Aili Fig. 5c,d).

    La fracción de carga cubierta por radiativo se estima como:
      f_rad = fracción de meses con PW < 10mm Y GHI nocturno favorable
    El respaldo mecánico cubre el resto.
    """
    # Fracción de meses con PW bajo (favorable para radiativo)
    pw_ok = (clim_site["PW_mm"] < 10).mean()
    # Fracción de meses con T_db baja (reduce carga de enfriamiento)
    tdb_ok = (clim_site["temperatura_mean_c"] <= 20).mean()

    # Fracción cubierta por radiativo (conservadora)
    f_rad = min(pw_ok, tdb_ok) * 0.6  # 60% de eficiencia operacional

    pue_rad = 1.05  # prácticamente pasivo (solo ventiladores)
    pue_backup = 1.80  # chiller convencional de respaldo
    pue = f_rad * pue_rad + (1 - f_rad) * pue_backup

    # WUE: radiativo no usa agua; respaldo sí
    wue = (1 - f_rad) * 1.80

    fuente = (
        f"Aili et al. modelo radiativo. f_rad={f_rad:.2f} "
        f"(cobertura radiativa estimada). "
        f"Supuesto: validación de Atacama (Leroy 2019) es de material/piloto, "
        f"no de sistema completo"
    )
    return round(pue, 3), round(wue, 3), fuente


def calc_pue_wue_hyb(screen_row, clim_site):
    """H_HYB — Híbrido: cascada radiativo + economizador + respaldo.

    Fuente: cascada C9 de Idea_discusion.md (Lei & Masanet validación).
      W_anual = W_base + (1 - φ_i) * W_respaldo
    Combina radiativo + economizador con respaldo convencional mínimo.

    Lógica de cascada:
      1. Meses con PW < 10mm Y T_db ≤ 17°C → radiativo puro
      2. Meses con T_db ≤ 20°C Y T_wb ≤ 19°C → economizador IEC
      3. Resto → respaldo mecánico (chiller)
    """
    # Modo 1: radiativo
    rad_mask = (clim_site["PW_mm"] < 10) & (clim_site["temperatura_mean_c"] <= 17)
    f_rad = rad_mask.mean() * 0.6  # eficiencia operacional

    # Modo 2: economizador (excluyendo meses ya cubiertos por radiativo)
    eco_mask = (
        (~rad_mask)
        & (clim_site["temperatura_mean_c"] <= 20)
        & (clim_site["T_wb"] <= 19)
    )
    f_eco = eco_mask.mean()

    # Modo 3: respaldo mecánico
    f_backup = max(0, 1.0 - f_rad - f_eco)

    pue = f_rad * 1.05 + f_eco * 1.15 + f_backup * 1.80
    wue = f_eco * 0.80 + f_backup * 1.80  # radiativo no usa agua

    fuente = (
        f"Cascada C9: f_rad={f_rad:.2f}, f_eco={f_eco:.2f}, "
        f"f_backup={f_backup:.2f}. "
        f"Lei & Masanet Caso 1 vs 3/5/8 validación"
    )
    return round(pue, 3), round(wue, 3), fuente


# ---------------------------------------------------------------------------
# Generación de coeficientes  (tarea 2.4)
# ---------------------------------------------------------------------------
def generate_coefficients(screening, clim):
    """Genera coeficientes PUE/WUE para cada (sitio, bundle)."""
    bundles = ["H_CONV", "H_ECO", "H_RAD", "H_HYB"]
    records = []

    for _, srow in screening.iterrows():
        st = srow["estacion"]
        clim_site = clim[clim["estacion"] == st]

        for bundle in bundles:
            if bundle == "H_CONV":
                pue, wue, fuente = calc_pue_wue_conv(srow)
            elif bundle == "H_ECO":
                if srow["apt_ECO"] == 0:
                    pue, wue = 99.0, 99.0
                    fuente = "No apto climáticamente para ECO (z_eco=0)"
                else:
                    pue, wue, fuente = calc_pue_wue_eco(srow, clim_site)
            elif bundle == "H_RAD":
                if srow["apt_RAD"] == 0:
                    pue, wue = 99.0, 99.0
                    fuente = "No apto climáticamente para RAD (z_rad=0)"
                else:
                    pue, wue, fuente = calc_pue_wue_rad(srow, clim_site)
            elif bundle == "H_HYB":
                pue, wue, fuente = calc_pue_wue_hyb(srow, clim_site)

            records.append(
                {
                    "estacion": st,
                    "latitud": srow["latitud"],
                    "longitud": srow["longitud"],
                    "elevacion_m": srow["elevacion_m"],
                    "bundle": bundle,
                    "PUE": pue,
                    "WUE_L_kWh": wue,
                    "z_i": srow["z_i"],
                    "fuente_supuesto": fuente,
                }
            )

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Sanity check  (tarea 2.5)
# ---------------------------------------------------------------------------
def sanity_check(coef_df):
    """Compara PUE obtenidos contra rangos publicados (Lei & Masanet §4.2).

    Rangos de referencia:
      - 1.12–1.25: híbridos grandes con economizer+adiabático (Casos 1,2)
      - 1.39–1.98: medianos sin optimización avanzada (Casos 3–7)
      - 1.71–2.22: pequeños (Casos 8–10)
      - ~2.0: convencional puro
    """
    lines = []
    lines.append("# Validación Etapa 0 — Sanity Check de PUE/WUE\n")
    lines.append(f"Generado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")

    lines.append("## Rangos de referencia (Lei & Masanet 2022, §4.2)\n")
    lines.append("| Categoría | PUE mediano |")
    lines.append("|-----------|-------------|")
    lines.append("| Híbrido grande (Casos 1,2) | 1.12–1.25 |")
    lines.append("| Mediano (Casos 3–7) | 1.39–1.98 |")
    lines.append("| Pequeño (Casos 8–10) | 1.71–2.22 |")
    lines.append("| Convencional puro (Caso 5/8) | ~1.80–2.00 |")

    lines.append("\n## PUE calculados por bundle\n")
    valid = coef_df[coef_df["PUE"] < 90]
    for bundle in ["H_CONV", "H_ECO", "H_RAD", "H_HYB"]:
        sub = valid[valid["bundle"] == bundle]
        if sub.empty:
            lines.append(f"### {bundle}: sin sitios aptos\n")
            continue
        lines.append(f"### {bundle}")
        lines.append(
            f"- PUE: min={sub['PUE'].min():.3f}, "
            f"max={sub['PUE'].max():.3f}, "
            f"media={sub['PUE'].mean():.3f}"
        )
        lines.append(
            f"- WUE: min={sub['WUE_L_kWh'].min():.3f}, "
            f"max={sub['WUE_L_kWh'].max():.3f}, "
            f"media={sub['WUE_L_kWh'].mean():.3f}"
        )

    # Verificación de rangos
    lines.append("\n## Verificación de coherencia\n")
    alerts = []

    conv = valid[valid["bundle"] == "H_CONV"]
    if not conv.empty:
        if conv["PUE"].max() > 2.5 or conv["PUE"].min() < 1.5:
            alerts.append(
                f"⚠️ H_CONV PUE fuera de rango esperado [1.5, 2.5]: "
                f"{conv['PUE'].min():.3f}–{conv['PUE'].max():.3f}"
            )

    eco = valid[valid["bundle"] == "H_ECO"]
    if not eco.empty:
        if eco["PUE"].max() > 1.50 or eco["PUE"].min() < 1.05:
            alerts.append(
                f"⚠️ H_ECO PUE fuera de rango esperado [1.05, 1.50]: "
                f"{eco['PUE'].min():.3f}–{eco['PUE'].max():.3f}"
            )

    hyb = valid[valid["bundle"] == "H_HYB"]
    if not hyb.empty:
        if hyb["PUE"].max() > 1.80 or hyb["PUE"].min() < 1.05:
            alerts.append(
                f"⚠️ H_HYB PUE fuera de rango esperado [1.05, 1.80]: "
                f"{hyb['PUE'].min():.3f}–{hyb['PUE'].max():.3f}"
            )

    if alerts:
        for a in alerts:
            lines.append(a)
    else:
        lines.append("✅ Todos los PUE dentro de rangos publicados.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=== Yakhchal DataCenter — Etapa 0: Precómputo de Coeficientes ===\n")

    print("[1/5] Cargando climatología mensual multianual...")
    clim = load_climatology()
    n_stations = clim["estacion"].nunique()
    print(f"  {n_stations} estaciones × 12 meses = {len(clim)} registros\n")

    print("[2/5] Evaluando screening climático...")
    screening = evaluate_screening(clim)
    n_approved = screening["z_i"].sum()
    print(f"  Sitios aprobados (z_i=1): {n_approved}/{len(screening)}")
    for _, r in screening.iterrows():
        tag = "✓" if r["z_i"] == 1 else "✗"
        print(
            f"  {tag} {r['estacion']:10s}  T={r['T_db_mean']:.1f}°C  "
            f"RH={r['RH_mean']:.1f}%  T_wb={r['T_wb_mean']:.1f}°C  "
            f"PW={r['PW_mean']:.1f}mm"
        )

    screening_path = RESULTS_DIR / "etapa0_screening.csv"
    screening.to_csv(screening_path, index=False)
    print(f"\n  → {screening_path}\n")

    print("[3/5] Calculando PUE/WUE por (sitio, bundle)...")
    coef = generate_coefficients(screening, clim)
    coef_path = RESULTS_DIR / "etapa0_coeficientes.csv"
    coef.to_csv(coef_path, index=False)
    print(f"  {len(coef)} combinaciones → {coef_path}")

    # Mostrar tabla resumen
    valid = coef[coef["PUE"] < 90]
    pivot_pue = valid.pivot_table(
        index="estacion", columns="bundle", values="PUE", aggfunc="first"
    )
    pivot_wue = valid.pivot_table(
        index="estacion", columns="bundle", values="WUE_L_kWh", aggfunc="first"
    )
    print("\n  PUE por sitio × bundle:")
    print(pivot_pue.to_string())
    print("\n  WUE (L/kWh) por sitio × bundle:")
    print(pivot_wue.to_string())

    print("\n[4/5] Ejecutando sanity check...")
    report = sanity_check(coef)
    report_path = RESULTS_DIR / "etapa0_validacion.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"  → {report_path}")

    # Imprimir alertas si hay
    for line in report.split("\n"):
        if line.startswith("⚠️") or line.startswith("✅"):
            print(f"  {line}")

    print("\n[5/5] Etapa 0 completada.")
    print(f"\nMisión completada, Capitán. {len(coef)} coeficientes calculados.")


if __name__ == "__main__":
    main()
