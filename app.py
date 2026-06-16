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
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PREMIUM E ELEGANTE ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@700&display=swap');

        /* Reset e Configuração Global */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        .stApp, body, html {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background: linear-gradient(135deg, #f4f7f9 0%, #ebf2f7 100%) !important;
            color: #2d3748;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* HEADER PREMIUM */
        .header-container {
            background: linear-gradient(135deg, #104f7e 0%, #0d3a5c 100%);
            padding: 28px 0;
            margin: -80px -80px 40px -80px;
            box-shadow: 0 8px 32px rgba(16, 79, 126, 0.12);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 40px;
        }

        .logo-section h1 {
            color: #ffffff !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
            letter-spacing: -0.5px !important;
        }

        .logo-section p {
            color: rgba(255,255,255,0.8) !important;
            font-size: 0.9rem !important;
            margin-top: 6px !important;
            font-weight: 300 !important;
        }

        /* SELECTBOX ESTILIZADO */
        .platform-selector {
            flex: 1;
            max-width: 400px;
        }

        div[data-testid="stSelectbox"] > div:first-child {
            background: linear-gradient(135deg, #ffffff 0%, #f9fbfc 100%) !important;
            border: 2px solid rgba(16, 79, 126, 0.15) !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            box-shadow: 0 4px 15px rgba(16, 79, 126, 0.08) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        div[data-testid="stSelectbox"] > div:first-child:hover {
            border-color: rgba(16, 79, 126, 0.3) !important;
            box-shadow: 0 8px 25px rgba(16, 79, 126, 0.12) !important;
        }

        div[data-testid="stSelectbox"] div[role="button"] span {
            color: #104f7e !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }

        div[data-testid="stSelectbox"] svg {
            fill: #104f7e !important;
        }

        /* TÍTULOS */
        h1 {
            color: #104f7e !important;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
            letter-spacing: -0.03em !important;
            margin-bottom: 8px !important;
            line-height: 1.1 !important;
        }

        h2 {
            color: #104f7e !important;
            font-weight: 700 !important;
            font-size: 1.4rem !important;
            letter-spacing: -0.02em !important;
            margin-top: 8px !important;
            margin-bottom: 16px !important;
        }

        h3 {
            color: #104f7e !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            letter-spacing: -0.01em !important;
            margin-bottom: 12px !important;
        }

        /* CARDS FLUTUANTES COM EFEITO PREMIUM */
        .card-container {
            background: #ffffff;
            padding: 32px;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(16, 79, 126, 0.08), 0 2px 8px rgba(0, 0, 0, 0.03);
            margin-bottom: 28px;
            border: 1px solid rgba(16, 79, 126, 0.06);
            line-height: 1.7;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }

        .card-container:hover {
            box-shadow: 0 20px 60px rgba(16, 79, 126, 0.12), 0 4px 12px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }

        /* CARD CRÍTICO */
        .card-critico {
            background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
            padding: 32px;
            border-radius: 16px;
            border-left: 6px solid #c03131;
            box-shadow: 0 12px 40px rgba(192, 49, 49, 0.12), 0 2px 8px rgba(0, 0, 0, 0.03);
            margin-bottom: 28px;
            border-top: 1px solid rgba(192, 49, 49, 0.1);
            border-right: 1px solid rgba(0,0,0,0.03);
            border-bottom: 1px solid rgba(0,0,0,0.03);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .card-critico:hover {
            box-shadow: 0 16px 50px rgba(192, 49, 49, 0.15), 0 4px 12px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }

        .critico-titulo {
            color: #c03131;
            font-weight: 800;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .critico-content {
            color: #2d3748;
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 12px;
        }

        .critico-palavra {
            color: #c03131;
            font-weight: 800;
            font-size: 1.45rem;
            display: block;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 2px solid rgba(192, 49, 49, 0.2);
        }

        /* LISTA DE RISCOS */
        .lista-riscos {
            list-style: none;
            padding-left: 0;
            margin-top: 12px;
        }

        .item-risco {
            font-size: 0.95rem;
            padding: 14px 0;
            border-bottom: 1px solid #edf2f7;
            display: flex;
            align-items: flex-start;
            color: #4a5568;
            transition: all 0.3s ease;
        }

        .item-risco:hover {
            color: #104f7e;
            padding-left: 8px;
        }

        .item-risco::before {
            content: "▸";
            color: #c03131;
            font-weight: bold;
            display: inline-block;
            width: 1.5em;
            font-size: 1.2rem;
            flex-shrink: 0;
        }

        /* CARDS DE NOTÍCIA */
        .card-noticia {
            background: #ffffff;
            padding: 28px;
            border-radius: 14px;
            border-top: 4px solid #f2c557;
            box-shadow: 0 8px 28px rgba(0,0,0,0.06);
            height: 100%;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            border: 1px solid rgba(242, 197, 87, 0.1);
        }

        .card-noticia:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.1);
            border-color: rgba(242, 197, 87, 0.3);
        }

        .noticia-link {
            color: #104f7e !important;
            text-decoration: none !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            line-height: 1.5 !important;
            transition: color 0.3s ease !important;
        }

        .noticia-link:hover {
            color: #c03131 !important;
        }

        .noticia-fonte {
            color: #a0aec0;
            font-weight: 500;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid #edf2f7;
        }

        /* ABAS CLEAN */
        .stTabs [data-baseweb="tab"] {
            font-weight: 600 !important;
            color: #718096 !important;
            font-size: 0.95rem !important;
            border-bottom: 3px solid transparent !important;
            padding: 14px 28px !important;
            transition: all 0.3s ease !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #104f7e !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #104f7e !important;
            border-bottom: 3px solid #104f7e !important;
            font-weight: 700 !important;
        }

        /* GRÁFICO PERSONALIZADO */
        .chart-container {
            background: #ffffff;
            padding: 32px;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(16, 79, 126, 0.08);
            margin-bottom: 28px;
            border: 1px solid rgba(16, 79, 126, 0.06);
        }

        /* RODAPÉ */
        .footer {
            font-size: 0.8rem;
            color: #a0aec0;
            text-align: center;
            margin-top: 60px;
            padding-top: 28px;
            border-top: 1px solid rgba(16, 79, 126, 0.1);
        }

        .footer a {
            color: #104f7e;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .footer a:hover {
            color: #c03131;
        }

        /* WELCOME CARD */
        .welcome-card {
            background: linear-gradient(135deg, #ffffff 0%, #f9fbfc 100%);
            padding: 48px;
            border-radius: 18px;
            text-align: center;
            box-shadow: 0 12px 40px rgba(16, 79, 126, 0.08);
            margin-top: 32px;
            border: 1px solid rgba(16, 79, 126, 0.06);
            margin-bottom: 20px;
        }

        .welcome-card h3 {
            font-size: 1.4rem;
            margin-bottom: 16px;
            background: linear-gradient(135deg, #104f7e, #c03131);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .welcome-card p {
            color: #718096;
            max-width: 600px;
            margin: 0 auto;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* RESPONSIVIDADE */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                align-items: flex-start;
                gap: 20px;
                padding: 0 20px;
            }

            .platform-selector {
                max-width: 100%;
            }

            .logo-section h1 {
                font-size: 1.4rem !important;
            }

            h1 {
                font-size: 1.8rem !important;
            }

            .card-container, .card-critico, .card-noticia {
                padding: 24px;
            }
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

@st.cache_data(show_spinner="🔍 Analisando termo de privacidade...")
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

# --- HEADER PREMIUM ---
st.markdown("""
    <div class="header-container">
        <div class="header-content">
            <div class="logo-section">
                <h1>🔒 Analisador de Privacidade</h1>
                <p>Transparência digital e auditoria inteligente de dados contratuais</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SELETOR DE PLATAFORMA ---
col1, col2, col3 = st.columns([2, 3, 2])
with col2:
    st.markdown("<div class='platform-selector'>", unsafe_allow_html=True)
    opcao_plataforma = st.selectbox(
        "Selecione uma plataforma:",
        ["Selecione uma plataforma..."] + list(MAPA_PLATAFORMAS.keys()),
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

if opcao_plataforma != "Selecione uma plataforma...":
    arquivo_alvo = MAPA_PLATAFORMAS[opcao_plataforma]
    texto_contrato = carregar_termo(arquivo_alvo)
    
    if texto_contrato:
        analise = analisar_termo_com_gemini(texto_contrato, opcao_plataforma)
        
        if analise:
            # --- ABAS COM CONTEÚDO ---
            aba_analise, aba_grafico = st.tabs(["🔍 Relatório Completo", "📊 Matriz Comparativa"])
            
            with aba_analise:
                st.write("")
                
                # Seção: Sumário Executivo
                st.markdown("<h2 style='margin-bottom: 16px;'>📋 Sumário Executivo</h2>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="card-container">
                        <p style="color: #4a5568; line-height: 1.8; font-size: 0.95rem;">{analise['resumo_claro']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Seção: Riscos e Ponto Crítico
                st.write("")
                col_risks, col_critical = st.columns([1, 1], gap="medium")
                
                with col_risks:
                    st.markdown("<h3 style='margin-bottom: 16px;'>🚩 Cláusulas de Alerta</h3>", unsafe_allow_html=True)
                    itens_html = "".join([f"<li class='item-risco'>{tag}</li>" for tag in analise['red_flags']])
                    st.markdown(f"<ul class='lista-riscos'>{itens_html}</ul>", unsafe_allow_html=True)
                    
                with col_critical:
                    st.markdown(f"""
                        <div class="card-critico">
                            <div class="critico-titulo">⚠️ Maior Vulnerabilidade</div>
                            <div class="critico-content">
                                O principal conceito de risco que exige atenção absoluta do internauta neste contrato:
                            </div>
                            <div class="critico-palavra">{analise['palavra_mais_critica']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Seção: Notícias
                st.write("")
                st.markdown("<h2 style='margin-bottom: 16px;'>📰 Notícias Recentes</h2>", unsafe_allow_html=True)
                
                termo_busca = f"{opcao_plataforma} privacidade dados"
                termo_codificado = urllib.parse.quote(termo_busca)
                url_feed = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
                
                try:
                    resposta = requests.get(url_feed, timeout=5)
                    root = ET.fromstring(resposta.content)
                    noticias = root.findall('.//item')[:3]
                    
                    if noticias:
                        cols = st.columns(len(noticias))
                        
                        for idx, (col, noticia) in enumerate(zip(cols, noticias)):
                            with col:
                                titulo = noticia.find('title').text
                                link = noticia.find('link').text
                                fonte = noticia.find('source').text if noticia.find('source') is not None else "Portal"
                                
                                st.markdown(f"""
                                    <div class="card-noticia">
                                        <a class="noticia-link" href="{link}" target="_blank">{titulo}</a>
                                        <div class="noticia-fonte">{fonte}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                except:
                    st.info("Consulte os portais de notícias para atualizações em tempo real.")

            with aba_grafico:
                st.write("")
                st.markdown("<h2 style='margin-bottom: 16px;'>📊 Comparativo de Riscos</h2>", unsafe_allow_html=True)
                st.markdown("<p style='color: #718096; margin-bottom: 24px;'>Visão consolidada do nível de rigor no tratamento de dados privados por plataforma</p>", unsafe_allow_html=True)
                
                df_grafico = pd.DataFrame(dados_risco_global)
                st.bar_chart(data=df_grafico, x='Plataformas', y='Nível de Risco (0-100)', color='#104f7e')
                
    else:
        st.error(f"❌ Arquivo '{arquivo_alvo}' não encontrado.")

else:
    st.markdown("""
        <div class="welcome-card">
            <h3>🌐 Decodifique seus Direitos na Rede</h3>
            <p>Termos jurídicos extensos escondem monitoramentos complexos. Selecione uma plataforma acima para receber uma análise completa gerada por inteligência artificial.</p>
        </div>
    """, unsafe_allow_html=True)

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        <p>Aluna <strong>FGV-ECMI</strong>: Keidy Alves Pizzetti Amaro &nbsp;•&nbsp; Orientador: <strong>Prof. Josir Gomes</strong></p>
    </div>
""", unsafe_allow_html=True)
