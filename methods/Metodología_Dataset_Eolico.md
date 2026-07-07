# Metodología de Construcción del Dataset de Medición Eólica Mensual

Este documento detalla el procedimiento metodológico, los pasos de procesamiento y las fuentes de datos utilizadas para generar el dataset consolidado de mediciones de viento en estaciones del norte de Chile, en el marco del proyecto de investigación doctoral **Yakhchal DataCenter** (PhD UNAB).

---

## 1. Fuentes de Datos

El dataset se construyó a partir de las siguientes fuentes:

1.  **Catálogo de Estaciones de Medición Eólica:**
    - *Origen:* Archivo `Estaciones de Medición Eólica.xlsx`, compilado a partir del repositorio del [Explorador Eólico (Ministerio de Energía / Universidad de Chile)](https://eolico.minenergia.cl/).
    - *Contenido:* Metadatos de 43 estaciones de medición eólica terrestre en el norte de Chile: código, nombre, coordenadas geográficas y UTM, elevación, fechas de medición y enlace a datos crudos.
    - *Regiones cubiertas:* Arica y Parinacota, Tarapacá, Antofagasta, Atacama, Coquimbo.

2.  **Datos de Series Temporales de Viento:**
    - *Origen:* Servidor `walker.dgf.uchile.cl` — repositorio del Departamento de Geofísica de la Universidad de Chile.
    - *Formato:* Archivos CSV con resolución temporal de 10 minutos.
    - *URL base:* `http://walker.dgf.uchile.cl/Mediciones/datos/csv/{CODIGO}.csv`
    - *Variables disponibles (varían por estación):* Velocidad de viento a múltiples alturas, Dirección del viento, Temperatura, Humedad Relativa, Presión Atmosférica, Radiación Solar Global Horizontal (GHI), Voltaje de Batería.
    - *Rango temporal:* Diciembre 2002 a Enero 2022 (varía por estación).

---

## 2. Procedimiento de Consolidación (Paso a Paso)

El flujo de trabajo implementado consta de las siguientes fases:

### Paso 1: Extracción de Metadatos desde Excel

1.  Se lee el archivo `Estaciones de Medición Eólica.xlsx` con la librería `openpyxl`.
2.  Se itera sobre las 43 hojas del libro, cada una correspondiente a una estación.
3.  Para cada hoja se extraen los siguientes campos mediante parsing posicional:
    - Código de estación (ej: `chaca`, `a7`, `d08`)
    - Nombre descriptivo (ej: `Valle Chaca`)
    - Comuna y región
    - Fechas de inicio y fin de medición
    - Latitud y longitud geográficas (WGS84, grados decimales)
    - Elevación en metros
    - URL del archivo CSV de datos crudos
4.  Se genera un catálogo de estaciones en formato tabular (`data/station_catalog_wind.csv`).

### Paso 2: Descarga de CSVs de Series Temporales

1.  Para cada estación del catálogo, se construye la URL de descarga a partir del campo `link_datos`.
2.  Se implementa un mecanismo de caché local en el directorio `data/wind_stations/`:
    - Si el archivo CSV ya existe en el caché, se omite la descarga.
    - Si no existe, se descarga desde el servidor remoto mediante `urllib.request`.
3.  Los archivos descargados se almacenan con el nombre `{CODIGO}.csv`.
4.  El directorio `data/wind_stations/` se incluye en `.gitignore`.

### Paso 3: Normalización de Esquemas por Detección Automática de Columnas

Los CSVs de las distintas estaciones presentan esquemas altamente heterogéneos, con tres familias principales identificadas:

| Tipo | Variables típicas | Ejemplos |
|:---|:---|:---|
| A (solo viento) | Velocidad + Dirección de viento a 1-2 alturas | `chaca`, `los_morros`, `ollague` |
| B (completo) | Viento (10m/20m) + Temp + Humedad + Presión + GHI | `a7`, `b41`, `d02`, `d08` |
| C (viento + temp) | Viento + Temperatura | `llano_chocolate`, `punta_choro` |

Se implementó un mapeo automático basado en coincidencia de substrings con las siguientes particularidades:

#### 3.1. Velocidad de Viento: Selección por Altura Óptima

Dado que las estaciones miden viento a distintas alturas (0 m, 10 m, 20 m, 30 m, 40 m, 50 m), se implementó un algoritmo de selección:

1.  Se detectan **todas** las columnas que coinciden con el patrón `velocidad.*viento.*\[mean.*m/s`.
2.  Para cada coincidencia, se extrae la altura del anemómetro mediante regex (`en X.X metros`).
3.  Se selecciona la columna cuya altura esté más cercana a **20 metros** (altura de referencia para torres de medición eólica estándar).
4.  Si ninguna columna tiene altura explícita, se toma la primera coincidencia disponible.

#### 3.2. Resto de Variables

| Variable destino | Patrón de búsqueda (case-insensitive) | Nota |
|:---|:---|:---|
| `wind_direction` | `dirección.*viento.*\[mean.*grados` | Primer match |
| `temperatura` | `temperatura.*\[mean.*[cC]` | Primer match |
| `humedad` | `humedad` | Primer match |
| `presion` | `presi[óo]n\s*atmosf[ée]rica` | Primer match |
| `ghi` | `global\s+horizontal` | Primer match |

1.  Se lee el header del CSV y se detecta automáticamente el encoding (UTF-8 con fallback a latin-1).
2.  Se parsea la columna `Fecha Hora` como índice datetime.
3.  Se aplican los mapeos por substring para identificar las columnas de interés.
4.  Las columnas no mapeadas se ignoran.
5.  Se convierten todas las variables a tipo numérico (`float`), forzando a `NaN` los valores no convertibles.

### Paso 4: Remuestreo a Medias Mensuales

1.  Para cada estación, se agrupan los datos por mes calendario utilizando `pandas.DataFrame.resample('ME')`.
2.  Se calcula la **media aritmética** de cada variable para cada mes.
3.  Se preserva el índice temporal como `YYYY-MM` (primer día de cada mes).
4.  Los meses sin datos generan registros `NaN` y se excluyen del dataset final mediante `dropna(how='all')`.

### Paso 5: Filtro de Calidad de Datos (Valores Centinela)

Se detectaron valores físicamente imposibles en algunas estaciones, atribuibles a fallas de sensor o calibración, particularmente en equipos antiguos (2003-2005):

| Variable | Umbral de filtro | Justificación |
|:---|:---|:---|
| Temperatura | < -30 °C | Valores centinela detectados: -30.05 °C (sensor caído en a7, b42, d05a), -60 a -123.5 °C (llano_chocolate, punta_choro, san_marcos). |
| GHI | > 1500 W/m² | La constante solar es ~1361 W/m². Valores superiores a 1500 W/m² en superficie son físicamente imposibles. Detectado en cupo (máx 12,259) y chaca. |

1.  Los valores que superan estos umbrales se reemplazan por `NaN` a nivel de registro mensual.
2.  Esto no elimina meses completos (las demás variables del mes se conservan), solo invalida la variable afectada.
3.  Los umbrales son conservadores: -30 °C es inferior a cualquier temperatura registrada en el norte de Chile, y 1500 W/m² supera la irradiancia solar extraterrestre.

> [!NOTE]
> La dirección del viento se promedia aritméticamente. Para análisis que requieran dirección circular (vector mean), se recomienda recalcular a partir de los datos crudos en `data/wind_stations/`.

### Paso 6: Consolidación en Dataset Único

1.  Las medias mensuales de cada estación se concatenan en un único `DataFrame`.
2.  Se incorporan las columnas de metadatos: `estacion`, `nombre`, `region`, `longitud`, `latitud`, `elevacion_m`, `fuente_datos`.
3.  Se reordenan las columnas al formato canónico especificado.
4.  El dataset resultante se exporta a `data/dataset_eolico_mensual.csv`.
5.  Se genera un archivo de metadatos en formato Markdown (`data/dataset_eolico_mensual.md`).

---

## 3. Estadísticas del Dataset

| Métrica | Valor |
|:---|---|
| Número de estaciones | 43 |
| Resolución temporal original | 10 minutos |
| Resolución del dataset final | Mensual (media aritmética) |
| Rango temporal total | Diciembre 2002 – Enero 2022 |
| Regiones cubiertas | Arica y Parinacota, Tarapacá, Antofagasta, Atacama, Coquimbo |
| Variables detectadas | Hasta 6 (viento velocidad, viento dirección, temperatura, humedad, presión, GHI) |

---

## 4. Estructura del Dataset Final (`dataset_eolico_mensual.csv`)

| Columna | Tipo | Descripción |
|:---|:---|:---|
| `estacion` | String | Código de la estación (ej: `a7`). |
| `nombre` | String | Nombre descriptivo de la estación. |
| `region` | String | Región administrativa de Chile. |
| `longitud` | Float | Longitud geográfica en grados decimales (Datum WGS84). |
| `latitud` | Float | Latitud geográfica en grados decimales (Datum WGS84). |
| `elevacion_m` | Float | Elevación en metros sobre el nivel del mar. |
| `fecha` | Date | Año-Mes de la medición (formato `YYYY-MM-DD`, primer día del mes). |
| `wind_speed_mean_ms` | Float | Velocidad de viento media mensual a la altura más cercana a 20 m [m/s]. |
| `wind_direction_mean_deg` | Float | Dirección del viento media mensual [grados] (media aritmética, no circular). |
| `temperatura_mean_c` | Float | Temperatura ambiente media mensual [°C] (puede ser NaN). |
| `humedad_mean_pct` | Float | Humedad Relativa media mensual [%] (puede ser NaN). |
| `presion_mean_hpa` | Float | Presión atmosférica media mensual [hPa] (puede ser NaN). |
| `ghi_mean_wm2` | Float | Radiación Solar Global Horizontal media mensual [W/m²] (puede ser NaN). |
| `fuente_datos` | String | URL del archivo CSV de datos crudos original. |

---

## 5. Reproducibilidad

### Requisitos

- Python >= 3.14
- Dependencias: `pandas`, `openpyxl`, `numpy` (ya incluidas en `pyproject.toml`)
- Conexión a internet para la descarga inicial de CSVs

### Ejecución

```bash
uv run methods/wind_stations_pipeline.py
```

El pipeline es **idempotente**: si los CSVs ya fueron descargados, solo re-ejecuta el procesamiento. Para forzar re-descarga, eliminar `data/wind_stations/`.

### Archivos generados

| Archivo | Descripción |
|:---|:---|
| `data/station_catalog_wind.csv` | Catálogo de 43 estaciones |
| `data/dataset_eolico_mensual.csv` | Dataset consolidado de medias mensuales |
| `data/dataset_eolico_mensual.md` | Reporte de cobertura y estadísticas |
| `data/wind_stations/*.csv` | Caché local de datos crudos |

---

## 6. Limitaciones Conocidas

1.  **Heterogeneidad extrema de esquemas:** Las 43 estaciones presentan 3 familias de columnas distintas. Solo ~20 estaciones (tipo B) tienen el conjunto completo de variables meteorológicas (viento + temperatura + humedad + presión + GHI). Las estaciones tipo A (~15) miden exclusivamente viento.
2.  **Altura de anemómetro variable:** Se seleccionó la altura más cercana a 20 m, pero algunas estaciones solo miden a 10 m o a 0 m, lo que introduce heterogeneidad en la comparación entre estaciones.
3.  **Media aritmética de dirección:** La dirección del viento es una variable circular (0° = 360°). La media aritmética simple no es válida para direcciones cercanas al norte (ej: promediar 350° y 10° da 180° en vez de 0°). Se recomienda usar media vectorial circular para análisis que lo requieran.
4.  **Datos faltantes:** Series con gaps temporales. Los meses sin ningún dato se excluyen del dataset final.
5.  **Valores centinela filtrados:** Se aplicaron filtros de calidad física (temperatura < -30 °C, GHI > 1500 W/m²) que eliminan datos espurios de sensores defectuosos, particularmente en estaciones antiguas (2003-2005). Las variables de viento no se vieron afectadas. Los datos crudos sin filtrar permanecen disponibles en `data/wind_stations/`.
