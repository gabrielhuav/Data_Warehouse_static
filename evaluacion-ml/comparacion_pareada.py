#!/usr/bin/env python3
"""Paired comparison of the deployed A_g ranking and Isolation Forest, seed by seed.

Every detector in sensibilidad_anomalias.py is scored on the same synthetic panel for
each seed, so the right comparison between two of them is paired: the difference
within each seed, not the overlap of two means with their own between-seed spread.
This script reads the per-seed results that sensibilidad_anomalias.py writes
(sensibilidad_anomalias.csv) and reports, for each injection setting, the mean paired
difference (Isolation Forest minus A_g), in how many seeds each method is ahead and a
two-sided exact conditional signed-rank sign-permutation test. The published
setting is the one in Table 5. The historical CSV column PR-AUC contains average
precision (AP), not trapezoidal integration of a precision--recall curve.

Usage: py -3 -I evaluacion-ml/comparacion_pareada.py [--csv evaluacion-ml/sensibilidad_anomalias.csv]
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import math
from pathlib import Path
import platform

import pandas as pd

DEPLOYED = "A_g (deployed ranking)"
BASELINE = "Isolation Forest"
METRICS = ("P=R=F1", "PR-AUC")
ROUND_DECIMALS = 12
QUANTUM = Decimal("1e-12")
SCALE = 10 ** ROUND_DECIMALS
PUBLISHED_ENTRIES = frozenset({
    ("prevalence", "3 % (published)"),
    ("composition", "70 % spikes (published)"),
    ("magnitude", "strong (x3-6 / x0.05-0.25, published)"),
})


@dataclass(frozen=True)
class SignedRankResult:
    positive: int
    negative: int
    zero: int
    extreme: int
    permutations: int

    @property
    def pvalue(self) -> float:
        return self.extreme / self.permutations


def exact_signed_rank(differences) -> SignedRankResult:
    """Exact conditional sign randomization, including tied ranks and zero pairs.

    Round paired differences to 12 decimal places (decimal half-even) before
    identifying zeros/ties, so float subtraction noise cannot split equal F1
    differences. Discard zero pairs (Wilcox convention), give equal absolute
    differences their average ranks, then count all 2**n equally likely sign
    assignments with integer dynamic programming. Ranks are doubled so they
    remain integers. Both tails include the observed statistic; all-zero pairs
    have p=1. This does not use SciPy's version-dependent method='auto' or its
    no-ties exact distribution. The conditional null assumes exchangeable signs
    of the nonzero paired differences; seeds are synthetic replicates.
    """
    rounded = []
    for value in differences:
        if not math.isfinite(float(value)):
            raise ValueError("Paired differences must all be finite.")
        rounded.append(int(Decimal(str(value)).quantize(QUANTUM, rounding=ROUND_HALF_EVEN) * SCALE))
    nonzero = [value for value in rounded if value]
    positive = sum(value > 0 for value in nonzero)
    negative = len(nonzero) - positive
    zero = len(rounded) - len(nonzero)
    if not nonzero:
        return SignedRankResult(0, 0, zero, 1, 1)
    if len(nonzero) > 200:
        raise ValueError("Exact signed-rank calculation supports at most 200 nonzero pairs.")

    ordered = sorted(abs(value) for value in nonzero)
    ranks2 = {}
    first = 0
    while first < len(ordered):
        last = first + 1
        while last < len(ordered) and ordered[last] == ordered[first]:
            last += 1
        ranks2[ordered[first]] = first + 1 + last  # twice the average 1-based rank
        first = last
    weights = [ranks2[abs(value)] for value in nonzero]
    total = sum(weights)
    observed = sum(weight for value, weight in zip(nonzero, weights) if value > 0)
    threshold = min(observed, total - observed)

    # counts[s] is the number of sign assignments whose doubled positive-rank
    # sum is s. Python integers keep the permutation counts exact.
    counts = [1]
    for weight in weights:
        expanded = counts + [0] * weight
        for score, count in enumerate(counts):
            expanded[score + weight] += count
        counts = expanded
    extreme = sum(count for score, count in enumerate(counts)
                  if min(score, total - score) <= threshold)
    return SignedRankResult(positive, negative, zero, extreme, 2 ** len(nonzero))


def paired(results: pd.DataFrame, metric: str) -> pd.Series:
    """Isolation Forest minus A_g, one value per seed."""
    table = results.pivot(index="seed", columns="method", values=metric)
    if table[[BASELINE, DEPLOYED]].isna().any().any():
        raise ValueError(f"Missing paired scores for {metric}.")
    return table[BASELINE] - table[DEPLOYED]


def comparison_groups(data: pd.DataFrame):
    """Collapse only the three known copies of the published configuration.

    Distinct scientific settings must remain separate even when their detector
    scores happen to coincide. Check all stored per-seed fields, not only the
    two compared metrics, before dropping a published duplicate.
    """
    groups = list(data.groupby(["factor", "setting"], sort=False))
    published = {key: group for key, group in groups if key in PUBLISHED_ENTRIES}
    if published and set(published) != PUBLISHED_ENTRIES:
        raise ValueError("The sensitivity CSV must contain all three published configuration entries.")
    reference = None
    for key, group in groups:
        if key not in PUBLISHED_ENTRIES:
            continue
        vector = group.drop(columns=["factor", "setting"]).sort_values(["seed", "method"]).reset_index(drop=True).round(ROUND_DECIMALS)
        if reference is None:
            reference = vector
        elif not reference.equals(vector):
            raise ValueError(f"Published configuration results disagree at {key!r} after 12-decimal rounding.")
    emitted_published = False
    selected = []
    for key, group in groups:
        if key in PUBLISHED_ENTRIES:
            if emitted_published:
                continue
            emitted_published = True
        selected.append((key, group))
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=Path(__file__).with_name("sensibilidad_anomalias.csv"))
    args = parser.parse_args()
    data = pd.read_csv(args.csv)
    groups = comparison_groups(data)
    print(f"Input: {args.csv.name}, {len(data)} rows; difference = {BASELINE} minus {DEPLOYED}.")
    print(f"Input SHA-256: {hashlib.sha256(args.csv.read_bytes()).hexdigest()}")
    print(f"Runtime: Python {platform.python_version()}, pandas {pd.__version__}; signed-rank uses standard-library integer arithmetic.")
    print("Exact conditional signed-rank sign permutation, two-sided, inclusive tails; average ranks for equal absolute differences.")
    print("Differences rounded to 12 decimal places (half-even); zeros omitted from ranks and count as neither method ahead; all-zero p=1.")
    print("PR-AUC is the historical CSV label for average precision (AP, sklearn.metrics.average_precision_score), not trapezoidal PR integration.\n")
    for (factor, setting), results in groups:
        cells = []
        for metric in METRICS:
            diff = paired(results, metric)
            test = exact_signed_rank(diff)
            label = "AP (CSV PR-AUC)" if metric == "PR-AUC" else metric
            cells.append(f"{label}: mean {diff.mean():+.4f} sd {diff.std(ddof=1):.4f}; "
                         f"IF ahead in {test.positive} of {len(diff)}, A_g ahead in {test.negative}, "
                         f"ties {test.zero}; p_exact = {test.pvalue:.6g} ({test.extreme}/{test.permutations})")
        print(f"{setting:<40} " + " | ".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
