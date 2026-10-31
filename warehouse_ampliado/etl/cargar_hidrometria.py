"""Estaciones del SIH y series diarias de Hidro-MX para la zona de abasto de la ZMVM.

La zona son las estaciones dentro de la CDMX y el Estado de Mexico, la cuenca del Valle de
Mexico y las cajas de Cutzamala y Lerma Alto que define el propio dataset en
conf/cuencas_piloto.yaml. El periodo es el de los reportes de SACMEX.
"""
from __future__ import annotations

import io
import re
import zipfile

import pandas as pd
import pyarrow.parquet as pq

from comun import asegurar_fechas, copiar, registrar, verificar
from cargar_territorio import leer_csv
import geo

ANIOS = range(2018, 2025)
CUENCA_VM = "Valle de México"
UNIDADES = ("Cutzamala", "Lerma Alto")


def cajas(texto: str) -> dict[str, list[float]]:
    r = {}
    for u in UNIDADES:
        m = re.search(rf'nombre:\s*"{u}".*?bbox:\s*\[([^\]]+)\]', texto, re.S)
        if not m:
            raise ValueError(f"sin caja para {u}")
        r[u] = [float(x) for x in m.group(1).split(",")]
    return r


def ejecutar(cur, cache) -> None:
    p, _ = verificar("D10", cache)
    z = zipfile.ZipFile(p)

    pb, _ = verificar("D9b", cache)
    pa, _ = verificar("D9a", cache)
    h = leer_csv(pb).drop_duplicates("clave")
    pr = leer_csv(pa).drop_duplicates("clave")
    cand = pd.read_csv(io.BytesIO(z.read("processed/estaciones_candidatas_hidrometricas.csv")), dtype=str,
                       keep_default_na=False)
    columnas = ["clave", "nombre", "latitud", "longitud", "altitud", "estado", "municipio", "region_hidrologica", "cuenca"]
    pp = pd.DataFrame({"clave": pr.clave, "nombre": pr.nombre, "latitud": pr.latitud, "longitud": pr.longitud,
                       "altitud": pr.altitud, "estado": pr.estado, "municipio": pr.municipio,
                       "region_hidrologica": pr.num_region_hidrologica, "cuenca": pr.cuenca_de_disponibilidad})
    d = pd.concat([h[columnas], pp[columnas], cand[columnas]], ignore_index=True).drop_duplicates("clave")
    d["es_presa"] = d.clave.isin(pr.clave)
    d["cuenca_disponibilidad"] = d.clave.map(pr.set_index("clave").cuenca_de_disponibilidad)
    d["lat"], d["lon"] = pd.to_numeric(d.latitud, errors="coerce"), pd.to_numeric(d.longitud, errors="coerce")
    d = d[d.lat.between(14, 33) & d.lon.between(-118, -86)].copy()    # Hay coordenadas erroneas en el catalogo
    d["cve_mun"] = geo.puntos_a_municipio(d.lon.values, d.lat.values, geo.municipios(cache)).values

    c = cajas(z.read("conf/cuencas_piloto.yaml").decode("utf-8", "replace"))
    en_caja = pd.Series(False, index=d.index)
    for x0, y0, x1, y1 in c.values():
        en_caja |= d.lon.between(x0, x1) & d.lat.between(y0, y1)
    zona = d.cve_mun.fillna("").str[:2].isin(["09", "15"]) | d.cuenca.eq(CUENCA_VM) | en_caja

    dim = pd.DataFrame({"clave": d.clave, "nombre": d.nombre, "latitud": d.lat, "longitud": d.lon,
                        "altitud_m": pd.to_numeric(d.altitud, errors="coerce"), "estado": d.estado,
                        "municipio": d.municipio, "region_hidrologica": d.region_hidrologica,
                        "cuenca": d.cuenca.replace("", None), "cuenca_disponibilidad": d.cuenca_disponibilidad,
                        "es_presa": d.es_presa, "cve_mun": d.cve_mun})
    n = copiar(cur, "dim_estacion_hidrometrica", list(dim.columns), dim)
    registrar(cur, "D9b", "dim_estacion_hidrometrica", len(h), None, cache)
    registrar(cur, "D9a", "dim_estacion_hidrometrica", len(pr), "marca es_presa", cache)
    registrar(cur, "D10", "dim_estacion_hidrometrica", n, "union con las estaciones candidatas de Hidro-MX", cache)

    claves = set(d.clave[zona])
    partes = []
    for a in ANIOS:
        nombres = [x for x in z.namelist() if x.startswith(f"processed/series_hidrometricas.parquet/anio={a}/")
                   and x.endswith(".parquet")]
        for x in nombres:
            t = pq.read_table(io.BytesIO(z.read(x))).to_pandas()
            partes.append(t[t.clave_estacion.isin(claves)])
    s = pd.concat(partes, ignore_index=True)
    s = s[s.nivel_m.notna() | s.gasto_medio_m3s.notna()]
    s = s.drop_duplicates(["clave_estacion", "fecha"])
    tiempo = asegurar_fechas(cur, s.fecha)
    f = pd.DataFrame({"clave": s.clave_estacion, "id_tiempo": s.fecha.dt.normalize().map(tiempo), "nivel_m": s.nivel_m,
                      "gasto_m3s": s.gasto_medio_m3s, "calidad": s.calidad})
    n = copiar(cur, "fact_caudal_diario", list(f.columns), f)
    registrar(cur, "D10", "fact_caudal_diario", n, f"{s.clave_estacion.nunique()} estaciones con datos de "
              f"{len(claves)} en la zona, {ANIOS[0]} a {ANIOS[-1]}", cache)
