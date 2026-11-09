#!/usr/bin/env python3
"""Independently check view counts, NULL guards and proxy-rate arithmetic.

Queries PostgreSQL in a read-only transaction. Expected values are recomputed in
Python Decimal from individual linked SACMEX rows; no exports/tables are written.
Use --salida to save the JSON evidence at an explicitly selected path.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'etl'))
from comun import conectar


def sum_known(values):
    values=[Decimal(value) for value in values if value is not None]
    return sum(values,Decimal(0)) if values else None


def rate(numerator,population,days,places):
    if numerator is None or population is None or population<=0:
        return None
    return (numerator*1000/(population*days)).quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP)


def json_value(value):
    if isinstance(value,Decimal):
        return int(value) if value==value.to_integral_value() else float(value)
    raise TypeError(type(value).__name__)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida',type=Path)
    args=parser.parse_args()
    conn=conectar()
    conn.set_session(readonly=True,isolation_level='REPEATABLE READ')
    errors=[]
    try:
        with conn.cursor() as cur:
            cur.execute('''SELECT u.cve_col_conapo,v.pob_censo_2020,v.consumo_dom_m3,v.falta_agua_2019_s1,v.fugas_2021_2024
                           FROM v_consumo_colonia_integrado v JOIN dim_ubicacion u USING(id_ubicacion)
                           WHERE u.cve_col_conapo IS NOT NULL''')
            groups=defaultdict(list)
            for code,*values in cur.fetchall():
                groups[code].append(values)
            cur.execute('SELECT * FROM v_colonia_conapo_contexto ORDER BY cve_col')
            names=[column.name for column in cur.description]
            rows=[dict(zip(names,row)) for row in cur.fetchall()]
            suppressed={'litros_hab_dia_dom':0,'falta_por_mil_hab':0,'fugas_por_mil_hab':0}
            for row in rows:
                group=groups.get(row['cve_col'],[])
                if not group:
                    if any(row[field] is not None for field in ('pob_sacmex','consumo_dom_m3',*suppressed)):
                        errors.append({'cve_col':row['cve_col'],'error':'Unlinked polygon has SACMEX quantities.'})
                    continue
                known_pop=[r[0] for r in group if r[0] is not None and r[0]>0]
                known_dom=[r[1] for r in group if r[1] is not None]
                population=sum_known(known_pop)
                volume=sum_known(known_dom)
                shortage=sum_known([r[2] for r in group])
                leaks=sum_known([r[3] for r in group])
                pop_available=len(known_pop)==len(group)
                dom_available=len(known_dom)==len(group)
                expected={'colonias_sacmex':len(group),'colonias_con_pob':len(known_pop),'colonias_con_dom':len(known_dom),
                          'pob_sacmex':population,'consumo_dom_m3':volume,
                          'litros_hab_dia_dom':rate(volume,population,181,1) if pop_available and dom_available else None,
                          'falta_por_mil_hab':rate(shortage,population,1,2) if pop_available else None,
                          'fugas_por_mil_hab':rate(leaks,population,1,2) if pop_available else None}
                for field,value in expected.items():
                    if row[field]!=value:
                        errors.append({'cve_col':row['cve_col'],'field':field,'expected':value,'actual':row[field]})
                old_population=sum_known([r[0] for r in group])
                legacy={'litros_hab_dia_dom':rate(volume,old_population,181,1),
                        'falta_por_mil_hab':rate(shortage,old_population,1,2),'fugas_por_mil_hab':rate(leaks,old_population,1,2)}
                for field in suppressed:
                    suppressed[field]+=int(legacy[field] is not None and row[field] is None)
            linked=[row for row in rows if row['colonias_sacmex'] is not None]
            cur.execute('SELECT count(DISTINCT id_fuente),count(*) FROM control_ingesta_fuentes')
            sources,ingestions=cur.fetchone()
            cur.execute('SELECT alcaldia,colonia,pob_censo_2020 FROM dim_ubicacion')
            population_rows=sorted([[a,c,None if p is None else int(p)] for a,c,p in cur.fetchall()])
            population_sha=hashlib.sha256(json.dumps(population_rows,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
            cur.execute('''SELECT fuente_volumen,calidad_volumen,count(*),sum(pob_2019),
                                  round(sum(vol_dom_m3_anio)*1000/NULLIF(sum(pob_2019) FILTER(WHERE vol_dom_m3_anio IS NOT NULL),0)/365,1)
                           FROM v_zm_indicadores_agua GROUP BY 1,2 ORDER BY 1,2''')
            municipal=[{'fuente':f,'calidad':q,'municipios':n,'poblacion_conapo_2019':p,'litros_hab_dia_anualizado':v}
                       for f,q,n,p,v in cur.fetchall()]
            out={'transaccion':'solo lectura','fuentes_verificadas':sources,'entradas_ingesta':ingestions,
                 'population_assignment_sha256':population_sha,
                 'poligonos_conapo':len(rows),'poligonos_con_unidades_sacmex':len(linked),
                 'unidades_sacmex_enlazadas':sum(row['colonias_sacmex'] for row in linked),
                 'grupos_sin_poblacion_en_cada_unidad':sum(row['colonias_con_pob']<row['colonias_sacmex'] for row in linked),
                 'grupos_sin_subtotal_dom_en_cada_unidad':sum(row['colonias_con_dom']<row['colonias_sacmex'] for row in linked),
                 'tasas_ahora_null_por_guardas':suppressed,
                 'tasas_disponibles':{field:sum(row[field] is not None for row in rows) for field in suppressed},
                 'ejemplos':[row for row in rows if row['cve_col'] in (90050007,90100215,90120045,90100190,90120172)],
                 'normalizacion_municipal':municipal,'verificaciones_fallidas':len(errors),'errores':errors}
    finally:
        conn.close()
    text=json.dumps(out,ensure_ascii=False,indent=2,default=json_value)
    if args.salida:
        args.salida.parent.mkdir(parents=True,exist_ok=True)
        args.salida.write_text(text+'\n',encoding='utf-8',newline='\n')
    print(text)
    return 1 if errors else 0


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    raise SystemExit(main())
