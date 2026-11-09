# Almacén ampliado de agua

Extiende el almacén de [`warehouse/`](../warehouse/) con fuentes hídricas de la Zona
Metropolitana de Ciudad de México, el Estado de México y el resto del país. Es aditivo:
no modifica ningún archivo de `warehouse/`, no toca `fact_consumo_agua` ni `fact_clima`, y
conserva todos los `id_tiempo` e `id_ubicacion` existentes. El cubo de datos queda para
después.

El informe de fuentes, con DOI, URL, hashes y descartes, está en
[`reports/Deep_Research_Ampliacion_DWH_IJCOPI.md`](../reports/Deep_Research_Ampliacion_DWH_IJCOPI.md).

## Reproducir

Hace falta Docker, Python 3.10 y unos 2 GB de disco. En Windows, clona en una ruta corta: con una
ruta muy larga, las DLL de `shapely` no cargan ("el nombre del archivo es demasiado largo"). Desde
la raíz del repositorio:

```bash
docker compose -f warehouse/compose.yml up -d --build
```

```bash
py -3 -m venv warehouse_ampliado/.venv
```

```bash
warehouse_ampliado/.venv/Scripts/python -m pip install -r warehouse_ampliado/requirements.txt
```

```bash
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/etl/descargar.py
```

```bash
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/etl/ejecutar.py
```

```bash
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/verificacion/verificar_ampliado.py
```

`descargar.py` deja los archivos en `datos_crudos/`, que no se sube al repositorio, y falla
si alguno no coincide con [`fuentes.json`](fuentes.json). No hace falta bajar nada a mano. Lo que
`repodatos.atdt.gob.mx` y `sih.conagua.gob.mx` rechazan a los programas ya viene en el repositorio:
los archivos pequeños en `snapshots/` y `colonias_imc2020_shp.zip` (47 MB) dividido en
`snapshots/partes/`. `descargar.py` une las partes y comprueba el MD5 y el SHA-256 del original.
El resto, unos 1.9 GB, baja por script desde su origen. `ejecutar.py` deja el almacén como
lo construye `warehouse/` y lo vuelve a extender, así que se puede repetir sin acumular datos.
Con `--pasos clima subsidencia` repite solo esos pasos. `verificar_ampliado.py` recalcula las
cifras y las escribe en [`verificacion/evidencia_ampliado.txt`](verificacion/evidencia_ampliado.txt).

`etl/partir.py D15 --mb 20` rehace las partes a partir del original verificado.

Las consultas al almacén, los comandos para verlas en la base de datos y cómo se publican en el mapa
están en [`consultas/README.md`](consultas/README.md).

## El grafo metropolitano

`grafo/mapeo_zm.r2rml.ttl` publica el almacén ampliado como grafo RDF, con el mismo motor R2RML del
grafo original. Enlaza con sus IRIs de alcaldía y colonia, así que los dos grafos se pueden unir. Usa
un entorno aparte, porque morph-kgc fija otras versiones de sus dependencias:

```bash
py -3 -m venv warehouse_ampliado/.venv_grafo
```

```bash
warehouse_ampliado/.venv_grafo/Scripts/python -m pip install -r warehouse_ampliado/grafo/requirements.txt
```

```bash
warehouse_ampliado/.venv_grafo/Scripts/python -I warehouse_ampliado/grafo/materializar.py
```

```bash
warehouse_ampliado/.venv_grafo/Scripts/python -I warehouse_ampliado/verificacion/verificar_grafo_zm.py
```

`verificar_grafo_zm.py` vuelve a materializar y compara, contrasta cada relación con su tabla y corre
las consultas de `grafo/consultas/`, las mismas que ofrece `ijcopi/grafo-zm.html`.

**Vecindad.** Las colonias usan `geo:sfTouches` estricto sobre los polígonos de CONAPO. Los municipios
no: los polígonos de INEGI se solapan hasta 0.49 m², la prueba estricta falla en pares que sí colindan
y solo 134 relaciones sobrevivían. Por eso usan `agua:sharesBoundaryWith`, una relación propia y
documentada: los polígonos se intersecan y comparten al menos 50 m de frontera.

**Lo que no hay.** Un `NULL` no produce tripleta. morph-kgc recibe los `NULL` como el texto `None`, y por
eso `materializar.py` lo declara nulo: sin eso aparecían 18,591 tripletas falsas.

## Qué garantiza el ETL

- **Todo dato viene de un archivo verificado.** Antes de leer una fuente, `comun.verificar()`
  compara tamaño, MD5 y SHA-256 con el manifiesto y, si el repositorio de origen publica un
  MD5, también con ese. Si algo no coincide, el paso se detiene.
- **No hay datos escritos a mano.** Las claves de alcaldía salen del cruce por nombre con el
  ITER, los catálogos salen de los archivos de INEGI, las categorías de sequía de la hoja
  `NOTAS` del propio XLSX y las cajas de Cutzamala y Lerma Alto de la configuración de Hidro-MX.
- **La procedencia se registra sola.** `control_ingesta_fuentes` la llena el ETL con el hash,
  la tabla destino y las filas cargadas. Ninguna fuente aparece ahí sin alimentar una tabla.
- **Los datos nuevos se cruzan con los originales.** `dim_ubicacion` gana `cve_mun`, que la une
  a `dim_municipio`; `dim_tiempo` crece con las fechas nuevas, con la misma regla de bimestre.

## Decisiones que conviene conocer

**Territorio.** La zona metropolitana es la delimitación oficial de 2020 de CONAPO, clave
`09.1.01`. Tiene 63 municipios: 16 alcaldías, 45 del Estado de México y 2 de Hidalgo. Los
"59 municipios conurbados" que suelen citarse vienen de una delimitación anterior.

**La CDMX y el Estado de México se miden distinto.** En el CNGMD las alcaldías responden "no
disponible" porque no operan el agua; lo hace SACMEX. Esos campos quedan vacíos y no se
rellenan. La CDMX tiene consumo por colonia de SACMEX y el Estado de México tiene datos por
municipio del CNGMD. `v_zm_indicadores_agua` los pone lado a lado y dice cuál usó cada fila.

**El volumen del CNGMD necesita filtro.** Un 0 suele significar "no reportó": Nezahualcóyotl tiene
211,749 tomas domésticas y ningún volumen. Otros valores son imposibles, de menos de 1 a casi 1,000
L/hab/día. Los datos crudos no se tocan; `calidad_volumen` en `v_zm_indicadores_agua` los clasifica en
`sin dato`, `atipico` y `plausible`, y `razon_ingreso_shcp` delata errores de captura como el de
Chicoloapan, 147 veces la recaudación de la SHCP. La banda de 10 a 400 L/hab/día es una decisión del
análisis para separar lo evidentemente mal reportado, no una medida de consumo.

**No hay fugas antes de 2021.** De 2018 a 2020 la fuente solo registra "Falta de agua". Un cero de
fugas en 2019 es ausencia de registro, no ausencia de fugas, y por eso `v_consumo_colonia_integrado`
las cuenta en 2021-2024. "Fuga" y "Falta de agua" también existen en agua tratada: para hablar de la
red potable hay que filtrar por `clasificacion = 'Agua Potable'`.

**Años.** El CNGMD 2019 refiere a 2018 y el de 2021 a 2020, y por eso `fact_agua_municipio` usa
esos años. El consumo de SACMEX es del primer semestre de 2019.

**Códigos especiales del CNGMD.** `-1`, `-2` y `-3` significan "no aplica", "no disponible" y
"no sabe" en 2018; en 2020 son `NA`, `ND` y `NSS`. Todos quedan `NULL`. El código 8 de fuente
cambió de "Otra" a "Mina", y por eso los catálogos se cruzan por descripción y no por número.

**Cruces por proximidad.** Los polígonos del IECM siguen bloqueados en el portal de la CDMX, y
las colonias de CONAPO no son las de SACMEX. Por eso cada manzana censal, establecimiento del
DENUE y píxel de InSAR se asigna al punto de consumo de SACMEX más cercano dentro de la misma
alcaldía, con distancia máxima. Es una aproximación, no una intersección de polígonos.

**Colonias CONAPO.** `dim_ubicacion.cve_col_conapo` elige el polígono con más puntos de cada
unidad SACMEX, si alcanza al menos la mitad. Un empate de votos se resuelve con la menor clave
numérica CONAPO; es una regla reproducible para un enlace aproximado, no una mayoría geográfica.
`enlace_conapo` distingue ese enlace del respaldo por nombre único. Los totales de cada unidad
SACMEX se enlazan enteros: no se recortan ni reparten sus registros según el polígono.

**Dos poblaciones en la capa CONAPO.** `v_colonia_conapo_contexto`, fuente común de SQL y RDF,
expone `pob_total` del polígono y `pob_sacmex`, la suma de población urbana asignada por proximidad
a sus unidades SACMEX enlazadas. Las tasas usan este segundo denominador y son proxies; no son
tasas de residentes del polígono. Los reportes se ubican por nombre o punto a menos de 1 km,
mientras que el censo usa puntos a 750 m dentro de la misma alcaldía. Cambiar el divisor a
`pob_total` no alinearía por sí solo esos soportes. `colonias_con_pob` y `colonias_con_dom` se
comparan con `colonias_sacmex`: si falta población positiva en alguna unidad, no se emiten tasas;
la tasa doméstica exige además un subtotal disponible por unidad. Esto no acredita cobertura
completa de cuentas, registros o bimestres. Un subtotal NULL se mantiene NULL y un cero conocido
se conserva como cero.

**Bases per cápita distintas.** La Tabla 4 usa volumen doméstico SACMEX de 2019 S1, los 181 días
observados y OCUPVIVPAR del Censo 2020. La vista municipal conserva su normalización anualizada
S1×2/365 y población CONAPO a mitad de 2019 (o volumen anual CNGMD de referencia 2018). La capa
de colonias usa 181 días y el soporte censal urbano aproximado descrito arriba. Cambian período,
población y grano; esos valores no son una única estimación intercambiable de consumo medido.

**Verificación de soportes.** `verificacion/test_soporte_colonias.py` ejecuta el fragmento SQL con
casos controlados de NULL, cobertura y empates. `verificacion/verificar_soporte_colonias.py` lee
PostgreSQL sin modificarlo y recalcula conteos y tasas en Python Decimal. El auditor
`verificacion/auditar_denominadores.py` reconstruye los cruces desde archivos crudos verificados,
sin base de datos; acepta `--datos-crudos` y una salida explícita. Para una base anterior al
desempate determinista, `etl/reconciliar_empates_conapo.py` muestra el plan en modo de lectura;
`--aplicar` actualiza en una transacción solo las claves CONAPO de las unidades empatadas. No
resembrar el almacén para esa corrección. Después deben regenerarse y comprobarse SQL/JSON y RDF.

```bash
warehouse_ampliado/.venv/Scripts/python -m unittest discover -s warehouse_ampliado/verificacion -p test_soporte_colonias.py
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/verificacion/verificar_soporte_colonias.py --salida warehouse_ampliado/verificacion/evidencia_soporte_colonias.json
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/verificacion/auditar_denominadores.py --salida warehouse_ampliado/verificacion/evidencia_denominadores.json
```

El auditor escribe también un CSV de unidades junto a la salida explícita; sirve para diagnóstico
y no es una entrada del almacén. El código de salida es 1 si el JSON publicado no coincide con la
reconstrucción. Las evidencias incluidas cotejan diez campos y comparten la huella canónica de
asignación poblacional `54be9c71f9559a6402081001a75044199b29cf9913aa4c6b38c4a05136fa38c3`:
JSON UTF-8 compacto de las filas `[alcaldia,colonia,poblacion_o_null]`, ordenadas por las etiquetas.
Esa huella compara población unidad por unidad entre los crudos y PostgreSQL, con independencia de
los identificadores internos o finales de línea. No es el SHA del archivo fuente ni de su exportación.

**Puente municipio-acuífero.** Es la intersección de los polígonos de INEGI y CONAGUA en la CDMX,
el Estado de México e Hidalgo. `pct_municipio` suma 100 % en los 225 municipios. Los polígonos de
acuíferos son simplificados, así que un porcentaje muy bajo puede ser solo una astilla del borde.

**Disponibilidad de acuíferos.** Es la del DOF del 9 de noviembre de 2023, según el nombre de la
capa. El archivo no trae unidades: las cifras se interpretan en hm³/año, como en la NOM-011.
Cumplen `VCAS + VEALA + VAPTYR + VAPRH = VEAS` y `R - DNC - VEAS = DMA`, y la verificación lo
comprueba en los 653 acuíferos.

**Presas.** Se cargan las series completas tal como vienen. En Madín y Taxhimay la relación entre
nivel y volumen cambia entre 2014 y 2019, lo que sugiere una curva de capacidad nueva, y hay dos
errores de captura de un día en el nivel. `evidencia_ampliado.txt` los lista.

**Calidad del agua.** Es un resumen por sitio de 2012 a 2025, no una serie anual. `limite` guarda
el signo de los valores fuera del límite de detección: no son mediciones exactas.

**Instantáneas.** Los archivos de `snapshots/` son copias congeladas de lo que el origen rechaza a
los scripts o actualiza a diario. Los que tienen `md5_oficial` coinciden con el MD5 del CKAN.

**DENUE.** Es la edición vigente al descargar, mayo de 2026, no 2019. Las columnas lo dicen.
