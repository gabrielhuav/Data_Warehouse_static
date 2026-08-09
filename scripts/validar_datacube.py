#!/usr/bin/env python3
"""Run reproducible RDF Data Cube integrity checks over demo data and schema.

Usage:
    py -3.12 scripts/validar_datacube.py

The script loads kg_demo.ttl and schema.ttl in one RDF graph.  It prints the
number of violations for each check, shows up to five violating rows, and exits
non-zero if any check fails.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from rdflib import Graph

CHECKS = {
    "IC-1 unique DataSet": """
        PREFIX qb: <http://purl.org/linked-data/cube#>
        SELECT ?observation (COUNT(?dataset) AS ?count) WHERE {
          ?observation a qb:Observation ; qb:dataSet ?dataset .
        } GROUP BY ?observation HAVING (COUNT(?dataset) != 1)
    """,
    "IC-2 unique DSD": """
        PREFIX qb: <http://purl.org/linked-data/cube#>
        SELECT ?dataset (COUNT(?dsd) AS ?count) WHERE {
          ?dataset a qb:DataSet ; qb:structure ?dsd .
        } GROUP BY ?dataset HAVING (COUNT(?dsd) != 1)
    """,
    "IC-3 DSD includes measure": """
        PREFIX qb: <http://purl.org/linked-data/cube#>
        SELECT ?dsd WHERE {
          ?dsd a qb:DataStructureDefinition .
          FILTER NOT EXISTS { ?dsd qb:component/qb:measure ?measure . }
        }
    """,
    "IC-11 all dimensions required": """
        PREFIX qb: <http://purl.org/linked-data/cube#>
        SELECT ?observation ?dimension WHERE {
          ?observation a qb:Observation ;
                       qb:dataSet/qb:structure ?dsd .
          ?dsd qb:component [ qb:dimension ?dimension ] .
          FILTER NOT EXISTS { ?observation ?dimension ?value . }
        }
    """,
    "Component dimensions typed": """
        PREFIX qb: <http://purl.org/linked-data/cube#>
        SELECT ?dsd ?dimension WHERE {
          ?dsd a qb:DataStructureDefinition ;
               qb:component [ qb:dimension ?dimension ] .
          FILTER NOT EXISTS { ?dimension a qb:DimensionProperty . }
        }
    """,
    "Component measures typed": """
        PREFIX qb: <http://purl.org/linked-data/cube#>
        SELECT ?dsd ?measure WHERE {
          ?dsd a qb:DataStructureDefinition ;
               qb:component [ qb:measure ?measure ] .
          FILTER NOT EXISTS { ?measure a qb:MeasureProperty . }
        }
    """,
    "Consumption datasets declare cubic-metre unit": """
        PREFIX agua: <https://w3id.org/cdmx/agua/>
        PREFIX qb: <http://purl.org/linked-data/cube#>
        SELECT ?dataset WHERE {
          VALUES ?dataset { agua:consumoCDMX agua:consumoCDMXDemo }
          ?dataset a qb:DataSet .
          FILTER NOT EXISTS { ?dataset agua:unit agua:cubicMetre . }
        }
    """,
}


def render(row) -> str:
    return " | ".join(str(value) for value in row)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kg", type=Path, default=root / "kg_demo.ttl")
    parser.add_argument("--schema", type=Path, default=root / "schema.ttl")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    graph = Graph()
    graph.parse(args.kg, format="turtle")
    graph.parse(args.schema, format="turtle")
    print(f"Loaded {args.kg}: {len(Graph().parse(args.kg, format='turtle')):,} triples")
    print(f"Loaded {args.schema}: {len(Graph().parse(args.schema, format='turtle')):,} triples")
    print(f"Combined graph: {len(graph):,} triples\n")

    failures = 0
    for name, query in CHECKS.items():
        rows = list(graph.query(query))
        print(f"{name}: {len(rows)} violation(s)")
        for row in rows[: args.limit]:
            print(f"  {render(row)}")
        if rows:
            failures += 1
    print(f"\nResult: {'PASS' if failures == 0 else 'FAIL'} ({failures} failing check(s))")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
