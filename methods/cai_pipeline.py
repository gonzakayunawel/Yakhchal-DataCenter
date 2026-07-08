"""Pipeline: Curtailment Availability Index (CAI) para sitios candidatos.

Calcula el Índice de Disponibilidad de Curtailment (CAI) para cada estación
candidata del catálogo solar, ponderando el curtailment acumulado (MWh) de
cada planta renovable del SEN por su proximidad geodésica al sitio.

    CAI_i = Σ_j  C_j · exp(−d_ij / d0)

donde C_j es el curtailment acumulado de la planta j, d_ij la distancia
Haversine entre el sitio i y la planta j, y d0 la escala de decaimiento (km).

Se evalúa para d0 ∈ {20, 50, 100} km y se desagrega por tipo de generación
(Solar, Eólica).
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

CURTAILMENT_PATH = DATA_DIR / "curtailment_acumulado.csv"
STATIONS_PATH = DATA_DIR / "station_catalog.csv"
OUTPUT_PATH = RESULTS_DIR / "cai_por_sitio.csv"

# Escalas de decaimiento (km) para el análisis de sensibilidad
D0_VALUES = [20, 50, 100]

# Tipos de generación para desagregar
TIPOS = {"Solar": "solar", "Eólica": "eolica"}


# ---------------------------------------------------------------------------
# Haversine
# ---------------------------------------------------------------------------
def haversine_km(
    lat1: np.ndarray,
    lon1: np.ndarray,
    lat2: np.ndarray,
    lon2: np.ndarray,
) -> np.ndarray:
    """Distancia geodésica (km) entre dos puntos usando la fórmula de Haversine.

    Acepta escalares o arrays de NumPy (broadcasting compatible).
    """
    R = 6371.0  # radio medio terrestre, km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    )
    return R * 2 * np.arcsin(np.sqrt(a))


# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
def load_curtailment(path: Path) -> pd.DataFrame:
    """Carga el dataset de curtailment y filtra plantas con coordenadas válidas."""
    df = pd.read_csv(path)
    n_total = len(df)
    df = df.dropna(subset=["latitud", "longitud"]).copy()
    n_valid = len(df)
    curtailment_total_gwh = df["curtailment (MWh)"].sum() / 1_000

    print(f"[DATOS] Curtailment: {n_total} plantas, {n_valid} con coordenadas")
    print(f"[DATOS] Curtailment total (con coords): {curtailment_total_gwh:,.1f} GWh")
    return df


def load_stations(path: Path) -> pd.DataFrame:
    """Carga el catálogo de estaciones solares candidatas.

    Excluye Crucero2: comparte ubicación con CRUC (-22.27, -69.57) y
    duplicaría el mismo sitio (y su CAI) en el modelo de localización
    (misma exclusión que en etapa0_precompute.py).
    """
    df = pd.read_csv(path)
    df = df[df["codigo"] != "Crucero2"]
    print(f"[DATOS] Estaciones candidatas: {len(df)}")
    return df


# ---------------------------------------------------------------------------
# Cálculo del CAI
# ---------------------------------------------------------------------------
def compute_cai(
    stations: pd.DataFrame,
    plants: pd.DataFrame,
    d0_km: float,
) -> np.ndarray:
    """Calcula el CAI para cada sitio dado un subconjunto de plantas y d0.

    Usa broadcasting matricial para eficiencia:
      - stations: (N, ) con columnas latitud, longitud
      - plants:   (M, ) con columnas latitud, longitud, curtailment (MWh)
      - retorna:  array (N,) con el CAI de cada sitio
    """
    # Coordenadas de sitios (N,1) y plantas (1,M)
    lat_s = stations["latitud"].values[:, np.newaxis]
    lon_s = stations["longitud"].values[:, np.newaxis]
    lat_p = plants["latitud"].values[np.newaxis, :]
    lon_p = plants["longitud"].values[np.newaxis, :]
    curtailment = plants["curtailment (MWh)"].values[np.newaxis, :]  # (1, M)

    # Matriz de distancias (N, M) en km
    dist = haversine_km(lat_s, lon_s, lat_p, lon_p)

    # Kernel de decaimiento exponencial y suma ponderada
    weights = np.exp(-dist / d0_km)  # (N, M)
    cai = np.sum(curtailment * weights, axis=1)  # (N,)
    return cai


def build_cai_table(
    stations: pd.DataFrame,
    curtailment: pd.DataFrame,
) -> pd.DataFrame:
    """Construye la tabla completa de CAI para todos los d0 y tipos."""
    result = stations[["codigo", "nombre", "latitud", "longitud"]].copy()
    result = result.rename(columns={"codigo": "estacion"})

    # Subconjuntos por tipo de generación
    subsets = {"total": curtailment}
    for tipo_es, tipo_en in TIPOS.items():
        subsets[tipo_en] = curtailment[curtailment["tipo"] == tipo_es]

    for label, plants_subset in subsets.items():
        for d0 in D0_VALUES:
            col = f"CAI_{label}_d{d0}"
            result[col] = compute_cai(stations, plants_subset, d0)
            # Convertir de MWh a GWh para legibilidad
            result[col] = result[col] / 1_000

    return result


# ---------------------------------------------------------------------------
# Reporte por consola
# ---------------------------------------------------------------------------
def print_ranking(cai_table: pd.DataFrame) -> None:
    """Imprime el ranking de sitios por CAI total para cada d0."""
    print("\n" + "=" * 72)
    print("  RANKING DE SITIOS POR CAI (Curtailment Availability Index)")
    print("  Unidades: GWh-equivalente ponderado por proximidad")
    print("=" * 72)

    for d0 in D0_VALUES:
        col = f"CAI_total_d{d0}"
        ranked = (
            cai_table[["estacion", "nombre", col]]
            .sort_values(col, ascending=False)
            .reset_index(drop=True)
        )
        ranked.index += 1  # ranking desde 1

        print(f"\n{'─' * 72}")
        print(f"  d0 = {d0} km")
        print(f"{'─' * 72}")
        print(ranked.to_string())

    # Resumen compacto: top-3 para cada d0
    print(f"\n{'─' * 72}")
    print("  RESUMEN: Top-3 sitios por d0")
    print(f"{'─' * 72}")
    for d0 in D0_VALUES:
        col = f"CAI_total_d{d0}"
        top3 = cai_table.nlargest(3, col)[["estacion", col]]
        names = ", ".join(
            f"{row['estacion']} ({row[col]:.1f})" for _, row in top3.iterrows()
        )
        print(f"  d0={d0:>3d} km → {names}")

    # Desagregación solar vs eólica para d0=50 km
    print(f"\n{'─' * 72}")
    print("  DESAGREGACIÓN SOLAR / EÓLICA (d0 = 50 km)")
    print(f"{'─' * 72}")
    cols_desg = ["estacion", "nombre", "CAI_solar_d50", "CAI_eolica_d50"]
    desg = cai_table[cols_desg].sort_values("CAI_solar_d50", ascending=False)
    desg = desg.reset_index(drop=True)
    desg.index += 1
    print(desg.to_string())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Punto de entrada del pipeline CAI."""
    print("=" * 72)
    print("  Yakhchal DataCenter — Pipeline CAI")
    print("  Capitán Cayunao, calculando índice de disponibilidad de curtailment")
    print("=" * 72)

    # 1. Cargar datos
    curtailment = load_curtailment(CURTAILMENT_PATH)
    stations = load_stations(STATIONS_PATH)

    # 2. Calcular tabla CAI
    cai_table = build_cai_table(stations, curtailment)

    # 3. Guardar resultados
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cai_table.to_csv(OUTPUT_PATH, index=False)
    print(f"\n[OUTPUT] Resultados guardados → {OUTPUT_PATH}")

    # 4. Imprimir rankings
    print_ranking(cai_table)

    print("\n" + "=" * 72)
    print("  Pipeline CAI completado exitosamente, Capitán Cayunao.")
    print("=" * 72)


if __name__ == "__main__":
    main()
