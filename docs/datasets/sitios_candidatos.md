# Sitios Candidatos I (Estaciones Solares)

A partir de las 11 estaciones solares evaluadas, se ha definido el **conjunto de sitios candidatos I** para el modelo de localización.
El criterio de inclusión requiere al menos 12 meses de datos completos y válidos simultáneamente para todas las variables críticas: GHI, DNI, Temperatura, Humedad Relativa y Velocidad de Viento.

> **Nota sobre conteos de meses:** la columna "Meses Completos" cuenta los meses con observaciones válidas *simultáneamente en todas las variables críticas*. Por eso difiere de los conteos de `qc_report.md`, que cuentan el total de filas mensuales por estación sin exigir completitud simultánea (p. ej. CAMA: 29 meses completos vs. 94 filas mensuales).

| Estación | Nombre | Meses Completos | Estado |
|----------|--------|-----------------|--------|
| ADDA | Aeropuerto Copiapo | 16 | Seleccionada |
| ARMA | Armazones | 41 | Seleccionada |
| CAMA | Pampa Camarones | 29 | Seleccionada |
| CRUC | Crucero | 63 | Seleccionada |
| Crucero2 | Crucero II | 115 | **Excluida** (duplicado de ubicación) |
| IDEO | Inca de Oro | 120 | Seleccionada |
| PALM | Pozo Almonte | 46 | Seleccionada |
| PANG | Puerto Angamos | 87 | Seleccionada |
| SALV | Aerodromo Salvador | 31 | Seleccionada |
| SLAR | Salar (Chuquicamata) | 24 | Seleccionada |
| SPED | San Pedro de Atacama | 37 | Seleccionada |

## Exclusión de Crucero2

**Crucero2 (Crucero II) comparte ubicación exacta con CRUC (-22.27, -69.57).** Son dos estaciones de medición en el mismo punto geográfico; tratarlas como sitios candidatos independientes duplicaría el mismo sitio físico — y su CAI — en el modelo de localización (en la versión previa del conjunto, el 27 % de los escenarios de la grilla seleccionaba ambas simultáneamente, lo que invalidaba la interpretación de "P sitios").

Se conserva **CRUC** porque su GHI medio (~563 W/m²) es físicamente consistente con la zona, mientras que el de Crucero2 (~301 W/m²) sugiere problemas de sensor o sombreado, pese a tener más meses de registro. La exclusión está implementada en `methods/etapa0_precompute.py` (`EXCLUDED_STATIONS`) y `methods/cai_pipeline.py`.

**Conclusión:** Las 11 estaciones cumplen el umbral mínimo de 12 meses válidos, pero el conjunto I final consta de **10 sitios candidatos** tras deduplicar la ubicación de Crucero.
