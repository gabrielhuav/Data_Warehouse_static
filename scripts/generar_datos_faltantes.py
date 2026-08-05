#!/usr/bin/env python3
"""
generar_datos_faltantes.py
===========================
Produces the three sets of numbers marked in red as [?] in the camera-ready
LaTeX source. Run it, copy the printed values into the .tex, and delete the
\\fillin{} markers.

Requirements:  pip install psycopg2-binary requests pandas

Usage:
    python generar_datos_faltantes.py limpieza  --csv datos_sacmex.csv
    python generar_datos_faltantes.py consultas --base-url http://localhost:8000
    python generar_datos_faltantes.py reparto   --dsn "postgresql://user:pw@host/db"
"""

import argparse
import statistics
import sys
import time

# =====================================================================
# 1) TABLE 2  -- records discarded during validation and cleaning
#    (Reviewer #5: "specify the approximate percentage of records
#     discarded, along with the main exclusion criteria")
# =====================================================================
CDMX_BBOX = dict(lat_min=19.04, lat_max=19.60, lon_min=-99.36, lon_max=-98.94)


def limpieza(csv_path: str) -> None:
    import pandas as pd

    df = pd.read_csv(csv_path, low_memory=False)
    total = len(df)
    print(f"Source records read: {total:,}\n")

    # Adjust these column names to the actual header of the SACMEX CSV.
    col_consumo = "consumo_total"
    col_lat, col_lon = "latitud", "longitud"
    col_alc, col_col = "alcaldia", "colonia"
    col_fecha = "fecha"

    reasons = {}

    m = pd.to_numeric(df.get(col_consumo), errors="coerce").isna()
    reasons["Missing or non-numeric measure"] = m

    lat = pd.to_numeric(df.get(col_lat), errors="coerce")
    lon = pd.to_numeric(df.get(col_lon), errors="coerce")
    m = (
        lat.isna() | lon.isna()
        | ~lat.between(CDMX_BBOX["lat_min"], CDMX_BBOX["lat_max"])
        | ~lon.between(CDMX_BBOX["lon_min"], CDMX_BBOX["lon_max"])
    )
    reasons["Null or out-of-range coordinates"] = m

    m = df.get(col_alc).isna() | df.get(col_col).isna()
    reasons["Unmatched territorial label"] = m

    m = pd.to_datetime(df.get(col_fecha), errors="coerce").isna()
    reasons["Unparseable reading date"] = m

    # First-match attribution so the rows sum to the total (no double counting)
    already = pd.Series(False, index=df.index)
    print(f"{'Criterion':<38}{'Records':>10}{'% of source':>14}")
    print("-" * 62)
    for name, mask in reasons.items():
        excl = mask & ~already
        already = already | mask
        print(f"{name:<38}{excl.sum():>10,}{100*excl.sum()/total:>13.2f}%")

    disc = int(already.sum())
    print("-" * 62)
    print(f"{'Total discarded':<38}{disc:>10,}{100*disc/total:>13.2f}%")
    print(f"{'Loaded into the fact table':<38}{total-disc:>10,}"
          f"{100*(total-disc)/total:>13.2f}%")
    print("\n>> If 'Loaded' != 70,886, the ETL applies rules not modelled here.")
    print(">> Either align this script with loader.py, or correct the paper.")


# =====================================================================
# 2) TABLE 9  -- response time of the retrieval endpoints over the
#    COMPLETE warehouse (Reviewer #5: "no performance metric for query
#    execution over the total data volume")
# =====================================================================
def consultas(base_url: str, n: int = 200) -> None:
    import requests

    workloads = {
        "Paginated retrieval (limit=100)": "/api/consumption?limit=100",
        "Full aggregation by borough": "/api/consumption/by-borough",
        "Aggregation by neighbourhood and bimester": "/api/consumption/by-colonia-bimestre",
        "Top-10 neighbourhoods with ordering": "/api/consumption/top?limit=10",
    }

    print(f"{n} executions per workload, after 10 warm-up calls\n")
    print(f"{'Workload':<44}{'Mean (ms)':>11}{'p95 (ms)':>10}{'n':>6}")
    print("-" * 71)
    for label, path in workloads.items():
        url = base_url.rstrip("/") + path
        try:
            for _ in range(10):
                requests.get(url, timeout=30)
            samples = []
            for _ in range(n):
                t0 = time.perf_counter()
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                samples.append((time.perf_counter() - t0) * 1000)
            samples.sort()
            p95 = samples[int(0.95 * len(samples)) - 1]
            print(f"{label:<44}{statistics.mean(samples):>11.1f}"
                  f"{p95:>10.1f}{n:>6}")
        except Exception as exc:
            print(f"{label:<44}{'ERROR':>11}  {exc}")

    print("\n>> Also record the hardware/hosting in the paper: the sentence")
    print(">> 'on [hardware/hosting description]' must be replaced.")


# =====================================================================
# 3) SECTION 5.2 -- domestic vs non-domestic share by borough
#    (needed for the two [?] markers in the Findings section)
# =====================================================================
def reparto(dsn: str) -> None:
    import psycopg2

    sql = """
        SELECT l.alcaldia,
               SUM(f.consumo_total)                                  AS total,
               SUM(f.consumo_no_dom)                                 AS no_dom,
               100.0*SUM(f.consumo_no_dom)/NULLIF(SUM(f.consumo_total),0) AS pct_no_dom
        FROM fact_water_consumption f
        JOIN dim_location l USING (location_id)
        GROUP BY l.alcaldia
        ORDER BY total DESC;
    """
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(sql)
        print(f"{'Borough':<24}{'Total (m3)':>16}{'Non-dom (m3)':>16}{'% non-dom':>11}")
        print("-" * 67)
        for alc, tot, nod, pct in cur.fetchall():
            print(f"{alc:<24}{tot:>16,.0f}{(nod or 0):>16,.0f}{(pct or 0):>10.1f}%")

    print("\n>> Copy the Cuauhtemoc and Gustavo A. Madero percentages into")
    print(">> Section 5.2. If the columns do not exist, the claim about the")
    print(">> domestic/non-domestic decomposition must be REMOVED from the paper.")


# =====================================================================
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("limpieza"); a.add_argument("--csv", required=True)
    b = sub.add_parser("consultas")
    b.add_argument("--base-url", required=True)
    b.add_argument("--n", type=int, default=200)
    c = sub.add_parser("reparto"); c.add_argument("--dsn", required=True)

    args = ap.parse_args()
    if args.cmd == "limpieza":
        limpieza(args.csv)
    elif args.cmd == "consultas":
        consultas(args.base_url, args.n)
    else:
        reparto(args.dsn)
    return 0


if __name__ == "__main__":
    sys.exit(main())
