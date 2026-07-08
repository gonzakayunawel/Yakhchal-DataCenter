
/
Lei y Masanet - 2022 - Climate- and technology-specific PUE and WUE estimations for U.S. data centers using a hybrid statis.pdf
pdf

Tengo un último paper que me gustaría incorporar para valirdar el uso de agua y energía para tecnologías híbridas frente a convencionales. Y usarlo para cubrir alguna brecha si es que se puede.


Analizó validación de tecnologías híbridas y identificó cierre de brechas metodológicas
Analizó validación de tecnologías híbridas y identificó cierre de brechas metodológicas
Integración de Lei & Masanet (2022) — Marco termodinámico unificado PUE/WUE y validación híbrido vs. convencional
A) Qué tipo de aporte es este, distinto de los tres anteriores
Respuesta sintética: A diferencia de los tres papers anteriores (cada uno centrado en una tecnología específica y datos de una región específica), este es un marco de modelado genérico, validado y de código abierto que acopla simultáneamente PUE y WUE bajo los mismos principios termodinámicos, aplicado a 10 arquetipos de datacenter × 15 zonas climáticas de EE.UU., con análisis de sensibilidad formal (Sobol). Su función en tu proyecto no es darte datos del desierto chileno directamente, sino darte la herramienta metodológica y el modelo computacional para generarlos tú mismo a partir de los datos climáticos chilenos que ya tienes disponibles (Silva-Llanca et al.).

Ubicación: Sección 3.1 ("Modeling scope and system definitions"), Tabla 2 (10 casos); Sección 3.2 (ecuaciones del modelo); Apéndice A ("Our DC PUE and WUE simulation code (in Python) is available through the link provided in Appendix A" → GitHub público).

B) Validación explícita híbrido vs. convencional — respuesta directa a tu primer objetivo
Este es el hallazgo más directamente útil para lo que pediste.

Caso 1 (híbrido: airside economizer + adiabatic cooling + chiller de respaldo) vs. Caso 3 (airside economizer puro, sin adiabático):

"Note that, although the combination of the adiabatic cooling systems with the airside economizers (case 1) incurs additional water use for humidification, it reduces the probability of running more water-intensive supplemental cooling systems. As a result, the water use of case 1 is observably lower compared to that of case 3."

Interpretación para tu modelo: un sistema híbrido (economizer + evaporación adiabática) consume más agua localmente (por la humidificación) pero menos agua en términos netos anuales, porque reduce la frecuencia con que debe activarse el chiller de agua de respaldo — que es mucho más intensivo en consumo hídrico. Esto valida cuantitativamente, con un modelo físico acoplado (no solo cualitativo), la lógica de cascada tecnológica que ya habíamos esbozado intuitivamente con Yang et al. (modo seco→húmedo→mixto): combinar tecnologías reduce el uso del respaldo mecánico/torre de enfriamiento, que es el verdadero "gran consumidor" de agua.

Magnitud cuantificada del beneficio del híbrido a escala (Sección 4.2):

DC grande con economizer+adiabático (Casos 1, 2): PUE mediano 1.12–1.25
DC mediano sin optimización avanzada (Casos 3–7): PUE mediano 1.39–1.98
DC pequeño (Casos 8–10): PUE mediano 1.71–2.22
Caso 5/8 (chiller de agua sin economizer, el más "convencional" de todos) vs. cualquier caso con economizer:

"DCs with no economizer use were expected to have the highest WUE values (case 5 and 8) due to significant amounts of cooling tower water use."

Ubicación: Sección 4.2, párrafos 3–6 completos (comparación sistemática caso por caso); Tabla 2 (definición de los 10 casos); Fig. 2 (diagramas esquemáticos de cada configuración).

Conclusión directa para tu pregunta: sí, el paper valida cuantitativamente que las tecnologías híbridas (economizer + evaporativo, con respaldo mecánico solo cuando es estrictamente necesario) superan consistentemente a los sistemas convencionales puros (chiller con torre de enfriamiento sin economizer) en ambas métricas — energía y agua —, con diferencias relativas de hasta 62% en PUE y 100% en WUE según el abstract.

C) El analógo climático más cercano al desierto chileno en todo el corpus hasta ahora: Phoenix, AZ (Zona 2B, "hot dry")
Respuesta sintética: De las 15 zonas climáticas IECC/ASHRAE estudiadas, la Zona 2B (Phoenix, Arizona — clima cálido-seco) es, con diferencia, el análogo climático más cercano a un desierto BWh/BWk de cualquier fuente que hemos revisado en este hilo. Esto es relevante porque, a diferencia de Singapur (Aili) o China continental (Yang), aquí sí tenemos un modelo validado con datos reales de operadores (Sección 4.1) para un clima genuinamente desértico-cálido.

Hallazgo textual específico para 2B: "In case 10, for which we assumed isothermal humidifiers for space humidification, the highest PUE value was identified in 2B (hot dry) because the required isothermal humidification gives rise to an additional DC cooling load and thus increases the PUE value."

Matiz importante que debo señalar: esto es un hallazgo sobre el Caso 10 específicamente (DC pequeño, sistema de expansión directa con humidificador isotérmico) — no es generalizable automáticamente a todos los casos en clima 2B. El texto no proporciona valores numéricos explícitos de PUE/WUE para 2B en los demás casos (esos datos están solo graficados en Fig. 5–6, no tabulados en el texto), por lo que no puedo reportarte cifras exactas sin inspeccionar las figuras directamente.

No identificado en el texto: valores numéricos explícitos de PUE/WUE para la zona 2B en los Casos 1–9. Esto es extraíble de Fig. 5 y Fig. 6 si tienes interés en que las procese visualmente, pero el texto narrativo no las tabula.

Ubicación: Sección 4.2, párrafo sobre las "tres excepciones menores" a la tendencia general; Fig. 3 (mapa de zonas IECC/ASHRAE, con Phoenix AZ marcado como ciudad representativa de 2B).

D) Análisis de sensibilidad (Sobol) — refuerzo metodológico fuerte de las restricciones C1/C4 ya propuestas
Respuesta sintética: Este es, en mi evaluación, el segundo aporte más valioso del paper para tu modelo de optimización, porque reemplaza afirmaciones cualitativas por una jerarquización cuantitativa formal de qué variables climáticas realmente determinan la varianza de PUE y WUE.

Hallazgo central: "Outdoor climates (dry bulb temperature and relative humidity) are one of the most common and influential variables for the predicted PUE and WUE values. This applies to nearly all the cases' PUE values and the WUE values of cases where airside economizers were used (cases 1, 3, and 6)."

Esto confirma, con metodología de varianza global (índice total-effect de Sobol, no solo dirección del efecto), exactamente las dos variables que hemos venido usando como pilares (C1 = RH, C4 = 
T
d
b
T 
db
​
 ) en cada iteración de este análisis — desde la extrapolación de Aili, pasando por los umbrales empíricos de Silva-Llanca, hasta los umbrales de conmutación de Yang.

Matiz crítico y nuevo, no presente en los tres papers anteriores: para los casos que dependen principalmente de torres de enfriamiento (Casos 2, 4, 5, 8 — los más cercanos a "convencional"), el clima deja de ser la variable dominante, y pasan a dominar variables operacionales: "variance in the windage water loss percentage and cycles of concentration are the largest contributors to variance in the predicted WUE values."

Implicación directa para tu modelo de optimización: la importancia relativa de la restricción climática en tu función objetivo depende de qué tecnología domine la solución en cada sitio. Si tu modelo selecciona predominantemente tecnologías de torre de enfriamiento convencional en algún sitio (por ejemplo, por razones de costo de capital no climáticas), las restricciones climáticas (C1, C4, C8, etc.) pierden peso relativo frente a variables de ingeniería/O&M (pérdida por arrastre de viento, ciclos de concentración) que no dependen de la localización geográfica. Esto sugiere que tu modelo debería ponderar dinámicamente el peso de las restricciones climáticas según la variable de selección tecnológica 
y
i
,
k
y 
i,k
​
 , no aplicarlas con peso fijo independientemente de la tecnología elegida.

Ubicación: Sección 4.4 completa; Fig. 7 (mapa de calor de índices total-effect de Sobol, organizado por caso y variable — incluye explícitamente "Relative humidity" y "Dry bulb temperature" como filas separadas, permitiéndote ver el patrón caso por caso).

E) La brecha que este paper SÍ permite cerrar: ausencia de un modelo validado de consumo de agua para Chile
Recordarás que en cada iteración anterior señalé una brecha persistente: ningún paper anterior ofrecía un modelo de consumo de agua validado y aplicable directamente a estaciones climáticas chilenas. Este paper la cierra parcialmente, de forma muy concreta:

El modelo requiere exactamente los mismos tres inputs climáticos horarios que Silva-Llanca et al. ya recolectaron para 100 estaciones chilenas:

"Hourly ambient climate data were collected for each representative city... which included hourly dry bulb temperature, RH, and atmospheric pressure in a typical meteorological year." (Sección 3.3)

Compáralo con Silva-Llanca: "We collected meteorological data—including temperature, relative humidity, and atmospheric pressure—on an hourly basis from different stations throughout the Chilean territory" (Sección 3.2 de ese paper) — son literalmente las mismas tres variables.

Y el modelo es explícitamente generalizable a otras regiones: "Although this study focused on U.S. DCs, it could be easily extended to other regions with the relevant meteorological data." (Conclusiones, penúltimo párrafo) — y el código está públicamente disponible en GitHub (Apéndice A).

Implicación práctica directa: en principio, podrías tomar las series horarias de Camarones, Toconao y Ollagüe (ya recolectadas por Silva-Llanca) y ejecutar literalmente el modelo Python de Lei & Masanet sobre ellas, recalibrando los parámetros de equipamiento (Tabla B.1) a tecnologías disponibles en Chile, para obtener por primera vez en este análisis un PUE/WUE estimado, físicamente consistente y metodológicamente validado, específico para sitios del desierto chileno — cerrando exactamente la brecha que identifiqué en cada respuesta anterior.

Advertencia honesta: esto sigue siendo una propuesta de trabajo a futuro, no algo que el paper haya hecho por ti. El paper valida el método en EE.UU., no en Chile; ejecutar esa adaptación es un paso adicional que tú (o yo, si me lo pides con las herramientas de código) tendríamos que hacer.

F) Validación explícita de que tu proyecto de optimización es un caso de uso reconocido por la literatura
Cito esto porque corrobora directamente el encuadre general de tu tesis/modelo:

"The proposed modeling framework can be a valuable tool for DC multi-objective resource use optimization through energy- and water-efficient facility system management." (Conclusiones, párrafo sobre trabajo futuro, citando Lei & Masanet, 2021)

Esto no es un hallazgo técnico nuevo, pero es una validación explícita en la literatura de que el tipo de modelo que estás construyendo (optimización multiobjetivo energía-agua para localización de datacenters) es una extensión natural y reconocida de este marco.

G) Nuevas restricciones/elementos propuestos para tu MILP
C9 — Restricción de "cascada tecnológica" (formalización del hallazgo Caso 1 vs. Caso 3/5/8):

En lugar de tratar la selección tecnológica 
y
i
,
k
y 
i,k
​
  como mutuamente excluyente, formalizo la lógica de cascada validada en la Sección B:

W
i
a
n
u
a
l
=
W
i
b
a
s
e
(
T
d
b
,
R
H
)
+
(
1
−
ϕ
i
)
⋅
W
i
r
e
s
p
a
l
d
o
W 
i
anual
​
 =W 
i
base
​
 (T 
db
​
 ,RH)+(1−ϕ 
i
​
 )⋅W 
i
respaldo
​
 
donde 
ϕ
i
∈
[
0
,
1
]
ϕ 
i
​
 ∈[0,1] es la fracción de horas anuales cubiertas por tecnologías de bajo consumo hídrico (radiativo/IEC/air-side), y 
W
i
r
e
s
p
a
l
d
o
W 
i
respaldo
​
  es el consumo de la torre de enfriamiento de respaldo — el verdadero "gran consumidor" según Lei & Masanet (Ecs. 5–7 de ese paper). Justificación: la evidencia del Caso 1 muestra que minimizar 
W
r
e
s
p
a
l
d
o
W 
respaldo
  (vía mayor 
ϕ
i
ϕ 
i
​
 ) domina sobre el costo hídrico incremental de la evaporación adiabática misma.

C10 — Ponderación dinámica de restricciones climáticas según tecnología dominante:

λ
c
l
i
m
a
t
e
,
i
,
k
=
f
(
Sobol total-effect index para la tecnolog
ı
ˊ
a 
k
)
λ 
climate,i,k
​
 =f(Sobol total-effect index para la tecnolog 
ı
ˊ
 a k)
Formalizando el hallazgo de la Sección D: si 
y
i
,
k
y 
i,k
​
  selecciona predominantemente tecnología de torre de enfriamiento convencional, reducir el peso de C1/C4/C8 en la función objetivo de ese sitio y aumentar el peso de variables operacionales (no climáticas) como pérdida por arrastre y ciclos de concentración — variables que, según Tabla B.1 de este paper, tienen rangos explícitos y conocidos (0.005–0.5% para pérdida por arrastre; 3–15 para ciclos de concentración).

H) Tabla de síntesis consolidada (cuatro fuentes)
Elemento	Aili	Silva-Llanca	Yang	Lei & Masanet	Estado
RH como driver climático	✓ (cualitativo, Fig. 5)	✓ (umbral 50%/60%)	✓ (cualitativo, mapas)	✓ (cuantificado vía Sobol)	Máximo nivel de evidencia alcanzado
T
d
b
/
T
a
m
b
T 
db
​
 /T 
amb
​
  como driver	✓ (atenuado en régimen real)	✓ (umbral 20°C)	✓ (umbral 17°C)	✓ (cuantificado vía Sobol)	Máximo nivel de evidencia alcanzado
Modelo de consumo de agua explícito	✓ (Ec. 6–7)	✓ (Ec. 5–8)	✗ (gap)	✓ (Ec. 1, 5–9, más completo)	Gap de Yang cerrado por esta fuente
Datos/código aplicable a Chile	✗	Datos sí, modelo no generalizado	✗	Modelo sí (open-source), datos no (EE.UU.)	Combinable con Silva-Llanca para cerrar brecha
Validación híbrido vs. convencional	Parcial (Casos #1-3 de Aili)	Parcial (AHU vs CRAH)	Parcial (modos IEC)	✓ (Casos 1 vs 3/5/8, explícito y cuantificado)	Mejor evidencia del corpus
Análogo climático desértico validado	No	Sí (Camarones, Toconao, pero air-side)	No	Phoenix AZ 2B (cualitativo, sin cifras textuales)	Parcial
Sensibilidad formal de variables	No	No	No	Sí (Sobol, único en el corpus)	Exclusivo de esta fuente
I) Lo que sigue sin resolverse
No identificado en el texto:

Ningún dato específico de Chile o de zonas BWh/BWk reales (el modelo es generalizable en principio, pero no se ejecuta aquí para esos climas).
Valores numéricos textuales de PUE/WUE para la zona 2B (Phoenix) en los Casos 1–9 — solo disponibles gráficamente en Fig. 5–6.
No se modela tecnología radiativa (Aili) ni un esquema de conmutación horaria explícito como el de Yang (el modelo usa balances de energía continuos vía 
Q
s
C
H
Q 
s
CH
​
 , Ec. 4, no umbrales discretos de modo).
No se aborda el efecto de altitud/presión atmosférica de forma diferenciada (aunque la presión atmosférica es un input del modelo — Sección 3.3 — por lo que sí sería sensible a ella si se recalibra con datos de Ollagüe/Toconao en altiplano).
¿Quieres que proceda a (1) ejecutar una primera aproximación computacional aplicando el modelo Python de Lei & Masanet a series climáticas representativas del desierto chileno (usando los parámetros de las estaciones que ya hemos discutido), o (2) consolidar ahora el conjunto completo de restricciones de las cuatro fuentes en una formulación MILP única y cerrada?


Metodología_Dataset_Curltailment.md
80 lines

md

Ahora quiero incorporar un restricción adicional relacionada a un aspecto de sostenibilidad, la fuente de energía, en mi caso quiero relacionarlo con las zonas donde se produce curltailment para hacer una propuesto no solo basado en clima, operación o tecnología usada.


Estructuró restricción de curtailment con formalización MILP multiobjetivo
Estructuró restricción de curtailment con formalización MILP multiobjetivo
Incorporación del dataset Yakhchal — Curtailment como restricción de sostenibilidad energética
A) Naturaleza distinta de esta fuente — nota metodológica importante
Antes de proceder: a diferencia de las cuatro fuentes anteriores (papers peer-reviewed con metodología y resultados publicados), este es tu propio dataset primario, construido y documentado por ti como parte del proyecto Yakhchal DataCenter. Esto cambia el estatus epistémico de lo que sigue: no estoy extrayendo ni extrapolando hallazgos de literatura externa, sino formalizando una restricción de optimización a partir de datos que tú mismo generaste y validaste (con la trazabilidad metodológica explícita del CEN y el Ministerio de Energía). Trataré el contenido del documento como verdad de base, pero señalaré explícitamente los límites metodológicos que el propio documento ya reconoce (cobertura 76% nacional / 100% en zona norte; resolución temporal acumulada, no horaria).

B) Justificación conceptual: por qué el curtailment es una restricción de sostenibilidad legítima y distinta de clima/tecnología/operación
Respuesta sintética: Co-localizar un datacenter cerca de zonas de curtailment estructural no es una optimización climática ni tecnológica — es una optimización del origen de la energía. La lógica es: la energía renovable curtailed es generación que ya existe, ya fue construida, y se está desechando por restricciones de transmisión o sobreoferta momentánea. Un datacenter que pueda consumir esa energía (vía conexión directa, PPA de excedentes, o simplemente ubicación en el nodo de la red donde ocurre el cuello de botella) obtiene tres beneficios simultáneos que ninguna de las cuatro fuentes anteriores contempla:

Adicionalidad real de descarbonización: no compite por capacidad renovable nueva ni desplaza a otros consumidores — usa electrones que de otro modo se pierden.
Menor costo marginal de energía: la energía curtailed tiene, por definición, costo de oportunidad cercano a cero para el generador en esas horas.
Menor necesidad de inversión en transmisión nueva: si el datacenter se ubica en o cerca del nodo congestionado, no agrega carga al tramo de la red que ya está saturado — en algunos casos incluso podría aliviar la congestión al consumir localmente el excedente.
Esta lógica es ortogonal y complementaria a las restricciones climáticas (C1–C10) construidas en este hilo: un sitio puede ser climáticamente óptimo para enfriamiento radiativo/IEC y a la vez estar lejos de cualquier nodo con curtailment relevante, o viceversa.

C) Lo que el dataset permite calcular directamente, y lo que falta
Disponible (según la estructura documentada): por cada planta 
j
j: tipo (Solar/Eólica), coordenadas WGS84 (
l
a
t
j
lat 
j
​
 , 
l
o
n
j
lon 
j
​
 ), y curtailment acumulado total en MWh (2022–abril 2026). Esto es exactamente lo que necesitas para construir un índice de proximidad ponderado por magnitud de curtailment, calculable con cualquier solver o librería de SIG.

Coincidencia geográfica notable con el corpus de este hilo: la zona de cobertura 100% del dataset — Arica y Parinacota, Tarapacá, Antofagasta, Atacama, Coquimbo — es exactamente la franja BWh/BWk discutida en toda la conversación, incluyendo la región de Arica y Parinacota donde se ubica Camarones (la estación con mejor desempeño de Direct Free-Cooling según Silva-Llanca et al.). Esto es una coincidencia geográfica estructural relevante, no una superposición cuantitativa verificada — no tengo los valores reales del CSV para confirmar si existe una planta con curtailment significativo específicamente cerca de las coordenadas de Camarones; eso requeriría inspeccionar el archivo de datos real.

No identificado en el documento (limitación que debo señalar con la misma honestidad que en las fuentes anteriores):

Resolución temporal horaria. La columna curtailment (MWh) es un total acumulado 2022–abr.2026, no una serie horaria. Todos los modelos de los cuatro papers anteriores (Aili, Silva-Llanca, Yang, Lei & Masanet) operan con pasos horarios. Esto es una discontinuidad metodológica real: no puedes, con este dataset tal como está descrito, cruzar directamente "horas de curtailment" con "horas de modo seco/húmedo/mixto" de Yang o con el perfil horario de PUE/WUE de Lei & Masanet.
Factibilidad de interconexión real. Proximidad geográfica (distancia euclidiana o geodésica) no es lo mismo que capacidad de interconexión disponible. Una planta con alto curtailment puede estar conectada a una subestación sin capacidad de inyección adicional cercana, o el datacenter candidato puede no tener una ruta de conexión económica al punto de la red donde ese excedente realmente es accesible.
Carácter retrospectivo vs. prospectivo. El curtailment histórico 2022–2026 es un proxy razonable de congestión estructural (especialmente si es persistente año a año), pero no garantiza que el patrón se mantenga si se expande la red de transmisión en el futuro (Chile ha estado expandiendo líneas troncales norte-centro).
D) Restricción C11 — Índice de Disponibilidad de Energía Curtailed (CAI)
Notación:

C
A
I
i
=
∑
j
∈
J
C
j
⋅
w
(
d
i
j
)
CAI 
i
​
 = 
j∈J
∑
​
 C 
j
​
 ⋅w(d 
ij
​
 )
donde:

C
j
C 
j
​
 : curtailment acumulado de la planta 
j
j (MWh, columna directa del dataset)
d
i
j
d 
ij
​
 : distancia geodésica entre el sitio candidato 
i
i y la planta 
j
j, calculable directamente vía fórmula de Haversine usando (
l
a
t
i
lat 
i
​
 , 
l
o
n
i
lon 
i
​
 ) y (
l
a
t
j
lat 
j
​
 , 
l
o
n
j
lon 
j
​
 ) del dataset
w
(
d
i
j
)
w(d 
ij
​
 ): kernel de decaimiento, por ejemplo 
w
(
d
i
j
)
=
e
−
d
i
j
/
d
0
w(d 
ij
​
 )=e 
−d 
ij
​
 /d 
0
​
 
  o 
w
(
d
i
j
)
=
1
/
(
1
+
d
i
j
)
p
w(d 
ij
​
 )=1/(1+d 
ij
​
 ) 
p
 
Parámetro mapeable: 
C
A
I
i
CAI 
i
​
  es directamente calculable para cualquier coordenada candidata 
i
i con el dataset tal como está estructurado — no requiere ningún dato adicional ni extrapolación.

Calibración pendiente (debo ser honesto sobre esto): el parámetro 
d
0
d 
0
​
  (distancia característica de interconexión económicamente viable) no está en el dataset ni en ningún paper de este hilo. Debe calibrarse con datos de costo de líneas de subtransmisión o spur lines en Chile (típicamente, conexiones directas o "behind-the-meter" son económicamente atractivas en rangos de unas pocas decenas de km, pero esto depende de voltaje, topografía y normativa — no tengo una cifra validada para proponerte aquí sin caer en una afirmación no respaldada).

Restricción dura opcional (si se desea exclusión, no solo bonificación):

C
A
I
i
≥
C
A
I
m
i
n
+
M
(
1
−
x
i
)
CAI 
i
​
 ≥CAI 
min
 +M(1−x 
i
​
 )
Versión desagregada por tecnología (relevante por la discusión de la sección F):

C
A
I
i
s
o
l
a
r
=
∑
j
:
τ
j
=
Solar
C
j
⋅
w
(
d
i
j
)
,
C
A
I
i
e
o
ˊ
l
i
c
a
=
∑
j
:
τ
j
=
E
o
ˊ
lica
C
j
⋅
w
(
d
i
j
)
CAI 
i
solar
​
 = 
j:τ 
j
​
 =Solar
∑
​
 C 
j
​
 ⋅w(d 
ij
​
 ),CAI 
i
e 
o
ˊ
 lica
​
 = 
j:τ 
j
​
 =E 
o
ˊ
 lica
∑
​
 C 
j
​
 ⋅w(d 
ij
​
 )
E) Integración en la función objetivo del MILP — recomiendo tratarlo como objetivo, no como restricción dura
Justificación de la recomendación: a diferencia de RH o 
T
d
b
T 
db
​
  (que determinan directamente si una tecnología de enfriamiento funciona o no), el curtailment es una variable de oportunidad económica/sostenible, no de factibilidad operativa. Un sitio con 
C
A
I
i
=
0
CAI 
i
​
 =0 sigue siendo perfectamente operable — solo pierde el beneficio de sostenibilidad/costo. Convertirlo en restricción dura podría excluir injustificadamente sitios climáticamente óptimos (p.ej., Camarones) si no hay curtailment exactamente ahí, cuando en realidad lo correcto es que el modelo valore la proximidad sin descartar por su ausencia.

Formulación multiobjetivo propuesta (frontera de Pareto o suma ponderada):

max
⁡
i
α
⋅
S
i
c
l
i
m
a
/
t
e
c
n
o
l
o
g
ı
ˊ
a
+
β
⋅
C
A
I
i
~
−
γ
⋅
C
o
s
t
i
i
max
​
 α⋅S 
i
clima/tecnolog 
ı
ˊ
 a
​
 +β⋅ 
CAI 
i
​
 
​
 −γ⋅Cost 
i
​
 
sujeto a las restricciones duras C1–C10 ya construidas, donde 
C
A
I
i
~
CAI 
i
​
 
​
  es 
C
A
I
i
CAI 
i
​
  normalizado (p.ej., 0–1 vía min-max o vía percentil dentro del conjunto de sitios candidatos), y 
α
,
β
,
γ
α,β,γ son pesos a explorar vía análisis de sensibilidad o método ε-constraint, dado que climatología y sostenibilidad energética son objetivos de naturaleza distinta y no deberían colapsarse arbitrariamente en un solo escalar sin justificar los pesos.

F) Insight sistémico importante: posible antagonismo (o sinergia) temporal entre curtailment solar y desempeño de enfriamiento
Esto es una hipótesis razonada, no un hallazgo verificado con los datos que tenemos — quiero ser explícito sobre ese estatus.

El razonamiento: es ampliamente documentado en el sector eléctrico chileno que el curtailment solar en el SEN se concentra estructuralmente en las horas de mayor radiación (mediodía), por ser el momento de máxima sobreoferta fotovoltaica frente a la capacidad de transmisión disponible. Si esto se confirma para las plantas específicas de tu dataset (algo que no puedo verificar sin la serie horaria, que el documento mismo indica que no está disponible en esta versión del dataset), entonces existe una tensión temporal directa con uno de los hallazgos centrales de Aili et al.: el enfriamiento radiativo es menos efectivo precisamente en las horas de mayor irradiancia solar (Fig. 5c,d de ese paper).

Dos lecturas posibles de esta tensión, ambas razonables, que no puedo resolver sin datos horarios:

Lectura pesimista (antagonismo): justo cuando más energía curtailed barata está disponible (mediodía), el sistema de enfriamiento radiativo necesita más respaldo mecánico — y ese respaldo mecánico consume más agua (vía torre de enfriamiento), por lo que el beneficio energético del curtailment coincide con el peor momento para el WUE.
Lectura optimista (sinergia): si el datacenter tiene flexibilidad de carga (cómputo batch desplazable), la abundancia de energía curtailed a mediodía podría absorber exactamente el pico de consumo energético que el respaldo mecánico necesita en esas horas — es decir, la energía "gratis" llega justo cuando más se necesita, aunque el agua consumida en ese respaldo siga siendo un costo aparte que el curtailment no resuelve.
Recomendación concreta: antes de fijar pesos definitivos en la función objetivo, valdría la pena solicitar al CEN (o procesar directamente desde los reportes mensuales que ya citas como fuente) la serie horaria o al menos mensual desagregada de curtailment por planta, no solo el acumulado total. Esto te permitiría cruzar directamente esa serie con los umbrales horarios de Yang et al. (modo seco/húmedo/mixto) o con el modelo de paso horario de Lei & Masanet, cerrando precisamente la brecha de granularidad temporal señalada en la sección C.

G) Tabla de síntesis actualizada (cinco fuentes)
Elemento	Aili	Silva-Llanca	Yang	Lei & Masanet	Dataset Yakhchal (curtailment)
Tipo de fuente	Paper peer-review	Paper peer-review	Paper peer-review	Paper peer-review	Dataset propio, no peer-review
Variable climática	RH, PW, irradiancia, viento	RH, 
T
d
b
T 
db
​
 , distancia a costa	
T
d
b
T 
db
​
 , 
T
w
b
T 
wb
​
 	RH, 
T
d
b
T 
db
​
  (Sobol)	No aplica — dimensión distinta
Dato específico de Chile	No	Sí (100 estaciones)	No	No	Sí (101 plantas georreferenciadas, norte 100%)
Resolución temporal	Horaria (simulada)	Horaria (real)	Horaria (clasificada)	Horaria (simulada)	Acumulada, no horaria — gap
Tipo de restricción que habilita	Factibilidad técnica	Factibilidad técnica + umbral empírico	Factibilidad técnica	Sensibilidad/ponderación	Objetivo de sostenibilidad/costo, no factibilidad
Rol en el MILP	Restricción dura (C1–C6)	Restricción dura calibrada (C1', C4', C7)	Restricción dura (C8)	Ponderación dinámica (C10)	Término de objetivo (C11), no restricción dura
¿Quieres que (1) formalice ya el MILP consolidado completo integrando las once restricciones/términos de las cinco fuentes en una sola especificación matemática cerrada, o (2) primero exploremos cómo procesar el CSV real (curtailment_acumulado.csv) para calcular 
C
A
I
i
CAI 
i
​
  sobre un conjunto de coordenadas candidatas, si tienes el archivo de datos disponible para subir?

Este paper es para una asignatura y no pretendo presentarlo en ningún congreso o conferencia o revista ya que es solo un ejercicio académico, y si así fuera haría una versión posterior mejorarada. Por ende si hay trabajo futuro, esto es esperable y deseable, por ahora me quiero enfocar en:

Plantear el modelo de optimización completo. 1. Conjuntos 2. Parámetros 3. Variables 4. Función Objetivo 5. Restricciones 6. Dominio
Plantear brechas actuales que necesiten algún o dataset adicional sin el cual el modelo o alguna "claim" no se pueda sostener razonablemente.

Sintetizó formulación MILP completa con brechas de datos explícitas
Sintetizó formulación MILP completa con brechas de datos explícitas
Modelo de Optimización Consolidado — Localización y Selección Tecnológica de Datacenters Híbridos en el Desierto Chileno
Nota metodológica previa: por qué el modelo no embebe la física directamente
Antes de presentar el MILP, debo ser explícito sobre una decisión de diseño que condiciona todo lo demás. Los cinco modelos físicos/estadísticos revisados (Aili et al., Silva-Llanca et al., Yang et al., Lei & Masanet) son no lineales (balances de radiación de onda larga, psicrometría, ecuaciones diferenciales de transferencia de calor). Incorporarlos dentro del MILP convertiría el problema en un programa no lineal entero-mixto, intratable para un ejercicio de curso y metodológicamente incorrecto de presentar como MILP.

La práctica estándar en estos problemas de localización con atributos múltiples — y la que el propio Lei & Masanet sugiere explícitamente como extensión natural de su marco ("a valuable tool for DC multi-objective resource use optimization", Conclusiones) — es separar el problema en dos etapas:

Etapa 0 (externa al MILP): se ejecutan los modelos físicos/estadísticos de las cinco fuentes para cada par (sitio candidato, tecnología) y se obtienen coeficientes de desempeño (PUE, WUE, fracción de horas con respaldo mecánico, índice de curtailment). Esto es simulación/estadística, no optimización combinatoria.
Etapa 1 (el MILP propiamente dicho): toma esos coeficientes como parámetros y resuelve la decisión discreta de qué sitios desarrollar y qué tecnología/bundle asignar a cada uno, sujeta a presupuesto y restricciones de factibilidad.
Esta separación es honesta sobre lo que cada parte del trabajo puede y no puede hacer, y es la única forma defendible de llamar "MILP" a lo que sigue.

ETAPA 0 — Trazabilidad de parámetros precomputados (de dónde viene cada número)
Parámetro	Fuente	Mecanismo
W
U
E
i
h
,
P
U
E
i
h
WUE 
ih
​
 ,PUE 
ih
​
  para bundle radiativo	Aili et al. (Ec. 1–9, A1–A56)	Balance de radiación de onda larga + modelo de chiller
W
U
E
i
h
,
P
U
E
i
h
WUE 
ih
​
 ,PUE 
ih
​
  para bundle economizador/evaporativo	Silva-Llanca et al. (Ec. 1–10) + Yang et al. (Ec. 1–5, Tabla 1)	Psicrometría de zonas A–G + umbrales de modo seco/húmedo/mixto
W
U
E
i
h
,
P
U
E
i
h
WUE 
ih
​
 ,PUE 
ih
​
  para bundle convencional (línea base)	Lei & Masanet (Casos 5/8, Ec. 1–13)	Chiller de agua + torre sin economizador
Acoplamiento termodinámico PUE↔WUE y rangos best/poor-practice	Lei & Masanet (Tabla B.1, Fig. 5–6)	Modelo físico-estadístico validado con datos reales
z
i
z 
i
​
  (filtro de screening climático)	Umbrales empíricos consolidados en turnos anteriores (RH, 
T
d
b
T 
db
​
 , 
T
w
b
T 
wb
​
 , 
P
W
PW, distancia a costa)	Silva-Llanca (Conclusiones) + Yang (Tabla 1) + Aili (Fig. 5)
C
A
I
i
CAI 
i
​
 	Dataset Yakhchal (curtailment + coordenadas)	Índice de proximidad ponderado
1. Conjuntos
Conjunto	Definición
I
I	Sitios candidatos para localización del datacenter, 
i
∈
I
i∈I
H
H	Bundles tecnológicos predefinidos de climatización, 
h
∈
H
=
{
H
R
A
D
,
H
E
C
O
,
H
H
Y
B
,
H
C
O
N
V
}
h∈H={H 
RAD
​
 ,H 
ECO
​
 ,H 
HYB
​
 ,H 
CONV
​
 }
J
=
J
S
∪
J
W
J=J 
S
​
 ∪J 
W
​
 	Plantas de generación renovable con registro de curtailment (solar 
J
S
J 
S
​
 , eólica 
J
W
J 
W
​
 ), 
j
∈
J
j∈J
Donde 
H
R
A
D
H 
RAD
​
  = enfriamiento radiativo puro (Aili), 
H
E
C
O
H 
ECO
​
  = economizador de aire / IEC (Silva-Llanca/Yang), 
H
H
Y
B
H 
HYB
​
  = bundle híbrido (radiativo + economizador, con respaldo mecánico residual), 
H
C
O
N
V
H 
CONV
​
  = chiller convencional sin economizador (línea base, Lei & Masanet Caso 5/8).

2. Parámetros
Climáticos y geográficos (por sitio 
i
i):

Parámetro	Descripción	Fuente/cálculo
R
H
i
RH 
i
​
 	Humedad relativa media anual (%)	Silva-Llanca (dataset 100 estaciones)
T
d
b
,
i
T 
db,i
​
 	Temperatura de bulbo seco media/diseño (°C)	Silva-Llanca
T
w
b
,
i
T 
wb,i
​
 	Temperatura de bulbo húmedo (°C)	Derivada (Stull, Ec. A56 de Aili) a partir de 
R
H
i
,
T
d
b
,
i
RH 
i
​
 ,T 
db,i
​
 
P
W
i
PW 
i
​
 	Agua precipitable (mm)	Derivada (Ec. A5 de Aili) a partir de 
R
H
i
,
T
d
b
,
i
,
p
a
m
b
,
i
RH 
i
​
 ,T 
db,i
​
 ,p 
amb,i
​
 
P
s
o
l
a
r
,
i
P 
solar,i
​
 	Irradiancia solar media/diseño (W/m²)	Gap — ver sección de brechas
V
w
i
n
d
,
i
V 
wind,i
​
 	Velocidad de viento media (m/s)	Gap — ver sección de brechas
d
c
o
a
s
t
,
i
d 
coast,i
​
 	Distancia a la costa (km)	Calculable de coordenadas
a
l
t
i
alt 
i
​
 	Altitud (m)	Calculable de coordenadas (afecta 
p
a
m
b
,
i
p 
amb,i
​
 )
H
i
m
i
x
e
d
H 
i
mixed
​
 	Fracción de horas anuales en modo mixto (respaldo mecánico)	Yang (Tabla 1, umbral 
T
w
b
>
19
°
C
T 
wb
​
 >19°C) — requiere serie horaria; gap parcial
l
a
t
i
,
l
o
n
i
lat 
i
​
 ,lon 
i
​
 	Coordenadas	Dato de localización
Tecnológicos (por bundle 
h
h, calibrados por sitio cuando aplica, i.e. 
W
U
E
i
h
,
P
U
E
i
h
WUE 
ih
​
 ,PUE 
ih
​
 ):

Parámetro	Descripción
W
U
E
i
h
WUE 
ih
​
 	Water Usage Effectiveness (L/kWh) del bundle 
h
h en el sitio 
i
i
P
U
E
i
h
PUE 
ih
​
 	Power Usage Effectiveness (kWh/kWh) del bundle 
h
h en el sitio 
i
i
C
A
P
E
X
h
CAPEX 
h
​
 	Costo de capital del bundle 
h
h (USD/kW) — gap, ver sección de brechas
Energéticos y de curtailment:

Parámetro	Descripción
C
j
C 
j
​
 	Curtailment acumulado de la planta 
j
j (MWh, 2022–abr.2026) — dataset Yakhchal
d
i
j
d 
ij
​
 	Distancia geodésica entre sitio 
i
i y planta 
j
j (km), vía Haversine sobre coordenadas
d
0
d 
0
​
 	Distancia característica de decaimiento de interconexión (km) — gap
L
L	Carga IT fija del datacenter (kW) — supuesto de diseño
p
e
n
e
r
g
y
p 
energy
​
 	Precio de la energía (USD/kWh) — gap si no se fija exógenamente
p
w
a
t
e
r
p 
water
​
 	Precio del agua (USD/m³) — gap si no se fija exógenamente
N
=
8760
N=8760	Horas por año
B
u
d
g
e
t
Budget	Presupuesto total de CAPEX disponible — gap, parámetro de diseño
P
P	Número de sitios a desarrollar
Derivados (calculados, no decisiones):

z
i
∈
{
0
,
1
}
:
indicador de screening clim
a
ˊ
tico aprobado en el sitio 
i
z 
i
​
 ∈{0,1}:indicador de screening clim 
a
ˊ
 tico aprobado en el sitio i
z
i
=
{
1
si 
R
H
i
,
T
d
b
,
i
,
T
w
b
,
i
,
P
W
i
,
d
c
o
a
s
t
,
i
 satisfacen umbrales m
ı
ˊ
nimos de factibilidad
0
en otro caso
z 
i
​
 ={ 
1
0
​
  
si RH 
i
​
 ,T 
db,i
​
 ,T 
wb,i
​
 ,PW 
i
​
 ,d 
coast,i
​
  satisfacen umbrales m 
ı
ˊ
 nimos de factibilidad
en otro caso
​
 
C
A
I
i
=
∑
j
∈
J
C
j
⋅
e
−
d
i
j
/
d
0
CAI 
i
​
 = 
j∈J
∑
​
 C 
j
​
 ⋅e 
−d 
ij
​
 /d 
0
​
 
 
W
i
h
=
W
U
E
i
h
⋅
L
⋅
N
1000
(m
3
/a
n
˜
o)
,
E
i
h
=
P
U
E
i
h
⋅
L
⋅
N
(kWh/a
n
˜
o)
W 
ih
​
 = 
1000
WUE 
ih
​
 ⋅L⋅N
​
 (m 
3
 /a 
n
˜
 o),E 
ih
​
 =PUE 
ih
​
 ⋅L⋅N(kWh/a 
n
˜
 o)
3. Variables de decisión
Variable	Tipo	Descripción
x
i
x 
i
​
 	Binaria	1 si se desarrolla un datacenter en el sitio 
i
i
y
i
h
y 
ih
​
 	Binaria	1 si el sitio 
i
i utiliza el bundle tecnológico 
h
h
No se incluyen variables continuas adicionales en esta versión del modelo (los flujos de agua/energía se obtienen como producto de parámetros precomputados por las variables binarias, manteniendo el modelo estrictamente lineal entero-mixto).

4. Función objetivo
Dado que se trata de un problema genuinamente multiobjetivo (costo, agua, sostenibilidad energética compiten entre sí), presento la escalarización por suma ponderada normalizada, dejando explícito que los pesos son una elección de modelado a explorar por análisis de sensibilidad — no un valor verdadero único:

min
⁡
x
,
y
α
∑
i
,
h
C
o
s
t
^
i
h
 
y
i
h
  
+
  
β
∑
i
,
h
W
^
i
h
 
y
i
h
  
−
  
γ
∑
i
C
A
I
^
i
 
x
i
x,y
min
​
 α 
i,h
∑
​
  
Cost
  
ih
​
 y 
ih
​
 +β 
i,h
∑
​
  
W
  
ih
​
 y 
ih
​
 −γ 
i
∑
​
  
CAI
  
i
​
 x 
i
​
 
donde:

C
o
s
t
i
h
=
C
A
P
E
X
h
+
p
e
n
e
r
g
y
⋅
E
i
h
+
p
w
a
t
e
r
⋅
W
i
h
Cost 
ih
​
 =CAPEX 
h
​
 +p 
energy
​
 ⋅E 
ih
​
 +p 
water
​
 ⋅W 
ih
​
 
y 
C
o
s
t
^
i
h
,
W
^
i
h
,
C
A
I
^
i
Cost
  
ih
​
 , 
W
  
ih
​
 , 
CAI
  
i
​
  son versiones normalizadas min-max (0–1) de 
C
o
s
t
i
h
Cost 
ih
​
 , 
W
i
h
W 
ih
​
  y 
C
A
I
i
CAI 
i
​
  respectivamente, sobre el conjunto de sitios candidatos factibles, para hacer comparables magnitudes con unidades distintas (USD, m³, MWh-proximidad).

α
,
β
,
γ
≥
0
α,β,γ≥0, 
α
+
β
+
γ
=
1
α+β+γ=1, son pesos de preferencia a explorar (recomiendo método ε-constraint o exploración de frontera de Pareto en lugar de fijar un único triplete, dado que no existe en la literatura revisada un criterio objetivo para ponderar costo vs. agua vs. sostenibilidad).

5. Restricciones
(R1) Asignación tecnológica única por sitio seleccionado:

∑
h
∈
H
y
i
h
=
x
i
∀
i
∈
I
h∈H
∑
​
 y 
ih
​
 =x 
i
​
 ∀i∈I
(R2) Consistencia (no se asigna tecnología sin seleccionar el sitio):

y
i
h
≤
x
i
∀
i
∈
I
,
h
∈
H
y 
ih
​
 ≤x 
i
​
 ∀i∈I,h∈H
(R3) Filtro de screening climático (Etapa 0 → Etapa 1):

x
i
≤
z
i
∀
i
∈
I
x 
i
​
 ≤z 
i
​
 ∀i∈I
(R4) Número de sitios a desarrollar:

∑
i
∈
I
x
i
=
P
i∈I
∑
​
 x 
i
​
 =P
(R5) Restricción presupuestaria:

∑
i
,
h
C
A
P
E
X
h
⋅
y
i
h
≤
B
u
d
g
e
t
i,h
∑
​
 CAPEX 
h
​
 ⋅y 
ih
​
 ≤Budget
(R6) Piso mínimo de alineación con sostenibilidad energética (opcional, activable según política de diseño):

∑
i
C
A
I
i
⋅
x
i
≥
C
A
I
m
i
n
i
∑
​
 CAI 
i
​
 ⋅x 
i
​
 ≥CAI 
min
 
(R7) Techo de uso de agua por sitio (si existieran derechos de agua limitantes — ver brechas):

∑
h
W
i
h
⋅
y
i
h
≤
W
i
m
a
x
∀
i
∈
I
h
∑
​
 W 
ih
​
 ⋅y 
ih
​
 ≤W 
i
max
​
 ∀i∈I
6. Dominio
x
i
∈
{
0
,
1
}
∀
i
∈
I
x 
i
​
 ∈{0,1}∀i∈I
y
i
h
∈
{
0
,
1
}
∀
i
∈
I
,
h
∈
H
y 
ih
​
 ∈{0,1}∀i∈I,h∈H
z
i
∈
{
0
,
1
}
,
  
C
A
I
i
≥
0
,
  
W
i
h
≥
0
,
  
E
i
h
≥
0
(par
a
ˊ
metros, no variables)
z 
i
​
 ∈{0,1},CAI 
i
​
 ≥0,W 
ih
​
 ≥0,E 
ih
​
 ≥0(par 
a
ˊ
 metros, no variables)
P
∈
Z
+
,
  
B
u
d
g
e
t
,
  
C
A
I
m
i
n
,
  
W
i
m
a
x
∈
R
+
(constantes de dise
n
˜
o)
P∈Z 
+
 ,Budget,CAI 
min
 ,W 
i
max
​
 ∈R 
+
 (constantes de dise 
n
˜
 o)
Esto define un MILP puro (binario en variables de decisión, lineal en restricciones y objetivo) bajo el supuesto de que 
W
U
E
i
h
,
P
U
E
i
h
,
C
A
I
i
,
z
i
WUE 
ih
​
 ,PUE 
ih
​
 ,CAI 
i
​
 ,z 
i
​
  son parámetros precomputados en la Etapa 0.

7. Brechas explícitas — datasets sin los cuales ciertas afirmaciones no se sostienen razonablemente
Organizo esto por claim afectada, no solo por dato faltante, para que quede claro qué específicamente queda sin respaldo si la brecha no se cierra.

Brecha 1 — Irradiancia solar y viento por sitio
Claim afectada: "El modelo puede calcular 
W
U
E
i
h
,
P
U
E
i
h
WUE 
ih
​
 ,PUE 
ih
​
  para el bundle radiativo en cualquier sitio del desierto chileno."
Por qué es crítica: el modelo de Aili requiere 
P
s
o
l
a
r
,
i
P 
solar,i
​
  y 
V
w
i
n
d
,
i
V 
wind,i
​
  como inputs directos del balance de radiación (Ec. 1, A11–A14). El dataset de Silva-Llanca, aunque cubre 100 estaciones chilenas, documenta explícitamente solo temperatura, humedad relativa y presión atmosférica (Sección 3.2 de ese paper) — no irradiancia ni viento. Sin esto, 
W
U
E
i
h
,
P
U
E
i
h
WUE 
ih
​
 ,PUE 
ih
​
  para 
H
R
A
D
H 
RAD
​
  y 
H
H
Y
B
H 
HYB
​
  son inestimables con los datos ya reunidos en este hilo.
Dataset necesario: Explorador Solar y Explorador Eólico del Ministerio de Energía de Chile, o reanálisis (CAMS, ERA5), por coordenada.

Brecha 2 — Series horarias (no solo promedios anuales)
Claim afectada: "El modelo distingue correctamente horas de modo seco/húmedo/mixto (Yang) y puede cruzarlas con disponibilidad horaria de curtailment."
Por qué es crítica: 
H
i
m
i
x
e
d
H 
i
mixed
​
  requiere clasificación hora por hora (Tabla 1 de Yang) sobre series de 
T
d
b
,
T
w
b
T 
db
​
 ,T 
wb
​
  reales, no solo promedios. De manera análoga, 
C
A
I
i
CAI 
i
​
  tal como está construido usa curtailment acumulado total, no horario — por lo que la hipótesis de antagonismo/sinergia temporal entre curtailment solar y desempeño de enfriamiento (planteada en el turno anterior) no puede confirmarse ni refutarse con los datos actuales.
Dataset necesario: series horarias completas (no solo agregados anuales) tanto climáticas como de curtailment por planta.

Brecha 3 — CAPEX por tecnología
Claim afectada: "El modelo optimiza bajo una restricción presupuestaria realista (R5) y puede comparar bundles en términos de costo total."
Por qué es crítica: ninguna de las cinco fuentes reporta costos de capital. Sin 
C
A
P
E
X
h
CAPEX 
h
​
 , la función objetivo y la restricción (R5) son estructuralmente correctas pero no ejecutables con valores numéricos reales — solo con supuestos no validados.
Dataset necesario: cotizaciones de proveedores, literatura de costos de sistemas de enfriamiento radiativo/IEC/economizador (escasa incluso a nivel internacional), o estudios de CAPEX de datacenters en Chile (CBRE, JLL, informes sectoriales).

Brecha 4 — Parámetro de decaimiento de interconexión (
d
0
d 
0
​
 ) y capacidad real de red
Claim afectada: "
C
A
I
i
CAI 
i
​
  representa oportunidad de interconexión realmente aprovechable, no solo proximidad geográfica."
Por qué es crítica: proximidad geodésica no equivale a capacidad de inyección/retiro disponible en la subestación más cercana. Sin datos de capacidad de transmisión y de la topología real de la red, 
C
A
I
i
CAI 
i
​
  es un proxy razonable pero no validado de factibilidad de interconexión.
Dataset necesario: datos de capacidad de subestaciones y líneas del Coordinador Eléctrico Nacional (planificación de transmisión, informes de capacidad disponible).

Brecha 5 — Derechos de agua y restricciones legales/hidrológicas
Claim afectada: "El modelo respeta límites reales de disponibilidad de agua por sitio (R7)."
Por qué es crítica: ninguna de las cinco fuentes aborda derechos de agua, restricciones ambientales o consulta indígena — factores determinantes en el norte de Chile (zona de alta sensibilidad hídrica y presencia de comunidades originarias). 
W
i
m
a
x
W 
i
max
​
  en (R7) no tiene fuente de datos en este momento.
Dataset necesario: Dirección General de Aguas (DGA) — catastro de derechos de agua y disponibilidad por cuenca/acuífero en las regiones de interés.

Brecha 6 — Validación empírica de enfriamiento radiativo en clima BWh/BWk
Claim afectada: "Los coeficientes 
W
U
E
i
h
,
P
U
E
i
h
WUE 
ih
​
 ,PUE 
ih
​
  del bundle radiativo son confiables para el desierto chileno."
Por qué es crítica: señalada repetidamente en este hilo — el modelo de Aili está validado solo para Singapur (tropical húmedo); su aplicación al desierto chileno es extrapolación física razonada, no validación empírica.
Dataset necesario: estudio piloto o datos de un sistema radiativo real operando en clima desértico (no existe, hasta donde sabemos, en la literatura revisada).

Brecha 7 — Modelo de consumo de agua para IEC
Claim afectada: "
W
U
E
i
h
WUE 
ih
​
  para el bundle 
H
E
C
O
H 
ECO
​
  incluye correctamente el consumo de agua del modo húmedo/mixto de IEC."
Por qué es crítica: señalada en el turno sobre Yang et al. — ese paper no reporta una métrica agregada de consumo de agua anual, solo ecuaciones de transferencia de calor/masa a nivel de intercambiador (Ec. 1–3), sin coeficientes de efectividad hídrica comparables a Aili o Silva-Llanca.
Dataset necesario: un modelo de balance de agua para IEC con el mismo nivel de detalle que Silva-Llanca (Ec. 5–8) o Lei & Masanet (Ec. 8), o datos de fabricante de intercambiadores IEC.

Brecha 8 — Permisos ambientales y uso de suelo
Claim afectada: "El conjunto de sitios candidatos 
I
I es realmente desarrollable."
Por qué es crítica: ninguna fuente revisada aborda áreas protegidas, SEIA (Sistema de Evaluación de Impacto Ambiental chileno), o restricciones de uso de suelo — factor de exclusión binaria potencialmente más determinante que el clima mismo en varias zonas del desierto.
Dataset necesario: capas SIG de áreas protegidas (SNASPE, sitios prioritarios), catastro de uso de suelo, y resultados de SEIA de proyectos similares en la zona.

Esta estructura — modelo formal completo + brechas explícitamente acotadas por claim — me parece coherente con tu objetivo declarado: es un ejercicio académico honesto que reconoce sus propios límites en lugar de simular una completitud que los datos disponibles no respaldan, dejando además un mapa de trabajo futuro claro y justificado punto por punto.

1783442312504_image.png
Puedes responder esta pregunta


Deliberó entre opciones de resolución temporal para datos solares
Deliberó entre opciones de resolución temporal para datos solares
Opción 2 — Todas las variables como medias mensuales.

Justificación directa desde las brechas que ya tenemos identificadas:

Cierra Gap 1 completamente. Para precomputar 
W
U
E
i
h
WUE 
ih
​
  y 
P
U
E
i
h
PUE 
ih
​
  del bundle radiativo (
H
R
A
D
H 
RAD
​
 ) en Etapa 0, el modelo de Aili requiere dos inputs que ninguna fuente actual cubre: 
P
s
o
l
a
r
,
i
P 
solar,i
​
  (cubierto por GHI/DNI) y 
V
w
i
n
d
,
i
V 
wind,i
​
  (cubierto por viento). La Opción 1 da GHI pero omite el viento — insuficiente para Aili (Ec. A13–A14). La Opción 2 cubre ambos.

Cierra Gap 2 parcialmente, que es lo razonable para un paper de curso. La resolución mensual permite estimar 
H
i
m
i
x
e
d
H 
i
mixed
​
  (fracción de horas en modo mixto, Yang) por distribución de probabilidad estacional, sin necesitar la serie horaria completa. Para un ejercicio académico, esto es defendible.

Opción 3 sería ideal para publicación, pero para el alcance actual es excesiva — la granularidad diaria no aporta diferencia material si los coeficientes del MILP son parámetros precomputados, no series temporales dentro del solver.

La fuente natural para este dataset es el Explorador Solar del Ministerio de Energía de Chile (explorer.minenergia.cl), que entrega exactamente GHI, DNI, temperatura, humedad y viento en resolución mensual por coordenada — coincide con la cobertura geográfica del dataset de curtailment que ya tienes.







Claude is AI and can make mistakes. Please double-check responses.







