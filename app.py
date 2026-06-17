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
from io import BytesIO

# --- MOTOR DE PDF REVISADO ---
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

# --- ESTILO CSS (A BELA E A FERA) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
        
        .stApp { background-color: #FAF5EC; color: #2C1E21; font-family: 'Lora', serif; }
        
        h1, h2, h3, h4 { font-family: 'Cinzel', serif !important; color: #162E5C !important; }
        
        .gold-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #D4AF37, transparent);
            margin: 25px 0;
        }
        
        .parchment-card {
            background-color: #FFFFFF;
            border: 1px solid #E6D9C5;
            border-top: 4px solid #D4AF37;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }

        /* Nuvem de Palavras Customizada */
        .word-cloud-container {
            padding: 20px;
            text-align: center;
            line-height: 2.5;
            background: #FFFDF9;
            border-radius: 10px;
            border: 1px dashed #D4AF37;
        }

        /* Quadro de Atenção */
        .attention-box {
            background-color: #FFF5F5;
            border: 2px solid #991B1B;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-top: 20px;
            position: relative;
        }

        .attention-label {
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: #991B1B;
            color: white;
            padding: 2px 15px;
            font-family: 'Cinzel', serif;
            font-size: 0.8rem;
            border-radius: 4px;
        }

        .score-container {
            text-align: center;
            background: linear-gradient(135deg, #162E5C 0%, #0B1D3A 100%);
            color: #FAF5EC; padding: 30px; border-radius: 12px;
            border: 2px solid #D4AF37;
        }

        .score-number { font-family: 'Cinzel', serif; font-size: 4rem; color: #F5D04C; line-height: 1; }

        .footer {
            font-family: 'Cinzel', serif; font-size: 0.8rem; text-align: center;
            margin-top: 50px; border-top: 1px dashed #D4AF37; padding-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- MODELOS E BANCO DE DADOS ---
class DicaSeguranca(BaseModel):
    titulo: str = Field(description="Título curto da dica.")
    passos: list[str] = Field(description="3 a 5 passos simples.")

class AnalisePrivacidade(BaseModel):
    resumo_claro: str = Field(description="Resumo do termo.")
    red_flags: list[str] = Field(description="5-8 termos de risco.")
    palavra_mais_critica: str = Field(description="O maior risco.")
    pontuacao_risco: int = Field(description="Nota 0 a 100.")
    dicas_protecao: list[DicaSeguranca] = Field(description="3 dicas detalhadas.")

# (Acervo de contingência resumido para o exemplo)
ACERVO_CONTINGENCIA = {
    "Facebook": {"resumo_claro": "O Facebook monitora intensamente sua atividade fora do app...", "red_flags": ["Rastreamento", "Cookies", "Perfilamento", "Algoritmos", "Big Data"], "palavra_mais_critica": "Venda de Metadados", "pontuacao_risco": 88, "dicas_protecao": [{"titulo": "Desativar Rastreamento", "passos": ["Menu > Configurações", "Privacidade", "Atividade fora do FB > Desativar"]}]},
    "Instagram": {"resumo_claro": "O Instagram coleta dados de localização e interesses visuais...", "red_flags": ["IA", "Fotos", "Localização", "Reconhecimento", "Ads"], "palavra_mais_critica": "Treinamento de IA", "pontuacao_risco": 85, "dicas_protecao": [{"titulo": "Privacidade da Conta", "passos": ["Perfil > Menu", "Configurações", "Conta Privada"]}]},
    "TikTok": {"resumo_claro": "O TikTok possui regras invasivas de biometria e teclado...", "red_flags": ["Biometria", "Teclado", "China", "Navegador", "Algoritmo"], "palavra_mais_critica": "Coleta Biométrica", "pontuacao_risco": 90, "dicas_protecao": [{"titulo": "Navegador Externo", "passos": ["Não use o navegador do app", "Abra no Chrome ou Safari"]}]},
    "WhatsApp": {"resumo_claro": "O WhatsApp compartilha metadados de conexões com a Meta...", "red_flags": ["Metadados", "Contatos", "IP", "Status", "Backup"], "palavra_mais_critica": "Metadados de Conexão", "pontuacao_risco": 55, "dicas_protecao": [{"titulo": "Proteger IP", "passos": ["Configurações > Privacidade", "Avançado", "Proteger IP"]}]},
    "YouTube": {"resumo_claro": "O YouTube unifica seu histórico com a conta Google...", "red_flags": ["Histórico", "Perfilamento", "Google", "Padrão de Sono", "Crianças"], "palavra_mais_critica": "Rastreamento Unificado", "pontuacao_risco": 70, "dicas_protecao": [{"titulo": "Pausar Histórico", "passos": ["Perfil > Histórico", "Pausar", "Limpar dados"]}]},
    "Twitter (X)": {"resumo_claro": "O X utiliza seus posts para treinar o Grok sem permissão clara...", "red_flags": ["Grok", "IA", "Extração", "Dados Biométricos", "Posts"], "palavra_mais_critica": "Treinamento de IA Grok", "pontuacao_risco": 75, "dicas_protecao": [{"titulo": "Configurar Grok", "passos": ["Privacidade > Grok", "Desativar treinamento"]}]},
    "Snapchat": {"resumo_claro": "O Snapchat rastreia localização em tempo real no SnapMap...", "red_flags": ["Mapa", "Filtros", "Realidade Aumentada", "Sprints", "Memórias"], "palavra_mais_critica": "Snap Map (Geolocalização)", "pontuacao_risco": 65, "dicas_protecao": [{"titulo": "Modo Fantasma", "passos": ["Mapa > Engrenagem", "Modo Fantasma > Ativar"]}]}
}

# --- FUNÇÕES ---
@st.cache_data
def analisar_ia(texto, plataforma):
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        resp = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"Analise o termo de {plataforma}: {texto}",
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=AnalisePrivacidade)
        )
        return json.loads(resp.text), False
    except:
        return ACERVO_CONTINGENCIA.get(plataforma), True

def gerar_pdf_corrigido(plataforma, analise):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Estilos seguros
    title_style = ParagraphStyle('T', parent=styles['Heading1'], textColor=colors.HexColor('#162E5C'), alignment=1)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], textColor=colors.HexColor('#162E5C'), spaceBefore=10)
    body_style = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, spaceAfter=8)
    
    story = [
        Paragraph(f"<b>ESCUDO DE DEFESA: {plataforma}</b>", title_style),
        Spacer(1, 15),
        Paragraph(f"<b>Risco Geral: {analise['pontuacao_risco']}%</b>", h2_style),
        Paragraph(analise['resumo_claro'], body_style),
        Spacer(1, 10),
        Paragraph("<b>PASSO A PASSO DE PROTEÇÃO:</b>", h2_style)
    ]
    
    for dica in analise['dicas_protecao']:
        story.append(Paragraph(f"<b>• {dica['titulo']}</b>", body_style))
        for p in dica['passos']:
            story.append(Paragraph(f"- {p}", body_style))
        story.append(Spacer(1, 5))
        
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
    # Aqui você carregaria o arquivo .txt real. Usando mock para o exemplo.
    analise, fallback = analisar_ia("Texto do contrato...", opcao)
    
    if analise:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"""<div style="display: flex; align-items: center; gap: 15px;"><img src="{MAPA_ICONES[opcao]}" width="60"><h3>Relatório de {opcao}</h3></div>""", unsafe_allow_html=True)
            st.markdown(f'<div class="parchment-card">{analise["resumo_claro"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="score-container"><div class="score-number">{analise["pontuacao_risco"]}%</div><div style="font-family:Cinzel">Risco Detectado</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        f1, f2 = st.columns(2)
        with f1:
            st.subheader("🚩 Sinais de Alerta")
            # Nuvem de Palavras via CSS
            tags_html = ""
            for tag in analise['red_flags']:
                size = random.uniform(1, 2.2)
                opacity = random.uniform(0.6, 1)
                tags_html += f'<span style="font-size:{size}rem; opacity:{opacity}; margin: 10px; display: inline-block; color:#991B1B; font-family:Cinzel;">{tag}</span>'
            
            st.markdown(f'<div class="word-cloud-container">{tags_html}</div>', unsafe_allow_html=True)
            
            # Quadro de ATENÇÃO
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
                pdf = gerar_pdf_corrigido(opcao, analise)
                st.download_button("📜 Baixar Guia em PDF", data=pdf, file_name=f"Escudo_{opcao}.pdf", mime="application/pdf", use_container_width=True)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # --- GRÁFICO PREMIM PLOTLY ---
        st.subheader("📊 Comparativo de Periculosidade")
        df_plot = pd.DataFrame({
            'Plataforma': ["Facebook", "Instagram", "Snapchat", "TikTok", "Twitter (X)", "WhatsApp", "YouTube"],
            'Risco': [88, 85, 65, 90, 75, 55, 70]
        }).sort_values('Risco', ascending=True)

        fig = px.bar(df_plot, x='Risco', y='Plataforma', orientation='h',
                     color='Risco', color_continuous_scale=['#F5D04C', '#D4AF37', '#991B1B'])
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_family="Cinzel", font_color="#162E5C",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=False, range=[0, 100]), yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Relatório de Interpretação
        st.markdown(f"""
            <div class="parchment-card" style="border-top: 4px solid #162E5C;">
                <h4 style="margin-top:0">📜 Interpretação do Espelho</h4>
                <p>O gráfico acima revela a hierarquia das sombras no reino digital. 
                Observamos que o <b>TikTok</b> e o <b>Facebook</b> se posicionam como as "Feras" mais dominantes, 
                apresentando níveis de risco acima de 85% devido à coleta agressiva de dados biométricos e comportamentais. 
                Em contrapartida, o <b>WhatsApp</b>, embora pertença à Meta, figura como o "Convidado" mais seguro desta lista, 
                protegido por sua criptografia de mensagens, embora ainda exija cautela com seus metadados.</p>
                <p>Plataformas como <b>YouTube</b> e <b>Instagram</b> mantêm um equilíbrio perigoso, 
                onde a conveniência do serviço oculta um perfilamento profundo de seus usuários.</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">FGV-ECMI | Aluna: Keidy Alves Pizzetti Amaro | Prof. Josir Gomes</div>', unsafe_allow_html=True)
