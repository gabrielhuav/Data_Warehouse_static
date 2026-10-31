"""Velocidad vertical del terreno de Khorrami et al. (2023), por colonia y por municipio.

El archivo cubre de 18.25 a 20.40 N y de 99.50 a 98.20 O, asi que los municipios al poniente
de 99.5 O no tienen pixeles. El espaciado es de unos 350 m: una colonia chica puede tener
pocos pixeles, y n_pixeles lo deja a la vista.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from comun import copiar, registrar, verificar
import geo

MAX_M = 500


def resumen(g) -> pd.Series:
    return pd.Series({"n_pixeles": len(g), "vlm_media_cm_anio": g.v.mean(), "vlm_min_cm_anio": g.v.min(),
                      "vlm_p10_cm_anio": g.v.quantile(0.10), "vlm_p90_cm_anio": g.v.quantile(0.90),
                      "vlm_std_media_cm_anio": g.s.mean()})


def ejecutar(cur, cache) -> None:
    p, _ = verificar("A2", cache)
    d = pd.read_csv(p, header=None, names=["lon", "lat", "v", "s"])
    leidos = len(d)

    mun = geo.municipios(cache)
    d["cve_mun"] = geo.puntos_a_municipio(d.lon.values, d.lat.values, mun).values
    en = d[d.cve_mun.notna()]
    r = en.groupby("cve_mun")[["v", "s"]].apply(resumen).reset_index().round(4)
    r["n_pixeles"] = r.n_pixeles.astype(int)
    cols = ["cve_mun", "n_pixeles", "vlm_media_cm_anio", "vlm_min_cm_anio", "vlm_p10_cm_anio", "vlm_p90_cm_anio",
            "vlm_std_media_cm_anio"]
    n = copiar(cur, "fact_subsidencia_municipio", cols, r)
    registrar(cur, "A2", "fact_subsidencia_municipio", n, f"{len(en):,} de {leidos:,} pixeles dentro de los poligonos cargados", cache)

    sac = geo.puntos_sacmex(cur)
    c = en[en.cve_mun.str.startswith("09")].copy()
    x, y = geo.A_METROS.transform(c.lon.values, c.lat.values)
    ids, dist = geo.mas_cercano(sac, x, y, max_m=MAX_M, mun=c.cve_mun.values)
    c["id_ubicacion"] = ids
    con = c[c.id_ubicacion.notna()]
    r = con.groupby("id_ubicacion")[["v", "s"]].apply(resumen).reset_index().round(4)
    r["id_ubicacion"] = r.id_ubicacion.astype(int)
    r["n_pixeles"] = r.n_pixeles.astype(int)
    cols[0] = "id_ubicacion"
    n = copiar(cur, "fact_subsidencia_colonia", cols, r)
    registrar(cur, "A2", "fact_subsidencia_colonia", n,
              f"{len(con):,} de {len(c):,} pixeles de la CDMX a menos de {MAX_M} m, mediana {np.nanmedian(dist):.0f} m", cache)
