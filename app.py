import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import os
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import json
import random
import html
from io import BytesIO

# --- MOTOR DE PDF ROBUSTO ---
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Espelho da Verdade - Termos de Privacidade",
    page_icon="🌹",
    layout="wide"
)

# --- ESTILO CSS CUSTOMIZADO (NUVEM ORGÂNICA & DESIGN ALINHADO) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
        
        .stApp { background-color: #FAF5EC; color: #2C1E21; font-family: 'Lora', serif; }
        h1, h2, h3, h4 { font-family: 'Cinzel', serif !important; color: #162E5C !important; font-weight: 600; }
        
        .gold-divider { height: 2px; background: linear-gradient(90deg, transparent, #D4AF37, transparent); margin: 30px 0; }
        
        /* Alinhamento dos blocos superiores */
        .parchment-card {
            background-color: #FFFFFF; border: 1px solid #E6D9C5; border-top: 4px solid #D4AF37;
            padding: 25px; border-radius: 8px; box-shadow: 0 6px 15px rgba(0,0,0,0.04);
            margin-bottom: 20px; height: 280px; display: flex; flex-direction: column; justify-content: center;
        }

        .score-container {
            text-align: center; background: linear-gradient(135deg, #162E5C 0%, #0B1D3A 100%);
            color: #FAF5EC; padding: 30px; border-radius: 12px; border: 2px solid #D4AF37;
            box-shadow: 0 8px 25px rgba(22, 46, 92, 0.2); height: 280px; display: flex; flex-direction: column; justify-content: center;
        }
        .score-number { font-family: 'Cinzel', serif; font-size: 4.5rem; color: #F5D04C; line-height: 1; }

        /* DESIGN DA NUVEM DE PALAVRAS (ESTILO IMAGEM) */
        .word-cloud-wrapper {
            padding: 40px; text-align: center; background: #FFFDF9; border-radius: 20px;
            border: 1px solid #E6D9C5; min-height: 300px; line-height: 1.2;
        }
        .cloud-word {
            display: inline-block; margin: 10px 15px; font-family: 'Cinzel', serif;
            transition: transform 0.3s ease; vertical-align: middle;
        }
        .cloud-word:hover { transform: scale(1.2); }

        /* Quadro de ATENÇÃO */
        .attention-box {
            background-color: #FFF5F5; border: 2px solid #991B1B; padding: 25px; border-radius: 8px;
            text-align: center; margin-top: 20px; position: relative;
        }
        .attention-label {
            position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
            background: #991B1B; color: white; padding: 2px 15px; font-family: 'Cinzel', serif; font-size: 0.8rem; border-radius: 4px;
        }

        .footer { font-family: 'Cinzel', serif; font-size: 0.8rem; text-align: center; margin-top: 80px; border-top: 1px dashed #D4AF37; padding-top: 25px; color: #6B5B52; }
    </style>
""", unsafe_allow_html=True)

# --- MODELOS DE DATOS ---
class DicaSeguranca(BaseModel):
    titulo: str
    passos: list[str]

class AnalisePrivacidade(BaseModel):
    resumo_claro: str
    red_flags: list[str]
    palavra_mais_critica: str
    pontuacao_risco: int
    dicas_protecao: list[DicaSeguranca]

# --- BANCO DE CONTINGÊNCIA (MOCK) ---
ACERVO_CONTINGENCIA = {
    "Facebook": {"resumo_claro": "O Facebook monitora intensamente sua atividade fora do aplicativo, coletando dados de navegação e interesses para anúncios direcionados.", "red_flags": ["Rastreamento", "Cookies", "Perfilamento", "Big Data", "Metadata", "Audiente", "Terceiros", "Pixel"], "palavra_mais_critica": "Rastreamento Off-Platform", "pontuacao_risco": 88, "dicas_protecao": [{"titulo": "Desativar Atividade Fora do FB", "passos": ["Vá em Configurações.", "Atividade fora do Facebook > Desativar."]}]},
    "TikTok": {"resumo_claro": "O TikTok possui regras invasivas que monitoram desde biometria facial até padrões de digitação para recomendação algorítmica.", "red_flags": ["Biometria", "Keylogging", "Algoritmo", "China", "Rede Local", "Voz", "FaceID", "Dados"], "palavra_mais_critica": "Coleta Biométrica", "pontuacao_risco": 90, "dicas_protecao": [{"titulo": "Limitar Navegador Interno", "passos": ["Abra links sempre no navegador externo."]}]},
    "Instagram": {"resumo_claro": "O Instagram foca na coleta de dados visuais e localização, integrando agora seus conteúdos para treinamento de IA da Meta.", "red_flags": ["IA Generativa", "Metadados", "Localização", "Reconhecimento", "Directs", "Stories", "Explorar", "Shadowing"], "palavra_mais_critica": "Treinamento de IA", "pontuacao_risco": 85, "dicas_protecao": [{"titulo": "Conta Privada", "passos": ["Acesse Privacidade > Conta Privada."]}]},
    "WhatsApp": {"resumo_claro": "O WhatsApp protege mensagens, mas compartilha com a Meta metadados como horários de conexão, contatos e endereços IP.", "red_flags": ["Metadados", "IP Address", "Contatos", "Backup", "Sincronia", "Status", "Chamadas", "Visto Por Último"], "palavra_mais_critica": "Vazamento de Metadados", "pontuacao_risco": 55, "dicas_protecao": [{"titulo": "Proteger IP", "passos": ["Configurações > Privacidade > Avançado."]}]},
    "YouTube": {"resumo_claro": "O YouTube unifica cada pesquisa e tempo de visualização ao seu perfil central do Google para monitorar hábitos de consumo.", "red_flags": ["Histórico", "Google Ads", "Crianças", "WatchTime", "Perfil", "Cookies", "Tracking", "Analytics"], "palavra_mais_critica": "Rastreamento Unificado", "pontuacao_risco": 70, "dicas_protecao": [{"titulo": "Pausar Histórico", "passos": ["Configurações > Histórico > Pausar."]}]},
    "Twitter (X)": {"resumo_claro": "O X utiliza posts públicos para alimentar seu modelo de IA Grok, além de rastrear navegação e logs de dispositivo.", "red_flags": ["Grok", "Scraping", "Elon", "Treinamento", "Tweets", "Logs", "Navegador", "Clicks"], "palavra_mais_critica": "Mineração Grok", "pontuacao_risco": 75, "dicas_protecao": [{"titulo": "Desativar Grok", "passos": ["Privacidade > Grok > Desativar."]}]},
    "Snapchat": {"resumo_claro": "O Snapchat foca intensamente em geolocalização em tempo real (Snap Map) e processamento de filtros faciais interativos.", "red_flags": ["SnapMap", "Filtros", "Lentes", "Realidade", "Localização", "Contatos", "Sprints", "Memórias"], "palavra_mais_critica": "Geolocalização Contínua", "pontuacao_risco": 65, "dicas_protecao": [{"titulo": "Modo Fantasma", "passos": ["Ative o Modo Fantasma no Mapa."]}]}
}

# --- FUNÇÕES ---
@st.cache_data
def analisar_ia_com_contingencia(plataforma):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Analise a privacidade de {plataforma}.",
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=AnalisePrivacidade)
        )
        return json.loads(resp.text), False
    except:
        return ACERVO_CONTINGENCIA.get(plataforma), True

def gerar_pdf_blindado(plataforma, analise):
    if not PDF_DISPONIVEL: return None
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    t_style = ParagraphStyle('T', parent=styles['Heading1'], textColor=colors.HexColor('#162E5C'), alignment=1)
    b_style = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, leading=14)
    story = [Paragraph(f"<b>ESCUDO: {plataforma}</b>", t_style), Spacer(1, 15), Paragraph(analise['resumo_claro'], b_style)]
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- INTERFACE ---
MAPA_ICONES = {"Facebook": "https://img.icons8.com/fluency/96/facebook-new.png", "Instagram": "https://img.icons8.com/fluency/96/instagram-new.png", "Snapchat": "https://img.icons8.com/fluency/96/snapchat.png", "TikTok": "https://img.icons8.com/fluency/96/tiktok.png", "Twitter (X)": "https://img.icons8.com/fluency/96/twitterx.png", "WhatsApp": "https://img.icons8.com/fluency/96/whatsapp.png", "YouTube": "https://img.icons8.com/fluency/96/youtube-play.png"}

st.markdown('<div style="text-align: center;"><h1>🌹 O Espelho da Verdade</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    opcao = st.selectbox("Selecione a plataforma:", ["Selecione..."] + list(ACERVO_CONTINGENCIA.keys()))

if opcao != "Selecione...":
    analise, fallback = analisar_ia_com_contingencia(opcao)
    
    if analise:
        # ALINHAMENTO SUPERIOR PERFEITO
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"""<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;"><img src="{MAPA_ICONES[opcao]}" width="55"><h3>Relatório de {opcao}</h3></div>""", unsafe_allow_html=True)
            st.markdown(f'<div class="parchment-card"><p>{analise["resumo_claro"]}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div style="margin-bottom: 10px; height: 35px;"></div><div class="score-container"><div style="font-family:Cinzel; font-size:0.9rem;">RISCO DETECTADO</div><div class="score-number">{analise["pontuacao_risco"]}%</div></div>""", unsafe_allow_html=True)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        f1, f2 = st.columns(2)
        with f1:
            st.subheader("🚩 Sinais de Alerta")
            
            # NUVEM DE PALAVRAS ESTILO IMAGEM (ORGÂNICA)
            cores_nuvem = ["#991B1B", "#D4AF37", "#162E5C"] # Vermelho Rosa, Dourado, Azul Fera
            tamanhos = ["1.5rem", "2.2rem", "2.8rem", "1.8rem", "3.5rem", "1.2rem"]
            
            tags_html = ""
            for tag in analise['red_flags']:
                cor = random.choice(cores_nuvem)
                tam = random.choice(tamanhos)
                weight = "bold" if tam in ["2.8rem", "3.5rem"] else "normal"
                tags_html += f'<span class="cloud-word" style="color:{cor}; font-size:{tam}; font-weight:{weight};">{tag}</span>'
            
            st.markdown(f'<div class="word-cloud-wrapper">{tags_html}</div>', unsafe_allow_html=True)
            
            # Quadro de ATENÇÃO
            st.markdown(f"""<div class="attention-box"><div class="attention-label">ATENÇÃO</div><span style="font-size: 1.6rem; font-weight: bold; color: #991B1B; font-family: Cinzel;">{analise['palavra_mais_critica']}</span></div>""", unsafe_allow_html=True)

        with f2:
            st.subheader("🛡️ Escudo de Defesa")
            for d in analise['dicas_protecao']:
                with st.expander(f"⚙️ {d['titulo']}"):
                    for p in d['passos']: st.write(f"• {p}")
            
            if PDF_DISPONIVEL:
                pdf = gerar_pdf_blindado(opcao, analise)
                st.download_button("📜 Baixar Guia em PDF", data=pdf, file_name=f"Escudo_{opcao}.pdf", mime="application/pdf", use_container_width=True)

        # LINHA DIVISÓRIA ENTRE ATENÇÃO E GRÁFICO
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # GRÁFICO E INTERPRETAÇÃO PERSONALIZADA
        st.subheader("📊 Comparativo de Periculosidade")
        df_p = pd.DataFrame({'Plataforma': list(ACERVO_CONTINGENCIA.keys()), 'Risco': [v['pontuacao_risco'] for v in ACERVO_CONTINGENCIA.values()]}).sort_values('Risco', ascending=True)
        fig = px.bar(df_p, x='Risco', y='Plataforma', orientation='h', color='Risco', color_continuous_scale=['#F5D04C', '#D4AF37', '#991B1B'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Cinzel", font_color="#162E5C", margin=dict(l=20, r=20, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # RELATÓRIO DINÂMICO PERSONALIZADO
        outros_riscos = [v['pontuacao_risco'] for k, v in ACERVO_CONTINGENCIA.items() if k != opcao]
        avg_risco = sum(outros_riscos) / len(outros_riscos)
        status = "acima" if analise['pontuacao_risco'] > avg_risco else "abaixo"
        st.markdown(f"""<div class="parchment-card" style="border-top: 4px solid #162E5C; height: auto; min-height: auto;"><h4 style="margin-top:0">📜 Interpretação do Espelho: {opcao}</h4><p>O <b>{opcao}</b> possui um risco de <b>{analise['pontuacao_risco']}%</b>, situando-se <b>{status}</b> da média das outras plataformas ({avg_risco:.1f}%). Enquanto o TikTok e o Facebook são as feras mais vorazes, o {opcao} exige atenção em <i>{analise['palavra_mais_critica']}</i>.</p></div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">FGV-ECMI | Aluna: Keidy Alves Pizzetti Amaro | Prof. Josir Gomes</div>', unsafe_allow_html=True)
