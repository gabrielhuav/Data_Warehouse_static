# Prompts para sesiones en otros proyectos

Gabriel pidió estos prompts el 1 y el 2 de noviembre de 2026 para seguir en otros repositorios.
Se guardan aquí porque cambió de PC. Cada uno se pega en una sesión nueva abierta en la carpeta
indicada. Ninguno se ha ejecutado todavía.

## 1. Trabajo 37 (obras públicas) para IJCOPI

Carpeta: `PublicMunicipalWorks_DWH`. Envío: 9 de noviembre de 2026.

```text
Vamos a extender el trabajo 37 de ICOKG 2026, "A Dimensional Data Warehouse for Geospatial Monitoring of Municipal Public Works, with an Evolution Path Toward a Lakehouse Architecture", para el número especial de IJCOPI, igual que ya hicimos con el trabajo 38 en el repositorio Data_Warehouse_static. El envío es el 9 de noviembre de 2026. Conversa conmigo en español y sé breve: me importa no gastar créditos.

ANTES DE EMPEZAR
Lee la memoria del trabajo 38:
git -C "C:\Users\gabri\Documents\GitHub Desktop\Data_Warehouse_static" show ijcopi-zmvm:AGENTS.md
Ahí están los requisitos de IJCOPI, el flujo y los errores que ya se resolvieron. Sus rutas y cifras son de aquel trabajo, no de este.
En esa rama están las herramientas que debes copiar y adaptar aquí, sin editarlas allá: paper/ijcopi/latex_a_ijcopi.py, verificar_amarillo.py, word_a_pdf.ps1 y capturar_mapa.ps1; ijcopi/publicar.ps1 y ajustes_publicos.py; y warehouse_ampliado/ como modelo de ETL.

REGLAS QUE NO SE NEGOCIAN
1. Los enlaces del capítulo de Springer son inmutables. Los que apuntan a mi trabajo son https://gabrielhuav.github.io/PublicMunicipalWorks_DWH/, https://gabrielhuav.github.io/PublicMunicipalWorks_DWH/mapa/?modo=claro y https://github.com/gabrielhuav/PublicMunicipalWorks_DWH. No renombres el repositorio, no muevas páginas y no toques los tags v1.*-icokg2026 ni sus releases.
2. Todo va en una rama nueva, ijcopi-obras. No fusiones a main: cada push a main que toque docs/ republica el sitio. No empujes a upstream (Urigc/Obras_publicas).
3. Lo público nuevo lleva enlaces nuevos, en un repositorio nuevo con su propio Pages. Propón el nombre antes de crearlo.
4. No toques paper/Paper_37_1.tex ni sus PDF, ni paper/ijcopi/Paper37_IJCOPI_v0_fiel.docx ni su PDF. Son la base congelada. Paper_37_1.tex tampoco se copia encima.
5. Crea scripts/verificar_enlaces_springer.ps1 a partir del que tiene el otro repositorio, apuntando a Paper_37_1.tex, y córrelo antes de cada push. Ningún push sin mi autorización.
6. No envíes correos ni solicitudes sin que yo vea el texto y confirme.
7. Solo reporta cifras que hayas recalculado, y cada número del artículo debe salir de un script del repositorio. Si algo no se pudo verificar, dilo. No cites fuentes que no hayas leído o que no alimenten datos.
8. Los repositorios son públicos: no escribas enlaces a correos, borradores ni datos personales.

MEMORIA
Lo primero en la rama es crear AGENTS.md, con el formato del trabajo 38, y CLAUDE.md con la línea @AGENTS.md. Actualízalo conforme avances, no solo al final, para que otra sesión pueda seguir si se acaba el límite.

LO QUE DEBES SABER DE ESTE TRABAJO
- La base en Word mide 11 páginas y 6,844 palabras, así que hacen falta al menos 9,582 palabras en un máximo de 15 páginas. El script que generó esa base no está en el repositorio.
- El resumen del capítulo pasa de 150 palabras y trae 8 palabras clave. La versión extendida debe tener de 70 a 150 palabras y de 4 a 6 palabras clave.
- Todos los datos son sintéticos y las imágenes de obras están generadas con IA, con la marca ILUSTRATIVO. Nada sintético puede presentarse como real. Conserva la separación entre cifras medidas y proyectadas, y no confundas las tres poblaciones del artículo: las 6 obras del sitio, las 1,247 del almacén y el conjunto de detección.
- notas_release.md está desactualizado: da 0.9945 de precisión y 0.8411 de recall con una semilla, y el capítulo da 0.46 y 0.35 con diez semillas. Manda el capítulo, pero recalcula con scripts/evaluacion/.
- No reutilices texto del trabajo 38: va al mismo número y se revisa con herramientas de similitud y de IA.

QUÉ HACER
1. Reproduce desde este repositorio las cifras principales del capítulo y dime cuáles no coinciden.
2. Tráeme en un solo mensaje un plan ordenado por valor y esfuerzo, y espera mi aprobación. Mi preferencia es:
   a. Datos abiertos reales de obra pública para Temascaltepec o el Estado de México, porque hoy ninguna cifra viene de datos reales. Revisa primero https://github.com/Actronix09/fuentes-alternas, carpeta obra-publica-srft: ya trae contratos, metas y georreferencias de Temascaltepec del SRFT de la SHCP. Es de terceros: verifícalo contra la fuente oficial. Otras candidatas sin verificar: FAIS, Compras MX o CompraNet, y el CNGMD y el Censo de INEGI. Si no sirven, dilo.
   b. Del trabajo futuro del capítulo: el criterio de costo por tipo de obra, reevaluado con la misma verdad de referencia; la capa lakehouse con Parquet o Iceberg y DuckDB, medida; y el grafo RDF con R2RML y la proyección OC4IDS.
   No hace falta hacerlo todo: priorizo lo que dé resultados medidos y quepa en cuatro páginas.
3. Haz el ETL completo y reproducible: manifiesto con hashes, archivos grandes por partes, integración aditiva con las tablas actuales y prueba desde un clon limpio. Con core.autocrlf=true, protege los datos con .gitattributes.
4. Dame las consultas SQL y los comandos para verlas en la base de datos.
5. Publica las páginas nuevas en el repositorio nuevo. Cada capa debe ser una consulta exportada y verificada contra la base byte por byte.
6. Escribe la extensión en paper/ijcopi/ en inglés británico, con citas APA 7 y la plantilla obligatoria 2027-IJCOPI_template_simple_British_English.docx. Todo lo nuevo va en amarillo, y las figuras nuevas con marco amarillo. Propón un título que indique que es una extensión. Comprueba páginas, palabras y amarillo en Word, y revisa el PDF a ojo.

AUTORES
Antes de tocar el bloque de autores, pregúntame. En el trabajo 38 firmo primero y el Dr. Roberto Eswart Zagal Flores va segundo, pero aquí no lo he decidido.

Empieza creando la rama y AGENTS.md, y después reproduce las cifras.
```

## 2. Sistema de datos sísmicos para Computers and Geotechnics

Carpeta: `DWSismos` (su remoto es `gabrielhuav/Seismic-Data-Visualization-System`). Sin fecha de envío.

Riesgo detectado el 2 nov: el alcance de la revista es la ingeniería geotécnica, y el trabajo hoy no
tiene un problema geotécnico. El prompt pide decidir eso antes de implementar.

```text
Vamos a preparar un artículo nuevo a partir de este proyecto, el sistema de visualización de datos sísmicos (repositorio gabrielhuav/Seismic-Data-Visualization-System), para la revista Computers and Geotechnics de Elsevier (ISSN 0266-352X). Es un artículo original, no una versión extendida. Conversa conmigo en español y sé breve: me importa no gastar créditos.

ANTECEDENTE PUBLICADO
El sistema ya se publicó como artículo de divulgación: Villa Vargas, J. M., Hurtado Avilés, G., & Climent Hernández, J. A. (2026). Cuando México tiembla: la historia contada por los datos. AZCATL, 4(6), 28–33. https://doi.org/10.24275/AZC2026E1004. Está en español y bajo licencia CC BY-NC-ND 4.0. El artículo nuevo debe citarlo, aportar algo sustancialmente nuevo y no reutilizar su texto ni sus figuras. Toma los autores de la página del artículo o del BibTeX del README, no de Crossref, que tiene mal al primer autor.

MODELO DE TRABAJO
Ya hicimos este flujo con otro artículo. Lee su memoria como referencia, sin editarla:
git -C "C:\Users\gabri\Documents\GitHub Desktop\Data_Warehouse_static" show ijcopi-zmvm:AGENTS.md
Sus rutas y cifras son de aquel trabajo. Sirven de modelo su ETL con manifiesto de hashes (warehouse_ampliado/), sus verificaciones contra la base y la forma de publicar enlaces nuevos sin tocar los viejos.

REGLAS QUE NO SE NEGOCIAN
1. https://github.com/gabrielhuav/Seismic-Data-Visualization-System está citado en AZCATL y queda congelado. No renombres ni borres el repositorio, no cambies main (está en 8569667), no reescribas su historia y no hagas push forzado. Los demás enlaces de ese artículo son de terceros: SSN, INEGI, YouTube y ORCID.
2. Todo lo nuevo va en una rama nueva, articulo-revista, sin fusionarla a main. Si hace falta un sitio público o un tag que congele el estado citado, propónmelo antes.
3. Crea un verificador de los enlaces del artículo de AZCATL, a partir de scripts/verificar_enlaces_springer.ps1 del otro repositorio, y córrelo antes de cada push. Si falla un enlace de terceros, avísame. Ningún push sin mi autorización. No empujes nada a Actronix09/fuentes-alternas ni a los forks.
4. No envíes correos ni solicitudes sin que yo vea el texto y confirme.
5. Solo reporta cifras que hayas recalculado, y cada número del artículo debe salir de un script del repositorio. Si algo no se pudo verificar, dilo. No cites fuentes que no hayas leído o que no alimenten datos.
6. El repositorio es público: no escribas enlaces a correos, borradores ni datos personales.

MEMORIA
Lo primero en la rama es crear AGENTS.md, con el formato del otro trabajo, y CLAUDE.md con la línea @AGENTS.md. Actualízalo conforme avances, para que otra sesión pueda seguir si se acaba el límite.

DATOS NUEVOS
Vienen de https://github.com/Actronix09/fuentes-alternas, rama sismos-norteamerica, carpeta sismos-usgs. Es un repositorio de terceros: trátalo como datos, clónalo aparte, lee el código antes de ejecutarlo y no corras los .pyc que trae. Incluye el catálogo USGS ComCat bajado por la API FDSN (México desde 1900 con M ≥ 3.5, y Norteamérica de 2020 a 2025), población de Census y StatCan, límites de EE. UU. y Canadá, una copia de los SQL de este repositorio en 8569667 y un cruce SSN–USGS.
- Verifica cada archivo contra su fuente oficial. El catálogo de USGS cambia con sus revisiones, así que no esperes el mismo hash: repite cada consulta con los parámetros de su procedencia.json y compara identificadores y conteos.
- Su README afirma cifras que debes recalcular antes de usarlas. Por ejemplo, que el almacén une la fecha local del SSN con la hora UTC y deja 74,927 sismos (23.7 %) con un día de menos, y que el cruce da 7,884 pares, 19.2 km de distancia mediana y ΔM = −0.12 ± 0.27. Si el desfase se confirma, documéntalo y corrígelo en la rama, no en main.
- Integra lo nuevo de forma aditiva, con ETL reproducible, manifiesto de hashes y prueba desde un clon limpio. El repositorio ya tiene SQL de 44 a 73 MB, así que divide en partes cualquier archivo grande nuevo. Esta PC tiene core.autocrlf=true y el repositorio usa * text=auto: protege los datos con .gitattributes.
- El docker-compose original publica los puertos 80 y 5433, y el 5433 ya lo usa el almacén de agua (data_warehouse_cdmx). Usa otro puerto con un archivo override, sin editar el compose de main.

LA REVISTA (guía para autores, revisada el 2 nov 2026)
- Alcance: ingeniería geotécnica. Acepta ciencia de datos y aprendizaje automático solo si se centran en un problema geotécnico y aportan algoritmos o marcos computacionales nuevos, o IA informada por la física. Los casos históricos y el monitoreo de campo solo entran con métodos computacionales propios. La revisión es de anonimato simple.
- Plantilla: la clase oficial elsarticle de Elsevier (https://www.elsevier.com/latex; v3.5 en CTAN). MiKTeX ya está instalado, con pdflatex, latexmk y bibtex. Las referencias van en estilo autor-año, con nombres de revista abreviados según LTWA.
- Resumen de hasta 250 palabras; de 1 a 7 palabras clave; highlights de 3 a 5 viñetas de hasta 85 caracteres, en un archivo aparte; resumen gráfico opcional.
- Son obligatorios CRediT, la declaración de conflictos de interés, la de financiamiento y una sección de IA generativa con el título y la frase que fija la guía. Los datos se depositan en un repositorio y se citan.
- Las figuras van en archivos aparte: 300 dpi las imágenes y 1000 los dibujos de línea en mapa de bits. Un mapa solo debe mostrar el área estudiada. No se permiten imágenes de datos generadas con IA.
- Los autores solo pueden cambiar antes de la aceptación y con aprobación del editor. La guía no fija un límite de extensión.

PRIMER PASO: EL AJUSTE A LA REVISTA
Antes de implementar nada, dime con evidencia si este trabajo cabe en Computers and Geotechnics. Hoy es un sistema de visualización y validación de catálogos sísmicos, sin un problema geotécnico. Tráeme dos o tres rutas con su costo y no empieces a escribir hasta que yo decida. Por ejemplo:
a. Reorientarlo a un problema geotécnico con un método computacional propio, como los efectos de sitio en la zona de lago de la Ciudad de México. Fuentes candidatas, sin verificar: registros acelerográficos del Instituto de Ingeniería de la UNAM, periodos dominantes del suelo de las Normas Técnicas para Diseño por Sismo, ShakeMap y Vs30 de USGS, daños del 19S y hundimiento medido por InSAR.
b. Conservar el aporte de integración y validación de catálogos y elegir otra revista. Computers & Geosciences incluye la sismología y las bases de datos científicas, pero rechaza aplicaciones rutinarias y artículos de interfaz, y exige un repositorio documentado en inglés.

DESPUÉS DE MI DECISIÓN
1. Levanta el sistema original sin tocar main y reproduce sus cifras.
2. Integra y verifica los datos nuevos como se indicó arriba.
3. Dame las consultas SQL y los comandos para verlas en la base de datos.
4. Haz que cada figura salga de una consulta o un script verificado contra la base.
5. Escribe el artículo en inglés con elsarticle, en paper/ dentro de la rama, y revisa el PDF a ojo.

AUTORES Y FECHAS
Antes de tocar autores o fecha de envío, pregúntame.

Empieza creando la rama y AGENTS.md, y después tráeme la evaluación del ajuste a la revista.
```

## Avisos para la PC nueva

- Las rutas de los prompts suponen `C:\Users\gabri\Documents\GitHub Desktop\`. Si cambian, ajústalas.
- Los prompts dicen que MiKTeX está instalado y que el puerto 5433 lo usa el almacén de agua: eso
  vale para la PC anterior. Compruébalo en la nueva.
