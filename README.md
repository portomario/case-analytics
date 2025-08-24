# Case Técnico — Coordenador de People Analytics
Autor: Mario L. O. Porto — Coordenador de People Analytics (case técnico)

Este repositório contém o material do case com **código Python testável**, **gráficos** e **relatórios**.  
Turnover calculado por: `[(Admissões + Desligamentos)/2] / Total * 100` (rotatividade) e **taxa de desligamento** separada (desligamentos / HC médio).

## Visão Geral

O objetivo foi diagnosticar a rotatividade de pessoal ao longo de 24 meses, propor alavancas de melhoria contínua e um projeto preditivo, e transformar isso em um plano de ação mensurável.

## Pilar 1 — Diagnóstico Estatístico (Exploratório)

### 1.1 Definições e Fórmulas

Para evitar ambiguidade entre turnover e taxa de desligamento, adotamos duas métricas centrais:

Turnover (Rotatividade, “ampliado”) = [(Admissões + Desligamentos) / 2] / Headcount total × 100
Racional: mede a pressão de movimentação de pessoas (entrada + saída) no período.

Taxa de Desligamento = Desligamentos / Headcount médio × 100
Racional: métrica clássica para comparar saídas entre áreas/empresas. Em muitas praças, é chamada de “turnover”.

Headcount médio do mês = média de Total_{t-1} e Total_t (no primeiro mês, usa-se Total_t).

Também abrimos a composição:

Voluntário = Desligamentos voluntários / HC médio × 100
Involuntário = Desligamentos involuntários / HC médio × 100

### 1.2 Estatísticas Descritivas (taxas mensais, em %)

(Ver aba Estatísticas do arquivo output/people-analytics-turnover.xlsx).

Resumo qualitativo:

Turnover (rotatividade): nível moderado, com variação sazonal em meses de pico de movimento (jun–out).
Desligamento: picos notáveis em out/2021, coerentes com a série; CV indica variação moderada.
Mix voluntário/involuntário: média aproximada de ~45% voluntário / ~55% involuntário no período.

### 1.3 Série Temporal, Tendência e Sazonalidade

Tendência: média móvel 3M mostra leve alta estrutural na taxa de desligamento em 2022 vs 2021.
Sazonalidade: média por mês indica picos entre jun–out; vales no início de ano (jan–fev).
(Ver output/seasonality_desligamento.png.)

### 1.4 Anomalias

Usamos z-score na taxa de desligamento. Marcamos como anomalia |z| ≥ 2.

Destaque: out/2021 (~6,34%) → z elevado, merece deep dive (motivos, áreas, gestores).
Exportadas em output/anomalias_desligamento.csv.

### 1.5 Hipóteses e Dados Faltantes

H1 (Voluntário): compa-ratio e eNPS baixos elevam pedidos de desligamento.

H2 (Involuntário): absenteísmo e performance baixa elevam desligamentos por decisão da empresa.

Dados a coletar para validação estatística: remuneração (faixa, compa-ratio), carreira (mobilidade, promoções), eNPS, tenure (tempo de casa), engajamento (pulse), horas extras, jornada, registros de performance/PDIs, motivo de saída padronizado, localização/turno/gestor/cargo/família de cargo.

## Pilar 2 — Melhoria Contínua (Lean Six Sigma — DMAIC)

Meta do projeto: reduzir turnover voluntário para ≤ 1,40%/mês em 6 meses, mantendo qualidade operacional e evitando deslocamento do problema (ex.: aumento indevido do involuntário).

### D — Define (Definir)

Problema: pico e variabilidade do voluntário em áreas X/Y geram perdas de produtividade e custos de reposição.
Escopo: áreas X/Y (piloto), população CLT, centros A/B; período base 12 meses.
KPI primário: Voluntário % (mensal); secundários: eNPS, taxa 0–90 dias, TTM de reposição, custo por desligamento.
Meta: ≤ 1,40%/mês nas áreas piloto, com IC95% comprovando redução.

### M — Measure (Medir)

Mapa de dados: HRIS, folha, ponto eletrônico, pesquisa de clima (eNPS), remuneração, desempenho.
Qualidade dos dados: data quality checks (missing, duplicidades, consistência temporal).
Linha de base: série 12–24 meses por área/gestor; p-charts para estabilidade do processo.

### A — Analyze (Analisar)

Drivers (hipóteses): desequilíbrio salarial (compa-ratio), baixa mobilidade interna, liderança local, sobrecarga/horas extras, jornada em turnos específicos.
Técnicas: regressões/árvores de decisão (voluntário ~ variáveis), Pareto de motivos de saída, time-to-event nos 0–180 dias.

### I — Improve (Melhorar)

Ações candidatas:
Stay interviews entre 60–120 dias e após 1 ano (checklist padronizado).
Janela de mobilidade interna trimestral + comunicação ativa de vagas.
Revisão de bandas salariais (áreas com compa-ratio < 0,95).
Limite de horas extras sustentado e redistribuição de carga.
Treinamento de liderança em 1:1, feedback e carreira.
Teste controlado: pilotos A/B por área, 8–12 semanas; KPIs com SPC (p-charts) e diff-in-diff quando aplicável.

### C — Control (Controlar)

Painel mensal (People Analytics) com alerts, p-charts, e drill-down por gestor/cargo.
Ritual de governança: ops review mensal (RH + negócio), playbook de retenção e runbook de reposição.
Padronização: atualizar políticas (mobilidade, bandas), OKRs e PIPs para casos de performance.

## Pilar 3 — Preditivo (Machine Learning)

Objetivo: estimar probabilidade de pedido de demissão em 90 dias (janela deslizante), priorizando ações de retenção.

### 3.1 Dados & Features (exemplos)

Demográficos/contratuais: área, cargo/família, unidade, regime de trabalho, tenure (dias).
Remuneração: salário base, compa-ratio, variações recentes, PLR elegibilidade.
Jornada: horas extras, escala/turno, ponto (absenteísmo, extrapolações).
Carreira: mobilidade interna, promoções/rebaixamentos, treinamento.
Clima/engajamento: eNPS, pesquisas pulse, participação em rituais.
Histórico de gestão: span of control, rotatividade do gestor, sucessões.
Sazonais/temporais: mês, sazonalidade local.
Tratamento: reference date mensal; target = “pedido de demissão nos próximos 90 dias”; split temporal (treino < validação < teste).

### 3.2 Modelagem

Modelos base: Regressão Logística (baseline interpretável) e Gradient Boosting (XGBoost/LightGBM).
Métricas: PR AUC (caso raro), precisão@k, calibration (Brier) e fairness por grupo (área/unidade).
Explicabilidade: SHAP para feature importance global e local (nível pessoa).

### 3.3 Pipeline (pseudocódigo Python)

Ver scripts/analyze.py para preparação de série e tests/test_metrics.py para validações. O pipeline preditivo seria:

1) Extrair janela de referência mensal e montar target 90 dias
2) Engineer features (tenure, compa-ratio, horas extras, eNPS etc.)
3) Split por tempo (train/valid/test)
4) Treinar baseline (LogReg) + GBM
5) Avaliar por PR AUC, precision@k, calibration; fairness por área
6) Explicar com SHAP e gerar top fatores por colaborador

## Pilar 4 — Plano de Ação (Executivo)

### Conclusão A:Compa-ratio e baixa mobilidade correlacionam com voluntário alto.

Ações: (1) Revisão de bandas e ajustes de outliers; (2) Janela de mobilidade trimestral; (3) Comunicação ativa de carreira.
Meta: reduzir voluntário para ≤ 1,40% em 6 meses nas áreas piloto.
Indicadores: voluntário %, eNPS, taxa 0–90 dias, tempo de reposição.

### Conclusão B: Excesso de horas extras e gestão local explicam clusters de involuntário.

Ações: (1) Balanceamento de escala e limites de HE; (2) Treinamento de liderança e runbook de performance; (3) Workforce planning por turno.
Meta: reduzir involuntário em 0,4 pp; manter qualidade (absenteísmo estável).
Indicadores: involuntário %, HE média/mês, absenteísmo, PIPs concluídos.



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
