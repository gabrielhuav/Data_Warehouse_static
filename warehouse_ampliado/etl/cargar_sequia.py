"""Monitor de Sequia: un corte por municipio y fecha, de 2003 a la version congelada."""
from __future__ import annotations

import datetime as dt
import re

import openpyxl
import pandas as pd

from comun import asegurar_fechas, copiar, registrar, verificar


def categorias(wb) -> pd.DataFrame:
    """Lee las categorias de la hoja NOTAS. 'Sin Sequia' no tiene clave en el archivo:
    es la celda vacia, y aqui se guarda como SIN con severidad -1."""
    filas, sin = [], None
    for r in wb["NOTAS"].iter_rows(values_only=True):
        t = [str(x).strip() for x in r if x is not None]
        for i, c in enumerate(t):
            if re.fullmatch(r"D[0-4]", c) and i:
                filas.append((c, t[i - 1], int(c[1])))
            elif re.fullmatch(r"Sin Sequ.a", c):
                sin = ("SIN", c, -1)
    if len(filas) != 5 or sin is None:
        raise ValueError(f"hoja NOTAS inesperada: {filas} {sin}")
    return pd.DataFrame(filas + [sin], columns=["categoria", "descripcion", "severidad"])


def ejecutar(cur, cache) -> None:
    p, _ = verificar("D7", cache)
    wb = openpyxl.load_workbook(p, read_only=True)
    cat = categorias(wb)
    copiar(cur, "dim_categoria_sequia", ["categoria", "descripcion", "severidad"], cat)
    registrar(cur, "D7", "dim_categoria_sequia", len(cat), "hoja NOTAS", cache)
    cur.execute("SELECT categoria, id_categoria FROM dim_categoria_sequia")
    ids = dict(cur.fetchall())
    cur.execute("SELECT cve_mun FROM dim_municipio")
    validos = {r[0] for r in cur.fetchall()}

    filas = wb["MUNICIPIOS"].iter_rows(values_only=True)
    hdr = list(next(filas))
    columnas = [(i, h) for i, h in enumerate(hdr) if isinstance(h, dt.datetime)]
    fechas = [pd.Timestamp(h) for _, h in columnas]
    tiempo = asegurar_fechas(cur, fechas)
    id_t = [tiempo[f] for f in fechas]

    claves, tiempos, categ = [], [], []
    for r in filas:
        if not r[0]:
            continue
        c = str(r[0]).zfill(5)
        if c not in validos:
            raise ValueError(f"municipio {c} fuera de dim_municipio")
        for (i, _), t in zip(columnas, id_t):
            claves.append(c)
            tiempos.append(t)
            categ.append(ids[r[i]] if r[i] else ids["SIN"])
    f = pd.DataFrame({"cve_mun": claves, "id_tiempo": tiempos, "id_categoria": categ})
    n = copiar(cur, "fact_sequia_municipio", ["cve_mun", "id_tiempo", "id_categoria"], f)
    registrar(cur, "D7", "fact_sequia_municipio", n, f"{len(fechas)} cortes, {fechas[0].date()} a {fechas[-1].date()}", cache)
