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

# --- ESTILO CSS CUSTOMIZADO (ESTÉTICA A BELA E A FERA) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
        
        .stApp { background-color: #FAF5EC; color: #2C1E21; font-family: 'Lora', serif; }
        h1, h2, h3, h4 { font-family: 'Cinzel', serif !important; color: #162E5C !important; font-weight: 600; }
        
        .gold-divider { height: 2px; background: linear-gradient(90deg, transparent, #D4AF37, transparent); margin: 25px 0; }
        
        .parchment-card {
            background-color: #FFFFFF; border: 1px solid #E6D9C5; border-top: 4px solid #D4AF37;
            padding: 25px; border-radius: 8px; box-shadow: 0 6px 15px rgba(0,0,0,0.04);
            margin-bottom: 20px; min-height: 250px; display: flex; flex-direction: column; justify-content: center;
        }

        .word-cloud-container { padding: 20px; text-align: center; line-height: 2.5; background: #FFFDF9; border: 1px dashed #D4AF37; border-radius: 10px; }

        .attention-box {
            background-color: #FFF5F5; border: 2px solid #991B1B; padding: 25px; border-radius: 8px;
            text-align: center; margin-top: 20px; position: relative;
        }
        .attention-label {
            position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
            background: #991B1B; color: white; padding: 2px 15px; font-family: 'Cinzel', serif; font-size: 0.8rem; border-radius: 4px;
        }

        .score-container {
            text-align: center; background: linear-gradient(135deg, #162E5C 0%, #0B1D3A 100%);
            color: #FAF5EC; padding: 30px; border-radius: 12px; border: 2px solid #D4AF37;
            box-shadow: 0 8px 25px rgba(22, 46, 92, 0.2); min-height: 250px; display: flex; flex-direction: column; justify-content: center;
        }
        .score-number { font-family: 'Cinzel', serif; font-size: 4.5rem; color: #F5D04C; line-height: 1; }

        .footer { font-family: 'Cinzel', serif; font-size: 0.8rem; text-align: center; margin-top: 80px; border-top: 1px dashed #D4AF37; padding-top: 25px; color: #6B5B52; }
    </style>
""", unsafe_allow_html=True)

# --- MODELOS DE DADOS ---
class DicaSeguranca(BaseModel):
    titulo: str
    passos: list[str]

class AnalisePrivacidade(BaseModel):
    resumo_claro: str
    red_flags: list[str]
    palavra_mais_critica: str
    pontuacao_risco: int
    dicas_protecao: list[DicaSeguranca]

# --- ACERVO DE CONTINGÊNCIA (FALLBACK) ---
ACERVO_CONTINGENCIA = {
    "Facebook": {"resumo_claro": "O Facebook monitora e coleta praticamente toda a sua atividade, inclusive fora da rede social, criando perfis profundos para anúncios.", "red_flags": ["Rastreamento Cruzado", "Cookies", "Perfilamento", "Leitura de Metadados", "Big Data"], "palavra_mais_critica": "Rastreamento Off-Platform", "pontuacao_risco": 88, "dicas_protecao": [{"titulo": "Desativar Atividade Fora do Facebook", "passos": ["Vá em Configurações.", "Selecione 'Sua Atividade'.", "Toque em 'Atividade fora do Facebook' e desative."]}]},
    "TikTok": {"resumo_claro": "O TikTok possui regras invasivas que monitoram até o ritmo de digitação e biometria facial para fins de recomendação algorítmica.", "red_flags": ["Biometria", "Keylogging", "Jurisdição Externa", "Acesso à Rede Local", "Padrão de Rolagem"], "palavra_mais_critica": "Coleta Biométrica", "pontuacao_risco": 90, "dicas_protecao": [{"titulo": "Limitar Navegador Interno", "passos": ["Não insira senhas no navegador do app.", "Abra links em navegadores externos (Chrome/Safari)."]}]},
    "Instagram": {"resumo_claro": "O Instagram foca na coleta de dados visuais e localização precisa, agora integrando conteúdos públicos para treinamento de IA da Meta.", "red_flags": ["IA Generativa", "Metadados de Imagem", "Localização Precisa", "Reconhecimento Facial", "Perfil de Interesse"], "palavra_mais_critica": "Treinamento de IA", "pontuacao_risco": 85, "dicas_protecao": [{"titulo": "Tornar Conta Privada", "passos": ["Acesse Configurações.", "Privacidade.", "Ative a chave 'Conta Privada'."]}]},
    "WhatsApp": {"resumo_claro": "O WhatsApp protege mensagens, mas compartilha com a Meta metadados valiosos como horários, contatos e endereços IP.", "red_flags": ["Metadados", "Sincronização Meta", "Endereço IP", "Lista de Contatos", "Dados de Pagamento"], "palavra_mais_critica": "Metadados de Conexão", "pontuacao_risco": 55, "dicas_protecao": [{"titulo": "Proteger IP em Chamadas", "passos": ["Vá em Configurações > Privacidade.", "Avançado.", "Ative 'Proteger endereço IP'."]}]},
    "YouTube": {"resumo_claro": "O YouTube unifica cada pesquisa e tempo de visualização ao seu perfil central do Google, monitorando comportamentos de consumo.", "red_flags": ["Histórico Unificado", "Perfilamento Google", "Padrão de Sono", "Rastreamento de Crianças", "Algoritmo Viciante"], "palavra_mais_critica": "Rastreamento Google Ads", "pontuacao_risco": 70, "dicas_protecao": [{"titulo": "Limpar Histórico Automaticamente", "passos": ["Acesse sua Conta Google.", "Privacidade.", "Defina exclusão automática para 3 meses."]}]},
    "Twitter (X)": {"resumo_claro": "O X utiliza posts públicos para alimentar seu modelo de IA Grok, além de rastrear links externos e dados de navegação.", "red_flags": ["Treinamento Grok", "Extração de Dados", "Perfil Político", "Ads Direcionados", "Logs de Dispositivo"], "palavra_mais_critica": "Mineração de Dados (Scraping)", "pontuacao_risco": 75, "dicas_protecao": [{"titulo": "Desativar Treinamento do Grok", "passos": ["Configurações > Privacidade e Segurança.", "Toque em 'Grok'.", "Desmarque a opção de compartilhamento."]}]},
    "Snapchat": {"resumo_claro": "O Snapchat foca intensamente em geolocalização em tempo real e processamento de filtros faciais interativos.", "red_flags": ["Snap Map", "Geolocalização", "Realidade Aumentada", "Sincronização Contatos", "Memórias em Nuvem"], "palavra_mais_critica": "Snap Map (Geolocalização)", "pontuacao_risco": 65, "dicas_protecao": [{"titulo": "Ativar Modo Fantasma", "passos": ["Abra o Mapa.", "Toque na Engrenagem.", "Ative o 'Modo Fantasma'."]}]}
}

# --- FUNÇÕES DE LÓGICA ---
@st.cache_data
def analisar_ia_com_contingencia(plataforma):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Analise a privacidade da rede social {plataforma}. Responda em JSON.",
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
    
    clean_p = html.escape(plataforma)
    clean_res = html.escape(analise['resumo_claro'])
    
    t_style = ParagraphStyle('T', parent=styles['Heading1'], textColor=colors.HexColor('#162E5C'), alignment=1)
    b_style = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, leading=14)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], textColor=colors.HexColor('#162E5C'), spaceBefore=10)
    
    story = [
        Paragraph(f"<b>MANUAL DE PROTEÇÃO: {clean_p}</b>", t_style),
        Spacer(1, 15),
        Paragraph(f"<b>Risco Geral: {analise['pontuacao_risco']}%</b>", h2_style),
        Paragraph(clean_res, b_style),
        Spacer(1, 10),
        Paragraph("<b>PASSO A PASSO DE CONFIGURAÇÃO:</b>", h2_style)
    ]
    
    for d in analise['dicas_protecao']:
        story.append(Paragraph(f"<b>• {html.escape(d['titulo'])}</b>", b_style))
        for p in d['passos']:
            story.append(Paragraph(f"- {html.escape(p)}", b_style))
        story.append(Spacer(1, 5))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- INTERFACE PRINCIPAL ---
MAPA_ICONES = {
    "Facebook": "https://img.icons8.com/fluency/96/facebook-new.png", 
    "Instagram": "https://img.icons8.com/fluency/96/instagram-new.png", 
    "Snapchat": "https://img.icons8.com/fluency/96/snapchat.png", 
    "TikTok": "https://img.icons8.com/fluency/96/tiktok.png", 
    "Twitter (X)": "https://img.icons8.com/fluency/96/twitterx.png", 
    "WhatsApp": "https://img.icons8.com/fluency/96/whatsapp.png", 
    "YouTube": "https://img.icons8.com/fluency/96/youtube-play.png"
}

st.markdown('<div style="text-align: center;"><h1>🌹 O Espelho da Verdade</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

col_sel_1, col_sel_2, col_sel_3 = st.columns([1, 2, 1])
with col_sel_2:
    opcao = st.selectbox("Selecione a plataforma para desvendar:", ["Selecione..."] + list(ACERVO_CONTINGENCIA.keys()))

if opcao != "Selecione...":
    analise, fallback = analisar_ia_com_contingencia(opcao)
    
    if analise:
        # ALINHAMENTO SUPERIOR: Relatório Geral e Risco Detectado
        col_main, col_score = st.columns([2, 1])
        
        with col_main:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                    <img src="{MAPA_ICONES[opcao]}" width="60">
                    <h2 style="margin:0;">Relatório de {opcao}</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f'<div class="parchment-card"><p style="font-size:1.1rem; line-height:1.6;">{analise["resumo_claro"]}</p></div>', unsafe_allow_html=True)
        
        with col_score:
            st.markdown(f"""
                <div class="score-container">
                    <div style="font-family:Cinzel; font-size:1rem; margin-bottom:10px;">RISCO GERAL DETECTADO</div>
                    <div class="score-number">{analise["pontuacao_risco"]}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # COLUNAS DO MEIO: Nuvem e Escudo
        f1, f2 = st.columns(2)
        with f1:
            st.subheader("🚩 Sinais de Alerta")
            tags_html = "".join([f'<span style="font-size:{random.uniform(1.1, 2.0)}rem; opacity:{random.uniform(0.6, 1)}; margin: 8px; display: inline-block; color:#991B1B; font-family:Cinzel;">{t}</span>' for t in analise['red_flags']])
            st.markdown(f'<div class="word-cloud-container">{tags_html}</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="attention-box">
                    <div class="attention-label">ATENÇÃO</div>
                    <span style="font-size: 1.5rem; font-weight: bold; color: #991B1B; font-family: Cinzel;">{analise['palavra_mais_critica']}</span>
                </div>
            """, unsafe_allow_html=True)

        with f2:
            st.subheader("🛡️ Escudo de Defesa")
            for d in analise['dicas_protecao']:
                with st.expander(f"⚙️ {d['titulo']}"):
                    for p in d['passos']: st.write(f"• {p}")
            
            if PDF_DISPONIVEL:
                pdf_data = gerar_pdf_blindado(opcao, analise)
                st.download_button("📜 Baixar Guia em PDF", data=pdf_data, file_name=f"Escudo_{opcao}.pdf", mime="application/pdf", use_container_width=True)

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
        
        st.markdown(f"""
            <div class="parchment-card" style="border-top: 4px solid #162E5C; min-height: auto;">
                <h4 style="margin-top:0">📜 Interpretação do Espelho: {opcao}</h4>
                <p>Ao observarmos o reino digital, o <b>{opcao}</b> se destaca com um nível de risco de <b>{analise['pontuacao_risco']}%</b>, 
                o que o coloca <b>{status}</b> da média de periculosidade das outras plataformas avaliadas ({avg_risco:.1f}%).</p>
                <p>Enquanto o <b>TikTok</b> e o <b>Facebook</b> permanecem como as feras mais vorazes na coleta de dados biometrizados e comportamentais, 
                o <b>{opcao}</b> apresenta uma sombra particular focada em <i>{analise['palavra_mais_critica']}</i>. 
                Em comparação aos outros convidados deste baile, sua postura exige vigilância { "redobrada" if status == "acima" else "moderada" }.</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">FGV-ECMI | Aluna: Keidy Alves Pizzetti Amaro | Prof. Josir Gomes</div>', unsafe_allow_html=True)
