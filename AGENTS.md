# Memoria compartida del proyecto

Este archivo es la memoria común para Claude, ChatGPT, Gemini y cualquier otro
agente que trabaje en este repositorio. Léelo completo antes de empezar.
Al terminar una sesión, actualiza "Estado actual" y "Siguiente paso", y agrega a
"Bitácora" una línea con la fecha, el agente y lo que cambió. Solo escribe aquí lo
que el repositorio no dice por sí mismo.

Conversa con Gabriel en español. **Rama de trabajo: `ijcopi-zmvm`.** `main` queda congelada
para ICOKG (regla 6). Actualiza este archivo conforme avances, no solo al final: si se acaba
el límite, otra sesión debe poder seguir desde aquí.
Repositorio de trabajo: <https://github.com/gabrielhuav/Data_Warehouse_static>
Versión extendida publicada: <https://github.com/gabrielhuav/Data_Warehouse_ZMVM>, con el mapa en
<https://gabrielhuav.github.io/Data_Warehouse_ZMVM/ijcopi/mapa-zm.html>

Los dos repositorios son públicos: no escribas aquí enlaces a correos, borradores ni datos personales.

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
   revista. Lo nuevo va en rutas nuevas de esta rama y se publica en `Data_Warehouse_ZMVM`.

## El trabajo

Artículo aceptado en ICOKG 2026 (5.ª conferencia, BUAP; memorias de Springer): un
almacén de datos y un grafo RDF sobre el consumo de agua de SACMEX en la CDMX,
primer semestre de 2019. Es el trabajo **ID 38**. Autores: Eduardo Uriel Velázquez
Arrieta, Omar Fernando Pulido Morales, Emilio García López, Clara Aide Hernández
Martínez y Gabriel Hurtado Avilés (autor de correspondencia), todos de ESCOM-IPN. En la versión
de IJCOPI, por decisión de Gabriel, él firma primero y sigue como autor de correspondencia; el
último es el Dr. Roberto Eswart Zagal Flores (ESCOM-IPN, `rzagalf@ipn.mx`, ORCID
0000-0001-5649-6189), por instrucción del 9 nov. Entre Gabriel y él se conserva el
orden Eduardo, Omar, Emilio y Clara. El orden de Springer no cambia.

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
| `paper/ijcopi/dw_agua_IJCOPI_v1_extendida.docx` | Primera versión extendida, sin la ampliación regional (y su PDF) |
| `paper/ijcopi/dw_agua_IJCOPI_v2_zmvm.docx` | Ampliación metropolitana sin el grafo (y su PDF). Gabriel la tenía abierta en Word el 31 oct, por eso no se sobrescribió |
| `paper/ijcopi/dw_agua_IJCOPI_v3_grafo.docx` | **Versión actual para enviar** (y su PDF): agrega el grafo metropolitano y la aclaración del color |
| `paper/ijcopi/capturar_mapa.ps1` | Genera las figuras del artículo desde el mapa real, con Edge sin ventana |
| `paper/ijcopi/solicitudes_de_datos.md` | Plantillas para pedir más datos |
| `reports/Datos abiertos de agua CDMX.md` | Informe de fuentes de datos, con plan ordenado por valor y esfuerzo |
| `reports/Deep_Research_Ampliacion_DWH_IJCOPI.md` | Fuentes verificadas de la ampliación, correcciones a su primera versión, descartes y modelo implementado |
| `reports/Contexto_completo_sesion.md` | Decisiones de Gabriel, contenido de la v1, afirmaciones por revisar y estado de correos y push |
| `reports/Prompts_otras_sesiones.md` | Prompts listos para el trabajo 37 y para el artículo de sismos, que se trabajan en otros repositorios |
| `research_notes/` | Notas detalladas de esa investigación |
| `warehouse/` | Almacén original, componente importado. No se edita, y un push ahí regenera `consumo.json` |
| `warehouse_ampliado/` | **Almacén ampliado**: `fuentes.json` (manifiesto con hashes), `ddl/`, `etl/`, `snapshots/` y `verificacion/`. Su `README.md` explica cómo reproducirlo |
| `warehouse_ampliado/consultas/` | Las 15 consultas SQL del mapa y del artículo. Su `README.md` trae los comandos para verlas en la base de datos |
| `warehouse_ampliado/grafo/` | **Grafo metropolitano**: mapeo R2RML, vocabulario, `materializar.py`, consultas `.rq` y `requirements.txt` propio |
| `ijcopi/` | **Mapa nuevo** (`mapa-zm.html`), **grafo** (`grafo-zm.html`, `kg_zm.ttl`), consultas (`consultas.html`) y sus datos (`datos/`, generados, no se editan a mano). No toca las páginas de ICOKG |
| `ijcopi/publicar.ps1`, `ijcopi/README_publico.md`, `ijcopi/ajustes_publicos.py` | Preparan la copia que va a `Data_Warehouse_ZMVM`: sin memoria de trabajo, sin manuscrito y sin el workflow de `main`. Los ajustes dan al sitio su marca metropolitana y portada, y solo tocan la copia: en la rama, `assets/` y las páginas siguen iguales a `main` |
| `paper/presentacion/` | Presentaciones de ICOKG (ES y EN) |
| `evaluacion-ml/`, `scripts/` | Análisis reproducibles y sus evidencias |

Para regenerar la v3 (desde `paper/ijcopi/`):

```bash
py -3 latex_a_ijcopi.py dw_agua_ijcopi.tex 2027-IJCOPI_template_simple_British_English.docx . dw_agua_IJCOPI_v3_grafo.docx
py -3 verificar_amarillo.py dw_agua_IJCOPI_v0_base.docx dw_agua_IJCOPI_v3_grafo.docx
```

Si alguien edita el `.docx` a mano, esa edición se pierde al regenerar. Mientras el
texto siga cambiando, edita el `.tex`; pasa al Word solo en el ajuste final. Las
diferencias "sin amarillo" que quedan (62 palabras) son renumeración, cortes de línea y el
reordenamiento de autores; revísalas si ese número cambia. La v3 ocupa las 15 páginas: cualquier
figura nueva debe sustituir a otra. Una imagen no admite resaltado: las figuras nuevas
llevan un marco amarillo, que pone `recuadro()` en el conversor.

Para actualizar el mapa después de cambiar datos o consultas (desde la raíz):

```bash
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/etl/exportar_mapa.py
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/verificacion/verificar_mapa.py
```

Para publicar esos cambios, primero haz commit en la rama. Esto prepara la copia en `%TEMP%\zmvm`
sin subir nada; después se revisa, se hace commit y se sube desde esa carpeta:

```bash
powershell -ExecutionPolicy Bypass -File ijcopi/publicar.ps1
```

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
- **El ETL se reproduce desde un clon limpio.** El 31 oct, un clon con entorno nuevo bajó los
  1,997.6 MB en 11.5 minutos, sin fallos, y el almacén reconstruido aparte devolvió las 13
  consultas con los mismos SHA-256 (`verificacion/evidencia_clon_limpio.txt`).
- **GitHub Pages solo publica `main`** (`build_type: legacy`, raíz). Una rama nueva da enlaces de
  código, pero no una página pública. Cambiar eso tocaría el sitio de ICOKG. Por eso, con el visto
  bueno de Gabriel, la versión extendida se publica en el repositorio `Data_Warehouse_ZMVM`.
- **Autores en IJCOPI (revisado el 31 oct en sus páginas de envíos y de ética).** No fija límite ni
  reglas para agregar autores o cambiar su orden, y dice seguir a COPE. Su número actual (vol. 18,
  núm. 1) tiene 28 artículos, con 3 a 7 autores; lo más frecuente son 6. COPE pide que todos los
  autores acepten por escrito. El correo de invitación no menciona autores nuevos: conviene
  confirmarlo con `icokg@correo.buap.mx` antes de enviar.
- **La IA debe declararse.** IJCOPI pide declararla siempre que se use para redactar, editar,
  traducir, resumir o apoyar el análisis, y advierte: "Failure to disclose relevant AI use may
  result in rejection or retraction". La declaración de la v2 ya es breve, pero conserva lo
  esencial, y no puede decir menos que la de Springer, que ya menciona redacción y scripts.
- **Vecindad municipal.** Los polígonos de INEGI se solapan hasta 0.49 m², así que `touches` estricto
  deja a Iztapalapa sin vecinos. El grafo usa `agua:sharesBoundaryWith` (al menos 50 m de frontera),
  no `geo:sfTouches`. En colonias de CONAPO, `geo:sfTouches` sí es estricto: 15,510 pares.
- **El color del mapa no mide quién consume más.** Lo dijo Gabriel y el mapa lo aclara. Ordena valores
  disponibles por quintiles, y cada capa dice cuántas unidades tienen dato.
- **Facturar poco no significa demandar poco.** Las 435 colonias bajo 10 l/hab/día reportan 4.15
  faltas de agua por mil habitantes, contra 4.93 del resto; Spearman de volumen contra reportes
  0.18 (`11_cruces_colonia.sql`, confirmado con scipy).
- **Trabajos del grupo del Dr. Zagal, leídos solo en resumen (el texto completo es de pago).**
  Hernández-Vázquez et al. (W2GIS 2025, LNCS 15946) funde SACMEX, INEGI y DENUE en un SIG con una
  arquitectura por capas. Daowz Laguna et al. (W2GIS 2026, LNCS 17231, en línea el 18 oct) analiza
  fugas de 2018 a 2024 con LLM y fuentes web. Su autor es Erwin Enrique Daowz Laguna según su
  ORCID; Springer lo publicó invertido ("Enrique, D. L. E."), y aquí se cita con el nombre correcto.
  Ese resumen habla de fugas desde 2018, pero los CSV públicos no traen ninguna en 2018-2020: la
  primera es del 1 de enero de 2021 (recalculado el 1 nov). No se sabe cómo lo resuelve ese trabajo.

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
- morph-kgc entrega los `NULL` como el texto `None`. `materializar.py` lo declara en `na_values`; sin
  eso salen 18,591 tripletas falsas, incluidos enlaces a `municipio/None`.
- En el navegador, Comunica se vuelve lento al unir predicados con miles de tripletas. Para eso están
  `agua:touchesAcrossCityLimit` y `agua:inMunicipality`. Mide cada `.rq` nuevo en `grafo-zm.html`.
- Si `paper/ijcopi/` tiene un archivo `~$...`, Word tiene ese `.docx` abierto: no lo sobrescribas.
- Recortar texto antes de una figura puede no liberar nada: Word deja el espacio como hueco al pie
  de la página anterior. Mide dónde termina cada página antes de cortar; mover una figura un
  párrafo puede ahorrar más que quitar texto.
- Clona en una ruta corta: con una ruta muy larga, como el scratchpad de una sesión, las DLL de
  `shapely` no cargan en Windows.
- `docker cp warehouse_ampliado/consultas/. data_warehouse_cdmx:/consultas` lleva `/.` a propósito:
  sin eso, la segunda vez crea `/consultas/consultas` y psql sigue leyendo la versión vieja.
- Docker puede reiniciarse y dejar `data_warehouse_cdmx` apagado. Los datos siguen en el volumen
  `warehouse_pgdata`: basta con `docker start data_warehouse_cdmx`.
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

- 9 nov, cierre Git autorizado por Gabriel: un commit/push en ijcopi-zmvm y otro en
  el repo IJCOPI/main, identidad humana sin firmas ni créditos automáticos. Ejecutar
  verificador Springer intacto antes de cada push y detenerse si hay fallos. Primera
  ejecución de este cierre: 25 enlaces, 0 fallos; ADIP y AZCATL 200. Implementación web
  y QA confirmadas en IJCOPI; no incluye envío, correo, release ni sitios históricos.

- 9 nov, petición vigente de Gabriel: Roberto pasa al último lugar en IJCOPI,
  conservando Gabriel primero/correspondencia y datos de identificación. Fuente y
  conversor corregidos; v3 Word/PDF regenerados y copia Word sincronizada al repo IJCOPI.
  Word: 15 páginas/9,043 palabras, v0 medida 5,615 (+61.0507569 %). Páginas inspeccionadas;
  solo autoría, 5.8 y trabajo futuro cambian, cuerpo nuevo todo amarillo; título, tablas,
  imágenes, declaración de IA y v0 preservados. Trabajo futuro: ampliar población,
  densidad, usos del suelo y acceso al servicio para contextualizar facturación.
  Word SHA-256 86f7ea1fbc627ad0ab0ea4036f93b9399b55419abce963eb8d028b271081fac9;
  PDF bb59ccc1d85c352cec73f89e5c94430f5bc123f82ea24143a7fa86a8707bda03.
  Clon actual `C:/dev/Data_Warehouse_static`, ijcopi-zmvm, HEAD 967b9f9b; el viejo
  main de Descargas no se modificó. Web con expansión/distancias se edita solo en
  Data_Warehouse_IJCOPI. La autorización posterior de cierre Git se registra arriba.

- Revisión posterior al informe independiente del 9 nov: corregidos los hallazgos
  contrastados con fuentes y datos; descartadas cifras y autorías ajenas a esta versión.
  Word/PDF regenerados desde fuente: 15 páginas, 9,029 palabras, v0 5,615 (+60.8014 %),
  resumen 144 y seis keywords. Las quince páginas se inspeccionaron a 150 dpi; cero
  palabras nuevas sin amarillo frente al respaldo de 9,116 palabras. Título, autores,
  declaración académica de IA, figuras, plantilla y v0 preservados.
  Word SHA-256 d38e1e48c1741dcf80f3f58f8d62828bfed7089a2a581d4b345f6eeb93ff771e;
  PDF SHA-256 416f39d6b1ab0240d34f93d5fc6543c677d1ebdff405c40180a7ea570ae91c59.
- Datos: vista común de colonias expone población CONAPO, población asignada SACMEX,
  volumen y cobertura. Tasas etiquetadas como proxies, sin dividir por población de
  otro soporte; se omiten denominadores parciales. Desempate espacial determinista
  por menor clave numérica: reconciliados 22 enlaces sin resembrar ni tocar hechos.
  Reconstrucción cruda y JSON coinciden en diez campos; población unidad por unidad
  coincide con PostgreSQL. Quince consultas verificadas, 0 fallos.
- RDF: 91,230 triples; clase simétrica OWL correcta, población/cobertura proxy
  explícitas, huella decimal estable tras serializar y validación SQL/RDF sin fallos.
  Consulta 02: 27 pares de 21 municipios; interfaz muestra ambas cantidades ES/EN.
  Añadidos créditos bibliográficos de clima, vulnerabilidad e Hidro-MX con metadatos
  primarios; corregida atribución de Huerta en el informe ya versionado.
- Web: fichas muestran ambos soportes y cobertura, notas ES/EN, fuentes metropolitanas
  en el pie y vocabulario descargable; datos se revalidan para evitar caché antigua.
  QA real de mapa/grafo en escritorio y 375 px, catálogo y conteo SPARQL correctos.
- Gabriel autorizó un commit y push por repositorio para estas correcciones, con
  identidad Git humana y sin firmas/trailers/atribuciones de asistentes. No autoriza
  release, DOI, correo ni envío editorial. Cada push exige ejecutar el verificador
  original intacto: cero fallos o nueva excepción expresa de esa ejecución.

- **Corrección final autorizada 9 nov 2026:** Gabriel pidió corregir todo, commit y push
  con identidad Git humana, sin atribuciones/firmas de asistentes. Un cierre por repositorio;
  ningún permiso para release/DOI, correo o envío editorial. Word/PDF: 15 páginas, 9,116 palabras
  (+62.350846 % frente a 5,615), resumen 144 y seis keywords. Word d33e5f09cc6dc1d64546f8a5ff8b01de579085d1ed9e7d1dff20cda338ebd85f;
  PDF 36029cb2d1460aaa0c204ed8f8bdf7ab880cf166c5b72af6813cd530a821673f. Título, autores,
  declaración IA, imágenes, plantilla y v0 intactos. Quince páginas inspeccionadas y cero
  tokens nuevos sin amarillo vs respaldo de 9,431 palabras; contador histórico v0 83.
  Corregidos grano fiscal con cifras por registro/script, AP, tres listas implementadas,
  Discusión y cita fiscal oficial de Consejería (HTTP 200). Prueba exacta con empates/ceros
  sin SciPy, seis tests pasan en ambos repositorios. Web corregida solo en IJCOPI, sin tocar
  CSV base, SQL, TTL ni sitios históricos. Evidencia en IJCOPI/tmp/correccion_2026-11-09/.
  Comprobar Git y remoto para confirmar ejecución del cierre; permisos consumidos no se heredan.
- **Auditoría de lectura 9 nov 2026:** confirmados con Word 15 páginas, 9,431 palabras,
  base 5,615 (+67.960819 %), resumen 144 y seis keywords. PDF inspeccionado completo;
  original/copia Word idénticos; v0, título, autores, declaración de IA e imágenes intactos.
  Los conteos 79/67 del verificador amarillo son falsos positivos de alineación/tokenización,
  no nuevos añadidos sin amarillo, según comparación de párrafos y runs. Recalculados 10
  escenarios distintos, IF 19/20 y AP 20/20, 89 municipios, 1,508 colonias y 12 conteos web.
  Pendientes: índice fiscal de 5.2 atribuido a colonias cuando el grano es manzana/registro
  (1,200 de 1,553 mezclan categorías); tres listas todavía como trabajo futuro, aunque la
  nueva web ya las implementa. La web descarta error de captura sin confirmación y generaliza
  A_g solo-excesos más allá del top global observado; filtro de alcaldía vuelve al cambiar
  idioma y límite de filas no afecta ceros. Nuevo script pareado anuncia Wilcoxon exacto sin
  fijar método/versión: p depende de SciPy aunque el p exacto de la evidencia sí se reproduce
  por permutación. Localizada fuente fiscal SACMEX: Gaceta núm. 62, 1 abril 2019, pp. 39–40,
  https://www.sacmex.cdmx.gob.mx/storage/app/media/tandeo/Tandeo_2019_GOCDMX.pdf
  Acredita régimen fiscal, no la causa de cada valor del dataset. Evidencia en el repo
  Data_Warehouse_IJCOPI/tmp/auditoria_2026-11-09/ y tmp/auditoria_paper_2026-11-09/.
  Sin cambios a fuentes, Word/PDF, web o datos; solo continuidad local, sin commit/push.
- **Revisión local 8–9 nov 2026 (autorizada; sin commit ni push):** se corrigieron en
  dw_agua_ijcopi.tex hoja de ruta (secciones 4 y 6), «points», tabla 3 (m³, comas, «billed volume»),
  título del recurso «1° Semestre», correlación climática no reportada, 10 escenarios de sensibilidad,
  precisiones de 5.7 y pie de Fig. 3 (Tláhuac y Milpa Alta fuera de la banda). Nueva comparación
  pareada en 5.4 (19 de 20 semillas; PR-AUC 20 de 20): evaluacion-ml/comparacion_pareada.py y su
  evidencia. latex_a_ijcopi.py: «Mexico City», n.d. antes que fechadas, signo menos, párrafos con URL
  largo a la izquierda y rutas amarillas partibles tras «/». v3 y PDF regenerados: 15 páginas,
  9,431 palabras (+67.96 %), resumen 144; 0 palabras nuevas sin amarillo frente a la v3 previa
  (verificar_amarillo frente a v0: 79, solo cortes de token). Respaldo previo en
  Data_Warehouse_IJCOPI/tmp/revision_2026-11-08/antes/. Copia Word sincronizada en el repo IJCOPI.
- **Revisión local 5 nov 2026:** Gabriel pidió mejorar Word y web. Se revisaron
  dw_agua_ijcopi.tex y latex_a_ijcopi.py, se regeneró dw_agua_IJCOPI_v3_grafo.docx
  con la plantilla y se actualizó su PDF. Copia Word sincronizada en Data_Warehouse_IJCOPI.
  Word: 15 páginas, 9,318 palabras; base 5,615 (+65.95 %), resumen 144 palabras.
  Título, autores, tablas, figuras y v0 intactos; texto nuevo marcado en amarillo.
  Enlaces metropolitanos actualizados al repo independiente, sitios históricos intactos.
  Los cambios web están solo en Data_Warehouse_IJCOPI. No hubo commit ni push.
  No se recalcularon resultados científicos en esta revisión editorial y funcional.

- **Hecho:** v0 base y v1 extendida (8,311 palabras contra 5,615, +48 %; 14 páginas;
  resumen de 149 palabras; 6 palabras clave). Informe de datos. Presentaciones con logos.
- **Hecho (31 oct):** Deep research y auditoría completa de fuentes candidatas (lista de
  Gemini y `prdx919/Agua_en_la_cdmx`) en `reports/Deep_Research_Ampliacion_DWH_IJCOPI.md`,
  con DOIs, URLs de descarga directa, tamaños, sumas MD5/SHA-256, fuentes descartadas y
  propuesta de esquema de constelación y cubo de datos (`GROUP BY CUBE` + W3C `qb:DataSet`).
- **Hecho (31 oct):** almacén ampliado en `warehouse_ampliado/`, sin cubo: 2,762,834 filas en
  43 tablas, 62 archivos verificados y `verificar_ampliado.py` sin fallos. Agrega el Bloque D
  (CNGMD, SHCP, piezometría, acuíferos, sequía, presas, Hidro-MX, calidad del agua y CONAPO) y
  carga los bloques A, B y C1. La sección 0 del informe lista los errores que se corrigieron de
  su primera versión.
- **Hecho (31 oct, rama `ijcopi-zmvm`):** ETL completo desde un clon, 15 consultas SQL, mapa y grafo
  nuevos, y v3 del artículo: 9,387 palabras (+67 % sobre la base de 5,615), 15 páginas, resumen de
  144 palabras, secciones 5.7 y 5.8 y Fig. 3 con el mapa y el grafo. El almacén tiene 2,794,184
  filas en 45 tablas y el grafo 82,393 tripletas. Gabriel aprobó el título nuevo.
  En el mapa, la CDMX va en verde, el color del mapa original, y lo agregado en morado.
- **Trabajo 37:** tiene su base en Word en `PublicMunicipalWorks_DWH/paper/ijcopi/` (11 páginas,
  6,844 palabras); falta extenderlo. Su prompt está en `reports/Prompts_otras_sesiones.md`, sin
  ejecutar. `Actronix09/fuentes-alternas` (`obra-publica-srft`) ya trae datos del SRFT de la SHCP
  para Temascaltepec, sin verificar contra la fuente.
- **Artículo de sismos (proyecto aparte, `DWSismos`):** Gabriel quiere enviarlo a Computers and
  Geotechnics. Su prompt también está en ese archivo. Riesgo: la revista exige un problema
  geotécnico y el trabajo no lo tiene; el prompt pide decidirlo antes de implementar. Crossref
  registra mal al primer autor del artículo de AZCATL (`10.24275/AZC2026E1004`); la página del
  artículo y la referencia `villa2026` están bien.
- **Cambio de PC (3 nov):** la PC nueva necesita Docker con el volumen del almacén reconstruido
  (ver `warehouse_ampliado/README.md`, unos 2 GB de descarga), Word para el conversor y comprobar
  de nuevo si el portal de la ADIP sigue respondiendo 403.
- **Sin revisar por humanos:** el texto nuevo de la v1 y de la v2, los informes de datos, el
  almacén ampliado y el mapa. La declaración de IA de la v2 dice que los autores revisaron y
  aprobaron el texto: debe ser cierto antes de enviar.

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
- El correo a `datosabiertos@cdmx.gob.mx` sigue como borrador en el Gmail de Gabriel,
  sin enviar (revisado el 2026-10-31). No se sabe si presentó la solicitud en la PNT.
- Confirmar serie, volumen y páginas de la referencia de ICOKG, ahora "in press".
- Crear el release `v2.0-ijcopi` en `Data_Warehouse_ZMVM` cuando Gabriel apruebe el texto final. El
  Data Availability Statement de la v2 apunta por ahora al repositorio. El tag v1.5 no se toca.
- `SACMEX (n.d.)`, los reportes de agua, cita `datos.cdmx.gob.mx/dataset/reportes-de-agua`, que esta
  PC no puede abrir. Los datos vienen de la copia verificada contra el CKAN. Confirmar el enlace.
- Decidir si se implementa en el demo el diseño de tres listas; hoy es trabajo futuro.
- Aclarar la moneda de la contribución y revisar la licencia firmada con Springer.

## Siguiente paso

Cerrar el commit/push autorizado en ijcopi-zmvm para fuente/conversor/Word/PDF y el
del repo IJCOPI para Word y web implementada. Antes de cada push repetir el verificador
y detenerse si falla, según orden expresa de Gabriel. Confirmar remotos y Pages IJCOPI.
main original y sitios históricos intactos. No enviar el paper: faltan aval humano y
metadatos editoriales. Cada permiso se consume con la acción. Registros siguientes: antecedentes.

**9 nov, tras corrección:** Gabriel y coautores revisan la v3 final de 9,116 palabras.
Faltan aval humano y metadatos editoriales/referencia final de ICOKG; no inventarlos.
Confirmar cierre con Git/remoto y Pages del repo IJCOPI; no ejecutar publicadores históricos.
El permiso actual cubre solo este commit/push en ijcopi-zmvm, siempre sujeto al verificador
original y excepción expresa si falla. Cualquier acción posterior requiere autorización nueva.

**5 nov:** Gabriel revisa la v3 regenerada y los cambios web del repo independiente.
Confirmar aprobación humana de todos los autores, referencia final de ICOKG y metadatos
editoriales de la plantilla antes del envío. Estos cambios siguen locales: cada commit
y push requiere autorización expresa nueva, identidad humana y verificador Springer.
Los pendientes del 31 oct que aparecen abajo son antecedentes; la v3 local ya tiene
los enlaces nuevos de Data_Warehouse_IJCOPI. No ejecutar el publicador histórico sin tarea.

**Pedido de Gabriel del 31 oct, en curso en la rama `ijcopi-zmvm`:**

1. [x] ETL completo y reproducible: `colonias_imc2020_shp.zip` va en
   `warehouse_ampliado/snapshots/partes/` y `descargar.py` lo reconstruye. Probado desde un clon.
2. [x] Consultas SQL reales al almacén en `warehouse_ampliado/consultas/`, con su `README.md`.
3. [x] Mapa nuevo en `ijcopi/mapa-zm.html` y consultas en `ijcopi/consultas.html`, alimentados
   por `etl/exportar_mapa.py`. `verificacion/verificar_mapa.py` repite cada consulta y compara.
4. [x] Artículo v2 con capturas del mapa, todo lo agregado en amarillo y título nuevo.
5. [x] Publicado el 31 oct en `Data_Warehouse_ZMVM`, con su propio Pages. El artículo ya trae el
   mapa en la sección 5.7 y el repositorio en el Data Availability Statement.
6. [ ] Antes del 9 de noviembre: revisión humana del texto nuevo, incluida la sección 5.8 y la
   sustitución del panel de colonias por el grafo en la Fig. 3, y acuerdo de los coautores con
   el orden de autores. Falta el aval por escrito de todos, incluido el Dr. Zagal, y confirmar su
   inclusión con los editores. Sus dos trabajos sobre agua ya se citan en la sección 2.3, a partir
   de los resúmenes. Él debe confirmar esa descripción, que ninguno sea un almacén reproducible
   sobre datos de SACMEX (la sección 2.8 afirma que no existe) y qué fuente da fugas antes de 2021.
7. [ ] Cuando el texto quede aprobado: release `v2.0-ijcopi`, poner ese enlace en el artículo y
   regenerar la v2. Cada push al repositorio de trabajo necesita antes la autorización de
   Gabriel por el 403 de la ADIP (regla 2).
8. [ ] Cada push a `origin/ijcopi-zmvm` necesita la autorización de Gabriel, o que él lo haga.
   `Data_Warehouse_ZMVM` se actualiza con `ijcopi/publicar.ps1`: ese push no toca enlaces de Springer.

**El cubo de datos sigue pospuesto.** Gabriel debe revisar la sección 0 del informe: varias
cifras de su primera versión eran falsas, sobre todo lo de fugas en 2019. Cuando decida
retomar el cubo, sigue la sección 4.4 del informe.

## Bitácora

- 2026-11-09: cierre Git autorizado por Gabriel con identidad humana, sin firmas ni
  créditos automáticos; verificador original previo: 25 enlaces y 0 fallos. Se repetirá
  antes de cada push, con detención obligatoria si falla. Sin permiso de envío editorial.

- 2026-11-09: por petición de Gabriel, Roberto último; trabajo futuro de población y
  contexto geográfico, navegación a colonias/distancia descritas en 5.8. Regenerado desde
  fuente, Word/PDF de 15 páginas y 9,043 palabras; inspección de todas las páginas y amarillo
  comprobados. Copia Word IJCOPI idéntica. Sin commit/push ni cambios a main/históricos.

- 2026-11-09: corregida revisión independiente tras contrastar hallazgos; SQL y RDF
  reproducibles, 22 enlaces deterministas, población/cobertura explícitas y créditos
  científicos verificados. Word final 15 páginas/9,029 palabras, amarillo e identidad
  académica preservados. Cierre Git autorizado, sujeto al verificador por push.

- 2026-11-09: corregidos hallazgos científicos, estadística, referencia fiscal y Discusión;
  regenerada v3 en 15 páginas/9,116 palabras, amarillo e identidad académica preservados.
  Pruebas y QA correctos; preparado cierre Git autorizado con identidad humana, sujeto al verificador.
- 2026-11-09: auditoría independiente en lectura del informe de revisión; verificadas
  métricas, amarillo y datos, hallados pendientes científicos/UI y de reproducibilidad.
  Fuente fiscal primaria localizada; productos intactos, solo continuidad, sin commit/push.
- 2026-11-09: revisión autorizada del paper: fuente y conversor corregidos, script de comparación
  pareada, v3 y PDF regenerados en 15 páginas con amarillo comprobado. Todo local; sin commit/push.

- 2026-11-05: revisión autorizada del paper desde fuente; regeneración y medición con Word,
  inspección visual de las 15 páginas y comprobación de cambios amarillos. Se precisaron
  facturación/demanda, limitaciones del detector y RDF, declaración académica de IA y enlaces.
  Fuente, conversor, Word v3 y PDF quedan modificados localmente en ijcopi-zmvm; sin commit/push.

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
- 2026-10-31, Claude (Claude Code, Opus 5.5): abrió `ijcopi-zmvm` e integró
  `reports/Contexto_completo_sesion.md`. Subió el shapefile de colonias en partes, guardó las
  geometrías en la base de datos, escribió 13 consultas SQL, el mapa `ijcopi/mapa-zm.html` y su
  verificación contra la base, y generó la v2 del artículo. Un clon limpio reconstruyó el almacén
  con resultados idénticos byte por byte. Con la autorización de Gabriel, y con el 403 de la ADIP
  como único fallo, creó `Data_Warehouse_ZMVM`, activó su Pages y subió la rama. Quitó del historial
  local el enlace a un borrador de Gmail antes de publicar. Comprobó en línea los 13 hashes; `main`
  siguió en `f404787` y el tag v1.5 en `c4de86d`. Después, a pedido de Gabriel: marca metropolitana
  en el sitio público, verde para la CDMX y morado para lo agregado, Gabriel como primer autor y
  declaración de IA más breve. El título quedó aprobado. Luego aclaró en el mapa qué significa el
  color, tradujo "Guinda" y expandió el grafo a la zona metropolitana con vecindad real por
  polígonos, mapeo R2RML y página propia, verificado contra la base y repetido desde un clon.
  Agregó al Dr. Zagal como segundo autor, con ORCID y adscripción comprobados en ORCID y Crossref.
- 2026-11-01, Claude (Claude Code, Opus 5.5): citó en la sección 2.3 los dos trabajos del Dr. Zagal
  sobre agua, leídos en resumen, y comprobó en los CSV que no hay fugas antes de 2021. Para seguir
  en 15 páginas movió la Fig. 2 un párrafo y condensó texto nuevo, sin quitar resultados.
- 2026-11-03, Claude (Claude Code, Opus 5.5): guardó en `reports/Prompts_otras_sesiones.md` los
  prompts del trabajo 37 y del artículo de sismos, y anotó el contexto para cambiar de PC.
