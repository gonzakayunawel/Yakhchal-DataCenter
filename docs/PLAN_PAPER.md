# Plan de Trabajo — Paper Yakhchal DataCenter

> **Objetivo:** Paper académico (ejercicio de curso, formato IEEE vía Quarto) que formula y resuelve un MILP de dos etapas para localización y selección tecnológica de datacenters en el desierto chileno, integrando clima (PUE/WUE por tecnología), sostenibilidad energética (curtailment/CAI) y costo.
>
> **Decisiones ya tomadas:**
> - Brecha 4 (ECTD-2022 / capacidad real de red): **NO** se descargan datos reales. `d0` se trata como **parámetro de sensibilidad justificado** (valores 20/50/100 km), declarándolo explícitamente como limitación.
> - Resolución temporal: **mensual** (Opción 2 de `Idea_discusion.md`), suficiente para precomputar coeficientes de Etapa 0.
> - Modelo formal: el MILP consolidado de `docs/Idea_discusion.md` (secciones 1–6) es la especificación de referencia.
>
> **Cómo usar este documento:** marcar `[x]` cada tarea completada al cierre de cada sesión. Cada fase tiene criterios de verificación ("Done cuando…") para validar antes de avanzar.

---

## Estado global

| Fase | Descripción | Estado |
|------|-------------|--------|
| 0 | Ordenamiento del repositorio | ✅ Hecho |
| 1 | QC y limpieza de datasets | ✅ Hecho |
| 2 | Etapa 0 — Precómputo de coeficientes | ✅ Hecho |
| 3 | Índice CAI (curtailment) | ✅ Hecho |
| 4 | Etapa 1 — Modelo MILP | ✅ Hecho |
| 5 | Experimentos y análisis de sensibilidad | ✅ Hecho |
| 6 | Figuras y tablas | ✅ Hecho |
| 7 | Verificación de bibliografía | ✅ Hecho |
| 8 | Redacción del paper (.qmd) | ✅ Hecho |
| 9 | Render final y revisión de cierre | ⬜ Pendiente |

---

## Fase 0 — Ordenamiento del repositorio

Preparar el terreno para que las fases siguientes no arrastren desorden.

- [x] 0.1 Commitear los archivos sin trackear pendientes (`docs/feasibility/*.md`, CSVs demo del ECTD) con mensaje que deje claro que los docs de feasibility son **material de investigación sin verificar** (salidas de Perplexity).
- [x] 0.2 Mover o eliminar residuos de `data/`: `output.zip`, `output (1).zip`, `output (2).zip`, `snowflake.log` (raíz). Si no se usan, borrarlos y actualizar `.gitignore`.
- [x] 0.3 Marcar `datos_instalaciones_ectd2022_demo.csv` y `beta_por_coordenada_ectd2022.csv` como **datos ilustrativos no reales** (renombrar con sufijo `_demo`/`_ilustrativo` o documentarlo en `docs/datasets/`). Contienen filas corruptas (caracteres cirílicos, coordenadas incoherentes) — no deben usarse como datos de entrada del modelo.
- [x] 0.4 Crear estructura de directorios para resultados: `results/` (CSVs de salida de Etapa 0/CAI/MILP) y `figures/` (PNG/PDF para el paper). Agregar a `.gitignore` lo que corresponda (o versionar los CSVs finales pequeños).

**Done cuando:** `git status` limpio, sin archivos ambiguos, y estructura `results/` + `figures/` creada.

---

## Fase 1 — QC y limpieza de datasets

Los coeficientes de Etapa 0 dependen de climatologías confiables. Problemas detectados en la auditoría: GHI mínimo de −5 W/m² (valores nocturnos sin filtrar), viento mensual máximo de 26 m/s (outlier improbable para media mensual), columnas vacías de humedad/GHI en algunas estaciones eólicas (p.ej. ARMAZ).

- [x] 1.1 Agregar filtros de QC a `methods/solar_stations_pipeline.py`:
  - GHI/DNI: descartar valores < 0; recorte de outliers físicos (GHI > 1500 W/m² instantáneo).
  - Promedios mensuales de GHI/DNI: decidir si se calculan sobre 24 h o solo horas diurnas — **documentar la decisión** (afecta comparación con Explorador Solar).
  - Viento: descartar valores < 0 y > 40 m/s (instantáneo); revisar el origen del outlier de 26 m/s en la media mensual.
  - Temperatura/HR: rangos físicos (−15 a 45 °C; 0–100 %).
  - Requisito de completitud: descartar meses con < 60 % de datos horarios válidos (umbral a documentar).
- [x] 1.2 Aplicar los mismos filtros a `methods/wind_stations_pipeline.py`. Documentar qué estaciones quedan sin HR o presión (necesarias para T_wb y PW).
- [x] 1.3 Regenerar `data/dataset_solar_mensual.csv` y `data/dataset_eolico_mensual.csv`; regenerar los reportes de metadatos en `docs/datasets/`.
- [x] 1.4 Verificación: script o notebook rápido que confirme (a) no hay GHI/DNI negativos, (b) medias mensuales de viento < 15 m/s o justificadas, (c) conteo de meses por estación ≥ 12 para las estaciones que serán sitios candidatos. Guardar resumen en `docs/datasets/qc_report.md`.
- [x] 1.5 Definir y congelar el **conjunto de sitios candidatos I**: partir de las 11 estaciones solares; excluir las que tengan < 12 meses de cobertura o variables faltantes críticas. Registrar el conjunto final (con justificación de exclusiones) en `docs/datasets/sitios_candidatos.md`.

**Done cuando:** datasets regenerados pasan las verificaciones de 1.4 y el conjunto I está congelado y documentado.

---

## Fase 2 — Etapa 0: Precómputo de coeficientes por sitio × tecnología

Script nuevo: `methods/etapa0_precompute.py`. Entrada: datasets mensuales limpios. Salida: `results/etapa0_coeficientes.csv` con una fila por (sitio i, bundle h).

Bundles: `H_RAD` (radiativo, Aili), `H_ECO` (economizador/IEC, Silva-Llanca + Yang), `H_HYB` (híbrido), `H_CONV` (chiller convencional, Lei & Masanet Casos 5/8).

- [x] 2.1 **Climatología por sitio:** promedios mensuales multianuales (12 valores por variable por estación) de T_db, HR, GHI, DNI, viento, presión (presión: derivarla de la elevación vía atmósfera estándar si la estación no la mide — documentar).
- [x] 2.2 **Variables derivadas por sitio-mes:**
  - T_wb con la fórmula de Stull (válida para HR > 5 %; verificar aplicabilidad en meses extremadamente secos y documentar el tratamiento).
  - PW (agua precipitable) con la Ec. A5 de Aili a partir de T_db, HR, presión.
- [x] 2.3 **Screening climático z_i:** implementar los umbrales consolidados (RH 50–60 % Silva-Llanca; T_db 20 °C Silva-Llanca / 17 °C Yang; T_wb 19 °C Yang; PW bajo para radiativo, Aili). Definir z_i = 1 si el sitio cumple los umbrales en una fracción mínima de meses (fracción a definir y documentar). Salida: tabla de screening con detalle por umbral.
- [x] 2.4 **PUE/WUE por bundle:**
  - `H_CONV`: valores de referencia de Lei & Masanet (Casos 5/8, mediana y rango) — constantes por sitio, con corrección por clima si las figuras 5–6 lo permiten; si no, constante declarada.
  - `H_ECO`: horas/meses en modo seco/húmedo/mixto según umbrales de Yang aplicados a la climatología mensual → fracción φ_i; WUE del modo húmedo con el modelo de balance de agua IEC de EnergyPlus (evaporación + drift + blowdown, doc en `docs/feasibility/Balance de consumo de agua en IEC.md`, **verificar ecuaciones contra la fuente original antes de usar**).
  - `H_RAD`: potencial de enfriamiento radiativo con el modelo de Aili (requiere GHI, viento, PW, T_db); fracción de carga cubierta y respaldo mecánico restante.
  - `H_HYB`: cascada C9 de `Idea_discusion.md`: W_anual = W_base + (1−φ_i)·W_respaldo, combinando radiativo + economizador con respaldo convencional.
  - Para cada coeficiente, registrar en el CSV la **fuente y el supuesto** (columna `supuesto`/`fuente`), porque la trazabilidad es parte del argumento del paper.
- [x] 2.5 **Sanity check de resultados:** comparar los PUE obtenidos contra los rangos publicados (1.12–1.25 híbridos grandes; 1.39–1.98 medianos; ~2 convencional pequeño, Lei & Masanet §4.2). Si algo cae fuera, investigar antes de continuar. Registrar comparación en `results/etapa0_validacion.md`.
- [x] 2.6 Correr `ruff check` y `ruff format` sobre los scripts nuevos.

**Done cuando:** `results/etapa0_coeficientes.csv` existe con todas las combinaciones (sitio, bundle), los valores pasan el sanity check 2.5, y cada coeficiente tiene fuente/supuesto trazado.

---

## Fase 3 — Índice CAI (curtailment)

Script nuevo: `methods/cai_pipeline.py`. Entrada: `data/curtailment_acumulado.csv` + coordenadas de sitios candidatos. Salida: `results/cai_por_sitio.csv`.

- [x] 3.1 Implementar distancia de Haversine entre cada sitio i y las 100 plantas georreferenciadas.
- [x] 3.2 Implementar CAI_i = Σ_j C_j · exp(−d_ij/d0) con `d0` parametrizable. Calcular para d0 ∈ {20, 50, 100} km.
- [x] 3.3 Versión desagregada: CAI solar y CAI eólico por separado (columnas adicionales).
- [x] 3.4 Redactar (para uso en Fase 8) la **justificación de d0 como parámetro**: proximidad geodésica como proxy de factibilidad de interconexión; el análisis de sensibilidad sobre d0 sustituye el dato real del ECTD-2022; citar el ECTD-2022 como la fuente que cerraría la brecha en trabajo futuro. Guardar borrador en `docs/feasibility/justificacion_d0.md`.
- [x] 3.5 Verificación: ranking de sitios por CAI debe ser estable ante los tres valores de d0 (o documentar dónde cambia y por qué — eso mismo es un resultado del paper). Confirmar que el 25 % de plantas sin coordenadas (mayoritariamente eólicas del sur) no afecta la zona de estudio; cuantificar el % del curtailment total que sí está georreferenciado en las regiones XV–IV.

**Done cuando:** `results/cai_por_sitio.csv` con CAI total/solar/eólico × 3 valores de d0, y la justificación de d0 redactada.

---

## Fase 4 — Etapa 1: Modelo MILP

Script nuevo: `methods/milp_model.py` con PuLP (ya en dependencias). Especificación: secciones 1–6 de `docs/Idea_discusion.md`.

- [x] 4.1 Cargar parámetros desde `results/etapa0_coeficientes.csv` y `results/cai_por_sitio.csv`. Ningún número mágico embebido: todo parámetro de diseño (L, P, Budget, precios, pesos) en un bloque de configuración único o archivo de configuración.
- [x] 4.2 Fijar parámetros de diseño con justificación documentada:
  - L (carga IT, kW): proponer 1 MW (datacenter modular pequeño) — documentar.
  - p_energy, p_water: valores de referencia chilenos (costo marginal zona norte / tarifas de agua industrial) — si no hay fuente sólida, valores ilustrativos declarados.
  - CAPEX_h: valores proxy desde PNNL-24904 (`docs/feasibility/Data CAPEX.md`) + literatura, **declarados como proxy de edificios comerciales, no datacenters**.
  - P (número de sitios) y Budget: escenarios, no valores únicos.
- [x] 4.3 Implementar variables (x_i, y_ih binarias), restricciones R1–R7 y dominio, exactamente como la especificación. R6 y R7 como opcionales activables por configuración (R7 queda inactiva por defecto: sin datos DGA reales, se documenta como estructura preparada).
- [x] 4.4 Implementar la función objetivo normalizada min-max con pesos (α, β, γ).
- [x] 4.5 Salida: `results/milp_solucion_<escenario>.csv` (sitios seleccionados, bundle asignado, valores de objetivo desagregados) + log del solver.
- [x] 4.6 Verificación del modelo:
  - Caso trivial: P=1, un solo bundle factible → solución obvia a mano, el solver debe coincidir.
  - Extremos de pesos: α=1 (solo costo) debe elegir el bundle más barato; β=1 (solo agua) el de menor WUE; γ=1 (solo CAI) el sitio con mayor CAI. Verificar los tres.
  - Infactibilidad controlada: Budget demasiado bajo debe reportar infactible, no una solución absurda.
- [x] 4.7 `ruff check` + `ruff format`.

**Done cuando:** los tres tests de 4.6 pasan y el modelo resuelve el caso base en segundos.

---

## Fase 5 — Experimentos y análisis de sensibilidad

- [x] 5.1 Definir la grilla experimental (documentarla en `results/experimentos.md`):
  - Barrido de pesos (α, β, γ) sobre el simplex (paso 0.1) → frontera de Pareto aproximada.
  - Sensibilidad a d0 ∈ {20, 50, 100} km.
  - Escenarios de P ∈ {1, 2, 3} sitios.
  - (Opcional) Sensibilidad a CAPEX ±50 % dada la debilidad del proxy.
- [x] 5.2 Script `methods/experimentos.py` que corre la grilla y consolida en `results/experimentos_consolidado.csv`.
- [x] 5.3 Análisis: identificar (a) sitios que aparecen en toda la frontera (robustos), (b) puntos de quiebre donde cambia la selección, (c) efecto de d0 en el ranking. Estas tres cosas son el corazón de la sección de Resultados.
- [x] 5.4 Verificación de coherencia: los resultados deben ser explicables con los datos de entrada (p.ej., si un sitio domina, debe ser trazable a su clima o su CAI). Cualquier resultado contraintuitivo se investiga antes de reportarlo.

**Done cuando:** `results/experimentos_consolidado.csv` completo y los tres hallazgos de 5.3 redactados en borrador.

---

## Fase 6 — Figuras y tablas

Todas las figuras generadas por script (`methods/figuras.py`), reproducibles, guardadas en `figures/` como PDF (para XeLaTeX) o PNG de alta resolución.

- [x] 6.1 **Mapa de estudio:** norte de Chile con sitios candidatos (estaciones) y plantas con curtailment (tamaño ∝ MWh, color por tecnología).
- [x] 6.2 **Climatología comparada:** T_db, HR, T_wb mensuales por sitio (paneles o heatmap), con los umbrales de screening superpuestos.
- [x] 6.3 **Coeficientes Etapa 0:** PUE y WUE por sitio × bundle (barras agrupadas o heatmap).
- [x] 6.4 **CAI:** ranking de sitios con las tres curvas de d0.
- [x] 6.5 **Frontera de Pareto:** costo vs. agua vs. CAI (2D con color, o pares de proyecciones).
- [x] 6.6 **Tabla de solución:** sitios seleccionados y bundle por escenario.
- [x] 6.7 Tablas del paper: síntesis de fuentes (adaptar tabla H de `Idea_discusion.md`), parámetros del modelo con fuente/supuesto, resumen de datasets.

**Done cuando:** todas las figuras se regeneran con un solo comando y son legibles en el tamaño de columna IEEE.

---

## Fase 7 — Verificación de bibliografía

Los documentos de `docs/feasibility/` son salidas de Perplexity con URLs corruptas comprobadas. **Ninguna cita entra al paper sin verificar contra el documento original.**

- [x] 7.1 Verificar y agregar a `docs/ieee-paper/refs.bib` (vía Zotero, según convención del proyecto):
  - EnergyPlus Engineering Reference — modelo de agua de enfriadores evaporativos (Brecha 7).
  - PNNL-24904, Fernandez et al. 2015 (Brecha 3 — CAPEX proxy).
  - ECTD-2022, Coordinador Eléctrico Nacional (Brecha 4 — citado como trabajo futuro).
  - DGA — Catastro Público de Aguas (Brecha 5 — citado como trabajo futuro/estructura R7).
  - SNASPE/SEIA — capas de áreas protegidas (Brecha 8 — citado como screening futuro).
  - Leroy et al. 2019, *Science Advances* 5(10):eaat9480 — validación empírica radiativo en Atacama (Brecha 6). **Ojo:** las URLs del doc de feasibility están rotas; buscar el DOI real.
  - Fuentes de los datasets propios: reportes de curtailment del CEN, red de medición walker.dgf.uchile.cl (Ministerio de Energía / U. de Chile).
- [x] 7.2 Confirmar que los 5 papers ya presentes en `refs.bib` tienen metadatos completos (DOI, páginas).
- [x] 7.3 Verificar que cada claim del paper que dependa de una fuente de feasibility esté respaldado por el documento original, no por el resumen de Perplexity (en particular: ecuaciones de EnergyPlus y cifras de CAPEX de PNNL).

**Done cuando:** `refs.bib` completo y cada entrada verificada contra su fuente original.

---

## Fase 8 — Redacción del paper (.qmd)

Reemplazar la plantilla de `docs/ieee-paper/ieee-paper.qmd` (hoy es el ejemplo Typst de Quarto). **Decisión previa pendiente:** el template actual usa `format: ieee-typst` pero AGENTS.md declara XeLaTeX como motor — elegir uno y dejarlo consistente. Idioma: español (convención del proyecto).

Estructura y contenido por sección:

- [x] 8.1 **Título, abstract, keywords.** El abstract se escribe al final.
- [x] 8.2 **1. Introducción:** motivación (datacenters en Atacama, tensión agua-energía, ~13.7 TWh de curtailment acumulado en el dataset), pregunta de investigación, contribuciones (formulación MILP dos etapas; índice CAI como criterio de sostenibilidad energética novedoso; aplicación con datos chilenos reales), estructura del paper.
- [x] 8.3 **2. Trabajo relacionado:** los 4 papers organizados por lo que aporta cada uno (usar tabla H de `Idea_discusion.md`), cerrando con la brecha que este trabajo aborda: ningún trabajo previo integra clima + tecnología + origen de la energía (curtailment) en un modelo de localización para Chile.
- [x] 8.4 **3. Datos:** una subsección por dataset (solar, eólico, curtailment) condensando `methods/Metodología_*.md`; limitaciones declaradas (75 % georreferenciación, ventanas temporales heterogéneas, resolución mensual, no es TMY formal).
- [x] 8.5 **4. Metodología:**
  - 4.1 Arquitectura de dos etapas y justificación (por qué no embeber la física en el MILP).
  - 4.2 Etapa 0: derivación de coeficientes, screening, tabla de trazabilidad parámetro→fuente.
  - 4.3 CAI: definición, kernel de decaimiento, justificación de d0 como parámetro (desde `justificacion_d0.md`).
  - 4.4 Etapa 1: el MILP completo (conjuntos, parámetros, variables, objetivo, R1–R7, dominio).
- [x] 8.6 **5. Resultados:** caso base + los tres hallazgos de la Fase 5, con las figuras de la Fase 6.
- [x] 8.7 **6. Discusión y limitaciones:** convertir las brechas 2–8 en subsección de limitaciones (material ya casi escrito en `Idea_discusion.md` §7); qué claims quedan condicionados a qué datos; trabajo futuro (series horarias de curtailment, ECTD real, DGA, SEIA, piloto radiativo).
- [x] 8.8 **7. Conclusiones.**
- [x] 8.9 Escribir el abstract y revisar coherencia título↔contribuciones↔conclusiones.

**Done cuando:** borrador completo renderiza sin errores y cada sección cumple su checklist.

---

## Fase 9 — Render final y revisión de cierre

- [ ] 9.1 `quarto render` a PDF sin warnings; figuras y tablas legibles en formato final; ecuaciones bien numeradas y referenciadas.
- [ ] 9.2 Revisión de consistencia numérica: todo número del texto debe coincidir con `results/` (hacer una pasada explícita).
- [ ] 9.3 Revisión de citas: cada afirmación fuerte tiene cita o se declara como supuesto propio.
- [ ] 9.4 Reproducibilidad: desde repo limpio, la secuencia `uv sync` → pipelines → etapa0 → cai → milp → experimentos → figuras → render debe funcionar de punta a punta. Documentar la secuencia en el README.
- [ ] 9.5 Pasada de estilo/lenguaje (naturalidad del texto, consistencia de terminología ES).
- [ ] 9.6 Commit final y tag de versión del paper.

**Done cuando:** PDF final generado desde repo reproducible.

---

## Riesgos y puntos de atención (recordatorios entre sesiones)

1. **Datos demo del ECTD:** `datos_instalaciones_ectd2022_demo.csv` y `beta_por_coordenada_ectd2022.csv` contienen datos inventados/corruptos. Nunca usarlos como entrada del modelo.
2. **Docs de feasibility = Perplexity sin verificar:** URLs rotas confirmadas. Verificar todo contra originales (Fase 7) antes de citar.
3. **CAPEX es proxy:** PNNL-24904 es para edificios comerciales. Declararlo siempre; el análisis de sensibilidad ±50 % (5.1) es la defensa metodológica.
4. **Coeficientes de Aili son extrapolación:** modelo validado en Singapur; la validación en Atacama (Leroy 2019) es de material/piloto, no de sistema completo. El paper debe mantener ese matiz (Brecha 6).
5. **Formato Quarto:** resolver la inconsistencia ieee-typst vs. XeLaTeX antes de invertir en la redacción (inicio de Fase 8).
6. **Alcance:** es un paper de curso. Ante cualquier disyuntiva "más datos vs. declarar limitación", se declara la limitación y se avanza.
