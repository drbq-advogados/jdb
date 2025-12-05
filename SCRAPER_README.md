# PernambucoAval Scraper (fetch_pernambucoaval.py)

Este pequeno README descreve como usar o scraper que coleta metadados do site
`https://pernambucoaval.vitaldata.com.br/` e integra esses campos no
`cache_results.json` do projeto.

O que o scraper faz
- Faz download da página principal do `pernambucoaval`.
- Procura por informações próximas a cada `milhar` presente em `payload.table` do cache.
- Extrai heurísticas para `hora`, `local` e `tipo` e escreve esses campos nas linhas do `payload.table`.
- Faz backup do cache em `cache_results.json.bak` antes de sobrescrever.

Como rodar
1. Ative o ambiente virtual:
```powershell
.\.venv\Scripts\Activate.ps1
```
2. Execute o scraper:
```powershell
.\.venv\Scripts\python.exe fetch_pernambucoaval.py
```
3. (Opcional) Regenerar `web/landing_data.js` com as novas informações:
```powershell
.\.venv\Scripts\python.exe generate_landing_data.py
```

Notas sobre robustez
- O scraper usa múltiplas heurísticas (JSON embutido em scripts, busca por texto
  próximo ao milhar, labels como `Local:`/`Tipo:`). Pode não extrair 100% dos
  casos se o site alterar o layout.
- A função `clean_local_string` tenta normalizar e remover ruídos (ex.: `Grupo 12345`, `AVAL`).
- Se precisar de extração mais confiável, recomendo inspecionar o HTML da página
  e adaptar seletores (classes/ids) específicos.
 - Use o script `scraper_validation.py` para executar o scraper e gerar um relatório
   simples com contagens e exemplos. Comando:

```powershell
.\.venv\Scripts\python.exe scraper_validation.py
```

O script produz `scraper_report_examples.csv` com exemplos de linhas (útil para
inspecionar manualmente como os valores foram extraídos).
