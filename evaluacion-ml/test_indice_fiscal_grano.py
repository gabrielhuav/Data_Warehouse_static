"""Check that fiscal-index grain and record means keep missing values missing."""
from pathlib import Path
import tempfile
import unittest

from indice_fiscal_grano import calculate


class FiscalGrainTests(unittest.TestCase):
    def test_mixed_indices_and_field_specific_null_denominators(self):
        csv = ('alcaldia,colonia,indice_des,consumo_total,consumo_prom\n'
               'A,C,ALTO,10,NA\nA,C,BAJO,NA,4\nA,C,ALTO,30,2\n'
               'A,D,ALTO,,6\nNA,C,BAJO,100,100\nA,,BAJO,100,100\n')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.csv'
            path.write_text(csv, encoding='utf-8')
            result = calculate(path)
        self.assertEqual(result['retained_records'], 4)
        self.assertEqual(result['excluded_missing_territory'], 2)
        self.assertEqual(result['territorial_pairs'], 2)
        self.assertEqual(result['pairs_with_multiple_indices'], 1)
        alto = result['per_record_mean_by_index']['ALTO']
        bajo = result['per_record_mean_by_index']['BAJO']
        self.assertEqual((alto['n'], alto['consumo_total_valid_n'], alto['consumo_total_mean']), (3, 2, 20))
        self.assertEqual((alto['consumo_prom_valid_n'], alto['consumo_prom_mean']), (2, 4))
        self.assertIsNone(bajo['consumo_total_mean'])
        self.assertEqual(bajo['consumo_total_valid_n'], 0)


if __name__ == '__main__':
    unittest.main()
