# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def moving_avg(s, w=3):
    return s.rolling(window=w, min_periods=1).mean()

def compute(df):
    df = df.sort_values("date").copy()
    df["hc_prev"] = df["total_employees"].shift(1)
    df["hc_avg"] = (df["hc_prev"] + df["total_employees"]) / 2.0
    df.loc[df["hc_avg"].isna(), "hc_avg"] = df["total_employees"]
    # KPIs
    df["turnover_rotatividade_pct"] = ((df["hires"] + df["separations"]) / 2.0) / df["total_employees"] * 100.0
    df["desligamento_pct"] = df["separations"] / df["hc_avg"] * 100.0
    df["voluntario_pct"] = df["voluntary"] / df["hc_avg"] * 100.0
    df["involuntario_pct"] = df["involuntary"] / df["hc_avg"] * 100.0
    # MM3
    df["desligamento_pct_ma3"] = moving_avg(df["desligamento_pct"], 3)
    df["turnover_rotatividade_pct_ma3"] = moving_avg(df["turnover_rotatividade_pct"], 3)
    return df

def stats(series):
    s = series.dropna()
    mean = s.mean(); median = s.median(); std = s.std(ddof=1)
    cv = (std/mean) if mean != 0 else np.nan
    return mean, median, std, cv

def plot(df, outdir: Path):
    import matplotlib.pyplot as plt
    # desligamento
    plt.figure(); plt.plot(df["date"], df["desligamento_pct"]); plt.title("Taxa de desligamento (%)"); plt.xlabel("Data"); plt.ylabel("%"); plt.tight_layout(); plt.savefig(outdir / "taxa_desligamento.png"); plt.close()
    # turnover
    plt.figure(); plt.plot(df["date"], df["turnover_rotatividade_pct"]); plt.title("Turnover (rotatividade) (%)"); plt.xlabel("Data"); plt.ylabel("%"); plt.tight_layout(); plt.savefig(outdir / "turnover_rotatividade.png"); plt.close()
    # voluntário
    plt.figure(); plt.plot(df["date"], df["voluntario_pct"]); plt.title("Turnover voluntário (%)"); plt.xlabel("Data"); plt.ylabel("%"); plt.tight_layout(); plt.savefig(outdir / "turnover_voluntario.png"); plt.close()
    # involuntário
    plt.figure(); plt.plot(df["date"], df["involuntario_pct"]); plt.title("Turnover involuntário (%)"); plt.xlabel("Data"); plt.ylabel("%"); plt.tight_layout(); plt.savefig(outdir / "turnover_involuntario.png"); plt.close()
    # sazonalidade (boxplot por mês)
    month = df["date"].dt.month
    plt.figure(); plt.boxplot([df.loc[month==m, "desligamento_pct"].values for m in range(1,13)], positions=range(1,13), widths=0.6, showmeans=True); plt.title("Sazonalidade — desligamento (%) por mês"); plt.xlabel("Mês"); plt.ylabel("%"); plt.tight_layout(); plt.savefig(outdir / "seasonality_desligamento.png"); plt.close()
    # MM3 — desligamento
    plt.figure(); plt.plot(df["date"], df["desligamento_pct"], alpha=0.6); plt.plot(df["date"], df["desligamento_pct_ma3"]); plt.title("Desligamento (%) — MM3"); plt.xlabel("Data"); plt.ylabel("%"); plt.tight_layout(); plt.savefig(outdir / "desligamento_ma3.png"); plt.close()
    # MM3 — turnover
    plt.figure(); plt.plot(df["date"], df["turnover_rotatividade_pct"], alpha=0.6); plt.plot(df["date"], df["turnover_rotatividade_pct_ma3"]); plt.title("Turnover (%) — MM3"); plt.xlabel("Data"); plt.ylabel("%"); plt.tight_layout(); plt.savefig(outdir / "turnover_ma3.png"); plt.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/turnover_monthly.csv")
    ap.add_argument("--outdir", default="output")
    args = ap.parse_args()

    df = pd.read_csv(args.input, parse_dates=["date"])
    dfm = compute(df)
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    # salvar métricas
    dfm.to_csv(outdir / "metrics_enriched.csv", index=False)

    # stats
    rows = []
    for name, col in [("Turnover (rotatividade)", "turnover_rotatividade_pct"),
                      ("Taxa de desligamento", "desligamento_pct"),
                      ("Voluntário", "voluntario_pct"),
                      ("Involuntário", "involuntario_pct")]:
        mean, median, std, cv = stats(dfm[col])
        rows.append([name, mean, median, std, cv])
    pd.DataFrame(rows, columns=["KPI","mean","median","std","cv"]).to_csv(outdir / "turnover_stats.csv", index=False)

    # charts
    plot(dfm, outdir)

if __name__ == "__main__":
    main()
