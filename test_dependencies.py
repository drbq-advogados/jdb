#!/usr/bin/env python
# Test all project dependencies

import sys

deps_to_test = [
    'streamlit',
    'pandas',
    'numpy',
    'requests',
    'bs4',
    'scipy',
    'altair',
    'dotenv',
    'statsmodels',
    'pymc'
]

print("=" * 60)
print("🧪 TESTE DE DEPENDÊNCIAS - JDB PROJECT")
print("=" * 60)

passed = 0
failed = 0
optional_failed = 0

for dep in deps_to_test:
    try:
        module = __import__(dep)
        version = getattr(module, '__version__', 'N/A')
        if dep in ['pymc', 'statsmodels']:
            print(f"✅ {dep:<20} {version} (OPCIONAL)")
        else:
            print(f"✅ {dep:<20} {version}")
        passed += 1
    except ImportError as e:
        if dep in ['pymc', 'statsmodels']:
            print(f"⚠️  {dep:<20} NOT INSTALLED (OPCIONAL)")
            optional_failed += 1
        else:
            print(f"❌ {dep:<20} MISSING (CRÍTICO)")
            failed += 1

print("=" * 60)
print(f"Resultados: ✅ {passed} OK | ⚠️  {optional_failed} Optional | ❌ {failed} Falhas")
print("=" * 60)

if failed > 0:
    print("\n🚨 ERRO: Dependências críticas faltando!")
    sys.exit(1)
else:
    print("\n✅ SUCESSO: Ambiente pronto para testes!")
    sys.exit(0)
