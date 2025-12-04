<#
PowerShell script: install_and_push.ps1
- Verifica se o Git está instalado; se não, baixa e instala silenciosamente o Git for Windows.
- Atualiza PATH para a sessão atual (se necessário).
- Configura user.name e user.email (pede ao usuário se não configurados).
- Inicializa repo (se necessário), adiciona arquivos, faz commit.
- Pergunta o remote (ex: https://github.com/USER/REPO.git) e opcionalmente o Personal Access Token (PAT).
- Faz push para origin main. Se PAT fornecido, usa URL com token para push não interativo.

USO: Execute em PowerShell com privilégios normais. Para instalar o Git pode pedir permissão de UAC.
#>

$ErrorActionPreference = 'Stop'

function Ensure-Git {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "Git encontrado:" (git --version) -ForegroundColor Green
        return $true
    }

    Write-Host "Git não encontrado. Baixando instalador de Git for Windows..." -ForegroundColor Yellow
    $tmp = Join-Path $env:TEMP "Git-Installer.exe"
    $url = 'https://github.com/git-for-windows/git/releases/latest/download/Git-64-bit.exe'
    Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing

    Write-Host "Executando instalador (silencioso). Pode pedir permissão UAC..." -ForegroundColor Yellow
    Start-Process -FilePath $tmp -ArgumentList '/VERYSILENT','/NORESTART' -Wait

    # tentar localizar git instalado
    $paths = @(
        'C:\Program Files\Git\cmd\git.exe',
        'C:\Program Files (x86)\Git\cmd\git.exe'
    )
    foreach ($p in $paths) {
        if (Test-Path $p) {
            $gitDir = Split-Path $p
            $env:PATH = "$gitDir;" + $env:PATH
            Write-Host "Git instalado em $p" -ForegroundColor Green
            return $true
        }
    }

    Write-Host "Instalação concluída, mas não localizei o executável Git automaticamente. Verifique o PATH." -ForegroundColor Yellow
    return $false
}

# Start
Write-Host "== JDB - Install & Push Script ==" -ForegroundColor Cyan

$hasGit = Ensure-Git
if (-not $hasGit) {
    Write-Host "Continuando mesmo assim. Se o comando 'git' não for encontrado, você precisará reiniciar a sessão ou adicionar o Git ao PATH." -ForegroundColor Yellow
}

# Configurar user.name/user.email se não existirem
try {
    $currentName = git config --global user.name 2>$null
    $currentEmail = git config --global user.email 2>$null
} catch { }

if (-not $currentName) {
    $name = Read-Host 'Insira o nome do Git (git user.name) [ex: Seu Nome]'
    git config --global user.name "$name"
} else { Write-Host "git user.name já configurado: $currentName" }

if (-not $currentEmail) {
    $email = Read-Host 'Insira o email do Git (git user.email) [ex: seu_email@exemplo.com]'
    git config --global user.email "$email"
} else { Write-Host "git user.email já configurado: $currentEmail" }

# Inicializar repositório se necessário
if (-not (Test-Path .git)) {
    Write-Host "Inicializando repositório git local..."
    git init
} else { Write-Host "Repositório git já inicializado." }

# Adicionar e commitar
Write-Host "Adicionando arquivos e fazendo commit..."
git add --all
try {
    git commit -m "Initial commit: landing page + deploy workflow" -q
} catch {
    Write-Host "Commit pode já existir ou não houve alterações. Continuando..." -ForegroundColor Yellow
}

# Perguntar remote
$remote = Read-Host 'Digite o URL do repositório remoto (ex: https://github.com/USER/REPO.git)'
if (-not $remote) {
    Write-Host "Nenhum remote especificado. Saindo." -ForegroundColor Red
    exit 1
}

# Verificar se origin já existe
$existsOrigin = $false
try { git remote get-url origin; $existsOrigin = $true } catch { $existsOrigin = $false }
if ($existsOrigin) {
    Write-Host "Remote 'origin' já existe. Atualizando para o URL fornecido..."
    git remote set-url origin $remote
} else {
    git remote add origin $remote
}

# Pergunta sobre uso de PAT para push automático
Write-Host "Para push automático sem prompts, você pode usar um Personal Access Token (PAT)."
$useToken = Read-Host 'Deseja usar um PAT para push automático? (s/n)'

if ($useToken -match '^[sS]') {
    $secureToken = Read-Host 'Cole seu Personal Access Token (será ocultado)' -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    $plainToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) | Out-Null

    # Inserir token no URL (forma simples, cuidado com segurança)
    if ($remote -match '^https://') {
        $remoteNoProto = $remote -replace '^https://',''
        $remoteWithToken = "https://$plainToken@$remoteNoProto"
    } else {
        Write-Host "Remote não usa HTTPS. Não posso injetar token automaticamente." -ForegroundColor Red
        $remoteWithToken = $remote
    }

    git remote set-url origin $remoteWithToken
    Write-Host "Fazendo push para origin main usando token..."
    git branch -M main
    git push -u origin main

    # Restaurar URL sem token para segurança
    git remote set-url origin $remote
    Write-Host "Push concluído. Remote restaurado sem token." -ForegroundColor Green
} else {
    Write-Host "Tentando push interativo. Você será solicitado a inserir credenciais se necessário..."
    git branch -M main
    git push -u origin main
}

Write-Host "Pronto. Verifique o repositório remoto e o GitHub Actions (se configurado)." -ForegroundColor Green

# Fim do script
pause
