#!/usr/bin/env python3
"""Domestic consumption per inhabitant by borough, from the warehouse source file
and the 2020 Census.

Sums the domestic billed volume of the first semester of 2019 by alcaldía (rows
with a territorial label, as loaded into the fact table) and divides it by the
residents of private dwellings counted by the 2020 Census (OCUPVIVPAR, ITER) and
by the 181 days from 1 January to 30 June 2019. Mixed-use billing is reported
apart as an upper bound, since it covers premises that are partly domestic.

    py -3.12 scripts/per_capita_alcaldia.py \
        --consumo warehouse/data/consumo_agua_historico_2019.csv \
        --iter    warehouse/data/iter_09_cpv2020_alcaldias.csv

warehouse/data/iter_09_cpv2020_alcaldias.csv holds the 17 rows with LOC = 0000
(the city and its 16 boroughs) of INEGI's "Principales resultados por localidad
(ITER) 2020" for Mexico City, iter_09_cpv2020_csv.zip, unmodified; INEGI's terms
of free use allow its redistribution with credit. The full ITER file also works.
"""
from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path

import pandas as pd

DIAS = 181  # 1 January to 30 June 2019


def clave(nombre: str) -> str:
    sin_acentos = unicodedata.normalize("NFD", nombre).encode("ascii", "ignore").decode()
    return " ".join(sin_acentos.upper().replace(".", ". ").split()).replace(" .", ".")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--consumo", type=Path, required=True)
    parser.add_argument("--iter", type=Path, required=True)
    parser.add_argument("--salida", type=Path, default=None, help="optional CSV with the table")
    args = parser.parse_args()

    c = pd.read_csv(args.consumo)
    c = c[(c.alcaldia != "NA") & c.alcaldia.notna() & (c.colonia != "NA") & c.colonia.notna()]
    por = c.groupby("alcaldia")[["consumo_total_dom", "consumo_total_mixto", "consumo_total"]].sum()
    por.index = por.index.map(clave)

    it = pd.read_csv(args.iter, dtype=str, encoding="utf-8-sig")
    it = it[(it.MUN != "000") & (it.LOC == "0000")].copy()
    it["clave"] = it.NOM_MUN.map(clave)
    it = it.set_index("clave")[["MUN", "NOM_MUN", "POBTOT", "OCUPVIVPAR"]]
    it[["POBTOT", "OCUPVIVPAR"]] = it[["POBTOT", "OCUPVIVPAR"]].astype(int)

    t = it.join(por, how="outer")
    faltan = t[t.isna().any(axis=1)]
    if len(faltan):
        raise SystemExit(f"Boroughs that do not match between the two files:\n{faltan}")
    t["l_hab_dia_dom"] = t.consumo_total_dom * 1000 / (t.OCUPVIVPAR * DIAS)
    t["l_hab_dia_dom_mixto"] = (t.consumo_total_dom + t.consumo_total_mixto) * 1000 / (t.OCUPVIVPAR * DIAS)
    t["m3_total_hab"] = t.consumo_total / t.POBTOT
    t = t.sort_values("l_hab_dia_dom", ascending=False)

    ciudad_dom = t.consumo_total_dom.sum() * 1000 / (t.OCUPVIVPAR.sum() * DIAS)
    ciudad_mix = (t.consumo_total_dom.sum() + t.consumo_total_mixto.sum()) * 1000 / (t.OCUPVIVPAR.sum() * DIAS)
    print(f"Rows used: {len(c):,}; boroughs: {len(t)}; residents of private dwellings (2020): {t.OCUPVIVPAR.sum():,}")
    print(f"City: {ciudad_dom:.1f} l/inhabitant/day domestic, {ciudad_mix:.1f} with mixed use.\n")
    cols = ["NOM_MUN", "OCUPVIVPAR", "consumo_total_dom", "l_hab_dia_dom", "l_hab_dia_dom_mixto", "consumo_total"]
    print(t[cols].to_string(index=False, float_format=lambda v: f"{v:,.1f}"))
    rank_total = t.consumo_total.rank(ascending=False).astype(int)
    rank_pc = t.l_hab_dia_dom.rank(ascending=False).astype(int)
    print("\nRank by total consumption -> rank by domestic consumption per inhabitant:")
    for k in t.sort_values("consumo_total", ascending=False).index:
        print(f"  {t.loc[k, 'NOM_MUN']:<24} {rank_total[k]:>2} -> {rank_pc[k]:>2}")
    if args.salida:
        t.to_csv(args.salida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
