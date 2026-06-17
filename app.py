import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import os
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import json
from io import BytesIO

# Importação do motor de PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
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

# --- ESTILO VISUAL "A BELA E A FERA" ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
        
        .stApp { background-color: #FAF5EC; color: #2C1E21; font-family: 'Lora', serif; }
        
        h1, h2, h3, h4 { font-family: 'Cinzel', serif !important; color: #162E5C !important; font-weight: 600; }
        
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

        .red-flag-box {
            background-color: #FFF5F5;
            border-left: 5px solid #991B1B;
            padding: 20px;
            border-radius: 4px;
        }

        .tag-risco {
            background-color: #991B1B; color: white; padding: 8px 16px; 
            border-radius: 20px 4px 20px 4px; margin: 5px; 
            display: inline-block; font-weight: bold; font-size: 0.8rem;
            border: 1px solid #7F1D1D;
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
            margin-top: 80px; border-top: 1px dashed #D4AF37; padding-top: 25px; color: #6B5B52;
        }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA API GEMINI ---
# No Streamlit Cloud, adicione sua chave nos "Secrets" com o nome GEMINI_API_KEY
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets do Streamlit.")
    client = None

# --- MODELOS DE DADOS ---
class DicaSeguranca(BaseModel):
    titulo: str = Field(description="Título da ação de proteção.")
    passos: list[str] = Field(description="3 a 5 passos sequenciais simples para leigos.")

class AnalisePrivacidade(BaseModel):
    resumo_claro: str = Field(description="Resumo simples do termo.")
    red_flags: list[str] = Field(description="Lista de termos de risco.")
    palavra_mais_critica: str = Field(description="O maior risco isolado.")
    pontuacao_risco: int = Field(description="Nota 0 a 100.")
    dicas_protecao: list[DicaSeguranca] = Field(description="3 dicas com passo a passo para leigos.")

# --- FUNÇÕES ---
def carregar_termo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.read()
    return None

@st.cache_data(show_spinner="Desvendando o pergaminho com IA...")
def analisar_termo_ia(texto, plataforma):
    prompt = f"Analise o termo de privacidade de {plataforma} focado em um usuário totalmente leigo. Gere um guia passo a passo de proteção. Termo: {texto}"
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalisePrivacidade,
                temperature=0.2
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Erro na análise: {e}")
        return None

def gerar_pdf_bytes(plataforma, analise):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Cores e Estilos do Castelo para o PDF
    azul_fera = colors.HexColor('#162E5C')
    ouro_bela = colors.HexColor('#D4AF37')
    verde_defesa = colors.HexColor('#2E7D32')

    title_style = ParagraphStyle('T1', parent=styles['Heading1'], textColor=azul_fera, alignment=1, fontSize=22)
    sub_style = ParagraphStyle('T2', parent=styles['Normal'], alignment=1, fontSize=12, spaceAfter=20)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], textColor=azul_fera, spaceBefore=15)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, leading=14)
    step_style = ParagraphStyle('Step', parent=styles['Normal'], leftIndent=20, textColor=verde_defesa, fontSize=10)

    elements = [
        Paragraph("<b>O ESPELHO DA VERDADE</b>", title_style),
        Paragraph(f"Escudo de Defesa de Privacidade: {plataforma}", sub_style),
        Spacer(1, 10),
        Paragraph("<b>Resumo da IA:</b>", h2_style),
        Paragraph(analise['resumo_claro'], body_style),
        Spacer(1, 10),
        Paragraph("<b>Guia Passo a Passo de Proteção:</b>", h2_style)
    ]

    for dica in analise['dicas_protecao']:
        elements.append(Paragraph(f"<b>• {dica['titulo']}</b>", body_style))
        for i, passo in enumerate(dica['passos'], 1):
            elements.append(Paragraph(f"{i}. {passo}", step_style))
        elements.append(Spacer(1, 8))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- MAPEAMENTOS ---
MAPA_PLATAFORMAS = {
    "Facebook": "Facebook.txt", "Instagram": "Instagram.txt", "Snapchat": "Snapchat.txt", 
    "TikTok": "Tiktok.txt", "Twitter (X)": "Twitter.txt", "WhatsApp": "Whatsapp.txt", "YouTube": "Youtube.txt"
}

MAPA_ICONES = {
    "Facebook": "https://img.icons8.com/fluency/96/facebook-new.png",
    "Instagram": "https://img.icons8.com/fluency/96/instagram-new.png",
    "Snapchat": "https://img.icons8.com/fluency/96/snapchat.png",
    "TikTok": "https://img.icons8.com/fluency/96/tiktok.png",
    "Twitter (X)": "https://img.icons8.com/fluency/96/twitterx.png",
    "WhatsApp": "https://img.icons8.com/fluency/96/whatsapp.png",
    "YouTube": "https://img.icons8.com/fluency/96/youtube-play.png"
}

# --- INTERFACE ---
st.markdown('<div style="text-align: center;"><h1>🌹 O Espelho da Verdade</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    opcao = st.selectbox("Selecione a plataforma para desvendar:", ["Selecione..."] + list(MAPA_PLATAFORMAS.keys()))

if opcao != "Selecione..." and client:
    texto_termo = carregar_termo(MAPA_PLATAFORMAS[opcao])
    if texto_termo:
        res = analisar_termo_ia(texto_termo, opcao)
        if res:
            col_main, col_side = st.columns([2, 1])
            
            with col_main:
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                        <img src="{MAPA_ICONES[opcao]}" width="70">
                        <h2 style="margin: 0;">{opcao}</h2>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f'<div class="parchment-card"><h3>📋 Resumo</h3>{res["resumo_claro"]}</div>', unsafe_allow_html=True)
            
            with col_side:
                st.markdown(f"""
                    <div class="score-container">
                        <div style="font-family: 'Cinzel'; font-size: 1rem;">NÍVEL DE RISCO</div>
                        <div class="score-number">{res['pontuacao_risco']}%</div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🚩 Sinais de Alerta")
                tags = "".join([f'<span class="tag-risco">{t}</span>' for t in res['red_flags']])
                st.markdown(tags, unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="red-flag-box" style="margin-top: 15px;">
                        <b style="color: #991B1B;">MAIOR RISCO IDENTIFICADO:</b><br>{res['palavra_mais_critica']}
                    </div>
                """, unsafe_allow_html=True)

            with c2:
                st.subheader("🛡️ Escudo de Defesa")
                st.write("Passo a passo para leigos:")
                for dica in res['dicas_protecao']:
                    with st.expander(f"⚙️ {dica['titulo']}"):
                        for i, p in enumerate(dica['passos'], 1):
                            st.write(f"**{i}.** {p}")
                
                if PDF_DISPONIVEL:
                    pdf_data = gerar_pdf_bytes(opcao, res)
                    st.download_button(
                        label="📜 Baixar Escudo em PDF",
                        data=pdf_data,
                        file_name=f"Escudo_Privacidade_{opcao}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

st.markdown('<div class="footer">Aluna FGV-ECMI: Keidy Alves Pizzetti Amaro | Orientador: Prof. Josir Gomes</div>', unsafe_allow_html=True)
```

---

### 2. O arquivo de bibliotecas (`requirements.txt`)

Crie um arquivo com esse nome exato no seu repositório do GitHub. O Streamlit usará ele para instalar as funções de IA e PDF:

```text
google-genai
pandas
requests
reportlab
pydantic
