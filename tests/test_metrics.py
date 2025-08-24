# -*- coding: utf-8 -*-
import math
from pathlib import Path
import pandas as pd

from scripts.analyze import compute_metrics

DATA = Path(__file__).resolve().parents[1] / "data" / "turnover_monthly.csv"

def test_headcount_avg_first_month():
    df = pd.read_csv(DATA, parse_dates=["date"])
    m = compute_metrics(df)
    # Jan/2021 total = 1920; hc_avg for first month equals itself
    assert abs(m.loc[0, "hc_avg"] - 1920.0) < 1e-6

def test_oct_2021_desligamento_rate():
    df = pd.read_csv(DATA, parse_dates=["date"])
    m = compute_metrics(df)
    # Oct/2021 index = 9 (0-based). total(t)=1940, total(t-1)=1971 => hc_avg=1955.5; sep=124
    # desligamento_pct = 124 / 1955.5 * 100 = ~6.341%
    val = m.loc[9, "desligamento_pct"]
    assert abs(val - (124/1955.5*100)) < 1e-3

def test_turnover_rotatividade_definition():
    df = pd.read_csv(DATA, parse_dates=["date"])
    m = compute_metrics(df)
    # Check new turnover definition: ((hires + separations)/2) / total_employees * 100 for one month
    i = 4  # May/2021
    hires = 72; sep = 76
    total = df.loc[i, "total_employees"]
    expected = ((hires + sep) / 2.0) / total * 100.0
    assert abs(m.loc[i, "turnover_rotatividade_pct"] - expected) < 1e-6
