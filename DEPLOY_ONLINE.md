# 🚀 Colocar Landing Page Online

## Opção 1: GitHub Pages + Vercel (RECOMENDADO - 5 minutos)

### Passo 1: Clonar repositório do GitHub
1. Instale Git: https://git-scm.com/download/win
2. Abra PowerShell e execute:
```powershell
cd "c:\Users\Matrix\Downloads\Sistema JDB\jdb"
git config --global user.email "seu_email@gmail.com"
git config --global user.name "Seu Nome"
```

### Passo 2: Criar repositório no GitHub
1. Vá para https://github.com/new
2. Preencha:
   - **Repository name**: `jdb` (ou outro nome)
   - **Description**: "JDB - Análise de Probabilidades"
   - **Public**: Sim
3. Clique **Create repository**

### Passo 3: Enviar código
```powershell
cd "c:\Users\Matrix\Downloads\Sistema JDB\jdb"
git init
git add .
git commit -m "Initial commit: Landing page JDB"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/jdb.git
git push -u origin main
```

### Passo 4: Deploy no Vercel
1. Vá para https://vercel.com/new
2. Clique **Import Git Repository**
3. Conecte sua conta GitHub
4. Selecione o repositório `jdb`
5. Em **Project Settings**:
   - **Framework**: Selecione `Other`
   - **Build Command**: `python generate_landing_data.py`
   - **Output Directory**: `web`
6. Clique **Deploy**

✅ **Pronto!** A landing page estará online em: `https://seuprojetojdb.vercel.app/landing.html`

---

## Opção 2: GitHub Pages (GRATUITO, sem Vercel)

Após fazer os passos 1-3 acima:

1. Vá para o repositório no GitHub
2. Clique em **Settings** → **Pages**
3. **Source**: Selecione `main` branch, pasta `web/`
4. Clique **Save**

✅ A página estará em: `https://seu-usuario.github.io/jdb/landing.html`

---

## Opção 3: Netlify (SIMPLES)

1. Vá para https://netlify.com
2. Clique **Add new site** → **Import an existing project**
3. Conecte GitHub
4. Selecione repositório `jdb`
5. Em **Build settings**:
   - **Build command**: `python generate_landing_data.py`
   - **Publish directory**: `web`
6. Clique **Deploy**

✅ Seu site estará online em: `https://seu-site.netlify.app`

---

## 📊 Comparação

| Plataforma | Preço | Facilidade | Velocidade | Recomendação |
|-----------|-------|-----------|-----------|--------------|
| **Vercel** | Grátis | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 👍 MELHOR |
| **GitHub Pages** | Grátis | ⭐⭐⭐ | ⭐⭐⭐ | ✅ Grátis |
| **Netlify** | Grátis | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Fácil |

---

## 🔄 Atualizar dados depois

Sempre que quiser atualizar os dados da landing page:

```powershell
# Gerar novos dados
.\.venv\Scripts\python.exe generate_landing_data.py

# Fazer commit e push
git add web/landing_data.js
git commit -m "Atualizar dados de análise"
git push
```

A plataforma (Vercel/Netlify/GitHub Pages) fará redeploy automaticamente!

---

## ❓ Dúvidas?

- **Git não instala**: https://git-scm.com/download/win
- **GitHub não carrega**: Aguarde ~2 minutos após push
- **Vercel mais rápido**: Recomendado para production
