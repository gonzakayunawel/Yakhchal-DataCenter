# Declaración de uso de inteligencia artificial

Este documento detalla el uso de herramientas de inteligencia artificial (IA) generativa y software de apoyo en el desarrollo del paper *"Optimización Multiobjetivo para la Localización y Selección Tecnológica de Datacenters en el Desierto de Atacama"* y de este repositorio, en cumplimiento de las buenas prácticas de transparencia y trazabilidad metodológica en investigación académica.

## Declaración general

La idea original, la formulación del modelo MILP de dos etapas, la definición del índice CAI, el diseño metodológico y la selección final de las referencias citadas fueron desarrollados íntegramente por el autor. Todas las salidas generadas por IA fueron verificadas, corregidas y reelaboradas críticamente por el autor, quien asume la responsabilidad completa de los argumentos, resultados y conclusiones presentados.

## Desglose por etapas

| Etapa | Herramientas | Rol de la IA | Rol humano |
|:---|:---|:---|:---|
| Idea original y planteamiento del problema | — | Ninguno | Idea, hipótesis y pregunta de investigación desarrolladas de forma independiente por el autor |
| Búsqueda de brecha y exploración de literatura | Claude (Anthropic), Consensus | Identificación preliminar de estudios relevantes, síntesis de resultados y refinamiento de la brecha | Decisión sobre el *gap* específico y el marco teórico tras análisis crítico |
| Selección de referencias citadas | Claude (Anthropic) | Apoyo con resúmenes y agrupación temática | Selección manual; ninguna cita entró a la bibliografía sin verificación contra el documento original |
| Localización de fuentes de datos | Perplexity AI | Asistente de búsqueda avanzada: sugerencia de posibles fuentes según criterios definidos por el autor | Selección, verificación de autoridad/pertinencia y descarga manual desde los repositorios originales (Coordinador Eléctrico Nacional, red Walker DGF). Las síntesis de la herramienta **no** se usaron como fuente primaria |
| Gestión bibliográfica y notas | Zotero, Notion (plugin Notero), BibTeX | Ninguno (herramientas no generativas) | Organización de referencias y notas |
| Implementación de código (pipelines, modelo MILP, figuras) | Claude Code, OpenCode (Claude, Anthropic) | Asistencia agéntica en implementación de *pipelines* de datos, modelo de optimización y generación programática de figuras | Especificación, supervisión, validación de resultados (sanity checks contra rangos publicados) y decisiones de diseño |
| Redacción y estructura del manuscrito | Python, Quarto, BibTeX, Git (*paper as code*) + Claude | Sugerencias puntuales de formulación y organización; edición de estilo | Redacción, estructura y contenido sustantivo del autor; revisión y reelaboración de toda sugerencia |
| Revisión final | Claude Code (skills de revisión académica) | Detección de inconsistencias formales, redundancias y problemas de claridad; simulación de revisión por pares | Aplicación selectiva de sugerencias, previa evaluación crítica; verificación de consistencia numérica contra `results/` |

## Reproducibilidad

El flujo completo de análisis es reproducible sin herramientas de IA: la secuencia `uv sync` → pipelines de datos → precómputo Etapa 0 → CAI → MILP → experimentos → figuras → render Quarto está documentada en el [README](README.md) y no depende de modelos generativos. La IA participó en la *construcción* del código y del texto, no en su *ejecución*.

## Prácticas observadas

- La IA no figura como autor ni coautor del trabajo.
- No se incorporaron datos, citas ni referencias generadas por IA sin verificación explícita contra las fuentes originales (ver Fase 7 de `docs/PLAN_PAPER.md`).
- Los documentos exploratorios de `docs/feasibility/` (salidas de Perplexity) están marcados como material de investigación sin verificar y no se citan directamente en el paper.
