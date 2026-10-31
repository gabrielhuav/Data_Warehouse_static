#!/usr/bin/env python3
"""Sensitivity of the anomaly evaluation to prevalence, composition and magnitude.

eval_anomalias.py scores the deployed ranking under a single injection model
(3 % prevalence, 70 % spikes, spikes x3-6, drops x0.05-0.25). This script repeats
that exact protocol --same 1,553 real territorial identities, same deployed
function, same baselines, same equal operating point-- while varying one factor
of the injection model at a time, and additionally reports recall separately for
spikes and drops. It also scores log-A_g, the deployed statistic computed on log
consumption, as a candidate correction.

With the default model it reproduces eval_anomalias.py number for number, which
it checks before running the grid.

    py -3.12 evaluacion-ml/sensibilidad_anomalias.py --seeds 20
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.neighbors import LocalOutlierFactor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eval_anomalias as base  # noqa: E402


@dataclass(frozen=True)
class Injection:
    name: str
    factor: str
    rate: float = 0.03
    spike_share: float = 0.70
    spike_range: tuple[float, float] = (3.0, 6.0)
    drop_range: tuple[float, float] = (0.05, 0.25)


GRID = [
    Injection("1 %", "prevalence", rate=0.01),
    Injection("3 % (published)", "prevalence"),
    Injection("5 %", "prevalence", rate=0.05),
    Injection("10 %", "prevalence", rate=0.10),
    Injection("10 % spikes", "composition", spike_share=0.10),
    Injection("30 % spikes", "composition", spike_share=0.30),
    Injection("50 % spikes", "composition", spike_share=0.50),
    Injection("70 % spikes (published)", "composition"),
    Injection("90 % spikes", "composition", spike_share=0.90),
    Injection("subtle (x1.5-2 / x0.5-0.67)", "magnitude", spike_range=(1.5, 2.0), drop_range=(0.50, 0.67)),
    Injection("moderate (x2-3 / x0.33-0.5)", "magnitude", spike_range=(2.0, 3.0), drop_range=(0.33, 0.50)),
    Injection("strong (x3-6 / x0.05-0.25, published)", "magnitude"),
]


def synthetic_panel(units: pd.DataFrame, inj: Injection, rng: np.random.Generator):
    """base.synthetic_panel with the injection model as parameters.

    The random draws are made in the same order as in eval_anomalias.py, so the
    default Injection yields the identical panel for the same seed.
    """
    borough_mu = {borough: rng.normal(10.7, 0.35) for borough in units.alcaldia.unique()}
    rows = []
    for unit_id, unit in units.iterrows():
        baseline = np.exp(borough_mu[unit.alcaldia] + rng.normal(0.0, 0.42))
        for bimester, season in enumerate((0.94, 1.00, 1.06), start=1):
            rows.append((unit_id, 2019, bimester, unit.alcaldia, unit.colonia,
                         baseline * season * np.exp(rng.normal(0.0, 0.10))))
    panel = pd.DataFrame(rows, columns=["unit_id", "anio", "bimestre", "alcaldia", "colonia", "consumo"])
    n_anomalies = int(round(inj.rate * len(units)))
    selected = rng.choice(units.index.to_numpy(), n_anomalies, replace=False)
    n_spikes = int(round(inj.spike_share * n_anomalies))
    spikes, drops = selected[:n_spikes], selected[n_spikes:]
    kind = pd.Series("normal", index=units.index)
    kind.loc[spikes] = "spike"
    kind.loc[drops] = "drop"
    factors = pd.Series(1.0, index=units.index)
    factors.loc[spikes] = rng.uniform(*inj.spike_range, size=len(spikes))
    factors.loc[drops] = rng.uniform(*inj.drop_range, size=len(drops))
    panel["consumo"] *= panel.unit_id.map(factors)
    return panel, kind


def evaluate(units: pd.DataFrame, seed: int, inj: Injection) -> pd.DataFrame:
    panel, kind = synthetic_panel(units, inj, np.random.default_rng(seed))
    totals = base.deployed_scores(panel).merge(
        units.reset_index(names="unit_id"), on=["alcaldia", "colonia"], validate="one_to_one"
    ).sort_values("unit_id", kind="stable")
    kinds = kind.loc[totals.unit_id].to_numpy()
    labels = (kinds != "normal").astype(int)
    alerts = int(labels.sum())
    z = ((totals.total - totals.mu_alcaldia) / (totals.sigma_alcaldia + base.EPS)).to_numpy().reshape(-1, 1)
    scores = {
        "A_g (deployed ranking)": totals.A_g.to_numpy(),
        "Isolation Forest": -IsolationForest(
            n_estimators=300, contamination="auto", random_state=seed, n_jobs=-1
        ).fit(z).score_samples(z),
    }
    lof = LocalOutlierFactor(n_neighbors=20, contamination="auto")
    lof.fit_predict(z)
    scores["LOF"] = -lof.negative_outlier_factor_
    # Same statistic on log consumption: a multiplicative drop and a multiplicative
    # spike then lie at symmetric distances from the borough mean.
    log_total = np.log(totals.total)
    by_borough = log_total.groupby(totals.alcaldia)
    scores["log-A_g (proposed)"] = (
        (log_total - by_borough.transform("mean")).abs()
        / (by_borough.transform(lambda v: v.std(ddof=0)) + base.EPS)
    ).to_numpy()

    rows = []
    for method, values in scores.items():
        flagged = base.equal_alerts(values, alerts).astype(bool)
        row = {
            "factor": inj.factor, "setting": inj.name, "seed": seed, "method": method,
            "anomalies": alerts, "spikes": int((kinds == "spike").sum()), "drops": int((kinds == "drop").sum()),
            "P=R=F1": flagged[labels == 1].mean(),
            "ROC-AUC": roc_auc_score(labels, values),
            "PR-AUC": average_precision_score(labels, values),
        }
        for k in ("spike", "drop"):
            mask = kinds == k
            row[f"recall_{k}s"] = flagged[mask].mean() if mask.any() else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def check_reproduces_published(units: pd.DataFrame, seed: int) -> None:
    """The default model must give exactly what eval_anomalias.py gives."""
    ours = evaluate(units, seed, Injection("check", "check"))
    theirs, _, _ = base.evaluate_seed(units, seed, 0.03, 0.70)
    for _, row in theirs.iterrows():
        mine = ours[ours.method == row.Method].iloc[0]
        for a, b in (("P=R=F1", "F1"), ("ROC-AUC", "ROC-AUC"), ("PR-AUC", "PR-AUC")):
            if not np.isclose(mine[a], row[b], rtol=0, atol=1e-12):
                raise SystemExit(f"Default model diverges from eval_anomalias.py: {row.Method} {b}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--kg-demo", type=Path, default=root / "kg_demo.ttl")
    parser.add_argument("--seed-start", type=int, default=42)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("sensibilidad_anomalias.csv"))
    args = parser.parse_args()

    units = base.load_units(args.kg_demo)
    check_reproduces_published(units, args.seed_start)
    print("Default injection model reproduces eval_anomalias.py exactly (checked on seed "
          f"{args.seed_start}).")
    seeds = range(args.seed_start, args.seed_start + args.seeds)
    results = pd.concat([evaluate(units, s, inj) for inj in GRID for s in seeds], ignore_index=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)

    cols = ["P=R=F1", "ROC-AUC", "PR-AUC", "recall_spikes", "recall_drops"]
    summary = results.groupby(["factor", "setting", "method"], sort=False)[cols].agg(["mean", "std"])
    print(f"Seeds {seeds.start}--{seeds.stop - 1} ({args.seeds} runs per setting); "
          "equal operating point: as many alerts as injected anomalies.\n")
    current = None
    for (factor, setting, method), row in summary.iterrows():
        if factor != current:
            print(f"== {factor} ==")
            current = factor
        cells = "  ".join(
            f"{c}={row[(c, 'mean')]:.3f}+/-{row[(c, 'std')]:.3f}" if not np.isnan(row[(c, 'mean')]) else f"{c}=n/a"
            for c in cols)
        print(f"{setting:<40} {method:<24} {cells}")
    print(f"\nPer-seed results: {args.output} ({len(results):,} rows).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
