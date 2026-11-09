#!/usr/bin/env python3
"""Review/apply only deterministic CONAPO tie corrections, without reloading facts.

Default is read-only. --aplicar updates only dim_ubicacion.cve_col_conapo for units
with multiple half-vote polygon candidates. All files are verified, changes are
listed as JSON, and the updates occur in one transaction with row-level checks.
No facts, original identifiers, populations or other links are modified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import geopandas as gpd

sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import conectar, verificar
from enlace_conapo import candidatos_empatados, elegir_por_puntos
import geo


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aplicar',action='store_true')
    args=parser.parse_args()
    p,_=verificar('D15')
    conn=conectar()
    conn.set_session(readonly=not args.aplicar,isolation_level='REPEATABLE READ')
    try:
        with conn:
            with conn.cursor() as cur:
                sac=geo.puntos_sacmex(cur)
                polygons=gpd.read_file(f'zip://{p.as_posix()}!colonias_imc2020.shp',where="CVE_ENT = '09'",columns=['CVE_COL','CVE_ENT'])
                polygons['cve_col']=polygons.CVE_COL.str.replace('_','').astype('int64')
                points=gpd.GeoDataFrame(sac[['id_ubicacion']],geometry=gpd.points_from_xy(sac.lon,sac.lat),crs=polygons.crs)
                cross=gpd.sjoin(points,polygons[['cve_col','geometry']],how='inner',predicate='intersects')
                votes=cross.groupby(['id_ubicacion','cve_col']).size().rename('n').reset_index()
                totals=sac.groupby('id_ubicacion').size()
                candidates=candidatos_empatados(votes,totals)
                tied=set(int(i) for i in candidates.id_ubicacion.unique())
                chosen=elegir_por_puntos(votes,totals)
                targets={int(r.id_ubicacion):int(r.cve_col) for r in chosen.itertuples() if int(r.id_ubicacion) in tied}
                cur.execute('SELECT id_ubicacion,alcaldia,colonia,cve_col_conapo,enlace_conapo FROM dim_ubicacion ORDER BY id_ubicacion' + (' FOR UPDATE' if args.aplicar else ''))
                changes=[]
                for unit,borough,name,before,method in cur.fetchall():
                    if unit not in targets or before==targets[unit]:
                        continue
                    if method!='poligono':
                        raise ValueError(f'Unexpected non-polygon link for tied unit {unit}: {method!r}')
                    valid=set(int(c) for c in candidates.loc[candidates.id_ubicacion==unit,'cve_col'])
                    if before not in valid:
                        raise ValueError(f'Existing link for unit {unit} is not one of its tied candidates.')
                    changes.append({'id_ubicacion':unit,'alcaldia':borough,'colonia':name,'antes':before,'despues':targets[unit]})
                if args.aplicar:
                    for change in changes:
                        cur.execute('UPDATE dim_ubicacion SET cve_col_conapo=%s WHERE id_ubicacion=%s AND cve_col_conapo=%s AND enlace_conapo=\'poligono\'',
                                    (change['despues'],change['id_ubicacion'],change['antes']))
                        if cur.rowcount!=1:
                            raise ValueError('Concurrent or unexpected change; rolling back all corrections.')
                print(json.dumps({'modo':'aplicar' if args.aplicar else 'solo lectura','regla':'maximum points; at least 50%; tied maximum selects smallest numeric cve_col',
                                  'unidades_empatadas':len(tied),'cambios':changes,'actualizadas':len(changes) if args.aplicar else 0},ensure_ascii=False,indent=2))
    finally:
        conn.close()
    return 0


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    raise SystemExit(main())
