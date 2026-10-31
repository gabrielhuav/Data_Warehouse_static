#!/usr/bin/env python3
"""Materializa el grafo metropolitano desde el almacen y lo deja en ijcopi/kg_zm.ttl.

    python -I warehouse_ampliado/grafo/materializar.py

Usa morph-kgc, el mismo motor R2RML del grafo original, con mapeo_zm.r2rml.ttl. Nada del grafo se
escribe a mano: si cambia el almacen, se vuelve a materializar. Instala primero las dependencias
de grafo/requirements.txt en un entorno aparte, porque morph-kgc fija otras versiones de pandas.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import morph_kgc
import rdflib

GRAFO = Path(__file__).resolve().parent
RAIZ = GRAFO.parents[1]
SALIDA = RAIZ / "ijcopi" / "kg_zm.ttl"
RESUMEN = RAIZ / "ijcopi" / "datos" / "grafo.json"
DSN = os.environ.get("DW_DSN", "postgresql://postgres:postgres@localhost:5433/data_warehouse")
PREFIJOS = {
    "agua": "https://w3id.org/cdmx/agua/", "mun": "https://w3id.org/cdmx/agua/municipio/",
    "acu": "https://w3id.org/cdmx/agua/acuifero/", "pozo": "https://w3id.org/cdmx/agua/pozo/",
    "presa": "https://w3id.org/cdmx/agua/presa/", "sitio": "https://w3id.org/cdmx/agua/sitio/",
    "cc": "https://w3id.org/cdmx/agua/coloniaConapo/", "col": "https://w3id.org/cdmx/agua/colonia/",
    "alc": "https://w3id.org/cdmx/agua/alcaldia/", "geo": "http://www.opengis.net/ont/geosparql#",
    "skos": "http://www.w3.org/2004/02/skos/core#", "prov": "http://www.w3.org/ns/prov#",
    "dcterms": "http://purl.org/dc/terms/",
}


def materializar() -> rdflib.Graph:
    # El conector entrega los NULL como el texto "None": sin esto, el grafo afirmaria un dato inexistente
    cfg = (f"[CONFIGURATION]\noutput_format=N-TRIPLES\nna_values=,#N/A,N/A,NULL,None,none,nan,NaN\n\n"
           f"[DataSource1]\nmappings={(GRAFO / 'mapeo_zm.r2rml.ttl').as_posix()}\ndb_url={DSN}\n")
    fh = tempfile.NamedTemporaryFile("w", suffix=".ini", delete=False, encoding="utf-8")
    fh.write(cfg)
    fh.close()
    try:
        g = morph_kgc.materialize(fh.name)
    finally:
        os.unlink(fh.name)
    g.parse(GRAFO / "esquema_zm.ttl", format="turtle")
    return g


def huella(g: rdflib.Graph) -> str:
    """SHA-256 de las tripletas ordenadas: no depende del formato del archivo."""
    return hashlib.sha256("\n".join(sorted(" ".join(t.n3() for t in s) for s in g)).encode("utf-8")).hexdigest()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    g = materializar()
    for p, iri in PREFIJOS.items():
        g.bind(p, iri)
    g.serialize(destination=SALIDA, format="turtle", encoding="utf-8")
    resumen = {"tripletas": len(g), "sha256": huella(g),
               "consultas": sorted(p.name for p in (GRAFO / "consultas").glob("*.rq"))}
    RESUMEN.write_text(json.dumps(resumen, indent=1) + "\n", encoding="utf-8")
    print(f"{len(g):,} tripletas; {SALIDA.stat().st_size / 1024 / 1024:.1f} MB; sha256 {resumen['sha256'][:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
