"""Agua municipal: CNGMD 2019 y 2021 (referencia 2018 y 2020) y recaudacion de la SHCP.

La CDMX queda casi vacia en el CNGMD: las alcaldias no operan el agua y responden "no
disponible". Eso no se rellena; en la CDMX la granularidad la da SACMEX por colonia.
"""
from __future__ import annotations

import io
import zipfile

import pandas as pd

from comun import abrir_csv_zip, copiar, normalizar, num, registrar, verificar
from cargar_territorio import leer_csv

TIPOS_TOMA = {"d": "DOMESTICA", "i": "INDUSTRIAL", "c": "COMERCIAL", "p": "PUBLICA", "m": "MIXTA"}


def z(id_f, cache) -> zipfile.ZipFile:
    return zipfile.ZipFile(verificar(id_f, cache)[0])


def catalogo(zf: zipfile.ZipFile, sufijo: str) -> dict[str, str]:
    """{codigo: descripcion} del catalogo de INEGI, con sus dos columnas tal cual."""
    t = abrir_csv_zip(zf, sufijo)
    return dict(zip(t.iloc[:, 0].str.strip(), t.iloc[:, 1].str.strip()))


def si_no(s: pd.Series) -> pd.Series:
    """Codigo 1 Si, 2 No; el 0 es 'no aplica o sin respuesta'."""
    return s.map({"1": True, "2": False})


def folio(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.zfill(5)


def tipos(cur, cache) -> dict[str, int]:
    """dim_tipo_fuente_captacion con el catalogo 2021; el de 2018 se traduce por descripcion
    porque el codigo 8 cambio de significado: 'Otra' en 2018, 'Mina' en 2021."""
    c21 = catalogo(z("D3b", cache), "fuentcap_cngmd2021.csv")
    c18 = catalogo(z("D2b", cache), "ttc_tipo_fuente_captacion_2018.csv")
    cur.executemany("INSERT INTO dim_tipo_fuente_captacion VALUES (%s,%s)",
                    [(int(k), v) for k, v in c21.items() if k != "0"])
    por_desc = {normalizar(v): k for k, v in c21.items()}
    m18 = {k: por_desc[normalizar(v)] for k, v in c18.items() if k != "0"}
    toma = catalogo(z("D3d", cache), "tipotoma_cngmd2021.csv")
    cur.executemany("INSERT INTO dim_tipo_toma VALUES (%s,%s)", [(int(k), v) for k, v in toma.items() if k != "0"])
    registrar(cur, "D3b", "dim_tipo_fuente_captacion", len(c21) - 1, "catalogo fuentcap", cache)
    registrar(cur, "D3d", "dim_tipo_toma", len(toma) - 1, "catalogo tipotoma", cache)
    return {"fuente18": m18, "toma": {normalizar(v): int(k) for k, v in toma.items()}}


def validar_mun(df: pd.DataFrame, validos: set[str], etiqueta: str) -> pd.DataFrame:
    fuera = ~df.cve_mun.isin(validos)
    if fuera.any():
        raise ValueError(f"{etiqueta}: {int(fuera.sum())} claves fuera de dim_municipio: {df.cve_mun[fuera].unique()[:8]}")
    return df


def cargar_2018(cur, cache, cat, validos) -> None:
    sv = abrir_csv_zip(z("D2a", cache), "secc_i_tr_m5_2018.csv")
    ca = abrir_csv_zip(z("D2b", cache), "secc_ii_tr_m5_2018.csv")
    ad = abrir_csv_zip(z("D2d", cache), "secc_iv_tr_m5_2018.csv")
    t = sv.merge(ca, on="folio", validate="1:1").merge(ad, on="folio", validate="1:1")
    f = pd.DataFrame({"cve_mun": folio(t.folio), "anio": 2018})
    f["con_red_publica"] = si_no(t.ag_servi)
    f["pct_poblacion_servida"] = num(t.pobl_prc)
    f["prestadores"] = num(t.tot_pres).astype("Int64")
    f["km_red_conduccion"] = num(t.con_ex_p)
    f["km_red_distribucion"] = num(t.dis_ex_p)
    f["km_conduccion_rehabilitada"] = num(t.con_re_p)
    f["km_distribucion_rehabilitada"] = num(t.dis_re_p)
    for col, orig in (("tomas_dom_medidor_func", "t_cm_dom"), ("tomas_dom_medidor_sin_func", "t_cms_do"),
                      ("tomas_dom_sin_medidor", "t_sm_dom"), ("tomas_total_medidor_func", "t_cm_tot"),
                      ("tomas_total_medidor_sin_func", "t_cms_to"), ("tomas_total_sin_medidor", "t_sm_tot")):
        f[col] = num(t[orig]).astype("Int64")
    f["factura_servicio"] = si_no(t.factu_ag)
    for col, orig in (("gasto_total_pesos", "total"), ("ingreso_agua_pesos", "ing_agua"),
                      ("ingreso_total_pesos", "total_in"), ("subsidio_federal_pesos", "sub_fede"),
                      ("subsidio_estatal_pesos", "sub_esta"), ("subsidio_municipal_pesos", "sub_muni")):
        f[col] = num(t[orig])
    f["compra_agua_bloque"] = si_no(t.agu_bloq)
    f["vol_bloque_superficial_m3"] = num(t.vo_super)
    f["vol_bloque_subterraneo_m3"] = num(t.vo_subte)
    f["tanques"] = num(t.nu_tanqu).astype("Int64")
    f["capacidad_tanques_m3"] = num(t.cap_alma)
    validar_mun(f, validos, "CNGMD 2018")
    n = copiar(cur, "fact_agua_municipio", list(f.columns), f)
    for id_f in ("D2a", "D2b", "D2d"):
        registrar(cur, id_f, "fact_agua_municipio", n, "referencia 2018", cache)

    # Facturacion: columnas c_ (cuota fija) y e_ (servicio medido) por tipo de toma
    filas = []
    for pre, esquema in (("c", "cuota fija"), ("e", "servicio medido")):
        for suf, nombre in TIPOS_TOMA.items():
            d = pd.DataFrame({"cve_mun": folio(ad.folio), "anio": 2018, "id_tipo_toma": cat["toma"][nombre],
                              "esquema": esquema, "num_tomas": num(ad[f"{pre}_num_{suf}"]),
                              "recibos": num(ad[f"{pre}_reci_{suf}"]),
                              "monto_facturado_pesos": num(ad[f"{pre}_fact_{suf}"]),
                              "monto_recaudado_pesos": num(ad[f"{pre}_reca_{suf}"]),
                              "volumen_m3": num(ad[f"{pre}_v_m3_{suf}"])})
            filas.append(d)
    fa = pd.concat(filas, ignore_index=True)
    medidas = ["num_tomas", "recibos", "monto_facturado_pesos", "monto_recaudado_pesos", "volumen_m3"]
    fa = fa.dropna(subset=medidas, how="all")
    fa["num_tomas"] = fa.num_tomas.astype("Int64")
    fa["recibos"] = fa.recibos.astype("Int64")
    n = copiar(cur, "fact_facturacion_agua", list(fa.columns), fa)
    registrar(cur, "D2d", "fact_facturacion_agua", n, "referencia 2018", cache)

    ap = abrir_csv_zip(z("D2a", cache), "secc_i_td_m5_2018_admn_apsa.csv")
    reg = catalogo(z("D2a", cache), "ttc_tipo_regimen_juridico_2018.csv")
    amb = catalogo(z("D2a", cache), "ttc_tipo_ambito_trabajo_serv_2018.csv")
    p = pd.DataFrame({"anio": 2018, "id_prestador": ap.id_aps, "cve_mun": folio(ap.folio),
                      "regimen": ap.aps_regi.str.strip().map(reg), "ambito": ap.aps_ambi.str.strip().map(amb)})
    n = copiar(cur, "fact_prestador_agua", list(p.columns), validar_mun(p, validos, "prestadores 2018"))
    registrar(cur, "D2a", "fact_prestador_agua", n, "referencia 2018", cache)

    fu = abrir_csv_zip(z("D2b", cache), "secc_ii_td_m5_2018_funt_capt.csv")
    s = pd.DataFrame({"anio": 2018, "id_fuente": fu.id_fuente, "cve_mun": folio(fu.folio),
                      "id_tipo_fuente": fu.fnt_tcap.str.strip().map(cat["fuente18"]), "nombre": fu.fnt_nom,
                      "profundidad_m": num(fu.fnt_ppro), "macromedidor": num(fu.fnt_mcro).astype("Int64"),
                      "capacidad_ls": num(fu.capa_ext), "volumen_anual_m3": num(fu.fnt_m3),
                      "horas_dia": num(fu.hors_ope), "dias_anio": num(fu.dias_ope)})
    n = copiar(cur, "fact_fuente_captacion", list(s.columns), validar_mun(s, validos, "fuentes 2018"))
    registrar(cur, "D2b", "fact_fuente_captacion", n, "referencia 2018", cache)

    pl = abrir_csv_zip(z("D2c", cache), "secc_iii_td_m5_2018_plnt_pota.csv")
    a = pd.DataFrame({"anio": 2018, "tipo_planta": "potabilizadora", "id_planta": pl.id_pln, "cve_mun": folio(pl.folio),
                      "nombre": pl.pln_nom, "opera": si_no(pl.pln_cens), "capacidad_ls": num(pl.cap_inst),
                      "caudal_promedio_ls": num(pl.cau_prom)})
    n = copiar(cur, "fact_planta_agua", list(a.columns), validar_mun(a, validos, "potabilizadoras 2018"))
    registrar(cur, "D2c", "fact_planta_agua", n, "potabilizadoras, referencia 2018", cache)

    tr = abrir_csv_zip(z("D2e", cache), "secc_vi_td_m5_2018_plnt_trat.csv")
    b = pd.DataFrame({"anio": 2018, "tipo_planta": "tratamiento", "id_planta": tr.id_tra, "cve_mun": folio(tr.folio),
                      "nombre": tr.tra_nom, "opera": si_no(tr.tra_oper), "caudal_promedio_ls": num(tr.cau_trat)})
    n = copiar(cur, "fact_planta_agua", list(b.columns), validar_mun(b, validos, "tratamiento 2018"))
    registrar(cur, "D2e", "fact_planta_agua", n, "tratamiento, referencia 2018", cache)


def cargar_2020(cur, cache, cat, validos) -> None:
    fac = catalogo(z("D3d", cache), "factu_ag_cngmd2021.csv")
    if not (normalizar(fac["1"]).startswith("SI") and normalizar(fac["2"]).startswith("NO")):
        raise ValueError(f"catalogo factu_ag inesperado: {fac}")

    sv = abrir_csv_zip(z("D3a", cache), "servagua_cngmd2021.csv")
    ad = abrir_csv_zip(z("D3d", cache), "admncion_cngmd2021.csv")
    t = sv.merge(ad, on="folio", validate="1:1")
    f = pd.DataFrame({"cve_mun": folio(t.folio), "anio": 2020})
    f["con_red_publica"] = si_no(t.ag_servi)
    f["pct_poblacion_servida"] = num(t.pobl_prc)
    f["prestadores"] = num(t.tot_pres).astype("Int64")
    f["km_red_conduccion"] = num(t.con_ex_p)
    f["km_red_distribucion"] = num(t.dis_ex_p)
    f["km_conduccion_rehabilitada"] = num(t.con_re_p)
    f["km_distribucion_rehabilitada"] = num(t.dis_re_p)
    for col, orig in (("tomas_dom_medidor_func", "t_cm_dom"), ("tomas_dom_medidor_sin_func", "t_cms_do"),
                      ("tomas_dom_sin_medidor", "t_sm_dom"), ("tomas_total_medidor_func", "t_cm_tot"),
                      ("tomas_total_medidor_sin_func", "t_cms_to"), ("tomas_total_sin_medidor", "t_sm_tot")):
        f[col] = num(t[orig]).astype("Int64")
    f["factura_servicio"] = si_no(t.factu_ag)
    for col, orig in (("gasto_total_pesos", "total"), ("ingreso_agua_pesos", "ing_agua"),
                      ("ingreso_total_pesos", "total_in"), ("subsidio_federal_pesos", "sub_fede"),
                      ("subsidio_estatal_pesos", "sub_esta"), ("subsidio_municipal_pesos", "sub_muni")):
        f[col] = num(t[orig])
    validar_mun(f, validos, "CNGMD 2020")
    n = copiar(cur, "fact_agua_municipio", list(f.columns), f)
    for id_f in ("D3a", "D3d"):
        registrar(cur, id_f, "fact_agua_municipio", n, "referencia 2020", cache)

    filas = []
    me = abrir_csv_zip(z("D3d", cache), "servmedi_cngmd2021.csv")
    cu = abrir_csv_zip(z("D3d", cache), "cuotafij_cngmd2021.csv")
    filas.append(pd.DataFrame({"cve_mun": folio(me.folio), "anio": 2020, "id_tipo_toma": me.tipotom2,
                               "esquema": "servicio medido", "num_tomas": num(me.num_tom), "recibos": num(me.recib_ex),
                               "monto_facturado_pesos": num(me.mon_fact), "monto_recaudado_pesos": num(me.mon_reca),
                               "volumen_m3": num(me.v_sum_m3)}))
    filas.append(pd.DataFrame({"cve_mun": folio(cu.folio), "anio": 2020, "id_tipo_toma": cu.tipotoma,
                               "esquema": "cuota fija", "num_tomas": num(cu.num_toma), "recibos": num(cu.reci_exp),
                               "monto_facturado_pesos": num(cu.mont_fac), "monto_recaudado_pesos": num(cu.mont_rec),
                               "volumen_m3": num(cu.v_m3_sum)}))
    fa = pd.concat(filas, ignore_index=True)
    fa = fa[fa.id_tipo_toma.str.strip() != "0"]
    medidas = ["num_tomas", "recibos", "monto_facturado_pesos", "monto_recaudado_pesos", "volumen_m3"]
    fa = fa.dropna(subset=medidas, how="all")
    fa["num_tomas"] = fa.num_tomas.astype("Int64")
    fa["recibos"] = fa.recibos.astype("Int64")
    n = copiar(cur, "fact_facturacion_agua", list(fa.columns), fa)
    registrar(cur, "D3d", "fact_facturacion_agua", n, "referencia 2020", cache)

    ap = abrir_csv_zip(z("D3a", cache), "admnapsa_cngmd2021.csv")
    reg = catalogo(z("D3a", cache), "regjurid_cngmd2021.csv")
    amb = catalogo(z("D3a", cache), "ambito_cngmd2021.csv")
    p = pd.DataFrame({"anio": 2020, "id_prestador": ap.id_aps, "cve_mun": folio(ap.folio),
                      "regimen": ap.regjurid.str.strip().map(reg), "ambito": ap.ambito.str.strip().map(amb),
                      "dias_semana_suministro": num(ap.agua_dia), "horas_dia_suministro": num(ap.agua_hor),
                      "distribuye_pipas": si_no(ap.ag_pipas), "volumen_pipas_m3_mes": num(ap.v_m3_pip)})
    n = copiar(cur, "fact_prestador_agua", list(p.columns), validar_mun(p, validos, "prestadores 2020"))
    registrar(cur, "D3a", "fact_prestador_agua", n, "referencia 2020", cache)

    lo = abrir_csv_zip(z("D3a", cache), "admnlocs_cngmd2021.csv")
    m = lo.merge(ap[["id_aps", "folio"]], on="id_aps", how="left", validate="m:1")
    huerfanas = int(m.folio.isna().sum())     # Sin prestador en admnapsa no hay municipio que asignarles
    m = m[m.folio.notna()]
    q = pd.DataFrame({"id_abasto": m.id_local, "anio": 2020, "id_prestador": m.id_aps, "cve_mun": folio(m.folio),
                      "cve_loc": m.localid.str.strip(), "dias_semana_suministro": num(m.ag_dias),
                      "horas_dia_suministro": num(m.ag_horas)})
    n = copiar(cur, "fact_abasto_localidad", list(q.columns), validar_mun(q, validos, "localidades 2020"))
    registrar(cur, "D3a", "fact_abasto_localidad", n, f"referencia 2020, {huerfanas} localidades sin prestador excluidas", cache)

    fu = abrir_csv_zip(z("D3b", cache), "fntcapta_cngmd2021.csv")
    s = pd.DataFrame({"anio": 2020, "id_fuente": fu.id_fuente, "cve_mun": folio(fu.folio),
                      "id_tipo_fuente": fu.fuentcap.str.strip().replace("0", None), "nombre": fu.fnt_nom,
                      "profundidad_m": num(fu.fnt_ppro), "macromedidor": num(fu.fntmacro).astype("Int64"),
                      "capacidad_ls": num(fu.capa_ins), "gasto_promedio_ls": num(fu.gast_pro)})
    n = copiar(cur, "fact_fuente_captacion", list(s.columns), validar_mun(s, validos, "fuentes 2020"))
    registrar(cur, "D3b", "fact_fuente_captacion", n, "referencia 2020", cache)

    pl = abrir_csv_zip(z("D3c", cache), "plntpota_cngmd2021.csv")
    a = pd.DataFrame({"anio": 2020, "tipo_planta": "potabilizadora", "id_planta": pl.id_pln, "cve_mun": folio(pl.folio),
                      "nombre": pl.pln_nom, "opera": si_no(pl.plpotope), "capacidad_ls": num(pl.cap_inst),
                      "caudal_promedio_ls": num(pl.gasto_pr)})
    n = copiar(cur, "fact_planta_agua", list(a.columns), validar_mun(a, validos, "potabilizadoras 2020"))
    registrar(cur, "D3c", "fact_planta_agua", n, "potabilizadoras, referencia 2020", cache)

    tr = abrir_csv_zip(z("D3e", cache), "plnttrat_cngmd2021.csv")
    b = pd.DataFrame({"anio": 2020, "tipo_planta": "tratamiento", "id_planta": tr.id_tra, "cve_mun": folio(tr.folio),
                      "nombre": tr.tra_nom, "opera": si_no(tr.pltraope), "capacidad_ls": num(tr.capac_in),
                      "caudal_promedio_ls": num(tr.cau_trat)})
    n = copiar(cur, "fact_planta_agua", list(b.columns), validar_mun(b, validos, "tratamiento 2020"))
    registrar(cur, "D3e", "fact_planta_agua", n, "tratamiento, referencia 2020", cache)


def cargar_shcp(cur, cache, validos) -> None:
    p, _ = verificar("D4", cache)
    d = leer_csv(p)
    # Belisario Dominguez (Chiapas) viene con id_municipio 0: no tiene clave INEGI ni montos
    sin_clave = d.id_municipio.str.strip() == "0"
    excluidas = int(sin_clave.sum())
    if pd.to_numeric(d.monto_agua[sin_clave], errors="coerce").fillna(0).sum() != 0:
        raise ValueError("hay montos en filas sin clave de municipio")
    d = d[~sin_clave].copy()
    ent = d.id_entidad_federativa.str.strip().str.zfill(2)
    suma = d.municipio.str.startswith("Suma ")
    d["cve_mun"] = ent + d.id_municipio.str.strip().str.zfill(3)
    d.loc[suma, "cve_mun"] = ent[suma] + "000"     # Total de la entidad, no el municipio 001
    valor = lambda c: pd.to_numeric(d[c].replace("No disponible", None), errors="coerce")  # noqa: E731
    f = pd.DataFrame({"cve_mun": d.cve_mun, "anio": d.ciclo, "tomas_pagadas": valor("tomas_pagadas").astype("Int64"),
                      "monto_agua_pesos": valor("monto_agua"), "monto_percapita_pesos": valor("monto_recaudado_percapita"),
                      "poblacion": valor("poblacion").astype("Int64")})
    validar_mun(f, validos, "SHCP")
    n = copiar(cur, "fact_recaudacion_agua", list(f.columns), f)
    registrar(cur, "D4", "fact_recaudacion_agua", n, f"{int(suma.sum())} filas son el total de la CDMX; "
              f"{excluidas} sin clave de municipio y sin montos excluidas", cache)


def ejecutar(cur, cache) -> None:
    cat = tipos(cur, cache)
    cur.execute("SELECT cve_mun FROM dim_municipio")
    validos = {r[0] for r in cur.fetchall()}
    cargar_2018(cur, cache, cat, validos)
    cargar_2020(cur, cache, cat, validos)
    cargar_shcp(cur, cache, validos)
