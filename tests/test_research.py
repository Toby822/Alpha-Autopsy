import unittest
import json
from pathlib import Path
import numpy as np
from src import research as R

class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df=R.read_data()
        cls.report=R.study()

    def test_provenance_and_coverage(self):
        self.assertEqual(len(self.df),731)
        self.assertEqual(self.df.date.iloc[0].strftime('%Y-%m-%d'),'2024-01-01')
        self.assertEqual(self.df.date.iloc[-1].strftime('%Y-%m-%d'),'2025-12-31')
        self.assertAlmostEqual(self.df.close_usdt.iloc[0],44230.2)
        self.assertAlmostEqual(self.df.close_usdt.iloc[-1],87608.2)

    def test_frozen_train_only_winner(self):
        r=self.report
        self.assertEqual(r['chosen'],'momentum-2')
        self.assertEqual(len(r['candidates']),10)
        self.assertEqual(len([x for x in r['daily']['phase'] if x=='TRAIN']),366)
        self.assertEqual(len([x for x in r['daily']['phase'] if x=='VALIDATE']),181)
        self.assertEqual(len([x for x in r['daily']['phase'] if x=='TEST']),184)
        self.assertGreaterEqual(r['candidates'][0]['train']['sharpe'],r['candidates'][1]['train']['sharpe'])

    def test_no_lookahead_positions(self):
        p=self.df.close_usdt.to_numpy(float)
        first=R.positions(p,'momentum',5)
        future=p.copy();future[310:]=future[310:]*1.13
        second=R.positions(future,'momentum',5)
        np.testing.assert_array_equal(first[:310],second[:310])
        self.assertTrue(np.all(first[:6]==0))

    def test_fee_turnover_and_signs(self):
        p=np.array([100,101,104,102,99,98,100,110,97],float)
        x=R.paths(p,'momentum',2,10)
        y=R.paths(p,'momentum',2,20)
        np.testing.assert_allclose(x['gross'],y['gross'])
        np.testing.assert_allclose(x['net']-y['net'],x['turnover']*10/1e4)
        self.assertTrue(set(x['pos']).issubset({-1.,0.,1.}))
        self.assertTrue(np.any(x['turnover']==2))

    def test_statistical_reproducibility(self):
        a=R.study();b=R.study()
        self.assertEqual(a['chosen'],b['chosen'])
        self.assertEqual(a['holdout_bootstrap_mean_bps_ci_95'],b['holdout_bootstrap_mean_bps_ci_95'])
        self.assertEqual(a['holdout_shift_placebo'],b['holdout_shift_placebo'])
        self.assertGreater(a['holdout_shift_placebo']['one_sided_p'],0)
        self.assertLessEqual(a['holdout_shift_placebo']['one_sided_p'],1)

    def test_saved_artifact_exactly_reproducible(self):
        on_disk=json.loads(R.REPORT_PATH.read_text())
        expected=self.report
        self.assertEqual(expected,on_disk,'Run python -m src.research to refresh generated artifact')

if __name__=='__main__':unittest.main()