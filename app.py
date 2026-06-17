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

# Importação segura do motor de PDF para garantir resiliência
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

# --- ESTILO VISUAL "A BELA E A FERA" ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
        
        /* Fundo em pergaminho clássico */
        .stApp { 
            background-color: #FAF5EC; 
            color: #2C1E21; 
            font-family: 'Lora', serif; 
        }
        
        /* Títulos imperiais em Azul Real */
        h1, h2, h3, h4, h5, h6 { 
            font-family: 'Cinzel', serif !important; 
            color: #162E5C !important; 
            font-weight: 600; 
            letter-spacing: 1px;
        }
        
        /* Divisor dourado reluzente */
        .gold-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #D4AF37, transparent);
            margin: 25px 0;
        }
        
        /* Cartão de pergaminho branco com borda dourada superior */
        .parchment-card {
            background-color: #FFFFFF;
            border: 1px solid #E6D9C5;
            border-top: 4px solid #D4AF37;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 6px 15px rgba(44, 30, 33, 0.04);
            margin-bottom: 20px;
        }

        /* Caixa de alerta em vermelho carmesim */
        .red-flag-box {
            background-color: #FFF5F5;
            border-left: 5px solid #991B1B;
            border-top: 1px solid #F3E8E8;
            border-right: 1px solid #F3E8E8;
            border-bottom: 1px solid #F3E8E8;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        
        .atencao-texto { 
            color: #991B1B; 
            font-family: 'Cinzel', serif;
            font-weight: bold; 
            font-size: 1.1rem; 
            margin-bottom: 8px;
            letter-spacing: 1.5px;
        }

        /* Tags de risco modeladas como pétalas de rosa */
        .tag-risco {
            background-color: #991B1B; 
            color: #FFFDF9; 
            padding: 8px 16px; 
            border-radius: 20px 4px 20px 4px; 
            margin: 6px; 
            display: inline-block; 
            font-weight: bold;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 6px rgba(153, 27, 27, 0.15);
            border: 1px solid #7F1D1D;
        }

        /* Indicador do nível de risco com gradiente */
        .score-container {
            text-align: center;
            background: linear-gradient(135deg, #162E5C 0%, #0B1D3A 100%);
            color: #FAF5EC; 
            padding: 30px; 
            border-radius: 12px;
            border: 2px solid #D4AF37;
            box-shadow: 0 8px 25px rgba(22, 46, 92, 0.2);
        }

        .score-number { 
            font-family: 'Cinzel', serif; 
            font-size: 4rem; 
            color: #F5D04C; 
            line-height: 1; 
            text-shadow: 0 0 10px rgba(245, 208, 76, 0.3);
        }

        /* Rodapé clássico */
        .footer {
            font-family: 'Cinzel', serif; 
            font-size: 0.8rem; 
            text-align: center;
            margin-top: 80px; 
            border-top: 1px dashed #D4AF37; 
            padding-top: 25px; 
            color: #6B5B52;
            letter-spacing: 1px;
        }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA API GEMINI ---
try:
    # No Streamlit Cloud, adicione sua chave nos "Secrets" com o nome GEMINI_API_KEY
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets do Streamlit.")
    client = None

# --- MODELOS DE DADOS PARA A RESPOSTA ESTRUTURADA ---
class DicaSeguranca(BaseModel):
    titulo: str = Field(description="Título curto, direto e claro sobre a ação de proteção (ex: 'Limitar Anúncios Personalizados').")
    passos: list[str] = Field(description="Lista com exatamente 3 a 5 passos sequenciais extremamente simples de executar nas configurações do celular ou do app para leigos.")

class AnalisePrivacidade(BaseModel):
    resumo_claro: str = Field(description="Um resumo simples, claro e de fácil compreensão do termo de privacidade focado em usuários leigos.")
    red_flags: list[str] = Field(description="Lista de 5 a 8 palavras ou conceitos de risco (ex: Rastreamento, Compartilhamento com Terceiros).")
    palavra_mais_critica: str = Field(description="O conceito ou termo que representa o risco mais sério e urgente.")
    pontuacao_risco: int = Field(description="Nota geral de risco de 0 a 100 baseado na severidade do termo.")
    dicas_protecao: list[DicaSeguranca] = Field(description="Lista contendo exatamente 3 dicas de proteção detalhadas com passo a passo para leigos.")

# --- FUNÇÕES ---
def carregar_termo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.read()
    return None

@st.cache_data(show_spinner="Desvendando o pergaminho de termos de privacidade com IA...")
def analisar_termo_ia(texto, plataforma):
    if not client:
        return None
    
    prompt = (
        f"Analise o termo de privacidade de {plataforma} focado em um usuário totalmente leigo. "
        "Gere explicações simples e um guia passo a passo detalhado de proteção. "
        "Escreva os passos de cada dica como se estivesse ensinando uma pessoa com zero conhecimento de tecnologia. "
        f"Termo original: {texto}"
    )
    
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
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Erro na análise do Gemini: {e}")
        return None

def gerar_pdf_bytes(plataforma, analise):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    azul_fera = colors.HexColor('#162E5C')
    ouro_bela = colors.HexColor('#D4AF37')
    verde_defesa = colors.HexColor('#2E7D32')

    title_style = ParagraphStyle(
        'T1', 
        parent=styles['Heading1'], 
        textColor=azul_fera, 
        alignment=1, 
        fontSize=20,
        spaceAfter=5
    )
    sub_style = ParagraphStyle(
        'T2', 
        parent=styles['Normal'], 
        alignment=1, 
        fontSize=11, 
        textColor=colors.HexColor('#5C4B40'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'H2', 
        parent=styles['Heading2'], 
        textColor=azul_fera, 
        fontSize=13,
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body', 
        parent=styles['Normal'], 
        fontSize=10, 
        leading=14,
        textColor=colors.HexColor('#2C1E21')
    )
    step_style = ParagraphStyle(
        'Step', 
        parent=styles['Normal'], 
        leftIndent=15, 
        textColor=verde_defesa, 
        fontSize=9.5,
        leading=13,
        spaceAfter=4
    )

    elements = [
        Paragraph("<b>O ESPELHO DA VERDADE</b>", title_style),
        Paragraph(f"Escudo de Defesa & Manual de Configuração: {plataforma}", sub_style),
    ]
    
    # Linha divisória dourada elegante no PDF
    tabela_divisor = Table([['']], colWidths=[530], rowHeights=[2])
    tabela_divisor.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ouro_bela),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    
    elements.append(tabela_divisor)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>📋 Resumo do Termo de Privacidade:</b>", h2_style))
    elements.append(Paragraph(analise['resumo_claro'], body_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>🛡️ Manual Prático Passo a Passo (Sem Complicação):</b>", h2_style))

    for idx, dica in enumerate(analise['dicas_protecao'], 1):
        elements.append(Paragraph(f"<b>Opção {idx}: {dica['titulo']}</b>", ParagraphStyle('DicaTitle', parent=body_style, fontName='Helvetica-Bold', textColor=azul_fera, spaceBefore=6)))
        for j, passo in enumerate(dica['passos'], 1):
            elements.append(Paragraph(f"<b>Passo {j}:</b> {passo}", step_style))
        elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 10))
    elements.append(tabela_divisor)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Laudo de Segurança Gerado com IA | Aluna FGV-ECMI: Keidy Alves Pizzetti Amaro", ParagraphStyle('Foot', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.HexColor('#6B5B52'))))

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

# Dados pré-configurados do gráfico de nível de risco comparativo
dados_risco_global = {
    'Plataformas': ["Facebook", "Instagram", "Snapchat", "TikTok", "Twitter (X)", "WhatsApp", "YouTube"],
    'Nível de Risco (0-100)': [88, 85, 65, 90, 75, 55, 70]
}

# --- INTERFACE PRINCIPAL ---
st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <span style="font-size: 3.5rem; line-height: 1;">🌹</span>
        <h1 style="margin-top: 15px; font-size: 2.8rem; font-weight: 700;">O Espelho da Verdade</h1>
        <p style="font-style: italic; color: #5C4B40; font-size: 1.2rem; max-width: 700px; margin: 10px auto 0 auto;">
            Desmistificando os contratos de privacidade com inteligência artificial para que seus dados não fiquem presos em um feitiço de termos complexos.
        </p>
    </div>
""", unsafe_allow_html=True)
st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# Caixa de seleção da rede social desejada
col_sel_1, col_sel_2, col_sel_3 = st.columns([1, 2, 1])
with col_sel_2:
    opcao = st.selectbox("Selecione o pergaminho de privacidade de uma rede social:", ["Selecione..."] + list(MAPA_PLATAFORMAS.keys()))

if opcao != "Selecione..." and client:
    texto_termo = carregar_termo(MAPA_PLATAFORMAS[opcao])
    
    if texto_termo:
        res = analisar_termo_ia(texto_termo, opcao)
        if res:
            st.markdown("<br>", unsafe_allow_html=True)
            col_main, col_side = st.columns([2, 1])
            
            with col_main:
                # Cabeçalho da plataforma com o medalhão dourado do ícone
                st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 18px; margin-bottom: 20px;">
                        <div style="
                            background: #FFFFFF; 
                            border: 2px solid #D4AF37; 
                            border-radius: 50%; 
                            padding: 6px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                            box-shadow: 0 4px 12px rgba(212, 175, 55, 0.25);
                            width: 65px;
                            height: 65px;
                        ">
                            <img src="{MAPA_ICONES[opcao]}" style="width: 42px; height: 42px; object-fit: contain;" alt="{opcao} Icon" />
                        </div>
                        <h3 style="margin: 0 !important; font-size: 1.8rem; line-height: 1.2;">📋 Resumo sobre {opcao}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<div class="parchment-card" style="min-height: 220px;"><p style="font-size: 1.15rem; line-height: 1.6; margin: 0;">{res["resumo_claro"]}</p></div>', unsafe_allow_html=True)
            
            with col_side:
                # Medidor e barra de progresso do nível de risco
                progresso_html = f"""
                    <div style="background-color: rgba(255, 255, 255, 0.2); border-radius: 10px; height: 10px; width: 100%; overflow: hidden; margin-top: 15px;">
                        <div style="background: linear-gradient(90deg, #F5D04C 0%, #991B1B 100%); width: {res['pontuacao_risco']}%; height: 100%;"></div>
                    </div>
                """
                st.markdown(f"""
                    <div class="score-container" style="min-height: 220px; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-family: 'Cinzel'; font-size: 1rem; letter-spacing: 1.5px; text-transform: uppercase;">Nível de Risco</div>
                        <div class="score-number">{res['pontuacao_risco']}%</div>
                        {progresso_html}
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🚩 Sinais de Alerta no Contrato")
                st.write("Conceitos e termos críticos identificados no pergaminho de privacidade:")
                
                tags = "".join([f'<span class="tag-risco">{t}</span>' for t in res['red_flags']])
                st.markdown(tags, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="red-flag-box" style="margin-top: 20px;">
                        <div class="atencao-texto">⚠️ ELEMENTO CRÍTICO:</div>
                        <p style="font-size: 1.05rem; line-height: 1.5; margin: 0;">
                            O conceito mais sensível ou de maior risco encontrado neste termo de privacidade é: 
                            <span style="color: #991B1B; font-weight: bold; font-family: 'Cinzel', serif; font-size: 1.15rem;">
                                {res['palavra_mais_critica']}
                            </span>.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

            with c2:
                st.subheader("🛡️ Escudo de Defesa do Usuário")
                st.write("Siga os guias de configuração passo a passo extremamente didáticos para se proteger:")
                
                for idx, dica in enumerate(res['dicas_protecao'], 1):
                    with st.expander(f"⚙️ {idx}. {dica['titulo']}", expanded=(idx == 1)):
                        for step_idx, p in enumerate(dica['passos'], 1):
                            st.write(f"**{step_idx}º Passo:** {p}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Botão de download do laudo protetivo em formato PDF
                if PDF_DISPONIVEL:
                    pdf_data = gerar_pdf_bytes(opcao, res)
                    st.download_button(
                        label="📜 Baixar Escudo de Defesa em PDF",
                        data=pdf_data,
                        file_name=f"Escudo_Privacidade_{opcao}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.warning("O motor de PDF está temporariamente indisponível no servidor.")
            
            st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
            
            # Seção 3: Escala comparativa de riscos
            st.subheader("📊 A Escala de Risco no Reino Digital")
            st.markdown("Veja onde a plataforma selecionada se posiciona no comparativo geral de risco à segurança digital:")
            
            df_grafico = pd.DataFrame(dados_risco_global)
            st.bar_chart(data=df_grafico, x='Plataformas', y='Nível de Risco (0-100)', color='#D4AF37')
            
            st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
            
            # Seção 4: Feed de notícias relacionadas ao cenário de dados daquela plataforma
            st.subheader(f"📰 O Que Estão Falando Sobre a Privacidade do {opcao}?")
            st.markdown("Acompanhe notícias reais coletadas em tempo real sobre investigações ou mudanças de termos:")
            
            termo_busca = f"{opcao} privacidade"
            termo_codificado = urllib.parse.quote(termo_busca)
            url_feed = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

            try:
                resposta = requests.get(url_feed, timeout=5)
                root = ET.fromstring(resposta.content)
                noticias = root.findall('.//item')[:2]
                
                if noticias:
                    col_n1, col_n2 = st.columns(2)
                    
                    with col_n1:
                        titulo1 = noticias[0].find('title').text
                        link1 = noticias[0].find('link').text
                        fonte1 = noticias[0].find('source').text if noticias[0].find('source') is not None else "Portal de Notícias"
                        data1 = noticias[0].find('pubDate').text[:16]
                        
                        st.markdown(f"""
                            <div class="parchment-card" style="min-height: 200px;">
                                <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="{link1}" target="_blank" style="text-decoration: none; color: #162E5C;">{titulo1}</a></h4>
                                <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: {fonte1} | Publicado em: {data1}</p>
                                <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Clique no título acima para conferir a reportagem diretamente da fonte original.</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with col_n2:
                        if len(noticias) > 1:
                            titulo2 = noticias[1].find('title').text
                            link2 = noticias[1].find('link').text
                            fonte2 = noticias[1].find('source').text if noticias[1].find('source') is not None else "Portal de Notícias"
                            data2 = noticias[1].find('pubDate').text[:16]
                            
                            st.markdown(f"""
                                <div class="parchment-card" style="min-height: 200px;">
                                    <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="{link2}" target="_blank" style="text-decoration: none; color: #162E5C;">{titulo2}</a></h4>
                                    <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: {fonte2} | Publicado em: {data2}</p>
                                    <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe esta segunda cobertura jornalística clicando no link para entender os últimos acontecimentos.</p>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("Não encontramos notícias recentes específicas para esta plataforma no momento.")
            
            except Exception:
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    st.markdown(f"""
                        <div class="parchment-card" style="min-height: 200px;">
                            <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://g1.globo.com/tecnologia/" target="_blank" style="text-decoration: none; color: #162E5C;">{opcao} e investigações de tratamento de dados</a></h4>
                            <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: Portal G1 Tecnologia</p>
                            <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe notícias sobre as últimas auditorias da ANPD (Autoridade Nacional de Proteção de Dados) e processos regulatórios aplicados a empresas de tecnologia.</p>
                        </div>
                    """, unsafe_allow_html=True)
                with col_n2:
                    st.markdown(f"""
                        <div class="parchment-card" style="min-height: 200px;">
                            <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://www.bbc.com/portuguese/topics/c40g969r280t" target="_blank" style="text-decoration: none; color: #162E5C;">Mudanças nas políticas e regulamentações do {opcao}</a></h4>
                            <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: BBC Brasil</p>
                            <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Análise internacional sobre como novas diretrizes de inteligência artificial aplicadas à plataforma impactam os direitos de privacidade no Brasil.</p>
                        </div>
                    """, unsafe_allow_html=True)

# --- RODAPÉ REAL ---
st.markdown("""
    <div class="footer">
        Aluna FGV-ECMI: Keidy Alves Pizzetti Amaro | Orientador: Prof. Josir Gomes
    </div>
""", unsafe_allow_html=True)
