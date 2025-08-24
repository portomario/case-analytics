# Case Técnico — Coordenador de People Analytics

Este pacote contém **código Python testável**, **gráficos**, **relatório** e **apresentação (PPTX)** para o case de turnover.

## Estrutura

```
people-analytics-case/
├─ README.md
├─ requirements.txt
├─ data/
│  └─ turnover_monthly.csv
├─ scripts/
│  ├─ analyze.py
│  ├─ create_ppt.py
│  └─ generate_all.py
├─ docs/
│  ├─ report.md
│  ├─ deck_outline.md
│  └─ glossary.md
├─ tests/
│  └─ test_metrics.py
├─ tools/
│  └─ init_repo.ps1
└─ output/  (gerado pelos scripts)
```

## Como rodar localmente

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Gera métricas, tabelas (Excel), PNGs e PPTX (se python-pptx estiver instalado)
python scripts\generate_all.py

# Executa os testes automatizados
pytest -q
```

- Os arquivos gerados ficam em `output/`, incluindo `people-analytics-turnover.xlsx`, gráficos PNG e `case_turnover_apresentacao.pptx`.

## Subir no GitHub (via PowerShell)

1. Crie um repositório **vazio** (sem README) no GitHub, por exemplo: `people-analytics-case`.
2. No PowerShell, rode:

```powershell
git init
git add .
git commit -m "Case técnico: análise de turnover com código, testes e roteiro"
git branch -M main
git remote add origin https://github.com/<seu-usuario>/people-analytics-case.git
git push -u origin main
```

> Dica: você também pode usar o script `tools\init_repo.ps1` e editar as variáveis de usuário/repos.

## Decisões de Métrica (resumo)

- **Turnover (rotatividade)**: `[(Admissões + Desligamentos) / 2] / Headcount total`. Escolhemos este como o **turnover ampliado**, pois captura a **pressão de movimentação** média no período usando o total do mês como base.  
- **Taxa de desligamento**: `Desligamentos / Headcount médio`. Mantemos **separado** para comparabilidade com benchmarks que chamam esta métrica de “turnover”.  
- **Voluntário** e **Involuntário**: taxas por `HC médio`, permitindo entender composição do churn.
- **Média móvel de 3 meses**: leitura de tendência para uma série curta (24 meses).
- **Anomalias (z-score |z|≥2)**: destacar meses atípicos para *deep dive*.

Detalhes completos em `docs/report.md` e `docs/deck_outline.md`.
