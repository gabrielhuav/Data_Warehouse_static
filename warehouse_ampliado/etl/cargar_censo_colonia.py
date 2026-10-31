"""Censo 2020 por colonia: cada manzana urbana hereda la colonia del punto de SACMEX mas cercano.

Sirve como denominador de consumo. No sustituye a los poligonos oficiales de colonia, que
siguen bloqueados en el portal de la CDMX: es una aproximacion por proximidad dentro de la
misma alcaldia, y las manzanas a mas de MAX_M quedan sin colonia.
"""
from __future__ import annotations

import zipfile

import numpy as np
import pandas as pd

from comun import abrir_csv_zip, registrar, verificar
import geo

MAX_M = 750


def ejecutar(cur, cache) -> None:
    p, _ = verificar("B3", cache)
    mz = geo.capa_zip(p, "09m").to_crs(geo.CRS_METROS)
    c = mz.geometry.representative_point()
    g = pd.DataFrame({"cvegeo": mz.CVEGEO, "x": c.x.values, "y": c.y.values, "cve_mun": mz.CVEGEO.str[:5]})

    p1, _ = verificar("B1", cache)
    with zipfile.ZipFile(p1) as z:
        d = abrir_csv_zip(z, "conjunto_de_datos_ageb_urbana_09_cpv2020.csv")
    d.columns = [x.strip().upper() for x in d.columns]
    m = d[(d.MZA != "000") & (d.AGEB != "0000")].copy()
    m["cvegeo"] = m.ENTIDAD + m.MUN + m.LOC + m.AGEB + m.MZA
    for col in ("POBTOT", "TVIVPARHAB", "VPH_AGUADV", "VPH_TINACO", "VPH_CISTER"):
        m[col] = pd.to_numeric(m[col], errors="coerce")
    j = m.merge(g, on="cvegeo", how="inner", validate="1:1")

    sac = geo.puntos_sacmex(cur)
    ids, dist = geo.mas_cercano(sac, j.x.values, j.y.values, max_m=MAX_M, mun=j.cve_mun.values)
    j["id_ubicacion"] = ids
    con = j[j.id_ubicacion.notna()]
    r = con.groupby("id_ubicacion").agg(n=("cvegeo", "size"), pob=("POBTOT", "sum"), viv=("TVIVPARHAB", "sum"),
                                        agua=("VPH_AGUADV", "sum"), tin=("VPH_TINACO", "sum"),
                                        cis=("VPH_CISTER", "sum")).reset_index()
    filas = [(int(a.n), int(a.pob), int(a.viv), int(a.agua), int(a.tin), int(a.cis), int(a.id_ubicacion))
             for a in r.itertuples()]
    cur.executemany("""UPDATE dim_ubicacion SET n_manzanas_censo=%s, pob_censo_2020=%s, viv_hab_censo_2020=%s,
                       vph_agua_dentro_2020=%s, vph_tinaco_2020=%s, vph_cisterna_2020=%s WHERE id_ubicacion=%s""", filas)
    pob_total, pob_asig = j.POBTOT.sum(), con.POBTOT.sum()
    nota = (f"{len(con):,} de {len(j):,} manzanas a menos de {MAX_M} m; {100 * pob_asig / pob_total:.1f} % de la poblacion "
            f"de las manzanas; mediana {np.nanmedian(dist):.0f} m")
    registrar(cur, "B1", "dim_ubicacion", len(r), nota, cache)
    registrar(cur, "B3", "dim_ubicacion", len(r), "poligonos de manzana para el cruce", cache)
