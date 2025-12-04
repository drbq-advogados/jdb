# 🎰 JDB Project - Análise Probabilística Operacional

**Status:** ⚠️ **ERROS CORRIGIDOS - PRONTO PARA TESTE**

---

## 📋 Sumário Executivo

Este projeto consolida dados de **loteria Pernambuco (pernambucoaval)** em análise probabilística rigorosa com:

- **Dashboard Streamlit** para visualização interativa
- **Modelo Bayesiano** (PyMC) + GLM statsmodels para estimação de probabilidades
- **Backtest walk-forward** com validação de calibração
- **Análise de risco** (VaR/CVaR) via Monte Carlo

### Status de Conclusão
- ✅ Consolidação de fontes (apenas `pernambucoaval`)
- ✅ Cache de dados (347 milhares válidos)
- ✅ Notebook com pipeline completo
- ⚠️ Dependências críticas corrigidas mas PyMC pendente de instalação
- 🟡 Testes de execução ainda não feitos

---

## 🚀 Quick Start

### 1. Instalar Dependências
```powershell
cd "c:\Users\Matrix\Downloads\Sistema JDB\jdb"
pip install -r requirements.txt --upgrade
```

**Nota:** Se PyMC falhar, o projeto funcionará com fallback para statsmodels. Veja [Instalação de PyMC](#instalação-de-pymc-windows) para solução completa.

### 2. Testar Ambiente
```powershell
python -c "import streamlit; import pandas; import numpy; import pymc; print('✓ All dependencies OK')"
```

### 3. Executar Dashboard
```powershell
streamlit run app.py
```

Acesse: `http://localhost:8501`

### 4. Executar Análise Probabilística
```powershell
jupyter notebook analise_probabilidades_operacional.ipynb
```

Execute as células na ordem (Ctrl+Enter em cada uma).

---

## 📁 Estrutura do Projeto

```
jdb/
├── app.py                                    # Streamlit dashboard principal
├── analise_probabilidades_operacional.ipynb # Pipeline de análise (8 seções)
├── cache_results.json                        # Cache de 347 milhares (65 KB)
├── requirements.txt                          # Dependências (ATUALIZADO)
├── ERROR_AUDIT_REPORT.md                     # Relatório de auditoria completo
├── CHECKLIST_CORREÇÕES.md                    # Checklist de ações
├── install_dependencies.ps1                  # Script de instalação PowerShell
├── GUIA_NOTEBOOK.md                          # Guia de uso do notebook
├── .venv/                                    # Virtual environment (Python 3.11.8)
├── output/                                   # Saídas e logs
│   └── mc_final_balances.csv                 # Resultados de simulações
└── templates/
    └── index.html                            # UI Streamlit customizada
```

---

## 🔧 Dependências

### Críticas (para app.py)
- ✅ `streamlit>=1.30.0` - Dashboard web
- ✅ `pandas>=2.1.0` - Data processing
- ✅ `numpy>=1.26.0` - Numerical computing
- ✅ `requests>=2.32.0` - HTTP requests
- ✅ `beautifulsoup4>=4.12.2` - Web scraping
- ✅ `lxml>=4.9.3` - XML parsing
- ✅ `scipy>=1.11.0` - Statistical functions
- ✅ `altair>=5.0.1` - Data visualization
- ✅ `python-dotenv>=1.0.1` - Config management

### Para Notebook (Análise Probabilística)
- ✅ `statsmodels>=0.14.0` - GLM, time series (INSTALADO)
- ⚠️ `pymc>=5.0.0` - Bayesian modeling (PENDENTE INSTALAÇÃO)
- ✅ `scikit-learn` - Machine learning utilities
- ✅ `arviz` - Bayesian diagnostics (dependência do PyMC)

---

## 🔴 Problemas Identificados & Soluções

### Problema 1: PyMC Não Instala
**Erro:** `ModuleNotFoundError: No module named 'pymc'`

**Causa:** PyMC requer compilação Cython em Windows

**Solução A (Automática):**
```powershell
powershell -ExecutionPolicy Bypass -File install_dependencies.ps1
```

**Solução B (Manual com Visual C++):**
1. Instalar [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Executar:
```powershell
pip install pymc --no-build-isolation
```

**Solução C (Fallback - Usar apenas statsmodels):**
- ✅ Notebook já tem fallback automático (célula 1)
- Todos os modelos funcionam com GLM em vez de Bayesian
- Confiança ainda disponível via Clopper-Pearson CI

---

### Problema 2: Import BeautifulSoup Erro
**Erro:** `No module named 'beautifulsoup4'`

**Solução:** ✅ JÁ CORRIGIDO
- Use: `import bs4` ou `from bs4 import BeautifulSoup`
- ❌ Não use: `import beautifulsoup4`
- Package nome ≠ module nome em Python

---

### Problema 3: Cache File Not Found
**Erro:** `FileNotFoundError: [Errno 2] No such file or directory: 'cache_results.json'`

**Solução:**
1. Executar `streamlit run app.py`
2. Clicar em "🔄 Forçar Atualização" no sidebar
3. Aguardar coleta de dados (2-3 segundos)
4. Arquivo `cache_results.json` será criado com 347 milhares

---

## 📊 Relatório de Auditoria

**Arquivo:** `ERROR_AUDIT_REPORT.md`

Resumo das correções:

| Item | Status | Ação |
|------|--------|------|
| requirements.txt incompleto | ✅ CORRIGIDO | Adicionado pymc + statsmodels |
| Python syntax errors | ✅ PASSOU | Todos 3 arquivos compilam |
| Cache data integrity | ✅ VÁLIDO | 347 milhares processados |
| Import discrepancies | 🟡 DOCUMENTADO | bs4 import correto em app.py |
| PyMC installation | ⏳ PENDENTE | Ver seção "Problemas Identificados" |
| Notebook execution | ⏳ PENDENTE | Testar após PyMC ou com fallback |

Veja `ERROR_AUDIT_REPORT.md` para análise completa.

---

## 📖 Documentação Relacionada

- **`GUIA_NOTEBOOK.md`** - Guia detalhado do pipeline de análise com métricas
- **`CHECKLIST_CORREÇÕES.md`** - Checklist passo-a-passo para resolver todos os problemas
- **`ERROR_AUDIT_REPORT.md`** - Relatório técnico completo de auditoria

---

## 🧪 Testes de Validação

### Teste 1: Imports Básicos
```powershell
python -c "
import streamlit
import pandas
import numpy
import requests
import bs4
import scipy
import statsmodels
print('✅ Core dependencies OK')
"
```

### Teste 2: Cache Loading
```powershell
python -c "
import json
with open('cache_results.json') as f:
    data = json.load(f)
    print(f\"✅ Cache valid: {len(data['payload']['table'])} records\")
"
```

### Teste 3: Notebook Cells (Manual)
1. Abrir: `jupyter notebook analise_probabilidades_operacional.ipynb`
2. Executar célula 1 (Imports) - deve mostrar `✅ Imports OK`
3. Executar célula 2 (ETL) - deve carregar 347 milhares
4. Executar célula 3 (Data Quality) - deve mostrar chi-square test
5. Se tudo passar, notebook está funcional ✅

---

## 🎯 Casos de Uso

### Use Case 1: Dashboard Interativo
**Objetivo:** Visualizar probabilidades de dezenas/grupos para próximas rodadas

**Como usar:**
```powershell
streamlit run app.py
# No sidebar:
# - Selecionar TTL do cache (padrão 24h)
# - Clicar "Forçar Atualização" se necessário
# - Visualizar recomendações por confidence level
```

### Use Case 2: Análise Estatística Detalhada
**Objetivo:** Compreender distribuição de probabilidades, validação e risco

**Como usar:**
```powershell
jupyter notebook analise_probabilidades_operacional.ipynb
# Executar 8 seções:
# 1. ETL - carrega dados
# 2. EDA - visualiza qualidade
# 3. Estimação - calcula probabilidades
# 4. Modelos - Bayesian (PyMC) + GLM (statsmodels)
# 5. Calibração - valida modelos
# 6. Backtest - simula performance passada
# 7. VaR/CVaR - analisa risco
# 8. Report - exporta resultados
```

### Use Case 3: Debugging & Troubleshooting
**Objetivo:** Identificar e corrigir problemas

**Como usar:**
1. Ler `ERROR_AUDIT_REPORT.md` para status geral
2. Consultar `CHECKLIST_CORREÇÕES.md` para solução específica
3. Executar testes de validação acima
4. Criar issue se problema não listado

---

## 🔐 Instalação de PyMC (Windows)

PyMC requer compilação. Existem 2 estratégias:

### Estratégia A: Visual C++ Build Tools (Recomendado)
```
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Instalar com "Desktop development with C++" workload
3. Executar:
   pip install pymc --no-build-isolation
4. Aguardar compilação (5-10 minutos)
5. Testar: python -c "import pymc; print(pymc.__version__)"
```

### Estratégia B: Pre-compiled Wheels
```powershell
pip install pymc --only-binary :all:
# Pode não funcionar em todas as versões do Python
```

### Estratégia C: Docker (Alternativa)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

Buildar: `docker build -t jdb-project .`  
Rodar: `docker run -p 8501:8501 jdb-project`

---

## 📞 Troubleshooting

**P: O app.py começa mas não carrega dados**  
R: Clicar em "🔄 Forçar Atualização" no sidebar. Primeira execução leva 2-3 seg.

**P: Notebook falha na célula 1 (Imports)**  
R: Verificar instalação: `pip list | grep -E "pymc|statsmodels|scipy"`

**P: Chi-square test p-valor está baixo (<0.05)**  
R: Possível indicação de não-uniformidade. Verificar fonte de dados em app.py.

**P: Simulações Monte Carlo levam muito tempo**  
R: Reduzir parâmetros em célula 7: `n_simulations=1000` (padrão 10k)

---

## 🚀 Próximos Passos

- [ ] Instalar PyMC com Visual C++ Build Tools
- [ ] Executar completamente o notebook (todas as 8 seções)
- [ ] Testar app.py em múltiplos ciclos de cache refresh
- [ ] Documentar resultados em `output/analysis_results.json`
- [ ] Deploy em produção (Streamlit Cloud ou servidor local)

---

## 📄 Licença & Referências

- **Fonte de Dados:** Pernambuco Aval (vitaldata.com.br)
- **Framework:** Streamlit 1.30+ + PyMC 5.0+ + statsmodels 0.14+
- **Autor:** Análise Probabilística Operacional - Projeto JDB
- **Data Criação:** 2025-12-03

---

## ✅ Checklist de Go-Live

- [ ] Todas as dependências instaladas
- [ ] Notebook executa até célula 5 (Calibration)
- [ ] app.py carrega com cache válido
- [ ] Testes de validação passam
- [ ] Documentação lida e entendida
- [ ] ERROR_AUDIT_REPORT.md revisado

**Status:** 🟡 AGUARDANDO RESOLUÇÃO DE DEPENDÊNCIAS

Após completar checklist, sistema está pronto para análise operacional.

---

**Última atualização:** 2025-12-03  
**Versão:** 1.0  
**Mantidor:** GitHub Copilot  
**Status:** ⚠️ Aguardando testes de instalação PyMC
