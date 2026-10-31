"""Calidad del agua por sitio (RENAMECA), periodo 2012-2025.

Cada archivo trae una fila por sitio con un valor y una clasificacion por parametro, mas el
semaforo. Aqui pasa a formato largo. Los valores con < o > estan fuera del limite de deteccion:
se guardan con su signo y no se tratan como una medicion exacta.
"""
from __future__ import annotations

import re

import numpy as np
import openpyxl
import pandas as pd

from comun import copiar, normalizar, registrar, verificar
import geo

ARCHIVOS = (("D16a", "subterranea", "SITIO", "ACUIFERO", "PERIODO"),
            ("D16b", "superficial", "NOMBRE DEL SITIO", "CUENCA", "AÑO"))
FIJAS = {"CLAVE SITIO", "SITIO", "NOMBRE DEL SITIO", "ORGANISMO_DE_CUENCA", "ESTADO", "MUNICIPIO", "ACUIFERO", "CUENCA",
         "CUERPO DE AGUA", "TIPO", "SUBTIPO", "LATITUD", "LONGITUD", "PERIODO", "AÑO", "SEMÁFORO", "SEMAFORO", "CONTAMINANTES"}
VALOR = re.compile(r"^\s*([<>])?\s*(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\s*$")


def diccionario(wb) -> dict[str, str]:
    hoja = next(s for s in wb.sheetnames if s.lower().startswith("diccionario"))
    return {str(r[0]).strip(): str(r[1]).strip() for r in wb[hoja].iter_rows(min_row=2, values_only=True) if r[0]}


def pares(columnas: list[str]) -> dict[str, list[str]]:
    """{parametro: [columnas de calidad]}: cada parametro va seguido de sus clasificaciones."""
    r: dict[str, list[str]] = {}
    actual = None
    for c in columnas:
        if c in FIJAS:
            actual = None
        elif c.upper().startswith("CALIDAD"):
            if actual:
                r[actual].append(c)
        else:
            actual = c
            r[c] = []
    return r


def limpiar(s) -> str | None:
    if s is None:
        return None
    t = re.sub(r"\s+", " ", str(s)).strip()
    return t or None


def ejecutar(cur, cache) -> None:
    mun = geo.municipios(cache)
    acu = geo.acuiferos(cache)
    for id_f, tipo, col_nombre, col_unidad, col_periodo in ARCHIVOS:
        p, _ = verificar(id_f, cache)
        wb = openpyxl.load_workbook(p, read_only=True)
        hoja = wb[wb.sheetnames[0]]
        filas = hoja.iter_rows(values_only=True)
        cols = [str(c).strip() for c in next(filas)]
        d = pd.DataFrame([r for r in filas if r[0] is not None], columns=cols)
        dic = diccionario(wb)
        par = pares(cols)

        d["clave"] = d["CLAVE SITIO"].map(limpiar)
        repetidas = int(d.clave.duplicated().sum())
        d = d.drop_duplicates("clave").reset_index(drop=True)
        lat, lon = pd.to_numeric(d.LATITUD, errors="coerce"), pd.to_numeric(d.LONGITUD, errors="coerce")
        malas = ~(lat.between(14, 33) & lon.between(-118, -86))
        lat, lon = lat.mask(malas), lon.mask(malas)
        d["cve_mun"], d["clv_acui"] = None, None
        ok = lat.notna().values
        d.loc[ok, "cve_mun"] = geo.puntos_a_municipio(lon[ok].values, lat[ok].values, mun).values
        d.loc[ok, "clv_acui"] = geo.puntos_en(lon[ok].values, lat[ok].values, acu, "clv_acui").values
        semaforo = "SEMÁFORO" if "SEMÁFORO" in d else "SEMAFORO"
        s = pd.DataFrame({"clave_sitio": d.clave, "tipo_agua": tipo, "nombre": d[col_nombre].map(limpiar),
                          "organismo_cuenca": d.ORGANISMO_DE_CUENCA.map(limpiar), "estado": d.ESTADO.map(limpiar),
                          "municipio": d.MUNICIPIO.map(limpiar), "unidad_hidrologica": d[col_unidad].map(limpiar),
                          "subtipo": d.SUBTIPO.map(limpiar), "latitud": lat, "longitud": lon,
                          "periodo": d[col_periodo].map(limpiar), "semaforo": d[semaforo].map(limpiar),
                          "contaminantes": d.CONTAMINANTES.map(limpiar), "cve_mun": d.cve_mun, "clv_acui": d.clv_acui})
        n = copiar(cur, "dim_sitio_calidad", list(s.columns), s)
        registrar(cur, id_f, "dim_sitio_calidad", n, f"{repetidas} claves repetidas omitidas, {int(malas.sum())} sin coordenada valida", cache)
        cur.execute("SELECT clave_sitio, id_sitio FROM dim_sitio_calidad WHERE tipo_agua = %s", (tipo,))
        ids = dict(cur.fetchall())

        por_norm = {normalizar(k): v for k, v in dic.items()}
        q = pd.DataFrame({"tipo_agua": tipo, "parametro": list(par), "descripcion": [dic.get(c) or por_norm.get(normalizar(c)) for c in par]})
        copiar(cur, "dim_parametro_calidad", ["tipo_agua", "parametro", "descripcion"], q)
        cur.execute("SELECT parametro, id_parametro FROM dim_parametro_calidad WHERE tipo_agua = %s", (tipo,))
        id_par = dict(cur.fetchall())

        partes = []
        for c, calidades in par.items():
            m = d[c].map(limpiar).astype("object").str.extract(VALOR)
            cal = d[calidades].apply(lambda r: " / ".join(x for x in map(limpiar, r) if x) or None, axis=1) if calidades else None
            f = pd.DataFrame({"id_sitio": d.clave.map(ids), "id_parametro": id_par[c], "valor": pd.to_numeric(m[1]),
                              "limite": m[0], "calidad": cal})
            partes.append(f[f.valor.notna() | (f.calidad.notna() if calidades else False)])
        f = pd.concat(partes, ignore_index=True)
        f["limite"] = f.limite.replace({np.nan: None})
        n = copiar(cur, "fact_calidad_agua", ["id_sitio", "id_parametro", "valor", "limite", "calidad"], f)
        registrar(cur, id_f, "fact_calidad_agua", n, f"{len(par)} parametros en formato largo", cache)
