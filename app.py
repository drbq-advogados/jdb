# app.py — Sistema completo: coleta 1 fonte, análise estatística e dashboard
# Requisitos: ver requirements.txt
import os
import re
import time
import json
import requests
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import random
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from scipy.stats import chisquare
from dotenv import load_dotenv
time.sleep(random.uniform(0.6, 2.2))

load_dotenv()

logging.basicConfig(filename="output/system.log", level=logging.INFO)

# -----------------------
# CONFIGURAÇÃO
# -----------------------
st.set_page_config(
    page_title="JDB Analise",
    layout="wide",
    page_icon="🎲"
)

CACHE_FILE = "cache_results.json"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
REQUEST_TIMEOUT = 12
DEFAULT_TTL_MIN = int(os.environ.get("SCRAPER_TTL_MIN", "10"))

PROXIES = os.environ.get("SCRAPER_PROXY_LIST", "")
PROXIES = [p.strip() for p in PROXIES.split(",") if p.strip()]

# -----------------------
# FONTES
# -----------------------
SOURCES = [
    {
        "key": "pernambucoaval",
        "name": "pernambucoaval (vitaldata)",
        "url": "https://pernambucoaval.vitaldata.com.br/",
        "selectors": ["table tbody tr", ".resultados tr", ".entry-content tr"]
    }
]

ANIMAIS = {
    1:'Avestruz',2:'Águia',3:'Burro',4:'Borboleta',5:'Cachorro',6:'Cabra',7:'Carneiro',8:'Camelo',9:'Cobra',10:'Coelho',
    11:'Cavalo',12:'Elefante',13:'Galo',14:'Gato',15:'Jacaré',16:'Leão',17:'Macaco',18:'Porco',19:'Pavão',20:'Peru',
    21:'Touro',22:'Tigre',23:'Urso',24:'Veado',25:'Vaca'
}

# -----------------------
# UTILITÁRIOS
# -----------------------
re_milhar = re.compile(r"\b(\d{4})\b")

def fetch_text(url, proxy=None):
    """Requisição HTTP com fallback proxy"""
    try:
        kwargs = {"headers": HEADERS, "timeout": REQUEST_TIMEOUT}
        if proxy:
            kwargs["proxies"] = {"http": proxy, "https": proxy}
        r = requests.get(url, **kwargs)
        r.raise_for_status()
        return r.text
    except:
        return None

def extract_milhars_from_text(text):
    """Extrai números de 4 dígitos de texto"""
    found = re_milhar.findall(text or "")
    return list(dict.fromkeys(found))  # remove duplicados preservando ordem

def dezena_de_milhar(milhar):
    return int(str(milhar)[-2:]) % 100

def grupo_de_dezena(dez):
    dez = int(dez) % 100
    if dez == 0: return 25
    return ((dez-1)//4) + 1

def parse_with_selectors(html, selectors):
    soup = BeautifulSoup(html, "lxml")
    for sel in selectors:
        try:
            els = soup.select(sel)
            rows = [e.get_text(" ", strip=True) for e in els if e.get_text(strip=True)]
            if rows: return rows
        except: 
            continue
    return None

# -----------------------
# SCRAPER
# -----------------------
def scrape_source(src, proxies=[]):
    """Coleta uma fonte com fallback de proxies"""
    html = fetch_text(src["url"])
    if html:
        rows = parse_with_selectors(html, src.get("selectors",[])) or []
        mils = [m for r in rows for m in re_milhar.findall(r)]
        if mils: return {"source": src["key"], "url": src["url"], "milhares": list(dict.fromkeys(mils))}
        mils = extract_milhars_from_text(html)
        if mils: return {"source": src["key"], "url": src["url"], "milhares": mils}
    # fallback proxies
    for p in proxies:
        html = fetch_text(src["url"], proxy=p)
        if html:
            rows = parse_with_selectors(html, src.get("selectors",[])) or []
            mils = [m for r in rows for m in re_milhar.findall(r)]
            if mils: return {"source": src["key"], "url": src["url"], "milhares": list(dict.fromkeys(mils))}
            mils = extract_milhars_from_text(html)
            if mils: return {"source": src["key"], "url": src["url"], "milhares": mils}
    return {"source": src["key"], "url": src["url"], "milhares": []}

def unify_by_vote(results_list):
    """Unifica resultados de múltiplas fontes por votação"""
    cand_counts = {}
    for res in results_list:
        for m in res.get("milhares",[]):
            cand_counts.setdefault(m, set()).add(res["source"])
    confirmed = sorted(
        [{"milhar": m, "sources": list(sources), "count": len(sources)} for m,sources in cand_counts.items()],
        key=lambda x:(-x["count"], x["milhar"])
    )
    if not any(c["count"]>=2 for c in confirmed):
        seq=[]
        for res in results_list:
            for m in res.get("milhares",[]):
                if m not in seq: seq.append(m)
        return seq
    return [c["milhar"] for c in confirmed]

# -----------------------
# ANÁLISE
# -----------------------
def make_dataframe_from_milhars(milhars):
    rows=[]
    for idx,m in enumerate(milhars):
        dez = dezena_de_milhar(m)
        grp = grupo_de_dezena(dez)
        animal = ANIMAIS.get(grp,"")
        rows.append({"idx": idx+1, "milhar": str(m).zfill(4), "dezena": dez, "grupo": grp, "animal": animal})
    return pd.DataFrame(rows)

def frequency_dezenas(df):
    cnt = df["dezena"].value_counts().reindex(range(0,100), fill_value=0)
    cnt.index.name="dezena"
    return cnt

def group_counts_from_dezena(counts):
    grp = pd.Series(0,index=range(1,26),dtype=int)
    for dez,c in counts.items(): grp[grupo_de_dezena(dez)] += int(c)
    grp.index.name="grupo"
    return grp

def chi2_test(counts):
    obs = counts.values
    exp = np.ones_like(obs) * obs.sum()/len(obs)
    stat, p = chisquare(obs, f_exp=exp)
    return stat, p

def bayesian_dirichlet_predictive(counts, alpha0=1.0):
    N = counts.sum()
    alpha = alpha0 + counts
    denom = 100*alpha0 + N
    return alpha/denom

# -----------------------
# CACHE
# -----------------------
def load_cache():
    if not os.path.exists(CACHE_FILE): return {}
    try:
        with open(CACHE_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_cache(obj):
    with open(CACHE_FILE,"w",encoding="utf-8") as f:
        json.dump(obj,f,ensure_ascii=False,indent=2)

# -----------------------
# ORQUESTRAÇÃO
# -----------------------
def orchestrate(force=False, ttl_min=DEFAULT_TTL_MIN, proxies=[]):
    cache = load_cache()
    now = time.time()
    if cache and not force and (now - cache.get("fetched_at",0)) < ttl_min*60:
        return cache.get("payload"), True
    results = [scrape_source(src, proxies=proxies) for src in SOURCES]
    unified_milhars = unify_by_vote(results)
    df = make_dataframe_from_milhars(unified_milhars)
    counts = frequency_dezenas(df)
    groups = group_counts_from_dezena(counts)
    chi2_stat, chi2_p = chi2_test(counts)
    pred = bayesian_dirichlet_predictive(counts)
    payload = {
        "fetched_at": datetime.utcnow().isoformat(),
        "sources_raw": results,
        "unified_milhars": unified_milhars,
        "table": df.to_dict(orient="records"),
        "counts_dezena": counts.to_dict(),
        "counts_grupos": groups.to_dict(),
        "chi2": {"stat": float(chi2_stat), "p": float(chi2_p)},
        "predictive_probs": pred.tolist()
    }
    save_cache({"fetched_at": now, "payload": payload})
    return payload, False

# -----------------------
# RECOMENDADOR
# -----------------------
def generate_games_from_probs(pred_probs, n=6, payout=70.0):
    s = pd.Series(pred_probs, index=range(0,100))
    top = s.nlargest(n).index.tolist()
    low = s.nsmallest(n).index.tolist()
    expected = payout * s - (1 - s)
    top_er = expected.nlargest(n).index.tolist()
    return {"Conservador": top, "Agressivo": top_er, "Diversificado": low}

# -----------------------
# STREAMLIT UI
# -----------------------
st.title("🎲 JDB Análise & Sistema 🎲")
st.markdown("Coleta de  fontes com fallback, análise estatística e probabilidades preditivas (Dirichlet).")

# Sidebar
st.sidebar.header("Controles")
force = st.sidebar.button("🔄 Atualizar agora (forçar)")
ttl = st.sidebar.number_input("Cache TTL (minutos)", min_value=1, max_value=1440, value=DEFAULT_TTL_MIN)
use_proxies = st.sidebar.checkbox("Usar proxies", value=False)
proxy_input = st.sidebar.text_area("Lista de proxies (coma-separado)", value=",".join(PROXIES))
n_dezenas = st.sidebar.number_input("Quantas dezenas por jogo", min_value=1, max_value=10, value=6)

proxies = [p.strip() for p in proxy_input.split(",") if p.strip()] if use_proxies else []

with st.spinner("Executando coleta/análise..."):
    payload, from_cache = orchestrate(force=force, ttl_min=int(ttl), proxies=proxies)

if not payload:
    st.error("Nenhuma fonte retornou resultados.")
    st.stop()

st.markdown(f"**Atualizado**: {payload['fetched_at']} (cache: {'sim' if from_cache else 'não'})")
st.markdown("---")

df_table = pd.DataFrame(payload["table"])
if df_table.empty:
    st.warning("Nenhum resultado unificado.")
else:
    st.subheader("Resultados Unificados")
    st.dataframe(df_table)

# Charts
counts_df = pd.DataFrame({"dezena": range(0,100), "freq": list(payload["counts_dezena"].values())})
groups_df = pd.DataFrame({"grupo": range(1,26), "freq": list(payload["counts_grupos"].values())})

col1,col2 = st.columns([3,2])
with col1:
    st.subheader("Distribuição por Dezena")
    chart = alt.Chart(counts_df).mark_bar().encode(
        x=alt.X("dezena:O"),
        y=alt.Y("freq:Q"),
        tooltip=["dezena","freq"]
    ).properties(height=320)
    st.altair_chart(chart, use_container_width=True)
with col2:
    st.subheader("Frequência por Grupo")
    st.dataframe(groups_df)

# Estatística
st.markdown("---")
st.subheader("Testes estatísticos")
st.write(f"Qui-quadrado: estatística = {payload['chi2']['stat']:.2f}, p-value = {payload['chi2']['p']:.4g}")

# Probabilidades preditivas
pred = np.array(payload["predictive_probs"], dtype=float)
pred_df = pd.DataFrame({"dezena": range(0,100), "prob": pred})
top_pred = pred_df.nlargest(12, "prob")
st.subheader("Top probabilidades preditivas (Dirichlet)")
st.dataframe(top_pred)

chart2 = alt.Chart(top_pred).mark_bar().encode(
    x=alt.X("dezena:O"),
    y=alt.Y("prob:Q"),
    tooltip=["dezena","prob"]
).properties(height=240)
st.altair_chart(chart2, use_container_width=True)

# Jogos recomendados
games = generate_games_from_probs(pred, n=int(n_dezenas))
st.markdown("---")
st.subheader("🎯 Jogos recomendados")
for k,v in games.items():
    st.markdown(f"**{k}** — " + "  ".join([f"`{int(x):02d}`" for x in v]))

# Export CSV
st.markdown("---")
if st.button("⬇ Exportar resultados unificados (CSV)"):
    path = os.path.join(OUTPUT_DIR, f"unified_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv")
    df_table.to_csv(path, index=False)
    st.success(f"Exportado: {path}")

if st.button("⬇ Exportar probabilidades (CSV)"):
    pred_df.to_csv(os.path.join(OUTPUT_DIR, "predictive_probs.csv"), index=False)
    st.success("Exportado: output/predictive_probs.csv")

# Fontes brutas
st.markdown("### Fontes brutas")
for r in payload["sources_raw"]:
    st.write(f"- {r['source']}: {len(r.get('milhares',[]))} milhares encontrados — {r['url']}")

st.markdown("---")
st.caption("Sistema gerado: coleta + análise — use com responsabilidade.")
