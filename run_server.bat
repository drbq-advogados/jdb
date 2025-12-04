@echo off
REM -----------------------
REM Run Sistema Completo Jogo do Bicho
REM -----------------------

REM Ativar virtualenv
CALL ".venv\Scripts\activate.bat"

REM Atualizar pip
pip install --upgrade pip

REM Instalar dependências necessárias
pip install -r requirements.txt

REM Rodar Streamlit
echo Iniciando Streamlit...
streamlit run app.py

pause
