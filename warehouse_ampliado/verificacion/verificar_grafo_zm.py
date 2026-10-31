#!/usr/bin/env python3
"""Comprueba que el grafo metropolitano publicado es lo que dice la base de datos.

    python -I warehouse_ampliado/verificacion/verificar_grafo_zm.py

Vuelve a materializar el grafo desde el almacen y lo compara con ijcopi/kg_zm.ttl, contrasta sus
relaciones con las tablas y repite en SPARQL resultados que tambien se calculan en SQL. Corre las
consultas de ejemplo de la pagina y busca valores nulos convertidos en datos. Usa el entorno de
grafo/requirements.txt y escribe evidencia_grafo_zm.txt.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import psycopg2
import rdflib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "grafo"))
from materializar import DSN, GRAFO, RESUMEN, SALIDA, huella, materializar  # noqa: E402

AGUA = rdflib.Namespace("https://w3id.org/cdmx/agua/")
GEO = rdflib.Namespace("http://www.opengis.net/ont/geosparql#")
EVIDENCIA = GRAFO.parent / "verificacion" / "evidencia_grafo_zm.txt"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lineas = [f"Evidencia del grafo metropolitano, generada {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC", ""]
    fallos = 0

    def ok(cond: bool, texto: str) -> None:
        nonlocal fallos
        fallos += 0 if cond else 1
        lineas.append(f"[{'OK ' if cond else 'MAL'}] {texto}")
        print(lineas[-1])

    g = rdflib.Graph().parse(SALIDA, format="turtle")
    declarado = json.loads(RESUMEN.read_text(encoding="utf-8"))
    ok(len(g) == declarado["tripletas"], f"tripletas publicadas: {len(g):,}")
    ok(huella(g) == declarado["sha256"], f"sha256 de las tripletas {declarado['sha256'][:16]}")
    nuevo = materializar()
    ok(huella(nuevo) == declarado["sha256"], "materializar de nuevo desde el almacen da el mismo grafo")

    con = psycopg2.connect(DSN)
    cur = con.cursor()

    def sql(q: str):
        cur.execute(q)
        return cur.fetchall()

    def cuenta(q: str) -> int:
        return sql(q)[0][0]

    clases = (("Municipality", "dim_municipio WHERE en_zm_ciudad_mexico"), ("Aquifer", "v_acuiferos_zmvm"),
              ("Neighbourhood", "dim_colonia_conapo c JOIN dim_municipio m USING (cve_mun) WHERE m.en_zm_ciudad_mexico"))
    for clase, origen in clases:
        n = len(set(g.subjects(rdflib.RDF.type, AGUA[clase])))
        ok(n == cuenta(f"SELECT COUNT(*) FROM {origen}"), f"agua:{clase}: {n:,} instancias, igual que la base")
    relaciones = ((AGUA.sharesBoundaryWith, "puente_municipio_vecino"), (GEO.sfTouches, "puente_colonia_vecina"))
    for pred, tabla in relaciones:
        n = sum(1 for _ in g.triples((None, pred, None)))
        ok(n == cuenta(f"SELECT COUNT(*) FROM {tabla}"), f"{pred.split('/')[-1]}: {n:,} tripletas, igual que {tabla}")
        ok(all((o, pred, s) in g for s, _, o in g.triples((None, pred, None))), f"{pred.split('/')[-1]} es simetrica")

    nulos = [(s, p, o) for s, p, o in g if isinstance(o, rdflib.Literal) and str(o) in ("None", "nan", "NaN")]
    ok(not nulos, f"literales nulos convertidos en dato: {len(nulos)}")
    rotos = [o for _, _, o in g if isinstance(o, rdflib.URIRef) and str(o).endswith(("/None", "/nan"))]
    ok(not rotos, f"enlaces a recursos nulos: {len(rotos)}")
    sin_volumen = {str(s).rsplit("/", 1)[1] for s, _ in g.subject_objects(AGUA.volumeQuality)}
    con_litros = {str(s).rsplit("/", 1)[1] for s in g.subjects(rdflib.RDF.type, AGUA.Municipality)
                  if (s, AGUA.billedLitresPerDay, None) in g}
    ok(len(con_litros) == cuenta("SELECT COUNT(*) FROM v_zm_indicadores_agua WHERE litros_hab_dia_dom IS NOT NULL"),
       f"municipios con volumen: {len(con_litros)} de {len(sin_volumen)}; el resto no tiene la propiedad")

    consultas = sorted((GRAFO / "consultas").glob("*.rq"))
    resultados = {}
    for rq in consultas:
        texto = rq.read_text(encoding="utf-8")
        filas = list(g.query(texto))
        resultados[rq.stem] = filas
        ok(len(filas) > 0, f"{rq.stem}: {len(filas)} filas")

    frontera_sql = {(a, b) for a, b in sql("""
        SELECT m.nom_mun, n.nom_mun FROM puente_municipio_vecino v
        JOIN dim_municipio m ON m.cve_mun = v.cve_mun JOIN dim_municipio n ON n.cve_mun = v.cve_vecino
        WHERE m.cve_ent = '09' AND n.cve_ent <> '09'""")}
    frontera_rdf = {(str(f[0]), str(f[1])) for f in resultados["01_frontera_cdmx"]}
    ok(frontera_sql == frontera_rdf, f"la frontera de la CDMX coincide en SPARQL y SQL: {len(frontera_sql)} pares")
    completo = g.query("""
        PREFIX agua: <https://w3id.org/cdmx/agua/>
        PREFIX geo:  <http://www.opengis.net/ont/geosparql#>
        SELECT DISTINCT ?a ?b WHERE {
          ?a geo:sfTouches ?b ; agua:inMunicipality ?ma . ?b agua:inMunicipality ?mb .
          ?ma agua:isMexicoCityBorough true . ?mb agua:isMexicoCityBorough false .
        }""")
    pares = {(a, b) for a, b in completo}
    derivados = {(s, o) for s, o in g.subject_objects(AGUA.touchesAcrossCityLimit)
                 if str(next(g.objects(s, AGUA.inMunicipality))).rsplit("/", 1)[1][:2] == "09"}
    ok(pares == derivados, f"touchesAcrossCityLimit es igual al recorrido completo de sfTouches: {len(pares)} pares")
    enlaces = cuenta("SELECT COUNT(*) FROM dim_ubicacion WHERE cve_col_conapo IS NOT NULL")
    ok(sum(int(f[2]) for f in resultados["07_enlace_icokg"]) == enlaces,
       f"colonias del grafo original enlazadas: {enlaces:,}")
    con.close()

    lineas += ["", f"verificaciones fallidas: {fallos}"]
    print(lineas[-1])
    EVIDENCIA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
