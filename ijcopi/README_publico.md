# Water in the Mexico City Metropolitan Area: an Extended Data Warehouse

Reproducible artefact of the extended version of a paper accepted at the **5th International
Conference on Ontologies and Knowledge Graphs (ICOKG 2026)**, prepared for the special issue of the
*International Journal of Combinatorial Optimization Problems and Informatics*.

- **Map → <https://gabrielhuav.github.io/Data_Warehouse_ZMVM/ijcopi/mapa-zm.html>**
- **Warehouse queries → <https://gabrielhuav.github.io/Data_Warehouse_ZMVM/ijcopi/consultas.html>**

The conference version remains frozen as release
[`v1.5-icokg2026`](https://github.com/gabrielhuav/Data_Warehouse_static/releases/tag/v1.5-icokg2026) of
[`gabrielhuav/Data_Warehouse_static`](https://github.com/gabrielhuav/Data_Warehouse_static). This
repository adds to that work and does not change it.

## What it adds

The original warehouse holds the billed water consumption of Mexico City. This one extends it,
additively, to the 63 municipalities of the official 2020 metropolitan delimitation: 62 verified
files, 2.76 million rows and 43 tables. The original fact tables are untouched.

| Path | Content |
| --- | --- |
| `ijcopi/` | The map, the query page and the exported results |
| `warehouse_ampliado/` | Manifest of sources with hashes, DDL, ETL, frozen sources and verification |
| `warehouse_ampliado/consultas/` | The 13 SQL queries behind the map and the article |
| `warehouse/` | The original warehouse: star schema, ETL, source data and container |
| `reports/` | Sources, corrections, discarded datasets and the implemented model |
| Root pages, `assets/`, `scripts/`, `evaluacion-ml/` | The conference demonstration and its analyses |

## The map is the warehouse

The map is static: it does not query PostgreSQL live. `etl/exportar_mapa.py` runs each query and
stores its result in `ijcopi/datos/`, with a hash. `verificacion/verificar_mapa.py` repeats every query
and compares the result byte by byte with the published files. A warehouse rebuilt from a clean
clone returned the same bytes for all 13 queries
([evidence](warehouse_ampliado/verificacion/evidencia_clon_limpio.txt)).

## Rebuilding it

You need Docker, Python 3.10 and about 2 GB of disk. On Windows, clone into a short path: with a very
long one, the `shapely` DLLs fail to load. From the repository root:

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

```bash
warehouse_ampliado/.venv/Scripts/python -I warehouse_ampliado/verificacion/verificar_mapa.py
```

`descargar.py` obtains every source and stops if a file does not match the manifest. Sources that
refuse scripts are already stored here, the largest one in parts. Commands to run the queries are in
[`warehouse_ampliado/consultas/README.md`](warehouse_ampliado/consultas/README.md).

## Limits of the data

- Consumption values are billed volumes, not meter readings, and cover January to June 2019.
- Municipal volumes need the quality filter in `v_zm_indicadores_agua`: 24 of the 47 municipalities
  outside Mexico City report none and 7 are atypical.
- The source records no leaks before 2021.
- Neighbourhood polygons are CONAPO's, not the utility's.

## Credit and licences

`warehouse/` is the work of **Omar Fernando Pulido Morales**, imported unmodified from
[`omarpulidom/data_warehouse_cdmx`](https://github.com/omarpulidom/data_warehouse_cdmx) (MIT). The
static demonstration descends from
[`Uriel1024/Data_Warehouse_static`](https://github.com/Uriel1024/Data_Warehouse_static), the fork parent
of `gabrielhuav/Data_Warehouse_static`.

Code is released under the MIT licence; see `LICENSE`. Data files keep the licences of their publishers,
listed source by source in `warehouse_ampliado/fuentes.json`. The base map is © OpenStreetMap
contributors, ODbL.
