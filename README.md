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
demonstration and its documentation are preserved as published by its author.

### Provenance of each component

This repository now aggregates work by three different hands, and it matters
which is which:

| Component | Author | Status |
| --- | --- | --- |
| `index.html`, `mapa.html`, `consumo.json`, `alcaldias.geojson` | upstream author (see fork parent) | original static demonstration |
| `warehouse/` | **Omar Fernando Pulido Morales** | **the implementation that produced the reported results**, imported from [`omarpulidom/data_warehouse_cdmx`](https://github.com/omarpulidom/data_warehouse_cdmx) |
| `scripts/reproducir_cifras.py` | added for the camera-ready | recomputes the paper's figures from the published CSVs |
| `mapping.r2rml.ttl` | added for the camera-ready | R2RML mapping described in Section 4 |
| `evaluacion-ml/eval_anomalias.py` | added for the camera-ready | **reconstruction** — see the caveat below |
| `paper/` | the authors | manuscript sources |

### `warehouse/` — the data warehouse implementation

Imported unmodified from Omar Fernando Pulido Morales' repository, with his
authorship recorded here and in the paper. This is the code that built the
warehouse whose figures the article reports:

| File | Description |
| --- | --- |
| `ddl/0_schema.sql` | Star schema: `fact_consumo_agua` and `fact_clima` over `dim_tiempo`, `dim_ubicacion` and `dim_indice_des`, plus the two staging tables. |
| `etl/1_copy.sql` | Phase 1–2: `COPY` of both source CSVs into staging, with `NULL 'NA'`. |
| `etl/2_dim.sql` | Phase 3: populates the three dimensions. `dim_tiempo` is derived from the daily climate series; `dim_ubicacion` from distinct borough–neighbourhood pairs. |
| `etl/3_fact.sql` | Phase 4: populates both fact tables and drops staging. The `INNER JOIN`s against the dimensions are the cleaning step. |
| `scripts/consulta.sql` | Bimestral correlation between water consumption and climate. |
| `data/consumo_agua_historico_2019.csv` | SACMEX open data, 71,102 records, 2019 bimesters 1–3. |
| `data/open-meteo-19.44N99.11W2233m.csv` | Hourly climate series for Mexico City, 1 Jan – 30 Jun 2019 (Open-Meteo). |
| `Dockerfile`, `compose.yml` | PostgreSQL 16 image that runs the whole pipeline on start-up. |

```bash
cd warehouse && docker compose up -d
docker exec -it data_warehouse_cdmx psql -U postgres -d data_warehouse
```

### `scripts/reproducir_cifras.py`

Recomputes the volume and cleaning figures of the paper straight from the two
CSVs, with no database, by replicating what the SQL ETL does. It exists so that a
reader can verify the reported numbers in one command:

```bash
python scripts/reproducir_cifras.py \
    --consumo warehouse/data/consumo_agua_historico_2019.csv \
    --clima   warehouse/data/open-meteo-19.44N99.11W2233m.csv --correlacion
```

Verified output:

```
Source records read: 71,102
Unmatched territorial label            216    0.30%
Total discarded                        216    0.30%
Loaded into the fact table          70,886   99.70%

fact_consumo_agua   70,886      dim_ubicacion    1,553
dim_tiempo             181      dim_indice_des       4
```

Two facts about the data that the numbers make explicit. The 181 rows of
`dim_tiempo` are daily climate observations, not reading dates: the consumption
source carries three reading dates (28 Feb, 30 Apr, 30 Jun 2019). And
`dim_indice_des` has four members because the source scale is `ALTO`, `BAJO`,
`MEDIO` and `POPULAR`.

### `mapping.r2rml.ttl`

The R2RML mapping that projects the relational star schema onto an RDF knowledge
graph, as described in Section 4 of the paper, reusing RDF Data Cube, GeoSPARQL,
SKOS and OWL-Time. It runs under any R2RML engine:

```bash
java -jar rmlmapper.jar -m mapping.r2rml.ttl -o kg.nt
```

Two limitations are recorded in the file and repeated here. The topological
relation `geo:sfTouches` used by the SPARQL example is not produced by the
mapping; it is derived after materialisation. And the geometry triples map reads
`latitud`/`longitud` from the location dimension, columns which the warehouse
DDL currently does not retain although they are present in the source CSV —
materialising geometry therefore requires extending `dim_ubicacion` first.

### `evaluacion-ml/eval_anomalias.py` — reconstruction

This is the one component that is **not** the original code. The script that
produced the anomaly-detection table of the paper was not preserved, so this file
reimplements the protocol as the paper describes it (N ≈ 11,460, 3 % injected
anomalies, 70 % spikes / 30 % drops, log-scaled consumption and ratio to the
neighbourhood mean as features, thresholds A_g > 3, IF s > 0.60, LOF s > 1.5,
fixed seed). It is provided so the protocol can be inspected and re-executed, not
as evidence of what was executed previously. Figures obtained by running it
should be reported as such.

### `paper/`

| File | Description |
| --- | --- |
| `dw_agua_camera_ready.tex` | LaTeX source of the camera-ready manuscript. |
| `dw_agua_camera_ready.pdf` | Compiled manuscript. |
| `Mapa.png` | Choropleth figure of the 16 boroughs. |
| `llncs.cls` | Springer LNCS document class. |

### Scope of the static demonstration

The `consumo.json` bundled with the demonstration at the repository root is a
generated dataset for browser-side rendering, as its own `nota` field records: it
spans five years and six bimesters, while the warehouse covers 2019 bimesters 1–3
only. It exercises the retrieval interface faithfully — filters, aggregations and
the choropleth all behave as they do against the warehouse — but it is not an
export of the warehouse and reproduces none of the reported measurements. Those
come from `warehouse/`.

### Citing this artefact

The version cited by the paper is frozen as release `v1.1-icokg2026`. This
repository is a fork; authorship of the original static demonstration remains
with its author and the fork relationship is preserved on GitHub so that
attribution stays visible.
