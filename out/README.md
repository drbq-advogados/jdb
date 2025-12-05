# 🎲 Landing Page — JDB Análise de Probabilidades

Página estática com resultados das análises, probabilidades de dezenas e recomendações de jogos.

## 📋 Arquivos

- `landing.html` — Página HTML principal
- `styles.css` — Estilos (responsivo, clean design)
- `app.js` — JavaScript que carrega e renderiza os dados
- `landing_data.js` — **Gerado automaticamente** com dados do relatório/cache

## 🚀 Como usar

### 1. Gerar dados (se precisar atualizar)

```bash
.\.venv\Scripts\python.exe generate_landing_data.py
```

Isso cria/atualiza `web/landing_data.js` a partir de:
- `relatorio_analise_probabilidades.json` (se existir), ou
- `cache_results.json` (fallback)

### 2. Servir localmente

#### Opção A: Python (recomendado)
```bash
cd web
..\.venv\Scripts\python.exe -m http.server 8000
```
Depois abra: **http://127.0.0.1:8000/landing.html**

#### Opção B: Abrir direto (sem servidor)
Duplo-clique em `web/landing.html` — funciona também, mas com limitações CORS se precisar carregar recursos.

### 3. Deploy

Para colocar em produção (ex: GitHub Pages, Netlify):
1. Copie pasta `web/` para seu servidor
2. Execute `generate_landing_data.py` para gerar dados atualizados
3. Suba os arquivos

## 📊 Funcionalidades

- ✅ Resumo de qualidade de dados
- ✅ Top 12 dezenas por probabilidade
- ✅ 3 estratégias de jogos: Conservador, Agressivo, Diversificado
- ✅ Link para baixar relatório JSON completo
- ✅ Responsive (mobile-friendly)
- ✅ Sem dependências externas (vanilla HTML/CSS/JS)

## 🔧 Customização

Editar `styles.css` para mudar cores, fontes, layout:
- `--accent` — cor principal (azul)
- `--bg` — fundo da página
- `--card` — fundo dos cards

Editar `landing.html` para mudar layout ou adicionar seções.

---

**Gerado**: 2025-12-03
**Status**: Production-ready ✅
