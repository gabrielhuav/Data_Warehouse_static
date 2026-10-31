"""Series diarias de las presas del Sistema de Informacion Hidrologica.

Incluyen las tres que la CONAGUA ubica en la cuenca del Rio Cutzamala (Valle de Bravo, Villa
Victoria y El Bosque) y las demas del Estado de Mexico. Se carga cada serie completa.
"""
from __future__ import annotations

import io

import pandas as pd

from comun import asegurar_fechas, copiar, fuentes, registrar, verificar

COLUMNAS = {"Nivel(m)": "nivel_m", "Precipitacion(mm)": "precipitacion_mm", "VolumenAlm(Mm3)": "volumen_hm3",
            "ObraToma(m3/s)": "obra_toma_m3s", "Vertedor(m3/s)": "vertedor_m3s", "Derrame(m3/s)": "derrame_m3s",
            "Evaporacion(mm)": "evaporacion_mm"}


def leer(p) -> pd.DataFrame:
    """El archivo trae un encabezado libre; la tabla empieza en la linea Estacion,Fecha,..."""
    t = p.read_bytes().decode("utf-8", "replace")
    ini = t.index("Estacion,Fecha")
    return pd.read_csv(io.StringIO(t[ini:]), dtype=str, keep_default_na=False)


def ejecutar(cur, cache) -> None:
    partes = {}
    for id_f in [k for k in fuentes() if k.startswith("D14")]:
        p, _ = verificar(id_f, cache)
        d = leer(p)
        if set(COLUMNAS) - set(d.columns):
            raise ValueError(f"{id_f}: faltan columnas {set(COLUMNAS) - set(d.columns)}")
        d = d.rename(columns=COLUMNAS)
        for c in COLUMNAS.values():
            d[c] = pd.to_numeric(d[c], errors="coerce")
        d["fecha"] = pd.to_datetime(d.Fecha, errors="coerce")
        d = d[d.fecha.notna()].dropna(subset=list(COLUMNAS.values()), how="all").drop_duplicates(["Estacion", "fecha"])
        partes[id_f] = d
    todo = pd.concat(partes.values(), ignore_index=True)
    tiempo = asegurar_fechas(cur, todo.fecha)
    for id_f, d in partes.items():
        # La clave sale del manifiesto: Taxhimay trae txmhd en minusculas dentro del archivo
        f = pd.DataFrame({"clave": id_f[3:], "id_tiempo": d.fecha.dt.normalize().map(tiempo)})
        for c in COLUMNAS.values():
            f[c] = d[c].values
        n = copiar(cur, "fact_presa_diaria", list(f.columns), f)
        registrar(cur, id_f, "fact_presa_diaria", n, f"{d.fecha.min().date()} a {d.fecha.max().date()}", cache)
