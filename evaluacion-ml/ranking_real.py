#!/usr/bin/env python3
"""The deployed ranking and its log-scale variant on the real SACMEX data.

Replicates assets/atipicos.js::calcular over consumo.json with no filter (all
bimesters, all boroughs): consumption is summed by alcaldia--colonia, and each
colonia is scored against the population mean and standard deviation of its
own borough. Reports

* how skewed the colonia totals are within each borough, raw and in logs, which
  is what decides whether a symmetric |z| can see drops at all;
* the largest score a colonia below its borough mean can reach, against the
  score of the 15th entry the interface shows;
* how many of the 15 colonias the interface lists, and of the top 3 %, lie below
  their borough mean, under A_g and under log-A_g, and how much the two lists
  overlap.

    py -3.12 evaluacion-ml/ranking_real.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

EPS = 1e-9
TOPE = 15  # entries the interface lists (assets/atipicos.js)


def skew(values: pd.Series) -> float:
    centred = values - values.mean()
    sd = values.std(ddof=0)
    return float((centred ** 3).mean() / sd ** 3) if sd > 0 else float("nan")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--consumo", type=Path, default=root / "consumo.json")
    args = parser.parse_args()

    filas = pd.DataFrame(json.loads(args.consumo.read_text(encoding="utf8"))["consumo_colonia"])
    filas["consumo_total"] = pd.to_numeric(filas.consumo_total, errors="coerce").fillna(0.0)
    t = filas.groupby(["alcaldia", "colonia"], as_index=False).consumo_total.sum().rename(columns={"consumo_total": "total"})
    g = t.groupby("alcaldia").total
    t["mu"] = g.transform("mean")
    t["sigma"] = g.transform(lambda v: v.std(ddof=0))
    t["A_g"] = (t.total - t.mu).abs() / (t.sigma + EPS)
    t["below"] = t.total < t.mu

    ceros = int((t.total <= 0).sum())
    positivos = t[t.total > 0].copy()
    lg = np.log(positivos.total)
    gl = lg.groupby(positivos.alcaldia)
    positivos["log_A_g"] = (lg - gl.transform("mean")).abs() / (gl.transform(lambda v: v.std(ddof=0)) + EPS)
    t = t.merge(positivos[["alcaldia", "colonia", "log_A_g"]], on=["alcaldia", "colonia"], how="left")
    # A colonia with no billed volume has no logarithm. It is reported apart, as its own
    # flag, and the log ranking orders the colonias that do have a volume.
    t["log_A_g"] = t.log_A_g.fillna(-np.inf)

    print(f"Input: {args.consumo.name}, {len(filas):,} colonia-period rows -> {len(t):,} alcaldia--colonia totals "
          f"in {t.alcaldia.nunique()} boroughs; {ceros} with zero total.")

    sk = pd.DataFrame({
        "raw": t.groupby("alcaldia").total.apply(skew),
        "log": positivos.assign(l=np.log(positivos.total)).groupby("alcaldia").l.apply(skew),
        "cv": t.groupby("alcaldia").total.std(ddof=0) / t.groupby("alcaldia").total.mean(),
    })
    print("\nWithin-borough skewness of colonia totals (median over boroughs): "
          f"raw {sk.raw.median():.2f}, log {sk.log.median():.2f}; "
          f"raw skew > 1 in {(sk.raw > 1).sum()} of {len(sk)} boroughs, log |skew| > 1 in {(sk.log.abs() > 1).sum()}.")
    # A colonia below its borough mean can score at most mu/sigma = 1/CV (total -> 0).
    techo = 1 / sk.cv
    print(f"Largest A_g reachable below the mean (1/CV): median {techo.median():.2f}, "
          f"range {techo.min():.2f}-{techo.max():.2f} across boroughs.")

    n3 = int(round(0.03 * len(t)))
    for nombre, col in (("A_g (deployed)", "A_g"), ("log-A_g", "log_A_g")):
        orden = t.sort_values(col, ascending=False, kind="mergesort")
        for k in (TOPE, n3):
            top = orden.head(k)
            print(f"{nombre:<15} top {k:>3}: {int(top.below.sum()):>3} below their borough mean "
                  f"({100 * top.below.mean():.0f} %)" + (f"; 15th score {orden[col].iloc[TOPE - 1]:.2f}" if k == TOPE else ""))
    for k in (TOPE, n3):
        a = set(map(tuple, t.sort_values("A_g", ascending=False, kind="mergesort").head(k)[["alcaldia", "colonia"]].values))
        b = set(map(tuple, t.sort_values("log_A_g", ascending=False, kind="mergesort").head(k)[["alcaldia", "colonia"]].values))
        print(f"Overlap of the two top-{k} lists: {len(a & b)} of {k}.")
    print(f"\nColonias below their borough mean: {int(t.below.sum()):,} of {len(t):,}; "
          f"highest A_g among them {t[t.below].A_g.max():.2f}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
