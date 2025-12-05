# Git não detectado — Guia Alternativo de Deploy

## Situação

Git não está disponível no seu ambiente PowerShell. Você tem 3 opções:

## Opção 1: Instalar Git for Windows (Recomendado)

1. Acesse: https://git-scm.com/download/win
2. Baixe e execute o instalador
3. Durante a instalação, escolha "Use Git from the Windows Command Prompt"
4. Reinicie o PowerShell
5. Execute: `.\.venv\Scripts\python.exe git_workflow.py`

## Opção 2: Usar Git Bash (se já tiver Git instalado em outro lugar)

1. Abra Git Bash
2. Navegue até o diretório do projeto
3. Execute os comandos manualmente (veja Opção 3 abaixo)

## Opção 3: Upload Manual via GitHub Web

Se não quiser instalar Git agora, você pode fazer upload manual dos arquivos:

1. Acesse: https://github.com/drbq-advogados/jdb
2. Clique em "+" → "Create new branch"
3. Nome: `feat/pernambucoaval-scraper`
4. Upload dos arquivos modificados:
   - `fetch_pernambucoaval.py`
   - `generate_landing_data.py`
   - `web/landing.html`
   - `web/app.js`
   - `web/landing_data.js`
   - `SCRAPER_README.md`
   - `scraper_validation.py`
   - `tests/test_scraper_helpers.py`
   - `cache_results.json`
   - `cache_results.json.bak`
   - `scraper_report_examples.csv`
   - `commit_and_push.ps1`
   - `git_workflow.py`
   - `IMPLEMENTATION_NOTES.md`
5. Crie um commit com mensagem: `feat(pernambucoaval): add structured scraper, validation and predictive_by_group support`
6. Abra um Pull Request para `main`

## Opção 4: Usar WSL (Windows Subsystem for Linux)

Se tiver WSL instalado:

```bash
cd /mnt/c/Users/Matrix/Downloads/Sistema\ JDB/jdb
python git_workflow.py
```

## Verificar se você tem Git instalado em outro lugar

Tente estes comandos no PowerShell:

```powershell
# Procurar em Program Files
Get-ChildItem "C:\Program Files\Git\cmd\git.exe" -ErrorAction SilentlyContinue

# Procurar em Program Files (x86)
Get-ChildItem "C:\Program Files (x86)\Git\cmd\git.exe" -ErrorAction SilentlyContinue

# Se encontrar, adicione ao PATH:
$env:Path += ";C:\Program Files\Git\cmd"
git --version
```

## Resumo do que foi implementado

Enquanto resolve o Git, aqui está o que já está pronto para usar:

### Scripts prontos para rodar agora:

```powershell
# Rodar o scraper + validação (atualiza cache e landing data)
.\.venv\Scripts\python.exe scraper_validation.py

# Rodar os testes
.\.venv\Scripts\python.exe -m pytest tests/test_scraper_helpers.py -v

# Testar landing page localmente
python -m http.server 8000 --directory .\web
# Abra http://localhost:8000/landing.html
```

### Arquivos prontos para enviar:

Todos os arquivos estão na raiz do projeto e já funcionam. Você só precisa:
1. Instalar Git (ou usar opção manual)
2. Criar branch `feat/pernambucoaval-scraper`
3. Commit com mensagem `feat(pernambucoaval): add structured scraper, validation and predictive_by_group support`
4. Fazer PR para `main`

## Próximos passos

1. **Instale Git** (recomendado) ou escolha uma alternativa acima
2. **Rode o scraper** para validar:
   ```powershell
   .\.venv\Scripts\python.exe scraper_validation.py
   ```
3. **Teste a landing page** localmente:
   ```powershell
   python -m http.server 8000 --directory .\web
   ```
4. **Faça commit e push** usando um dos métodos acima

---

**Suporte**: Se precisar de ajuda com Git, acesse https://git-scm.com/doc ou https://github.com/git-tips/tips
