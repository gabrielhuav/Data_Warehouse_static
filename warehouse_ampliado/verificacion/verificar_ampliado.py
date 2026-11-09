#!/usr/bin/env python3
"""Comprueba el almacen ampliado y escribe evidencia_ampliado.txt.

Cada verificacion recalcula su cifra desde PostgreSQL o desde el archivo fuente verificado.
Sale con codigo 1 si alguna falla, para que no se reporten cifras que no se sostienen.

    python -I verificacion/verificar_ampliado.py
"""
from __future__ import annotations

import csv
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "etl"))
from comun import RAIZ, conectar, fuentes, huellas, normalizar, ruta  # noqa: E402

SALIDA = RAIZ / "verificacion" / "evidencia_ampliado.txt"
CSV_CONSUMO = RAIZ.parent / "warehouse" / "data" / "consumo_agua_historico_2019.csv"
lineas: list[str] = []
fallos = 0


def decir(t: str = "") -> None:
    print(t)
    lineas.append(t)


def ok(nombre: str, cond: bool, detalle: str = "") -> None:
    global fallos
    fallos += 0 if cond else 1
    decir(f"[{'OK ' if cond else 'FALLA'}] {nombre}{': ' + detalle if detalle else ''}")


def uno(cur, q: str):
    cur.execute(q)
    return cur.fetchone()[0]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    decir(f"Evidencia del almacen ampliado, generada {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC")
    conn = conectar()
    cur = conn.cursor()

    decir("\n## 1. El almacen original sigue intacto")
    ok("fact_consumo_agua", uno(cur, "SELECT count(*) FROM fact_consumo_agua") == 70886, "70,886 filas")
    ok("fact_clima", uno(cur, "SELECT count(*) FROM fact_clima") == 181, "181 filas")
    ok("dim_ubicacion", uno(cur, "SELECT count(*) FROM dim_ubicacion") == 1553, "1,553 colonias")
    ok("dim_indice_des", uno(cur, "SELECT count(*) FROM dim_indice_des") == 4, "4 niveles")
    with open(CSV_CONSUMO, encoding="utf-8", errors="replace", newline="") as fh:
        filas = [r for r in csv.DictReader(fh)
                 if r["colonia"] not in ("", "NA") and r["alcaldia"] not in ("", "NA") and r["indice_des"] not in ("", "NA")]
    suma = sum(float(r["consumo_total"] or 0) for r in filas if r["consumo_total"] not in ("", "NA"))
    bd = float(uno(cur, "SELECT sum(consumo_total) FROM fact_consumo_agua"))
    ok("consumo total igual al CSV", abs(suma - bd) < 1, f"{bd:,.2f} m3")
    cur.execute("SELECT min(fecha), max(fecha), count(*) FROM dim_tiempo WHERE id_tiempo IN (SELECT id_tiempo FROM fact_clima)")
    decir(f"     dim_tiempo original: {cur.fetchone()}")

    decir("\n## 2. Procedencia: cada archivo coincide con el manifiesto")
    malos = 0
    for f in fuentes().values():
        p = ruta(f)
        n, md5, sha = huellas(p)
        bien = n == f.get("bytes") and sha == f.get("sha256") and md5 == f.get("md5")
        if f.get("md5_oficial"):
            bien = bien and md5 == f["md5_oficial"]
        malos += 0 if bien else 1
        if not bien:
            decir(f"     no coincide {f['id']}")
    ok("archivos verificados", malos == 0, f"{len(fuentes())} fuentes, {malos} con diferencias")
    cur.execute("SELECT count(DISTINCT id_fuente) FROM control_ingesta_fuentes")
    ok("toda fuente del manifiesto alimenta una tabla", cur.fetchone()[0] == len(fuentes()))
    cur.execute("""SELECT count(*) FROM control_ingesta_fuentes WHERE md5_oficial_coincide IS FALSE""")
    ok("ningun MD5 oficial en desacuerdo", cur.fetchone()[0] == 0)

    decir("\n## 3. Integridad de las llaves nuevas")
    ok("las 1,553 colonias tienen clave INEGI", uno(cur, "SELECT count(*) FROM dim_ubicacion WHERE cve_mun IS NULL") == 0)
    ok("16 alcaldias enlazadas", uno(cur, "SELECT count(DISTINCT cve_mun) FROM dim_ubicacion") == 16)
    bad = uno(cur, """SELECT count(*) FROM v_colonia_conapo_contexto
                      WHERE (colonias_con_pob < colonias_sacmex AND
                             (litros_hab_dia_dom IS NOT NULL OR falta_por_mil_hab IS NOT NULL OR fugas_por_mil_hab IS NOT NULL))
                         OR (colonias_con_dom < colonias_sacmex AND litros_hab_dia_dom IS NOT NULL)
                         OR (litros_hab_dia_dom IS NOT NULL AND
                             litros_hab_dia_dom IS DISTINCT FROM round(consumo_dom_m3 * 1000.0 / NULLIF(pob_sacmex * 181,0),1))
                         OR (falta_por_mil_hab IS NOT NULL AND
                             falta_por_mil_hab IS DISTINCT FROM round(falta_agua_2019_s1 * 1000.0 / NULLIF(pob_sacmex,0),2))
                         OR (fugas_por_mil_hab IS NOT NULL AND
                             fugas_por_mil_hab IS DISTINCT FROM round(fugas_2021_2024 * 1000.0 / NULLIF(pob_sacmex,0),2))""")
    ok("tasas proxy CONAPO explicitas y sin denominadores parciales", bad == 0, f"{bad} excepciones")
    cur.execute("""SELECT count(*) FROM (
                     SELECT t.id_tiempo FROM dim_tiempo t GROUP BY t.id_tiempo HAVING count(*) > 1) x""")
    ok("dim_tiempo sin duplicados", cur.fetchone()[0] == 0)
    bad = uno(cur, """SELECT count(*) FROM dim_tiempo WHERE fecha <> make_date(anio, mes, dia)
                      OR bimestre <> (mes + 1) / 2""")
    ok("dim_tiempo consistente", bad == 0)

    decir("\n## 4. Identidades de cada fuente")
    bad = uno(cur, """SELECT count(*) FROM fact_disponibilidad_acuifero WHERE
                      abs(vol_concesionado + vol_libre_alumbramiento + vol_pendiente_titulacion + vol_reservas
                          - vol_extraccion) > 0.01""")
    ok("VCAS + VEALA + VAPTYR + VAPRH = VEAS en los 653 acuiferos", bad == 0, f"{bad} excepciones")
    bad = uno(cur, """SELECT count(*) FROM fact_disponibilidad_acuifero WHERE
                      abs(recarga_total - descarga_natural - vol_extraccion - (dma_positiva + dma_negativa)) > 0.01""")
    ok("R - DNC - VEAS = DMA en los 653 acuiferos", bad == 0, f"{bad} excepciones")
    cur.execute("SELECT count(*), sum(pob_total_2020) FROM dim_municipio WHERE cve_ent = '09' AND NOT es_total_entidad")
    n, pob = cur.fetchone()
    ok("poblacion de la CDMX en el ITER", n == 16 and pob == 9209944, f"{n} alcaldias, {pob:,} habitantes")
    cur.execute("""SELECT count(*), sum(CASE WHEN cve_ent='09' THEN 1 ELSE 0 END), sum(CASE WHEN cve_ent='15' THEN 1 ELSE 0 END),
                          sum(CASE WHEN cve_ent='13' THEN 1 ELSE 0 END)
                   FROM dim_municipio WHERE en_zm_ciudad_mexico""")
    n, a, b, c = cur.fetchone()
    ok("ZM de Ciudad de Mexico segun CONAPO 2020", n == 63, f"{n} municipios: {a} CDMX, {b} Edomex, {c} Hidalgo")
    cur.execute("SELECT count(*) FROM fact_vulnerabilidad_alcaldia")
    ok("Huerta-Vergara: 16 alcaldias por 3 anios", cur.fetchone()[0] == 48)
    cur.execute("""SELECT indice_z, percentil_beta, grado_vulnerabilidad, dotacion_lpcd FROM fact_vulnerabilidad_alcaldia
                   WHERE cve_mun = '09007' AND anio = 2015""")
    fila = cur.fetchone()
    ok("Iztapalapa 2015 igual al Apendice E y la Tabla 2",
       (float(fila[0]), float(fila[1]), fila[2], float(fila[3])) == (0.920, 0.995, "Very High", 215.05),
       f"Z {fila[0]}, beta {fila[1]}, {fila[2]}, {fila[3]} LPCD")
    cur.execute("""SELECT max(s) FROM (SELECT count(*) s FROM fact_reporte_agua GROUP BY recurso, folio) x""")
    ok("folios unicos en reportes", cur.fetchone()[0] == 1)
    cur.execute("""SELECT min(tavg_c), max(tavg_c), min(precip_mm), max(precip_mm) FROM fact_clima_colonia""")
    a, b, c, d = cur.fetchone()
    ok("clima en rango fisico", -5 < a < b < 35 and c >= 0, f"tavg {a} a {b} C, precipitacion {c} a {d} mm")
    bad = uno(cur, "SELECT count(*) FROM fact_clima_colonia WHERE tmin_c > tmax_c OR tavg_c NOT BETWEEN tmin_c AND tmax_c")
    ok("tmin <= tavg <= tmax", bad == 0, f"{bad} excepciones")

    decir("\n## 5. Cruces entre fuentes independientes")
    fs = fuentes()
    with open(ruta(fs["D4"]), encoding="utf-8-sig", newline="") as fh:
        shcp = {}
        for r in csv.DictReader(fh):
            if not r["municipio"].startswith("Suma ") and r["id_municipio"] != "0":
                shcp[r["id_entidad_federativa"].zfill(2) + r["id_municipio"].zfill(3)] = r["municipio"]
    cur.execute("SELECT cve_mun, nom_mun_norm FROM dim_municipio")
    nombres = dict(cur.fetchall())
    distintos = [(k, v, nombres.get(k)) for k, v in shcp.items() if normalizar(v) != nombres.get(k)]
    ok("las claves de la SHCP son las de INEGI", len(distintos) < 0.02 * len(shcp),
       f"{len(shcp) - len(distintos):,} de {len(shcp):,} nombres identicos; ejemplos distintos {distintos[:3]}")

    # Pearson se desploma por dos errores de captura del CNGMD; por eso se exige la correlacion
    # de rangos y se imprimen los dos valores y los atipicos con su nombre, sin ocultarlos.
    cur.execute("""WITH x AS (
                     SELECT m.nom_mun, a.ingreso_agua_pesos i, r.monto_agua_pesos s
                     FROM fact_agua_municipio a JOIN fact_recaudacion_agua r ON r.cve_mun = a.cve_mun AND r.anio = a.anio
                     JOIN dim_municipio m ON m.cve_mun = a.cve_mun
                     WHERE a.anio = 2018 AND m.cve_ent = '15' AND a.ingreso_agua_pesos > 0 AND r.monto_agua_pesos > 0),
                   y AS (SELECT *, rank() OVER (ORDER BY i) ri, rank() OVER (ORDER BY s) rs FROM x)
                   SELECT count(*), corr(i, s), corr(ri, rs),
                          percentile_cont(0.5) WITHIN GROUP (ORDER BY i / s),
                          string_agg(nom_mun || ' x' || round(i / s, 2), ', ') FILTER (WHERE i / s > 10 OR i / s < 0.1)
                   FROM y""")
    n, pearson, spearman, mediana, atipicos = cur.fetchone()
    ok("ingresos del CNGMD y recaudacion de la SHCP coinciden en orden, Edomex 2018", spearman > 0.8,
       f"{n} municipios, Spearman {spearman:.3f}, Pearson {pearson:.3f}, razon mediana {mediana:.2f}")
    decir(f"     atipicos fuera de 0.1 a 10 veces: {atipicos}")

    cur.execute("""WITH nuevo AS (SELECT t.mes, c.tavg_c FROM fact_clima_municipio c JOIN dim_tiempo t USING (id_tiempo)
                                  WHERE c.cve_mun = '09017' AND t.mes <= 6),
                        original AS (SELECT t.mes, avg(f.temp_promedio) AS tavg FROM fact_clima f JOIN dim_tiempo t USING (id_tiempo) GROUP BY t.mes)
                   SELECT corr(n.tavg_c, o.tavg), avg(n.tavg_c - o.tavg) FROM nuevo n JOIN original o USING (mes)""")
    rho, sesgo = cur.fetchone()
    ok("MexHiResClimDB sigue a Open-Meteo en Venustiano Carranza, ene-jun 2019", rho > 0.9, f"r = {rho:.3f}, diferencia media {sesgo:+.2f} C")

    cur.execute("""SELECT corr(v.area_urbana_km2, s.a), corr(v.poblacion, s.p) FROM fact_vulnerabilidad_alcaldia v
                   JOIN (SELECT cve_mun, count(*) a, sum(pob_censo_2020) p FROM dim_ubicacion GROUP BY 1) s USING (cve_mun)
                   WHERE v.anio = 2015""")
    a, b = cur.fetchone()
    ok("poblacion 2015 del articulo y poblacion censal por colonia, por alcaldia", b > 0.95, f"r = {b:.3f}")
    cur.execute("""SELECT sum(p.pob_mitad_anio), sum(m.pob_total_2020) FROM dim_municipio m
                   JOIN fact_poblacion_municipio p ON p.cve_mun = m.cve_mun AND p.anio = 2019 WHERE m.en_zm_ciudad_mexico""")
    a, b = cur.fetchone()
    ok("poblacion de la ZM: CONAPO 2019 y Censo 2020 difieren poco", abs(float(a) / float(b) - 1) < 0.03, f"CONAPO {a:,}, Censo {b:,}")
    cur.execute("""SELECT count(*), min(profundidad_nivel_m), percentile_cont(0.5) WITHIN GROUP (ORDER BY profundidad_nivel_m),
                          max(profundidad_nivel_m), count(*) FILTER (WHERE profundidad_nivel_m <= 0)
                   FROM fact_nivel_piezometrico""")
    a, b, c, d, e = cur.fetchone()
    decir(f"     piezometria nacional: {a:,} lecturas; min {b} m, mediana {c:.1f} m, max {d} m; {e:,} en cero o negativas (se conservan)")
    cur.execute("""WITH p AS (SELECT n.id_pozo, d.clv_acui,
                                     max(n.profundidad_nivel_m) FILTER (WHERE n.anio = 2010) a,
                                     max(n.profundidad_nivel_m) FILTER (WHERE n.anio = 2019) b
                              FROM fact_nivel_piezometrico n JOIN dim_pozo d USING (id_pozo)
                              WHERE d.clv_acui IN ('0901', '1506', '1507', '1508') GROUP BY 1, 2)
                   SELECT clv_acui, count(*), round(avg(a), 1), round(avg(b), 1), round(avg(b - a), 1) FROM p
                   WHERE a IS NOT NULL AND b IS NOT NULL GROUP BY 1 ORDER BY 1""")
    decir("     nivel estatico en los mismos pozos, 2010 y 2019:")
    for r in cur.fetchall():
        decir(f"       acuifero {r[0]}: {r[1]:>3} pozos; profundidad media {r[2]} m en 2010, {r[3]} m en 2019; cambio {r[4]:+} m")
    cur.execute("""SELECT 100.0 * sum(u.pob_censo_2020) / (SELECT sum(pob_total_2020) FROM dim_municipio WHERE cve_ent = '09' AND NOT es_total_entidad)
                   FROM dim_ubicacion u""")
    decir(f"     poblacion asignada a colonias: {cur.fetchone()[0]:.1f} % del total del ITER en la CDMX")
    cur.execute("""SELECT count(*), count(cve_col_conapo), count(*) FILTER (WHERE enlace_conapo = 'poligono'),
                          count(*) FILTER (WHERE enlace_conapo = 'nombre'), count(pob_censo_2020), count(ue_denue_2026) FROM dim_ubicacion""")
    a, b, c, d, e, f = cur.fetchone()
    decir(f"     colonias: {a:,}; con colonia CONAPO {b:,} ({c:,} por poligono, {d:,} por nombre); con poblacion {e:,}; con DENUE {f:,}")
    ok("casi todas las colonias se enlazan por poligono", c > 1500)

    cur.execute("""SELECT count(*), min(s), max(s) FROM (SELECT cve_mun, sum(pct_municipio) s FROM puente_municipio_acuifero GROUP BY 1) x""")
    n, a, b = cur.fetchone()
    ok("los acuiferos cubren cada municipio", n == 225 and float(a) > 95 and float(b) < 101, f"{n} municipios, suma de porcentajes de {a} a {b}")
    cur.execute("""SELECT count(*), count(*) FILTER (WHERE n_pozos > 0), sum(n_pozos) FROM puente_municipio_acuifero""")
    a, b, c = cur.fetchone()
    decir(f"     puente municipio-acuifero: {a} relaciones, {b} con pozos, {c} pozos")
    cur.execute("""SELECT count(*), count(*) FILTER (WHERE p.clv_acui = u.clv_acui) FROM dim_pozo p
                   JOIN LATERAL (SELECT x.clv_acui FROM puente_municipio_acuifero x WHERE x.cve_mun = p.cve_mun AND x.clv_acui = p.clv_acui) u ON TRUE
                   WHERE p.cve_mun IS NOT NULL""")
    a, _ = cur.fetchone()
    n = uno(cur, "SELECT count(*) FROM dim_pozo WHERE cve_mun IS NOT NULL")
    ok("los pozos caen en un acuifero que toca su municipio", a / n > 0.97, f"{a} de {n}")

    cur.execute("""SELECT p.volumen_hm3, p.nivel_m, p.evaporacion_mm FROM fact_presa_diaria p JOIN dim_tiempo t USING (id_tiempo)
                   WHERE p.clave = 'VBRMX' AND t.fecha = DATE '2026-10-30'""")
    a, b, c = cur.fetchone()
    ok("ultima fila de Valle de Bravo igual al CSV", (float(a), float(b), float(c)) == (384.938, 1829.55, 3.57), f"{a} hm3, {b} m")
    # Nivel y volumen estan ligados fisicamente. Se exige en Cutzamala; las demas se reportan por nombre.
    cur.execute("""SELECT p.clave, e.nombre, e.cuenca_disponibilidad = 'Río Cutzamala', round(corr(p.nivel_m, p.volumen_hm3)::numeric, 3)
                   FROM fact_presa_diaria p JOIN dim_estacion_hidrometrica e USING (clave) GROUP BY 1, 2, 3 ORDER BY 4""")
    presas = cur.fetchall()
    cutz = [r for r in presas if r[2]]
    ok("en las presas de Cutzamala el nivel y el volumen van juntos", len(cutz) == 3 and all(r[3] >= 0.99 for r in cutz),
       ", ".join(f"{r[0]} r = {r[3]}" for r in cutz))
    decir(f"     presas con r < 0.8: {[(r[0], float(r[3])) for r in presas if r[3] < 0.8]}")
    cur.execute("""SELECT p.clave, t.fecha, p.nivel_m, p.volumen_hm3 FROM fact_presa_diaria p JOIN dim_tiempo t USING (id_tiempo)
                   WHERE (p.clave = 'GDLMX' AND p.nivel_m < 2000) OR (p.clave = 'PNDMX' AND p.nivel_m < 2000) ORDER BY 1""")
    for r in cur.fetchall():
        decir(f"       error de captura de un dia en la fuente: {r[0]} {r[1]}, nivel {r[2]}, volumen {r[3]}")
    cur.execute("""SELECT p.clave, t.anio, percentile_cont(0.5) WITHIN GROUP (ORDER BY p.nivel_m), percentile_cont(0.5) WITHIN GROUP (ORDER BY p.volumen_hm3)
                   FROM fact_presa_diaria p JOIN dim_tiempo t USING (id_tiempo)
                   WHERE p.clave IN ('PMDMX', 'TXMHD') AND t.anio IN (2014, 2019) GROUP BY 1, 2 ORDER BY 1, 2""")
    for r in cur.fetchall():
        decir(f"       posible cambio de curva nivel-volumen: {r[0]} en {r[1]}: nivel mediano {r[2]:.2f} m, volumen mediano {r[3]:.1f} hm3")
    cur.execute("""SELECT count(*), count(*) FILTER (WHERE limite IS NOT NULL), count(valor), count(calidad) FROM fact_calidad_agua""")
    a, b, c, d = cur.fetchone()
    decir(f"     calidad del agua: {a:,} valores; {b:,} fuera del limite de deteccion; {c:,} con numero; {d:,} con clasificacion")

    decir("\n## 6. Cifras del informe, recalculadas")
    cur.execute("""SELECT relname, n_live_tup FROM pg_stat_user_tables WHERE relname LIKE 'fact\\_%' OR relname LIKE 'dim\\_%'
                   OR relname LIKE 'puente\\_%' ORDER BY relname""")
    tablas = cur.fetchall()
    total = 0
    for t, _ in tablas:
        n = uno(cur, f"SELECT count(*) FROM {t}")
        total += n
        decir(f"     {t:<36}{n:>12,}")
    decir(f"     {'total de filas':<36}{total:>12,}")

    decir("\n     Reportes por anio; falta, fuga y calidad son de agua potable (la fuente no registra fugas antes de 2021):")
    potable = "tr.clasificacion = 'Agua Potable' AND tr.reporte ="
    cur.execute(f"""SELECT t.anio, count(*), count(*) FILTER (WHERE {potable} 'Falta de agua'),
                           count(*) FILTER (WHERE {potable} 'Fuga'), count(*) FILTER (WHERE {potable} 'Mala calidad'),
                           count(*) FILTER (WHERE tr.clasificacion = 'Drenaje')
                    FROM fact_reporte_agua r JOIN dim_tiempo t USING (id_tiempo) JOIN dim_tipo_reporte tr USING (id_tipo_reporte)
                    GROUP BY 1 ORDER BY 1""")
    for r in cur.fetchall():
        decir(f"       {r[0]}: total {r[1]:>8,}  falta de agua {r[2]:>8,}  fuga {r[3]:>7,}  mala calidad {r[4]:>6,}  drenaje {r[5]:>6,}")
    cur.execute("""SELECT min(t.fecha), max(t.fecha) FROM fact_reporte_agua r JOIN dim_tiempo t USING (id_tiempo)""")
    decir(f"     periodo de los reportes: {cur.fetchone()}")
    cur.execute(f"""SELECT count(*), count(*) FILTER (WHERE {potable} 'Falta de agua'), count(*) FILTER (WHERE {potable} 'Fuga')
                    FROM fact_reporte_agua r JOIN dim_tiempo t USING (id_tiempo) JOIN dim_tipo_reporte tr USING (id_tipo_reporte)
                    WHERE t.fecha BETWEEN DATE '2019-01-01' AND DATE '2019-06-30'""")
    a, b, c = cur.fetchone()
    decir(f"     reportes ene-jun 2019: {a:,}; falta de agua {b:,}; fugas {c:,}")
    ok("ene-jun 2019 son 39,685 reportes de falta de agua y ninguna fuga", (a, b, c) == (39685, 39685, 0))
    cur.execute("SELECT count(*), count(id_ubicacion), count(DISTINCT id_ubicacion) FROM fact_reporte_agua")
    a, b, c = cur.fetchone()
    decir(f"     reportes: {a:,}; ubicados en colonia {b:,} ({100 * b / a:.1f} %); colonias con reportes {c:,}")

    decir("\n     ZM de Ciudad de Mexico, referencia 2018 (CNGMD), por entidad:")
    cur.execute("""SELECT m.nom_ent, count(DISTINCT m.cve_mun),
                          count(DISTINCT a.cve_mun) FILTER (WHERE a.tomas_total_medidor_func IS NOT NULL),
                          sum(a.tomas_total_medidor_func), sum(a.tomas_total_sin_medidor)
                   FROM dim_municipio m JOIN fact_agua_municipio a USING (cve_mun)
                   WHERE m.en_zm_ciudad_mexico AND a.anio = 2018 GROUP BY 1 ORDER BY 1""")
    for r in cur.fetchall():
        decir(f"       {r[0]:<20} municipios {r[1]:>3}; con dato {r[2]:>3}; medidor funcionando {r[3] or 0:>10,}; sin medidor {r[4] or 0:>10,}")
    decir("\n     Acuiferos de la ZMVM:")
    cur.execute("SELECT clv_acui, nom_acui, recarga_total, vol_extraccion, dma_negativa, extraccion_entre_recarga, pozos, lecturas_2019 FROM v_acuiferos_zmvm ORDER BY 1")
    for r in cur.fetchall():
        decir(f"       {r[0]} {r[1]:<42} R {r[2]:>8} VEAS {float(r[3]):>9.2f} DMA {float(r[4]):>9.2f} VEAS/R {r[5]} pozos {r[6]:>3} lecturas 2019 {r[7]:>3}")

    decir("\n     Volumen domestico por municipio de la ZM, por calidad (v_zm_indicadores_agua):")
    cur.execute("""SELECT fuente_volumen, calidad_volumen, count(*), sum(pob_2019),
                          round(sum(vol_dom_m3_anio) * 1000 / NULLIF(sum(pob_2019) FILTER (WHERE vol_dom_m3_anio IS NOT NULL), 0) / 365, 1),
                          min(litros_hab_dia_dom), max(litros_hab_dia_dom)
                   FROM v_zm_indicadores_agua GROUP BY 1, 2 ORDER BY 1, 2""")
    for r in cur.fetchall():
        decir(f"       {r[0]:<20} {r[1]:<10} municipios {r[2]:>3}; poblacion 2019 {r[3]:>11,}; conjunto {r[4]} l/hab/dia; min {r[5]}; max {r[6]}")

    decir("\n     Hundimiento medio por municipio, los cinco mayores de la ZM:")
    cur.execute("""SELECT m.nom_ent, m.nom_mun, s.n_pixeles, s.vlm_media_cm_anio, s.vlm_min_cm_anio FROM fact_subsidencia_municipio s
                   JOIN dim_municipio m USING (cve_mun) WHERE m.en_zm_ciudad_mexico AND s.n_pixeles >= 30
                   ORDER BY s.vlm_media_cm_anio LIMIT 5""")
    for r in cur.fetchall():
        decir(f"       {r[0]:<18} {r[1]:<28} pixeles {r[2]:>5}; media {r[3]:>7} cm/anio; minimo {r[4]:>7}")

    decir("\n     Abasto declarado por prestadores en 2020 (CNGMD):")
    cur.execute("""SELECT m.cve_ent, count(*), count(dias_semana_suministro), round(avg(dias_semana_suministro), 2), round(avg(horas_dia_suministro), 1),
                          count(*) FILTER (WHERE dias_semana_suministro < 7)
                   FROM fact_prestador_agua p JOIN dim_municipio m USING (cve_mun)
                   WHERE p.anio = 2020 AND m.cve_ent IN ('09', '15') GROUP BY 1 ORDER BY 1""")
    for r in cur.fetchall():
        decir(f"       entidad {r[0]}: prestadores {r[1]}, con dato {r[2]}, dias/semana {r[3]}, horas/dia {r[4]}, con menos de 7 dias {r[5]}")

    decir("\n     Presas de la cuenca del Rio Cutzamala, volumen en hm3 (fact_presa_diaria):")
    cur.execute("""SELECT e.nombre, count(p.volumen_hm3), min(t.fecha) FILTER (WHERE p.volumen_hm3 IS NOT NULL),
                          round(avg(p.volumen_hm3) FILTER (WHERE t.anio = 2019), 1),
                          round(min(p.volumen_hm3) FILTER (WHERE t.anio >= 2018), 1), round(max(p.volumen_hm3) FILTER (WHERE t.anio >= 2018), 1)
                   FROM fact_presa_diaria p JOIN dim_estacion_hidrometrica e USING (clave) JOIN dim_tiempo t USING (id_tiempo)
                   WHERE e.cuenca_disponibilidad = 'Río Cutzamala' GROUP BY 1 ORDER BY 1""")
    for r in cur.fetchall():
        decir(f"       {r[0]:<22} dias con volumen {r[1]:>6,}; desde {r[2]}; media 2019 {r[3]}; min y max desde 2018: {r[4]} y {r[5]}")
    cur.execute("""WITH d AS (SELECT t.fecha, t.anio, sum(p.volumen_hm3) v, count(p.volumen_hm3) n
                              FROM fact_presa_diaria p JOIN dim_estacion_hidrometrica e USING (clave) JOIN dim_tiempo t USING (id_tiempo)
                              WHERE e.cuenca_disponibilidad = 'Río Cutzamala' AND t.anio >= 2018 GROUP BY 1, 2)
                   SELECT anio, round(avg(v), 1), round(min(v), 1), count(*) FROM d WHERE n = 3 GROUP BY 1 ORDER BY 1""")
    for r in cur.fetchall():
        decir(f"       suma de las tres en {r[0]}: media {r[1]} hm3, minimo {r[2]} hm3, {r[3]} dias con las tres")

    decir("\n     Calidad del agua subterranea en acuiferos de la ZMVM, sitios por semaforo:")
    cur.execute("""SELECT a.clv_acui, a.nom_acui, count(*), count(*) FILTER (WHERE upper(s.semaforo) = 'VERDE'),
                          count(*) FILTER (WHERE upper(s.semaforo) = 'AMARILLO'), count(*) FILTER (WHERE upper(s.semaforo) = 'ROJO')
                   FROM dim_sitio_calidad s JOIN dim_acuifero a USING (clv_acui)
                   WHERE s.tipo_agua = 'subterranea' AND s.clv_acui IN ('0901', '1506', '1507', '1508') GROUP BY 1, 2 ORDER BY 1""")
    for r in cur.fetchall():
        decir(f"       {r[0]} {r[1]:<42} sitios {r[2]:>3}; verde {r[3]:>3}; amarillo {r[4]:>3}; rojo {r[5]:>3}")
    cur.execute("""SELECT s.tipo_agua, count(*), count(*) FILTER (WHERE m.en_zm_ciudad_mexico),
                          count(*) FILTER (WHERE m.cve_ent = '15'), count(*) FILTER (WHERE m.cve_ent = '09')
                   FROM dim_sitio_calidad s LEFT JOIN dim_municipio m USING (cve_mun) GROUP BY 1 ORDER BY 1""")
    for r in cur.fetchall():
        decir(f"       sitios {r[0]}: {r[1]:,} en el pais; {r[2]} en la ZM; {r[3]} en el Edomex; {r[4]} en la CDMX")

    decir("\n     Series diarias de 2019 por cuenca (fact_caudal_diario):")
    cur.execute("""SELECT coalesce(e.cuenca, 'sin cuenca en el catalogo'), count(DISTINCT e.clave), count(*), count(f.gasto_m3s), round(avg(f.gasto_m3s) FILTER (WHERE f.calidad <> 2), 2)
                   FROM fact_caudal_diario f JOIN dim_estacion_hidrometrica e USING (clave) JOIN dim_tiempo t USING (id_tiempo)
                   WHERE t.anio = 2019 GROUP BY 1 ORDER BY 3 DESC""")
    for r in cur.fetchall():
        decir(f"       {r[0]:<30} estaciones {r[1]:>3}; dias {r[2]:>6,}; con gasto {r[3]:>6,}; gasto medio {r[4]} m3/s")
    cur.close()
    conn.close()

    decir(f"\nverificaciones fallidas: {fallos}")
    SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
