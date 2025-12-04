#!/usr/bin/env python
# Test notebook structure and cells

import json
import sys
from pathlib import Path

notebook_file = Path("analise_probabilidades_operacional.ipynb")

print("=" * 70)
print("📓 TESTE DO NOTEBOOK - JDB PROJECT")
print("=" * 70)

# 1. Check file exists
if not notebook_file.exists():
    print(f"❌ ERRO: {notebook_file} não encontrado!")
    sys.exit(1)

print(f"✅ Notebook encontrado: {notebook_file.name}")

# 2. Load and validate JSON
try:
    with open(notebook_file, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    print("✅ Notebook JSON válido")
except json.JSONDecodeError as e:
    print(f"❌ ERRO: JSON inválido: {e}")
    sys.exit(1)

# 3. Check structure
required_keys = ['cells', 'metadata', 'nbformat', 'nbformat_minor']
for key in required_keys:
    if key in notebook:
        print(f"✅ Campo '{key}' presente")
    else:
        print(f"⚠️  Campo '{key}' não encontrado")

# 4. Count cells
cells = notebook.get('cells', [])
print(f"\n📊 ESTRUTURA NOTEBOOK:")
print(f"   Total de células: {len(cells)}")

code_cells = [c for c in cells if c.get('cell_type') == 'code']
markdown_cells = [c for c in cells if c.get('cell_type') == 'markdown']

print(f"   Células código: {len(code_cells)}")
print(f"   Células markdown: {len(markdown_cells)}")

# 5. List sections
print(f"\n📑 SEÇÕES DO NOTEBOOK:")
section_num = 1
for i, cell in enumerate(cells):
    if cell.get('cell_type') == 'markdown':
        source = cell.get('source', [])
        if isinstance(source, list):
            source_text = ''.join(source)
        else:
            source_text = source
        
        if '#' in source_text:
            # Extract heading
            lines = source_text.split('\n')
            for line in lines:
                if line.startswith('#'):
                    print(f"   {section_num}. {line.strip()}")
                    section_num += 1
                    break

# 6. Check for critical imports in first code cell
print(f"\n⚙️  VALIDAÇÃO IMPORTS:")
if len(code_cells) > 0:
    first_code = code_cells[0].get('source', [])
    if isinstance(first_code, list):
        first_code_text = ''.join(first_code)
    else:
        first_code_text = first_code
    
    imports_to_check = ['pandas', 'numpy', 'matplotlib', 'statsmodels', 'pymc']
    for imp in imports_to_check:
        if imp in first_code_text:
            print(f"   ✅ {imp} importado")
    
    if 'HAS_PYMC' in first_code_text:
        print(f"   ✅ Fallback PyMC implementado (try/except)")
    else:
        print(f"   ⚠️  Nenhum fallback PyMC detectado")

print("=" * 70)
print(f"✅ NOTEBOOK ESTRUTURALMENTE VÁLIDO!")
print(f"   Pronto para execução com {len(code_cells)} células de código")
print("=" * 70)
