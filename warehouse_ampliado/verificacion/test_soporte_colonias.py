"""Execute the actual CONAPO-context SQL with controlled NULL/coverage cases.

Uses SQLite only for this portable SQL fragment; PostgreSQL/export verification
remains a separate required check against the live warehouse.
"""
from pathlib import Path
import sqlite3
import sys
import unittest

import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'etl'))
from enlace_conapo import elegir_por_puntos, candidatos_empatados


class ContextCoverageTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
            CREATE TABLE dim_municipio(cve_mun TEXT, en_zm_ciudad_mexico INTEGER);
            INSERT INTO dim_municipio VALUES ('09010',1);
            CREATE TABLE dim_colonia_conapo(cve_col INTEGER,cve_mun TEXT,colonia TEXT,
                pob_total REAL,pct_ocup_sin_agua REAL,pct_ocup_sin_drenaje REAL,im_2020 REAL,gm_2020 TEXT);
            CREATE TABLE dim_ubicacion(id_ubicacion INTEGER,cve_col_conapo INTEGER);
            CREATE TABLE v_consumo_colonia_integrado(id_ubicacion INTEGER,consumo_dom_m3 REAL,
                pob_censo_2020 REAL,falta_agua_2019_s1 INTEGER,fugas_2021_2024 INTEGER,vlm_media_cm_anio REAL);
        ''')
        for code in range(1, 7):
            self.db.execute('INSERT INTO dim_colonia_conapo VALUES (?,\'09010\',?,9999,0,0,0,\'Bajo\')', (code, str(code)))
        fixtures = [
            (1, 1, 10., 100., 3, 5), (2, 1, 20., 200., 6, 10),
            (3, 2, 10., 100., 3, 5), (4, 2, 20., None, 6, 10),
            (5, 3, 10., 100., 3, 5), (6, 3, None, 200., 6, 10),
            (7, 5, None, 100., 3, 5),
            (8, 6, 0., 100., 0, 0), (9, 6, 0., 200., 0, 0),
        ]
        for unit, code, volume, population, shortage, leaks in fixtures:
            self.db.execute('INSERT INTO dim_ubicacion VALUES (?,?)', (unit, code))
            self.db.execute('INSERT INTO v_consumo_colonia_integrado VALUES (?,?,?,?,?,0)',
                            (unit, volume, population, shortage, leaks))
        sql = (Path(__file__).resolve().parents[1] / 'ddl/30_vistas.sql').read_text(encoding='utf-8')
        fragment = 'CREATE VIEW v_colonia_conapo_contexto AS' + sql.split('CREATE VIEW v_colonia_conapo_contexto AS', 1)[1].split(';', 1)[0] + ';'
        self.db.executescript(fragment)

    def tearDown(self):
        self.db.close()

    def row(self, code):
        return dict(self.db.execute('SELECT * FROM v_colonia_conapo_contexto WHERE cve_col=?', (code,)).fetchone())

    def test_complete_support_uses_proxy_population_not_polygon_population(self):
        row = self.row(1)
        self.assertEqual((row['pob_total'], row['pob_sacmex']), (9999, 300))
        self.assertEqual((row['colonias_sacmex'], row['colonias_con_pob'], row['colonias_con_dom']), (2, 2, 2))
        self.assertEqual(row['litros_hab_dia_dom'], .6)
        self.assertEqual(row['falta_por_mil_hab'], 30.)
        self.assertEqual(row['fugas_por_mil_hab'], 50.)

    def test_partial_population_suppresses_all_rates(self):
        row = self.row(2)
        self.assertEqual((row['colonias_sacmex'], row['colonias_con_pob'], row['pob_sacmex']), (2, 1, 100))
        self.assertEqual(row['consumo_dom_m3'], 30.)
        self.assertTrue(all(row[field] is None for field in ('litros_hab_dia_dom','falta_por_mil_hab','fugas_por_mil_hab')))

    def test_partial_billing_suppresses_only_billing_rate(self):
        row = self.row(3)
        self.assertEqual(row['colonias_con_dom'], 1)
        self.assertIsNone(row['litros_hab_dia_dom'])
        self.assertEqual(row['falta_por_mil_hab'], 30.)
        self.assertEqual(row['fugas_por_mil_hab'], 50.)

    def test_unmatched_and_all_null_billing_stay_null(self):
        self.assertIsNone(self.row(4)['pob_sacmex'])
        self.assertIsNone(self.row(4)['falta_por_mil_hab'])
        self.assertIsNone(self.row(5)['consumo_dom_m3'])
        self.assertIsNone(self.row(5)['litros_hab_dia_dom'])

    def test_known_zero_billing_is_not_missing(self):
        row = self.row(6)
        self.assertEqual(row['colonias_con_dom'], 2)
        self.assertEqual(row['consumo_dom_m3'], 0.)
        self.assertEqual(row['litros_hab_dia_dom'], 0.)


class PolygonTieTests(unittest.TestCase):
    def test_overlapping_candidates_with_unequal_votes_are_not_ties(self):
        votes=pd.DataFrame({'id_ubicacion':[1,1,2,2], 'cve_col':[10,20,30,40], 'n':[8,5,5,5]})
        totals=pd.Series({1:10,2:10})
        ties=candidatos_empatados(votes,totals)
        self.assertEqual(set(ties.id_ubicacion),{2})
        self.assertEqual(dict(zip(elegir_por_puntos(votes,totals).id_ubicacion,elegir_por_puntos(votes,totals).cve_col)),{1:10,2:30})

    def test_tied_choice_is_invariant_to_row_order_and_surrogate_ids(self):
        votes=pd.DataFrame({'id_ubicacion':[9,9,2,2,7], 'cve_col':[90,80,70,60,50], 'n':[2,2,3,1,1]})
        totals=pd.Series({9:4,2:4,7:3})
        expected={2:70,9:80}  # unit 7 never reaches half; unit 2 has a clear winner
        for seed in range(8):
            chosen=elegir_por_puntos(votes.sample(frac=1,random_state=seed),totals)
            self.assertEqual(dict(zip(chosen.id_ubicacion,chosen.cve_col)),expected)
        remap={9:1,2:200,7:30}
        moved=votes.copy()
        moved['id_ubicacion']=moved.id_ubicacion.map(remap)
        moved_totals=pd.Series({remap[k]:v for k,v in totals.items()})
        selected=elegir_por_puntos(moved,moved_totals)
        self.assertEqual(dict(zip(selected.id_ubicacion,selected.cve_col)),{200:70,1:80})


if __name__ == '__main__':
    unittest.main()
