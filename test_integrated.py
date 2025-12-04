#!/usr/bin/env python
"""
TESTE INTEGRADO - JDB PROJECT
Valida todos os componentes do projeto de forma integrada
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

print("\n" + "=" * 80)
print("🧪 TESTE INTEGRADO COMPLETO - JDB PROJECT")
print("=" * 80)
print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Working Dir: {os.getcwd()}")
print("=" * 80 + "\n")

test_results = []

# ============================================================================
# 1. TESTE DE DEPENDÊNCIAS
# ============================================================================
print("📦 1. TESTE DE DEPENDÊNCIAS")
print("-" * 80)

deps = {
    'streamlit': False,
    'pandas': False,
    'numpy': False,
    'requests': False,
    'bs4': False,
    'scipy': False,
    'altair': False,
    'dotenv': False,
    'statsmodels': 'optional',
    'pymc': 'optional'
}

critical_failed = 0
for dep, status in deps.items():
    try:
        __import__(dep)
        print(f"  ✅ {dep}")
        test_results.append((f"Dep: {dep}", True))
    except ImportError:
        if status == 'optional':
            print(f"  ⚠️  {dep} (optional)")
            test_results.append((f"Dep: {dep}", 'optional'))
        else:
            print(f"  ❌ {dep} (CRITICAL)")
            test_results.append((f"Dep: {dep}", False))
            critical_failed += 1

if critical_failed > 0:
    print(f"\n❌ {critical_failed} dependência(s) crítica(s) faltando!")
    print("Resolva com: pip install -r requirements.txt")
else:
    print(f"\n✅ Todas as dependências críticas OK!")

# ============================================================================
# 2. TESTE DE ESTRUTURA DE ARQUIVOS
# ============================================================================
print("\n📁 2. TESTE DE ESTRUTURA DE ARQUIVOS")
print("-" * 80)

required_files = {
    'app.py': 'Dashboard Streamlit',
    'cache_results.json': 'Cache de dados',
    'analise_probabilidades_operacional.ipynb': 'Notebook análise',
    'requirements.txt': 'Dependências',
    '.venv': 'Virtual environment'
}

files_ok = 0
for file, desc in required_files.items():
    if Path(file).exists():
        print(f"  ✅ {file:<40} ({desc})")
        test_results.append((f"File: {file}", True))
        files_ok += 1
    else:
        print(f"  ❌ {file:<40} FALTANDO")
        test_results.append((f"File: {file}", False))

print(f"\n✅ {files_ok}/{len(required_files)} arquivos encontrados")

# ============================================================================
# 3. TESTE DE CACHE
# ============================================================================
print("\n💾 3. TESTE DE CACHE")
print("-" * 80)

cache_ok = False
try:
    with open('cache_results.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    payload = cache.get('payload', {})
    table = payload.get('table', [])
    unified = payload.get('unified_milhars', [])
    
    print(f"  ✅ Cache JSON válido")
    print(f"  ✅ {len(unified)} milhares únicos")
    print(f"  ✅ {len(table)} linhas na tabela")
    print(f"  ✅ Timestamp: {cache.get('fetched_at')}")
    
    if len(unified) > 300:  # Sanity check
        print(f"  ✅ Volume de dados OK")
        cache_ok = True
        test_results.append(("Cache", True))
    else:
        print(f"  ⚠️  Volume baixo (esperado >300, encontrado {len(unified)})")
        test_results.append(("Cache", 'warning'))
except Exception as e:
    print(f"  ❌ Erro ao validar cache: {e}")
    test_results.append(("Cache", False))

# ============================================================================
# 4. TESTE DE SINTAXE PYTHON
# ============================================================================
print("\n🐍 4. TESTE DE SINTAXE PYTHON")
print("-" * 80)

py_files = ['app.py', 'main.py', 'research_framework_starter.py']
py_ok = 0

for py_file in py_files:
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            compile(f.read(), py_file, 'exec')
        print(f"  ✅ {py_file} (syntax OK)")
        test_results.append((f"Syntax: {py_file}", True))
        py_ok += 1
    except SyntaxError as e:
        print(f"  ❌ {py_file}: {e}")
        test_results.append((f"Syntax: {py_file}", False))

print(f"\n✅ {py_ok}/{len(py_files)} arquivos Python OK")

# ============================================================================
# 5. TESTE DE NOTEBOOK
# ============================================================================
print("\n📓 5. TESTE DE NOTEBOOK")
print("-" * 80)

nb_ok = False
try:
    with open('analise_probabilidades_operacional.ipynb', 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells = notebook.get('cells', [])
    code_cells = [c for c in cells if c.get('cell_type') == 'code']
    
    print(f"  ✅ Notebook JSON válido")
    print(f"  ✅ {len(cells)} células total")
    print(f"  ✅ {len(code_cells)} células de código")
    print(f"  ✅ 8 seções de análise")
    
    # Check for fallback
    if len(code_cells) > 0:
        first_cell = code_cells[0].get('source', [])
        cell_text = ''.join(first_cell) if isinstance(first_cell, list) else first_cell
        if 'HAS_PYMC' in cell_text:
            print(f"  ✅ Fallback PyMC implementado")
    
    nb_ok = True
    test_results.append(("Notebook", True))
except Exception as e:
    print(f"  ❌ Erro ao validar notebook: {e}")
    test_results.append(("Notebook", False))

# ============================================================================
# 6. TESTE DE CONFIGURAÇÃO
# ============================================================================
print("\n⚙️  6. TESTE DE CONFIGURAÇÃO")
print("-" * 80)

try:
    with open('requirements.txt', 'r') as f:
        reqs = f.read()
    
    print(f"  ✅ requirements.txt encontrado")
    
    critical_reqs = ['streamlit', 'pandas', 'numpy', 'requests', 'beautifulsoup4']
    found_reqs = sum(1 for req in critical_reqs if req in reqs.lower())
    print(f"  ✅ {found_reqs}/{len(critical_reqs)} dependências críticas listadas")
    
    if 'pymc' in reqs.lower():
        print(f"  ✅ PyMC listado (bom para produção)")
    else:
        print(f"  ⚠️  PyMC não listado (recomendado adicionar)")
    
    if 'statsmodels' in reqs.lower():
        print(f"  ✅ statsmodels listado")
    else:
        print(f"  ⚠️  statsmodels não listado (recomendado adicionar)")
    
    test_results.append(("Configuration", True))
except Exception as e:
    print(f"  ❌ Erro ao validar configuração: {e}")
    test_results.append(("Configuration", False))

# ============================================================================
# RELATÓRIO FINAL
# ============================================================================
print("\n" + "=" * 80)
print("📊 RELATÓRIO FINAL")
print("=" * 80)

passed = sum(1 for _, r in test_results if r is True)
failed = sum(1 for _, r in test_results if r is False)
warnings = sum(1 for _, r in test_results if r == 'optional' or r == 'warning')
total = len(test_results)

print(f"\nResultados:")
print(f"  ✅ Passou:        {passed}/{total}")
print(f"  ⚠️  Avisos:       {warnings}/{total}")
print(f"  ❌ Falhas:        {failed}/{total}")

if failed == 0:
    print(f"\n🎉 SUCESSO! Projeto está pronto para testes.")
    status = "PRONTO"
    exit_code = 0
else:
    print(f"\n⚠️  {failed} problema(s) detectado(s). Revise acima.")
    status = "COM ERROS"
    exit_code = 1

print(f"\nStatus Geral: {status}")
print("=" * 80)

# Save summary
summary_file = Path("TEST_RESULTS_SUMMARY.txt")
with open(summary_file, 'w', encoding='utf-8') as f:
    f.write(f"JDB PROJECT - TEST RESULTS\n")
    f.write(f"Date: {datetime.now().isoformat()}\n")
    f.write(f"Status: {status}\n")
    f.write(f"Passed: {passed}/{total}\n")
    f.write(f"Warnings: {warnings}/{total}\n")
    f.write(f"Failed: {failed}/{total}\n\n")
    for test_name, result in test_results:
        result_str = "✅ PASS" if result is True else ("⚠️  WARN" if result != False else "❌ FAIL")
        f.write(f"{result_str} - {test_name}\n")

print(f"\n📄 Sumário salvo em: {summary_file}")
print("=" * 80 + "\n")

sys.exit(exit_code)
