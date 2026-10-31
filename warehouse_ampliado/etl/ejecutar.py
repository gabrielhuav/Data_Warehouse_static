#!/usr/bin/env python3
"""Construye el almacen ampliado sobre el almacen de warehouse/ ya levantado.

    python -I etl/ejecutar.py                    limpia, crea el esquema y corre todos los pasos
    python -I etl/ejecutar.py --pasos clima      repite solo esos pasos

Cada paso confirma en su propia transaccion: si uno falla no deja datos a medias y el
error dice cual fue. Ningun paso escribe en fact_consumo_agua ni en fact_clima.
"""
from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import RAIZ, conectar  # noqa: E402

PASOS = {
    "territorio": ("cargar_territorio", []),
    "agua_municipal": ("cargar_agua_municipal", ["fact_agua_municipio", "fact_facturacion_agua", "fact_prestador_agua",
                                                 "fact_abasto_localidad", "fact_fuente_captacion", "fact_planta_agua",
                                                 "fact_recaudacion_agua", "dim_tipo_toma", "dim_tipo_fuente_captacion"]),
    "sequia": ("cargar_sequia", ["fact_sequia_municipio", "dim_categoria_sequia"]),
    "subterranea": ("cargar_subterranea", ["puente_municipio_acuifero", "fact_nivel_piezometrico", "dim_pozo",
                                           "fact_disponibilidad_acuifero", "dim_acuifero"]),
    "hidrometria": ("cargar_hidrometria", ["fact_presa_diaria", "fact_caudal_diario", "dim_estacion_hidrometrica"]),
    "presas": ("cargar_presas", ["fact_presa_diaria"]),
    "calidad": ("cargar_calidad", ["fact_calidad_agua", "dim_parametro_calidad", "dim_sitio_calidad"]),
    "reportes": ("cargar_reportes", ["fact_reporte_agua", "dim_tipo_reporte", "dim_medio_recepcion"]),
    "censo_colonia": ("cargar_censo_colonia", []),
    "economia": ("cargar_economia", []),
    "clima": ("cargar_clima", ["fact_clima_colonia", "fact_clima_municipio"]),
    "subsidencia": ("cargar_subsidencia", ["fact_subsidencia_colonia", "fact_subsidencia_municipio"]),
    "vulnerabilidad": ("cargar_vulnerabilidad", ["fact_vulnerabilidad_alcaldia"]),
    "geometria": ("cargar_geometria", ["geo_territorio"]),
}


def sql(cur, nombre: str) -> None:
    cur.execute((RAIZ / "ddl" / nombre).read_text(encoding="utf-8"))


def correr(conn, paso: str, cache: dict) -> None:
    modulo, tablas = PASOS[paso]
    print(f"\n== {paso}")
    t0 = time.time()
    with conn.cursor() as cur:
        if tablas:
            cur.execute(f"TRUNCATE {', '.join(tablas)} RESTART IDENTITY CASCADE")
        importlib.import_module(modulo).ejecutar(cur, cache)
    conn.commit()
    print(f"   listo en {time.time() - t0:.0f} s")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pasos", nargs="*", choices=list(PASOS))
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    cache: dict = {}
    conn = conectar()
    try:
        if args.pasos is None:
            with conn.cursor() as cur:
                for s in ("00_limpiar.sql", "10_dimensiones.sql", "20_hechos.sql"):
                    sql(cur, s)
            conn.commit()
        for paso in (args.pasos if args.pasos is not None else PASOS):
            try:
                correr(conn, paso, cache)
            except Exception:
                conn.rollback()
                print(f"\nFALLO EL PASO {paso}; se revirtio y no dejo datos a medias")
                raise
        with conn.cursor() as cur:
            sql(cur, "30_vistas.sql")
            cur.execute("ANALYZE")
        conn.commit()
    finally:
        conn.close()
    print("\nalmacen ampliado listo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
