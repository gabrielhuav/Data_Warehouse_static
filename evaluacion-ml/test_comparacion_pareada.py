"""Check the exact signed-rank DP against independent exhaustive sign enumeration."""
from fractions import Fraction
from itertools import product
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from comparacion_pareada import exact_signed_rank, paired, comparison_groups, METRICS


def enumerate_signs(values):
    values = [v for v in values if v]
    if not values:
        return Fraction(1)
    magnitudes = [abs(v) for v in values]
    ranks = [Fraction(2 * sum(x < abs(v) for x in magnitudes)
                      + sum(x == abs(v) for x in magnitudes) + 1, 2) for v in values]
    total = sum(ranks)
    observed = sum(rank for value, rank in zip(values, ranks) if value > 0)
    cutoff = abs(2 * observed - total)
    extreme = 0
    for signs in product((-1, 1), repeat=len(values)):
        signed_sum = sum(sign * rank for sign, rank in zip(signs, ranks))
        extreme += abs(signed_sum) >= cutoff
    return Fraction(extreme, 2 ** len(values))


class ExactSignedRankTests(unittest.TestCase):
    def test_ties_zeros_and_inclusive_tails(self):
        cases = [[], [0, 0], [1], [1, 1], [1, -1], [1, 2, 3],
                 [0, 1, 1, -2], [1, -1, 2, 2, -3, 0], [1, 1, 1, -1, -1]]
        for values in cases:
            with self.subTest(values=values):
                result = exact_signed_rank(values)
                self.assertEqual(Fraction(result.extreme, result.permutations), enumerate_signs(values))
                opposite = exact_signed_rank([-v for v in values])
                self.assertEqual(result.pvalue, opposite.pvalue)

    def test_decimal_rounding_preserves_quantized_f1_ties(self):
        plain = exact_signed_rank([1 / 47, 1 / 47, -2 / 47, 0])
        noise = exact_signed_rank([1 / 47 + 1e-16, 1 / 47 - 1e-16, -2 / 47, 1e-16])
        self.assertEqual(plain, noise)
        self.assertEqual(exact_signed_rank([0.49e-12]).zero, 1)
        self.assertEqual(exact_signed_rank([0.51e-12]).positive, 1)

    def test_rejects_nonfinite_values(self):
        for value in (float('nan'), float('inf'), -float('inf')):
            with self.assertRaises(ValueError):
                exact_signed_rank([value])

    def test_stored_twenty_seed_grid_against_all_sign_assignments(self):
        data = pd.read_csv(Path(__file__).with_name('sensibilidad_anomalias.csv'))
        for setting, group in data.groupby(['factor', 'setting']):
            for metric in METRICS:
                with self.subTest(setting=setting, metric=metric):
                    differences = paired(group, metric)
                    result = exact_signed_rank(differences)
                    values = np.round(differences.to_numpy(), 12)
                    values = values[values != 0]
                    magnitudes = np.abs(values)
                    weights = np.array([2 * (magnitudes < v).sum() + (magnitudes == v).sum() + 1
                                        for v in magnitudes], dtype=np.int64)
                    # Explicitly materialize one sum for every sign assignment,
                    # independent of the production DP that stores multiplicities.
                    assignments = np.array([0], dtype=np.int64)
                    for weight in weights:
                        assignments = np.concatenate((assignments, assignments + weight))
                    total = weights.sum()
                    observed = weights[values > 0].sum()
                    extreme = np.count_nonzero(np.abs(2 * assignments - total) >= abs(2 * observed - total))
                    self.assertEqual(result.extreme, extreme)
                    self.assertEqual(result.permutations, len(assignments))

    def test_only_published_duplicates_are_collapsed(self):
        data = pd.read_csv(Path(__file__).with_name('sensibilidad_anomalias.csv'))
        self.assertEqual(len(comparison_groups(data)), 10)
        # A scientifically different setting with identical scores is retained.
        duplicate = data[(data.factor == 'prevalence') & (data.setting == '1 %')].copy()
        duplicate['setting'] = 'different setting with coincident scores'
        self.assertEqual(len(comparison_groups(pd.concat([data, duplicate]))), 11)
        changed = data.copy()
        first = changed.index[(changed.factor == 'composition') & (changed.setting == '70 % spikes (published)')][0]
        changed.loc[first, 'PR-AUC'] += .01
        with self.assertRaisesRegex(ValueError, 'Published configuration results disagree'):
            comparison_groups(changed)


if __name__ == '__main__':
    unittest.main()
