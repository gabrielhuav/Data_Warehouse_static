# Consumo de Agua CDMX — versión estática

Sitio estático (HTML + JavaScript + JSON + GeoJSON) que permite consultar y visualizar el consumo de agua de la Ciudad de México sin depender de un servidor backend. Esta versión corresponde a la demostración pública del proyecto y está lista para publicarse en **GitHub Pages** o cualquier servicio de alojamiento estático.

## Contenido

| Archivo             | Descripción                                                                         |
| ------------------- | ----------------------------------------------------------------------------------- |
| `index.html`        | Dashboard con indicadores, gráficos interactivos (Plotly) y tabla de consulta.      |
| `mapa.html`         | Mapa coroplético interactivo de las 16 alcaldías utilizando Leaflet.                |
| `consumo.json`      | Conjunto de datos exportado desde el almacén de datos para la demostración pública. |
| `alcaldias.geojson` | Polígonos geográficos de las 16 alcaldías de la Ciudad de México.                   |

## Datos

Los datos utilizados en esta versión fueron exportados desde el almacén de datos construido durante el proyecto, el cual integra información proveniente de los conjuntos de datos abiertos publicados por el Sistema de Aguas de la Ciudad de México (SACMEX).

La versión estática contiene la información necesaria para ejecutar las consultas, filtros y visualizaciones del sistema directamente en el navegador, sin requerir conexión a una base de datos.

## Funcionalidades

* Consulta por alcaldía.
* Consulta por colonia.
* Filtros por año y bimestre.
* Visualización mediante mapa coroplético.
* Indicadores y gráficas interactivas.
* Detección exploratoria de consumos atípicos.

## Publicación en GitHub Pages

1. Subir el contenido del repositorio a GitHub.
2. Ir a **Settings → Pages**.
3. Seleccionar:

* **Deploy from a branch**
* Rama `main`
* Carpeta correspondiente al sitio

Una vez publicado, el sistema estará disponible mediante GitHub Pages como demostración pública del proyecto.

## Ejecución local

```bash
python3 -m http.server 8000
```

Después abrir:

```
http://127.0.0.1:8000/
```

## Notas

* La versión publicada corresponde a una implementación completamente estática destinada a la demostración y consulta del sistema.
* Toda la recuperación de información se realiza mediante procesamiento de los archivos JSON cargados en el navegador.
* El backend desarrollado con FastAPI y PostgreSQL forma parte de la implementación completa del proyecto, pero no es necesario para ejecutar esta versión de demostración.

## ICOKG 2026 camera-ready

This section documents the artefacts added to this fork for the camera-ready
version of the ICOKG 2026 paper on the Mexico City water-consumption data
warehouse. Nothing above this line has been modified; the original static
demonstration and its documentation are preserved as published by the original
author.

### `paper/`

The camera-ready manuscript and everything needed to typeset it:

| File | Description |
| --- | --- |
| `dw_agua_camera_ready.tex` | LaTeX source of the camera-ready manuscript. |
| `dw_agua_camera_ready.pdf` | Compiled manuscript, as submitted. |
| `Mapa.png` | Choropleth figure of the 16 boroughs used in the paper. |
| `llncs.cls` | Springer LNCS document class required to compile the source. |

### `mapping.r2rml.ttl`

The complete R2RML mapping that projects the relational star schema of the
warehouse onto an RDF knowledge graph, as described in Section 4 of the paper.
It declares four triples maps — observations (`fact_water_consumption` →
`qb:Observation`), territory (`dim_location` → `geo:Feature` plus a derived
`geo:Geometry`), time (`dim_time` → `time:TemporalEntity`) and the development
index (`dim_dev_index` → an ordinal `skos:Concept` scheme) — reusing the RDF
Data Cube, GeoSPARQL, SKOS and OWL-Time vocabularies. It runs unmodified under
any R2RML engine, for example:

```bash
java -jar rmlmapper.jar -m mapping.r2rml.ttl -o kg.nt
# or
morph-kgc config.ini
```

One limitation is stated explicitly in the file and repeated here: the
topological relation `geo:sfTouches` used by the SPARQL example in the paper is
**not** produced by the mapping. It is derived after materialisation, either by
the triple store's spatial index or by a one-off PostGIS statement over
`dim_location`.

### `scripts/generar_datos_faltantes.py`

Reproduces the two sets of empirical figures reported in the paper. It has three
subcommands:

```bash
python scripts/generar_datos_faltantes.py limpieza  --csv datos_sacmex.csv
python scripts/generar_datos_faltantes.py consultas --base-url http://localhost:8000
python scripts/generar_datos_faltantes.py reparto   --dsn "postgresql://user:pw@host/db"
```

`limpieza` recomputes the **cleaning statistics**: it applies the four exclusion
criteria (missing or non-numeric measure, null or out-of-range coordinates,
unmatched territorial label, unparseable reading date) with first-match
attribution, so the per-criterion counts sum to the total discarded without
double counting. `consultas` measures the **query response times** of the four
retrieval workloads against a running instance of the API, reporting mean and
p95 over repeated executions after a warm-up round. `reparto` recovers the
domestic / non-domestic split by borough used in the findings section.

### `etl/` and `evaluacion-ml/`

Reference implementations of the pipeline described in Section 4 and of the
evaluation protocol of Section 5:

| File | Description |
| --- | --- |
| `etl/schema.sql` | DDL of the star schema: one fact table and three dimensions, with the check constraints and indexes that support the benchmarked workloads. The table and column identifiers are authoritative — `mapping.r2rml.ttl` and `generar_datos_faltantes.py` both reference them. |
| `etl/loader.py` | Four-phase ETL: extraction from the SACMEX CSV files, validation and cleaning, `COPY` to staging and population of the dimensions, and the fact load with surrogate-key resolution. `--dry-run` prints the exclusion report without touching a database. |
| `etl/queries.sql` | The parameterised retrieval queries behind the API endpoints and the benchmark, including the atypicality score `A_g`. All user-supplied values are bound parameters; no query is assembled by string concatenation. |
| `evaluacion-ml/eval_anomalias.py` | Controlled evaluation of the atypical-consumption module: builds the synthetic panel, injects 3 % labelled anomalies (70 % spikes, 30 % drops), and compares the `A_g` z-score, Isolation Forest and LOF at the operating points stated in the paper, under a fixed seed. |

```bash
pip install -r evaluacion-ml/requirements.txt
python evaluacion-ml/eval_anomalias.py --latex
```

### Provenance and scope

Two points of scope, stated so that readers can calibrate what this repository
does and does not demonstrate.

**The files under `etl/` and `evaluacion-ml/` are reconstructions.** They were
written for this camera-ready artefact from the process described in the paper.
They are not the original scripts used to produce the submitted results, which
were not published with the upstream repository. They are provided so that the
described pipeline can be inspected, criticised and re-executed — not as
evidence of what was executed previously. Any figure obtained by running them
should be reported as such.

**The dataset shipped with the static demonstration is illustrative.** The
`consumo.json` file bundled with the demo is a generated dataset for
browser-side display, as its own `nota` field records. The experimental results
in the paper were obtained over the original warehouse built from SACMEX open
data, which is not distributed here. The static demo shows the behaviour of the
retrieval interface; it does not reproduce the paper's measurements.

### Citing this artefact

The version cited by the paper is frozen as release `v1.0-icokg2026`. This
repository is a fork of
[`Uriel1024/Data_Warehouse_static`](https://github.com/Uriel1024/Data_Warehouse_static);
authorship of the original static demonstration remains with its author, and the
fork relationship is preserved on GitHub so that attribution is visible.
