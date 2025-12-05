"""
Gera `web/landing_data.js` com dados completos para landing page.
Extrai: ranking de dezenas, estatísticas por grupo, probabilidades, etc.

Uso:
  .\.venv\Scripts\python.exe generate_landing_data.py

Resultado: `web/landing_data.js` criado/atualizado.
"""
import json
from pathlib import Path
from datetime import datetime

ANIMAIS = {
    1:'Avestruz',2:'Águia',3:'Burro',4:'Borboleta',5:'Cachorro',6:'Cabra',7:'Carneiro',8:'Camelo',9:'Cobra',10:'Coelho',
    11:'Cavalo',12:'Elefante',13:'Galo',14:'Gato',15:'Jacaré',16:'Leão',17:'Macaco',18:'Porco',19:'Pavão',20:'Peru',
    21:'Touro',22:'Tigre',23:'Urso',24:'Veado',25:'Vaca'
}

root = Path(__file__).parent
cache_path = root / 'cache_results.json'
out_js = root / 'web' / 'landing_data.js'

cache = {}
if cache_path.exists():
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)

payload = cache.get('payload', {})
table = payload.get('table', [])
counts_dezena = payload.get('counts_dezena', {})
counts_grupo = payload.get('counts_grupos', {})
chi2_data = payload.get('chi2', {})

# Calcular probabilidades
total_obs = len(table)
probs_dezena = [counts_dezena.get(str(i), counts_dezena.get(i, 0)) / total_obs if total_obs > 0 else 1.0/100 for i in range(100)]

# Ranking de dezenas
ranking_dezenas = []
for dez in range(100):
    ranking_dezenas.append({
        'dezena': str(dez).zfill(2),
        'frequencia': int(counts_dezena.get(str(dez), counts_dezena.get(dez, 0))),
        'probabilidade': float(probs_dezena[dez]),
        'percentual': round(probs_dezena[dez] * 100, 2)
    })
ranking_dezenas.sort(key=lambda x: x['frequencia'], reverse=True)

# Top 10 e Bottom 5
top_10_dezenas = ranking_dezenas[:10]
bottom_5_dezenas = ranking_dezenas[-5:]

# Estatísticas por grupo (animal)
grupos_stats = []
for grupo in range(1, 26):
    freq = int(counts_grupo.get(str(grupo), counts_grupo.get(grupo, 0)))
    prob = freq / total_obs if total_obs > 0 else 1.0/25
    animal = ANIMAIS.get(grupo, f'Grupo {grupo}')
    grupos_stats.append({
        'grupo': grupo,
        'animal': animal,
        'frequencia': freq,
        'probabilidade': float(prob),
        'percentual': round(prob * 100, 2)
    })
grupos_stats.sort(key=lambda x: x['frequencia'], reverse=True)

# Estatísticas gerais
resumo = {
    'total_sorteios': total_obs,
    'data_coleta': payload.get('fetched_at', ''),
    'dezena_mais_sorteada': ranking_dezenas[0] if ranking_dezenas else {},
    'dezena_menos_sorteada': ranking_dezenas[-1] if ranking_dezenas else {},
    'grupo_mais_sorteado': grupos_stats[0] if grupos_stats else {},
    'grupo_menos_sorteado': grupos_stats[-1] if grupos_stats else {},
    'frequencia_media': round(total_obs / 100, 2),
    'chi2_teste': {
        'estatistica': round(float(chi2_data.get('stat', 0)), 4),
        'p_value': round(float(chi2_data.get('p', 1)), 6),
        'resultado': 'Uniforme' if float(chi2_data.get('p', 1)) > 0.05 else 'Não uniforme'
    }
}

# Recomendações de jogos
top_6 = ranking_dezenas[:6]
top_6_dezenas = [item['dezena'] for item in top_6]

bottom_6 = ranking_dezenas[-6:]
bottom_6_dezenas = [item['dezena'] for item in bottom_6]

mid_range = ranking_dezenas[45:51]
mid_dezenas = [item['dezena'] for item in mid_range]

recomendacoes = {
    'conservador': {
        'titulo': 'Conservador',
        'descricao': 'Top 6 dezenas mais sortidas',
        'dezenas': top_6_dezenas,
        'estrategia': 'Apostar nas dezenas com maior frequência histórica'
    },
    'diversificado': {
        'titulo': 'Diversificado',
        'descricao': 'Dezenas com freq. média',
        'dezenas': mid_dezenas,
        'estrategia': 'Distribuir risco entre dezenas com freq. moderada'
    },
    'contrarian': {
        'titulo': 'Contrarian',
        'descricao': 'Bottom 6 dezenas (menor freq)',
        'dezenas': bottom_6_dezenas,
        'estrategia': 'Apostar em dezenas com menor frequência (possível regressão à média)'
    }
}

# Compilar dados
data = {
    'generated_at': datetime.utcnow().isoformat(),
    'resumo': resumo,
    'ranking_dezenas': ranking_dezenas,
    'top_10': top_10_dezenas,
    'bottom_5': bottom_5_dezenas,
    'grupos': grupos_stats,
    'probabilidades': probs_dezena,
    'recomendacoes': recomendacoes
}

# write JS
js = 'window.LANDING_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + ';\n'
out_js.parent.mkdir(parents=True, exist_ok=True)
with open(out_js, 'w', encoding='utf-8') as f:
    f.write(js)

print(f'Wrote {out_js}')
print(f'  - Total de sorteios: {resumo["total_sorteios"]}')
print(f'  - Dezena mais sorteada: {resumo["dezena_mais_sorteada"].get("dezena")} ({resumo["dezena_mais_sorteada"].get("frequencia")}x)')
print(f'  - Grupo mais sorteado: {resumo["grupo_mais_sorteado"].get("animal")}')
print(f'  - Chi-square p-value: {resumo["chi2_teste"]["p_value"]}')

# --- Build conditional predictive probabilities by group (if metadata present)
table_rows = table
known_cols = {'idx', 'milhar', 'dezena', 'grupo', 'animal'}
group_keys = set()
for row in table_rows:
    for k in row.keys():
        if k not in known_cols:
            group_keys.add(k)

predictive_by_group = {}
for gk in sorted(group_keys):
    # collect unique values
    values = sorted({row.get(gk) for row in table_rows if gk in row})
    mapping = {}
    for val in values:
        subset = [r for r in table_rows if r.get(gk) == val]
        total = len(subset)
        counts = [0] * 100
        for r in subset:
            try:
                d = int(r.get('dezena')) if r.get('dezena') is not None else None
            except Exception:
                d = None
            if d is not None and 0 <= d < 100:
                counts[d] += 1
        if total > 0:
            probs = [c / total for c in counts]
        else:
            probs = [1.0 / 100] * 100
        mapping[str(val)] = {
            'count': total,
            'probs': probs,
            'top': sorted([
                {'dezena': str(i).zfill(2), 'count': counts[i], 'prob': probs[i]} for i in range(100)
            ], key=lambda x: x['count'], reverse=True)[:10]
        }
    predictive_by_group[gk] = mapping

if predictive_by_group:
    # merge into data and rewrite JS with the new field
    data['predictive_by_group'] = predictive_by_group
    js = 'window.LANDING_DATA = ' + json.dumps(data, ensure_ascii=False, indent=2) + '\n;'
    with open(out_js, 'w', encoding='utf-8') as f:
        f.write(js)
    print(f'Added predictive_by_group keys: {list(predictive_by_group.keys())}')
