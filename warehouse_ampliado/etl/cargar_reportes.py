"""Reportes ciudadanos de agua de SACMEX, 2018 a 2024.

Sigue la regla de Actronix09/fuentes-alternas: un reporte se ubica en una colonia por
nombre normalizado o, si no coincide, por el punto de consumo mas cercano a menos de 1 km.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from comun import asegurar_fechas, copiar, normalizar, registrar, verificar
import geo

DISTANCIA_MAX_M = 1000
LAT, LON = (19.00, 19.65), (-99.40, -98.90)


def leer(cache) -> pd.DataFrame:
    p, _ = verificar("C1h", cache)
    h = pd.read_csv(p, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    h = pd.DataFrame({"recurso": "historico_2018_2021", "folio": h.folio, "fecha": h.fecha, "clasificacion": "Agua Potable",
                      "reporte": h.tipo_de_falla, "medio": "No registrado (sistema anterior a 2022)",
                      "alcaldia": h.alcaldia, "colonia": h.colonia_datos_abiertos, "latitud": h.latitud, "longitud": h.longitud})
    p, _ = verificar("C1i", cache)
    i = pd.read_csv(p, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    i = pd.DataFrame({"recurso": "incidentes_2022_2024", "folio": i.id_reporte, "fecha": i.fecha_reporte,
                      "clasificacion": i.clasificacion.replace({"": "Sin clasificación", "NA": "Sin clasificación"}),
                      "reporte": i.reporte, "medio": i.medio_recepcion.replace({"": "No registrado", "NA": "No registrado"}),
                      "alcaldia": i.alcaldia_catalogo, "colonia": i.colonia_catalogo, "latitud": i.latitud, "longitud": i.longitud})
    return pd.concat([h, i], ignore_index=True)


def ejecutar(cur, cache) -> None:
    d = leer(cache)
    leidos = len(d)
    d = d[~d.folio.isin(["", "NA"])].drop_duplicates(["recurso", "folio"])
    d = d[~d.fecha.isin(["", "NA"]) & ~d.reporte.isin(["", "NA"])].copy()
    d["fecha"] = pd.to_datetime(d.fecha, errors="coerce")
    d = d[d.fecha.notna()].copy()
    lat, lon = pd.to_numeric(d.latitud, errors="coerce"), pd.to_numeric(d.longitud, errors="coerce")
    fuera = ~(lat.between(*LAT) & lon.between(*LON))
    d["latitud"], d["longitud"] = lat.mask(fuera), lon.mask(fuera)
    d["alcaldia_norm"] = d.alcaldia.map(normalizar)
    d["colonia_norm"] = d.colonia.map(normalizar)

    tipos = d[["clasificacion", "reporte"]].drop_duplicates().sort_values(["clasificacion", "reporte"])
    copiar(cur, "dim_tipo_reporte", ["clasificacion", "reporte"], tipos)
    medios = d[["medio"]].drop_duplicates().sort_values("medio")
    copiar(cur, "dim_medio_recepcion", ["medio"], medios)
    cur.execute("SELECT clasificacion, reporte, id_tipo_reporte FROM dim_tipo_reporte")
    id_tipo = {(a, b): c for a, b, c in cur.fetchall()}
    cur.execute("SELECT medio, id_medio_recepcion FROM dim_medio_recepcion")
    id_medio = dict(cur.fetchall())

    cur.execute("SELECT id_ubicacion, alcaldia, colonia_norm, cve_mun FROM dim_ubicacion")
    filas = cur.fetchall()
    por_nombre = {(normalizar(a), c): i for i, a, c, _ in filas}
    alc_mun = {normalizar(a): m for _, a, _, m in filas}

    d["id_ubicacion"] = [por_nombre.get(k) for k in zip(d.alcaldia_norm, d.colonia_norm)]
    d["id_ubicacion"] = pd.to_numeric(d.id_ubicacion, errors="coerce")
    d["metodo_ubicacion"] = np.where(d.id_ubicacion.notna(), "nombre", None)
    d["distancia_m"] = np.nan

    sac = geo.puntos_sacmex(cur)
    falta = d.id_ubicacion.isna() & d.latitud.notna()
    x, y = geo.A_METROS.transform(d.longitud[falta].values, d.latitud[falta].values)
    ids, dist = geo.mas_cercano(sac, x, y, max_m=DISTANCIA_MAX_M)
    d.loc[falta, "id_ubicacion"] = ids
    d.loc[falta, "distancia_m"] = np.round(dist, 1)
    d.loc[falta & d.id_ubicacion.notna(), "metodo_ubicacion"] = "punto_cercano"

    tiempo = asegurar_fechas(cur, d.fecha)
    f = pd.DataFrame({"recurso": d.recurso, "folio": d.folio, "id_tiempo": d.fecha.dt.normalize().map(tiempo),
                      "id_ubicacion": d.id_ubicacion.astype("Int64"),
                      "id_tipo_reporte": [id_tipo[k] for k in zip(d.clasificacion, d.reporte)],
                      "id_medio_recepcion": d.medio.map(id_medio), "metodo_ubicacion": d.metodo_ubicacion,
                      "distancia_m": d.distancia_m, "latitud": d.latitud, "longitud": d.longitud,
                      "cve_mun": d.alcaldia_norm.map(alc_mun)})
    n = copiar(cur, "fact_reporte_agua", list(f.columns), f)
    ubicados = int(f.id_ubicacion.notna().sum())
    for id_f in ("C1h", "C1i"):
        registrar(cur, id_f, "fact_reporte_agua", int((d.recurso == {"C1h": "historico_2018_2021", "C1i": "incidentes_2022_2024"}[id_f]).sum()),
                  f"leidos {leidos}, ubicados {ubicados} de {n}", cache)
    registrar(cur, "C1h", "dim_tipo_reporte", len(tipos), "tambien usa C1i", cache)
    registrar(cur, "C1h", "dim_medio_recepcion", len(medios), "tambien usa C1i", cache)
