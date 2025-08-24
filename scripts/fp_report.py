# -*- coding: utf-8 -*-
""" FP report with XML + stats """
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

def confusion_at_threshold(y_true, y_score, thr):
    y_pred = (y_score >= thr).astype(int)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    tn = int(((y_pred == 0) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2*precision*recall)/(precision+recall) if (precision+recall) else 0.0
    return {"threshold": float(thr), "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": precision, "recall": recall, "f1": f1}

def pick_thresholds(y_true, y_score, k_top=0.05):
    grid = np.linspace(0.01, 0.99, 99)
    rows = []
    for thr in grid:
        rows.append(confusion_at_threshold(y_true, y_score, thr))
    df_grid = pd.DataFrame(rows)
    best = df_grid.sort_values(["f1","precision","recall"], ascending=False).iloc[0].to_dict()

    n = max(1, int(len(y_score) * k_top))
    order = np.argsort(-y_score)  # desc
    thr_topk = float(y_score[order[n-1]])
    topk = confusion_at_threshold(y_true, y_score, thr_topk)
    return best, topk, df_grid

def describe(series):
    series = pd.Series(series)
    mean = float(series.mean())
    median = float(series.median())
    std = float(series.std(ddof=1)) if series.size > 1 else 0.0
    cv = float(std/mean) if mean != 0 else float('nan')
    return {"mean": mean, "median": median, "std": std, "cv": cv}

def to_junit_xml(path: Path, suite_name: str, metrics: dict, extra_note: str = ""):
    sysout = (
        f"Threshold usado: {metrics['strategy']}={metrics['threshold']}\n"
        f"TP={metrics['tp']} FP={metrics['fp']} TN={metrics['tn']} FN={metrics['fn']}\n"
        f"Precision={metrics['precision']:.4f}  Recall={metrics['recall']:.4f}  F1={metrics['f1']:.4f}\n"
        f"{extra_note}\n"
    )
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="{suite_name}" tests="3" failures="0">
  <testcase classname="ml.eval" name="precision">
    <system-out>{metrics['precision']:.6f}</system-out>
  </testcase>
  <testcase classname="ml.eval" name="recall">
    <system-out>{metrics['recall']:.6f}</system-out>
  </testcase>
  <testcase classname="ml.eval" name="f1">
    <system-out>{metrics['f1']:.6f}</system-out>
  </testcase>
  <system-out><![CDATA[
{sysout}
  ]]></system-out>
</testsuite>
'''
    path.write_text(xml, encoding="utf-8")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--k_top", type=float, default=0.05)
    ap.add_argument("--strategy", choices=["best_f1", "topk"], default="best_f1")
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.preds)
    if not {"id","y_true","y_score"}.issubset(df.columns):
        raise ValueError("CSV deve conter colunas: id,y_true,y_score")

    y_true = df["y_true"].astype(int).values
    y_score = df["y_score"].astype(float).values

    best, topk, df_grid = pick_thresholds(y_true, y_score, k_top=args.k_top)
    chosen = best if args.strategy == "best_f1" else topk
    chosen["strategy"] = "best_f1" if args.strategy == "best_f1" else f"topk@{args.k_top:.2f}"

    stats_all = describe(y_score)
    y_pred = (y_score >= chosen["threshold"]).astype(int)
    stats_predpos = describe(y_score[y_pred == 1]) if (y_pred == 1).any() else {"mean":0.0,"median":0.0,"std":0.0,"cv":float("nan")}

    pd.DataFrame([
        {"group":"scores_all", **stats_all},
        {"group":"scores_predicted_positive", **stats_predpos}
    ]).to_csv(outdir / "fp_stats.csv", index=False)

    note = (
        f"SCORES — ALL: mean={stats_all['mean']:.4f}, median={stats_all['median']:.4f}, std={stats_all['std']:.4f}, cv={stats_all['cv']:.4f}\n"
        f"SCORES — PRED_POS: mean={stats_predpos['mean']:.4f}, median={stats_predpos['median']:.4f}, std={stats_predpos['std']:.4f}, cv={stats_predpos['cv']:.4f}"
    )

    to_junit_xml(outdir / "ml_evaluation.xml", "ML_Evaluation", chosen, extra_note=note)

    pd.DataFrame([{
        "threshold": chosen["threshold"],
        "tp": chosen["tp"], "fp": chosen["fp"], "tn": chosen["tn"], "fn": chosen["fn"],
        "precision": chosen["precision"], "recall": chosen["recall"], "f1": chosen["f1"],
        "strategy": chosen["strategy"]
    }]).to_csv(outdir / "confusion_matrix.csv", index=False)
    df_grid.to_csv(outdir / "metrics_by_threshold.csv", index=False)
    (outdir / "metrics_summary.json").write_text(json.dumps({
        "strategy": chosen["strategy"],
        "threshold": chosen["threshold"],
        "tp": chosen["tp"], "fp": chosen["fp"], "tn": chosen["tn"], "fn": chosen["fn"],
        "precision": chosen["precision"], "recall": chosen["recall"], "f1": chosen["f1"]
    }, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
