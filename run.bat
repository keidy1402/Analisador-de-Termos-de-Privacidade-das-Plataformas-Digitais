@echo off
REM Script de inicialização rápida para o Analisador de Privacidade Digital (Windows)

echo.
echo ========================================
echo  Analisador de Privacidade Digital
echo  Quick Start Script
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao foi encontrado!
    echo Por favor, instale Python de: https://www.python.org/downloads/
    echo Certifique-se de marcar "Add Python to PATH" durante a instalacao
    pause
    exit /b 1
)

echo [1/4] Python encontrado!
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv\" (
    echo [2/4] Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERRO ao criar ambiente virtual!
        pause
        exit /b 1
    )
) else (
    echo [2/4] Ambiente virtual ja existe!
)
echo.

REM Ativar ambiente virtual
echo [3/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERRO ao ativar ambiente virtual!
    pause
    exit /b 1
)
echo.

REM Instalar dependências
echo [4/4] Instalando dependencias...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERRO ao instalar dependencias!
    pause
    exit /b 1
)
echo.

REM Sucesso!
echo ========================================
echo  Tudo pronto!
echo ========================================
echo.
echo Iniciando Streamlit...
echo.
echo O app abrira em seu navegador:
echo http://localhost:8501
echo.
echo Para parar o servidor, pressione CTRL+C
echo.

REM Iniciar Streamlit
streamlit run app.py

pause
