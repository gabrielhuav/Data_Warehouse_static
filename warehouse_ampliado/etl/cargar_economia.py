"""Actividad economica: Censos Economicos 2019 por municipio y DENUE por municipio y colonia.

El DENUE es la edicion vigente al descargar (mayo de 2026), no 2019; las columnas lo dicen.
"""
from __future__ import annotations

import io
import zipfile

import pandas as pd

from comun import copiar, registrar, verificar
import geo

# Giros de uso intensivo de agua. Es una decision del analisis, no un dato de la fuente:
# industria alimentaria y de bebidas, hoteles, restaurantes y lavanderias (SCIAN 2018).
SCIAN_AGUA = ("311", "312", "7211", "722", "8122")


def censo_economico(cur, cache) -> None:
    cur.execute("""CREATE TEMP TABLE t_ce (cve_mun CHAR(5), ue BIGINT, personal BIGINT, produccion NUMERIC) ON COMMIT DROP""")
    for id_f, nombre in (("B4", "conjunto_de_datos/ce2019_cdmx.csv"), ("B9c", "conjunto_de_datos/ce2019_mex.csv")):
        p, _ = verificar(id_f, cache)
        with zipfile.ZipFile(p) as z:
            raw = z.read(nombre)
        d = pd.read_csv(io.BytesIO(raw), dtype=str, encoding="utf-8-sig", keep_default_na=False, index_col=False,
                        usecols=["ENTIDAD", "MUNICIPIO", "CODIGO", "ID_ESTRATO", "UE", "H001A", "A111A"])
        for c in d.columns:
            d[c] = d[c].str.strip()
        t = d[(d.MUNICIPIO != "") & (d.CODIGO == "") & (d.ID_ESTRATO == "")]
        f = pd.DataFrame({"cve_mun": t.ENTIDAD + t.MUNICIPIO, "ue": pd.to_numeric(t.UE, errors="coerce").astype("Int64"),
                          "personal": pd.to_numeric(t.H001A, errors="coerce").round().astype("Int64"),
                          "produccion": pd.to_numeric(t.A111A, errors="coerce")})
        n = copiar(cur, "t_ce", ["cve_mun", "ue", "personal", "produccion"], f)
        registrar(cur, id_f, "dim_municipio", n, "totales municipales, personal ocupado y produccion bruta", cache)
    cur.execute("""UPDATE dim_municipio d SET ue_2019 = t.ue, personal_ocupado_2019 = t.personal,
                   produccion_bruta_mdp_2019 = t.produccion FROM t_ce t WHERE d.cve_mun = t.cve_mun""")


def denue(cur, cache) -> None:
    filas = []
    for id_f in ("B5", "B9d1", "B9d2"):
        p, _ = verificar(id_f, cache)
        with zipfile.ZipFile(p) as z:
            n = [x for x in z.namelist() if x.endswith(".csv") and "conjunto_de_datos" in x]
            for nombre in n:
                with z.open(nombre) as fh:
                    d = pd.read_csv(fh, dtype=str, encoding="latin-1", keep_default_na=False,
                                    usecols=["codigo_act", "cve_ent", "cve_mun", "latitud", "longitud"])
                d["fuente"] = id_f
                filas.append(d)
    d = pd.concat(filas, ignore_index=True)
    d["mun"] = d.cve_ent.str.zfill(2) + d.cve_mun.str.zfill(3)
    d["agua"] = d.codigo_act.str.startswith(SCIAN_AGUA)
    r = d.groupby("mun").agg(ue=("mun", "size"), agua=("agua", "sum")).reset_index()
    cur.execute("CREATE TEMP TABLE t_den (cve_mun CHAR(5), ue BIGINT, agua BIGINT) ON COMMIT DROP")
    copiar(cur, "t_den", ["cve_mun", "ue", "agua"], r.rename(columns={"mun": "cve_mun"}))
    cur.execute("""UPDATE dim_municipio d SET ue_denue_2026 = t.ue, ue_agua_intensiva_denue_2026 = t.agua
                   FROM t_den t WHERE d.cve_mun = t.cve_mun""")
    for id_f in ("B5", "B9d1", "B9d2"):
        registrar(cur, id_f, "dim_municipio", int((d.fuente == id_f).sum()), "establecimientos agregados por municipio", cache)

    c = d[d.cve_ent.str.zfill(2) == "09"].copy()
    lat, lon = pd.to_numeric(c.latitud, errors="coerce"), pd.to_numeric(c.longitud, errors="coerce")
    ok = lat.notna() & lon.notna()
    c = c[ok]
    x, y = geo.A_METROS.transform(lon[ok].values, lat[ok].values)
    ids, _ = geo.mas_cercano(geo.puntos_sacmex(cur), x, y, max_m=750, mun=c.mun.values)
    c["id_ubicacion"] = ids
    con = c[c.id_ubicacion.notna()]
    a = con.groupby("id_ubicacion").agg(ue=("mun", "size"), agua=("agua", "sum")).reset_index()
    cur.executemany("UPDATE dim_ubicacion SET ue_denue_2026=%s, ue_agua_intensiva_denue_2026=%s WHERE id_ubicacion=%s",
                    [(int(r.ue), int(r.agua), int(r.id_ubicacion)) for r in a.itertuples()])
    registrar(cur, "B5", "dim_ubicacion", len(a), f"{len(con):,} de {len(c):,} establecimientos a menos de 750 m", cache)


def ejecutar(cur, cache) -> None:
    censo_economico(cur, cache)
    denue(cur, cache)
