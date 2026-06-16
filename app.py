import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Analisador de Termos de Privacidade",
    page_icon="🌹",
    layout="wide"
)

# --- PALETA DE CORES (A Bela e a Fera) ---
st.markdown("""
    <style>
        .stApp { background-color: #ebf2f7; color: #221e23; }
        h1, h2, h3 { color: #104f7e !important; }
        .red-flag-box {
            background-color: #f0dbb6;
            border-left: 5px solid #c03131;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .atencao-texto { color: #c03131; font-weight: bold; font-size: 1.1rem; }
        .tag-risco {
            background-color: #c03131; color: white; padding: 6px 12px; 
            border-radius: 4px; margin: 3px; display: inline-block; font-weight: bold;
        }
        .footer {
            font-size: 0.75rem; color: #555555; text-align: center;
            margin-top: 50px; border-top: 1px solid #104f7e; padding-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA API GEMINI ---
# O Streamlit gerencia segredos de forma segura. No GitHub/Streamlit Cloud,
# você configurará a variável "GEMINI_API_KEY" nos Secrets do painel.
try:
    # A nova biblioteca lê automaticamente a variável de ambiente GEMINI_API_KEY
    client = genai.Client()
except Exception as e:
    st.error("Erro ao inicializar a API do Gemini. Certifique-se de que a GEMINI_API_KEY está configurada.")
    client = None
    
# Mapeamento das plataformas para os respectivos nomes de arquivos salvos na pasta do projeto
MAPA_PLATAFORMAS = {
    "Facebook": "Facebook.txt",
    "Instagram": "Instagram.txt",
    "Snapchat": "Snapchat.txt",
    "TikTok": "Tiktok.txt",
    "Twitter (X)": "Twitter.txt",
    "WhatsApp": "Whatsapp.txt",
    "YouTube": "Youtube.txt"
}

# --- DEFINIÇÃO DO FORMATO DE RESPOSTA (Pydantic) ---
# Força o Gemini a responder exatamente com os campos necessários para preencher o layout
class AnalisePrivacidade(BaseModel):
    resumo_claro: str = Field(description="Um resumo em linguagem muito clara, simples e direta sobre o termo de privacidade.")
    red_flags: list[str] = Field(description="Lista de 5 a 8 palavras ou termos curtos de risco encontrados (ex: Rastreamento, Terceiros).")
    palavra_mais_critica: str = Field(description="A palavra ou conceito que representa o maior risco isolado ao usuário.")
    pontuacao_risco: int = Field(description="Uma nota inteira de 0 a 100 baseada na severidade das cláusulas de privacidade avaliadas.")

# Função para carregar o arquivo txt localmente
def carregar_termo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.read()
    return None

# Função cacheada para economizar requisições à API e acelerar a navegação do usuário
@st.cache_data(show_spinner="Gemini analisando o termo juridico... Por favor, aguarde.")
def analisar_termo_com_gemini(texto_termo, nome_plataforma):
    if not client:
        return None
        
    prompt = f"""
    Você é um especialista em direito digital e privacidade de dados. 
    Analise o termo de privacidade completo da plataforma {nome_plataforma} fornecido abaixo.
    Extraia as informações necessárias respeitando estritamente o esquema JSON solicitado.
    
    Termo de Privacidade:
    {texto_termo}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Rápido, econômico e com contexto massivo
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalisePrivacidade,
                temperature=0.2
            ),
        )
        # O SDK retorna a string JSON validada no formato do Pydantic em .text
        import json
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Erro na chamada da API: {e}")
        return None

# --- MAPA FIXO DE COMPARAÇÃO DE RISCOS (Para a Seção 3) ---
# Como o gráfico precisa listar TODAS as plataformas simultaneamente, o ideal é ter uma base centralizada.
# Você pode preencher com valores pré-avaliados ou mockados enquanto consolida o app.
dados_risco_global = {
    'Plataformas': ["Facebook", "Instagram", "Snapchat", "TikTok", "Twitter (X)", "WhatsApp", "YouTube"],
    'Nível de Risco (0-100)': [88, 85, 65, 90, 75, 55, 70]
}

# --- INTERFACE DO USUÁRIO ---
st.title("🌹 Analisador de Termos de Privacidade das Plataformas Digitais")
st.markdown("Entenda de forma clara o que as grandes plataformas fazem com os seus dados usando Inteligência Artificial.")
st.divider()

# Menu de seleção
opcao_plataforma = st.selectbox("Escolha uma plataforma para análise detalhada:", ["Selecione..."] + list(MAPA_PLATAFORMAS.keys()))

if opcao_plataforma != "Selecione...":
    arquivo_alvo = MAPA_PLATAFORMAS[opcao_plataforma]
    texto_contrato = carregar_termo(arquivo_alvo)
    
    if texto_contrato:
        # Executa a análise inteligente
        analise = analisar_termo_com_gemini(texto_contrato, opcao_plataforma)
        
        if analise:
            # 1. RESUMO
            st.header("📋 Resumo do Termo de Privacidade")
            st.write(analise['resumo_claro'])
            st.divider()
            
            # 2. RED FLAGS
            st.header("🚩 Principais Pontos de Atenção - RED FLAGS")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Nuvem de Termos de Risco")
                tags_html = "".join([f"<span class='tag-risco'>{tag}</span>" for tag in analise['red_flags']])
                st.markdown(tags_html, unsafe_allow_html=True)
                
            with col2:
                st.subheader("Destaque Importante")
                st.markdown(f"""
                    <div class="red-flag-box">
                        <p class="atencao-texto">⚠️ ATENÇÃO:</p>
                        <p>A palavra que mais aparece (ou possui maior criticidade) nesse termo é: 
                        <span style="color: #c03131; font-weight: bold; font-size: 1.2rem;">{analise['palavra_mais_critica']}</span>.</p>
                    </div>
                """, unsafe_allow_html=True)
            st.divider()
            
            # 3. GRÁFICO COMPARATIVO
            st.header("📊 Classificação do Nível de Risco")
            st.markdown("Veja onde a plataforma selecionada se posiciona no comparativo geral de risco à segurança digital:")
            
            df_grafico = pd.DataFrame(dados_risco_global)
            st.bar_chart(data=df_grafico, x='Plataformas', y='Nível de Risco (0-100)', color='#104f7e')
            st.divider()
            
            # 4. NOTÍCIAS (Dinâmico/Links Estruturados)
            st.header("📰 Notícias Relacionadas")
            st.markdown(f"Pesquisas recentes e atualizações jornalísticas envolvendo a privacidade da **{opcao_plataforma}**:")
            
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                st.markdown(f"### [{opcao_plataforma} e investigações de tratamento de dados](https://g1.globo.com)")
                st.caption("Fonte: Portal G1 | Atualizado Recentemente")
                st.write("Acompanhe notícias sobre as últimas auditorias da ANPD (Autoridade Nacional de Proteção de Dados) e processos regulatórios aplicados a empresas de tecnologia.")
            with col_n2:
                st.markdown(f"### [Mudanças globais nas políticas da controladora do {opcao_plataforma}](https://www.bbc.com/portuguese)")
                st.caption("Fonte: BBC Brasil | Atualizado Recentemente")
                st.write("Análise internacional sobre como novas diretrizes de inteligência artificial aplicadas à plataforma impactam os direitos de privacidade no Brasil.")
                
    else:
        st.error(f"Arquivo '{arquivo_alvo}' não encontrado no repositório. Verifique o upload no GitHub.")
else:
    st.info("Por favor, selecione uma plataforma para iniciar a análise em tempo real.")

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        Aluna FGV-ECMI: Keidy Alves Pizzetti Amaro | Orientador: Prof. Josir Gomes
    </div>
""", unsafe_allow_html=True)
