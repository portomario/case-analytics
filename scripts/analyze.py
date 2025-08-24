# -*- coding: utf-8 -*-
"""
Analyze turnover metrics, generate charts and Excel tables.

We intentionally compute BOTH:
- Rotatividade (Turnover “ampliado”\): \(\(Hires \+ Separations\) / 2\) / Total Employees
- Taxa de Desligamento (Termination Rate): Separations / Avg Headcount
Plus breakdowns: Voluntary and Involuntary.

Why both? Many orgs (e.g., ABRH em algumas referências) usam "turnover" como (admissões + desligamentos),
enquanto outras tratam "turnover" como sinônimo de desligamento. Para eliminar ambiguidade,
apresentamos os dois KPIs – e explicamos os nomes em todos gráficos e documentos.
"""
import argparse
from pathlib import Path
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ====== Helpers ======

def headcount_avg(series_total: pd.Series) -> pd.Series:
    """
    Headcount médio de t = média entre total_{t-1} e total_t.
    Para o primeiro mês, usa o próprio total (não há mês anterior).
    """
    prev = series_total.shift(1)
    hc_avg = (prev + series_total) / 2.0
    hc_avg.iloc[0] = series_total.iloc[0]
    return hc_avg

def moving_avg(series: pd.Series, window: int = 3) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()

def zscore(series: pd.Series) -> pd.Series:
    mu = series.mean()
    sd = series.std(ddof=1)
    return (series - mu) / (sd if sd != 0 else 1.0)

def pct(a, b):
    return (a / b) * 100.0

# ====== Core calc ======

def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d = d.sort_values("date").reset_index(drop=True)
    d["hc_avg"] = headcount_avg(d["total_employees"])

    # KPIs
    d["turnover_rotatividade_pct"] = pct((d["hires"] + d["separations"]) / 2.0, d["hc_avg"])
    d["desligamento_pct"] = pct(d["separations"], d["hc_avg"])  # "taxa de desligamento"
    d["voluntario_pct"] = pct(d["voluntary"], d["hc_avg"])
    d["involuntario_pct"] = pct(d["involuntary"], d["hc_avg"])

    # Smooth
    d["desligamento_ma3"] = moving_avg(d["desligamento_pct"], 3)
    d["turnover_ma3"] = moving_avg(d["turnover_rotatividade_pct"], 3)

    # Seasonality (month index)
    d["month"] = pd.to_datetime(d["date"]).dt.month

    # z-score for anomaly detection (on desligamento_pct, as it's most commonly used)
    d["z_desligamento"] = zscore(d["desligamento_pct"])

    return d

def describe_series(series: pd.Series) -> pd.Series:
    desc = series.describe()
    cv = (series.std(ddof=1) / series.mean()) if series.mean() != 0 else np.nan
    out = pd.Series({
        "mean": desc["mean"],
        "median": series.median(),
        "std": desc["std"],
        "cv": cv,
        "min": desc["min"],
        "max": desc["max"],
        "count": desc["count"],
    })
    return out

def ensure_outdir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def line_chart(x, y, title, ylabel, outpath: Path):
    plt.figure()
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel("Mês")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def bar_chart(x, y, title, ylabel, outpath: Path):
    plt.figure()
    plt.bar(x, y)
    plt.title(title)
    plt.xlabel("Mês")
    plt.ylabel(ylabel)
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def seasonality_chart(df: pd.DataFrame, col: str, outpath: Path):
    # average by month across years
    pivot = df.groupby("month")[col].mean().reindex(range(1,13))
    plt.figure()
    plt.bar(pivot.index, pivot.values)
    plt.title(f"Sazonalidade média por mês – {col}")
    plt.xlabel("Mês (1–12)")
    plt.ylabel("%")
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def to_excel_tables(df: pd.DataFrame, outpath: Path):
    with pd.ExcelWriter(outpath, engine="xlsxwriter") as xw:
        df.to_excel(xw, index=False, sheet_name="Mensal")
        # Descriptive stats
        stats = pd.DataFrame({
            "KPI": ["Turnover (rotatividade)", "Taxa de desligamento", "Voluntário", "Involuntário"],
            "mean": [
                df["turnover_rotatividade_pct"].mean(),
                df["desligamento_pct"].mean(),
                df["voluntario_pct"].mean(),
                df["involuntario_pct"].mean(),
            ],
            "median": [
                df["turnover_rotatividade_pct"].median(),
                df["desligamento_pct"].median(),
                df["voluntario_pct"].median(),
                df["involuntario_pct"].median(),
            ],
            "std": [
                df["turnover_rotatividade_pct"].std(ddof=1),
                df["desligamento_pct"].std(ddof=1),
                df["voluntario_pct"].std(ddof=1),
                df["involuntario_pct"].std(ddof=1),
            ],
        })
        stats["cv"] = stats["std"] / stats["mean"]
        stats.to_excel(xw, index=False, sheet_name="Estatísticas")
        # Yearly summary
        df["year"] = pd.to_datetime(df["date"]).dt.year
        yearly = df.groupby("year")[["turnover_rotatividade_pct","desligamento_pct","voluntario_pct","involuntario_pct"]].mean().reset_index()
        yearly.to_excel(xw, index=False, sheet_name="Resumo Anual")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV path")
    ap.add_argument("--outdir", required=True, help="Output directory")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    ensure_outdir(outdir)

    df = pd.read_csv(args.input, parse_dates=["date"])
    metrics = compute_metrics(df)

    # Save enriched CSV
    metrics.to_csv(outdir / "metrics_enriched.csv", index=False)

    # Excel tables
    to_excel_tables(metrics, outdir / "people-analytics-turnover.xlsx")

    # Charts
    # 1) Taxa de desligamento (principal série, comum em benchmarks)
    line_chart(metrics["date"], metrics["desligamento_pct"],
               "Taxa de Desligamento Mensal (%)", "%", outdir / "taxa_desligamento.png")

    # 2) Turnover (rotatividade ampliada)
    line_chart(metrics["date"], metrics["turnover_rotatividade_pct"],
               "Turnover (Rotatividade) Mensal (%)", "%", outdir / "turnover_rotatividade.png")

    # 3) Voluntário e 4) Involuntário
    line_chart(metrics["date"], metrics["voluntario_pct"],
               "Turnover Voluntário Mensal (%)", "%", outdir / "turnover_voluntario.png")
    line_chart(metrics["date"], metrics["involuntario_pct"],
               "Turnover Involuntário Mensal (%)", "%", outdir / "turnover_involuntario.png")

    # 5) Sazonalidade (usando Taxa de Desligamento como base)
    seasonality_chart(metrics, "desligamento_pct", outdir / "seasonality_desligamento.png")

    # 6) Média móvel para leitura de tendência
    line_chart(metrics["date"], metrics["desligamento_ma3"],
               "Taxa de Desligamento – Média Móvel 3M (%)", "%", outdir / "desligamento_ma3.png")
    line_chart(metrics["date"], metrics["turnover_ma3"],
               "Turnover (Rotatividade) – Média Móvel 3M (%)", "%", outdir / "turnover_ma3.png")

    # 7) Exportar anomalias simples (|z|>=2)
    anomalies = metrics.loc[metrics["z_desligamento"].abs() >= 2, ["date","desligamento_pct","z_desligamento"]]
    anomalies.to_csv(outdir / "anomalias_desligamento.csv", index=False)

if __name__ == "__main__":
    main()
