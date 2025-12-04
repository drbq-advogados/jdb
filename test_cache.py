#!/usr/bin/env python
# Test cache_results.json integrity

import json
import sys
from pathlib import Path

cache_file = Path("cache_results.json")

print("=" * 70)
print("🔍 TESTE DE CACHE - JDB PROJECT")
print("=" * 70)

# 1. Check file exists
if not cache_file.exists():
    print(f"❌ ERRO: {cache_file} não encontrado!")
    sys.exit(1)

print(f"✅ Arquivo encontrado: {cache_file.name} ({cache_file.stat().st_size} bytes)")

# 2. Load and validate JSON
try:
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    print("✅ JSON válido e parseable")
except json.JSONDecodeError as e:
    print(f"❌ ERRO: JSON inválido: {e}")
    sys.exit(1)

# 3. Check structure
required_keys = ['fetched_at', 'payload']
for key in required_keys:
    if key in cache:
        print(f"✅ Campo obrigatório '{key}' presente")
    else:
        print(f"❌ Campo obrigatório '{key}' FALTANDO")
        sys.exit(1)

payload = cache.get('payload', {})

# 4. Check payload structure
payload_keys = ['fetched_at', 'sources_raw', 'unified_milhars', 'table', 'counts_dezena', 'counts_grupos', 'chi2', 'predictive_probs']
for key in payload_keys:
    if key in payload:
        print(f"✅ Payload.{key} presente")
    else:
        print(f"⚠️  Payload.{key} não encontrado")

# 5. Data statistics
table = payload.get('table', [])
unified = payload.get('unified_milhars', [])

print(f"\n📊 ESTATÍSTICAS:")
print(f"   Timestamp: {cache.get('fetched_at')}")
print(f"   Milhares únicos: {len(unified)}")
print(f"   Tabela linhas: {len(table)}")

# 6. Verify data quality
if len(unified) > 0:
    print(f"   Min/Max milhar: {min(unified)}/{max(unified)}")
    print(f"   ✅ Dados de milhares válidos")
else:
    print(f"   ❌ Nenhum milhar encontrado!")
    sys.exit(1)

# 7. Chi-square stats
chi2_data = payload.get('chi2', {})
if chi2_data:
    stat = chi2_data.get('statistic')
    p_value = chi2_data.get('p_value')
    print(f"\n📈 CHI-SQUARE TEST:")
    print(f"   Statistic: {stat}")
    print(f"   P-value: {p_value}")
    if p_value and p_value > 0.05:
        print(f"   ✅ Dados UNIFORMES (p > 0.05)")
    else:
        print(f"   ⚠️  Dados podem NÃO ser uniformes")
else:
    print(f"⚠️  Chi-square stats não encontrados")

print("=" * 70)
print("✅ CACHE VALIDADO COM SUCESSO!")
print("=" * 70)
