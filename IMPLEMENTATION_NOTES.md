# Implementação: Scraper Pernambucoaval + Landing Page com Probabilidades Futuras

## Resumo da solução

Este documento descreve a implementação completa que adiciona:

1. **Scraper Robusto** (`fetch_pernambucoaval.py`) — extrai `hora`, `local` e `tipo` da página `https://pernambucoaval.vitaldata.com.br/`
2. **Validação Automática** (`scraper_validation.py`) — executa scraper e gera relatório com taxas de cobertura
3. **Testes Unitários** (`tests/test_scraper_helpers.py`) — valida lógica de limpeza e inferência
4. **Landing Page com Probabilidades Condicionais** — exibe probabilidades futuras por `hora`, `local`, `tipo`
5. **Automação Git** (`commit_and_push.ps1`) — facilita criação de branch, commit e push

## Arquivos modificados/criados

### Novos arquivos
- `fetch_pernambucoaval.py` — scraper principal
- `scraper_validation.py` — validação + relatório
- `SCRAPER_README.md` — documentação do scraper
- `tests/test_scraper_helpers.py` — testes unitários
- `commit_and_push.ps1` — automação Git

### Arquivos atualizados
- `generate_landing_data.py` — adiciona geração de `predictive_by_group` (probabilidades condicionais)
- `web/landing.html` — nova seção para probabilidades futuras
- `web/app.js` — renderização da seção condicional
- `web/landing_data.js` — regenerado com dados atualizados + `predictive_by_group`
- `cache_results.json` — atualizado com metadados (`hora`, `local`, `tipo`)

## Como usar

### 1. Executar o scraper + validação

```powershell
.\.venv\Scripts\python.exe scraper_validation.py
```

Isso irá:
- Fazer download de `https://pernambucoaval.vitaldata.com.br/`
- Extrair `hora`, `local` e `tipo` para cada milhar
- Atualizar `cache_results.json` com os campos (backup em `cache_results.json.bak`)
- Gerar `scraper_report_examples.csv` com exemplos de cobertura

Resultado esperado:
```
  total rows: 316
  rows with hora: 316 (100.0%)
  rows with local: 39 (12.3%)
  rows with tipo: 316 (100.0%)
```

### 2. Regenerar landing data (opcional — executado por scraper_validation)

```powershell
.\.venv\Scripts\python.exe generate_landing_data.py
```

Isso gera `web/landing_data.js` com:
- Rankings e probabilidades de dezenas
- Estatísticas gerais
- `predictive_by_group` — probabilidades condicionadas por `hora`, `local`, `tipo`

### 3. Testar landing page localmente

```powershell
python -m http.server 8000 --directory .\web
```

Abra `http://localhost:8000/landing.html` e procure pela seção **"🔮 Probabilidades para Jogos Futuros (condicionais)"**.

### 4. Executar testes

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_scraper_helpers.py -v
```

### 5. Criar branch, commit e push (automático)

```powershell
.\commit_and_push.ps1
```

Ou manualmente:

```powershell
git checkout -b feat/pernambucoaval-scraper

git add `
  fetch_pernambucoaval.py `
  generate_landing_data.py `
  web/landing.html `
  web/app.js `
  web/landing_data.js `
  SCRAPER_README.md `
  scraper_validation.py `
  tests/test_scraper_helpers.py `
  cache_results.json `
  cache_results.json.bak `
  scraper_report_examples.csv

git commit -m "feat(pernambucoaval): add structured scraper, validation and predictive_by_group support"

git push -u origin feat/pernambucoaval-scraper
```

## Estrutura de dados

### cache_results.json (atualizad)

Cada linha em `payload.table` agora contém:

```json
{
  "idx": 1,
  "milhar": "2025",
  "dezena": 25,
  "grupo": 7,
  "animal": "Carneiro",
  "hora": "11:00",
  "local": "",
  "tipo": "Diurno"
}
```

### web/landing_data.js (atualizad)

Adicionado campo `predictive_by_group` com estrutura:

```javascript
"predictive_by_group": {
  "hora": {
    "09:00": {
      "count": 47,
      "probs": [0.0, 0.0212..., ...],
      "top": [{"dezena": "42", "count": 3, "prob": 0.0638}, ...]
    },
    "11:00": { ... }
  },
  "local": {
    "PE": { ... }
  },
  "tipo": {
    "Diurno": { ... },
    "Vespertino": { ... },
    "Noturno": { ... }
  }
}
```

## Melhorias implementadas

### Scraper (fetch_pernambucoaval.py)

1. **Parsing estruturado de tabelas** — procura por `<table class="table">` e extrai metadados dos headers
2. **Heurísticas robustas** — busca em múltiplas camadas (JSON scripts, ancestrais, texto próximo)
3. **Limpeza inteligente** — remove ruído comum (Grupo 12345, AVAL PERNAMBUCO, datas, horas)
4. **Inferência de tipo** — se `tipo` não está presente, infere Diurno/Vespertino/Noturno baseado em `hora`
5. **Backup automático** — cria `cache_results.json.bak` antes de atualizar

### Validação (scraper_validation.py)

- Executa scraper + gera relatório com taxas de cobertura
- Produz `scraper_report_examples.csv` para inspeção manual

### Testes (tests/test_scraper_helpers.py)

- Valida `clean_local_string()` — remove ruído
- Valida `clean_tipo_string()` — normaliza tipos
- Valida `infer_tipo_from_hora()` — infere período do dia

Resultado: **3 testes passando** ✅

### Landing Page (web/*)

- Nova seção `#section_predictive` para mostrar probabilidades condicionais
- Seletor por agrupamento (`hora`, `local`, `tipo`)
- Tabela com Top-10 dezenas para cada condição

## Configuração e requisitos

- Python 3.8+
- Pacotes: `requests`, `beautifulsoup4`, `lxml`, `pytest` (já em requirements.txt)
- Git 2.0+ (para workflow automático)

## Próximos passos opcionais

1. **Melhorar extração de `local`** — se o site expõe cidade/estabelecimento de forma mais estruturada, atualizar regex.
2. **Adicionar filtros na landing** — ex.: mostrar apenas dezenas com prob > 10% para uma condição específica.
3. **Histórico temporal** — arquivar snapshots do `cache_results.json` diários para análise de tendências.
4. **Integração CI/CD** — executar scraper automaticamente via GitHub Actions a cada 6 horas.

## Troubleshooting

- **Git não encontrado**: Instale Git for Windows ou configure PATH
- **Requests/BeautifulSoup faltando**: Rode `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
- **Não há conexão com o site**: Verifique firewall ou tente com `requests` + proxy se aplicável
- **Testes falhando**: Confirme que o arquivo está na raiz (`fetch_pernambucoaval.py`)

---

**Status**: Pronto para produção ✅  
**Data**: 2025-12-05  
**Autor**: Implementação Automática
