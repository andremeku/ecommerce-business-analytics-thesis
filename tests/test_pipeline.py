"""Minimal deterministic smoke test, no Kaggle download needed."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from run_analysis import run

class TestPipeline(unittest.TestCase):
    def test_small_valid_dataset(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            data=pd.DataFrame([
                {'TransactionNo':'101','Date':'12/01/2018','ProductNo':'P1','ProductName':'Tea','Price':5.0,'Quantity':2,'CustomerNo':'123','Country':'United Kingdom'},
                {'TransactionNo':'102','Date':'12/02/2018','ProductNo':'P2','ProductName':'Cup','Price':4.0,'Quantity':3,'CustomerNo':'124','Country':'France'},
                {'TransactionNo':'C102','Date':'12/03/2018','ProductNo':'P2','ProductName':'Cup','Price':4.0,'Quantity':-3,'CustomerNo':'124','Country':'France'}
            ])
            src=base/'input.csv'; data.to_csv(src,index=False)
            result=run(src,base/'exports',base/'figures')
            self.assertEqual(result['rows'],3)
            self.assertEqual(result['clean_sales_lines'],2)
            self.assertEqual(result['transactions'],2)
            self.assertEqual(result['customers'],2)
            self.assertAlmostEqual(result['revenue'],22.0)
            exported=pd.read_csv(base/'exports'/'customer_summary.csv')
            self.assertEqual(sorted(exported['CustomerNo'].tolist()),[1,2])
            self.assertTrue((base/'figures'/'top_products.png').exists())

if __name__=='__main__': unittest.main()
