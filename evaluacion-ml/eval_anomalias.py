#!/usr/bin/env python3
"""Evaluate the deployed atypical-consumption ranking at its actual grain.

assets/atipicos.js sums consumption by alcaldia--colonia, computes the
population mean and population standard deviation of those totals per alcaldia,
and ranks A_g = abs(total - mu_alcaldia) / (sigma_alcaldia + 1e-9).  This script
implements that function exactly, on 16 alcaldias, 1,553 territorial units and
three bimesters.  Labels are injected at colonia level, the unit the browser
module scores.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from rdflib import Graph, Namespace
from rdflib.namespace import RDFS
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.neighbors import LocalOutlierFactor

EPS = 1e-9
AGUA = Namespace("https://w3id.org/cdmx/agua/")


def load_units(path: Path) -> pd.DataFrame:
    """Load the real 1,553 alcaldia--colonia identities from the demo graph."""
    graph = Graph().parse(path, format="turtle")
    borough_names = {
        iri: str(label)
        for iri, label in graph.subject_objects(RDFS.label)
        if str(iri).startswith("https://w3id.org/cdmx/agua/alcaldia/")
    }
    rows = []
    for location, borough in graph.subject_objects(AGUA.borough):
        label = graph.value(location, RDFS.label)
        if label is not None and borough in borough_names:
            rows.append((borough_names[borough], str(label)))
    units = pd.DataFrame(rows, columns=["alcaldia", "colonia"]).drop_duplicates()
    units = units.sort_values(["alcaldia", "colonia"], kind="stable").reset_index(drop=True)
    if len(units) != 1553 or units.alcaldia.nunique() != 16:
        raise ValueError(
            f"Expected 16 alcaldias and 1,553 units; got {units.alcaldia.nunique()} "
            f"and {len(units)} from {path}."
        )
    return units


def synthetic_panel(
    units: pd.DataFrame, rate: float, spike_share: float, rng: np.random.Generator
) -> tuple[pd.DataFrame, pd.Series, dict[str, int]]:
    """Create three bimesters and inject labelled anomalies by colonia."""
    borough_mu = {
        borough: rng.normal(10.7, 0.35) for borough in units.alcaldia.unique()
    }
    rows = []
    for unit_id, unit in units.iterrows():
        baseline = np.exp(borough_mu[unit.alcaldia] + rng.normal(0.0, 0.42))
        for bimester, season in enumerate((0.94, 1.00, 1.06), start=1):
            rows.append(
                (
                    unit_id,
                    2019,
                    bimester,
                    unit.alcaldia,
                    unit.colonia,
                    baseline * season * np.exp(rng.normal(0.0, 0.10)),
                )
            )
    panel = pd.DataFrame(
        rows,
        columns=["unit_id", "anio", "bimestre", "alcaldia", "colonia", "consumo"],
    )
    n_anomalies = int(round(rate * len(units)))
    selected = rng.choice(units.index.to_numpy(), n_anomalies, replace=False)
    n_spikes = int(round(spike_share * n_anomalies))
    spikes, drops = selected[:n_spikes], selected[n_spikes:]
    labels = pd.Series(False, index=units.index, name="is_anomaly")
    labels.loc[selected] = True
    factors = pd.Series(1.0, index=units.index)
    factors.loc[spikes] = rng.uniform(3.0, 6.0, size=len(spikes))
    factors.loc[drops] = rng.uniform(0.05, 0.25, size=len(drops))
    panel["consumo"] *= panel.unit_id.map(factors)
    return panel, labels, {
        "records": len(panel),
        "units": len(units),
        "alcaldias": units.alcaldia.nunique(),
        "periods": 3,
        "anomalies": n_anomalies,
        "spikes": n_spikes,
        "drops": n_anomalies - n_spikes,
    }


def deployed_scores(panel: pd.DataFrame) -> pd.DataFrame:
    """Literal data transformation in assets/atipicos.js::calcular."""
    totals = (
        panel.groupby(["alcaldia", "colonia"], as_index=False, sort=False).consumo.sum()
        .rename(columns={"consumo": "total"})
    )
    group = totals.groupby("alcaldia").total
    totals["mu_alcaldia"] = group.transform("mean")
    totals["sigma_alcaldia"] = group.transform(lambda values: values.std(ddof=0))
    totals["A_g"] = (
        (totals.total - totals.mu_alcaldia).abs() / (totals.sigma_alcaldia + EPS)
    )
    return totals


def equal_alerts(scores: np.ndarray, alert_count: int) -> np.ndarray:
    """Select exactly alert_count units, including deterministic tie handling."""
    predicted = np.zeros(len(scores), dtype=int)
    predicted[np.argsort(-scores, kind="mergesort")[:alert_count]] = 1
    return predicted


def evaluate_method(
    seed: int, name: str, labels: np.ndarray, scores: np.ndarray, alert_count: int
) -> tuple[dict[str, float | int | str], pd.DataFrame]:
    prediction = equal_alerts(scores, alert_count)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, prediction, average="binary", zero_division=0
    )
    p_curve, r_curve, thresholds = precision_recall_curve(labels, scores)
    metrics = {
        "Seed": seed,
        "Method": name,
        "Alerts": int(prediction.sum()),
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ROC-AUC": roc_auc_score(labels, scores),
        "PR-AUC": average_precision_score(labels, scores),
    }
    curve = pd.DataFrame(
        {
            "seed": seed,
            "method": name,
            "point": np.arange(len(p_curve)),
            "precision": p_curve,
            "recall": r_curve,
            "threshold": np.append(thresholds, np.nan),
        }
    )
    return metrics, curve


def evaluate_seed(
    units: pd.DataFrame, seed: int, rate: float, spike_share: float
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    panel, unit_labels, details = synthetic_panel(
        units, rate, spike_share, np.random.default_rng(seed)
    )
    totals = deployed_scores(panel).merge(
        units.reset_index(names="unit_id"),
        on=["alcaldia", "colonia"],
        validate="one_to_one",
    ).sort_values("unit_id", kind="stable")
    labels = unit_labels.loc[totals.unit_id].to_numpy(dtype=int)
    alerts = int(labels.sum())
    borough_standardised_total = (
        (totals.total - totals.mu_alcaldia) / (totals.sigma_alcaldia + EPS)
    ).to_numpy().reshape(-1, 1)

    scores = {
        "A_g (deployed ranking)": totals.A_g.to_numpy(),
        "Isolation Forest": -IsolationForest(
            n_estimators=300, contamination="auto", random_state=seed, n_jobs=-1
        ).fit(borough_standardised_total).score_samples(borough_standardised_total),
    }
    lof = LocalOutlierFactor(n_neighbors=20, contamination="auto")
    lof.fit_predict(borough_standardised_total)
    scores["LOF"] = -lof.negative_outlier_factor_

    rows, curves = [], []
    for name, values in scores.items():
        row, curve = evaluate_method(seed, name, labels, values, alerts)
        rows.append(row)
        curves.append(curve)
    return pd.DataFrame(rows), pd.concat(curves, ignore_index=True), details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--kg-demo", type=Path, default=root / "kg_demo.ttl")
    parser.add_argument("--seed-start", type=int, default=42)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--rate", type=float, default=0.03)
    parser.add_argument("--spike-share", type=float, default=0.70)
    parser.add_argument(
        "--pr-output",
        type=Path,
        default=Path(__file__).with_name("curvas_precision_recall.csv"),
    )
    args = parser.parse_args()
    if args.seeds < 20:
        parser.error("--seeds must be at least 20")
    if not 0 < args.rate < 1 or not 0 < args.spike_share < 1:
        parser.error("--rate and --spike-share must be between 0 and 1")

    units = load_units(args.kg_demo)
    metric_frames, curve_frames = [], []
    details = {}
    seeds = range(args.seed_start, args.seed_start + args.seeds)
    for seed in seeds:
        metrics, curves, details = evaluate_seed(units, seed, args.rate, args.spike_share)
        metric_frames.append(metrics)
        curve_frames.append(curves)
    results = pd.concat(metric_frames, ignore_index=True)
    all_curves = pd.concat(curve_frames, ignore_index=True)
    args.pr_output.parent.mkdir(parents=True, exist_ok=True)
    all_curves.to_csv(args.pr_output, index=False)

    print("Deployed function: aggregate total per alcaldia--colonia; population "
          "mean and population standard deviation within alcaldia; "
          "A_g = abs(total - mu_alcaldia) / (sigma_alcaldia + 1e-9).")
    print(
        f"Synthetic structure: {details['alcaldias']} alcaldias, "
        f"{details['units']} units, {details['periods']} bimesters, "
        f"{details['records']} records per seed."
    )
    print(
        f"Injected anomalies: {details['anomalies']} / {details['units']} "
        f"({100 * details['anomalies'] / details['units']:.2f}%): "
        f"{details['spikes']} spikes, {details['drops']} drops."
    )
    print(f"Seeds: {args.seed_start}--{args.seed_start + args.seeds - 1} ({args.seeds} runs).")
    print(f"Equal operating point: exactly {details['anomalies']} alerts per method and seed.")
    print("\nPer-seed metrics:")
    print(results.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    columns = ["Precision", "Recall", "F1", "ROC-AUC", "PR-AUC"]
    summary = results.groupby("Method", sort=False)[columns].agg(["mean", "std"])
    print("\nMean +/- standard deviation across seeds:")
    for method, row in summary.iterrows():
        print(method + ": " + "  ".join(
            f"{column}={row[(column, 'mean')]:.4f} +/- {row[(column, 'std')]:.4f}"
            for column in columns
        ))
    print(
        f"\nComplete precision--recall curves: {args.pr_output} "
        f"({len(all_curves):,} points)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
