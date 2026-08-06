#!/usr/bin/env python3
"""
reproducir_cifras.py -- Reproduce the volume and cleaning figures of the paper
directly from the source CSV files, without a database.

It replicates exactly what the SQL ETL of the warehouse does:
  * dim_ubicacion   <- DISTINCT (alcaldia, colonia) WHERE colonia IS NOT NULL
  * dim_indice_des  <- DISTINCT indice_des
  * dim_tiempo      <- DISTINCT DATE(fecha_hora) from the climate CSV
  * fact_consumo    <- staging INNER JOINed against the three dimensions

The INNER JOINs are the cleaning step: any record that fails to match a
dimension is silently dropped. This script makes that loss explicit and
countable, which is what the paper's cleaning table reports.

Verified output on the published data (6 Aug 2026):
    source 71,102 -> discarded 216 (0.30%) -> fact 70,886 (99.70%)
    dim_ubicacion 1,553   dim_tiempo 181   dim_indice_des 4

Usage:
    python reproducir_cifras.py \
        --consumo data/consumo_agua_historico_2019.csv \
        --clima   data/open-meteo-19.44N99.11W2233m.csv
"""

from __future__ import annotations

import argparse
import collections
import csv
import statistics
import sys

NULOS = {"", "NA"}


def es_nulo(v) -> bool:
    return v is None or v.strip() in NULOS


def bimestre(mes: int) -> int:
    return (mes - 1) // 2 + 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--consumo", required=True)
    ap.add_argument("--clima", required=True)
    ap.add_argument("--correlacion", action="store_true",
                    help="also run the climate/consumption correlation query")
    args = ap.parse_args()

    # ---------------- dim_tiempo + fact_clima (from the climate CSV) ------
    por_dia: dict[str, list[dict]] = collections.defaultdict(list)
    with open(args.clima, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            por_dia[r["time"][:10]].append(r)

    col_t = "temperature_2m (°C)"
    col_h = "relative_humidity_2m (%)"
    col_l = "rain (mm)"
    clima = {}
    for dia, rs in por_dia.items():
        t = [float(x[col_t]) for x in rs if not es_nulo(x[col_t])]
        h = [float(x[col_h]) for x in rs if not es_nulo(x[col_h])]
        ll = [float(x[col_l]) for x in rs if not es_nulo(x[col_l])]
        clima[dia] = dict(
            tmax=max(t), tmin=min(t), tavg=statistics.mean(t),
            hum=statistics.mean(h) if h else None, lluvia=sum(ll),
            anio=int(dia[:4]), bimestre=bimestre(int(dia[5:7])),
        )

    # ---------------- staging_consumo -------------------------------------
    with open(args.consumo, encoding="utf-8", errors="replace") as fh:
        filas = list(csv.DictReader(fh))
    total = len(filas)

    def ok_territorio(r):
        return not es_nulo(r["colonia"]) and not es_nulo(r["alcaldia"])

    def ok_indice(r):
        return not es_nulo(r["indice_des"])

    def ok_fecha(r):
        return r["fecha_referencia"] in clima

    # First-match attribution, mirroring the order of the JOINs in 3_fact.sql
    criterios = [
        ("Unmatched territorial label", lambda r: not ok_territorio(r)),
        ("Missing development index", lambda r: ok_territorio(r) and not ok_indice(r)),
        ("Date absent from dim_tiempo",
         lambda r: ok_territorio(r) and ok_indice(r) and not ok_fecha(r)),
    ]
    cargados = [r for r in filas
                if ok_territorio(r) and ok_indice(r) and ok_fecha(r)]

    print(f"\nSource records read: {total:,}\n")
    print(f"{'Criterion':<42}{'Records':>10}{'% of source':>14}")
    print("-" * 66)
    for nombre, test in criterios:
        n = sum(1 for r in filas if test(r))
        print(f"{nombre:<42}{n:>10,}{100*n/total:>13.2f}%")
    desc = total - len(cargados)
    print("-" * 66)
    print(f"{'Total discarded':<42}{desc:>10,}{100*desc/total:>13.2f}%")
    print(f"{'Loaded into the fact table':<42}{len(cargados):>10,}"
          f"{100*len(cargados)/total:>13.2f}%")

    # ---------------- dimension cardinalities -----------------------------
    ubic = {(r["alcaldia"], r["colonia"]) for r in filas
            if not es_nulo(r["colonia"])}
    idx = {r["indice_des"] for r in filas if not es_nulo(r["indice_des"])}
    print(f"\n{'Table':<28}{'Records':>10}")
    print("-" * 38)
    print(f"{'fact_consumo_agua':<28}{len(cargados):>10,}")
    print(f"{'dim_ubicacion':<28}{len(ubic):>10,}")
    print(f"{'dim_tiempo':<28}{len(clima):>10,}")
    print(f"{'dim_indice_des':<28}{len(idx):>10,}")
    print(f"\ndim_indice_des members: {sorted(idx)}")
    fechas = sorted({r['fecha_referencia'] for r in cargados})
    print(f"Reading dates in the source: {len(fechas)} -> {fechas}")
    print(f"dim_tiempo range: {min(clima)} .. {max(clima)}  "
          f"({len(clima)} daily climate observations)")

    # ---------------- domestic / non-domestic split -----------------------
    print(f"\n{'Borough':<26}{'Total':>16}{'Non-dom':>16}{'% non-dom':>11}")
    print("-" * 69)
    agg = collections.defaultdict(lambda: [0.0, 0.0])
    for r in cargados:
        a = agg[r["alcaldia"]]
        a[0] += float(r["consumo_total"] or 0)
        a[1] += float(r["consumo_total_no_dom"] or 0)
    for alc, (tot, nod) in sorted(agg.items(), key=lambda x: -x[1][0]):
        pct = 100 * nod / tot if tot else 0
        print(f"{alc:<26}{tot:>16,.0f}{nod:>16,.0f}{pct:>10.1f}%")

    # ---------------- correlation query -----------------------------------
    if args.correlacion:
        print(f"\n{'Year':>6}{'Bim':>5}{'Total water':>16}{'Temp':>8}"
              f"{'Heat d.':>9}{'Cold d.':>9}{'Rain':>9}")
        print("-" * 62)
        agua = collections.defaultdict(float)
        for r in cargados:
            b = clima[r["fecha_referencia"]]["bimestre"]
            agua[(2019, b)] += float(r["consumo_total"] or 0)
        for (a, b), tot in sorted(agua.items()):
            dias = [v for v in clima.values()
                    if v["anio"] == a and v["bimestre"] == b]
            print(f"{a:>6}{b:>5}{tot:>16,.2f}"
                  f"{statistics.mean(d['tavg'] for d in dias):>8.2f}"
                  f"{sum(1 for d in dias if d['tmax'] >= 28):>9}"
                  f"{sum(1 for d in dias if d['tmin'] <= 10):>9}"
                  f"{sum(d['lluvia'] for d in dias):>9.2f}")

    print("\n>> These are the figures the paper must report. Nothing here is")
    print(">> estimated: every number is recomputed from the published CSVs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
