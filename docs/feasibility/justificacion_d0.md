# Justificación del parámetro d0 en el Índice de Disponibilidad de Curtailment (CAI)

## Contexto

El Índice de Disponibilidad de Curtailment (CAI) pondera el curtailment acumulado
de cada planta renovable del SEN por su proximidad geodésica al sitio candidato,
utilizando un kernel de decaimiento exponencial:

$$
\text{CAI}_i = \sum_j C_j \cdot \exp\!\left(-\frac{d_{ij}}{d_0}\right)
$$

donde $d_0$ es la **escala de decaimiento** que controla cuán rápido pierde
relevancia una planta a medida que se aleja del sitio candidato.

## Proximidad geodésica como proxy de factibilidad de interconexión

La distancia Haversine entre un sitio candidato y una planta renovable es un proxy
razonable de la factibilidad técnico-económica de interconexión eléctrica. A menor
distancia:

- Menor longitud de líneas de transmisión o distribución requeridas.
- Menores pérdidas por transmisión.
- Menor costo de inversión en infraestructura eléctrica.
- Mayor posibilidad de conexiones *behind-the-meter* o líneas dedicadas (*spur lines*).

## Análisis de sensibilidad sobre d0

En ausencia de datos detallados de topología de red (subestaciones, líneas de
transmisión y su capacidad disponible), el análisis de sensibilidad sobre
$d_0 \in \{20, 50, 100\}$ km permite explorar el rango de escenarios:

| d0 (km) | Interpretación |
|---------|--------------------------------------|
| 20      | Solo plantas en entorno inmediato; conexión *behind-the-meter* o spur line corta. |
| 50      | Radio de influencia moderado; factible con líneas de distribución o transmisión local. |
| 100     | Alcance regional amplio; requiere acceso a infraestructura de transmisión troncal. |

## Conexiones típicas en el rango de decenas de km

La literatura técnica y la experiencia del SEN chileno indican que:

- Las conexiones *behind-the-meter* (tras el medidor) son económicamente atractivas
  cuando la fuente renovable y la carga se encuentran dentro de un radio de
  **pocos kilómetros** (< 5 km).
- Las líneas dedicadas (*spur lines*) son viables en rangos de
  **10 a 50 km**, dependiendo de la tensión y el terreno.
- Más allá de 50 km, la interconexión depende fuertemente de la infraestructura
  troncal existente y las restricciones de capacidad del sistema de transmisión.

El valor $d_0 = 50$ km representa un compromiso razonable entre relevancia local
y cobertura regional.

## Trabajo futuro: datos del ECTD-2022

El **Estudio de Costos de Transmisión y Distribución (ECTD-2022)** del Coordinador
Eléctrico Nacional contiene información detallada sobre:

- Costos unitarios de líneas de transmisión por tensión y tipo de terreno.
- Capacidades disponibles en subestaciones y líneas troncales.
- Topología de la red y restricciones de capacidad.

Incorporar los datos del ECTD-2022 permitiría reemplazar el proxy de distancia
geodésica por un modelo de costo de interconexión más realista, cerrando la brecha
principal de esta metodología. Este refinamiento queda planteado como trabajo
futuro del proyecto Yakhchal DataCenter.

## Referencias

- Coordinador Eléctrico Nacional (CEN). *Estudio de Costos de Transmisión y
  Distribución*, ECTD-2022.
- Coordinador Eléctrico Nacional (CEN). *Reportes de curtailment de energías
  renovables*, 2022–2026.
