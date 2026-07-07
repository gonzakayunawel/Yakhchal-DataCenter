# Metodología de Construcción del Dataset de Radiación Solar Mensual

Este documento detalla el procedimiento metodológico, los pasos de procesamiento y las fuentes de datos utilizadas para generar el dataset consolidado de mediciones de radiación solar en estaciones del norte de Chile, en el marco del proyecto de investigación doctoral **Yakhchal DataCenter** (PhD UNAB).

---

## 1. Fuentes de Datos

El dataset se construyó a partir de las siguientes fuentes:

1.  **Catálogo de Estaciones de Medición Solar:**
    - *Origen:* Archivo `Estaciones de Medición Solar.xlsx`, compilado a partir del repositorio del [Explorador Solar (Ministerio de Energía / Universidad de Chile)](https://solar.minenergia.cl/).
    - *Contenido:* Metadatos de 11 estaciones de medición solar terrestre en el norte de Chile: código, nombre, coordenadas geográficas y UTM, elevación, fechas de medición y enlace a datos crudos.
    - *Regiones cubiertas:* Arica y Parinacota, Tarapacá, Antofagasta, Atacama.

2.  **Datos de Series Temporales de Radiación Solar:**
    - *Origen:* Servidor `walker.dgf.uchile.cl` — repositorio del Departamento de Geofísica de la Universidad de Chile.
    - *Formato:* Archivos CSV con resolución temporal de 10 minutos.
    - *URL base:* `http://walker.dgf.uchile.cl/Mediciones/datos/csv/{CODIGO}.csv`
    - *Variables disponibles:* Radiación Solar Global Horizontal (GHI), Radiación Solar Global en Seguimiento (GTI), Radiación Solar Difusa, Radiación Directa Normal (DNI), Temperatura, Humedad Relativa, Velocidad de Viento, Voltaje de Batería.
    - *Rango temporal:* Agosto 2008 a Marzo 2022 (varía por estación).

---

## 2. Procedimiento de Consolidación (Paso a Paso)

El flujo de trabajo implementado consta de las siguientes fases:

### Paso 1: Extracción de Metadatos desde Excel

1.  Se lee el archivo `Estaciones de Medición Solar.xlsx` con la librería `openpyxl`.
2.  Se itera sobre las 11 hojas del libro, cada una correspondiente a una estación.
3.  Para cada hoja se extraen los siguientes campos mediante parsing posicional:
    - Código de estación (ej: `PALM`)
    - Nombre descriptivo (ej: `Pozo Almonte`)
    - Comuna y región
    - Fechas de inicio y fin de medición
    - Latitud y longitud geográficas (WGS84, grados decimales)
    - Elevación en metros
    - URL del archivo CSV de datos crudos
4.  Se genera un catálogo de estaciones en formato tabular (`data/station_catalog.csv`).

### Paso 2: Descarga de CSVs de Series Temporales

1.  Para cada estación del catálogo, se construye la URL de descarga a partir del campo `link_datos`.
2.  Se implementa un mecanismo de caché local en el directorio `data/solar_stations/`:
    - Si el archivo CSV ya existe en el caché, se omite la descarga.
    - Si no existe, se descarga desde el servidor remoto mediante `urllib.request`.
3.  Los archivos descargados se almacenan con el nombre `{CODIGO}.csv` para referencia directa.
4.  El directorio `data/solar_stations/` se incluye en `.gitignore` para evitar commits de archivos binarios de gran tamaño.

### Paso 3: Normalización de Esquemas por Detección Automática de Columnas

Dado que los CSVs de distintas estaciones presentan esquemas heterogéneos (columnas en distinto orden, nombres variables, presencia/ausencia de ciertas mediciones), se implementó un mapeo automático basado en coincidencia de substrings:

| Variable destino | Patrón de búsqueda (case-insensitive) |
|:---|:---|
| `ghi` | `global horizontal` |
| `dni` | `directa normal` |
| `temperatura` | `temperatura` |
| `humedad` | `humedad` |
| `viento` | `viento.*mean` (excluyendo `min` y `max`) |

1.  Se lee el header del CSV y se detecta automáticamente el encoding (UTF-8 con fallback a latin-1).
2.  Se parsea la columna `Fecha Hora` como índice datetime.
3.  Se aplica el mapeo por substring para identificar las columnas de interés, independientemente de su posición o nombre exacto.
4.  Las columnas no mapeadas se ignoran.
5.  Se convierten todas las variables a tipo numérico (`float`), forzando a `NaN` los valores no convertibles.

### Paso 4: Remuestreo a Medias Mensuales

1.  Para cada estación, se agrupan los datos por mes calendario utilizando `pandas.DataFrame.resample('ME')`.
2.  Se calcula la **media aritmética** de cada variable para cada mes.
3.  Se preserva el índice temporal como `YYYY-MM` (primer día de cada mes).
4.  Los meses sin datos (estación fuera de operación) generan registros `NaN` y se excluyen del dataset final mediante `dropna()`.

### Paso 5: Consolidación en Dataset Único

1.  Las medias mensuales de cada estación se concatenan en un único `DataFrame`.
2.  Se incorporan las columnas de metadatos: `estacion`, `nombre`, `region`, `longitud`, `latitud`, `elevacion_m`, `fuente_datos`.
3.  Se reordenan las columnas al formato canónico especificado.
4.  El dataset resultante se exporta a `data/dataset_solar_mensual.csv`.
5.  Simultáneamente se genera un archivo de metadatos en formato Markdown (`data/dataset_solar_mensual.md`) con estadísticas descriptivas y notas de cobertura temporal.

---

## 3. Estadísticas del Dataset

| Métrica | Valor |
|:---|---|
| Número de estaciones | 11 |
| Resolución temporal original | 10 minutos |
| Resolución del dataset final | Mensual (media aritmética) |
| Rango temporal total | Agosto 2008 – Marzo 2022 |
| Regiones cubiertas | Arica y Parinacota, Tarapacá, Antofagasta, Atacama |
| Variables consolidadas | 5 (GHI, DNI, temperatura, humedad, viento) |

> [!NOTE]
> La variable DNI no está disponible en todas las estaciones. En los casos donde la estación no mide radiación directa normal, la columna `dni_mean_wm2` queda con valores `NaN` y se excluye de las filas correspondientes.

---

## 4. Estructura del Dataset Final (`dataset_solar_mensual.csv`)

| Columna | Tipo | Descripción |
|:---|:---|:---|
| `estacion` | String | Código de la estación (ej: `PALM`). |
| `nombre` | String | Nombre descriptivo de la estación (ej: `Pozo Almonte`). |
| `region` | String | Región administrativa de Chile. |
| `longitud` | Float | Longitud geográfica en grados decimales (Datum WGS84). |
| `latitud` | Float | Latitud geográfica en grados decimales (Datum WGS84). |
| `elevacion_m` | Float | Elevación en metros sobre el nivel del mar. |
| `fecha` | Date | Año-Mes de la medición (formato `YYYY-MM-DD`, primer día del mes). |
| `ghi_mean_wm2` | Float | Radiación Solar Global Horizontal media mensual [W/m²]. |
| `dni_mean_wm2` | Float | Radiación Directa Normal media mensual [W/m²] (puede ser NaN si la estación no mide DNI). |
| `temperatura_mean_c` | Float | Temperatura ambiente media mensual [°C]. |
| `humedad_mean_pct` | Float | Humedad Relativa media mensual [%]. |
| `viento_mean_ms` | Float | Velocidad de viento media mensual [m/s]. |
| `fuente_datos` | String | URL del archivo CSV de datos crudos original. |

---

## 5. Reproducibilidad

### Requisitos

- Python >= 3.14
- Dependencias: `pandas`, `openpyxl`, `numpy` (ya incluidas en `pyproject.toml` del proyecto)
- Conexión a internet para la descarga inicial de CSVs

### Ejecución

```bash
uv run methods/solar_stations_pipeline.py
```

El pipeline es **idempotente**: si los CSVs ya fueron descargados, solo re-ejecuta el procesamiento sin volver a descargar. Si se requiere forzar la re-descarga, eliminar el directorio `data/solar_stations/` antes de ejecutar.

### Archivos generados

| Archivo | Descripción |
|:---|:---|
| `data/station_catalog.csv` | Catálogo de estaciones extraído del Excel |
| `data/dataset_solar_mensual.csv` | Dataset consolidado de medias mensuales |
| `data/dataset_solar_mensual.md` | Reporte de estadísticas y cobertura temporal |
| `data/solar_stations/*.csv` | Caché local de datos crudos descargados |

---

## 6. Limitaciones Conocidas

1.  **Heterogeneidad de columnas:** Las estaciones miden conjuntos de variables ligeramente distintos. La columna `dni_mean_wm2` solo está disponible para ~6 de las 11 estaciones.
2.  **Altura de anemómetro:** La velocidad de viento se mide a distintas alturas según la estación (2.0 m, 2.5 m, 4.0 m, 5.0 m, 6.0 m, 12.0 m). El script selecciona la primera columna de viento que hace match con el patrón `mean` (excluyendo `min`/`max`), lo que puede introducir sesgo al comparar vientos entre estaciones con distintas alturas de medición.
3.  **Datos faltantes:** Los CSVs contienen registros con valores negativos (ej: `-3.0` para GHI nocturna) que no fueron filtrados. Para análisis que requieran solo irradiancia diurna, se recomienda filtrar GHI > 0.
4.  **Cobertura temporal:** El rango de fechas varía significativamente entre estaciones (desde 2 años para SLAR hasta 13 años para PALM).
