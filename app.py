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

# Tenta importar as ferramentas de PDF de forma segura
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from io import BytesIO
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Espelho da Verdade - Termos de Privacidade",
    page_icon="🌹",
    layout="wide"
)

# --- PALETA DE CORES & ESTILO "A BELA E A FERA" ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght=400;600;700&family=Lora:ital,wght=0,400;0,500;1,400&display=swap');
        
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
class DicaSeguranca(BaseModel):
    titulo: str = Field(description="Título curto, direto e claro sobre a ação (ex: 'Limitar Anúncios Personalizados').")
    passos: list[str] = Field(description="Lista com passos sequenciais extremamente simples de executar nas configurações para leigos.")

class AnalisePrivacidade(BaseModel):
    resumo_claro: str = Field(description="Um resumo em linguagem muito clara, simples e direta sobre o termo de privacidade.")
    red_flags: list[str] = Field(description="Lista de palavras ou termos curtos de risco encontrados.")
    palavra_mais_critica: str = Field(description="A palavra ou conceito que representa o maior risco isolado ao usuário.")
    pontuacao_risco: int = Field(description="Uma nota inteira de 0 a 100 baseada na severidade do termo.")
    dicas_protecao: list[DicaSeguranca] = Field(description="Lista com dicas detalhadas, escritas de forma didática e guiada para leigos.")

# --- BANCO DE DADOS DE CONTINGÊNCIA (MOCK/OFFLINE COPIES) ---
# Caso a API esteja indisponível (Erro 503) ou sem chave configurada, o app continua perfeito e funcional.
ACERVO_CONTINGENCIA = {
    "Facebook": {
        "resumo_claro": "O Facebook monitora e coleta praticamente toda a sua atividade, incluindo as páginas que você curte, as fotos que publica e até o que você faz em outros sites e aplicativos fora da rede social. Essas informações são usadas para traçar um perfil altamente detalhado sobre seus interesses, permitindo que empresas enviem anúncios personalizados de forma agressiva.",
        "red_flags": ["Rastreamento Fora da Rede", "Compartilhamento com Terceiros", "Perfilamento para Anúncios", "Coleta de Metadados", "Reconhecimento de Imagem"],
        "palavra_mais_critica": "Rastreamento Cruzado (Cross-App Tracking)",
        "pontuacao_risco": 88,
        "dicas_protecao": [
            {
                "titulo": "Desativar Rastreamento de Outros Sites (Atividade Fora do Facebook)",
                "passos": [
                    "Abra o aplicativo do Facebook no celular e toque no menu (sua foto de perfil no canto direito).",
                    "Toque no ícone de engrenagem (Configurações e Privacidade) e depois em 'Configurações'.",
                    "Role a página até encontrar a seção 'Sua Atividade' e toque em 'Atividade fora do Facebook'.",
                    "Toque em 'Desconectar atividade recente' e depois selecione 'Gerenciar atividade futura' para marcar como desativado."
                ]
            },
            {
                "titulo": "Limitar Anúncios com Seus Dados Pessoais",
                "passos": [
                    "Acesse o menu de 'Configurações' do Facebook (como feito no Passo 1).",
                    "Acesse a 'Central de Contas' (geralmente o primeiro bloco no topo da tela).",
                    "Toque em 'Preferências de anúncios' e selecione 'Configurações de anúncios'.",
                    "Procure pela opção 'Dados de parceiros sobre sua atividade' e marque-a como 'Não permitido'."
                ]
            },
            {
                "titulo": "Restringir o Compartilhamento de Localização Permanente",
                "passos": [
                    "Vá nas configurações gerais do seu próprio celular (fora do app do Facebook).",
                    "Procure por 'Aplicativos' ou 'Privacidade' e selecione o 'Facebook'.",
                    "Toque em 'Permissões' e selecione 'Localização'.",
                    "Mude a permissão de 'Sempre permitir' para 'Permitir apenas durante o uso do app' ou 'Não permitir'."
                ]
            }
        ]
    },
    "Instagram": {
        "resumo_claro": "O Instagram coleta dados sobre cada foto que você visualiza, quanto tempo passa olhando uma publicação, suas mensagens diretas (DMs) e sua localização exata. Além disso, as diretrizes recentes da Meta permitem a utilização de fotos públicas, legendas e interações para alimentar e treinar os modelos de inteligência artificial da empresa.",
        "red_flags": ["Uso para Treinamento de IA", "Localização Precisa", "Rastreamento de Cliques", "Perfil de Interesses", "Compartilhamento de Metadados"],
        "palavra_mais_critica": "Uso de Conteúdo Pessoal para Treinamento de IA",
        "pontuacao_risco": 85,
        "dicas_protecao": [
            {
                "titulo": "Tornar sua Conta Privada para Proteger seu Conteúdo de Coletores de IA",
                "passos": [
                    "Abra o Instagram, vá para o seu perfil e toque nos três traços no canto superior direito.",
                    "Role até a seção 'Quem pode ver seu conteúdo' e toque em 'Privacidade da conta'.",
                    "Ative a chave para mudar sua conta de pública para 'Conta privada'."
                ]
            },
            {
                "titulo": "Desativar Localização Precisa nas Configurações do Celular",
                "passos": [
                    "Abra as configurações principais do seu smartphone.",
                    "Vá em 'Privacidade e Segurança' ou 'Aplicativos' e escolha 'Instagram'.",
                    "Selecione 'Localização' e desative a chave 'Localização Precisa' (assim o app só saberá sua cidade aproximada, e não sua rua)."
                ]
            },
            {
                "titulo": "Bloquear Anúncios Baseados em Tópicos Sensíveis",
                "passos": [
                    "Acesse seu perfil do Instagram e toque nas três linhas do menu superior.",
                    "Selecione 'Configurações e Privacidade' e vá em 'Preferências de anúncios'.",
                    "Toque em 'Tópicos de anúncios' e selecione aqueles que você deseja visualizar menos (como política, finanças ou beleza)."
                ]
            }
        ]
    },
    "TikTok": {
        "resumo_claro": "O TikTok possui regras extremamente invasivas. Ele monitora a digitação na tela através de seu navegador interno, rastreia as redes Wi-Fi às quais você se conecta e coleta informações biométricas (como características do rosto e de voz). Seus dados de consumo são amplamente repassados para a empresa controladora com sede na China.",
        "red_flags": ["Biometria Facial/Voz", "Leitura de Digitação", "Acesso à Rede Local", "Envio para Controladora Externa", "Padrões de Rolagem"],
        "palavra_mais_critica": "Monitoramento de Teclado no Navegador Interno",
        "pontuacao_risco": 90,
        "dicas_protecao": [
            {
                "titulo": "Evitar o Uso de Links dentro do Navegador do TikTok",
                "passos": [
                    "Ao clicar em um link no TikTok, o app abre a página dentro dele mesmo (navegador interno) onde ele consegue ler tudo o que você digita.",
                    "Sempre que abrir um link, procure no canto superior ou inferior da tela o ícone de três pontos.",
                    "Selecione a opção 'Abrir no navegador externo' (como Chrome ou Safari) para sair do ambiente de monitoramento do TikTok."
                ]
            },
            {
                "titulo": "Desativar Anúncios Personalizados de Terceiros",
                "passos": [
                    "No TikTok, vá em seu perfil e toque nas três barras no canto superior direito.",
                    "Selecione 'Configurações e Privacidade' e toque na opção 'Anúncios'.",
                    "Desative a chave chamada 'Anúncios personalizados'."
                ]
            },
            {
                "titulo": "Bloquear o Compartilhamento de Contatos e Facebook",
                "passos": [
                    "Nas 'Configurações e Privacidade' do TikTok, clique em 'Privacidade'.",
                    "Toque em 'Sincronizar contatos e amigos do Facebook'.",
                    "Desative ambas as chaves para que o aplicativo não varra sua lista telefônica ou amigos do Facebook."
                ]
            }
        ]
    },
    "WhatsApp": {
        "resumo_claro": "Embora o conteúdo das mensagens de texto e áudio seja protegido por criptografia de ponta a ponta (o WhatsApp não pode ler suas conversas), o aplicativo coleta e compartilha massivamente os metadados. Isso inclui as pessoas com quem você conversa, os horários das mensagens, o modelo do seu celular, seu endereço de IP e dados de compras.",
        "red_flags": ["Compartilhamento de Metadados", "Acesso à Lista de Contatos", "Histórico de Conexões", "Rastreamento de IP", "Dados de Pagamentos"],
        "palavra_mais_critica": "Vazamento de Metadados (Com quem e quando você conversa)",
        "pontuacao_risco": 55,
        "dicas_protecao": [
            {
                "titulo": "Proteger seu Endereço de IP em Chamadas",
                "passos": [
                    "No WhatsApp, abra as 'Configurações' do aplicativo.",
                    "Toque em 'Privacidade' e depois role a página até o final e toque em 'Configurações avançadas'.",
                    "Ative a chave 'Proteger endereço IP nas chamadas' (isso evita que a outra pessoa descubra sua localização aproximada através da ligação)."
                ]
            },
            {
                "titulo": "Ativar Criptografia para Seus Backups em Nuvem",
                "passos": [
                    "Vá em 'Configurações' no WhatsApp e selecione 'Conversas'.",
                    "Toque em 'Backup de conversas'.",
                    "Toque em 'Backup protegido por criptografia de ponta a ponta', ative e crie uma senha segura (isso impede que a Google ou a Apple acessem suas mensagens salvas)."
                ]
            },
            {
                "titulo": "Remover Informações de Status e Foto Pública",
                "passos": [
                    "Vá em 'Configurações' > 'Privacidade'.",
                    "Toque em 'Visto por último e online' e mude para 'Meus contatos' ou 'Ninguém'.",
                    "Faça o mesmo para 'Foto do perfil' e 'Recado', garantindo que desconhecidos não vejam seus detalhes pessoais."
                ]
            }
        ]
    },
    "YouTube": {
        "resumo_claro": "O YouTube é de propriedade da Google, o que significa que seu histórico de vídeos assistidos, termos pesquisados e tempo de exibição são unidos ao seu perfil global de pesquisas. Esses dados alimentam algoritmos projetados para traçar perfis psicológicos e influenciar seus hábitos de consumo através de vídeos recomendados.",
        "red_flags": ["Perfilamento Psicográfico", "Registro Eterno de Histórico", "Conexão com Contas Google", "Monitoramento de Tempo de Tela", "Rastreamento de Interesses"],
        "palavra_mais_critica": "Perfilamento Unificado com Conta Google",
        "pontuacao_risco": 70,
        "dicas_protecao": [
            {
                "titulo": "Desativar ou Pausar o Histórico de Exibição do YouTube",
                "passos": [
                    "Abra o YouTube e toque na sua foto de perfil ('Você') no canto inferior direito.",
                    "Toque no ícone de engrenagem no topo direito e clique em 'Gerenciar todo o histórico'.",
                    "Toque na aba 'Controles' e mude a chave de 'Histórico do YouTube' para desativada (pausada)."
                ]
            },
            {
                "titulo": "Remover Seus Dados de Anúncios na Conta Google",
                "passos": [
                    "Acesse o site 'myaccount.google.com' no navegador e faça login.",
                    "Vá para a aba 'Dados e Privacidade' e procure por 'Configurações de anúncios'.",
                    "Selecione 'Minha central de anúncios' e desligue completamente a chave de 'Anúncios personalizados'."
                ]
            },
            {
                "titulo": "Configurar a Exclusão Automática do Histórico",
                "passos": [
                    "No menu 'Gerenciar todo o histórico' (conforme Passo 1), procure a opção 'Exclusão automática'.",
                    "Escolha o período limite que deseja (por exemplo, excluir automaticamente tudo com mais de 3 meses).",
                    "Confirme a configuração para que a Google não acumule dados de anos sobre sua rotina."
                ]
            }
        ]
    },
    "Twitter (X)": {
        "resumo_claro": "O Twitter (X) alterou radicalmente seus termos de privacidade para extrair, ler e processar todas as suas postagens públicas, curtidas e repostagens de forma a treinar e evoluir seu modelo proprietário de Inteligência Artificial chamado Grok. Além disso, rastreia links acessados e repassa dados de emprego e biometria se houver cadastro formal.",
        "red_flags": ["Treinamento de IA Proprietária", "Rastreamento de Biometria", "Venda de Dados para Parceiros", "Monitoramento de Cliques", "Extração de Posts"],
        "palavra_mais_critica": "Treinamento do Grok com Posts Pessoais",
        "pontuacao_risco": 75,
        "dicas_protecao": [
            {
                "titulo": "Impedir que o X use seus Posts para Treinar a IA (Grok)",
                "passos": [
                    "No site ou app do X, clique na sua foto de perfil e vá em 'Configurações e suporte' > 'Configurações e privacidade'.",
                    "Toque em 'Privacidade e segurança' e role até encontrar a opção 'Grok'.",
                    "Desmarque a caixa de seleção que permite o compartilhamento de dados e posts com a inteligência artificial."
                ]
            },
            {
                "titulo": "Restringir o Compartilhamento de Dados com Parceiros",
                "passos": [
                    "Acesse novamente as configurações de 'Privacidade e segurança'.",
                    "Selecione 'Compartilhamento de dados e personalização'.",
                    "Desative todas as chaves associadas a 'Compartilhamento de dados com parceiros de negócios'."
                ]
            },
            {
                "titulo": "Remover a Visibilidade dos seus Posts para Mecanismos de Busca",
                "passos": [
                    "Nas configurações de 'Privacidade e segurança', vá em 'Público e marcação'.",
                    "Ative a chave 'Proteger suas postagens' (isso tornará sua conta privada, fazendo com que somente seus seguidores aprovados vejam seus posts)."
                ]
            }
        ]
    },
    "Snapchat": {
        "resumo_claro": "Embora o Snapchat promova que as fotos desaparecem instantaneamente, o aplicativo rastreia intensamente sua localização em tempo real para exibi-la em um mapa global interativo público (o Snap Map). O app também monitora o comportamento de câmeras, rostos (filtros) e contatos, usando IA para perfilar sua rotina diária.",
        "red_flags": ["Rastreamento de Localização em Tempo Real", "Processamento de Imagens de Rosto", "Metadados de Fotos salvas", "Compartilhamento de Contatos", "Publicidade Direcionada"],
        "palavra_mais_critica": "Rastreamento de Localização Contínua em Tempo Real",
        "pontuacao_risco": 65,
        "dicas_protecao": [
            {
                "titulo": "Ativar o Modo Fantasma no Mapa do Snapchat",
                "passos": [
                    "Abra o Snapchat, deslize a tela para a direita para acessar o Mapa.",
                    "Toque no ícone de engrenagem no canto superior direito do Mapa.",
                    "Ative a chave do 'Modo Fantasma' para esconder sua localização de todos os seus amigos permanentemente."
                ]
            },
            {
                "titulo": "Limitar o Acesso à Câmera quando o App não estiver em Uso",
                "passos": [
                    "Vá nas configurações gerais do seu smartphone.",
                    "Procure o aplicativo 'Snapchat' na lista.",
                    "Toque em 'Permissões' > 'Câmera' e selecione 'Permitir apenas durante o uso do app'."
                ]
            },
            {
                "titulo": "Desativar Anúncios de Terceiros e Interesses",
                "passos": [
                    "No Snapchat, toque no seu perfil e depois na engrenagem de Configurações.",
                    "Role até encontrar 'Controles de Privacidade' e clique em 'Preferências de anúncios'.",
                    "Desmarque todas as opções de categorias de interesses para evitar publicidade direcionada agressiva."
                ]
            }
        ]
    }
}

# Função para carregar o arquivo txt
def carregar_termo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return f.read()
    return None

# Função cacheada para análise com o Gemini com mecanismo automático de fallback em caso de erros (ex: 503)
@st.cache_data(show_spinner="Desvendando o pergaminho de termos de privacidade... Por favor, aguarde.")
def analisar_termo_com_gemini(texto_termo, nome_plataforma):
    # Se a API não estiver configurada no servidor, vai direto para o acervo de contingência offline
    if not client:
        return ACERVO_CONTINGENCIA.get(nome_plataforma), True
        
    prompt = f"""
    Você é um especialista em direito digital e privacidade de dados. 
    Analise o termo de privacidade completo da plataforma {nome_plataforma} fornecido abaixo.
    Extraia as informações necessárias respeitando estritamente o esquema JSON solicitado.
    Escreva os 'passos' de cada dica como se estivesse explicando para uma avó ou pessoa totalmente leiga em tecnologia.
    
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
        return json.loads(response.text), False
    except Exception as e:
        # Se a API der erro (503, indisponibilidade ou limite), recuperamos o laudo do banco offline
        # Isso garante que o app NUNCA quebre ou exiba erros vermelhos de código!
        dados_reserva = ACERVO_CONTINGENCIA.get(nome_plataforma)
        if dados_reserva:
            return dados_reserva, True
        else:
            st.error(f"Ocorreu um erro ao obter dados do Gemini e não localizamos cópias locais de contingência: {e}")
            return None, False

# --- GERADOR DE PDF TEMÁTICO "A BELA E A FERA" ---
def gerar_pdf_escudo(nome_plataforma, analise):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    story = []
    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle(
        'RoyalTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#162E5C'), # Azul Imperial
        alignment=1,
        spaceAfter=5
    )
    
    style_subtitle = ParagraphStyle(
        'RoyalSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        textColor=colors.HexColor('#5C4B40'),
        alignment=1,
        spaceAfter=15
    )

    style_section = ParagraphStyle(
        'RoyalSec',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#162E5C'),
        spaceBefore=12,
        spaceAfter=8
    )
    
    style_body = ParagraphStyle(
        'RoyalBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#2C1E21'),
        leading=14,
        spaceAfter=8
    )

    style_step = ParagraphStyle(
        'RoyalStep',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#2E7D32'), # Verde floresta de proteção
        leading=13,
        leftIndent=15,
        spaceAfter=4
    )
    
    story.append(Paragraph("<b>O ESPELHO DA VERDADE</b>", style_title))
    story.append(Paragraph(f"Escudo de Defesa & Manual de Configuração — {nome_plataforma}", style_subtitle))
    
    tabela_divisor = Table([['']], colWidths=[530], rowHeights=[2])
    tabela_divisor.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#D4AF37')),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(tabela_divisor)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>📋 Cenário de Privacidade</b>", style_section))
    story.append(Paragraph(analise['resumo_claro'], style_body))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph("<b>🛡️ Manual Prático Passo a Passo (Sem Complicação)</b>", style_section))
    story.append(Paragraph("Siga atentamente as orientações abaixo para recuperar o controle da sua privacidade:", style_body))
    
    for i, dica in enumerate(analise['dicas_protecao'], 1):
        story.append(Paragraph(f"<b>Opção {i}: {dica['titulo']}</b>", ParagraphStyle('SubDica', parent=style_body, fontName='Helvetica-Bold', textColor=colors.HexColor('#162E5C'), spaceBefore=6)))
        for j, passo in enumerate(dica['passos'], 1):
            story.append(Paragraph(f"<b>Passo {j}:</b> {passo}", style_step))
        story.append(Spacer(1, 6))
        
    story.append(Spacer(1, 10))
    story.append(tabela_divisor)
    story.append(Spacer(1, 10))
    
    style_footer = ParagraphStyle(
        'RoyalFoot',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#6B5B52'),
        alignment=1
    )
    story.append(Paragraph("Laudo de Segurança Gerado com IA | Aluna FGV-ECMI: Keidy Alves Pizzetti Amaro", style_footer))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Dados estáticos para o gráfico de comparação
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

# Seleção de redes
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

if texto_contrato:
    # Retorna o dicionário de dados e se foi gerado a partir do backup offline (contingência)
    analise, is_fallback = analisar_termo_com_gemini(texto_contrato, nome_analise)
    
    if analise:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Alerta amigável no tema do site caso o Gemini esteja fora do ar e ativamos a contingência
        if is_fallback:
            st.markdown("""
                <div style="
                    background-color: #FCF4E3; 
                    border: 1px solid #D4AF37; 
                    border-radius: 6px; 
                    padding: 15px; 
                    margin-bottom: 25px; 
                    text-align: center;
                ">
                    <span style="font-size: 1.2rem;">✨</span> 
                    <span style="font-family: 'Lora', serif; font-style: italic; font-size: 1rem; color: #73571A;">
                        <b>Nota do Castelo:</b> O Espelho da Verdade está sob alta névoa mágica no momento devido à alta demanda (Instabilidade na Google Cloud). 
                        Para sua proteção, o castelo carregou instantaneamente uma cópia arquivada de alta precisão deste pergaminho de defesa!
                    </span>
                </div>
            """, unsafe_allow_html=True)

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
            
            st.markdown("""
                <div class="defenda-se-texto">🛡️ GUIA PASSO A PASSO DE CONFIGURAÇÃO:</div>
            """, unsafe_allow_html=True)
            
            for index, dica in enumerate(analise['dicas_protecao'], 1):
                with st.expander(f"⚙️ {index}. {dica['titulo']}", expanded=(index == 1)):
                    for step_idx, passo in enumerate(dica['passos'], 1):
                        st.markdown(f"**{step_idx}º Passo:** {passo}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- EXPORTAR RELATÓRIO EM PDF ---
            if PDF_DISPONIVEL:
                pdf_bytes = gerar_pdf_escudo(nome_analise, analise)
                st.download_button(
                    label="📜 Baixar Escudo de Defesa em PDF",
                    data=pdf_bytes,
                    file_name=f"Escudo_Defesa_{nome_analise.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("O motor de geração de PDF está temporariamente offline. Baixe em formato de texto abaixo:")
                relatorio_txt = f"Guia de Proteção: {nome_analise}\n"
                st.download_button(
                    label="📄 Baixar Relatório em formato de Texto (.txt)",
                    data=relatorio_txt,
                    file_name=f"Guia_Defesa_{nome_analise}.txt",
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
