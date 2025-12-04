@echo off
REM Script para enviar landing page para GitHub

echo.
echo ===== JDDB Deploy para GitHub =====
echo.

REM Verificar se Git está instalado
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Git nao esta instalado!
    echo Baixe em: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Gerar dados
echo [1/4] Gerando dados da landing page...
.\.venv\Scripts\python.exe generate_landing_data.py
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao gerar dados
    pause
    exit /b 1
)
echo [OK] Dados gerados

REM Git add
echo [2/4] Adicionando arquivos...
git add .
echo [OK] Arquivos adicionados

REM Git commit
echo [3/4] Fazendo commit...
set /p msg="Digite mensagem de commit: "
if "%msg%"=="" set msg="Update landing page data"
git commit -m "%msg%"
echo [OK] Commit realizado

REM Git push
echo [4/4] Enviando para GitHub...
git push
echo [OK] Push concluido!

echo.
echo ===== DEPLOY CONCLUIDO =====
echo Sua landing page esta atualizada online!
echo.
pause
