"""Agua subterranea: acuiferos con disponibilidad, red piezometrica y puente con municipios.

Los dos archivos son shapefiles con MD5 oficial. El de disponibilidad corresponde al DOF del
9 de noviembre de 2023, como dice el nombre de su capa, y trae los poligonos de los 653 acuiferos.
"""
from __future__ import annotations

import zipfile

import geopandas as gpd
import pandas as pd

from comun import copiar, registrar, verificar
import geo


def capa(p) -> gpd.GeoDataFrame:
    with zipfile.ZipFile(p) as z:
        n = [x for x in z.namelist() if x.endswith(".shp")]
    if len(n) != 1:
        raise ValueError(f"{p}: se esperaba una capa, hay {n}")
    return gpd.read_file(f"zip://{p.as_posix()}!{n[0]}")


def cargar_acuiferos(cur, cache) -> gpd.GeoDataFrame:
    p, _ = verificar("D6", cache)
    d = capa(p)
    claves = d.CLV_ACUI.astype(str).str.zfill(4)
    a = pd.DataFrame({"clv_acui": claves, "nom_acui": d.NOM_ACUI, "clv_edo": d.CLV_EDO.astype(str).str.zfill(2),
                      "nom_edo": d.NOM_EDO, "clv_region": d.CLV_REGION, "nom_region": d.NOM_REGION, "area_km2": d.AREA_KM2})
    n = copiar(cur, "dim_acuifero", list(a.columns), a)
    registrar(cur, "D6", "dim_acuifero", n, "poligonos del DOF del 9 de noviembre de 2023", cache)
    f = pd.DataFrame({"clv_acui": claves, "recarga_total": d.RECARGA_TO, "descarga_natural": d.DESCARGA_N,
                      "vol_concesionado": d.VCAS, "vol_libre_alumbramiento": d.VEALA,
                      "vol_pendiente_titulacion": d.VAPTYR, "vol_reservas": d.VAPRH, "vol_extraccion": d.VEAS,
                      "dma_positiva": d.DMA_POSITI, "dma_negativa": d.DMA_NEGATI})
    n = copiar(cur, "fact_disponibilidad_acuifero", list(f.columns), f)
    registrar(cur, "D6", "fact_disponibilidad_acuifero", n, None, cache)
    return gpd.GeoDataFrame({"clv_acui": claves}, geometry=d.geometry.make_valid(), crs=d.crs).to_crs(geo.CRS_METROS)


def cargar_pozos(cur, cache, mun) -> None:
    p, _ = verificar("D5", cache)
    d = capa(p)
    lat, lon = d.LATITUD.astype(float), d.LONGITUD.astype(float)
    pozo = pd.DataFrame({"id_pozo": d.NUM_POZO, "nom_pozo": d.NOM_POZO, "clv_acui": d.CVE_ACUI.astype(str).str.zfill(4),
                         "cve_edo": d.CVE_EDO.astype(str).str.zfill(2), "nom_edo": d.NOM_EDO, "elev_brocal_m": d.ELEV_BROC,
                         "latitud": lat, "longitud": lon})
    pozo["cve_mun"] = geo.puntos_a_municipio(lon, lat, mun).values
    sac = geo.puntos_sacmex(cur)
    en_cdmx = pozo.cve_mun.fillna("").str.startswith("09").values
    x, y = geo.A_METROS.transform(lon.values, lat.values)
    ids, dist = geo.mas_cercano(sac, x[en_cdmx], y[en_cdmx], max_m=2000)
    pozo["id_ubicacion_cercana"] = pd.array([pd.NA] * len(pozo), dtype="Int64")
    pozo["distancia_ubicacion_m"] = float("nan")
    pozo.loc[en_cdmx, "id_ubicacion_cercana"] = pd.array(ids, dtype="Float64").astype("Int64")
    pozo.loc[en_cdmx, "distancia_ubicacion_m"] = dist.round(1)
    n = copiar(cur, "dim_pozo", list(pozo.columns), pozo)
    registrar(cur, "D5", "dim_pozo", n, f"{int(pozo.cve_mun.notna().sum())} con municipio por cruce espacial", cache)

    largo = pd.DataFrame(d.drop(columns="geometry")).melt(id_vars=["NUM_POZO"], value_vars=[c for c in d.columns if c.startswith("PNE_")],
                                                          var_name="c", value_name="v").dropna(subset=["v"])
    f = pd.DataFrame({"id_pozo": largo.NUM_POZO, "anio": largo.c.str[4:], "profundidad_nivel_m": largo.v})
    n = copiar(cur, "fact_nivel_piezometrico", list(f.columns), f)
    registrar(cur, "D5", "fact_nivel_piezometrico", n, "lecturas anuales no vacias", cache)


def cargar_puente(cur, cache, mun, acu) -> None:
    m = mun[["cve_mun", "geometry"]].copy()
    m["geometry"] = m.geometry.make_valid()
    m["area_mun"] = m.area
    x = gpd.overlay(m, acu.cx[m.total_bounds[0]:m.total_bounds[2], m.total_bounds[1]:m.total_bounds[3]],
                    how="intersection", keep_geom_type=True)
    x["a"] = x.area
    r = x.groupby(["cve_mun", "clv_acui", "area_mun"], as_index=False).a.sum()
    r["area_km2"] = (r.a / 1e6).round(3)
    r["pct_municipio"] = (100 * r.a / r.area_mun).round(2)
    r = r[r.area_km2 >= 0.01]
    cur.execute("SELECT cve_mun, clv_acui, count(*) FROM dim_pozo WHERE cve_mun IS NOT NULL GROUP BY 1, 2")
    pozos = {(a, b): c for a, b, c in cur.fetchall()}
    r["n_pozos"] = [pozos.get(k, 0) for k in zip(r.cve_mun, r.clv_acui)]
    n = copiar(cur, "puente_municipio_acuifero", ["cve_mun", "clv_acui", "area_km2", "pct_municipio", "n_pozos"], r)
    registrar(cur, "D6", "puente_municipio_acuifero", n, "interseccion de poligonos de municipios y acuiferos", cache)


def ejecutar(cur, cache) -> None:
    acu = cargar_acuiferos(cur, cache)
    mun = geo.municipios(cache)
    cargar_pozos(cur, cache, mun)
    cargar_puente(cur, cache, mun, acu)
    # Los poligonos municipales alimentan este cruce y los de hidrometria, clima y subsidencia
    for id_f, ent in geo.MARCOS.items():
        registrar(cur, id_f, "puente_municipio_acuifero", int(mun.cve_mun.str.startswith(ent).sum()),
                  "poligonos municipales para los cruces espaciales", cache)
