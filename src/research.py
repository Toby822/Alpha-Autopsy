"""Alpha Autopsy: a small but auditable, chronology-first signal-selection experiment.

The app intentionally tests *fragility*, not whether a backtest should be traded.
Daily price observations are historical third-party mirrored Binance Futures closes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'data' / 'btcusdt_2024_2025_daily_close.csv'
REPORT_PATH = ROOT / 'research' / 'results.json'
LOOKBACKS = (2, 5, 10, 20, 40)
FAMILIES = ('momentum', 'reversal')
CANDIDATES = tuple(f'{f}-{n}' for f in FAMILIES for n in LOOKBACKS)
COST_BPS = 10.0  # 10 basis points per unit of position change, including crossings
BARS_PER_YEAR = 365  # BTC futures reference data, not an equity market calendar
TRAIN_END = '2024-12-31'
VALIDATION_END = '2025-06-30'
BOOT_SEED = 72941


def read_data(path=DATA_PATH):
    df = pd.read_csv(path, parse_dates=['date']).sort_values('date').reset_index(drop=True)
    if df['date'].duplicated().any():
        raise ValueError('Duplicate trading dates')
    if df.isna().any().any() or not np.isfinite(df.close_usdt).all() or (df.close_usdt <= 0).any():
        raise ValueError('Missing, infinite or nonpositive price data')
    steps = df.date.diff().dropna()
    if not steps.eq(pd.Timedelta(days=1)).all():
        raise ValueError('Non-daily gaps found — do not silently fill missing observations')
    if len(df) != 731 or str(df.date.iloc[0].date()) != '2024-01-01' or str(df.date.iloc[-1].date()) != '2025-12-31':
        raise ValueError('Unexpected historical data window')
    return df


def phase(dates):
    return np.where(dates <= np.datetime64(TRAIN_END), 'TRAIN',
                    np.where(dates <= np.datetime64(VALIDATION_END), 'VALIDATE', 'TEST'))


def positions(prices, family, lookback):
    """Position during interval (t-1,t] only sees closes through t-1."""
    p = np.asarray(prices, dtype=float)
    position = np.zeros(len(p), dtype=float)
    for t in range(lookback + 1, len(p)):
        sign = np.sign(p[t-1] / p[t-1-lookback] - 1)
        position[t] = sign if family == 'momentum' else -sign
    return position


def paths(prices, family, lookback, cost_bps=COST_BPS):
    price = np.asarray(prices, dtype=float)
    pos = positions(price, family, lookback)
    underlying = np.zeros(len(price))
    underlying[1:] = price[1:] / price[:-1] - 1
    turnover = np.abs(np.diff(pos, prepend=0))
    gross = pos * underlying
    cost = turnover * cost_bps / 1e4
    net = gross - cost
    return {'pos':pos,'underlying':underlying,'turnover':turnover,'gross':gross,'cost':cost,'net':net}


def stats(r, turnover=None):
    x=np.asarray(r,dtype=float)
    if not len(x):
        raise ValueError('Empty sample')
    equity = np.cumprod(1+x)
    drawdown = np.min(equity / np.maximum.accumulate(np.maximum.accumulate(np.r_[1,equity]))[1:] - 1)
    mu=float(np.mean(x)); sd=float(np.std(x,ddof=1)) if len(x)>1 else 0.
    sharpe=float(np.sqrt(BARS_PER_YEAR) * mu/sd) if sd>1e-14 else 0.
    return {'n':len(x),'return':float(equity[-1]-1),'sharpe':sharpe,
            'mean_bps':mu*1e4,'annualised_vol':sd*np.sqrt(BARS_PER_YEAR),
            'max_drawdown':float(drawdown),'hit_rate':float(np.mean(x>0)),
            'trades':float(np.sum(turnover)) if turnover is not None else 0.}


def circular_shift_pvalue(signal, returns, turnover, cost_bps=COST_BPS):
    """Diagnostic circular-shift placebo; NOT a fully valid trading p-value.

    Finite shifts retain underlying return order, but break the actual signal alignment.
    Fees are deterministic on the precomputed position changes.
    """
    p=np.asarray(signal,float); r=np.asarray(returns,float); t=np.asarray(turnover,float)
    obs=float(np.mean(p*r-t*cost_bps/1e4))
    null=[float(np.mean(p*np.roll(r,k)-t*cost_bps/1e4)) for k in range(1,len(r))]
    count=sum(x>=obs-1e-15 for x in null)
    return {'observed_bps':obs*1e4,'one_sided_p':(count+1)/len(r),
            'null_bps':[round(x*1e4,6) for x in null], 'shifts':len(null)}


def block_bootstrap_mean_ci(r, seed=BOOT_SEED, block=7, draws=1000):
    """Circular moving-block bootstrap of arithmetic daily mean; not a return-CI."""
    x=np.asarray(r,float); n=len(x)
    rng=np.random.default_rng(seed)
    k=int(np.ceil(n/block))
    starts=rng.integers(0,n,size=(draws,k))
    offsets=np.arange(block)
    indices=((starts[:,:,None]+offsets[None,None,:])%n).reshape(draws,-1)[:,:n]
    boot=x[indices].mean(axis=1)*1e4
    return [float(np.quantile(boot,.025)),float(np.quantile(boot,.975))]


def study(cost_bps=COST_BPS, data_path=DATA_PATH):
    df=read_data(data_path)
    dates=df.date.to_numpy(dtype='datetime64[D]')
    groups=phase(dates)
    price=df.close_usdt.to_numpy(float)
    records=[];track={}
    for family in FAMILIES:
        for lookback in LOOKBACKS:
            key=f'{family}-{lookback}'
            p=paths(price,family,lookback,cost_bps)
            track[key]=p
            rows={'id':key,'family':family,'lookback':lookback}
            for part in ['TRAIN','VALIDATE','TEST']:
                mask=groups==part
                rows[part.lower()]=stats(p['net'][mask],p['turnover'][mask])
            records.append(rows)
    # The train-only selection rule is frozen before examining other phases.
    ranking=sorted(records,key=lambda r:(-r['train']['sharpe'],r['id']))
    winner=ranking[0]['id']
    best=track[winner]
    test=groups=='TEST'
    test_turn=best['turnover'][test];test_pos=best['pos'][test];test_market=best['underlying'][test]
    reference=circular_shift_pvalue(test_pos,test_market,test_turn,cost_bps)
    ci=block_bootstrap_mean_ci(best['net'][test])
    # One static artifact for the deployed app; JSON includes the frozen selection rule.
    dataset={'instrument':'BTC/USDT (Binance USD-M futures mirrored data)',
             'resolution':'UTC daily close sampled from third-party hourly records',
             'source':'https://github.com/SubhayanBiswas/Binance-Vision-Sample-Data',
             'source_git_blob_sha1':'629859ca96ea5e13816c10ce74bdd48e01ba93dd',
             'start':'2024-01-01','end':'2025-12-31','observations':len(df),
             'fee_schedule_note':'Illustrative fixed fee + slippage per unit position turnover; no funding, bid/ask data or execution simulation.'}
    output={'schema':2,'label':'frozen training-only model-selection experiment',
            'dataset':dataset,'rule':'Five lookbacks × momentum/reversal = 10 candidates; rank by training Sharpe only; validation diagnostic; holdout unseen during choice.',
            'cost_bps':cost_bps,'train_end':TRAIN_END,'validation_end':VALIDATION_END,
            'chosen':winner,'candidates':ranking,
            'daily':{'date':df.date.dt.strftime('%Y-%m-%d').tolist(),
                    'close':[round(float(x),1) for x in price],
                    'phase':groups.tolist(),
                    'market_return':np.round(best['underlying'],10).tolist(),
                    'position':best['pos'].astype(int).tolist(),
                    'turnover':best['turnover'].astype(int).tolist(),
                    'strategy_gross':np.round(best['gross'],10).tolist()},
            'holdout_bootstrap_mean_bps_ci_95':ci,
            'holdout_shift_placebo':reference,
            'cautions':['No training data from outside 2024 is used to select the winner.',
                        'Validation and holdout are displayed, but never used to pick the headline champion.',
                        'If you inspect the holdout and then redesign the model, it is no longer a pristine holdout.',
                        'The position rule is not a calibrated executable order strategy; overnight/funding effects absent.',
                        'Circular-shift placebo tests signal alignment, not a formal significance guarantee.',
                        'Bootstrap confidence interval describes the *daily sample mean*, not a probability of profits.']}
    return output


def main():
    a=argparse.ArgumentParser(description='Chronological, auditable signal research')
    a.add_argument('--data',type=Path,default=DATA_PATH)
    a.add_argument('--output',type=Path,default=REPORT_PATH)
    a.add_argument('--cost-bps',type=float,default=COST_BPS)
    args=a.parse_args()
    if not 0<=args.cost_bps<=100:
        raise SystemExit('cost-bps must be in [0,100]')
    result=study(cost_bps=args.cost_bps,data_path=args.data)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print('Written:',args.output)
    print('Training-only winner:',result['chosen'])
    for item in result['candidates'][:3]:
        print(item['id'],'TRAIN:',round(item['train']['sharpe'],3),
              'VALID:',round(item['validate']['sharpe'],3),'TEST:',round(item['test']['sharpe'],3))
    print('Test circular-shift placebo p:',result['holdout_shift_placebo']['one_sided_p'])

if __name__=='__main__':main()