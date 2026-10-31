"""Geometria compartida: municipios del Marco Geoestadistico y puntos de consumo de SACMEX."""
from __future__ import annotations

import csv
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree

from comun import RAIZ, normalizar, verificar

CRS_METROS = "EPSG:6372"        # Lambert conforme conica ITRF2008, la de INEGI
CSV_CONSUMO = RAIZ.parent / "warehouse" / "data" / "consumo_agua_historico_2019.csv"
A_METROS = Transformer.from_crs("EPSG:4326", CRS_METROS, always_xy=True)
MARCOS = {"B3": "09", "B8": "15", "B11": "13"}


def capa_zip(p: Path, capa: str) -> gpd.GeoDataFrame:
    return gpd.read_file(f"zip://{p.as_posix()}!conjunto_de_datos/{capa}.shp")


def municipios(cache) -> gpd.GeoDataFrame:
    """Poligonos municipales de CDMX, Estado de Mexico e Hidalgo, en metros."""
    capas = []
    for id_f, ent in MARCOS.items():
        p, _ = verificar(id_f, cache)
        g = capa_zip(p, f"{ent}mun").to_crs(CRS_METROS)
        capas.append(g[["CVEGEO", "geometry"]].rename(columns={"CVEGEO": "cve_mun"}))
    return gpd.GeoDataFrame(pd.concat(capas, ignore_index=True), crs=CRS_METROS)


def puntos_a_municipio(lon, lat, mun: gpd.GeoDataFrame) -> pd.Series:
    """cve_mun de cada punto, o NaN si cae fuera de los poligonos cargados."""
    x, y = A_METROS.transform(np.asarray(lon, dtype=float), np.asarray(lat, dtype=float))
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(x, y), crs=CRS_METROS)
    j = gpd.sjoin(pts, mun, how="left", predicate="intersects")
    return j[~j.index.duplicated()].cve_mun.reindex(pts.index)


def acuiferos(cache) -> gpd.GeoDataFrame:
    """Poligonos de los 653 acuiferos, en metros."""
    p, _ = verificar("D6", cache)
    with zipfile.ZipFile(p) as z:
        capa = next(x for x in z.namelist() if x.endswith(".shp"))
    d = gpd.read_file(f"zip://{p.as_posix()}!{capa}")
    return gpd.GeoDataFrame({"clv_acui": d.CLV_ACUI.astype(str).str.zfill(4)}, geometry=d.geometry.make_valid(),
                            crs=d.crs).to_crs(CRS_METROS)


def puntos_en(lon, lat, poligonos: gpd.GeoDataFrame, campo: str) -> pd.Series:
    """Valor de campo del poligono que contiene cada punto, o NaN."""
    x, y = A_METROS.transform(np.asarray(lon, dtype=float), np.asarray(lat, dtype=float))
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(x, y), crs=CRS_METROS)
    j = gpd.sjoin(pts, poligonos, how="left", predicate="intersects")
    return j[~j.index.duplicated()][campo].reindex(pts.index)


def puntos_sacmex(cur) -> pd.DataFrame:
    """Cada punto distinto del CSV de consumo, con la colonia que le da SACMEX."""
    cur.execute("SELECT id_ubicacion, alcaldia, colonia, cve_mun FROM dim_ubicacion")
    ub = {(a, c): (i, m) for i, a, c, m in cur.fetchall()}
    vistos = {}
    with open(CSV_CONSUMO, encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh):
            k = ub.get((r["alcaldia"], r["colonia"]))
            if k is None or r["latitud"] in ("", "NA") or r["longitud"] in ("", "NA"):
                continue
            vistos[(float(r["longitud"]), float(r["latitud"]))] = k
    d = pd.DataFrame([(lo, la, i, m) for (lo, la), (i, m) in vistos.items()],
                     columns=["lon", "lat", "id_ubicacion", "cve_mun"])
    d["x"], d["y"] = A_METROS.transform(d.lon.values, d.lat.values)
    return d


def mas_cercano(pts: pd.DataFrame, x, y, max_m: float | None = None, mun=None) -> tuple[np.ndarray, np.ndarray]:
    """(id_ubicacion, distancia_m) del punto SACMEX mas cercano. Con mun busca dentro de la
    misma alcaldia, para que una manzana no herede la colonia de la alcaldia vecina."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    ids = np.full(len(x), np.nan)
    dist = np.full(len(x), np.nan)
    grupos = [(None, np.arange(len(x)), pts)] if mun is None else [
        (m, np.flatnonzero(np.asarray(mun) == m), pts[pts.cve_mun == m]) for m in pd.unique(np.asarray(mun))]
    for _, idx, sub in grupos:
        if len(idx) == 0 or sub.empty:
            continue
        arbol = cKDTree(sub[["x", "y"]].values)
        d, i = arbol.query(np.c_[x[idx], y[idx]])
        ids[idx] = sub.id_ubicacion.values[i]
        dist[idx] = d
    if max_m is not None:
        lejos = dist > max_m
        ids[lejos] = np.nan
        dist[lejos] = np.nan
    return ids, dist


__all__ = ["CRS_METROS", "A_METROS", "acuiferos", "capa_zip", "mas_cercano", "municipios", "normalizar",
           "puntos_a_municipio", "puntos_en", "puntos_sacmex"]
