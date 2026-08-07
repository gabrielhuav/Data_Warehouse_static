#!/usr/bin/env python3
"""
benchmark_consultas.py -- Response time of the retrieval workloads over the
complete warehouse (Reviewer #5: "no performance metric for query execution
over the total data volume").

Measures the four workloads of the paper directly against PostgreSQL, over all
70,886 fact rows. Reports mean, p95 and the number of executions, and prints
the LaTeX table body ready to paste.

IMPORTANT: this measures SQL latency at the database, not end-to-end latency of
the REST API. The paper must say so; the script prints the wording to use.

    pip install psycopg2-binary

    python scripts/benchmark_consultas.py \
        --dsn "postgresql://postgres:postgres@localhost:5433/data_warehouse" \
        --n 200 --latex
"""

from __future__ import annotations

import argparse
import platform
import statistics
import sys
import time

WORKLOADS = {
    "Paginated retrieval (limit=100)": """
        SELECT t.anio, t.bimestre, t.fecha, u.alcaldia, u.colonia,
               i.indice_des, f.consumo_total, f.consumo_prom
        FROM   fact_consumo_agua f
        JOIN   dim_tiempo     t USING (id_tiempo)
        JOIN   dim_ubicacion  u USING (id_ubicacion)
        JOIN   dim_indice_des i USING (id_indice_des)
        ORDER  BY t.anio, t.bimestre, u.alcaldia, u.colonia
        LIMIT  100 OFFSET 0;
    """,
    "Full aggregation by borough": """
        SELECT u.alcaldia, COUNT(*), SUM(f.consumo_total),
               AVG(f.consumo_prom), SUM(f.consumo_total_no_dom),
               100.0*SUM(f.consumo_total_no_dom)/NULLIF(SUM(f.consumo_total),0)
        FROM   fact_consumo_agua f
        JOIN   dim_ubicacion u USING (id_ubicacion)
        GROUP  BY u.alcaldia
        ORDER  BY 3 DESC;
    """,
    "Aggregation by neighbourhood and bimester": """
        SELECT u.alcaldia, u.colonia, t.anio, t.bimestre,
               SUM(f.consumo_total), AVG(f.consumo_prom)
        FROM   fact_consumo_agua f
        JOIN   dim_ubicacion u USING (id_ubicacion)
        JOIN   dim_tiempo    t USING (id_tiempo)
        GROUP  BY u.alcaldia, u.colonia, t.anio, t.bimestre
        ORDER  BY u.alcaldia, u.colonia, t.anio, t.bimestre;
    """,
    "Top-10 neighbourhoods with ordering": """
        SELECT u.alcaldia, u.colonia, SUM(f.consumo_total) AS total
        FROM   fact_consumo_agua f
        JOIN   dim_ubicacion u USING (id_ubicacion)
        GROUP  BY u.alcaldia, u.colonia
        ORDER  BY total DESC
        LIMIT  10;
    """,
}


def entorno(cur) -> dict:
    cur.execute("SHOW server_version;")
    pg = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM fact_consumo_agua;")
    filas = cur.fetchone()[0]
    try:
        import psutil
        ram = f"{psutil.virtual_memory().total/1024**3:.0f} GB RAM"
        cpu = f"{psutil.cpu_count(logical=True)} logical cores"
    except ImportError:
        ram, cpu = "RAM n/d", f"{platform.machine()}"
    return dict(pg=pg, filas=filas, ram=ram, cpu=cpu,
                so=f"{platform.system()} {platform.release()}",
                proc=platform.processor() or platform.machine())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dsn", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--latex", action="store_true")
    args = ap.parse_args()

    import psycopg2

    conn = psycopg2.connect(args.dsn)
    cur = conn.cursor()
    env = entorno(cur)

    print("=" * 76)
    print("QUERY RESPONSE TIME OVER THE COMPLETE WAREHOUSE")
    print("=" * 76)
    print(f"  Fact rows scanned : {env['filas']:,}")
    print(f"  PostgreSQL        : {env['pg']}")
    print(f"  Host              : {env['so']}, {env['cpu']}, {env['ram']}")
    print(f"  Executions        : {args.n} per workload, after {args.warmup} warm-up calls")
    print()
    print(f"  {'Workload':<44}{'Mean (ms)':>11}{'p95 (ms)':>11}{'n':>6}")
    print("  " + "-" * 70)

    resultados = []
    for etiqueta, sql in WORKLOADS.items():
        for _ in range(args.warmup):
            cur.execute(sql); cur.fetchall()
        m = []
        for _ in range(args.n):
            t0 = time.perf_counter()
            cur.execute(sql); cur.fetchall()
            m.append((time.perf_counter() - t0) * 1000)
        m.sort()
        media = statistics.mean(m)
        p95 = m[int(0.95 * len(m)) - 1]
        resultados.append((etiqueta, media, p95))
        print(f"  {etiqueta:<44}{media:>11.1f}{p95:>11.1f}{args.n:>6}")

    cur.close(); conn.close()

    if args.latex:
        print("\n" + "=" * 76)
        print("TABLE BODY FOR THE PAPER (paste into Table 9)")
        print("=" * 76)
        for etiqueta, media, p95 in resultados:
            print(f"{etiqueta} & {env['filas']:,} & {media:.1f} & {p95:.1f} & {args.n} \\\\")
        print("\n% Replace the two \\fillin{} markers above the table with:")
        print(f"%   executed {args.n} times after a warm-up round, on "
              f"{env['so']}, {env['cpu']}, {env['ram']}, PostgreSQL {env['pg']} in Docker")

    print("\n" + "=" * 76)
    print("WORDING THE PAPER MUST USE")
    print("=" * 76)
    print("  These are SQL latencies measured at the database over all")
    print(f"  {env['filas']:,} fact rows, not end-to-end latencies of the REST API.")
    print("  State it explicitly: a reviewer who reads 'dashboard response time'")
    print("  will assume the figure includes serialisation and network transfer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
