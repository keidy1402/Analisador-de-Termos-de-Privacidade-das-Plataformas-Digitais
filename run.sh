#!/bin/bash

# Script de inicialização rápida para o Analisador de Privacidade Digital (Linux/Mac)

echo ""
echo "========================================"
echo " Analisador de Privacidade Digital"
echo " Quick Start Script"
echo "========================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não foi encontrado!"
    echo "Por favor, instale Python 3:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "  macOS: brew install python3"
    exit 1
fi

echo "[1/4] Python encontrado!"
echo ""

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "[2/4] Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERRO ao criar ambiente virtual!"
        exit 1
    fi
else
    echo "[2/4] Ambiente virtual já existe!"
fi
echo ""

# Ativar ambiente virtual
echo "[3/4] Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERRO ao ativar ambiente virtual!"
    exit 1
fi
echo ""

# Instalar dependências
echo "[4/4] Instalando dependências..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO ao instalar dependências!"
    exit 1
fi
echo ""

# Sucesso!
echo "========================================"
echo " Tudo pronto!"
echo "========================================"
echo ""
echo "Iniciando Streamlit..."
echo ""
echo "O app abrirá em seu navegador:"
echo "http://localhost:8501"
echo ""
echo "Para parar o servidor, pressione CTRL+C"
echo ""

# Iniciar Streamlit
streamlit run app.py
