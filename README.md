# Case Técnico — Coordenador de People Analytics

Este repositório contém o material do case com **código Python testável**, **gráficos** e **relatórios**.  
Turnover calculado por: `[(Admissões + Desligamentos)/2] / Total * 100` (rotatividade) e **taxa de desligamento** separada (desligamentos / HC médio).

## 📊 Gráficos (principais)
![Taxa de desligamento](output/taxa_desligamento.png)
![Turnover (rotatividade)](output/turnover_rotatividade.png)
![Turnover voluntário](output/turnover_voluntario.png)
![Turnover involuntário](output/turnover_involuntario.png)
![Sazonalidade (desligamento)](output/seasonality_desligamento.png)
![Tendência MM3 — desligamento](output/desligamento_ma3.png)
![Tendência MM3 — turnover](output/turnover_ma3.png)

## 📈 Estatísticas Descritivas (KPIs em %)
| KPI | mean | median | std | cv |
|:---|:---:|:---:|:---:|:---:|
| Turnover (rotatividade) | 5.79 | 5.97 | 1.26 | 0.22 |
| Taxa de desligamento | 5.34 | 5.12 | 1.92 | 0.36 |
| Voluntário | 2.65 | 2.51 | 0.97 | 0.36 |
| Involuntário | 2.69 | 2.63 | 1.10 | 0.41 |

> **Média** (valor médio), **Mediana** (valor central), **Desvio Padrão** (dispersão) e **CV** (*Coeficiente de Variação* = Desvio Padrão ÷ Média; quanto menor, mais estável).

## 🔎 Análise de Falsos Positivos (XML + Estatísticas)
Gera **XML estilo JUnit** e estatísticas de **scores** (média, mediana, desvio, CV) no *threshold* escolhido:
```bash
python scripts/fp_report.py --preds data/predictions_sample.csv --outdir output --strategy best_f1
# Artefatos:
# - output/ml_evaluation.xml
# - output/confusion_matrix.csv
# - output/metrics_by_threshold.csv
# - output/metrics_summary.json
# - output/fp_stats.csv
```

## 🧠 Esqueleto do Pipeline (Python)
```python
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss

# 1) Snapshot pessoa-mês e label 90d (voluntário)
# 2) Split temporal (train/valid/test)
# 3) Pré-processamento (imputação, OneHot, padronização)
# 4) Modelos: LogReg (baseline) e GBDT (não linear)
# 5) Métricas: PR AUC, ROC AUC, Brier, Precision@K
# 6) Explicabilidade: SHAP (global/local)
# 7) Seleção de limiar: capacidade do RH (top-K)
# 8) Monitoração: drift, recalibração, retrain
```


## 🎞️ Apresentação (PPT)

Gere a apresentação com os gráficos já prontos:
```bash
pip install python-pptx
python scripts/create_ppt.py
# Saída: output/case_turnover_apresentacao.pptx
```

## ✅ Testes rápidos (pytest)
```bash
pip install pytest
pytest -q
```
