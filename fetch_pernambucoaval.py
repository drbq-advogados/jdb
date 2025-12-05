"""Fetch and extract metadata (hora, local, tipo) from pernambucoaval.vitaldata.com.br

This script attempts several parsing strategies to find per-milhar metadata
and will update `cache_results.json` by adding `hora`, `local`, `tipo` fields
to the matching rows in `payload.table` when found.

Usage:
  .\.venv\Scripts\python.exe fetch_pernambucoaval.py

The script creates a backup `cache_results.json.bak` before modifying.
"""
import re
import json
import time
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup


URL = 'https://pernambucoaval.vitaldata.com.br/'


def load_cache(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def save_cache(path: Path, data):
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_html(url: str, timeout=15):
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_metadata_for_milhar(html_text: str, milhar: str):
    """Heuristic extraction: find the first occurrence of milhar and look
    for patterns for time, local, and tipo in nearby text.
    """
    # normalize
    text = html_text
    idx = text.find(milhar)
    if idx == -1:
        return {}

    window = text[max(0, idx - 400): idx + 400]

    meta = {}

    # time patterns like 13:45 or 1:23
    tmatch = re.search(r'(\b\d{1,2}:\d{2}\b)', window)
    if tmatch:
        meta['hora'] = tmatch.group(1)

    # look for explicit labels Local: or Localidade:
    lmatch = re.search(r'(?:Local(?:idade)?|Local):?\s*([^\n<]{2,120})', window, flags=re.IGNORECASE)
    if lmatch:
        meta['local'] = clean_local_string(lmatch.group(1))
    else:
        # fallback: look for "- CITY/PLACE" patterns after milhar
        fmatch = re.search(r'%s\s*[-–—]\s*([^\n<]{2,120})' % re.escape(milhar), window)
        if fmatch:
            meta['local'] = clean_local_string(fmatch.group(1))

    # tipo: look for labels Tipo:, Modalidade:, Sorteio:
    tm = re.search(r'(?:Tipo|Modalidade|Sorteio|Extra[cç][aã]o):?\s*([^\n<]{2,60})', window, flags=re.IGNORECASE)
    if tm:
        meta['tipo'] = clean_tipo_string(tm.group(1))

    return meta


def clean_local_string(s: str) -> str:
    """Normalize/clean the detected local string.
    - remove repetitive fragments like 'Grupo 12345', 'AVAL', 'AVAL PERNAMBUCO'
    - trim and collapse whitespace
    - remove trailing artifacts like 'ID Milhar' or embedded dates
    """
    if not s:
        return s
    out = s
    # remove common noise patterns
    out = re.sub(r'Grupo\s*\d+', '', out, flags=re.IGNORECASE)
    out = re.sub(r'AVAL\s*PERNAMBUCO', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\bAVAL\b', '', out, flags=re.IGNORECASE)
    out = re.sub(r'PERNAMBUCO', '', out, flags=re.IGNORECASE)
    # remove embedded dates like 05/12/2025
    out = re.sub(r'\d{2}/\d{2}/\d{4}', '', out)
    # remove time artifacts
    out = re.sub(r'\b\d{1,2}:\d{2}\b', '', out)
    out = re.sub(r'PE\s*\d{1,2}:?\d{0,2}', '', out, flags=re.IGNORECASE)
    out = re.sub(r'ID\s*Milhar.*', '', out, flags=re.IGNORECASE)
    # remove punctuation at ends
    out = out.strip(' \t\n:-–—')
    # collapse multi spaces
    out = re.sub(r'\s{2,}', ' ', out)
    # final trim
    return out.strip()


def clean_tipo_string(s: str) -> str:
    if not s:
        return s
    out = s.strip()
    out = re.sub(r'\s{2,}', ' ', out)
    # canonicalize common keywords
    out_l = out.lower()
    if 'diurno' in out_l or 'manhã' in out_l or 'matut' in out_l:
        return 'Diurno'
    if 'vesp' in out_l or 'tarde' in out_l:
        return 'Vespertino'
    if 'noite' in out_l or 'noturno' in out_l:
        return 'Noturno'
    # fallback: try to infer from a time-like substring
    tm = re.search(r'(\d{1,2}):(\d{2})', out)
    if tm:
        hour = int(tm.group(1))
        if 5 <= hour < 12:
            return 'Diurno'
        if 12 <= hour < 18:
            return 'Vespertino'
        return 'Noturno'
    # fallback: return cleaned string with capitalization
    return out.title()


def infer_tipo_from_hora(hora: str) -> str:
    """Infer a broad period (Diurno/Vespertino/Noturno) from a time string like '11:00'."""
    if not hora:
        return None
    try:
        hh = int(str(hora).split(':')[0])
    except Exception:
        return None
    if 5 <= hh < 12:
        return 'Diurno'
    if 12 <= hh < 18:
        return 'Vespertino'
    return 'Noturno'


def try_parse_json_inside_scripts(soup: BeautifulSoup):
    """Try to find JSON blobs inside <script> tags that contain useful keys."""
    candidates = []
    for s in soup.find_all('script'):
        if not s.string:
            continue
        txt = s.string.strip()
        if 'milhar' in txt or 'milhares' in txt or 'table' in txt:
            # try to extract JSON
            try:
                # find first { ... } or [ ... ] block
                jtxt = re.search(r'({[\s\S]*})|([\[][\s\S]*[\]])', txt)
                if jtxt:
                    obj = json.loads(jtxt.group(0))
                    candidates.append(obj)
            except Exception:
                continue
    return candidates


def main():
    root = Path(__file__).parent
    cache_path = root / 'cache_results.json'
    if not cache_path.exists():
        print('cache_results.json not found in', root)
        return

    print('Fetching', URL)
    try:
        html = fetch_html(URL)
    except Exception as e:
        print('Error fetching site:', e)
        return

    soup = BeautifulSoup(html, 'lxml')

    # Try to identify structured entries on the page (table-like or cards)
    def find_structured_entries(soup):
        """Attempt to find structured blocks that contain milhar and metadata.
        Returns list of dicts {milhar:..., hora:..., local:..., tipo:...}
        """
        entries = []
        # find all elements that contain a 4-digit milhar pattern
        for el in soup.find_all(string=re.compile(r'\b\d{4}\b')):
            text = el.strip()
            m = re.search(r'\b(\d{4})\b', text)
            if not m:
                continue
            mil = m.group(1)
            # climb up to a reasonable ancestor to gather siblings
            ancestor = el.parent
            for _ in range(4):
                if ancestor is None:
                    break
                block_text = ' '.join(ancestor.stripped_strings)
                # if block contains labels like Hora, Local, Tipo then capture
                if re.search(r'Hora|Localidade|Local|Tipo|Modalidade|Sorteio', block_text, flags=re.IGNORECASE):
                    hora = None
                    local = None
                    tipo = None
                    # hora
                    th = re.search(r'\b(\d{1,2}:\d{2})\b', block_text)
                    if th:
                        hora = th.group(1)
                    lm = re.search(r'(?:Local(?:idade)?|Local):?\s*([^\n<]{2,120})', block_text, flags=re.IGNORECASE)
                    if lm:
                        local = clean_local_string(lm.group(1))
                    tm = re.search(r'(?:Tipo|Modalidade|Sorteio|Extra[cç][aã]o):?\s*([^\n<]{2,60})', block_text, flags=re.IGNORECASE)
                    if tm:
                        tipo = clean_tipo_string(tm.group(1))
                    entries.append({'milhar': mil, 'hora': hora, 'local': local, 'tipo': tipo})
                    break
                ancestor = ancestor.parent
        return entries

    structured = find_structured_entries(soup)
    if structured:
        # incorporate structured findings to speed up extraction
        struct_map = {e['milhar']: e for e in structured}
    else:
        struct_map = {}

    # --- New: parse explicit tables with class 'table' which contain structured rows
    def parse_tables_map(soup):
        mapping = {}
        tables = soup.find_all('table', class_='table')
        for table in tables:
            # header rows often contain a TH with date/group/time
            header_ths = table.find_all('th')
            header_text = ' '.join([h.get_text(separator=' ', strip=True) for h in header_ths[:2]])
            # try to extract time and local from header_text
            hora = None
            local = None
            # pattern: 05/12/2025 - Grupo 28482 AVAL PE 11:00 HS
            m = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*Grupo\s*(\d+)\s*(.*?)\s*(\d{1,2}:\d{2})\s*HS", header_text)
            if m:
                # date = m.group(1)
                # group = m.group(2)
                local_raw = m.group(3).strip()
                hora = m.group(4)
                local = clean_local_string(local_raw)
            else:
                # fallback: any time pattern
                th = re.search(r"(\d{1,2}:\d{2})", header_text)
                if th:
                    hora = th.group(1)

            # parse rows: expect rows with td: idx, milhar, grupo, descricao
            for tr in table.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) >= 2:
                    milhar = tds[1].get_text(strip=True)
                    entry = {}
                    if hora:
                        entry['hora'] = hora
                    if local:
                        entry['local'] = local
                    # tipo left as None unless found elsewhere
                    mapping[str(milhar)] = entry
        return mapping

    table_map = parse_tables_map(soup)
    # merge table_map into struct_map (table_map takes precedence)
    struct_map.update(table_map)

    # load cache
    cache = load_cache(cache_path)
    payload = cache.get('payload', {})
    table = payload.get('table', [])

    # list of milhares to search for (prefer unified_milhars)
    milhares = payload.get('unified_milhars') or []
    if not milhares:
        # try sources_raw[0].milhares
        sr = payload.get('sources_raw', [])
        if sr and isinstance(sr, list) and 'milhares' in sr[0]:
            milhares = sr[0].get('milhares', [])

    print('Found', len(milhares), 'milhares in cache; scanning HTML for metadata...')

    # Pre-parse JSON blobs in scripts (may contain structured data)
    json_candidates = try_parse_json_inside_scripts(soup)

    html_text = soup.get_text(separator=' ', strip=True)

    updated = 0
    for row in table:
        milhar = row.get('milhar')
        if not milhar:
            continue
        meta = {}

        # prefer structured extraction if available
        if str(milhar) in struct_map:
            m = struct_map.get(str(milhar), {})
            for k in ('hora', 'local', 'tipo'):
                if m.get(k):
                    meta[k] = m.get(k)

        # First, look into any JSON candidate objects for an entry matching milhar
        for obj in json_candidates:
            try:
                # search recursively for milhar
                jtxt = json.dumps(obj)
                if str(milhar) in jtxt:
                    # try to extract nearby fields for that milhar
                    m = extract_metadata_for_milhar(jtxt, str(milhar))
                    meta.update(m)
            except Exception:
                continue

        # second, use HTML text heuristics
        if not meta.get('hora') or not meta.get('local') or not meta.get('tipo'):
            m2 = extract_metadata_for_milhar(html_text, str(milhar))
            for k, v in m2.items():
                if v and not meta.get(k):
                    meta[k] = v

        # third, try element-based nearby search: find elements containing the milhar
        if not meta.get('hora') or not meta.get('local') or not meta.get('tipo'):
            el = soup.find(text=re.compile(re.escape(str(milhar))))
            if el:
                parent = el.parent
                snippet = ' '.join(parent.stripped_strings)
                m3 = extract_metadata_for_milhar(snippet, str(milhar))
                for k, v in m3.items():
                    if v and not meta.get(k):
                        meta[k] = v

        # If tipo not found, try to infer from hora
        if not meta.get('tipo') and meta.get('hora'):
            inferred = infer_tipo_from_hora(meta.get('hora'))
            if inferred:
                meta['tipo'] = inferred

        # normalize tipo if present
        if meta.get('tipo'):
            meta['tipo'] = clean_tipo_string(meta.get('tipo'))

        # attach found meta to row
        changed = False
        for k in ('hora', 'local', 'tipo'):
            if meta.get(k) is not None:
                if row.get(k) != meta.get(k):
                    row[k] = meta.get(k)
                    changed = True

        if changed:
            updated += 1

    if updated > 0:
        # backup
        bak = cache_path.with_suffix('.json.bak')
        try:
            cache_path.replace(bak)
            print('Backup written to', bak)
            # write modified cache to original path
            save_cache(cache_path, cache)
        except Exception:
            # fallback copy
            cache_path.with_suffix('.bak').write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
        # set fetched_at
        cache['fetched_at'] = time.time()
        if 'payload' in cache:
            cache['payload']['fetched_at'] = time.time()
        save_cache(cache_path, cache)
        print(f'Updated {updated} rows in cache_results.json')
    else:
        print('No metadata found or nothing to update.')


if __name__ == '__main__':
    main()
