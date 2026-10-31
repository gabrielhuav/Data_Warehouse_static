"""Huerta-Vergara et al. (2022): indicadores por alcaldia, leidos del PDF del articulo.

El orden del texto extraido no respeta el de la tabla: Iztapalapa queda partida entre las
paginas 7 y 8. Por eso cada fila se asigna a la alcaldia que aun no tiene ese anio, y al
final se exige 16 alcaldias por 3 anios y se recalcula la normalizacion del Apendice B
con estos valores crudos. Si no coincide, el paso falla en vez de cargar datos mal leidos.
"""
from __future__ import annotations

import re

import pandas as pd
from pypdf import PdfReader

from comun import copiar, normalizar, registrar, verificar

ANIOS = ("2005", "2010", "2015")
FILA_T1 = re.compile(r"\b(2005|2010|2015)\s+([\d.]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+"
                     r"([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)")
COLS_T1 = ["area_urbana_km2", "poblacion", "unidades_economicas", "reportes_fugas", "reportes_falta_agua",
           "reportes_mala_calidad", "agua_tratada_ls", "agua_disponible_ls", "pib_mdp"]
FILA_E = re.compile(r"\b(2005|2010|2015)\s+([\d.]+)\s+([\d.]+)\s+(\d+)%\s+(Very\s+[Hh]igh|Very\s+low|High|Medium|Low)")
GRADO = r"(Very High|Very low|High|Medium|Low)"
FILA_T2 = re.compile(rf"^(.+?) {GRADO} ([\d.]+) {GRADO} ([\d.]+) {GRADO} ([\d.]+)\s*$")


def clave(alcaldia_texto: str, claves: dict[str, str]) -> str | None:
    n = normalizar(alcaldia_texto)
    if n is None:
        return None
    if n in claves:
        return claves[n]
    # Formas abreviadas o partidas: 'Cuajimalpa', 'Benito J', 'La Magdalena C'
    cand = [c for k, c in claves.items() if k.startswith(n) or n.startswith(k)]
    return cand[0] if len(set(cand)) == 1 else None


def tabla_1(paginas: list[str], claves: dict[str, str]) -> pd.DataFrame:
    filas: dict[tuple[str, str], list[str]] = {}
    actual = None
    pendiente = ""
    for pag in paginas:
        # En muchas filas el anio viene en su propia linea y los valores en la siguiente
        for ln in re.sub(r"\b(2005|2010|2015)\s*\n\s*", r"\1 ", pag).splitlines():
            t = ln.strip()
            m = FILA_T1.search(t)
            if m:
                pendiente = ""
                anio = m.group(1)
                destino = actual
                if destino is None or (destino, anio) in filas:
                    # Fila huerfana por el orden del PDF: va a la alcaldia a la que le falta ese anio
                    libres = [c for c in set(k[0] for k in filas) if (c, anio) not in filas]
                    if len(libres) != 1:
                        raise ValueError(f"no se puede asignar la fila {t!r}: candidatas {libres}")
                    destino = libres[0]
                filas[(destino, anio)] = list(m.groups()[1:])
                continue
            if re.fullmatch(r"(2005|2010|2015)", t):
                continue
            pendiente = f"{pendiente} {t}".strip()
            c = clave(pendiente, claves) or clave(t, claves)
            if c:
                actual, pendiente = c, ""
            elif len(pendiente) > 34:
                pendiente = t
    d = pd.DataFrame([[c, a] + v for (c, a), v in filas.items()], columns=["cve_mun", "anio"] + COLS_T1)
    for col in COLS_T1:
        d[col] = pd.to_numeric(d[col].str.replace(",", ""))
    return d


def tabla_2(pagina: str, claves: dict[str, str]) -> pd.DataFrame:
    filas = []
    for ln in pagina.splitlines():
        m = FILA_T2.match(ln.strip())
        if not m:
            continue
        c = clave(m.group(1), claves)
        if c is None:
            raise ValueError(f"Tabla 2: alcaldia no reconocida {m.group(1)!r}")
        for i, a in enumerate(ANIOS):
            filas.append((c, a, m.group(2 + 2 * i), float(m.group(3 + 2 * i))))
    return pd.DataFrame(filas, columns=["cve_mun", "anio", "grado_t2", "dotacion_lpcd"]).drop(columns="grado_t2")


def apendice_e(paginas: list[str], claves: dict[str, str]) -> pd.DataFrame:
    filas, actual, pend = [], None, ""
    texto = "\n".join(paginas)
    texto = texto[texto.find("Appendix E."):]
    # Une 'anio' en linea propia con los valores de la linea siguiente
    bloques = re.sub(r"\b(2005|2010|2015)\s*\n\s*", r"\1 ", texto)
    for ln in bloques.splitlines():
        t = ln.strip()
        m = FILA_E.search(t)
        if m:
            filas.append((actual, m.group(1), float(m.group(2)), float(m.group(3)), re.sub(r"\s+", " ", m.group(5))))
            continue
        if not t:
            continue
        pend = f"{pend} {t}".strip()
        c = clave(pend, claves) or clave(t, claves)
        if c:
            actual, pend = c, ""
        elif len(pend) > 34:
            pend = t
    return pd.DataFrame(filas, columns=["cve_mun", "anio", "indice_z", "percentil_beta", "grado_vulnerabilidad"])


def apendice_b(paginas: list[str], claves: dict[str, str]) -> pd.DataFrame:
    """Valores normalizados publicados, para validar la lectura de la Tabla 1."""
    texto = "\n".join(paginas)
    texto = texto[texto.find("Appendix B."):]
    texto = re.sub(r"\b(2005|2010|2015)\s*\n\s*", r"\1 ", texto)
    filas, actual, pend = [], None, ""
    patron = re.compile(r"\b(2005|2010|2015)\s+((?:[\d.]+\s+){8}[\d.]+)\s*$")
    for ln in texto.splitlines():
        t = ln.strip()
        m = patron.search(t)
        if m:
            filas.append([actual, m.group(1)] + [float(x) for x in m.group(2).split()])
            continue
        if not t:
            continue
        pend = f"{pend} {t}".strip()
        c = clave(pend, claves) or clave(t, claves)
        if c:
            actual, pend = c, ""
        elif len(pend) > 34:
            pend = t
    return pd.DataFrame(filas, columns=["cve_mun", "anio"] + COLS_T1)


def validar(t1: pd.DataFrame, b: pd.DataFrame) -> str:
    """Recalcula (x - min) / (max - min) por anio y lo compara con el Apendice B."""
    if len(t1) != 48 or t1.cve_mun.nunique() != 16:
        raise ValueError(f"Tabla 1 incompleta: {len(t1)} filas, {t1.cve_mun.nunique()} alcaldias")
    m = t1.merge(b, on=["cve_mun", "anio"], suffixes=("", "_b"), validate="1:1")
    if len(m) != 48:
        raise ValueError(f"Apendice B incompleto: cruzaron {len(m)} de 48")
    difs = []
    for col in ("area_urbana_km2", "poblacion", "unidades_economicas", "reportes_fugas", "reportes_falta_agua"):
        g = t1.groupby("anio")[col]
        norm = (t1[col] - g.transform("min")) / (g.transform("max") - g.transform("min"))
        comp = pd.DataFrame({"cve_mun": t1.cve_mun, "anio": t1.anio, "n": norm}).merge(
            b[["cve_mun", "anio", col]], on=["cve_mun", "anio"])
        difs.append((comp.n - comp[col]).abs().max())
    if max(difs) > 0.02:
        raise ValueError(f"la Tabla 1 no reproduce el Apendice B: diferencias maximas {difs}")
    return f"normalizacion del Apendice B reproducida, diferencia maxima {max(difs):.3f}"


def ejecutar(cur, cache) -> None:
    p, _ = verificar("A3", cache)
    r = PdfReader(p)
    cur.execute("SELECT nom_mun_norm, cve_mun FROM dim_municipio WHERE cve_ent = '09' AND NOT es_total_entidad")
    claves = dict(cur.fetchall())

    t1 = tabla_1([r.pages[6].extract_text(), r.pages[7].extract_text()], claves)
    b = apendice_b([r.pages[30].extract_text(), r.pages[31].extract_text()], claves)
    nota = validar(t1, b)
    t2 = tabla_2(r.pages[11].extract_text(), claves)
    e = apendice_e([r.pages[35].extract_text(), r.pages[36].extract_text()], claves)
    if len(t2) != 48 or len(e) != 48:
        raise ValueError(f"Tabla 2 con {len(t2)} filas y Apendice E con {len(e)}; se esperaban 48")

    f = t1.merge(t2, on=["cve_mun", "anio"], validate="1:1").merge(e, on=["cve_mun", "anio"], validate="1:1")
    for col in ("poblacion", "unidades_economicas", "reportes_fugas", "reportes_falta_agua", "reportes_mala_calidad"):
        f[col] = f[col].astype("Int64")
    n = copiar(cur, "fact_vulnerabilidad_alcaldia", list(f.columns), f)
    registrar(cur, "A3", "fact_vulnerabilidad_alcaldia", n, nota, cache)
