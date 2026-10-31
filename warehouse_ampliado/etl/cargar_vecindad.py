"""Vecindad real entre poligonos oficiales: municipios de la ZM y colonias de CONAPO.

Sustituye, para el grafo metropolitano, la proximidad entre centroides del grafo original.
"""
from __future__ import annotations

import geopandas as gpd
import pandas as pd

import geo
from comun import copiar, registrar, verificar

# Margen para medir la frontera comun y minimo para contarla: unos metros de contacto entre
# esquinas no son una frontera. Ver el comentario de puente_municipio_vecino en el DDL.
TOLERANCIA_M = 2
FRONTERA_MINIMA_KM = 0.05


def municipios_vecinos(cur, cache) -> None:
    cur.execute("SELECT cve_mun FROM dim_municipio WHERE en_zm_ciudad_mexico")
    zm = {r[0] for r in cur.fetchall()}
    mun = geo.municipios(cache)
    m = mun[mun.cve_mun.isin(zm)].reset_index(drop=True)
    j = gpd.sjoin(m, m, predicate="intersects")
    j = j[j.cve_mun_left < j.cve_mun_right]
    poligono = m.set_index("cve_mun").geometry
    filas = []
    for a, b in zip(j.cve_mun_left, j.cve_mun_right):
        km = poligono[a].boundary.intersection(poligono[b].buffer(TOLERANCIA_M)).length / 1000
        if km >= FRONTERA_MINIMA_KM:
            filas += [(a, b, round(km, 3)), (b, a, round(km, 3))]
    d = pd.DataFrame(filas, columns=["cve_mun", "cve_vecino", "frontera_km"]).sort_values(["cve_mun", "cve_vecino"])
    copiar(cur, "puente_municipio_vecino", ["cve_mun", "cve_vecino", "frontera_km"], d)
    for id_fuente, ent in (("B3", "09"), ("B8", "15"), ("B11", "13")):
        registrar(cur, id_fuente, "puente_municipio_vecino", int((d.cve_mun.str[:2] == ent).sum()),
                  f"frontera comun de al menos {FRONTERA_MINIMA_KM * 1000:.0f} m", cache)


def colonias_vecinas(cur, cache) -> None:
    cur.execute("""SELECT cve_col FROM dim_colonia_conapo c JOIN dim_municipio m USING (cve_mun)
                   WHERE m.en_zm_ciudad_mexico""")
    ids = {r[0] for r in cur.fetchall()}
    p, _ = verificar("D15", cache)
    g = gpd.read_file(f"zip://{p.as_posix()}!colonias_imc2020.shp", columns=["CVE_COL", "CVE_ENT"],
                      where="CVE_ENT IN ('09', '13', '15')")
    g["cve_col"] = g.CVE_COL.str.replace("_", "").astype("int64")
    g = g[g.cve_col.isin(ids)].reset_index(drop=True)
    g["geometry"] = g.geometry.make_valid()
    capa = g[["cve_col", "geometry"]]
    j = gpd.sjoin(capa, capa, predicate="touches")
    j = j[j.cve_col_left != j.cve_col_right]
    d = pd.DataFrame({"cve_col": j.cve_col_left.values, "cve_vecina": j.cve_col_right.values}).drop_duplicates()
    d = d.sort_values(["cve_col", "cve_vecina"])
    copiar(cur, "puente_colonia_vecina", ["cve_col", "cve_vecina"], d)
    registrar(cur, "D15", "puente_colonia_vecina", len(d), "relacion touches estricta", cache)


def ejecutar(cur, cache) -> None:
    municipios_vecinos(cur, cache)
    colonias_vecinas(cur, cache)
