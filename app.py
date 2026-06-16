import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import os
import urllib.parse
import xml.etree.ElementTree as ET
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Analisador de Privacidade",
    page_icon="🌹",
    layout="wide"
)

# --- CSS MINIMALISTA E CLEAN (Inspirado em 'Privacidade na Rede') ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* Configuração Global */
        .stApp, body, html, [data-testid="stWidgetLabel"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #f4f7f9;
            color: #2d3748;
            -webkit-font-smoothing: antialiased;
        }

        /* Título do Site */
        h1 {
            color: #104f7e !important;
            font-weight: 800 !important;
            font-size: 2.1rem !important;
            letter-spacing: -0.03em !important;
            margin-bottom: 6px !important;
            line-height: 1.2 !important;
        }
        h2, h3 {
            color: #104f7e !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
            margin-top: 5px !important;
        }
        
        /* ESTILIZAÇÃO DO SELECTBOX */
        div[data-testid="stSelectbox"] > div :first-child {
            background-color: #ffffff !important;
            border: 1.5px solid #104f7e !important;
            border-radius: 24px !important;
            padding: 2px 16px !important;
            box-shadow: 0 4px 10px rgba(16, 79, 126, 0.04) !important;
        }
        div[data-testid="stSelectbox"] div[role="button"] span {
            color: #104f7e !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }
        div[data-testid="stSelectbox"] svg {
            fill: #104f7e !important;
        }

        /* CARDS FLUTUANTES CLEAN */
        .card-container {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(16, 79, 126, 0.03), 0 2px 6px rgba(0, 0, 0, 0.01);
            margin-bottom: 24px;
            border: 1px solid rgba(16, 79, 126, 0.05);
            line-height: 1.7;
        }

        /* Card Alerta Fator Crítico */
        .card-critico {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 16px;
            border-left: 6px solid #c03131;
            box-shadow: 0 10px 25px rgba(16, 79, 126, 0.03);
            margin-bottom: 24px;
            border-top: 1px solid rgba(0,0,0,0.02);
            border-right: 1px solid rgba(0,0,0,0.02);
            border-bottom: 1px solid rgba(0,0,0,0.02);
        }
        .critico-titulo {
            color: #c03131;
            font-weight: 700;
            font-size: 1.05rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 8px;
        }

        /* Lista Fina de Indicadores (Substituindo as Bolinhas) */
        .lista-riscos {
            list-style: none;
            padding-left: 0;
            margin-top: 10px;
        }
        .item-risco {
            font-size: 1rem;
            padding: 10px 0;
            border-bottom: 1px solid #edf2f7;
            display: flex;
            align-items: center;
            color: #4a5568;
        }
        .item-risco::before {
            content: "•";
            color: #c03131;
            font-weight: bold;
            display: inline-block;
            width: 1.5em;
            font-size: 1.3rem;
        }

        /* Notícias em Cards Limpos */
        .card-noticia {
            background-color: #ffffff;
            padding: 24px;
            border-radius: 14px;
            border-top: 4px solid #f2c557;
            box-shadow: 0 6px 18px rgba(0,0,0,0.01);
            height: 100%;
        }
        .noticia-link {
            color: #104f7e !important;
            text-decoration: none !important;
            font-weight: 600 !important;
        }
        .noticia-link:hover {
            color: #c03131 !important;
        }

        /* Abas Laterais/Superiores Clean */
        .stTabs [data-baseweb="tab"] {
            font-weight: 600 !important;
            color: #718096 !important;
            font-size: 1rem !important;
            border-bottom: 2px solid transparent !important;
            padding: 12px 24px !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #104f7e !important;
            border-bottom: 2px solid #104f7e !important;
            font-weight: 700 !important;
        }

        /* Rodapé */
        .footer {
            font-size: 0.8rem;
            color: #a0aec0;
            text-align: center;
            margin-top: 80px;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA API GEMINI ---
try:
    client = genai.Client()
except Exception as e:
    st.error("Erro ao inicializar a API do Gemini. Verifique a chave GEMINI_API_KEY nos Secrets.")
    client = None

MAPA_PLATAFORMAS = {
    "Facebook": "Facebook.txt",
    "Instagram": "Instagram.txt",
    "Snapchat": "Snapchat.txt",
    "TikTok": "Tiktok.txt",
    "Twitter (X)": "Twitter.txt",
    "WhatsApp": "Whatsapp.txt",
    "YouTube": "Youtube.txt"
}

class AnalisePrivacidade(BaseModel):
    resumo_claro: str = Field(description="Um resumo em linguagem muito clara, simples e direta sobre o termo de privacidade.")
    red_flags: list[str] = Field(description="Lista de 5 a 8 cláusulas ou conceitos curtos de risco encontrados.")
    palavra_mais_critica: str = Field(description="A palavra ou conceito que representa o maior risco isolado ao usuário.")
    pontuacao_risco: int = Field(description="Uma nota inteira de 0 a 100 baseada na severidade das cláusulas avaliadas.")

def carregar_termo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.read()
    return None

@st.cache_data(show_spinner="Avaliando conformidade do contrato de privacidade...")
def analisar_termo_com_gemini(texto_termo, nome_plataforma):
    if not client: 
        return None
    prompt = f"Você é um auditor de privacidade sênior. Analise o termo da plataforma {nome_plataforma}: {texto_termo}"
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalisePrivacidade,
                temperature=0.2
            ),
        )
        import json
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Erro na API: {e}")
        return None

dados_risco_global = {
    'Plataformas': ["Facebook", "Instagram", "Snapchat", "TikTok", "Twitter (X)", "WhatsApp", "YouTube"],
    'Nível de Risco (0-100)': [88, 85, 65, 90, 75, 55, 70]
}

# --- TOOLBAR SUPERIOR COMPACTA (Logotipo por Extenso + Menu Lateralizado) ---
col_head_left, col_head_right = st.columns([7, 3])

with col_head_left:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=340)
    else:
        st.markdown("<h1>Analisador de Termos de Privacidade das Plataformas Digitais</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #718096; margin:0; font-size:1rem;'>Transparência digital e auditoria inteligente de dados contratuais.</p>", unsafe_allow_html=True)

with col_head_right:
    st.write("") # Alinhamento vertical simples
    opcao_plataforma = st.selectbox("", ["Selecione uma plataforma..."] + list(MAPA_PLATAFORMAS.keys()))

st.write("")

if opcao_plataforma != "Selecione uma plataforma...":
    arquivo_alvo = MAPA_PLATAFORMAS[opcao_plataforma]
    texto_contrato = carregar_termo(arquivo_alvo)
    
    if texto_contrato:
        analise = analisar_termo_com_gemini(texto_contrato, opcao_plataforma)
        
        if analise:
            # --- COMPACTAÇÃO POR ABAS CLEAN ---
            aba_analise, aba_grafico = st.tabs(["🔍 Relatório Geral", "📊 Índice de Exposição Contratual"])
            
            with aba_analise:
                st.write("")
                
                # Seção 1: Sumário Executivo
                st.markdown("<h3 style='font-size: 1.2rem; color: #4a5568; margin-bottom:12px;'>📋 Sumário Executivo</h3>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="card-container">
                        {analise['resumo_claro']}
                    </div>
                """, unsafe_allow_html=True)
                
                # Seção 2: Indicadores de Risco em Lista Limpa vs Card Crítico
                st.write("")
                col
