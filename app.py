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
    layout="narrow"
)

# --- PALETA DE CORES E DESIGN REFINADO ---
# Mudando a fonte geral, customizando o st.selectbox e aplicando o tema "A Bela e a Fera"
st.markdown("""
    <style>
        /* Importando uma fonte moderna e elegante */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

        /* Aplicação da fonte e do fundo do site */
        .stApp, body, html, [data-testid="stWidgetLabel"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #ebf2f7;
            color: #221e23;
        }
        
        /* Customização Estrita da Caixinha de Seleção (Selectbox) */
        /* 1. Define o fundo azul escuro e a borda fina */
        div[data-testid="stSelectbox"] div[role="button"] {
            background-color: #104f7e !important;
            border: 1px solid #104f7e !important;
            border-radius: 8px !important;
            padding: 4px 12px !important;
        }
        
        /* 2. Deixa o texto da plataforma selecionada em azul claro */
        div[data-testid="stSelectbox"] div[role="button"] span {
            color: #ebf2f7 !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }
        
        /* 3. Garante que a setinha do menu também fique clara */
        div[data-testid="stSelectbox"] svg {
            fill: #ebf2f7 !important;
        }

        /* Customização dos Títulos */
        h1 {
            color: #104f7e !important;
            font-weight: 800 !important;
            margin-bottom: 5px !important;
        }
        h2, h3 {
            color: #104f7e !important;
            font-weight: 700 !important;
        }
        
        /* Card de Resumo Elegante */
        .card-resumo {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 12px;
            border-top: 5px solid #104f7e;
            box-shadow: 0 4px 12px rgba(16, 79, 126, 0.08);
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        /* Alerta Vermelho Rosa (Red Flags) */
        .card-atencao {
            background-color: #f0dbb6;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid #c03131;
            box-shadow: 0 4px 10px rgba(192, 49, 49, 0.1);
            margin-bottom: 20px;
        }
        .atencao-titulo {
            color: #c03131;
            font-weight: bold;
            font-size: 1.2rem;
            margin-bottom: 5px;
        }
        
        /* Nuvem de Tags Coloridas e Vivas */
        .tag-risco {
            background-color: #c03131;
            color: white;
            padding: 8px 14px;
            border-radius: 20px;
            margin: 5px;
            display: inline-block;
            font-weight: bold;
            font-size: 0.95rem;
            box-shadow: 0 2px 5px rgba(192, 49, 49, 0.2);
        }
        
        /* Cards de Notícias modernos */
        .card-noticia {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            border-bottom: 4px solid #f2c557;
            box-shadow: 0 4px 10px rgba(0,0,0,0.04);
            height: 100%;
        }
        
        /* Customização Estética das Abas (Tabs) */
        .stTabs [data-baseweb="tab"] {
            font-family: 'Inter', sans-serif !important;
            font-weight: bold !important;
            color: #104f7e !important;
            font-size: 1.05rem !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #104f7e !important;
            color: #ffffff !important;
            border-radius: 4px 4px 0px 0px;
            padding: 10px 20px !important;
        }
        
        /* Rodapé Discreto */
        .footer {
            font-size: 0.75rem;
            color: #555555;
            text-align: center;
            margin-top: 60px;
            border-top: 1px solid #104f7e;
            padding-top: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA API GEMINI ---
try:
    client = genai.Client()
except Exception as e:
    st.error("Erro ao inicializar a API do Gemini. Verifique a chave GEMINI_API_KEY nos Secrets.")
    client = None

# Mapeamento de arquivos
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
    red_flags: list[str] = Field(description="Lista de 5 a 8 palavras ou termos curtos de risco encontrados (ex: Rastreamento, Terceiros).")
    palavra_mais_critica: str = Field(description="A palavra ou conceito que representa o maior risco isolado ao usuário.")
    pontuacao_risco: int = Field(description="Uma nota inteira de 0 a 100 baseada na severidade das cláusulas de privacidade avaliadas.")

def carregar_termo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.read()
    return None

@st.cache_data(show_spinner="Analisando cláusulas contratuais com Inteligência Artificial...")
def analisar_termo_com_gemini(texto_termo, nome_plataforma):
    if not client: return None
    prompt = f"Você é um especialista em direito digital. Analise o termo da plataforma {nome_plataforma} fornecido: {texto_termo}"
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

# Dados globais fixos para o gráfico
dados_risco_global = {
    'Plataformas': ["Facebook", "Instagram", "Snapchat", "TikTok", "Twitter (X)", "WhatsApp", "YouTube"],
    'Nível de Risco (0-100)': [88, 85, 65, 90, 75, 55, 70]
}

# --- CABEÇALHO COMPACTO E COLORIDO ---
col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='font-size: 4rem; text-align: center; margin:0;'>🌹</h1>", unsafe_allow_html=True)

with col_titulo:
    st.markdown("<h1>Analisador de Termos de Privacidade</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #104f7e; font-size: 1.1rem; margin:0;'>Desmistificando a segurança digital e os seus direitos nas plataformas.</p>", unsafe_allow_html=True)

st.write("") 

# --- MENU DE SELEÇÃO E FILTRO ---
col_select, _ = st.columns([2, 2])
with col_select:
    # A label (texto explicativo acima da caixa) respeita a nova fonte automática
    opcao_plataforma = st.selectbox("🎯 Escolha uma plataforma digital para auditar:", ["Selecione..."] + list(MAPA_PLATAFORMAS.keys()))

st.divider()

if opcao_plataforma != "Selecione...":
    arquivo_alvo = MAPA_PLATAFORMAS[opcao_plataforma]
    texto_contrato = carregar_termo(arquivo_alvo)
    
    if texto_contrato:
        analise = analisar_termo_com_gemini(texto_contrato, opcao_plataforma)
        
        if analise:
            aba_analise, aba_grafico = st.tabs(["🔍 Análise da Plataforma", "📊 Comparativo Geral de Risco"])
            
            with aba_analise:
                st.write("")
                st.subheader("📋 Resumo Direto do Termo")
                st.markdown(f"""
                    <div class="card-resumo">
                        {analise['resumo_claro']}
                    </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                st.subheader("🚩 Pontos de Atenção Críticos")
                col_tags, col_box = st.columns(2)
                
                with col_tags:
                    st.markdown("<p style='font-weight: bold; color: #221e23;'>Termos de maior recorrência e risco:</p>", unsafe_allow_html=True)
                    tags_html = "".join([f"<span class='tag-risco'>{tag}</span>" for tag in analise['red_flags']])
                    st.markdown(tags_html, unsafe_allow_html=True)
                    
                with col_box:
                    st.markdown(f"""
                        <div class="card-atencao">
                            <div class="atencao-titulo">⚠️ ATENÇÃO:</div>
                            A palavra ou conceito que mais se destaca de forma crítica neste termo é: 
                            <br><span style="color: #c03131; font-weight: 900; font-size: 1.3rem;">{analise['palavra_mais_critica']}</span>.
                        </div>
                    """, unsafe_allow_html=True)
                
                st.write("")
                st.markdown("<hr style='border: 0; border-top: 1px solid #104f7e; opacity: 0.2;'>", unsafe_allow_html=True)
                st.subheader("📰 Notícias em Tempo Real")
                
                termo_busca = f"{opcao_plataforma} privacidade dados"
                termo_codificado = urllib.parse.quote(termo_busca)
                url_feed = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
                
                try:
                    resposta = requests.get(url_feed, timeout=5)
                    root = ET.fromstring(resposta.content)
                    noticias = root.findall('.//item')[:2]
                    
                    if noticias:
                        col_n1, col_n2 = st.columns(2)
                        
                        with col_n1:
                            t1 = noticias[0].find('title').text
                            l1 = noticias[0].find('link').text
                            f1 = noticias[0].find('source').text if noticias[0].find('source') is not None else "Portal"
                            st.markdown(f"""
                                <div class="card-noticia">
                                    <h4 style='margin:0 0 8px 0; font-family: "Inter", sans-serif;'><a href="{l1}" target="_blank" style="color: #104f7e; text-decoration: none;">{t1}</a></h4>
                                    <span style="color: #c03131; font-weight: bold; font-size: 0.8rem;">Fonte: {f1}</span>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        with col_n2:
                            if len(noticias) > 1:
                                t2 = noticias[1].find('title').text
                                l2 = noticias[1].find('link').text
                                f2 = noticias[1].find('source').text if noticias[1].find('source') is not None else "Portal"
                                st.markdown(f"""
                                    <div class="card-noticia">
                                        <h4 style='margin:0 0 8px 0; font-family: "Inter", sans-serif;'><a href="{l2}" target="_blank" style="color: #104f7e; text-decoration: none;">{t2}</a></h4>
                                        <span style="color: #c03131; font-weight: bold; font-size: 0.8rem;">Fonte: {f2}</span>
                                    </div>
                                """, unsafe_allow_html=True)
                except:
                    st.write("Consulte os portais de tecnologia para ver as últimas novidades.")

            with aba_grafico:
                st.write("")
                st.subheader("📊 Ranking Comparativo de Vulnerabilidade")
                st.markdown("O gráfico ilustra o nível de exposição e risco dos seus dados em cada ecossistema digital:")
                df_grafico = pd.DataFrame(dados_risco_global)
                st.bar_chart(data=df_grafico, x='Plataformas', y='Nível de Risco (0-100)', color='#104f7e')
                
    else:
        st.error(f"Arquivo '{arquivo_alvo}' não encontrado.")
else:
    st.markdown("""
        <div style="background-color: #ffffff; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.02);">
            <h3 style="color: #104f7e; margin-top:0;">🌹 Boas-vindas ao Analisador</h3>
            <p style="color: #555555; max-width: 600px; margin: 0 auto;">
                Contratos de termos de uso são longos e complexos. Selecione uma das 7 plataformas no menu acima 
                para decodificar as cláusulas ocultas usando nossa auditoria inteligente baseada no modelo Gemini.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- RODAPÉ ACADÊMICO ---
st.markdown("""
    <div class="footer">
        Aluna FGV-ECMI: Keidy Alves Pizzetti Amaro &nbsp;|&nbsp; Orientador: Prof. Josir Gomes
    </div>
""", unsafe_allow_html=True)
