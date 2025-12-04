from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import json
import pandas as pd

from research_framework_starter import demo_workflow, monte_carlo_final_balances, mt19937, lcg, ensure_output_dir

app = FastAPI()
templates = Jinja2Templates(directory="templates")
OUTPUT_DIR = ensure_output_dir("output")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": ""})

@app.post("/run_demo", response_class=HTMLResponse)
def run_demo(request: Request):
    try:
        demo_workflow(output_dir=OUTPUT_DIR)
        message = "✅ Demo executado com sucesso! Resultados em 'output/'"
    except Exception as e:
        message = f"❌ Erro: {e}"
    return templates.TemplateResponse("index.html", {"request": request, "message": message})

@app.post("/run_mc", response_class=HTMLResponse)
def run_mc(request: Request, n_rounds: int = Form(...), n_sims: int = Form(...)):
    try:
        finals = monte_carlo_final_balances(lambda n: mt19937(n), {}, n_rounds=n_rounds, n_sims=n_sims, payout=18.0)
        df = pd.DataFrame({"final_balances": finals})
        df.to_csv(os.path.join(OUTPUT_DIR, "mc_final_balances.csv"), index=False)
        message = f"✅ Monte Carlo executado! CSV gerado em 'output/mc_final_balances.csv'"
    except Exception as e:
        message = f"❌ Erro: {e}"
    return templates.TemplateResponse("index.html", {"request": request, "message": message})
