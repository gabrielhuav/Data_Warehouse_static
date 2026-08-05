#!/usr/bin/env python3
"""
loader.py -- ETL for the CDMX water-consumption data warehouse.

Implements the four phases described in Section 4 (ETL Consolidation
Process) of the ICOKG 2026 paper:

  1. Extraction              -- read the SACMEX open CSV files
  2. Validation and cleaning -- discard records failing the four criteria
  3. Staging + dimensions    -- COPY to staging, populate the dimensions
  4. Fact load               -- resolve surrogate keys, insert facts

The exclusion criteria and their order are the same ones reported in the
cleaning table of the paper, so that the counts printed by
scripts/generar_datos_faltantes.py and the counts printed here agree.

PROVENANCE
  Reconstruction written for the camera-ready artefact. It reproduces the
  documented pipeline; it is not the original loader used for the
  submission. Numbers it produces must be re-derived, not assumed.

Usage:
    python loader.py --csv datos_sacmex.csv \
                     --dsn "postgresql://user:pw@localhost/agua" \
                     --schema schema.sql
    python loader.py --csv datos_sacmex.csv --dry-run   # cleaning report only
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import unicodedata
from datetime import datetime

CDMX_BBOX = dict(lat_min=19.04, lat_max=19.60, lon_min=-99.36, lon_max=-98.94)

# Source header -> canonical name. Extend if the SACMEX export changes.
COLUMN_ALIASES = {
    "consumo_total": ["consumo_total", "consumo_total_mixto", "total"],
    "consumo_promedio": ["consumo_prom", "consumo_promedio", "promedio"],
    "consumo_dom": ["consumo_total_dom", "consumo_dom"],
    "consumo_no_dom": ["consumo_total_no_dom", "consumo_no_dom"],
    "consumo_mixto": ["consumo_total_mixto", "consumo_mixto"],
    "alcaldia": ["alcaldia", "nomgeo", "delegacion"],
    "colonia": ["colonia", "nom_colonia"],
    "indice_des": ["indice_des", "indice_desarrollo", "index_des"],
    "latitud": ["latitud", "lat", "y"],
    "longitud": ["longitud", "lon", "lng", "x"],
    "fecha": ["fecha", "fecha_referencia", "fecha_lectura"],
    "anio": ["anio", "año", "year"],
    "bimestre": ["bimestre", "bim"],
}

EXCLUSION_ORDER = [
    "Missing or non-numeric measure",
    "Null or out-of-range coordinates",
    "Unmatched territorial label",
    "Unparseable reading date",
]


# ---------------------------------------------------------------- helpers
def norm(s: str) -> str:
    """Fold accents and case so header matching is robust."""
    s = unicodedata.normalize("NFKD", (s or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def resolve_headers(fieldnames):
    found = {}
    available = {norm(f): f for f in (fieldnames or [])}
    for canon, aliases in COLUMN_ALIASES.items():
        for a in aliases:
            if norm(a) in available:
                found[canon] = available[norm(a)]
                break
    return found


def to_float(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def to_date(v):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(v).strip(), fmt).date()
        except (TypeError, ValueError):
            continue
    return None


def bimester_of(d):
    return (d.month - 1) // 2 + 1


# ------------------------------------------------------- phases 1 and 2
def extract_and_clean(csv_path: str):
    """Yield clean rows; return them plus the exclusion tally."""
    tally = {k: 0 for k in EXCLUSION_ORDER}
    clean, total = [], 0

    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        cols = resolve_headers(reader.fieldnames)
        missing = {"consumo_total", "alcaldia", "colonia"} - set(cols)
        if missing:
            sys.exit(f"FATAL: source is missing required columns: {missing}\n"
                     f"       headers seen: {reader.fieldnames}")

        for raw in reader:
            total += 1
            g = lambda c: raw.get(cols.get(c, ""), None)  # noqa: E731

            # -- criterion 1: measure ---------------------------------
            consumo = to_float(g("consumo_total"))
            if consumo is None or consumo < 0:
                tally[EXCLUSION_ORDER[0]] += 1
                continue

            # -- criterion 2: coordinates -----------------------------
            lat, lon = to_float(g("latitud")), to_float(g("longitud"))
            if (lat is None or lon is None
                    or not CDMX_BBOX["lat_min"] <= lat <= CDMX_BBOX["lat_max"]
                    or not CDMX_BBOX["lon_min"] <= lon <= CDMX_BBOX["lon_max"]):
                tally[EXCLUSION_ORDER[1]] += 1
                continue

            # -- criterion 3: territorial label -----------------------
            alcaldia = (g("alcaldia") or "").strip()
            colonia = (g("colonia") or "").strip()
            if not alcaldia or not colonia:
                tally[EXCLUSION_ORDER[2]] += 1
                continue

            # -- criterion 4: reading date ----------------------------
            fecha = to_date(g("fecha"))
            if fecha is None:
                anio, bim = to_float(g("anio")), to_float(g("bimestre"))
                if anio and bim:
                    fecha = to_date(f"{int(anio)}-{2*int(bim)-1:02d}-01")
            if fecha is None:
                tally[EXCLUSION_ORDER[3]] += 1
                continue

            clean.append(dict(
                fecha=fecha, anio=fecha.year, bimestre=bimester_of(fecha),
                alcaldia=alcaldia, colonia=colonia,
                indice_des=(g("indice_des") or "No especificado").strip()
                            or "No especificado",
                latitud=lat, longitud=lon,
                consumo_total=consumo,
                consumo_promedio=to_float(g("consumo_promedio")),
                consumo_dom=to_float(g("consumo_dom")),
                consumo_no_dom=to_float(g("consumo_no_dom")),
                consumo_mixto=to_float(g("consumo_mixto")),
            ))
    return clean, tally, total


def report(tally, total, kept):
    print(f"\nSource records read: {total:,}\n")
    print(f"{'Criterion':<38}{'Records':>10}{'% of source':>14}")
    print("-" * 62)
    for k in EXCLUSION_ORDER:
        print(f"{k:<38}{tally[k]:>10,}{100*tally[k]/max(total,1):>13.2f}%")
    disc = sum(tally.values())
    print("-" * 62)
    print(f"{'Total discarded':<38}{disc:>10,}{100*disc/max(total,1):>13.2f}%")
    print(f"{'Loaded into the fact table':<38}{kept:>10,}"
          f"{100*kept/max(total,1):>13.2f}%")
    print("\n>> Copy these figures into the cleaning table of the paper.")


# ------------------------------------------------------- phases 3 and 4
def load(rows, dsn: str, schema_path: str | None):
    import psycopg2
    from psycopg2.extras import execute_values

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    cur = conn.cursor()

    if schema_path:
        with open(schema_path, encoding="utf-8") as fh:
            cur.execute(fh.read())
        print(f"Schema applied from {schema_path}")

    # -- phase 3a: COPY into staging ---------------------------------
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
    for r in rows:
        w.writerow([
            r["fecha"], r["anio"], r["bimestre"], r["alcaldia"], r["colonia"],
            r["indice_des"], r["latitud"], r["longitud"], r["consumo_total"],
            r["consumo_promedio"], r["consumo_dom"], r["consumo_no_dom"],
            r["consumo_mixto"],
        ])
    buf.seek(0)
    cur.execute("TRUNCATE staging_consumo;")
    cur.copy_expert(
        "COPY staging_consumo FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        buf,
    )
    print(f"Staged {len(rows):,} rows")

    # -- phase 3b: dimensions ----------------------------------------
    cur.execute("""
        INSERT INTO dim_time (fecha, anio, bimestre)
        SELECT DISTINCT fecha::date, anio::int, bimestre::smallint
        FROM staging_consumo
        ON CONFLICT (fecha) DO NOTHING;
    """)
    cur.execute("""
        INSERT INTO dim_location (colonia, alcaldia, latitud, longitud, geom)
        SELECT DISTINCT ON (alcaldia, colonia)
               colonia, alcaldia,
               latitud::double precision, longitud::double precision,
               ST_SetSRID(ST_MakePoint(longitud::double precision,
                                       latitud::double precision), 4326)
        FROM staging_consumo
        ON CONFLICT (alcaldia, colonia) DO NOTHING;
    """)
    cur.execute("""
        INSERT INTO dim_dev_index (nivel)
        SELECT DISTINCT indice_des FROM staging_consumo
        ON CONFLICT (nivel) DO NOTHING;
    """)

    # -- phase 4: facts ----------------------------------------------
    cur.execute("""
        INSERT INTO fact_water_consumption (
            time_id, location_id, dev_index_id,
            consumo_total, consumo_promedio,
            consumo_dom, consumo_no_dom, consumo_mixto)
        SELECT t.time_id, l.location_id, d.dev_index_id,
               s.consumo_total::numeric,
               NULLIF(s.consumo_promedio,'')::numeric,
               NULLIF(s.consumo_dom,'')::numeric,
               NULLIF(s.consumo_no_dom,'')::numeric,
               NULLIF(s.consumo_mixto,'')::numeric
        FROM staging_consumo s
        JOIN dim_time      t ON t.fecha    = s.fecha::date
        JOIN dim_location  l ON l.alcaldia = s.alcaldia
                            AND l.colonia  = s.colonia
        JOIN dim_dev_index d ON d.nivel    = s.indice_des;
    """)
    conn.commit()

    for tbl in ("fact_water_consumption", "dim_location",
                "dim_time", "dim_dev_index"):
        cur.execute(f"SELECT count(*) FROM {tbl};")
        print(f"{tbl:<28}{cur.fetchone()[0]:>10,}")
    print("\n>> These four counts are the ones the paper's data-volume table "
          "must report.")
    cur.close()
    conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", required=True, help="SACMEX open-data CSV")
    ap.add_argument("--dsn", help="PostgreSQL DSN; omit with --dry-run")
    ap.add_argument("--schema", help="path to schema.sql, applied before load")
    ap.add_argument("--dry-run", action="store_true",
                    help="only extract, clean and print the exclusion report")
    args = ap.parse_args()

    rows, tally, total = extract_and_clean(args.csv)
    report(tally, total, len(rows))

    if args.dry_run:
        return 0
    if not args.dsn:
        sys.exit("ERROR: --dsn is required unless --dry-run is given.")
    load(rows, args.dsn, args.schema)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
