import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Analisador de Termos de Privacidade",
    page_icon="🌹",
    layout="wide"
)

# --- PALETA DE CORES (A Bela e a Fera) ---
# #f0dbb6 (Creme/Fundo secundário)
# #221e23 (Escuro/Texto)
# #f2c557 (Dourado/Destaques)
# #104f7e (Azul Fera/Botões e Títulos)
# #ebf2f7 (Azul Claro/Fundo Geral)
# #c03131 (Vermelho Rosa/Alertas e Red Flags)

# Aplicando estilização customizada via CSS para respeitar a paleta
st.markdown(f"""
    <style>
        /* Fundo geral do app */
        .stApp {{
            background-color: #ebf2f7;
            color: #221e23;
        }}
        /* Estilização de títulos */
        h1, h2, h3 {{
            color: #104f7e !important;
        }}
        /* Caixas de destaque (Red Flags) */
        .red-flag-box {{
            background-color: #f0dbb6;
            border-left: 5px solid #c03131;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .atencao-texto {{
            color: #c03131;
            font-weight: bold;
            font-size: 1.1rem;
        }}
        /* Rodapé bem pequeno */
        .footer {{
            font-size: 0.75rem;
            color: #555555;
            text-align: center;
            margin-top: 50px;
            border-top: 1px solid #104f7e;
            padding-top: 10px;
        }}
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
# Nota: Como não tenho o arquivo da logo, deixei o espaço para você carregar ou manter o título.
# Se tiver a logo no GitHub, use: st.image("logo.png", width=100)
st.title("🌹 Analisador de Termos de Privacidade das Plataformas Digitais")
st.markdown("Entenda de forma clara e rápida o que as grandes plataformas fazem com os seus dados.")

st.divider()

# --- SELEÇÃO DE PLATAFORMA ---
# Simulando uma base de dados para o exemplo rodar perfeitamente
plataformas = ["Selecione uma plataforma...", "Rede Social X", "Plataforma de Vídeo Y", "Aplicativo de Mensagem Z"]
plataforma_selecionada = st.selectbox("Escolha uma plataforma para analisar:", plataformas)

if plataforma_selecionada != "Selecione uma plataforma...":
    
    # --- 1. RESUMO DO TERMO ---
    st.header("📋 Resumo do Termo de Privacidade")
    # Aqui você trocará pelos resumos reais de cada plataforma
    st.write(f"Este é um resumo simplificado do termo de privacidade da **{plataforma_selecionada}**. "
             f"A plataforma coleta dados de navegação, localização em tempo real e compartilha informações "
             f"com parceiros de publicidade direcionada. O usuário tem direito de solicitar a exclusão, "
             f"mas o histórico de interações permanece guardado para melhoria dos algoritmos.")

    st.divider()

    # --- 2. PRINCIPAIS PONTOS DE ATENÇÃO (RED FLAGS) ---
    st.header("🚩 Principais Pontos de Atenção - RED FLAGS")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Nuvem de Palavras de Risco")
        # Como o Streamlit puro não faz nuvem de tags visual sem bibliotecas pesadas, 
        # uma alternativa nativa elegante e leve é usar áreas de tags coloridas ou uma imagem gerada.
        # Exemplo simulando os termos de risco:
        st.markdown("""
        <span style='background-color: #c03131; color: white; padding: 5px 10px; border-radius: 3px; margin: 2px; display: inline-block;'>Rastreamento</span>
        <span style='background-color: #c03131; color: white; padding: 8px 15px; border-radius: 3px; margin: 2px; display: inline-block; font-size: 1.2rem;'>Compartilhamento</span>
        <span style='background-color: #f2c557; color: #221e23; padding: 4px 8px; border-radius: 3px; margin: 2px; display: inline-block;'>Cookies</span>
        <span style='background-color: #c03131; color: white; padding: 10px 20px; border-radius: 3px; margin: 2px; display: inline-block; font-size: 1.4rem;'>Dados Biométricos</span>
        <span style='background-color: #f2c557; color: #221e23; padding: 6px 12px; border-radius: 3px; margin: 2px; display: inline-block;'>Localização</span>
        <span style='background-color: #c03131; color: white; padding: 5px 10px; border-radius: 3px; margin: 2px; display: inline-block;'>Terceiros</span>
        """, unsafe_allow_html=True)

    with col2:
        st.subheader("Destaque Importante")
        palavra_mais_comum = "Compartilhamento com Terceiros" # Exemplo dinâmico
        st.markdown(f"""
            <div class="red-flag-box">
                <p class="atencao-texto">⚠️ ATENÇÃO:</p>
                <p>A palavra ou conceito que mais aparece de forma crítica nesse termo é: 
                <span style="color: #c03131; font-weight: bold; font-size: 1.2rem;">{palavra_mais_comum}</span>.</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- 3. CLASSIFICAÇÃO DO NÍVEL DE RISCO ---
    st.header("📊 Classificação do Nível de Risco")
    st.markdown("Compare o nível de risco de segurança digital entre diferentes plataformas (Quanto maior a barra, maior o risco).")
    
    # Dados fictícios para o gráfico comparativo
    dados_grafico = pd.DataFrame({
        'Plataformas': ["Rede Social X", "Plataforma de Vídeo Y", "Aplicativo de Mensagem Z", "Média Geral"],
        'Nível de Risco (0-100)': [85, 60, 40, 61]
    })
    
    # Gráfico de barras nativo do Streamlit utilizando a cor Azul da sua paleta
    st.bar_chart(data=dados_grafico, x='Plataformas', y='Nível de Risco (0-100)', color='#104f7e')

    st.divider()

    # --- 4. NOTÍCIAS RELACIONADAS ---
    st.header("📰 Notícias Relacionadas")
    st.markdown(f"Fique por dentro das últimas atualizações jornalísticas sobre a **{plataforma_selecionada}**:")
    
    # Dica: Para deixar dinâmico no futuro você pode usar a biblioteca 'feedparser' para ler RSS de portais como G1, Nexo, etc.
    # Aqui estruturamos o layout de exibição das notícias:
    col_noticia1, col_noticia2 = st.columns(2)
    
    with col_noticia1:
        st.markdown(f"### [Título da Notícia Real sobre {plataforma_selecionada}](https://g1.globo.com)")
        st.caption("Fonte: Portal de Notícias | Atualizado recentemente")
        st.write("Breve linha fina ou resumo da notícia explicando a investigação ou nova política que a plataforma adotou recentemente.")
        
    with col_noticia2:
        st.markdown(f"### [Vazamento de dados ou nova regulamentação da {plataforma_selecionada}](https://www.bbc.com/portuguese)")
        st.caption("Fonte: Canal de Jornalismo | Atualizado recentemente")
        st.write("Explicação rápida sobre como essa notícia impacta os usuários e a privacidade dos dados coletados na plataforma.")

else:
    st.info("Por favor, selecione uma plataforma no menu acima para visualizar a análise completa.")

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        Aluna FGV-ECMI: Keidy Alves Pizzetti Amaro | Orientador: Prof. Josir Gomes
    </div>
""", unsafe_allow_html=True)
