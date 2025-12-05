"""Run the scraper and produce a short validation report.

Usage:
  .\.venv\Scripts\python.exe scraper_validation.py

Outputs a simple summary: counts of rows with hora/local/tipo and a CSV with
example rows where fields are missing or present.
"""
import json
from pathlib import Path
import csv
import subprocess
import sys

ROOT = Path(__file__).parent
CACHE = ROOT / 'cache_results.json'

def run_scraper():
    print('Running fetch_pernambucoaval.py...')
    subprocess.check_call([sys.executable, str(ROOT / 'fetch_pernambucoaval.py')])

def load_cache():
    with open(CACHE, 'r', encoding='utf-8') as f:
        return json.load(f)

def report(cache):
    table = cache.get('payload', {}).get('table', [])
    total = len(table)
    hora = sum(1 for r in table if r.get('hora'))
    local = sum(1 for r in table if r.get('local'))
    tipo = sum(1 for r in table if r.get('tipo'))

    print('Validation report:')
    print(f'  total rows: {total}')
    print(f'  rows with hora: {hora} ({hora/total:.1%})')
    print(f'  rows with local: {local} ({local/total:.1%})')
    print(f'  rows with tipo: {tipo} ({tipo/total:.1%})')

    # write CSV with examples of missing fields
    out = ROOT / 'scraper_report_examples.csv'
    keys = ['idx', 'milhar', 'dezena', 'grupo', 'animal', 'hora', 'local', 'tipo']
    with open(out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in table[:500]:
            row = {k: r.get(k, '') for k in keys}
            writer.writerow(row)
    print('Wrote examples to', out)

def main():
    run_scraper()
    cache = load_cache()
    report(cache)

if __name__ == '__main__':
    main()
