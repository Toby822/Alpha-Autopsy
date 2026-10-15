"""Reproduce the bundled daily closes from the named upstream hourly CSV.

This is a separate, opt-in data refresh command: it never fetches live prices on app load.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timedelta
import hashlib
from io import StringIO
from pathlib import Path
from urllib.request import urlopen

URL='https://raw.githubusercontent.com/SubhayanBiswas/Binance-Vision-Sample-Data/main/BTCUSDT_1h_Cleaned.csv'
EXPECTED_BLOB='629859ca96ea5e13816c10ce74bdd48e01ba93dd'
ROOT=Path(__file__).resolve().parents[1]

def git_blob_sha(data:bytes):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def extract(raw:bytes):
    reader=csv.DictReader(StringIO(raw.decode('utf-8-sig')))
    prices=[];previous=None;count=0
    for row in reader:
        stamp=datetime.strptime(row['Date'],'%d-%m-%Y %H:%M')
        if previous is not None and stamp-previous!=timedelta(hours=1):
            raise ValueError(f'Gap or duplicate at {stamp!s}')
        previous=stamp
        for key in ('Open','High','Low','Close','Volume'):
            float(row[key])
        if stamp.hour==23:
            prices.append((stamp.strftime('%Y-%m-%d'),f'{float(row["Close"]):.1f}'))
        count+=1
    if count!=17544 or len(prices)!=731 or prices[0][0]!='2024-01-01' or prices[-1][0]!='2025-12-31':
        raise ValueError('Upstream data did not match expected two-year historical window')
    return prices

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--local',type=Path,help='Read an already downloaded hourly CSV instead of fetching')
    parser.add_argument('--allow-changed-source',action='store_true',help='Explicitly permit upstream bytes not matching pinned Git blob SHA')
    args=parser.parse_args()
    if args.local:
        raw=args.local.read_bytes()
    else:
        with urlopen(URL,timeout=25) as response:raw=response.read()
    actual=git_blob_sha(raw)
    if actual!=EXPECTED_BLOB and not args.allow_changed_source:
        raise SystemExit(f'Unexpected upstream version {actual}, expected {EXPECTED_BLOB}. Aborted without altering data.')
    data=extract(raw)
    target=ROOT/'data'/'btcusdt_2024_2025_daily_close.csv'
    with target.open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['date','close_usdt']);writer.writerows(data)
    print(f'Wrote {len(data)} observed daily prices to {target}. Original Git blob: {actual}.')
    print('Run python -m src.research to regenerate the historical analysis JSON.')
if __name__=='__main__':main()