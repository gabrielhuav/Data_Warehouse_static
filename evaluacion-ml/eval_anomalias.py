#!/usr/bin/env python3
"""
eval_anomalias.py -- Controlled evaluation of the atypical-consumption module.

Reference implementation of the protocol described in Section 5 of the ICOKG
2026 paper. It builds a synthetic dataset with the structure of the warehouse,
injects labelled anomalies, and compares three detectors under the operating
points stated in the paper.

Protocol (as specified in the paper):
  * N ~= 11,460 records over 16 boroughs, 5 years x 6 bimesters
  * 3% labelled anomalies: 70% high spikes, 30% drops
  * Features: log-scaled consumption, ratio to the neighbourhood mean
  * Operating points: z-score A_g > 3 ; IsolationForest s > 0.60 ; LOF s > 1.5
  * Fixed seed for reproducibility

IMPORTANT -- PROVENANCE
  This script is a reconstruction written for the camera-ready artefact. It was
  NOT the code used to produce the figures in the original submission. Run it
  and report the numbers it actually emits; do not copy numbers from elsewhere.

Usage:
    pip install -r requirements.txt
    python eval_anomalias.py                # default: seed 42, N = 11460
    python eval_anomalias.py --seed 7 --n 11460 --latex
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    average_precision_score,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.neighbors import LocalOutlierFactor

BOROUGHS = [
    "Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán",
    "Cuajimalpa de Morelos", "Cuauhtémoc", "Gustavo A. Madero", "Iztacalco",
    "Iztapalapa", "La Magdalena Contreras", "Miguel Hidalgo", "Milpa Alta",
    "Tlalpan", "Venustiano Carranza", "Tláhuac", "Xochimilco",
]
YEARS = [2019, 2020, 2021, 2022, 2023]
BIMESTERS = [1, 2, 3, 4, 5, 6]
EPS = 1e-9


def build_dataset(n_target: int, rate: float, spike_share: float, rng):
    """Synthetic panel with the grain of fact_water_consumption."""
    periods = len(YEARS) * len(BIMESTERS)              # 30
    n_colonias = max(1, round(n_target / periods))     # ~382
    per_borough = int(np.ceil(n_colonias / len(BOROUGHS)))

    rows = []
    for borough in BOROUGHS:
        # each borough has its own consumption regime
        mu_b = rng.normal(11.6, 0.35)
        for c in range(per_borough):
            mu_c = mu_b + rng.normal(0, 0.25)
            colonia = f"{borough[:12]}-COL-{c:03d}"
            for year in YEARS:
                for bim in BIMESTERS:
                    # mild seasonality: bimesters 2-3 run higher
                    season = 0.08 * np.sin((bim - 1) / 6 * 2 * np.pi)
                    val = np.exp(mu_c + season + rng.normal(0, 0.18))
                    rows.append((year, bim, borough, colonia, val))

    df = pd.DataFrame(
        rows, columns=["anio", "bimestre", "alcaldia", "colonia", "consumo"]
    )
    df = df.sample(n=min(n_target, len(df)), random_state=int(rng.integers(1e6)))
    df = df.sort_values(["alcaldia", "colonia", "anio", "bimestre"])
    df = df.reset_index(drop=True)

    # --- inject labelled anomalies -------------------------------------
    n_anom = int(round(rate * len(df)))
    idx = rng.choice(len(df), size=n_anom, replace=False)
    n_spike = int(round(spike_share * n_anom))
    spikes, drops = idx[:n_spike], idx[n_spike:]

    df["is_anomaly"] = 0
    df.loc[spikes, "consumo"] *= rng.uniform(3.0, 6.0, size=len(spikes))
    df.loc[drops, "consumo"] *= rng.uniform(0.05, 0.25, size=len(drops))
    df.loc[idx, "is_anomaly"] = 1
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """log-scaled consumption and ratio to the neighbourhood mean."""
    df = df.copy()
    df["log_consumo"] = np.log1p(df["consumo"])
    grp = df.groupby("colonia")["consumo"]
    df["ratio_vecindario"] = df["consumo"] / (grp.transform("mean") + EPS)
    # A_g: z-score of the record within its territorial group
    mu = grp.transform("mean")
    sd = grp.transform("std").fillna(0.0)
    df["A_g"] = ((df["consumo"] - mu) / (sd + EPS)).abs()
    return df


def metrics(name, y_true, y_pred, score):
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    return {
        "Method": name,
        "Precision": p,
        "Recall": r,
        "F1": f1,
        "ROC-AUC": roc_auc_score(y_true, score),
        "PR-AUC": average_precision_score(y_true, score),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=11460)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--rate", type=float, default=0.03)
    ap.add_argument("--spike-share", type=float, default=0.70)
    ap.add_argument("--thr-zscore", type=float, default=3.0)
    ap.add_argument("--thr-iforest", type=float, default=0.60)
    ap.add_argument("--thr-lof", type=float, default=1.5)
    ap.add_argument("--latex", action="store_true",
                    help="also print the LaTeX table body")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    df = add_features(build_dataset(args.n, args.rate, args.spike_share, rng))
    y = df["is_anomaly"].to_numpy()

    print(f"Records: {len(df):,}   Boroughs: {df.alcaldia.nunique()}   "
          f"Neighbourhoods: {df.colonia.nunique():,}")
    print(f"Injected anomalies: {y.sum():,} ({100*y.mean():.2f}%)   "
          f"seed={args.seed}\n")

    X = df[["log_consumo", "ratio_vecindario"]].to_numpy()
    results = []

    # 1) z-score A_g (this work)
    s = df["A_g"].to_numpy()
    results.append(metrics(f"z-score A_g (A_g>{args.thr_zscore:g})",
                           y, (s > args.thr_zscore).astype(int), s))

    # 2) Isolation Forest -- score min-max normalised to [0,1]
    iso = IsolationForest(n_estimators=200, contamination=args.rate,
                          random_state=args.seed)
    iso.fit(X)
    raw = -iso.score_samples(X)
    s = (raw - raw.min()) / (raw.max() - raw.min() + EPS)
    results.append(metrics(f"Isolation Forest (s>{args.thr_iforest:g})",
                           y, (s > args.thr_iforest).astype(int), s))

    # 3) Local Outlier Factor -- s is the outlier factor itself
    lof = LocalOutlierFactor(n_neighbors=20, contamination=args.rate)
    lof.fit_predict(X)
    s = -lof.negative_outlier_factor_
    results.append(metrics(f"LOF (s>{args.thr_lof:g})",
                           y, (s > args.thr_lof).astype(int), s))

    out = pd.DataFrame(results).set_index("Method")
    print(out.to_string(float_format=lambda v: f"{v:.3f}"))

    if args.latex:
        print("\n% --- table body for the paper ---")
        for m, row in out.iterrows():
            print(f"{m} & " + " & ".join(f"{row[c]:.3f}" for c in out.columns)
                  + r" \\")

    print("\nNOTE: these are the numbers this script actually produces. If they")
    print("differ from the table in the manuscript, the table must be updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
