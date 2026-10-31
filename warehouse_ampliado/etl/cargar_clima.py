"""Clima mensual de 2019 de MexHiResClimDB, por colonia y por municipio.

En las colonias se promedia el valor de la celda de cada punto de SACMEX. En los municipios
se promedian las celdas cuyo centro cae dentro del poligono. id_tiempo es el ultimo dia del mes.
"""
from __future__ import annotations

import calendar
import re
import zipfile

import numpy as np
import pandas as pd
import rasterio
from rasterio.features import rasterize
from rasterio.windows import from_bounds, transform as trans_ventana

from comun import asegurar_fechas, copiar, registrar, verificar
import geo

VARIABLES = {"A1x": "tmax_c", "A1n": "tmin_c", "A1a": "tavg_c", "A1p": "precip_mm"}


def tifs(p) -> dict[int, str]:
    with zipfile.ZipFile(p) as z:
        n = [x for x in z.namelist() if x.lower().endswith(".tif")]
    r = {int(re.search(r"2019(\d\d)\.tif$", x, re.I).group(1)): x for x in n}
    if sorted(r) != list(range(1, 13)):
        raise ValueError(f"{p}: se esperaban 12 meses, hay {sorted(r)}")
    return r


def ejecutar(cur, cache) -> None:
    sac = geo.puntos_sacmex(cur)
    mun = geo.municipios(cache).to_crs("EPSG:4326")
    mun["id_r"] = np.arange(1, len(mun) + 1)
    x0, y0, x1, y1 = mun.total_bounds
    x0, y0, x1, y1 = x0 - 0.02, y0 - 0.02, x1 + 0.02, y1 + 0.02

    colonias, municipios = [], []
    mascara = None
    for id_f, var in VARIABLES.items():
        p, _ = verificar(id_f, cache)
        for mes, nombre in tifs(p).items():
            with rasterio.open(f"zip://{p.as_posix()}!{nombre}") as src:
                v = from_bounds(x0, y0, x1, y1, src.transform).round_offsets().round_lengths()
                a = src.read(1, window=v, masked=True).astype("float64").filled(np.nan)
                tr = trans_ventana(v, src.transform)
                if mascara is None or mascara.shape != a.shape:
                    mascara = rasterize(zip(mun.geometry, mun.id_r), out_shape=a.shape, transform=tr, fill=0,
                                        dtype="int32", all_touched=False)
                fil, col = rasterio.transform.rowcol(tr, sac.lon.values, sac.lat.values)
            s = pd.DataFrame({"id_ubicacion": sac.id_ubicacion.values, "v": a[np.asarray(fil), np.asarray(col)]})
            c = s.groupby("id_ubicacion").v.mean().rename("valor").reset_index()
            c["mes"], c["var"] = mes, var
            colonias.append(c)

            m = pd.DataFrame({"id_r": mascara.ravel(), "v": a.ravel()})
            m = m[(m.id_r > 0) & m.v.notna()].groupby("id_r").v.agg(["mean", "size"]).reset_index()
            m["mes"], m["var"] = mes, var
            municipios.append(m)
        print(f"  {var}: 12 meses")

    fechas = {mes: pd.Timestamp(2019, mes, calendar.monthrange(2019, mes)[1]) for mes in range(1, 13)}
    tiempo = asegurar_fechas(cur, list(fechas.values()))

    c = pd.concat(colonias).pivot_table(index=["id_ubicacion", "mes"], columns="var", values="valor").reset_index()
    c["id_tiempo"] = c.mes.map(lambda k: tiempo[fechas[k]])
    columnas = ["id_ubicacion", "id_tiempo"] + list(VARIABLES.values())
    n = copiar(cur, "fact_clima_colonia", columnas, c.round(3))
    for id_f in VARIABLES:
        registrar(cur, id_f, "fact_clima_colonia", n, None, cache)

    m = pd.concat(municipios)
    celdas = m.groupby(["id_r", "mes"])["size"].max().rename("n_celdas").reset_index()
    m = m.pivot_table(index=["id_r", "mes"], columns="var", values="mean").reset_index().merge(celdas, on=["id_r", "mes"])
    m = m.merge(mun[["id_r", "cve_mun"]], on="id_r")
    m["id_tiempo"] = m.mes.map(lambda k: tiempo[fechas[k]])
    columnas = ["cve_mun", "id_tiempo"] + list(VARIABLES.values()) + ["n_celdas"]
    n = copiar(cur, "fact_clima_municipio", columnas, m.round(3))
    for id_f in VARIABLES:
        registrar(cur, id_f, "fact_clima_municipio", n, None, cache)
