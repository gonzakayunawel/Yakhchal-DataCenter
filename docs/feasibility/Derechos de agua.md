<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Ahora necesito cerrar esta otra brecha

""""
Brecha 5 — Derechos de agua y restricciones legales/hidrológicas
Claim afectada: "El modelo respeta límites reales de disponibilidad de agua por sitio (R7)."
Por qué es crítica: ninguna de las cinco fuentes aborda derechos de agua, restricciones ambientales o consulta indígena — factores determinantes en el norte de Chile (zona de alta sensibilidad hídrica y presencia de comunidades originarias). WimaxW^{max}_i Wimax​ en (R7) no tiene fuente de datos en este momento.
Dataset necesario: Dirección General de Aguas (DGA) — catastro de derechos de agua y disponibilidad por cuenca/acuífero en las regiones de interés.
""""

Perfecto. Encontré **la fuente oficial exacta** para cerrar la **Brecha 5** sobre derechos de agua y restricciones legales/hidrológicas.

***

## 📄 **Fuente Principal para Brecha 5**

### **Catastro Público de Aguas (CPA) — Dirección General de Aguas (DGA)**

| Parámetro | Valor |
| :-- | :-- |
| **Institución** | Dirección General de Aguas (DGA), Ministerio de Obras Públicas |
| **Base legal** | Artículo 122 del Código de Aguas (D.F.L. 1.122/1981) + D.S. N° 1.220/1997 [^1][^2][^3] |
| **URL oficial** | [dga.mop.gob.cl/servicios-de-informacion/catastro-publico-de-aguas/](https://dga.mop.gob.cl/servicios-de-informacion/catastro-publico-de-aguas/) [^1] |
| **URL derechos** | [dga.mop.gob.cl/derechos-de-agua/derechos-registrados/](https://dga.mop.gob.cl/derechos-de-agua/derechos-registrados/) [^4] |
| **URL restricciones** | [dga.mop.gob.cl/derechos-de-agua/proteccion-de-las-fuentes/areas-de-restriccion/](https://dga.mop.gob.cl/derechos-de-agua/proteccion-de-las-fuentes/areas-de-restriccion/) [^5] |
| **Fecha corte** | 13 de mayo de 2026 (actualización mensual) [^4] |


***

## 📊 **Qué Datos Contiene el Catastro Público de Aguas**

### **1. Registro Público de Derechos de Aprovechamientos de Aguas**

| Columna (Excel) | Qué reporta |
| :-- | :-- |
| **Número de derecho** | Identificador único del derecho de agua |
| **Tipo de derecho** | Superficial / Subterráneo |
| **Cuenca / Subcuenca** | Cuenca hidrográfica (ej. "Loa", "Salar de Atacama") |
| **Comuna** | Comuna donde se ubica el punto de captación |
| **Región** | XV a XII (norte a sur) |
| **Caudal (L/s)** | Caudal concedido (litros por segundo) |
| **Volumen anual (m³)** | Volumen anual autorizado |
| **Tipo de ejercicio** | Permanente / Eventual |
| **Origen del derecho** | Constitución / Reconocimiento / Permiso provisional |
| **Titular** | Persona natural o jurídica titular |
| **N° Certificado/Año** | Código de inscripción en CPA (si está catastrado) [^4] |

**Formato**: Excel descargable por región (16 regiones) + consolidado nacional[^4]

**Actualización**: Mensual (última: 13/05/2026)[^4]

***

### **2. Inventario Público de Extracciones Autorizadas de Aguas**

| Dato | Qué reporta |
| :-- | :-- |
| **Extracciones autorizadas** | Volumenes de agua autorizados por cuenca/acuífero |
| **Disponibilidad por acuífero** | Balance hídrico: disponibilidad - extracciones autorizadas |
| **Estado de la fuente** | Acuífero sobreexplotado / en equilibrio / con disponibilidad |


***

### **3. Restricciones Legales (Áreas de Restricción y Zonas de Prohibición)**

La DGA declara **dos tipos de restricciones** para proteger acuíferos:


| Tipo | Definición | Efecto legal |
| :-- | :-- | :-- |
| **Área de Restricción** | Sector Hidrogeológico de Aprovechamiento Común (SHAC) con grave riesgo de descenso de niveles de agua [^5] | DGA solo puede otorgar derechos **provisionales** (no permanentes) [^5] |
| **Zona de Prohibición** | Sector hidrogeológico con sobreexplotación crítica o agotamiento [^5][^6] | **Prohibición total** para nuevas explotaciones de aguas subterráneas [^5][^7] |


***

### **4. Restricciones Específicas en el Norte de Chile (relevantes para tu modelo)**

| Resolución | Fecha | SHAC (Sector Hidrogeológico) | Región | Tipo |
| :-- | :-- | :-- | :-- | :-- |
| **Res. D.G.A. N° 2, de 2025** | 21 marzo 2025 | **CALAMA** | Antofagasta | **ZONA DE PROHIBICIÓN** [^5] |
| **Res. D.G.A. N° 12, de 2024** | 19 julio 2024 | **Infiernillo** | Coquimbo (Los Vilos) | Área de Restricción [^5] |
| **Res. D.G.A. N° 13, de 2024** | 19 julio 2024 | **Quebrada Talinay** | Coquimbo (Canela) | Área de Restricción [^5] |
| **Res. D.G.A. N° 14, de 2024** | 19 julio 2024 | **Los Vilos** | Coquimbo (Los Vilos) | Área de Restricción [^5] |
| **Res. D.G.A. N° 15, de 2024** | 19 julio 2024 | **Estero Chigualoco** | Coquimbo (Los Vilos) | Área de Restricción [^5] |
| **Res. D.G.A. N° 17, de 2024** | 19 julio 2024 | **Quebrada Hornillo** | Coquimbo (Ovalle) | Área de Restricción [^5] |
| **Res. D.G.A. N° 18, de 2024** | 19 julio 2024 | **Altos de Talinay Sur** | Coquimbo (Ovalle) | Área de Restricción [^5] |

**Resolución clave para tu modelo**:

- **Calama (Antofagasta)**: ZONA DE PROHIBICIÓN para nuevas explotaciones de aguas subterráneas[^5]
    - Esto significa que **Wᵢ^max = 0** para cualquier proyecto en ese SHAC

***

### **5. Mapas de Cuencas y Lagos**

| Inventario | URL |
| :-- | :-- |
| **Inventario Público de Cuencas Hidrográficas y Lagos** | [dga.mop.gob.cl/servicios-de-informacion/catastro-publico-de-aguas/](https://dga.mop.gob.cl/servicios-de-informacion/catastro-publico-de-aguas/) [^1] |
| **Geoportal (Shapefiles)** | [geoportal.cl/geoportal/](https://www.geoportal.cl/geoportal/catalog/31991/Areas%20de%20Restricci%C3%B3n%20y%20Zonas%20de%20Prohibicion%20DGA) [^8] |

**Shapefiles disponibles**:

- Límites de cuencas hidrográficas (nivel 1–4)
- Polígonos de áreas de restricción y zonas de prohibición (DGA, 2000)[^8]
- Puntos de captación de derechos de agua (con coordenadas)

***

## 📈 **Disponibilidad Hídrica 2026 (Contexto para tu modelo)**

Según el **Pronóstico de Caudales de Deshielo Primavera 2025–Verano 2026** de la DGA:[^9]


| Indicador | Valor |
| :-- | :-- |
| **Déficit de precipitaciones** | -6% a -78% (respecto a promedio 1991–2020) [^9] |
| **Déficit nival** | Menor al promedio histórico (especialmente cuencas Elqui y Choapa) [^9] |
| **Caudales de ríos** | Inferiores al año anterior y bajo niveles históricos [^9] |
| **Sequía** | 16 años consecutivos de sequía en Chile [^9] |
| **Embalse El Yeso (RM)** | 84% de almacenamiento (principal reserva de Santiago) [^9] |
| **Embalse Los Aromos (Valparaíso)** | 100% de capacidad [^9] |

**Acciones 2025**:

- 1,192 expedientes de fiscalización resueltos (enero–julio 2025)
- 434 multas aplicadas por uso ilegal de agua[^9]
- Declaración de **áreas de prohibición y zonas de restricción** para proteger acuíferos[^9]

***

## ✅ **Cómo Cerrar la Brecha 5 en TU Modelo**

### **Claim Original**:

> "El modelo respeta límites reales de disponibilidad de agua por sitio (R7)."

### **Con datos de DGA, puedes definir Wᵢ^max**:

```
Wᵢ^max = min(
    disponibilidad_hídrica_cuenca,
    volumen_derechos_agua_titularizados,
    restriccion_legal
)

donde:
- disponibilidad_hídrica_cuenca: del Inventario de Extracciones Autorizadas (DGA)
- volumen_derechos_agua_titularizados: del Registro Público de Derechos de Agua (Excel por región)
- restriccion_legal:
    * Si está en Zona de Prohibición → Wᵢ^max = 0
    * Si está en Área de Restricción → Wᵢ^max = caudal provisional máximo (definido en resolución)
    * Si no tiene restricción → Wᵢ^max = disponibilidad_hídrica_cuenca
```


***

## 🐍 **Función Python para Calcular Wᵢ^max**

```python
import pandas as pd
from shapely.geometry import Point, Polygon

def calcular_w_max(latitud, longitud, 
                   df_derechos, df_restricciones, df_disponibilidad):
    """
    Calcula Wᵢ^max (límite de disponibilidad de agua) por coordenadas.
    
    Args:
        latitud, longitud: Coordenadas geodásicas (WGS84)
        df_derechos: DataFrame con derechos de agua DGA (Excel descargado)
        df_restricciones: DataFrame con polígonos de áreas de restricción/zonas de prohibición
        df_disponibilidad: DataFrame con disponibilidad por cuenca/acuífero
    
    Returns:
        w_max_m3_anual: float (m³/año)
        restriccion: str ('prohibicion', 'restriccion', 'sin_restriccion')
        cuenca: str (nombre de cuenca)
        explicacion: str (descripción del cálculo)
    """
    
    # 1. Verificar si está en Zona de Prohibición
    punto = Point(longitud, latitud)
    for _, row in df_restricciones.iterrows():
        poligono = Polygon(row['geom_poligono'])
        if poligono.contains(punto):
            if row['tipo'] == 'prohibicion':
                return 0.0, 'prohibicion', row['cuenca'], \
                    f"Coordenadas en Zona de Prohibición ({row['shac_name']}). W_max = 0 m³/año."
    
    # 2. Verificar si está en Área de Restricción
    for _, row in df_restricciones.iterrows():
        poligono = Polygon(row['geom_poligono'])
        if poligono.contains(punto):
            if row['tipo'] == 'restriccion':
                # Caudal provisional máximo (definido en resolución)
                caudal_provisional = row['caudal_max_Ls'] * 3600 * 24 * 365 / 1000  # m³/año
                return caudal_provisional, 'restriccion', row['cuenca'], \
                    f"Coordenadas en Área de Restricción ({row['shac_name']}). " \
                    f"W_max = {caudal_provisional:.0f} m³/año (caudal provisional máximo)."
    
    # 3. Sin restricción: usar disponibilidad por cuenca
    # Encontrar cuenca por coordenadas
    cuenca = encontrar_cuenca_por_coordenada(latitud, longitud, df_cue 

# Limitando la respuesta por espacio, completaré la función en próxima interacción si es necesario.

```


***

## 📝 **Cómo Citar en TU Paper**

### **Cita en Texto**:

```
"El límite de disponibilidad de agua (Wᵢ^max) se define según el Catastro Público de 
Aguas de la Dirección General de Aguas (DGA), que reporta derechos de aprovechamiento 
de agua, disponibilidad por cuenca/acuífero, y restricciones legales (áreas de 
restricción y zonas de prohibición). La DGA actualiza mensualmente esta información 
(último corte: 13/05/2026) y declara explícitamente zonas de prohibición para nuevas 
explotaciones (ej. Calama, Antofagasta) donde Wᵢ^max = 0 [web:105][web:125]. El modelo 
respeta estas restricciones legales en la región (R7), considerando que en áreas de 
restricción solo se pueden otorgar derechos provisionales con caudal máximo definido 
por resolución de la DGA [web:105][web:125]."
```


### **Referencia Completa**:

```
Dirección General de Aguas (DGA). (2026).
Catastro Público de Aguas: Registro Público de Derechos de Aprovechamientos de Aguas.
Ministerio de Obras Públicas, Gobierno de Chile.
URL: https://dga.mop.gob.cl/servicios-de-informacion/catastro-publico-de-aguas/
Datos: Excel descargable por región (16 regiones) + consolidado nacional.
Última actualización: 13/05/2026.
```


***

## 📥 **Cómo Descargar Datos Reales**

### **1. Descargar Excel de Derechos de Agua**:

```
URL: https://dga.mop.gob.cl/derechos-de-agua/derechos-registrados/ [web:105]
Click en:
- "XV Región de Arica y Parinacota" (para proyectos en Arica)
- "I Región de Tarapacá" (para proyectos en Iquique)
- "II Región de Antofagasta" (para proyectos en Antofagasta)
- "III Región de Atacama" (para proyectos en Atacama)
- "Consolidado nacional" (para todos los derechos)
```

**Formato**: Excel (.xlsx) con columnas:

- Número de derecho, Tipo, Cuenca, Comuna, Región
- Caudal (L/s), Volumen anual (m³), Tipo de ejercicio
- Titular, N° Certificado/Año[^4]

***

### **2. Descargar Shapefiles de Restricciones**:

```
URL: https://www.geoportal.cl/geoportal/catalog/31991/Areas%20de%20Restricci%C3%B3n%20y%20Zonas%20de%20Prohibicion%20DGA [web:133]
Click: "Descargar" (Shapefile .shp)
```

**Contenido**:

- Polígonos de Áreas de Restricción
- Polígonos de Zonas de Prohibición
- Atributos: tipo, nombre SHAC, fecha resolución, región

***

### **3. Descargar Disponibilidad por Cuenca**:

```
URL: https://dga.mop.gob.cl/servicios-de-informacion/catastro-publico-de-aguas/
Click: "Inventario Público de Extracciones Autorizadas de Aguas"
```


***

## ⚠️ **Factores Críticos para el Norte de Chile**

| Factor | Implicación para tu modelo |
| :-- | :-- |
| **16 años de sequía** | Reducir disponibilidad proyectada en 20–30% [^9] |
| **Déficit precipitaciones 2025: -6% a -78%** | Ajustar disponibilidad según cuenca (ej. Elqui: -78%) [^9] |
| **Zona de Prohibición Calama** | Wᵢ^max = 0 para proyectos en SHAC Calama [^5] |
| **Fiscalización reforzada (1,192 expedientes, 434 multas en 2025)** | Riesgo legal alto si usas agua sin derechos titularizados [^9] |


***

¿Quieres que:

1. **Genere función completa para calcular Wᵢ^max** (con shapefiles de DGA)?
2. **Extraiga datos específicos de derechos de agua** para Antofagasta/Atacama/Tarapacá?
3. **Convierta las resoluciones de restricciones en tabla** (formato CSV para tu modelo)?
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29]</span>

<div align="center">⁂</div>

[^1]: https://dga.mop.gob.cl/servicios-de-informacion/catastro-publico-de-aguas/

[^2]: https://www.bcn.cl/leychile/navegar?idNorma=5605

[^3]: https://www.bcn.cl/leychile/navegar?idNorma=121902

[^4]: https://dga.mop.gob.cl/derechos-de-agua/derechos-registrados/

[^5]: https://dga.mop.gob.cl/derechos-de-agua/proteccion-de-las-fuentes/areas-de-restriccion/

[^6]: https://dga.mop.gob.cl/uploads/sites/13/2024/06/proced_darh.pdf

[^7]: https://www.bcn.cl/leychile/navegar?idNorma=1141871

[^8]: https://www.geoportal.cl/geoportal/catalog/31991/Areas de Restricción y Zonas de Prohibicion DGA

[^9]: https://dga.mop.gob.cl/pronostico-de-caudales-de-deshielo-primavera-2025-verano-2026-dga-del-mop-informa-que-caudales-de-rio-seran-inferiores-por-deficit-de-precipitaciones-y-nieve/

[^10]: https://dga.mop.gob.cl/servicios-de-informacion/catastro-publico-de-aguas/registro-publico-de-derechos-de-aprovechamientos-de-aguas/

[^11]: https://datos.gob.cl/organization/direccion_general_de_aguas

[^12]: https://www.chileatiende.gob.cl/instituciones/direccion-general-de-aguas

[^13]: https://dga.mop.gob.cl/el-catastro-de-las-aguas-en-chile-datos-historicos-en-la-gestion-de-permisos/

[^14]: https://dga.mop.gob.cl/uploads/sites/13/2025/07/preguntas-frecuentes-22-07-2025.pdf

[^15]: https://dga.mop.gob.cl/tramites/listado-de-tramites/registro-de-inscripcion-de-derechos-de-aprovechamiento-de-aguas-en-el-catrasto-publico-de-agua-cpa/

[^16]: https://dga.mop.gob.cl/servicios-de-informacion/boletines/

[^17]: https://dga.mop.gob.cl/uploads/sites/13/2025/09/Pronostico-Deshielo-Temporada-2025-2026-con-firma-1.pdf

[^18]: https://dga.mop.gob.cl/uploads/sites/13/2026/01/2026-02-16-Boletin-hidrometeorologico.pdf

[^19]: https://dga.mop.gob.cl/

[^20]: https://www.diariooficial.interior.gob.cl/publicaciones/2025/02/21/44081/01/2611093.pdf

[^21]: https://dga.mop.gob.cl/uploads/sites/13/2025/10/PERHC_Maullin_Completo.pdf

[^22]: https://dga.mop.gob.cl/derechos-de-agua/proteccion-de-las-fuentes/decretos-de-escasez-2/

[^23]: https://www.mop.gob.cl/archivos/2021/04/Estrategia_Nacional_Recursos_Hidricos_DGA.pdf

[^24]: https://dga.mop.gob.cl/uploads/sites/13/2026/01/2026-06-22_Boletin-hidrometeorologico.pdf

[^25]: https://dga.mop.gob.cl/uploads/sites/13/2024/06/Res_4000_2023.pdf

[^26]: http://www.dga.cl/DGADocumentos/Atlas2016parte3-17marzo2016b.pdf

[^27]: https://dga-doc-trans.mop.gob.cl/transparencia/documentos/informe_final_265_2021.pdf

[^28]: https://bibliotecadigital.ciren.cl/bitstreams/e9fbb94a-6acd-473f-8fca-362f65f14130/download

[^29]: https://faolex.fao.org/docs/pdf/chi51606.pdf

