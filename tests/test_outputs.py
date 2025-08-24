# -*- coding: utf-8 -*-
from pathlib import Path
import csv, json

def test_outputs_exist():
    base = Path(__file__).resolve().parent.parent
    out = base / "output"
    must = [
        "taxa_desligamento.png",
        "turnover_rotatividade.png",
        "turnover_voluntario.png",
        "turnover_involuntario.png",
        "desligamento_ma3.png",
        "turnover_ma3.png",
        "seasonality_desligamento.png",
        "metrics_enriched.csv",
        "turnover_stats.csv",
        "ml_evaluation.xml",
        "confusion_matrix.csv",
        "metrics_by_threshold.csv",
        "metrics_summary.json",
        "fp_stats.csv",
    ]
    missing = [m for m in must if not (out / m).exists()]
    assert not missing, f"Arquivos faltando em output/: {missing}"
