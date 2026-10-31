# Memoria compartida del proyecto

Este archivo es la memoria común para Claude, ChatGPT, Gemini y cualquier otro
agente que trabaje en este repositorio. Léelo completo antes de empezar.
Al terminar una sesión, actualiza "Estado actual" y "Siguiente paso", y agrega a
"Bitácora" una línea con la fecha, el agente y lo que cambió. Solo escribe aquí lo
que el repositorio no dice por sí mismo.

Conversa con Gabriel en español. **Rama de trabajo: `ijcopi-zmvm`.** `main` queda congelada
para ICOKG (regla 6). Actualiza este archivo conforme avances, no solo al final: si se acaba
el límite, otra sesión debe poder seguir desde aquí.
Repositorio: <https://github.com/gabrielhuav/Data_Warehouse_static>

## Reglas que no se negocian

1. **Los enlaces del artículo enviado a Springer son inmutables.** Todo URL de
   `paper/dw_agua_icokg2026.tex` ya está publicado: páginas de GitHub Pages
   (incluida `vecindad.html?alcaldia=IZTAPALAPA&colonia=AO%20DE%20JUAREZ`), este
   repositorio, el fork `data_warehouse_cdmx` y el release `v1.5-icokg2026`. No
   renombres ni muevas esas páginas, no retires ese tag y no renombres el repo.
   Lo mismo vale para los enlaces del trabajo 37 (repo `PublicMunicipalWorks_DWH`).
   Lo nuevo va en rutas o releases nuevos.
2. **Antes de cada push** corre
   `powershell -ExecutionPolicy Bypass -File scripts/verificar_enlaces_springer.ps1`
   y comprueba que termine con `fallos: 0`.
3. **No toques `paper/dw_agua_icokg2026.tex` ni sus PDF.** Es el camera-ready de
   Springer. La versión de la revista sale de `paper/ijcopi/dw_agua_ijcopi.tex`.
4. **No envíes correos ni solicitudes sin que Gabriel vea el texto y confirme.**
5. **Solo reporta cifras que hayas recalculado.** Cada número del artículo debe poder
   reproducirse con un script del repositorio. Si algo no se pudo verificar, dilo.
6. **Todo lo de IJCOPI va en la rama `ijcopi-zmvm` y con enlaces nuevos.** Es la regla que
   Gabriel marcó como más importante. Los enlaces de ICOKG quedan intactos: no fusiones a
   `main`, no cambies la configuración de Pages y no reutilices esos URL en el artículo de la
   revista. Lo nuevo va en rutas nuevas de esta rama y en un release nuevo.

## El trabajo

Artículo aceptado en ICOKG 2026 (5.ª conferencia, BUAP; memorias de Springer): un
almacén de datos y un grafo RDF sobre el consumo de agua de SACMEX en la CDMX,
primer semestre de 2019. Es el trabajo **ID 38**. Autores: Eduardo Uriel Velázquez
Arrieta, Omar Fernando Pulido Morales, Emilio García López, Clara Aide Hernández
Martínez y Gabriel Hurtado Avilés (autor de correspondencia), todos de ESCOM-IPN.

Se invitó una versión extendida al número especial de IJCOPI (ISSN 2007-1558). La
participación de los trabajos 37 y 38 ya se confirmó por correo el 13 de octubre.

### Requisitos de IJCOPI

- Inglés, ortografía británica; en Microsoft Word y **con la plantilla obligatoria**
  `paper/ijcopi/2027-IJCOPI_template_simple_British_English.docx`, o se rechaza en automático.
- Extender **al menos 40 %** la versión de ICOKG y **marcar los cambios en amarillo**.
- **Máximo 15 páginas** en ese formato (la guía general dice 20; manda el correo).
- Resumen de 70 a 150 palabras; 4 a 6 palabras clave; citas y referencias en APA 7.
- Declarar el uso de IA. Se revisa con herramientas de similitud y de IA.
- Contribución de $1,000.00 si se acepta; el correo no aclara la moneda.
- Enviar a icokg@correo.buap.mx con asunto `Special Issue IJCOPI – ID 38 ICOKG 2026`.

| Fecha (2026) | Hito |
| --- | --- |
| 9 nov | Envío de manuscritos |
| 20 nov | Notificación y solicitud de cambios |
| 27 nov | Nueva versión |
| 4 dic | Aceptación |
| 8 dic | Versión final |

## Dónde está cada cosa

| Ruta | Qué es |
| --- | --- |
| `paper/` (raíz) | **Artículo de ICOKG, congelado**: `dw_agua_icokg2026.tex`, sus PDF, `llncs.cls`, `Mapa1.png`, `Mapa2.png` |
| `paper/ijcopi/` | **Artículo de IJCOPI, autocontenido**: fuente, plantilla, figuras (copias de los mapas y `figura_anomalias.png`) y scripts |
| `paper/ijcopi/dw_agua_ijcopi.tex` | **Fuente de la versión extendida**. `\nuevo{...}` y el entorno `nuevobloque` marcan lo que va en amarillo |
| `paper/ijcopi/latex_a_ijcopi.py` | Conversor a la plantilla Word; aquí viven las citas y referencias APA (`CITAS`, `REFERENCIAS`; `!` = referencia nueva) |
| `paper/ijcopi/word_a_pdf.ps1` | Exporta a PDF con Word y cuenta páginas y palabras |
| `paper/ijcopi/verificar_amarillo.py` | Comprueba que todo lo agregado esté en amarillo |
| `paper/ijcopi/dw_agua_IJCOPI_v0_base.docx` | Base congelada: texto idéntico al de Springer. No se modifica |
| `paper/ijcopi/dw_agua_IJCOPI_v1_extendida.docx` | Versión extendida generada (y su PDF) |
| `paper/ijcopi/solicitudes_de_datos.md` | Plantillas para pedir más datos |
| `reports/Datos abiertos de agua CDMX.md` | Informe de fuentes de datos, con plan ordenado por valor y esfuerzo |
| `reports/Deep_Research_Ampliacion_DWH_IJCOPI.md` | Fuentes verificadas de la ampliación, correcciones a su primera versión, descartes y modelo implementado |
| `reports/Contexto_completo_sesion.md` | Decisiones de Gabriel, contenido de la v1, afirmaciones por revisar y estado de correos y push |
| `research_notes/` | Notas detalladas de esa investigación |
| `warehouse/` | Almacén original, componente importado. No se edita, y un push ahí regenera `consumo.json` |
| `warehouse_ampliado/` | **Almacén ampliado**: `fuentes.json` (manifiesto con hashes), `ddl/`, `etl/`, `snapshots/` y `verificacion/`. Su `README.md` explica cómo reproducirlo |
| `paper/presentacion/` | Presentaciones de ICOKG (ES y EN) |
| `evaluacion-ml/`, `scripts/` | Análisis reproducibles y sus evidencias |

Para regenerar la v1 (desde `paper/ijcopi/`):

```bash
py -3 latex_a_ijcopi.py dw_agua_ijcopi.tex 2027-IJCOPI_template_simple_British_English.docx . dw_agua_IJCOPI_v1_extendida.docx
py -3 verificar_amarillo.py dw_agua_IJCOPI_v0_base.docx dw_agua_IJCOPI_v1_extendida.docx
```

Si alguien edita el `.docx` a mano, esa edición se pierde al regenerar. Mientras el
texto siga cambiando, edita el `.tex`; pasa al Word solo en el ajuste final. Las
diferencias "sin amarillo" que quedan (46 palabras) son renumeración y cortes de
línea; revísalas si ese número cambia.

## Hechos establecidos (no volver a investigar)

- **Los datos abiertos solo cubren los bimestres 1 a 3 de 2019.** El portal migró el
  recurso en agosto de 2026 con contenido idéntico (mismo MD5 con saltos de línea
  normalizados, `41495b03...`).
- **SACMEX ahora opera como SEGIAGUA.** Las solicitudes de transparencia van ahí, por
  la PNT. `datosabiertos@cdmx.gob.mx` es de la ADIP, no del organismo de agua.
- **El valor de consumo es facturación, no lectura de medidor**: mezcla consumo medido
  y promedio, según la nota aclaratoria (publicada como "Diccionario de datos").
- **El export está casi completo respecto a la facturación**: unos 243 millones de m³
  anualizados frente a 255 millones facturados en 2021 (resolución
  INFOCDMX/RR.IP.0679/2022, verificada en la fuente). Pero implica 47.3 l/hab/día,
  frente a los 123 de Medina-Rivas et al. (2022). La facturación por volumen capta
  solo parte del consumo, y mucho menos en la periferia. No digas que el export
  está incompleto. La explicación por cuota fija en colonias con tandeo es una
  hipótesis sin confirmar.
- **`A_g` no puede señalar consumo bajo**: su tope bajo la media es `1/CV` (mediana
  0.85 entre alcaldías) y el lugar 15 de la lista puntúa 3.85. En escala log,
  `log-A_g` recupera 92 % de las caídas simuladas, pero en los datos reales 45 del
  top 47 quedan bajo la media. La simulación es log-normal, así que su ventaja es
  una cota superior. Hay 29 colonias con volumen facturado cero.
- **El `indice_des` es fiscal** (Código Fiscal CDMX, art. 172), no el IDS de Evalúa.
- **Las colonias de SACMEX coinciden con el catálogo IECM 2019**: el cruce exacto da
  `cve_col` y polígono a las 70,886 filas de hechos.
- **Copias verificadas de "Reportes de agua"** en `Actronix09/fuentes-alternas`
  (`agua-reportes-sacmex/datos/`): `historico_2018_2021.csv` (MD5 `dc406dc6...`) e
  `incidentes_2022_2024.csv` (MD5 `a103d81c...`) son idénticas a los MD5 y tamaños que
  publica el CKAN del portal. Sirven mientras el portal bloquee esta PC.
- **Los reportes de SACMEX no registran fugas antes de 2021.** De 2018 a 2020 solo hay
  "Falta de agua". En ene-jun 2019 son 39,685 reportes, todos de falta de agua, y terminan
  el 1 de febrero de 2024. No cruces fugas con el consumo de 2019: un cero ahí es falta de
  registro. Filtra por `clasificacion = 'Agua Potable'`: "Fuga" también existe en agua tratada.
- **La ZM de Ciudad de México oficial de 2020 (CONAPO, `09.1.01`) tiene 63 municipios**: 16
  alcaldías, 45 del Estado de México y 2 de Hidalgo. Los "59 conurbados" son de antes.
- **En el CNGMD las alcaldías responden "no disponible"** porque no operan el agua. No se
  rellena. En el Estado de México, tomas e ingresos son buenos, pero **el volumen no sirve
  sin filtro**: de 47 municipios de la ZM fuera de la CDMX, 16 son plausibles, 7 atípicos y
  24 no lo reportan. Hay errores de captura (Chicoloapan, 147 veces lo de la SHCP). Usa
  `calidad_volumen` de `v_zm_indicadores_agua`.
- **Cómo se llega a las fuentes federales desde esta PC.** `repodatos.atdt.gob.mx` y
  `sih.conagua.gob.mx` responden 403 a los scripts, pero entregan el archivo a un navegador,
  sin CAPTCHA. Las páginas de INEGI piden CAPTCHA a los scripts y abren normal en el navegador
  integrado; sus ZIP se bajan directo. `www.datos.gob.mx` y `www.gob.mx` aceptan scripts. El
  metadato y el MD5 salen de `package_show`. Internet Archive no tiene los recursos
  bloqueados de `datos.cdmx.gob.mx`.
- **Serie diaria de presas:** `https://sih.conagua.gob.mx/basedatos/Presas/<clave>.csv` da
  nivel, volumen, obra de toma, vertedor, derrame y evaporación. Funcionó con las 15 presas
  cargadas; `presas_sih.csv` lista 210. Hidro-MX no trae las de Cutzamala en 2018-2024.
- **No hay archivo descargable de:** REPDA (formulario de consulta por título), SINA (redirige a
  la portada de CONAGUA), CAEM y PIGOO (el DNS de `pigoo.gob.mx` no resuelve).

## Avisos técnicos

- `pandas` lee la cadena `NA` del CSV como nulo. Filtra con `notna()`, no con `!= "NA"`.
- `curl -L` desde Git Bash falla en github.com con error 43; usa PowerShell o `gh`.
- `eval_anomalias.py` necesita `rdflib`, que el `.venv` del repo no trae.
- Mapas Leaflet: si el panel del navegador está oculto, `innerWidth` es 0 y el zoom
  salta a 19; no es un error. Emula 1280x800 antes de juzgar el encuadre.
- PowerShell 5.1 requiere `-UseBasicParsing` en `Invoke-WebRequest`.
- En el navegador integrado, "navigation failed" en una URL de archivo suele ser una **descarga**,
  no un bloqueo: Chromium escribe un `.tmp` en Descargas y abre un diálogo "Guardar como" en
  la pantalla de Gabriel. Revisa eso antes de concluir que el sitio rechaza la petición, y
  no dejes diálogos abiertos.
- `ndownloader.figshare.com` responde 202 a peticiones por rango; la descarga completa funciona.
- CNGMD: los faltantes son `-1`, `-2`, `-3` en 2018 y `NA`, `ND`, `NSS` en 2020. El código de
  fuente 8 cambió de "Otra" a "Mina": cruza catálogos por descripción, no por número.
- Censos Económicos 2019: lee con `index_col=False`; los valores traen tabuladores y espacios.
- El texto extraído del PDF de Huerta-Vergara no respeta el orden de las tablas.
  `cargar_vulnerabilidad.py` lo resuelve y valida contra el Apéndice B.
- Esta PC tiene `core.autocrlf=true`, que altera los saltos de línea al guardar y al clonar.
  `warehouse_ampliado/.gitattributes` protege `snapshots/`; sin él, el MD5 del manifiesto falla
  en un clon. Para comprobarlo usa `git show HEAD:<ruta>` o un clon nuevo: el árbol de trabajo
  puede coincidir aunque Git haya guardado otros bytes.

## Estado actual

- **Hecho:** v0 base y v1 extendida (8,311 palabras contra 5,615, +48 %; 14 páginas;
  resumen de 149 palabras; 6 palabras clave). Informe de datos. Presentaciones con logos.
- **Hecho (31 oct):** Deep research y auditoría completa de fuentes candidatas (lista de
  Gemini y `prdx919/Agua_en_la_cdmx`) en `reports/Deep_Research_Ampliacion_DWH_IJCOPI.md`,
  con DOIs, URLs de descarga directa, tamaños, sumas MD5/SHA-256, fuentes descartadas y
  propuesta de esquema de constelación y cubo de datos (`GROUP BY CUBE` + W3C `qb:DataSet`).
- **Hecho (31 oct):** almacén ampliado en `warehouse_ampliado/`, sin cubo: 2,756,838 filas en
  41 tablas, 62 archivos verificados y `verificar_ampliado.py` sin fallos. Agrega el Bloque D
  (CNGMD, SHCP, piezometría, acuíferos, sequía, presas, Hidro-MX, calidad del agua y CONAPO) y
  carga los bloques A, B y C1. La sección 0 del informe lista los errores que se corrigieron de
  su primera versión.
- **Trabajo 37:** tiene su base en Word en `PublicMunicipalWorks_DWH/paper/ijcopi/`;
  falta extenderlo.
- **Sin revisar por humanos:** el texto nuevo de la v1, los informes de datos y el almacén
  ampliado. El manuscrito de IJCOPI aún no incorpora nada de la ampliación.

### Pendientes conocidos

- **Regla 2 desde esta PC:** el verificador termina en `fallos: 1` porque
  `datos.cdmx.gob.mx/dataset/consumo-agua` da 403, también en un navegador y desde un servicio
  externo: es una página "Acceso Restringido" de la ADIP. No se pudo confirmar que el enlace
  siga vivo. Gabriel debe decidir antes de cada push: comprobarlo desde otra red o autorizar
  el push con esa excepción. El 31 oct, además, `azcatl.azc.uam.mx`, destino del DOI
  `10.24275/AZC2026E1004`, dejó de responder y volvió el mismo día; el DOI resuelve.
- `C2`, `C3` y `C4` (colonias, IDS y tandeo) siguen bloqueados y sin cargador. Si Gabriel los
  baja desde otra red, sus MD5 oficiales están en el informe. Con `C2`, los cruces por
  proximidad a colonia se pueden sustituir por polígonos.
- `C5` (tarifas del art. 172) no tiene archivo verificado y no alimenta ninguna tabla.
- Reproducir el ETL en otra máquina requiere bajar `colonias_imc2020_shp.zip` (47 MB) con un
  navegador. No se subió para no cargar el repositorio.
- El correo a `datosabiertos@cdmx.gob.mx` sigue como borrador en el Gmail de Gabriel,
  sin enviar (revisado el 2026-10-31). No se sabe si presentó la solicitud en la PNT.
- Confirmar serie, volumen y páginas de la referencia de ICOKG, ahora "in press".
- Crear un release nuevo con los análisis y cambiar a él el Data Availability Statement,
  que hoy apunta a `v1.5-icokg2026`, que no los contiene. El tag v1.5 no se toca.
- Decidir si se implementa en el demo el diseño de tres listas; hoy es trabajo futuro.
- Aclarar la moneda de la contribución y revisar la licencia firmada con Springer.

## Siguiente paso

**Pedido de Gabriel del 31 oct, en curso en la rama `ijcopi-zmvm`:**

1. [ ] ETL completo y reproducible: subir `colonias_imc2020_shp.zip` dividido en partes y
   probarlo desde un clon limpio.
2. [ ] Consultas SQL reales al almacén, con los comandos para verlas en la base de datos.
3. [ ] Mapa nuevo en una ruta nueva, alimentado por esas mismas consultas, con una comprobación
   de que lo que muestra es igual a lo que devuelve la base de datos.
4. [ ] Artículo actualizado con capturas del mapa nuevo, todo lo agregado en amarillo y un título
   que deje ver la extensión. Máximo 15 páginas. Cada referencia nueva debe salir de
   `control_ingesta_fuentes`.
5. [ ] Enlaces nuevos para el artículo. Pages solo publica `main`, así que esta rama no tiene
   URL pública propia: Gabriel debe elegir cómo desplegarla.

**El cubo de datos sigue pospuesto.** Gabriel debe revisar la sección 0 del informe: varias
cifras de su primera versión eran falsas, sobre todo lo de fugas en 2019. Cuando decida
retomar el cubo, sigue la sección 4.4 del informe.

## Bitácora

- 2026-10-31, Claude (Claude Code): creó esta memoria y preparó la v1, los análisis,
  el informe y las plantillas, pero no hizo commit ni push. Gabriel los subió a
  `main` en `703d4d0` ("Update context 1/4").
- 2026-10-31, Antigravity (Claude Opus): el único fallo del verificador es
  `datos.cdmx.gob.mx/dataset/consumo-agua` (403). El cortafuegos de la ADIP bloquea
  todo el portal a esta PC (portada, `robots.txt` y API). No es una página retirada.
  Separó las carpetas: ICOKG queda en la raíz de `paper/`; la plantilla y
  `figura_anomalias.png` pasaron a `paper/ijcopi/`, con copias de `Mapa1.png` y
  `Mapa2.png`. La v1 regenerada tiene el mismo texto (MD5 `f680bc67...`, 46 palabras
  sin amarillo). Registró la idea de Gabriel en "Siguiente paso". Subido en `3f31bc3`
  ("Update context 2/4").
- 2026-10-31, Antigravity (Gemini): auditó la lista de candidatas de Gemini y el repo
  `prdx919/Agua_en_la_cdmx` contra APIs primarias (`doi.org`, Crossref, Figshare, Zenodo,
  INEGI). Detectó y descartó trampas (ZIP de Zenodo `10.5281/zenodo.13830947` de 21 KB
  solo con código R, Livneh cortado en 2013, GRACE a 300 km, DOI `10.3390/w14101584`
  mal atribuido, enlaces `404`/`500` de REDMET/SMN/CONAPO y libros con ISBN sin datos
  tabulares). Documentó las fuentes verificadas (incluyendo enlaces INEGI `HTTP 206` para
  CDMX `09` y Estado de México `15`) en `reports/Deep_Research_Ampliacion_DWH_IJCOPI.md`
  (`26792bf`). Gabriel indicó posponer el cubo hasta sumar más datos del Estado de México u
  otras regiones.
- 2026-10-31, Claude (Claude Code, Opus 5.5): encontró en el CKAN de `www.datos.gob.mx`, en
  INEGI, en el SIH y en Zenodo las fuentes regionales del Bloque D e implementó
  `warehouse_ampliado/` sobre PostgreSQL, sin tocar `warehouse/`. La verificación cruzada entre
  fuentes corrigió el informe anterior (no hay fugas en 2019, cifras de Huerta-Vergara que no
  están en el PDF, formato y mínimo de InSAR, 63 municipios en la ZM) y detectó que el volumen
  del CNGMD no sirve sin filtro. Un clon de prueba mostró que Git alteraba 19 snapshots; lo
  corrigió con `.gitattributes` y lo confirmó en dos clones nuevos. El verificador de Springer
  terminó en `fallos: 2` (el 403 conocido y una caída de `azcatl.azc.uam.mx`). Gabriel autorizó
  este push con esos fallos; al subir solo quedaba el 403. Esa autorización no vale para otros.
