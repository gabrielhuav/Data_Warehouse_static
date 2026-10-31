"""Geometria simplificada de la ZM para el mapa: municipios, colonias y acuiferos."""
from __future__ import annotations

import json

import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping

import geo
from comun import copiar, registrar, verificar

# Tolerancia de simplificacion en metros: suficiente para la escala de cada capa
TOLERANCIA_M = {"municipio": 100, "colonia": 20, "acuifero": 300}
DECIMALES = 5


def texto(geom) -> str:
    def redondear(c):
        return [round(c[0], DECIMALES), round(c[1], DECIMALES)] if isinstance(c[0], float) else [redondear(x) for x in c]

    m = mapping(geom)
    return json.dumps({"type": m["type"], "coordinates": redondear(m["coordinates"])}, separators=(",", ":"))


def filas(capa: str, g: gpd.GeoDataFrame, campo: str) -> pd.DataFrame:
    limpia = g.geometry.simplify(TOLERANCIA_M[capa], preserve_topology=True).to_crs("EPSG:4326")
    return pd.DataFrame({"capa": capa, "clave": g[campo].astype(str).values, "geojson": [texto(x) for x in limpia]})


def ejecutar(cur, cache) -> None:
    cur.execute("SELECT cve_mun FROM dim_municipio WHERE en_zm_ciudad_mexico")
    zm = {r[0] for r in cur.fetchall()}

    mun = geo.municipios(cache)
    d = filas("municipio", mun[mun.cve_mun.isin(zm)], "cve_mun")
    copiar(cur, "geo_territorio", ["capa", "clave", "geojson"], d)
    registrar(cur, "B3", "geo_territorio", int((d.clave.str[:2] == "09").sum()), "municipios, geometria simplificada", cache)
    registrar(cur, "B8", "geo_territorio", int((d.clave.str[:2] == "15").sum()), "municipios, geometria simplificada", cache)
    registrar(cur, "B11", "geo_territorio", int((d.clave.str[:2] == "13").sum()), "municipios, geometria simplificada", cache)

    cur.execute("""SELECT cve_col FROM dim_colonia_conapo c JOIN dim_municipio m USING (cve_mun)
                   WHERE m.en_zm_ciudad_mexico""")
    colonias = {r[0] for r in cur.fetchall()}
    p, _ = verificar("D15", cache)
    g = gpd.read_file(f"zip://{p.as_posix()}!colonias_imc2020.shp", columns=["CVE_COL", "CVE_ENT"],
                      where="CVE_ENT IN ('09', '13', '15')")
    g["cve_col"] = g.CVE_COL.str.replace("_", "").astype("int64")
    g = g[g.cve_col.isin(colonias)].to_crs(geo.CRS_METROS)
    d = filas("colonia", g, "cve_col")
    copiar(cur, "geo_territorio", ["capa", "clave", "geojson"], d)
    registrar(cur, "D15", "geo_territorio", len(d), f"colonias de la ZM, {len(colonias) - len(d)} sin poligono", cache)

    cur.execute("""SELECT DISTINCT clv_acui FROM puente_municipio_acuifero x JOIN dim_municipio m USING (cve_mun)
                   WHERE m.en_zm_ciudad_mexico AND x.pct_municipio >= 1""")
    claves = {r[0] for r in cur.fetchall()}
    a = geo.acuiferos(cache)
    d = filas("acuifero", a[a.clv_acui.isin(claves)], "clv_acui")
    copiar(cur, "geo_territorio", ["capa", "clave", "geojson"], d)
    registrar(cur, "D6", "geo_territorio", len(d), "acuiferos de la ZM, geometria simplificada", cache)
