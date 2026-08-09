#!/usr/bin/env python3
"""
materializar_grafo.py -- Materialises the RDF knowledge graph from the warehouse
and runs the territorial queries of Section 4 against it.

Produces the evidence that the graph layer of the paper actually executes:
triple counts by class and the result sets of three SPARQL queries.

Uses morph-kgc (R2RML engine, pure Python) and rdflib (in-memory store with
SPARQL 1.1). No Java, no external triple store.

    pip install morph-kgc rdflib psycopg2-binary

    python scripts/materializar_grafo.py \
        --dsn "postgresql://postgres:postgres@localhost:5433/data_warehouse" \
        --mapping mapping.r2rml.ttl \
        --salida kg.nt
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time

CONSULTAS = {
    "Q1 -- Neighbourhoods adjacent to a high-consumption one, with their own totals":
    """
    PREFIX agua: <https://w3id.org/cdmx/agua/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?vecino ?nombre (SUM(?c) AS ?consumo)
    WHERE {
      ?origen agua:nearbyWithin1500m ?vecino .
      ?vecino rdfs:label ?nombre .
      ?obs agua:location ?vecino ;
           agua:totalConsumption ?c .
      FILTER(?origen = <https://w3id.org/cdmx/agua/colonia/1>)
    }
    GROUP BY ?vecino ?nombre
    ORDER BY DESC(?consumo)
    LIMIT 10
    """,

    "Q2 -- Consumption and climate joined through the shared temporal dimension":
    """
    PREFIX agua: <https://w3id.org/cdmx/agua/>
    SELECT ?anio ?bimestre
           (SUM(?c) AS ?agua) (AVG(?t) AS ?tempMedia)
    WHERE {
      ?obs   agua:location ?loc ;
             agua:period ?p ;
             agua:totalConsumption ?c .
      ?p     agua:year ?anio ; agua:bimester ?bimestre .
      ?clima agua:period ?p ; agua:meanTemperature ?t .
    }
    GROUP BY ?anio ?bimestre
    ORDER BY ?anio ?bimestre
    """,

    "Q3 -- Consumption by development level, traversing the SKOS scheme":
    """
    PREFIX agua: <https://w3id.org/cdmx/agua/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?nivel (COUNT(?obs) AS ?observaciones) (SUM(?c) AS ?total)
    WHERE {
      ?obs agua:developmentIndex ?idx ;
           agua:totalConsumption ?c .
      ?idx skos:prefLabel ?nivel .
    }
    GROUP BY ?nivel
    ORDER BY DESC(?total)
    """,
}

CONTEO = """
PREFIX qb:   <http://purl.org/linked-data/cube#>
PREFIX geo:  <http://www.opengis.net/ont/geosparql#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX time: <http://www.w3.org/2006/time#>
SELECT ?clase (COUNT(?s) AS ?n) WHERE {
  ?s a ?clase .
  VALUES ?clase { qb:Observation geo:Feature geo:Geometry
                  skos:Concept time:TemporalEntity }
} GROUP BY ?clase ORDER BY DESC(?n)
"""


def barra(titulo: str) -> None:
    print("\n" + "=" * 78)
    print(titulo)
    print("=" * 78)


def materializar(dsn: str, mapping: str, salida: str, schema: str):
    import morph_kgc

    cfg = f"""
[CONFIGURATION]
output_file={salida}
output_format=N-TRIPLES
na_values=,#N/A,N/A,NULL,none,nan

[DataSource1]
mappings={mapping}
db_url={dsn}
"""
    fh = tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False, encoding="utf-8")
    fh.write(cfg)
    fh.close()
    barra("MATERIALISING THE GRAPH (morph-kgc over the live warehouse)")
    print(f"  mapping : {mapping}")
    print(f"  source  : {dsn.split('@')[-1]}")
    t0 = time.perf_counter()
    g = morph_kgc.materialize(fh.name)
    dt = time.perf_counter() - t0
    os.unlink(fh.name)
    print(f"\n  Triples materialised : {len(g):,}")
    print(f"  Elapsed              : {dt:.1f} s")
    incorporar_esquema(g, schema)
    if salida:
        print(f"  Serialising to {salida} ...", flush=True)
        t1 = time.perf_counter()
        g.serialize(destination=salida, format="nt", encoding="utf-8")
        mb = os.path.getsize(salida) / 1024 / 1024
        print(f"  Written              : {salida}  ({mb:.1f} MB, "
              f"{time.perf_counter()-t1:.1f} s)")
    return g


def consultar(g) -> int:
    barra("QUERYING THE GRAPH (rdflib, SPARQL 1.1)")
    print(f"  {len(g):,} triples in memory")

    barra("GRAPH COMPOSITION BY CLASS")
    print(f"  {'Class':<46}{'Instances':>12}")
    print("  " + "-" * 58)
    for fila in g.query(CONTEO):
        print(f"  {str(fila[0]):<46}{int(fila[1]):>12,}")

    for titulo, q in CONSULTAS.items():
        barra(titulo)
        print("  running...", flush=True)
        t0 = time.perf_counter()
        try:
            res = list(g.query(q))
        except Exception as exc:
            print(f"  ERROR: {exc}")
            continue
        dt = (time.perf_counter() - t0) * 1000
        if not res:
            print("  (no rows -- check that the adjacency table was materialised)")
            continue
        cols = [str(v) for v in res.vars] if hasattr(res, "vars") else None
        filas = [[str(c).split("/")[-1] if str(c).startswith("http") else str(c)
                  for c in fila] for fila in res]
        anchos = [max(len(str(x[i])) for x in filas) for i in range(len(filas[0]))]
        for fila in filas[:15]:
            print("  " + "  ".join(str(c).ljust(anchos[i])
                                   for i, c in enumerate(fila)))
        print(f"\n  {len(filas)} rows in {dt:.0f} ms")

    barra("DONE")
    print("  Every figure above was produced by executing SPARQL over the graph")
    print("  materialised from the warehouse. Screenshot this output for the paper.")
    return 0


def incorporar_esquema(g, schema: str) -> None:
    """Load Data Cube metadata into the materialised graph before querying it."""
    if not os.path.exists(schema):
        raise FileNotFoundError(f"No existe el esquema RDF: {schema}")
    antes = len(g)
    g.parse(schema, format="turtle")
    print(f"  Schema loaded  : {schema}  (+{len(g) - antes:,} triples)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dsn", required=True)
    ap.add_argument("--mapping", default="mapping.r2rml.ttl")
    ap.add_argument("--schema", default="schema.ttl",
                    help="Data Cube metadata loaded with the materialised graph")
    ap.add_argument("--salida", default="kg.nt")
    ap.add_argument("--solo-consultar", action="store_true",
                    help="skip materialisation and query an existing .nt file")
    ap.add_argument("--sin-guardar", action="store_true",
                    help="do not write the .nt file; query straight from memory")
    args = ap.parse_args()

    if args.solo_consultar:
        import rdflib
        if not os.path.exists(args.salida):
            sys.exit(f"No existe {args.salida}")
        barra("LOADING THE GRAPH FROM DISK")
        g = rdflib.Graph()
        t0 = time.perf_counter()
        g.parse(args.salida, format="nt")
        print(f"  {len(g):,} triples loaded in {time.perf_counter()-t0:.1f} s")
    else:
        g = materializar(args.dsn, args.mapping,
                         None if args.sin_guardar else args.salida, args.schema)
    if args.solo_consultar:
        incorporar_esquema(g, args.schema)
    return consultar(g)


if __name__ == "__main__":
    sys.exit(main())
