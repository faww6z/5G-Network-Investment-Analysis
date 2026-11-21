"""Run with python -m unittest discover -s tests -v."""
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"analysis"))
from finance import evaluate,load_assumptions,payback,find_threshold


class FinanceTests(unittest.TestCase):
    def setUp(self): self.a=load_assumptions()
    def test_year_zero_and_npv_timing(self):
        r=evaluate(self.a,expanded=False);f=r["forecast"]
        self.assertEqual(f.iloc[0].fcf,-50e6)
        self.assertAlmostEqual(r["metrics"]["npv"],sum(v/(1.1**t) for t,v in enumerate(f.fcf)),places=6)
        self.assertAlmostEqual(f.iloc[1].revenue,19.5e6)
    def test_average_opening_closing_and_gross_flow(self):
        f=evaluate(self.a)["forecast"]
        for i in range(1,6):
            row=f.iloc[i]
            self.assertAlmostEqual((row.opening_customers+row.closing_customers)/2,row.average_customers)
            self.assertAlmostEqual(row.opening_customers+row.gross_additions-row.cancellations,row.closing_customers)
            if i>1:self.assertAlmostEqual(row.opening_customers,f.iloc[i-1].closing_customers)
    def test_churn_not_subtracted_twice(self):
        r=evaluate(self.a);stress=evaluate(dict(self.a,annual_churn=.20))
        np.testing.assert_allclose(r["forecast"].average_customers,stress["forecast"].average_customers)
        self.assertGreater(stress["forecast"].acquisition_cost.sum(),r["forecast"].acquisition_cost.sum())
        self.assertLess(stress["metrics"]["npv"],r["metrics"]["npv"])
    def test_nol_no_immediate_refund(self):
        f=evaluate(dict(self.a,initial_opex=30e6))["forecast"]
        self.assertTrue((f.cash_tax==0).all())
        self.assertTrue((f.closing_nol>=0).all())
    def test_depreciation_is_noncash(self):
        f=evaluate(dict(self.a,tax_rate=0))["forecast"].iloc[1:]
        np.testing.assert_allclose(f.fcf,f.ebit+f.depreciation-f.delta_nwc-f.capex)
    def test_no_invented_payback_or_irr(self):
        r=evaluate(dict(self.a,arpu=0))
        self.assertIsNone(r["metrics"]["irr"])
        self.assertIsNone(r["metrics"]["payback"])
        self.assertIsNone(payback(np.array([-100.,20.,20.])))
    def test_break_even_bracket_and_capacity(self):
        x=find_threshold(self.a,"arpu",20,150)
        self.assertLess(abs(evaluate(dict(self.a,arpu=x))["metrics"]["npv"]),.01)
        self.assertIsNone(find_threshold(self.a,"incremental_share",.1,1))
        self.assertGreater(evaluate(self.a,self.a["bull_growth"])["metrics"]["year5_capacity_utilization"],1)
    def test_residual_discounting(self):
        original=evaluate(self.a)["metrics"]["npv"]
        revised=evaluate(dict(self.a,terminal_cash=10e6))["metrics"]["npv"]
        self.assertAlmostEqual(revised-original,10e6/1.1**5,places=6)


if __name__=="__main__":unittest.main()
