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

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Espelho da Verdade - Termos de Privacidade",
    page_icon="🌹",
    layout="wide"
)

# --- PALETA DE CORES & ESTILO "A BELA E A FERA" ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
        
        /* Tema Geral e Fundo de Pergaminho Real */
        .stApp { 
            background-color: #FAF5EC; 
            color: #2C1E21; 
            font-family: 'Lora', serif;
        }
        
        /* Títulos e Subtítulos Clássicos */
        h1, h2, h3, h4, h5, h6 { 
            font-family: 'Cinzel', serif !important; 
            color: #162E5C !important; /* Azul Imperial (Fera) */
            font-weight: 600;
            letter-spacing: 1px;
        }
        
        /* Divisores Decorativos Dourados */
        .gold-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #D4AF37, transparent); /* Ouro Real (Bela) */
            margin: 25px 0;
        }
        
        /* Cartão de Pergaminho para Resumos e Notícias */
        .parchment-card {
            background-color: #FFFFFF;
            border: 1px solid #E6D9C5;
            border-top: 4px solid #D4AF37;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 6px 15px rgba(44, 30, 33, 0.04);
            margin-bottom: 20px;
        }
        
        /* Caixa de Defesa / Dicas */
        .defense-box {
            background-color: #F0F6F0;
            border-left: 5px solid #2E7D32; /* Verde Floresta */
            border-top: 1px solid #E2EFE2;
            border-right: 1px solid #E2EFE2;
            border-bottom: 1px solid #E2EFE2;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        
        .defenda-se-texto {
            color: #2E7D32;
            font-family: 'Cinzel', serif;
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 8px;
            letter-spacing: 1.5px;
        }

        /* Caixa de Alerta / Rosa Encantada */
        .red-flag-box {
            background-color: #FFF5F5;
            border-left: 5px solid #991B1B; /* Vermelho Carmesim (Rosa) */
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
        
        /* Tags de Risco modeladas como Pétalas de Rosa */
        .tag-risco {
            background-color: #991B1B; 
            color: #FFFDF9; 
            padding: 8px 16px; 
            border-radius: 20px 4px 20px 4px; /* Formato de pétala */
            margin: 6px; 
            display: inline-block; 
            font-weight: bold;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 6px rgba(153, 27, 27, 0.15);
            border: 1px solid #7F1D1D;
        }
        
        /* Cartão com Pontuação do Termo */
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
            font-weight: 700;
            color: #F5D04C; /* Ouro Brilhante */
            line-height: 1;
            text-shadow: 0 0 10px rgba(245, 208, 76, 0.3);
        }
        
        .score-label {
            font-family: 'Cinzel', serif;
            letter-spacing: 1.5px;
            font-size: 0.85rem;
            color: #FAF5EC;
            margin-top: 10px;
            text-transform: uppercase;
        }

        /* Input / Selectbox Customizado */
        .stSelectbox div[data-baseweb="select"] {
            border-color: #D4AF37 !important;
            background-color: #FFFFFF !important;
        }
        
        /* Rodapé Real */
        .footer {
            font-family: 'Cinzel', serif;
            font-size: 0.8rem; 
            color: #6B5B52; 
            text-align: center;
            margin-top: 80px; 
            border-top: 1px dashed #D4AF37; 
            padding-top: 25px;
            letter-spacing: 1px;
        }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA API GEMINI ---
try:
    client = genai.Client()
except Exception as e:
    st.error("Erro ao inicializar a API do Gemini. Certifique-se de que a GEMINI_API_KEY está configurada.")
    client = None
    
# Mapeamento estrito das 7 plataformas oficiais
MAPA_PLATAFORMAS = {
    "Facebook": "Facebook.txt",
    "Instagram": "Instagram.txt",
    "Snapchat": "Snapchat.txt",
    "TikTok": "Tiktok.txt",
    "Twitter (X)": "Twitter.txt",
    "WhatsApp": "Whatsapp.txt",
    "YouTube": "Youtube.txt"
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

# --- DEFINIÇÃO DO FORMATO DE RESPOSTA ---
class AnalisePrivacidade(BaseModel):
    resumo_claro: str = Field(description="Um resumo em linguagem muito clara, simples e direta sobre o termo de privacidade.")
    red_flags: list[str] = Field(description="Lista de 5 a 8 palavras ou termos curtos de risco encontrados (ex: Rastreamento, Terceiros).")
    palavra_mais_critica: str = Field(description="A palavra ou conceito que representa o maior risco isolado ao usuário.")
    pontuacao_risco: int = Field(description="Uma nota inteira de 0 a 100 baseada na severidade das cláusulas de privacidade avaliadas.")
    dicas_protecao: list[str] = Field(description="Lista com exatamente 3 dicas ou ações práticas que o usuário pode tomar nas configurações da plataforma para se proteger.")

# Função para carregar o arquivo txt
def carregar_termo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.read()
    return None

# Função cacheada
@st.cache_data(show_spinner="Desvendando o mistério do pergaminho jurídico com o Gemini... Aguarde.")
def analisar_termo_com_gemini(texto_termo, nome_plataforma):
    if not client:
        return None
        
    prompt = f"""
    Você é um especialista em direito digital e privacidade de dados. 
    Analise o termo de privacidade completo da plataforma {nome_plataforma} fornecido abaixo.
    Extraia as informações necessárias respeitando estritamente o esquema JSON solicitado, adaptando-o para o português brasileiro.
    Gere sugestões de proteção realistas nas 'dicas_protecao' voltadas para o usuário final.
    
    Termo de Privacidade:
    {texto_termo}
    """
    
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
        st.error(f"Erro na chamada da API: {e}")
        return None

# --- MAPA FIXO DE COMPARAÇÃO DE RISCOS ---
dados_risco_global = {
    'Plataformas': ["Facebook", "Instagram", "Snapchat", "TikTok", "Twitter (X)", "WhatsApp", "YouTube"],
    'Nível de Risco (0-100)': [88, 85, 65, 90, 75, 55, 70]
}

# --- INTERFACE DO USUÁRIO ---

# Banner Principal Temático
st.markdown("""
    <div style="text-align: center; padding: 25px 0;">
        <span style="font-size: 3.5rem; line-height: 1;">🌹</span>
        <h1 style="margin-top: 15px; font-size: 2.8rem; font-weight: 700;">O Espelho da Verdade</h1>
        <p style="font-style: italic; color: #5C4B40; font-size: 1.2rem; max-width: 700px; margin: 10px auto 0 auto;">
            Desmistificando os contratos de privacidade com inteligência artificial para que seus dados não fiquem presos em um feitiço de termos complexos.
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# Centralização elegante da caixa de seleção
col_select_1, col_select_2, col_select_3 = st.columns([1, 2, 1])
with col_select_2:
    opcao_plataforma = st.selectbox(
        "Selecione o pergaminho de privacidade de uma rede social:", 
        ["Selecione..."] + list(MAPA_PLATAFORMAS.keys())
    )

texto_contrato = None
nome_analise = opcao_plataforma

if opcao_plataforma != "Selecione...":
    arquivo_alvo = MAPA_PLATAFORMAS[opcao_plataforma]
    texto_contrato = carregar_termo(arquivo_alvo)

# Se temos um texto pronto para analisar
if texto_contrato:
    analise = analisar_termo_com_gemini(texto_contrato, nome_analise)
    
    if analise:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- 1. RESUMO & PONTUAÇÃO DE RISCO ---
        col_res_1, col_res_2 = st.columns([2, 1])
        
        with col_res_1:
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
                        <img src="{MAPA_ICONES[nome_analise]}" style="width: 42px; height: 42px; object-fit: contain;" alt="{nome_analise} Icon" />
                    </div>
                    <h3 style="margin: 0 !important; font-size: 1.8rem; line-height: 1.2;">📋 Resumo sobre {nome_analise}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="parchment-card" style="min-height: 220px;">
                    <p style="font-size: 1.1rem; line-height: 1.6; margin: 0;">
                        {analise['resumo_claro']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_res_2:
            # Caixa com pontuação, barra de progresso do risco e visual de palácio real
            progresso_html = f"""
                <div style="background-color: rgba(255, 255, 255, 0.2); border-radius: 10px; height: 10px; width: 100%; overflow: hidden; margin-top: 15px;">
                    <div style="background: linear-gradient(90deg, #F5D04C 0%, #E53935 100%); width: {analise['pontuacao_risco']}%; height: 100%;"></div>
                </div>
            """
            st.markdown(f"""
                <div class="score-container" style="min-height: 220px; display: flex; flex-direction: column; justify-content: center;">
                    <div class="score-number">{analise['pontuacao_risco']}%</div>
                    <div class="score-label">Nível Geral de Risco</div>
                    {progresso_html}
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # --- 2. RED FLAGS & ESCUDO DE DEFESA ---
        col_flags_1, col_flags_2 = st.columns(2)
        
        with col_flags_1:
            st.markdown("### 🚩 Sinais de Alerta no Contrato")
            st.markdown("##### Palavras e Termos Críticos Identificados")
            st.markdown("<div style='padding: 10px 0;'>", unsafe_allow_html=True)
            tags_html = "".join([f"<span class='tag-risco'>{tag}</span>" for tag in analise['red_flags']])
            st.markdown(tags_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="red-flag-box">
                    <p class="atencao-texto">⚠️ ELEMENTO CRÍTICO:</p>
                    <p style="font-size: 1.05rem; line-height: 1.5; margin: 0;">
                        O conceito mais sensível ou de maior risco encontrado neste termo de privacidade é: 
                        <span style="color: #991B1B; font-weight: bold; font-family: 'Cinzel', serif; font-size: 1.15rem;">
                            {analise['palavra_mais_critica']}
                        </span>.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_flags_2:
            st.markdown("### 🛡️ Escudo de Defesa do Usuário")
            st.markdown("##### Dicas Práticas de Configuração e Proteção")
            
            dicas_lista = "".join([f"<li style='margin-bottom: 12px; font-size: 1.05rem; line-height: 1.5;'>{dica}</li>" for dica in analise['dicas_protecao']])
            st.markdown(f"""
                <div class="defense-box" style="min-height: 215px;">
                    <p class="defenda-se-texto">🛡️ COMO SE PROTEGER:</p>
                    <ul style="margin: 0; padding-left: 20px;">
                        {dicas_lista}
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            # --- EXPORTAR RELATÓRIO ---
            relatorio_txt = f"""==================================================
        O ESPELHO DA VERDADE - LAUDO DE PRIVACIDADE
==================================================
Plataforma Analisada: {nome_analise}
Nível Geral de Risco: {analise['pontuacao_risco']}%

RESUMO DO TERMO:
{analise['resumo_claro']}

TERMOS DE ALERTA IDENTIFICADOS:
{', '.join(analise['red_flags'])}

CONCEITO CRÍTICO DE MAIOR ATENÇÃO:
{analise['palavra_mais_critica']}

DICAS DE PROTEÇÃO RECOMENDADAS:
{chr(10).join([f"- {dica}" for dica in analise['dicas_protecao']])}

--------------------------------------------------
Relatório gerado via IA "O Espelho da Verdade"
=================================================="""

            st.download_button(
                label="📜 Baixar Pergaminho de Defesa (Relatório .txt)",
                data=relatorio_txt,
                file_name=f"Laudo_Privacidade_{nome_analise.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # --- 3. GRÁFICO COMPARATIVO ---
        st.markdown("### 📊 A Escala de Risco no Reino Digital")
        st.markdown("Veja como a plataforma se compara com as principais redes em termos de exposição de dados:")
        
        df_grafico = pd.DataFrame(dados_risco_global)
        st.bar_chart(data=df_grafico, x='Plataformas', y='Nível de Risco (0-100)', color='#D4AF37')
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # --- 4. NOTÍCIAS RELACIONADAS ---
        st.markdown(f"### 📰 O Que Estão Falando Sobre a Privacidade do {nome_analise}?")
        st.markdown("Fique por dentro das últimas manchetes e investigações de tratamento de dados:")
        
        termo_busca = f"{nome_analise} privacidade"
        termo_codificado = urllib.parse.quote(termo_busca)
        url_feed = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

        try:
            resposta = requests.get(url_feed, timeout=5)
            root = ET.fromstring(resposta.content)
            noticias = root.findall('.//item')[:2]
            
            if noticias:
                col_n1, col_n2 = st.columns(2)
                
                # Notícia 1
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
                
                # Notícia 2
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
                                <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe a segunda cobertura do cenário regulatório internacional desta plataforma.</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Não encontramos notícias recentes específicas para esta plataforma no momento.")
        
        except Exception as e:
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                st.markdown(f"""
                    <div class="parchment-card" style="min-height: 200px;">
                        <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://g1.globo.com/tecnologia/" target="_blank" style="text-decoration: none; color: #162E5C;">{nome_analise} e Investigações de Tratamento de Dados</a></h4>
                        <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: Portal G1 Tecnologia</p>
                        <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe as notícias sobre as auditorias mais recentes da ANPD envolvendo tratamento de informações sensíveis no Brasil.</p>
                    </div>
                """, unsafe_allow_html=True)
            with col_n2:
                st.markdown(f"""
                    <div class="parchment-card" style="min-height: 200px;">
                        <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://www.bbc.com/portuguese/topics/c40g969r280t" target="_blank" style="text-decoration: none; color: #162E5C;">Mudanças nas Políticas e Regulamentações da Controladora do {nome_analise}</a></h4>
                        <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: BBC Brasil</p>
                        <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Análise crítica sobre as novas regras globais de inteligência artificial e privacidade de dados de grandes corporações.</p>
                    </div>
                """, unsafe_allow_html=True)

# --- RODAPÉ REAL ---
st.markdown("""
    <div class="footer">
        Aluna FGV-ECMI: Keidy Alves Pizzetti Amaro | Orientador: Prof. Josir Gomes
    </div>
""", unsafe_allow_html=True)
