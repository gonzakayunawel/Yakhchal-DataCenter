# Metodología de Construcción del Dataset de Curtailment Geoespacial

Este documento detalla el procedimiento metodológico, los pasos de procesamiento y las fuentes de datos oficiales utilizadas para generar el dataset consolidado de reducciones de energía (*curtailment*) y coordenadas geográficas de centrales solares y eólicas en el Sistema Eléctrico Nacional (SEN) de Chile, en el marco del proyecto de investigación doctoral **Yakhchal DataCenter** (PhD UNAB).

---

## 1. Fuentes de Datos Oficiales

El dataset se construyó a partir de la integración de las siguientes plataformas y fuentes de datos:

1.  **Datos de Curtailment (Reducciones de Energía):**
    *   *Origen:* [Coordinador Eléctrico Nacional (CEN)](https://www.coordinador.cl/) de Chile.
    *   *Enlace de descarga:* [Documentos de Reducciones de Generación Renovable](https://www.coordinador.cl/operacion/documentos/reducciones-de-generacion-renovable/)
    *   *Rango:* Enero de 2022 a Abril de 2026.
    *   *Unidad:* Megavatios-hora (MWh) acumulados de energía recortada.

2.  **Datos de Ubicación y Geografía de Centrales:**
    *   *Origen:* [Infraestructura de Datos Geoespaciales (IDE Energía)](https://ide-energia.minenergia.cl/) - Ministerio de Energía de Chile.
    *   *Enlace del visor cartográfico:* [Visualizador IDE Energía](https://ide-energia.minenergia.cl/portal/apps/webappviewer/index.html?id=5c526a138b1449458e0667b2235d2b19)
    *   *Formato:* Capas vectoriales ESRI Shapefile (`Eólicas.shp` y `Solares.shp`).
    *   *Datum nativo:* `GCS_SIRGAS-Chile` (EPSG:9184).

---

## 2. Procedimiento de Consolidación (Paso a Paso)

El flujo de trabajo implementado para la estructuración y cruce de datos consta de las siguientes fases:

### Paso 1: Descarga e Integración de Curtailment (2022 - Abril 2026)
1.  Se recopilaron los reportes históricos y mensuales de reducciones del CEN.
2.  Se procesaron las hojas de cálculo `Acumulado-Anual-Solar` y `Acumulado-Anual-Eólico` de los libros Excel.
3.  Debido a que el formato de origen apila verticalmente bloques mensuales (cada uno con cabeceras y totales propios), se utilizó un script de barrido automatizado para:
    *   Detectar el cambio de mes mediante celdas con marcas de tiempo datetime.
    *   Identificar la columna final de suma acumulada mensual (`Total`).
    *   Extraer de manera iterativa todas las filas correspondientes a centrales únicas, ignorando registros vacíos y filas de totales globales del sistema.
4.  Se agregaron los datos de todas las series temporales para obtener un total acumulado en **MWh** para cada planta.

### Paso 2: Procesamiento Cartográfico de Centrales
1.  Se cargaron las capas vectoriales Shapefile correspondientes a centrales solares y eólicas.
2.  Se aplicó una transformación del Sistema de Referencia Geográfico (CRS) nativo `SIRGAS-Chile` a coordenadas **WGS84** (EPSG:4326) para obtener latitud y longitud métricas en grados decimales globales.

### Paso 3: Filtro Territorial y Algoritmo de Matching
Dado que el CEN nombra a las plantas según su código operativo (ej: `PFV-POZOALMONTE-2`) y la CNE las registra según su nombre formal (ej: `POZO ALMONTE SOLAR II`), se desarrolló un pipeline de emparejamiento:

1.  **Normalización de Nombres:**
    *   Conversión de nombres a mayúsculas y remoción de prefijos (`PE-`, `PFV-`, `PMGD-`).
    *   Estandarización de números romanos a arábigos finales (`II` -> `2`, `III` -> `3`, etc.).
    *   Remoción de términos de ruido (`PARQUE`, `EOLICO`, `EOLICA`, `PFV`, `PMGD`, `SOLAR`, `CENTRAL`, `FV`, `PE`).
    *   Eliminación de espacios en blanco y caracteres no alfanuméricos.
2.  **Lógica de Búsqueda:**
    *   *Fase 1:* Coincidencia exacta de las cadenas normalizadas.
    *   *Fase 2:* Búsqueda por contención o subcadena (*substring matching*) para resolver nombres complejos (ej: vincular `PFV-VALLEDELSOL` con `VALLE DEL SOL (MODIFICACION)`).
3.  **Filtro por Zona de Interés:**
    *   Se priorizó el filtrado territorial en las regiones de interés del norte chileno: **Coquimbo, Atacama, Antofagasta, Tarapacá y Arica y Parinacota**.

---

## 3. Estadísticas del Emparejamiento y Cobertura

*   **Total de centrales en Excel:** 133 centrales (100%).
*   **Centrales georreferenciadas con éxito:** 101 centrales (76% del total).
*   **Centrales sin coordenadas (Unmatched):** 32 centrales (24% del total).

> [!IMPORTANT]
> **Garantía de Cobertura Territorial:**
> Las 32 centrales sin coordenadas corresponden en su totalidad a proyectos eólicos de las regiones del **centro-sur y sur de Chile** (Biobío, La Araucanía y Los Lagos; ej. `PE-NEGRETE`, `PE-LOSOLMOS`), fuera de los shapefiles descargados. Por consiguiente, **la cobertura para las regiones de Coquimbo, Atacama, Antofagasta, Tarapacá y Arica y Parinacota es del 100%**; todos los registros del norte fueron geolocalizados y emparejados.

---

## 4. Estructura del Dataset Final (`curtailment_acumulado.csv`)

El dataset consolidado se guardó en `data/curtailment_acumulado.csv` con las siguientes columnas:

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `planta` | String | Identificador/código de la planta en el CEN (ej: `PFV-POZOALMONTE-2`). |
| `tipo` | String | Tecnología de generación (`Solar` o `Eólica`). |
| `longitud` | Float | Longitud geográfica en grados decimales (Datum WGS84). |
| `latitud` | Float | Latitud geográfica en grados decimales (Datum WGS84). |
| `curtailment (MWh)` | Float | Energía acumulada total recortada (2022-2026) en Megavatios-hora (MWh). |