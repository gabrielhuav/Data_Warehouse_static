#!/usr/bin/env python3
"""Recalculate fiscal-index grain and unweighted record means from SACMEX CSV.

Read-only, standard-library only. Missing numeric values (NA or empty) stay
missing and are excluded from each field's mean, as in SQL AVG; they are never
converted to zero. Records without alcaldia or colonia (NA or empty) are excluded.
The index is a source-record attribute, not one mutually exclusive category per
neighbourhood. consumo_prom is an average already supplied by the source; this
script does not infer account counts or reconstruct an account-weighted average.

Usage: python evaluacion-ml/indice_fiscal_grano.py [--csv warehouse/data/consumo_agua_historico_2019.csv]
JSON is written to stdout; redirect it explicitly to save evidence.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

FIELDS = ('consumo_total', 'consumo_prom')


def missing(value: str) -> bool:
    return value.strip() in ('', 'NA')


def nullable_number(value: str) -> Decimal | None:
    if missing(value):
        return None
    number = Decimal(value)
    if not number.is_finite():
        raise ValueError(f'Nonfinite numeric value: {value!r}')
    return number


def calculate(path: Path) -> dict:
    groups = defaultdict(set)
    totals = defaultdict(lambda: {'records': 0, **{f: [] for f in FIELDS}})
    source_rows = retained = missing_index = 0
    with path.open(encoding='utf-8-sig', newline='') as handle:
        for row in csv.DictReader(handle):
            source_rows += 1
            if missing(row['alcaldia']) or missing(row['colonia']):
                continue
            retained += 1
            key = (row['alcaldia'], row['colonia'])
            indices = groups[key]  # retain the territorial pair even if index is missing
            index = row['indice_des']
            if missing(index):
                missing_index += 1
                continue
            indices.add(index)
            bucket = totals[index]
            bucket['records'] += 1
            for field in FIELDS:
                value = nullable_number(row[field])
                if value is not None:
                    bucket[field].append(value)
    means = {}
    for index, values in sorted(totals.items()):
        means[index] = {'n': values['records']}
        for field in FIELDS:
            valid = values[field]
            means[index][field + '_valid_n'] = len(valid)
            means[index][field + '_mean'] = float(sum(valid, Decimal(0)) / len(valid)) if valid else None
    return {
        'input_name': path.name,
        'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'source_rows': source_rows,
        'retained_records': retained,
        'excluded_missing_territory': source_rows - retained,
        'retained_records_missing_index': missing_index,
        'territorial_pairs': len(groups),
        'pairs_with_multiple_indices': sum(len(indices) > 1 for indices in groups.values()),
        'grain': 'Source billing records, grouped by indice_des; territories keyed by (alcaldia, colonia).',
        'means': 'Unweighted arithmetic means across non-null source-record values; NA/empty are not zero.',
        'consumo_prom_note': 'Reported source average; account counts and account weighting are not inferred.',
        'per_record_mean_by_index': means,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=Path(__file__).resolve().parents[1] / 'warehouse/data/consumo_agua_historico_2019.csv')
    args = parser.parse_args()
    print(json.dumps(calculate(args.csv), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
