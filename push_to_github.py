"""
Upload de repositório para GitHub via REST API + PAT (100% Python, sem Git CLI).
Simula um repositório git local e faz upload via GitHub API.
"""

import os
import sys
import json
import base64
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

def upload_to_github():
    """Faz upload dos arquivos via GitHub REST API."""
    
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise SystemExit('GITHUB_TOKEN not set. Set it in PowerShell with `$env:GITHUB_TOKEN = "<YOUR_TOKEN>"` or configure it as a repository secret named `GITHUB_TOKEN`.')
    owner = "drbq-advogados"
    repo = "jdb"
    branch = "main"
    
    repo_dir = Path.cwd()
    
    print("=" * 60)
    print("JDB - Upload via GitHub API (sem Git CLI)")
    print("=" * 60)
    
    # Lista de arquivos a ignorar
    ignore_patterns = ['.venv', '__pycache__', '.git', '.egg-info', '.pytest_cache', '.ipynb_checkpoints', '*.pyc']
    
    def should_ignore(path):
        path_str = str(path)
        for pattern in ignore_patterns:
            if pattern in path_str:
                return True
        return False
    
    # Coletar arquivos
    files_to_upload = []
    for root, dirs, files in os.walk(repo_dir):
        # Filtrar diretórios
        dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]
        
        for file in files:
            file_path = Path(root) / file
            if not should_ignore(file_path):
                rel_path = file_path.relative_to(repo_dir)
                files_to_upload.append((file_path, rel_path))
    
    print(f"Encontrados {len(files_to_upload)} arquivos para upload")
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # Fazer upload de cada arquivo
    success_count = 0
    for file_path, rel_path in files_to_upload:
        try:
            # Ler arquivo
            if file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.bin', '.exe']:
                with open(file_path, 'rb') as f:
                    content = base64.b64encode(f.read()).decode()
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = base64.b64encode(f.read().encode()).decode()
            
            # Preparar request
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{str(rel_path).replace(chr(92), '/')}"
            data = {
                "message": f"Add {rel_path}",
                "content": content,
                "branch": branch
            }
            
            req = Request(url, data=json.dumps(data).encode(), headers=headers, method='PUT')
            
            try:
                urlopen(req, timeout=10)
                success_count += 1
                print(f"  ✓ {rel_path}")
            except HTTPError as e:
                if e.code == 422:
                    # Arquivo pode já existir, tentar GET primeiro
                    get_req = Request(url, headers=headers, method='GET')
                    try:
                        urlopen(get_req)
                        print(f"  ~ {rel_path} (já existe)")
                        success_count += 1
                    except:
                        print(f"  ✗ {rel_path} (erro {e.code})")
                else:
                    print(f"  ✗ {rel_path} (erro {e.code})")
        
        except Exception as e:
            print(f"  ✗ {rel_path} (erro: {e})")
    
    print("\n" + "=" * 60)
    print(f"✓ Upload concluído: {success_count}/{len(files_to_upload)} arquivos")
    print("=" * 60)
    print("\nPróximas etapas:")
    print(f"1. Verifique o repositório em: https://github.com/{owner}/{repo}")
    print("2. Aguarde o GitHub Actions executar (.github/workflows/deploy.yml)")
    print("3. Ative GitHub Pages em Settings → Pages")
    print(f"4. Seu site estará em: https://{owner}.github.io/{repo}/landing.html")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    upload_to_github()
