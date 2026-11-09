"""Territorio: dim_anio, dim_municipio, colonias CONAPO, enlace de dim_ubicacion y poblacion."""
from __future__ import annotations

import calendar
import re
import zipfile

import geopandas as gpd
import pandas as pd

from comun import abrir_csv_zip, copiar, normalizar, registrar, verificar
import geo
from enlace_conapo import elegir_por_puntos

ANIOS = range(1990, 2041)
RUIDO = re.compile(r"\b(U HAB|UNIDAD HABITACIONAL|FRACC|FRACCIONAMIENTO|PBLO|PUEBLO|BARR|BARRIO|BO|COL|COLONIA|"
                   r"AMPL|AMPLIACION|EJIDO|CONJ|CONJUNTO)\b")
ROMANO = re.compile(r"\b(I|II|III|IV|V|VI|VII|VIII|IX|X)$")


def nombre_base(t: str | None) -> str:
    """Quita el tipo de asentamiento y el romano final de la unidad territorial del IECM."""
    t = ROMANO.sub(" ", RUIDO.sub(" ", t or "").strip())
    return re.sub(r"\s+", " ", t).strip()


def clave5(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(5)


def leer_csv(p, **kw) -> pd.DataFrame:
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(p, dtype=str, encoding=enc, keep_default_na=False, **kw)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"codificacion desconocida: {p}")


def iter_municipal(cache) -> pd.DataFrame:
    """Totales municipales del ITER: LOC 0000 con municipio distinto de 000."""
    p, _ = verificar("B10", cache)
    with zipfile.ZipFile(p) as z:
        n = [x for x in z.namelist() if x.lower().endswith(".csv") and "conjunto_de_datos" in x]
        df = abrir_csv_zip(z, n[0][-40:] if len(n) == 1 else "conjunto_de_datos_iter_00cpv2020.csv")
    df.columns = [c.strip().strip('"').upper() for c in df.columns]
    m = df[(df.MUN != "000") & (df.LOC == "0000") & (df.ENTIDAD != "00")].copy()
    m["cve_mun"] = m.ENTIDAD + m.MUN
    return m


def nombres_extra(cache) -> pd.DataFrame:
    """Municipios creados despues del Censo 2020 que usan el SMN o CONAPO."""
    import openpyxl

    p, _ = verificar("D7", cache)
    wb = openpyxl.load_workbook(p, read_only=True)
    filas = []
    for i, r in enumerate(wb["MUNICIPIOS"].iter_rows(values_only=True)):
        if i and r[0]:
            filas.append((str(r[0]).zfill(5), str(r[3]).rstrip("*").strip(), r[4]))
    smn = pd.DataFrame(filas, columns=["cve_mun", "nom_mun", "nom_ent"])
    p, _ = verificar("D13", cache)
    pob = leer_csv(p, usecols=["CLAVE", "NOM_ENT", "NOM_MUN"]).drop_duplicates()
    pob = pd.DataFrame({"cve_mun": clave5(pob.CLAVE), "nom_mun": pob.NOM_MUN, "nom_ent": pob.NOM_ENT})
    return pd.concat([smn, pob], ignore_index=True).drop_duplicates("cve_mun")


def cargar_municipios(cur, cache) -> None:
    it = iter_municipal(cache)
    n_iter = len(it)
    base = pd.DataFrame({"cve_mun": it.cve_mun, "cve_ent": it.ENTIDAD, "nom_ent": it.NOM_ENT, "nom_mun": it.NOM_MUN})
    for col, orig in (("pob_total_2020", "POBTOT"), ("viv_part_hab_2020", "TVIVPARHAB"),
                      ("vph_agua_dentro_2020", "VPH_AGUADV"), ("vph_agua_fuera_2020", "VPH_AGUAFV"),
                      ("vph_agua_servpub_2020", "VPH_AEASP"), ("vph_tinaco_2020", "VPH_TINACO"),
                      ("vph_cisterna_2020", "VPH_CISTER"), ("vph_drenaje_2020", "VPH_DRENAJ")):
        base[col] = pd.to_numeric(it[orig], errors="coerce").astype("Int64")

    extra = nombres_extra(cache)
    extra = extra[~extra.cve_mun.isin(base.cve_mun)].copy()
    extra["cve_ent"] = extra.cve_mun.str[:2]
    tot = base.groupby("cve_ent", as_index=False).nom_ent.first()
    tot = pd.DataFrame({"cve_mun": tot.cve_ent + "000", "cve_ent": tot.cve_ent, "nom_ent": tot.nom_ent,
                        "nom_mun": "Total de " + tot.nom_ent, "es_total_entidad": True})
    dim = pd.concat([base, extra, tot], ignore_index=True)
    dim["es_total_entidad"] = dim["es_total_entidad"].eq(True)
    dim["nom_mun_norm"] = dim.nom_mun.map(normalizar)
    columnas = ["cve_mun", "cve_ent", "nom_ent", "nom_mun", "nom_mun_norm", "es_total_entidad",
                "pob_total_2020", "viv_part_hab_2020", "vph_agua_dentro_2020", "vph_agua_fuera_2020",
                "vph_agua_servpub_2020", "vph_tinaco_2020", "vph_cisterna_2020", "vph_drenaje_2020"]
    copiar(cur, "dim_municipio", columnas, dim)
    registrar(cur, "B10", "dim_municipio", n_iter, f"{len(extra)} municipios adicionales del SMN y CONAPO, "
              f"{len(tot)} filas de total por entidad", cache)

    # Metropolis 2020
    p, _ = verificar("D1a", cache)
    m = leer_csv(p)
    p, _ = verificar("D1b", cache)
    t = leer_csv(p)
    t["cve_mun"] = clave5(t.clave_compuesta_municipio)
    verdad = lambda c: t[c].str.lower().eq("true")  # noqa: E731
    centrales = [c for c in t.columns if c.startswith("centrales_")]
    t["central"] = pd.concat([verdad(c) for c in centrales], axis=1).any(axis=1)
    m["cve_mun"] = clave5(m.clave_compuesta_municipio)
    m = m.merge(t[["cve_mun", "central"]], on="cve_mun", how="left")
    m["superficie"] = pd.to_numeric(m.superficie_km2.str.replace(",", ""), errors="coerce")
    m["densidad"] = pd.to_numeric(m.densidad_media_urbana.str.replace(",", ""), errors="coerce")
    cur.execute("CREATE TEMP TABLE t_met (cve_mun CHAR(5), clave TEXT, nombre TEXT, tipo TEXT, central BOOLEAN,"
                " superficie NUMERIC, densidad NUMERIC) ON COMMIT DROP")
    fil = m.rename(columns={"clave_metropoli": "clave", "nombre": "nombre", "tipo": "tipo"})
    copiar(cur, "t_met", ["cve_mun", "clave", "nombre", "tipo", "central", "superficie", "densidad"], fil)
    cur.execute("""UPDATE dim_municipio d SET clave_metropoli = t.clave, nombre_metropoli = t.nombre,
                   tipo_metropoli = t.tipo, municipio_central = t.central, superficie_km2 = t.superficie,
                   densidad_urbana = t.densidad, en_zm_ciudad_mexico = (t.clave = '09.1.01')
                   FROM t_met t WHERE d.cve_mun = t.cve_mun""")
    registrar(cur, "D1a", "dim_municipio", cur.rowcount, "municipios metropolitanos", cache)
    registrar(cur, "D1b", "dim_municipio", len(t), "tipificacion central o exterior", cache)

    # Indice de marginacion municipal
    p, _ = verificar("D11", cache)
    imm = leer_csv(p)
    imm["cve_mun"] = clave5(imm.CVE_MUN)
    cur.execute("CREATE TEMP TABLE t_imm (cve_mun CHAR(5), im NUMERIC, gm TEXT, agua NUMERIC, dren NUMERIC) ON COMMIT DROP")
    fil = imm.rename(columns={"IM_2020": "im", "GM_2020": "gm", "OVSAE": "agua", "OVSDE": "dren"})
    copiar(cur, "t_imm", ["cve_mun", "im", "gm", "agua", "dren"], fil)
    cur.execute("""UPDATE dim_municipio d SET im_2020 = t.im, gm_2020 = t.gm, pct_ocup_sin_agua_2020 = t.agua,
                   pct_ocup_sin_drenaje_2020 = t.dren FROM t_imm t WHERE d.cve_mun = t.cve_mun""")
    registrar(cur, "D11", "dim_municipio", cur.rowcount, None, cache)

    # PRONACOSE
    for id_f, sufijo in (("D8a", "social"), ("D8b", "economica"), ("D8c", "ambiental")):
        p, _ = verificar(id_f, cache)
        v = leer_csv(p)
        v["cve_mun"] = clave5(v.cve_concatenada)
        cur.execute(f"CREATE TEMP TABLE t_v_{sufijo} (cve_mun CHAR(5), probabilidad NUMERIC, t_prob TEXT) ON COMMIT DROP")
        copiar(cur, f"t_v_{sufijo}", ["cve_mun", "probabilidad", "t_prob"], v)
        cur.execute(f"""UPDATE dim_municipio d SET prob_sequia_{sufijo} = t.probabilidad,
                        clase_sequia_{sufijo} = t.t_prob FROM t_v_{sufijo} t WHERE d.cve_mun = t.cve_mun""")
        registrar(cur, id_f, "dim_municipio", cur.rowcount, None, cache)


def cargar_tiempo_anio(cur) -> None:
    filas = [(a, 366 if calendar.isleap(a) else 365, calendar.isleap(a)) for a in ANIOS]
    cur.executemany("INSERT INTO dim_anio (anio, dias, bisiesto) VALUES (%s,%s,%s)", filas)


def enlazar_ubicacion(cur) -> None:
    """Cada alcaldia de SACMEX se enlaza a su clave INEGI por nombre, sin tablas escritas a mano."""
    cur.execute("SELECT cve_mun, nom_mun_norm FROM dim_municipio WHERE cve_ent = '09' AND NOT es_total_entidad")
    claves = dict((n, c) for c, n in cur.fetchall())
    cur.execute("SELECT DISTINCT alcaldia FROM dim_ubicacion")
    faltan = []
    for (alc,) in cur.fetchall():
        n = normalizar(alc)
        c = claves.get(n) or next((v for k, v in claves.items() if n in k or k in n), None)
        if c is None:
            faltan.append(alc)
            continue
        cur.execute("UPDATE dim_ubicacion SET cve_mun = %s WHERE alcaldia = %s", (c, alc))
    if faltan:
        raise ValueError(f"alcaldias sin clave INEGI: {faltan}")
    cur.execute("SELECT id_ubicacion, colonia FROM dim_ubicacion")
    filas = [(normalizar(c), i) for i, c in cur.fetchall()]
    cur.executemany("UPDATE dim_ubicacion SET colonia_norm = %s WHERE id_ubicacion = %s", filas)


def cargar_colonias(cur, cache) -> None:
    p, _ = verificar("D12", cache)
    c = leer_csv(p, usecols=["CVE_COL", "COLONIA", "CP", "CLASIF", "CVE_MUN", "POB_TOT", "OVSAE", "OVSDE",
                             "IM_2020", "GM_2020"])
    c["cve_mun"] = clave5(c.CVE_MUN)
    d = pd.DataFrame({"cve_col": c.CVE_COL, "cve_mun": c.cve_mun, "colonia": c.COLONIA,
                      "colonia_norm": c.COLONIA.map(normalizar), "cp": c.CP.str.zfill(5).str[:5],
                      "clasificacion": c.CLASIF, "pob_total": c.POB_TOT, "pct_ocup_sin_agua": c.OVSAE,
                      "pct_ocup_sin_drenaje": c.OVSDE, "im_2020": c.IM_2020, "gm_2020": c.GM_2020})
    d = d.replace({"NA": None, "": None})
    cur.execute("SELECT cve_mun FROM dim_municipio")
    validos = {r[0] for r in cur.fetchall()}
    sin_mun = ~d.cve_mun.isin(validos)
    n = copiar(cur, "dim_colonia_conapo", ["cve_col", "cve_mun", "colonia", "colonia_norm", "cp", "clasificacion",
                                           "pob_total", "pct_ocup_sin_agua", "pct_ocup_sin_drenaje", "im_2020",
                                           "gm_2020"], d[~sin_mun])
    registrar(cur, "D12", "dim_colonia_conapo", n, f"{int(sin_mun.sum())} filas sin municipio valido", cache)

    # Enlace por nombre dentro de la misma alcaldia, primero exacto y luego sin calificadores.
    # Solo cuenta si el nombre es unico en CONAPO; no hay coincidencia difusa. Varias colonias
    # de SACMEX pueden caer en una de CONAPO porque el IECM parte colonias: ROMA NORTE I, II y III.
    cdmx = d[d.cve_mun.str.startswith("09") & d.colonia_norm.notna()].copy()
    cdmx["base"] = cdmx.colonia_norm.map(nombre_base)
    unica = lambda col: cdmx.groupby(["cve_mun", col]).cve_col.agg(["first", "size"]).query("size == 1")["first"].to_dict()  # noqa: E731
    exacta, por_base = unica("colonia_norm"), unica("base")
    cur.execute("SELECT id_ubicacion, cve_mun, colonia_norm FROM dim_ubicacion")
    filas, n_exactas = [], 0
    for i, m, c in cur.fetchall():
        col = exacta.get((m, c))
        n_exactas += col is not None
        col = col or por_base.get((m, nombre_base(c)))
        if col is not None:
            filas.append((int(col), i))
    por_nombre = {i: c for c, i in filas}

    # El enlace principal elige el poligono con mas puntos, si alcanza al menos 50 %.
    # En un empate 50/50 gana la menor cve_col (regla reproducible, no mayoria geografica).
    # El nombre queda como respaldo si ningun poligono alcanza la mitad de los puntos.
    p, _ = verificar("D15", cache)
    g = gpd.read_file(f"zip://{p.as_posix()}!colonias_imc2020.shp", where="CVE_ENT = '09'", columns=["CVE_COL", "CVE_ENT"])
    if g.empty:
        raise ValueError("sin poligonos de colonias para la CDMX")
    g["cve_col"] = g.CVE_COL.str.replace("_", "").astype("int64")
    sac = geo.puntos_sacmex(cur)
    pts = gpd.GeoDataFrame(sac[["id_ubicacion"]], geometry=gpd.points_from_xy(sac.lon, sac.lat), crs=g.crs)
    j = gpd.sjoin(pts, g[["cve_col", "geometry"]], how="inner", predicate="intersects")
    c = j.groupby(["id_ubicacion", "cve_col"]).size().rename("n").reset_index()
    total = sac.groupby("id_ubicacion").size()
    top = elegir_por_puntos(c, total)
    por_poligono = dict(zip(top.id_ubicacion, top.cve_col))
    ambos = [i for i in por_nombre if i in por_poligono]
    iguales = sum(por_nombre[i] == por_poligono[i] for i in ambos)
    final = [(int(c), "poligono", int(i)) for i, c in por_poligono.items()]
    final += [(int(c), "nombre", int(i)) for i, c in por_nombre.items() if i not in por_poligono]
    cur.executemany("UPDATE dim_ubicacion SET cve_col_conapo = %s, enlace_conapo = %s WHERE id_ubicacion = %s", final)
    nota = (f"{len(por_poligono)} por poligono y {len(final) - len(por_poligono)} por nombre; el nombre coincide con el "
            f"poligono en {iguales} de {len(ambos)}")
    registrar(cur, "D12", "dim_ubicacion", len(final), f"{n_exactas} nombres exactos; {nota}", cache)
    registrar(cur, "D15", "dim_ubicacion", len(por_poligono), nota, cache)


def cargar_poblacion(cur, cache) -> None:
    p, _ = verificar("D13", cache)
    d = leer_csv(p, usecols=["CLAVE", "ANO", "POB_MIT_MUN"])
    f = pd.DataFrame({"cve_mun": clave5(d.CLAVE), "anio": d.ANO, "pob_mitad_anio": d.POB_MIT_MUN})
    n = copiar(cur, "fact_poblacion_municipio", ["cve_mun", "anio", "pob_mitad_anio"], f)
    registrar(cur, "D13", "fact_poblacion_municipio", n, None, cache)


def cargar_ageb(cur, cache) -> None:
    for id_f, ent in (("B1", "09"), ("B6", "15")):
        p, _ = verificar(id_f, cache)
        with zipfile.ZipFile(p) as z:
            df = abrir_csv_zip(z, f"conjunto_de_datos_ageb_urbana_{ent}_cpv2020.csv")
        df.columns = [c.strip().upper() for c in df.columns]
        a = df[(df.MZA == "000") & (df.AGEB != "0000") & (df.LOC != "0000")].copy()
        a = a[a.NOM_LOC.str.contains("Total AGEB", case=False)]
        f = pd.DataFrame({"cvegeo_ageb": a.ENTIDAD + a.MUN + a.LOC + a.AGEB, "cve_mun": a.ENTIDAD + a.MUN})
        for col, orig in (("pob_total", "POBTOT"), ("viv_part_hab", "TVIVPARHAB"), ("vph_agua_dentro", "VPH_AGUADV"),
                          ("vph_agua_fuera", "VPH_AGUAFV"), ("vph_agua_servpub", "VPH_AEASP"),
                          ("vph_tinaco", "VPH_TINACO"), ("vph_cisterna", "VPH_CISTER"), ("vph_drenaje", "VPH_DRENAJ")):
            f[col] = pd.to_numeric(a[orig], errors="coerce").astype("Int64")
        n = copiar(cur, "fact_vivienda_agua_ageb", list(f.columns), f)
        registrar(cur, id_f, "fact_vivienda_agua_ageb", n, "valores reservados con * quedan NULL", cache)


def ejecutar(cur, cache) -> None:
    cargar_tiempo_anio(cur)
    cargar_municipios(cur, cache)
    enlazar_ubicacion(cur)
    cargar_colonias(cur, cache)
    cargar_poblacion(cur, cache)
    cargar_ageb(cur, cache)
