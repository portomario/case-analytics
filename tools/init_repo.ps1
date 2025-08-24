Param(
  [string]$RepoUrl = "https://github.com/<seu-usuario>/people-analytics-case.git",
  [string]$Branch = "main"
)

Write-Host "Inicializando repositório Git local..."
git init
git add .
git commit -m "Case técnico: análise de turnover com código, testes e roteiro"
git branch -M $Branch
git remote add origin $RepoUrl
Write-Host "Realizando push para $RepoUrl ..."
git push -u origin $Branch
Write-Host "Concluído."
