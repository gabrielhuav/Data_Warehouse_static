"""Deterministic choice of a CONAPO polygon for a SACMEX territorial unit."""
from __future__ import annotations

import pandas as pd


def elegir_por_puntos(votos: pd.DataFrame, total_puntos: pd.Series) -> pd.DataFrame:
    """Pick the largest vote count; tied counts use the smallest numeric cve_col.

    Require at least half of the unit's points. A 50/50 choice is a documented
    tie-break for a proxy link, not evidence that either polygon contains most
    of the unit. Sorting must not depend on database surrogate IDs or input
    row order, which changed the former quicksort's selection in tied groups.
    """
    order = votos.sort_values(['id_ubicacion','n','cve_col'], ascending=[True,False,True], kind='stable')
    top = order.drop_duplicates('id_ubicacion')
    return top[top.n / top.id_ubicacion.map(total_puntos) >= .5].copy()


def candidatos_empatados(votos: pd.DataFrame, total_puntos: pd.Series) -> pd.DataFrame:
    eligible = votos[votos.n / votos.id_ubicacion.map(total_puntos) >= .5]
    eligible = eligible[eligible.n == eligible.groupby('id_ubicacion').n.transform('max')]
    return eligible[eligible.id_ubicacion.duplicated(False)].sort_values(['id_ubicacion','cve_col'],kind='stable')
