#!/usr/bin/env python3
"""Reconstruct spatial/population supports from verified raw files, without SQL/Docker.

Uses the ETL's source readers, coordinate transform and nearest-point function.
Recalculates census assignment, CONAPO linkage and report assignment; contrasts
them with the existing export. JSON goes to stdout or an explicit --salida file.
With --salida, also writes a .unidades.csv sidecar for assignment diagnosis.
No source files, database tables or published exports are modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--datos-crudos', type=Path, help='verified raw cache, including D12/D13/D15 and B1/B3')
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    if args.datos_crudos:
        os.environ['DIR_DATOS_CRUDOS'] = str(args.datos_crudos.resolve())
    sys.path.insert(0, str(RAIZ / 'etl'))
    from comun import abrir_csv_zip, normalizar, verificar
    from cargar_territorio import nombre_base, clave5
    from enlace_conapo import elegir_por_puntos, candidatos_empatados
    import cargar_reportes
    import geo

    cache = {}
    paths = {key: verificar(key, cache)[0] for key in ('B1','B3','D12','D13','D15','C1h','C1i')}
    source = pd.read_csv(RAIZ.parent/'warehouse/data/consumo_agua_historico_2019.csv', dtype=str, keep_default_na=False)
    valid = source[~source.alcaldia.isin(['','NA']) & ~source.colonia.isin(['','NA']) & ~source.indice_des.isin(['','NA'])].copy()
    units = valid[['alcaldia','colonia']].drop_duplicates().sort_values(['alcaldia','colonia']).reset_index(drop=True)
    units['id_ubicacion'] = np.arange(1,len(units)+1)
    it = pd.read_csv(RAIZ.parent/'warehouse/data/iter_09_cpv2020_alcaldias.csv', dtype=str, encoding='utf-8-sig')
    it = it[(it.MUN != '000') & (it.LOC == '0000')].copy()
    by_name = dict(zip(it.NOM_MUN.map(normalizar), '09'+it.MUN.str.zfill(3)))
    def mun(alc):
        name=normalizar(alc)
        return by_name.get(name) or next(v for k,v in by_name.items() if name in k or k in name)
    units['cve_mun'] = units.alcaldia.map(mun)
    units['colonia_norm'] = units.colonia.map(normalizar)
    class Cursor:
        def execute(self, sql):
            assert sql == 'SELECT id_ubicacion, alcaldia, colonia, cve_mun FROM dim_ubicacion'
        def fetchall(self):
            return list(units[['id_ubicacion','alcaldia','colonia','cve_mun']].itertuples(index=False,name=None))
    sac = geo.puntos_sacmex(Cursor())

    # Same 750 m, same-borough census assignment as cargar_censo_colonia.py.
    blocks = geo.capa_zip(paths['B3'],'09m').to_crs(geo.CRS_METROS)
    centers = blocks.geometry.representative_point()
    geometry = pd.DataFrame({'cvegeo':blocks.CVEGEO,'x':centers.x.values,'y':centers.y.values,'cve_mun':blocks.CVEGEO.str[:5]})
    with zipfile.ZipFile(paths['B1']) as z:
        census = abrir_csv_zip(z,'conjunto_de_datos_ageb_urbana_09_cpv2020.csv')
    census.columns=[c.strip().upper() for c in census.columns]
    census=census[(census.MZA!='000') & (census.AGEB!='0000')].copy()
    census['cvegeo']=census.ENTIDAD+census.MUN+census.LOC+census.AGEB+census.MZA
    census['POBTOT']=pd.to_numeric(census.POBTOT,errors='coerce')
    census=census.merge(geometry,on='cvegeo',how='inner',validate='1:1')
    census['id_ubicacion'],distance=geo.mas_cercano(sac,census.x.values,census.y.values,max_m=750,mun=census.cve_mun.values)
    pop=census[census.id_ubicacion.notna()].groupby('id_ubicacion').POBTOT.sum(min_count=1)
    units=units.merge(pop.rename('pob_sacmex_unit'),on='id_ubicacion',how='left',validate='1:1')
    for field in ('consumo_total_dom','consumo_total_mixto','consumo_total'):
        valid[field]=pd.to_numeric(valid[field],errors='coerce')
    totals=valid.groupby(['alcaldia','colonia'])[['consumo_total_dom','consumo_total_mixto','consumo_total']].sum(min_count=1).reset_index()
    units=units.merge(totals,on=['alcaldia','colonia'],validate='1:1')

    # Same deterministic largest-vote linkage and name fallback as cargar_territorio.py.
    official=pd.read_csv(paths['D12'],dtype=str,encoding='utf-8-sig',keep_default_na=False)
    official['cve_mun']=clave5(official.CVE_MUN)
    official['colonia_norm']=official.COLONIA.map(normalizar)
    cdmx=official[official.cve_mun.str.startswith('09') & official.colonia_norm.notna()].copy()
    cdmx['base']=cdmx.colonia_norm.map(nombre_base)
    def unique(column):
        return cdmx.groupby(['cve_mun',column]).CVE_COL.agg(['first','size']).query('size==1')['first'].to_dict()
    exact,base=unique('colonia_norm'),unique('base')
    name_links={r.id_ubicacion: exact.get((r.cve_mun,r.colonia_norm)) or base.get((r.cve_mun,nombre_base(r.colonia_norm))) for r in units.itertuples()}
    polygons=gpd.read_file(f'zip://{paths["D15"].as_posix()}!colonias_imc2020.shp',where="CVE_ENT = '09'",columns=['CVE_COL','CVE_ENT'])
    polygons['cve_col']=polygons.CVE_COL.str.replace('_','').astype('int64')
    points=gpd.GeoDataFrame(sac[['id_ubicacion']],geometry=gpd.points_from_xy(sac.lon,sac.lat),crs=polygons.crs)
    cross=gpd.sjoin(points,polygons[['cve_col','geometry']],how='inner',predicate='intersects')
    votes=cross.groupby(['id_ubicacion','cve_col']).size().rename('n').reset_index()
    point_counts=sac.groupby('id_ubicacion').size()
    eligible=candidatos_empatados(votes,point_counts)
    tied_ids=eligible.id_ubicacion.unique()
    top=elegir_por_puntos(votes,point_counts)
    polygon_links=dict(zip(top.id_ubicacion,top.cve_col))
    units['cve_col']=units.id_ubicacion.map(lambda i: int(polygon_links.get(i) or name_links[i]) if polygon_links.get(i) or name_links.get(i) else None)
    units['link_method']=units.id_ubicacion.map(lambda i:'poligono' if i in polygon_links else 'nombre' if name_links.get(i) else None)

    # Same historical report filters and location assignment as cargar_reportes.py.
    reports=cargar_reportes.leer(cache)
    reports=reports[~reports.folio.isin(['','NA'])].drop_duplicates(['recurso','folio'])
    reports=reports[~reports.fecha.isin(['','NA']) & ~reports.reporte.isin(['','NA'])].copy()
    reports['fecha']=pd.to_datetime(reports.fecha,errors='coerce')
    reports=reports[reports.fecha.notna()].copy()
    names={(normalizar(r.alcaldia),r.colonia_norm):r.id_ubicacion for r in units.itertuples()}
    reports['id_ubicacion']=[names.get(k) for k in zip(reports.alcaldia.map(normalizar),reports.colonia.map(normalizar))]
    reports['id_ubicacion']=pd.to_numeric(reports.id_ubicacion,errors='coerce')
    lat,lon=pd.to_numeric(reports.latitud,errors='coerce'),pd.to_numeric(reports.longitud,errors='coerce')
    available=lat.between(*cargar_reportes.LAT)&lon.between(*cargar_reportes.LON)&reports.id_ubicacion.isna()
    x,y=geo.A_METROS.transform(lon[available].values,lat[available].values)
    report_ids,_=geo.mas_cercano(sac,x,y,max_m=cargar_reportes.DISTANCIA_MAX_M)
    reports.loc[available,'id_ubicacion']=report_ids
    potable=reports[reports.clasificacion=='Agua Potable']
    shortage=potable[(potable.reporte=='Falta de agua') & potable.fecha.between('2019-01-01','2019-06-30')].groupby('id_ubicacion').size()
    leaks=potable[(potable.reporte=='Fuga') & (potable.fecha.dt.year>=2021)].groupby('id_ubicacion').size()
    units['shortage']=units.id_ubicacion.map(shortage).fillna(0)
    units['leaks']=units.id_ubicacion.map(leaks).fillna(0)
    linked=units[units.cve_col.notna()].copy()
    grouped=linked.groupby('cve_col').agg(colonias_sacmex=('id_ubicacion','size'),
        colonias_con_pob=('pob_sacmex_unit',lambda s:int((s>0).sum())),
        colonias_con_dom=('consumo_total_dom','count'),
        pob_sacmex=('pob_sacmex_unit',lambda s:s[s>0].sum(min_count=1)),
        consumo_dom_m3=('consumo_total_dom',lambda s:s.sum(min_count=1)),
        falta_agua_2019_s1=('shortage','sum'),fugas_2021_2024=('leaks','sum')).reset_index()
    pop_complete=grouped.colonias_con_pob==grouped.colonias_sacmex
    dom_complete=grouped.colonias_con_dom==grouped.colonias_sacmex
    grouped['litros_hab_dia_dom']=(grouped.consumo_dom_m3*1000/(grouped.pob_sacmex*181)).where(pop_complete&dom_complete)
    grouped['falta_por_mil_hab']=(grouped.falta_agua_2019_s1*1000/grouped.pob_sacmex).where(pop_complete)
    grouped['fugas_por_mil_hab']=(grouped.fugas_2021_2024*1000/grouped.pob_sacmex).where(pop_complete)
    exported=json.loads((RAIZ.parent/'ijcopi/datos/04_colonias_zm.json').read_text(encoding='utf-8'))
    export=pd.DataFrame(exported['filas'],columns=exported['columnas'])
    joined=export.merge(grouped,on='cve_col',suffixes=('_export',''),how='inner',validate='1:1')
    checks={}
    tolerances={'colonias_sacmex':0,'colonias_con_pob':0,'colonias_con_dom':0,'pob_sacmex':0,
                'consumo_dom_m3':1e-6,'falta_agua_2019_s1':0,'fugas_2021_2024':0,
                'litros_hab_dia_dom':.050000001,'falta_por_mil_hab':.005000001,'fugas_por_mil_hab':.005000001}
    for field,tolerance in tolerances.items():
        actual,expected=joined[field],joined[field+'_export']
        checks[field]=int(((actual.isna()!=expected.isna()) | ((actual-expected).abs()>tolerance)).sum())
    ratio=joined.pob_sacmex/joined.pob_total
    conapo_examples=joined[joined.colonia.map(normalizar).isin(['REAL DEL MONTE','ACUEDUCTO DE GUADALUPE','EL DIVISADERO','SAN MIGUEL TOPILEJO','SAN JUAN IXTAYOPAN','SAN ANDRES TOTOLTEPEC'])]

    # The three per-capita bases: exact 181-day census, annualized /365 CONAPO,
    # and the nearest-point urban population used by the colonia layer.
    conapo=pd.read_csv(paths['D13'],dtype=str,encoding='utf-8-sig',usecols=['CLAVE','ANO','POB_MIT_MUN'])
    conapo['cve_mun']=clave5(conapo.CLAVE)
    conapo=conapo[conapo.ANO=='2019'].copy()
    conapo['pob_2019']=pd.to_numeric(conapo.POB_MIT_MUN)
    municipal=units.groupby('cve_mun').consumo_total_dom.sum(min_count=1).reset_index().merge(conapo[['cve_mun','pob_2019']],on='cve_mun',validate='1:1')
    municipal['lpcd']=municipal.consumo_total_dom*2*1000/(municipal.pob_2019*365)
    plausible=municipal[municipal.lpcd.round(1).between(10,400)]
    census_pop=pd.to_numeric(it.OCUPVIVPAR).sum()
    total_dom=valid.consumo_total_dom.sum(min_count=1)
    def rate(frame):
        return float(frame.consumo_total_dom.sum()*2*1000/(frame.pob_2019.sum()*365))
    population_rows=sorted([[r.alcaldia,r.colonia,None if pd.isna(r.pob_sacmex_unit) else int(r.pob_sacmex_unit)] for r in units.itertuples()])
    population_sha=hashlib.sha256(json.dumps(population_rows,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
    out={'versions':{'python':sys.version.split()[0],'pandas':pd.__version__,'geopandas':gpd.__version__},
        'source_sha256':{key:cache[key][2] for key in paths},
        'source_records':{'raw':len(source),'valid':len(valid),'territories':len(units),
            'coordinates_raw':len(source[['latitud','longitud']].drop_duplicates()),
            'coordinates_valid':len(valid[['latitud','longitud']].drop_duplicates()),
            'coordinate_pairs_shared_by_territories':int((valid[['latitud','longitud','alcaldia','colonia']].drop_duplicates().groupby(['latitud','longitud']).size()>1).sum()),
            'dom_null':int(valid.consumo_total_dom.isna().sum()),'mixed_null':int(valid.consumo_total_mixto.isna().sum())},
        'census_support':{'units_with_population':int(units.pob_sacmex_unit.notna().sum()),'population':float(units.pob_sacmex_unit.sum()),'blocks_assigned':int(census.id_ubicacion.notna().sum()),'assignment_sha256':population_sha},
        'conapo_support':{'linked_units':len(linked),'linked_polygons':len(grouped),'link_methods':linked.link_method.value_counts().to_dict(),
            'export_count_differences':checks,'partial_population_groups':int((~pop_complete).sum()),'groups_missing_unit_dom_subtotal':int((~dom_complete).sum()),
            'units_with_multiple_half_vote_candidates':len(tied_ids),
            'half_vote_candidates':json.loads(eligible[eligible.id_ubicacion.isin(tied_ids)].merge(units[['id_ubicacion','alcaldia','colonia']],on='id_ubicacion').to_json(orient='records')),
            'positive_population_pairs':int(ratio.notna().sum()),'population_difference_over20pct':int((abs(ratio-1)>.2).sum()),
            'population_difference_over50pct':int((abs(ratio-1)>.5).sum()),'examples':json.loads(conapo_examples[['cve_col','colonia','pob_total','pob_sacmex','colonias_sacmex','colonias_con_pob','colonias_con_dom','consumo_dom_m3','litros_hab_dia_dom','falta_agua_2019_s1','falta_por_mil_hab','fugas_2021_2024','fugas_por_mil_hab']].to_json(orient='records'))},
        'per_capita_bases':{'dom_m3_s1':float(total_dom),'census_2020_occupants_private_dwellings':int(census_pop),
            'census_181_days_lpcd':float(total_dom*1000/(census_pop*181)),
            'conapo_2019_population_16':int(municipal.pob_2019.sum()),'conapo_x2_365_lpcd_16':rate(municipal),
            'plausible_boroughs':len(plausible),'conapo_2019_population_plausible':int(plausible.pob_2019.sum()),
            'conapo_x2_365_lpcd_plausible':rate(plausible)}}
    text=json.dumps(out,ensure_ascii=False,indent=2)
    if args.salida:
        args.salida.parent.mkdir(parents=True,exist_ok=True)
        args.salida.write_text(text+'\n',encoding='utf-8',newline='\n')
        units.to_csv(args.salida.with_suffix('.unidades.csv'),index=False)
    print(text)
    return 1 if any(checks.values()) else 0


if __name__=='__main__':
    raise SystemExit(main())
