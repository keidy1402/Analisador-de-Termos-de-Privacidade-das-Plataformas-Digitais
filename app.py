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
        
        /* Configurações Gerais */
        .stApp { background-color: #FAF5EC; color: #2C1E21; font-family: 'Lora', serif; }
        h1, h2, h3, h4 { font-family: 'Cinzel', serif !important; color: #162E5C !important; font-weight: 600; }
        
        .gold-divider { 
            height: 2px; 
            background: linear-gradient(90deg, transparent, #D4AF37, transparent); 
            margin: 30px 0; 
        }
        
        /* Cartão de Pergaminho (Resumo) */
        .parchment-card {
            background-color: #FFFFFF; 
            border: 1px solid #E6D9C5; 
            border-top: 4px solid #D4AF37;
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 6px 15px rgba(0,0,0,0.04);
            margin-bottom: 20px; 
            height: 260px; /* Altura fixa idêntica para alinhamento absoluto */
            display: flex; 
            flex-direction: column; 
            justify-content: center;
            overflow-y: auto;
        }

        /* Nova Nuvem de Palavras Estilo Medalhões de Época */
        .word-cloud-container { 
            padding: 25px; 
            text-align: center; 
            background: #FFFDF9; 
            border: 1px dashed #D4AF37; 
            border-radius: 12px;
            box-shadow: inset 0 0 10px rgba(212, 175, 55, 0.05);
        }

        .vintage-tag {
            font-family: 'Cinzel', serif;
            color: #991B1B;
            border: 1px solid #D4AF37;
            background-color: rgba(212, 175, 55, 0.06);
            padding: 6px 14px;
            border-radius: 20px;
            margin: 6px;
            display: inline-block;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            transition: all 0.3s ease;
        }
        
        .vintage-tag:hover {
            transform: scale(1.06) translateY(-2px);
            background-color: rgba(153, 27, 27, 0.08);
            border-color: #991B1B;
            box-shadow: 0 4px 8px rgba(153, 27, 27, 0.12);
        }

        /* Quadro de Atenção Vermelho Carmesim */
        .attention-box {
            background-color: #FFF5F5; 
            border: 2px solid #991B1B; 
            padding: 25px; 
            border-radius: 8px;
            text-align: center; 
            margin-top: 20px; 
            position: relative;
            box-shadow: 0 4px 12px rgba(153, 27, 27, 0.05);
        }
        .attention-label {
            position: absolute; 
            top: -12px; 
            left: 50%; 
            transform: translateX(-50%);
            background: #991B1B; 
            color: white; 
            padding: 2px 18px; 
            font-family: 'Cinzel', serif; 
            font-size: 0.85rem; 
            border-radius: 4px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        /* Container de Risco Geral Detectado */
        .score-container {
            text-align: center; 
            background: linear-gradient(135deg, #162E5C 0%, #0B1D3A 100%);
            color: #FAF5EC; 
            padding: 30px; 
            border-radius: 12px; 
            border: 2px solid #D4AF37;
            box-shadow: 0 8px 25px rgba(22, 46, 92, 0.2); 
            height: 260px; /* Altura fixa idêntica para alinhamento absoluto */
            display: flex; 
            flex-direction: column; 
            justify-content: center;
        }
        .score-number { font-family: 'Cinzel', serif; font-size: 4.8rem; color: #F5D04C; line-height: 1; font-weight: 700; }

        /* Rodapé de Época */
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

# --- BANCO DE CONTINGÊNCIA (FALLBACK SEGURO) ---
ACERVO_CONTINGENCIA = {
    "Facebook": {
        "resumo_claro": "O Facebook monitora intensamente sua atividade fora do aplicativo, coletando dados de navegação, histórico de compras e interesses para traçar perfis psicológicos profundos voltados a anúncios direcionados.",
        "red_flags": ["Rastreamento", "Cookies", "Perfilamento", "Algoritmos", "Big Data", "Compartilhamento"],
        "palavra_mais_critica": "Venda de Metadados",
        "pontuacao_risco": 88,
        "dicas_protecao": [
            {"titulo": "Desativar Rastreamento Fora do Facebook", "passos": ["Abra o aplicativo e vá em Configurações.", "Desça até 'Suas informações do Facebook' e toque em 'Atividade fora do Facebook'.", "Selecione 'Desativar atividade futura' para impedir o rastreamento em outros sites."]},
            {"titulo": "Limitar Preferências de Anúncios", "passos": ["Vá em Configurações > Preferências de Anúncios.", "Toque em 'Configurações de anúncios'.", "Desative o uso de dados de parceiros para exibição de anúncios."]},
            {"titulo": "Revisar Permissões de Aplicativos", "passos": ["Acesse Configurações > Aplicativos e Sites.", "Remova jogos ou testes antigos que ainda têm acesso à sua conta."]}
        ]
    },
    "Instagram": {
        "resumo_claro": "O Instagram coleta dados geográficos em tempo real e analisa detalhadamente o tempo de visualização e interações com fotos e vídeos para calibrar algoritmos de engajamento viciantes.",
        "red_flags": ["Inteligência Artificial", "Metadados de Fotos", "Localização Exata", "Reconhecimento Facial", "Anúncios Comportamentais"],
        "palavra_mais_critica": "Treinamento de IA",
        "pontuacao_risco": 85,
        "dicas_protecao": [
            {"titulo": "Tornar a Conta Privada", "passos": ["Vá ao seu Perfil e toque nas três linhas no canto superior.", "Acesse Configurações > Privacidade da Conta.", "Ative a chave 'Conta Privada'."]},
            {"titulo": "Desativar Localização Precisa", "passos": ["Abra as configurações do seu celular.", "Vá em Aplicativos > Instagram > Permissões.", "Selecione 'Localização' e desative a opção 'Usar localização precisa'."]},
            {"titulo": "Pausar Sugestões de Conteúdo", "passos": ["Vá ao seu feed inicial.", "Toque no 'X' em uma publicação sugerida e selecione 'Soneca de postagens sugeridas por 30 dias'."]}
        ]
    },
    "Snapchat": {
        "resumo_claro": "O Snapchat rastreia de forma ativa a geolocalização do usuário mesmo em segundo plano para o recurso 'Snap Map', além de catalogar dados de filtros faciais interativos.",
        "red_flags": ["Mapa de Amigos", "Filtros 3D", "Localização Contínua", "Memórias em Nuvem", "Reconhecimento de Voz"],
        "palavra_mais_critica": "Snap Map (Rastreamento Físico)",
        "pontuacao_risco": 65,
        "dicas_protecao": [
            {"titulo": "Ativar o Modo Fantasma", "passos": ["Abra a tela do Mapa no Snapchat.", "Toque na engrenagem no canto superior.", "Marque a caixa 'Modo Fantasma' para esconder sua posição de todos."]},
            {"titulo": "Limpar Dados de Lentes", "passos": ["Vá em Configurações > Ações de Conta.", "Toque em 'Limpar Dados de Lente' para apagar mapeamentos faciais temporários."]},
            {"titulo": "Desativar Contribuição ao Holofote", "passos": ["Evite enviar Snaps com localização para o 'Holofote público' se quiser manter privacidade total."]}
        ]
    },
    "TikTok": {
        "resumo_claro": "O TikTok possui políticas extremamente invasivas, incluindo a capacidade de capturar o ritmo de digitação, biometria facial e comportamentos de navegação através de seu navegador embutido.",
        "red_flags": ["Biometria", "Ritmo de Digitação", "Navegador Embutido", "Padrão de Teclado", "Compartilhamento na China"],
        "palavra_mais_critica": "Coleta Biométrica Invasiva",
        "pontuacao_risco": 90,
        "dicas_protecao": [
            {"titulo": "Evitar o Navegador Interno", "passos": ["Nunca faça login ou insira senhas em links abertos dentro do TikTok.", "Sempre toque nos três pontos no topo da página aberta e escolha 'Abrir no navegador externo' (Safari ou Chrome)."]},
            {"titulo": "Desativar Compartilhamento de Contatos", "passos": ["Acesse Perfil > Configurações > Privacidade.", "Toque em 'Sincronizar contatos e amigos do Facebook' e desative ambas as chaves."]},
            {"titulo": "Limitar Anúncios Personalizados", "passos": ["Vá em Configurações > Anúncios.", "Desative a opção 'Anúncios personalizados' para parar de ser rastreado para fins comerciais."]}
        ]
    },
    "Twitter (X)": {
        "resumo_claro": "O X utiliza por padrão todas as suas postagens públicas, interações e curtidas para treinar sua inteligência artificial proprietária (Grok), sem consentimento explícito prévio.",
        "red_flags": ["Treinamento Grok", "Inteligência Artificial", "Extração de Dados", "Perfil Político", "Dados Biométricos"],
        "palavra_mais_critica": "Treinamento de IA Grok",
        "pontuacao_risco": 75,
        "dicas_protecao": [
            {"titulo": "Desativar Treinamento do Grok", "passos": ["Acesse Configurações e Privacidade no menu lateral.", "Vá em 'Privacidade e segurança' > 'Grok'.", "Desmarque a caixa que permite que o X use seus posts para treinamento da IA."]},
            {"titulo": "Proteger Seus Posts", "passos": ["Vá em Configurações > Privacidade e segurança > Audiência e marcação.", "Ative a opção 'Proteger seus posts' para torná-los visíveis apenas a seguidores aprovados."]},
            {"titulo": "Limitar Compartilhamento com Parceiros", "passos": ["Vá em Configurações > Privacidade > Compartilhamento de dados com parceiros.", "Desative todas as permissões."]}
        ]
    },
    "WhatsApp": {
        "resumo_claro": "Embora o WhatsApp proteja o conteúdo das mensagens com criptografia de ponta a ponta, ele coleta e compartilha uma grande quantidade de metadados com as demais empresas da Meta, como contatos, IPs e horários de conexão.",
        "red_flags": ["Metadados", "Lista de Contatos", "Endereço IP", "Registro de Chamadas", "Sincronização Meta"],
        "palavra_mais_critica": "Vazamento de Metadados",
        "pontuacao_risco": 55,
        "dicas_protecao": [
            {"titulo": "Ocultar Endereço IP nas Chamadas", "passos": ["Vá em Configurações > Privacidade.", "Toque em 'Configurações Avançadas'.", "Ative a opção 'Proteger endereço IP nas chamadas'."]},
            {"titulo": "Desativar Confirmações de Leitura", "passos": ["Acesse Configurações > Privacidade.", "Desative a chave 'Confirmações de leitura' para evitar monitoramento de resposta."]},
            {"titulo": "Bloquear Backup em Nuvem sem Senha", "passos": ["Vá em Configurações > Conversas > Backup de conversas.", "Ative o 'Backup criptografado de ponta a ponta' para que o Google/Apple não leiam suas conversas na nuvem."]}
        ]
    },
    "YouTube": {
        "resumo_claro": "O YouTube rastreia meticulosamente cada segundo de vídeo assistido, pesquisas realizadas e termos clicados, unificando essas informações ao seu perfil central do Google para publicidade direcionada.",
        "red_flags": ["Histórico de Vídeos", "Perfil Unificado Google", "Segmentação por Idade", "Padrões de Sono", "Rastreamento Infantil"],
        "palavra_mais_critica": "Rastreamento Unificado Google",
        "pontuacao_risco": 70,
        "dicas_protecao": [
            {"titulo": "Pausar Histórico de Exibição", "passos": ["Abra o YouTube e toque no seu Perfil.", "Vá em Histórico e toque nos três pontos no canto superior.", "Selecione 'Pausar histórico de exibição' para evitar perfilamento comportamental."]},
            {"titulo": "Configurar Exclusão Automática", "passos": ["Acesse sua 'Conta do Google' > Dados e Privacidade.", "Vá em 'Atividade na Web e de Apps' e defina a exclusão automática para 3 meses."]},
            {"titulo": "Desativar Anúncios Personalizados", "passos": ["Acesse as configurações do seu perfil do Google (My Ad Center) e desligue totalmente a personalização de anúncios."]}
        ]
    }
}

# --- FUNÇÕES DE LÓGICA ---
@st.cache_data
def analisar_ia_com_contingencia(texto, plataforma):
    try:
        client = genai.Client()
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Analise o termo de privacidade de {plataforma}: {texto}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AnalisePrivacidade,
                temperature=0.2
            )
        )
        return json.loads(resp.text), False
    except Exception:
        return ACERVO_CONTINGENCIA.get(plataforma), True

def limpar_texto_pdf(texto):
    if not PDF_DISPONIVEL or not texto:
        return ""
    texto_escapado = html.escape(str(texto))
    texto_escapado = texto_escapado.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    texto_escapado = texto_escapado.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    return texto_escapado

def gerar_pdf_corrigido(plataforma, analise):
    if not PDF_DISPONIVEL:
        return None
        
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#162E5C'), alignment=1)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#162E5C'), spaceBefore=15, spaceAfter=8)
    body_style = ParagraphStyle('B', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#2C1E21'), leading=14, spaceAfter=10)
    step_style = ParagraphStyle('S', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, textColor=colors.HexColor('#2E7D32'), leading=13, leftIndent=15, spaceAfter=5)
    
    story = [
        Paragraph(f"<b>ESCUDO DE DEFESA: {limpar_texto_pdf(plataforma)}</b>", title_style),
        Spacer(1, 15),
        Paragraph(f"<b>Grau Geral de Risco Detectado: {analise['pontuacao_risco']}%</b>", h2_style),
        Paragraph(limpar_texto_pdf(analise['resumo_claro']), body_style),
        Spacer(1, 5),
        Paragraph("<b>PASSO A PASSO DE PROTEÇÃO (DIDÁTICO):</b>", h2_style)
    ]
    
    for i, dica in enumerate(analise['dicas_protecao'], 1):
        story.append(Paragraph(f"<b>{i}. {limpar_texto_pdf(dica['titulo'])}</b>", body_style))
        for j, p in enumerate(dica['passos'], 1):
            story.append(Paragraph(f"<b>Passo {j}:</b> {limpar_texto_pdf(p)}", step_style))
        story.append(Spacer(1, 5))
        
    story.append(Spacer(1, 20))
    story.append(Paragraph("<font color='#6B5B52'>FGV-ECMI | Aluna: Keidy Alves Pizzetti Amaro | Prof. Josir Gomes</font>", ParagraphStyle('F', parent=styles['Normal'], alignment=1, fontSize=8)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO (A BELA E A FERA) ---
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

# Centralização da Caixa de Seleção
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    opcao = st.selectbox("Selecione a plataforma para abrir o Relatório:", ["Selecione..."] + list(ACERVO_CONTINGENCIA.keys()))

if opcao != "Selecione...":
    analise, fallback = analisar_ia_com_contingencia("Contrato fictício ou real para análise...", opcao)
    
    if fallback:
        st.info("🔮 *O Espelho da Verdade está sob uma névoa de alta demanda neste momento. Para sua segurança imediata, revelamos o Laudo Sagrado de nossa biblioteca interna de contingência.*")

    if analise:
        # ALINHAMENTO SUPERIOR SIMÉTRICO: Relatório Geral e Risco Detectado com Altura Coesa
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                    <img src="{MAPA_ICONES[opcao]}" width="55" alt="{opcao}">
                    <h3 style="margin: 0 !important;">Relatório Real de {opcao}</h3>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f'<div class="parchment-card"><p style="font-size:1.05rem; line-height:1.6; margin:0;">{analise["resumo_claro"]}</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div style="margin-bottom: 10px; height: 35px;"></div>
                <div class="score-container">
                    <div style="font-family: 'Cinzel', serif; font-size: 1rem; margin-bottom: 5px;">Risco Geral Detectado</div>
                    <div class="score-number">{analise["pontuacao_risco"]}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # --- SINAIS DE ALERTA & ESCUDO DE DEFESA ---
        f1, f2 = st.columns(2)
        with f1:
            st.subheader("🚩 Sinais de alerta - RED FLAGS:")
            
            # Nuvem de Palavras Premium: Medalhões individuais com sutil variação de tamanho e opacidade
            tags_html = ""
            for tag in analise['red_flags']:
                size_pct = random.randint(90, 115)  # Pequena variação tipográfica harmônica
                tags_html += f'<span class="vintage-tag" style="font-size: {size_pct}%;">{tag}</span>'
            
            st.markdown(f'<div class="word-cloud-container">{tags_html}</div>', unsafe_allow_html=True)
            
            # Quadro de ATENÇÃO Solicitado
            st.markdown(f"""
                <div class="attention-box">
                    <div class="attention-label">ATENÇÃO</div>
                    <span style="font-size: 1.6rem; font-weight: bold; color: #991B1B; font-family: 'Cinzel', serif;">
                        {analise['palavra_mais_critica']}
                    </span>
                </div>
            """, unsafe_allow_html=True)

        with f2:
            st.subheader("🛡️ Como garantir pelo menos um pouco de segurança?")
            st.markdown("Siga as orientações práticas para se proteger dentro do aplicativo:")
            
            for d in analise['dicas_protecao']:
                with st.expander(f"⚙️ {d['titulo']}"):
                    for i, p in enumerate(d['passos'], 1): 
                        st.write(f"**{i}º Passo:** {p}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Botão de download do PDF robusto
            if PDF_DISPONIVEL:
                pdf_output = gerar_pdf_corrigido(opcao, analise)
                if pdf_output:
                    st.download_button(
                        label="📜 Baixar esse Guia Prático em PDF", 
                        data=pdf_output, 
                        file_name=f"Escudo_Defesa_{opcao}.pdf", 
                        mime="application/pdf", 
                        use_container_width=True
                    )
            else:
                st.warning("O motor de PDFs está offline no momento. Utilize o guia na tela.")
        
        # LINHA DIVISÓRIA SOLICITADA entre o quadro de destaque e o gráfico comparativo
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

        # --- GRÁFICO E INTERPRETAÇÃO PERSONALIZADA ---
        st.subheader("📊 Comparativo de Periculosidade")
        df_p = pd.DataFrame({'Plataforma': list(ACERVO_CONTINGENCIA.keys()), 'Risco': [v['pontuacao_risco'] for v in ACERVO_CONTINGENCIA.values()]}).sort_values('Risco', ascending=True)
        
        if PLOTLY_DISPONIVEL:
            fig = px.bar(df_p, x='Risco', y='Plataforma', orientation='h', color='Risco', color_continuous_scale=['#F5D04C', '#D4AF37', '#991B1B'])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_family="Cinzel", 
                font_color="#162E5C", 
                margin=dict(l=20, r=20, t=10, b=10),
                xaxis=dict(showgrid=False, range=[0, 100], title="Nível de Risco (%)"),
                yaxis=dict(showgrid=False, title="")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(data=df_p, x='Plataforma', y='Risco', color='#D4AF37')

        # RELATÓRIO DINÂMICO PERSONALIZADO
        outros_riscos = [v['pontuacao_risco'] for k, v in ACERVO_CONTINGENCIA.items() if k != opcao]
        avg_risco = sum(outros_riscos) / len(outros_riscos)
        status = "acima" if analise['pontuacao_risco'] > avg_risco else "abaixo"
        
        st.markdown(f"""
            <div class="parchment-card" style="border-top: 4px solid #162E5C; height: auto; min-height: auto; margin-top: 20px;">
                <h4 style="margin-top:0">📜 Interpretação do Espelho: {opcao}</h4>
                <p>Ao observarmos o reino digital, o <b>{opcao}</b> se destaca com um nível de risco de <b>{analise['pontuacao_risco']}%</b>, 
                o que o coloca <b>{status}</b> da média de periculosidade das outras plataformas avaliadas ({avg_risco:.1f}%).</p>
                <p>Enquanto o <b>TikTok</b> e o <b>Facebook</b> permanecem como as feras mais vorazes na coleta de dados biometrizados e comportamentais, 
                o <b>{opcao}</b> apresenta uma sombra particular focada em <i>{analise['palavra_mais_critica']}</i>. 
                Em comparação aos outros convidados deste baile, sua postura exige vigilância { "redobrada" if status == "acima" else "moderada" }.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

        # --- 4. NOTÍCIAS RELACIONADAS ---
        st.markdown(f"### 📰 O Que Estão Falando Sobre a Privacidade do {opcao}?")
        st.markdown("Fique por dentro das últimas manchetes e investigações de tratamento de dados:")
        
        termo_busca = f"{opcao} privacidade"
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
                        <div class="parchment-card" style="height: auto; min-height: 200px;">
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
                            <div class="parchment-card" style="height: auto; min-height: 200px;">
                                <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="{link2}" target="_blank" style="text-decoration: none; color: #162E5C;">{titulo2}</a></h4>
                                <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: {fonte2} | Publicado em: {data2}</p>
                                <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe a segunda cobertura do cenário regulatório internacional desta plataforma.</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Não encontramos notícias recentes específicas para esta plataforma no momento.")
        
        except Exception as e:
            # Fallback visual seguro caso ocorra erro de conexão/RSS
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                st.markdown(f"""
                    <div class="parchment-card" style="height: auto; min-height: 200px;">
                        <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://g1.globo.com/tecnologia/" target="_blank" style="text-decoration: none; color: #162E5C;">{opcao} e Investigações de Tratamento de Dados</a></h4>
                        <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: Portal G1 Tecnologia</p>
                        <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Acompanhe as notícias sobre as auditorias mais recentes da ANPD envolvendo tratamento de informações sensíveis no Brasil.</p>
                    </div>
                """, unsafe_allow_html=True)
            with col_n2:
                st.markdown(f"""
                    <div class="parchment-card" style="height: auto; min-height: 200px;">
                        <h4 style="font-size: 1.15rem; margin-bottom: 8px;"><a href="https://www.bbc.com/portuguese/topics/c40g969r280t" target="_blank" style="text-decoration: none; color: #162E5C;">Mudanças nas Políticas e Regulamentações da Controladora do {opcao}</a></h4>
                        <p style="color: #8C7A6B; font-size: 0.8rem; margin-bottom: 12px; font-style: italic;">Fonte: BBC Brasil</p>
                        <p style="font-size: 0.95rem; margin: 0; line-height: 1.5;">Análise crítica sobre as novas regras globais de inteligência artificial e privacidade de dados de grandes corporações.</p>
                    </div>
                """, unsafe_allow_html=True)

st.markdown('<div class="footer">FGV-ECMI | Aluna: Keidy Alves Pizzetti Amaro | Prof. Josir Gomes</div>', unsafe_allow_html=True)
