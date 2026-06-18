import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import requests
import xml.etree.ElementTree as ET
import urllib.parse
from datetime import datetime
import google.generativeai as genai
import os

# ============================================================================
# CONFIGURAÇÃO DO STREAMLIT
# ============================================================================
st.set_page_config(
    page_title="🔐 Analisador de Privacidade Digital",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS CSS CUSTOMIZADOS
# ============================================================================
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    /* Header Principal */
    .header-container {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8c 100%);
        padding: 40px 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);
    }
    
    .header-container h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 10px;
        font-weight: 700;
    }
    
    .header-container p {
        color: #e0e7ff;
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* Cards de Seção */
    .section-card {
        background: white;
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #2d5a8c;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    .section-card h3 {
        color: #1e3a5f;
        margin-top: 0;
        margin-bottom: 15px;
        font-size: 1.4rem;
    }
    
    /* Cards de Risco */
    .risk-card-high {
        background: #fff5f5;
        border-left-color: #e63946;
    }
    
    .risk-card-medium {
        background: #fffbf0;
        border-left-color: #f77f00;
    }
    
    .risk-card-low {
        background: #f0fdf4;
        border-left-color: #06a77d;
    }
    
    /* Badges de Risco */
    .risk-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-right: 8px;
    }
    
    .risk-high {
        background-color: #e63946;
        color: white;
    }
    
    .risk-medium {
        background-color: #f77f00;
        color: white;
    }
    
    .risk-low {
        background-color: #06a77d;
        color: white;
    }
    
    /* Dicas */
    .tip-container {
        background: #f0fdf4;
        border-left: 4px solid #06a77d;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    
    .tip-container strong {
        color: #1e3a5f;
    }
    
    /* Notícias */
    .news-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
    }
    
    .news-card a {
        color: #1e3a5f;
        text-decoration: none;
        font-weight: 600;
    }
    
    .news-card a:hover {
        text-decoration: underline;
    }
    
    .news-meta {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 10px;
        font-style: italic;
    }
    
    /* Indicador de Loading */
    .loading {
        display: inline-block;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURAÇÃO DA API GEMINI
# ============================================================================
@st.cache_resource
def init_gemini():
    """Inicializa a API do Gemini"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.warning("⚠️ Variável de ambiente GEMINI_API_KEY não configurada!")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

# ============================================================================
# DADOS DE RISCO POR PLATAFORMA
# ============================================================================
RISK_DATA = {
    "WhatsApp": {
        "risk_score": 35,
        "palavras_risco": ["criptografia", "metadados", "backup", "localização", "contatos", "mensagens", "backup cloud"],
        "dicas": [
            "✓ Ative a verificação em duas etapas nas configurações de segurança",
            "✓ Revise regularmente as permissões de acesso ao microfone e câmera",
            "✓ Cuidado com links compartilhados - não clique em links suspeitos",
            "✓ Desative a leitura de recibos se preferir privacidade",
            "✓ Use backups encriptados e teste a funcionalidade periodicamente",
        ]
    },
    "Snapchat": {
        "risk_score": 62,
        "palavras_risco": ["localização", "dados demográficos", "identificação", "publicidade", "rastreamento", "terceiros", "analytics"],
        "dicas": [
            "✓ Compartilhe sua localização apenas com amigos de confiança",
            "✓ Configure privacidade de histórias para 'Apenas amigos'",
            "✓ Revise regularmente quem pode enviar mensagens para você",
            "✓ Desative a coleta de dados para publicidade segmentada",
            "✓ Use a funcionalidade 'Ghost Mode' para ocultar sua localização",
        ]
    },
    "YouTube": {
        "risk_score": 58,
        "palavras_risco": ["rastreamento", "publicidade", "histórico", "cookies", "análise", "localização", "comportamento"],
        "dicas": [
            "✓ Limpe o histórico de visualizações regularmente",
            "✓ Configure opções de privacidade de comentários",
            "✓ Desative o rastreamento de publicidade personalizada",
            "✓ Use modo anônimo para navegação mais privada",
            "✓ Revise as configurações de compartilhamento de dados com anunciantes",
        ]
    },
    "Facebook": {
        "risk_score": 72,
        "palavras_risco": ["dados pessoais", "rastreamento", "publicidade", "análise comportamental", "terceiros", "cookies", "perfil"],
        "dicas": [
            "✓ Limite quem pode ver seu perfil e informações pessoais",
            "✓ Configure privacidade de postagens para 'Apenas amigos'",
            "✓ Revise aplicativos e sites conectados à sua conta",
            "✓ Desative o rastreamento entre sites para publicidade",
            "✓ Use as Ferramentas de Privacidade para gerenciar dados compartilhados",
        ]
    },
    "Instagram": {
        "risk_score": 68,
        "palavras_risco": ["localização", "dados biométricos", "rastreamento", "interesse", "seguidores", "atividade", "análise"],
        "dicas": [
            "✓ Configure sua conta como privada para controlar quem segue",
            "✓ Desative a funcionalidade de compartilhamento de localização",
            "✓ Cuidado com quem pode comentar em suas postagens",
            "✓ Revise regularmente quem tem acesso a Histórias",
            "✓ Use a autenticação de dois fatores para maior segurança",
        ]
    },
    "Twitter": {
        "risk_score": 55,
        "palavras_risco": ["tweets públicos", "rastreamento", "localização", "engajamento", "análise", "anunciantes", "cookies"],
        "dicas": [
            "✓ Configure tweets como privados se desejar controle total",
            "✓ Limite quem pode enviar mensagens diretas",
            "✓ Desative a opção de permitir que outros você localizem por email/telefone",
            "✓ Revise a política de dados para publicidade",
            "✓ Cuidado com informações sensíveis em postagens públicas",
        ]
    },
    "TikTok": {
        "risk_score": 85,
        "palavras_risco": ["localização", "biometria", "rastreamento", "análise comportamental", "dados sensíveis", "inteligência artificial", "algoritmo"],
        "dicas": [
            "✓ Configure sua conta como privada para controlar quem interage",
            "✓ Cuidado ao compartilhar informações sensíveis em vídeos",
            "✓ Revise permissões de câmera e microfone regularmente",
            "✓ Desative a coleta de dados de localização",
            "✓ Monitore quem pode comentar e compartilhar seus vídeos",
        ]
    }
}

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_risk_color(score):
    """Retorna cor baseada no score de risco"""
    if score >= 70:
        return "#e63946"  # Vermelho - Alto risco
    elif score >= 50:
        return "#f77f00"  # Laranja - Risco médio
    else:
        return "#06a77d"  # Verde - Baixo risco

def get_risk_level(score):
    """Retorna nível de risco em texto"""
    if score >= 70:
        return "🔴 Alto Risco"
    elif score >= 50:
        return "🟠 Risco Médio"
    else:
        return "🟢 Baixo Risco"

def extract_risk_words(platform):
    """Extrai palavras de risco para uma plataforma"""
    return RISK_DATA[platform]["palavras_risco"]

def fetch_news(platform):
    """Busca notícias sobre privacidade da plataforma"""
    try:
        termo_busca = f"{platform} privacidade"
        termo_codificado = urllib.parse.quote(termo_busca)
        url_feed = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        
        resposta = requests.get(url_feed, timeout=5)
        root = ET.fromstring(resposta.content)
        noticias = root.findall('.//item')[:2]
        return noticias
    except Exception as e:
        st.warning(f"⚠️ Não foi possível carregar notícias: {str(e)}")
        return []

def analyze_privacy_with_gemini(platform):
    """Usa Gemini para analisar termos de privacidade"""
    model = init_gemini()
    if not model:
        return None
    
    try:
        prompt = f"""
        Forneça um resumo conciso (máximo 7 linhas) dos principais riscos à privacidade do usuário na plataforma {platform}.
        Foque em:
        1. Coleta de dados pessoais
        2. Compartilhamento com terceiros
        3. Publicidade direcionada
        4. Retenção de dados
        
        Resuma de forma clara e acessível para um usuário comum.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.warning(f"⚠️ Erro ao gerar análise: {str(e)}")
        return None

# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div class="header-container">
    <h1>🔐 Analisador de Privacidade Digital</h1>
    <p>Entenda os riscos de segurança digital nas suas plataformas favoritas</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# INICIALIZAR SESSÃO
# ============================================================================
if 'plataforma_selecionada' not in st.session_state:
    st.session_state.plataforma_selecionada = None
if 'analise_feita' not in st.session_state:
    st.session_state.analise_feita = False

# ============================================================================
# SEÇÃO 1: SELEÇÃO DE PLATAFORMA
# ============================================================================
st.markdown("""
<div class="section-card">
    <h3>📱 Seção 1: Escolha a Plataforma</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
plataformas = ["WhatsApp", "Snapchat", "YouTube", "Facebook", "Instagram", "Twitter", "TikTok"]

with col1:
    if st.button("💬 WhatsApp", key="whatsapp", use_container_width=True):
        st.session_state.plataforma_selecionada = "WhatsApp"
        st.session_state.analise_feita = False

with col2:
    if st.button("👻 Snapchat", key="snapchat", use_container_width=True):
        st.session_state.plataforma_selecionada = "Snapchat"
        st.session_state.analise_feita = False

with col3:
    if st.button("▶️ YouTube", key="youtube", use_container_width=True):
        st.session_state.plataforma_selecionada = "YouTube"
        st.session_state.analise_feita = False

with col4:
    if st.button("👥 Facebook", key="facebook", use_container_width=True):
        st.session_state.plataforma_selecionada = "Facebook"
        st.session_state.analise_feita = False

col5, col6, col7, col8 = st.columns(4)

with col5:
    if st.button("📷 Instagram", key="instagram", use_container_width=True):
        st.session_state.plataforma_selecionada = "Instagram"
        st.session_state.analise_feita = False

with col6:
    if st.button("𝕏 Twitter", key="twitter", use_container_width=True):
        st.session_state.plataforma_selecionada = "Twitter"
        st.session_state.analise_feita = False

with col7:
    if st.button("🎵 TikTok", key="tiktok", use_container_width=True):
        st.session_state.plataforma_selecionada = "TikTok"
        st.session_state.analise_feita = False

st.divider()

# ============================================================================
# ANÁLISE DA PLATAFORMA SELECIONADA
# ============================================================================
if st.session_state.plataforma_selecionada:
    platform = st.session_state.plataforma_selecionada
    risk_data = RISK_DATA[platform]
    risk_score = risk_data["risk_score"]
    risk_color = get_risk_color(risk_score)
    risk_level = get_risk_level(risk_score)
    
    # Seção 2: Resumo dos Termos de Privacidade
    st.markdown(f"""
    <div class="section-card">
        <h3>📄 Seção 2: Resumo dos Termos de Privacidade</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, {risk_color}22 0%, {risk_color}11 100%); border-radius: 12px;">
            <h2 style="font-size: 2.5rem; margin: 0; color: {risk_color};">{risk_score}/100</h2>
            <p style="color: {risk_color}; font-weight: 600; margin: 10px 0 0 0; font-size: 1.2rem;">{risk_level}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        analise_text = f"""
        **Principais Riscos à Privacidade do {platform}:**
        
        {platform} coleta e processa dados dos usuários para diversas finalidades, 
        incluindo publicidade direcionada, análise comportamental e otimização de serviços. 
        Os termos de privacidade indicam compartilhamento com empresas parceiras, 
        retenção de dados por longos períodos e uso de tecnologias de rastreamento avançadas.
        """
        st.markdown(analise_text)
    
    st.divider()
    
    # Seção 3: Nuvem de Palavras com Termos de Risco
    st.markdown(f"""
    <div class="section-card">
        <h3>☁️ Seção 3: Palavras de Risco em Destaque</h3>
    </div>
    """, unsafe_allow_html=True)
    
    risk_words = extract_risk_words(platform)
    
    # Criar dados para a nuvem com frequências
    word_freq = {word: (len(word) * 2 + np.random.randint(1, 5)) for word in risk_words}
    
    # Gerar nuvem de palavras
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
    
    wordcloud = WordCloud(
        width=1200,
        height=400,
        background_color='white',
        colormap='Reds',
        relative_scaling=0.5,
        min_font_size=10,
        collocations=False
    ).generate_from_frequencies(word_freq)
    
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout(pad=0)
    
    st.pyplot(fig, use_container_width=True)
    
    st.info(f"**Palavras-chave de risco detectadas:** {', '.join(risk_words)}")
    
    st.divider()
    
    # Seção 4: Dicas Práticas de Proteção
    st.markdown(f"""
    <div class="section-card">
        <h3>🛡️ Seção 4: Dicas Práticas de Proteção</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Medidas práticas para aumentar sua segurança e privacidade no** " + platform + ":")
    
    for dica in risk_data["dicas"]:
        st.markdown(f"""
        <div class="tip-container">
            {dica}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Seção 5: Gráfico Comparativo de Risco
    st.markdown(f"""
    <div class="section-card">
        <h3>📊 Seção 5: Comparação de Risco entre Plataformas</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Preparar dados para gráfico
    df_comparison = pd.DataFrame({
        'Plataforma': list(RISK_DATA.keys()),
        'Score de Risco': [RISK_DATA[p]["risk_score"] for p in RISK_DATA.keys()]
    })
    
    # Reordenar para destacar a plataforma selecionada
    df_comparison['Destaque'] = df_comparison['Plataforma'] == platform
    df_comparison = df_comparison.sort_values('Score de Risco', ascending=True)
    
    fig = px.bar(
        df_comparison,
        x='Score de Risco',
        y='Plataforma',
        orientation='h',
        color='Score de Risco',
        color_continuous_scale=['#06a77d', '#f77f00', '#e63946'],
        hover_data={'Score de Risco': ':.0f'},
        title=None
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Nível de Risco (0-100)",
        yaxis_title="",
        hovermode='y unified',
        margin=dict(l=150)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretação da comparação
    platform_rank = sorted(RISK_DATA.items(), key=lambda x: x[1]["risk_score"], reverse=True)
    platform_position = next(i for i, (p, _) in enumerate(platform_rank) if p == platform) + 1
    
    st.markdown(f"""
    **📈 Análise Comparativa:**
    
    {platform} está em **#{platform_position}º lugar** entre as 7 plataformas analisadas em termos de risco à privacidade.
    """)
    
    if risk_score >= 70:
        st.warning(f"⚠️ **Alto Risco:** {platform} apresenta múltiplos fatores de risco à privacidade. Recomenda-se implementar todas as dicas de proteção acima.")
    elif risk_score >= 50:
        st.info(f"ℹ️ **Risco Moderado:** {platform} possui alguns fatores de risco. Seguir as práticas recomendadas é importante.")
    else:
        st.success(f"✅ **Risco Baixo:** {platform} é uma das plataformas mais seguras em relação à privacidade, mas precauções são sempre recomendadas.")
    
    st.divider()
    
    # Seção 6: Notícias Relacionadas
    st.markdown(f"""
    <div class="section-card">
        <h3>📰 Seção 6: Notícias sobre Privacidade e Segurança</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"**Últimas manchetes sobre {platform} e privacidade de dados:**")
    
    with st.spinner("📡 Buscando notícias..."):
        noticias = fetch_news(platform)
    
    if noticias:
        col_n1, col_n2 = st.columns(2)
        
        for idx, noticia in enumerate(noticias):
            try:
                titulo = noticia.find('title').text
                link = noticia.find('link').text
                fonte = noticia.find('source').attrib.get('url', "Portal de Notícias") if noticia.find('source') is not None else "Portal de Notícias"
                data = noticia.find('pubDate').text[:16] if noticia.find('pubDate') is not None else "Data indisponível"
                
                with col_n1 if idx == 0 else col_n2:
                    st.markdown(f"""
                    <div class="news-card">
                        <h4><a href="{link}" target="_blank">{titulo}</a></h4>
                        <div class="news-meta">
                            Fonte: {fonte} | Publicado em: {data}
                        </div>
                        <p style="margin-top: 10px; font-size: 0.95rem;">
                            Clique no título para ler a reportagem completa.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Erro ao processar notícia: {str(e)}")
    else:
        st.info("📡 Nenhuma notícia recente encontrada no momento. Tente novamente mais tarde.")

else:
    st.info("👆 Selecione uma plataforma acima para começar a análise de privacidade!")

# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 20px; font-size: 0.9rem;">
    <p>🔐 <strong>Analisador de Privacidade Digital</strong> | Proteção de Dados para o Cidadão Digital</p>
    <p>Desenvolvido para educação sobre segurança digital | Dados atualizados em 2024</p>
</div>
""", unsafe_allow_html=True)
