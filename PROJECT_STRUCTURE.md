# 📁 Estrutura do Projeto - Analisador de Privacidade Digital

## 📂 Estrutura de Arquivos

```
analisador-privacidade/
│
├── 📄 app.py                      # Aplicação principal do Streamlit
├── 📄 requirements.txt             # Dependências do Python
├── 📄 README.md                    # Documentação principal
├── 📄 DEPLOYMENT.md                # Guia de deploy no Streamlit Cloud
├── 📄 CUSTOMIZATION.md             # Guia de personalização e melhorias
├── 📄 .env.example                 # Exemplo de variáveis de ambiente
├── 📄 .gitignore                   # Arquivos a ignorar no Git
├── 📄 run.bat                      # Script de inicialização (Windows)
├── 📄 run.sh                       # Script de inicialização (Linux/Mac)
│
└── 📁 .streamlit/
    └── 📄 config.toml              # Configuração do Streamlit
```

## 📋 Descrição de Cada Arquivo

### 🔴 **app.py** (Aplicação Principal)
- **Tamanho**: ~800 linhas
- **Função**: Contém toda a lógica do aplicativo
- **Principais componentes**:
  - Interface do Streamlit com 6 seções
  - Dados de risco para 7 plataformas
  - Integração com Google Gemini API (opcional)
  - Geração de nuvem de palavras
  - Gráficos comparativos
  - Busca de notícias via Google News
  - Estilos CSS customizados

### 📦 **requirements.txt**
- **Função**: Lista todas as bibliotecas Python necessárias
- **Conteúdo**:
  - streamlit (framework web)
  - pandas (análise de dados)
  - numpy (computação numérica)
  - matplotlib (gráficos estáticos)
  - plotly (gráficos interativos)
  - wordcloud (nuvem de palavras)
  - requests (requisições HTTP)
  - google-generativeai (API Gemini)

### 📚 **README.md**
- **Função**: Documentação principal do projeto
- **Contém**:
  - Descrição das 6 seções
  - Instruções de instalação local
  - Guia de deploy no Streamlit Cloud
  - Segurança e privacidade
  - Informações sobre as fontes de dados

### 🚀 **DEPLOYMENT.md**
- **Função**: Guia passo a passo para deploy
- **Tópicos**:
  - Como obter chave do Gemini
  - Preparação do repositório GitHub
  - Deploy no Streamlit Cloud
  - Configuração de secrets
  - Troubleshooting

### 🎨 **CUSTOMIZATION.md**
- **Função**: Guia de personalização
- **Inclui**:
  - Mudanças fáceis (cores, textos)
  - Melhorias intermediárias (mais plataformas)
  - Melhorias avançadas (banco de dados, autenticação)
  - Otimizações de performance
  - Dicas de UX/UI

### 🔑 **.env.example**
- **Função**: Exemplo de variáveis de ambiente
- **Uso**: Copiar para `.env` e preencher com suas chaves
- **NÃO enviar para GitHub** (protege suas credenciais)

### 🚫 **.gitignore**
- **Função**: Indica ao Git quais arquivos NÃO fazer upload
- **Inclui**:
  - Ambiente virtual (`venv/`)
  - Arquivos Python compilados
  - IDE settings
  - Variáveis de ambiente (`.env`)

### ⚙️ **run.bat** (Windows)
- **Função**: Script de inicialização automática
- **O que faz**:
  1. Verifica se Python está instalado
  2. Cria ambiente virtual
  3. Instala dependências
  4. Inicia o Streamlit

**Como usar:**
```bash
duplo clique em run.bat
```

### 🐧 **run.sh** (Linux/Mac)
- **Função**: Mesmo do run.bat, mas para Unix
- **Como usar**:
```bash
chmod +x run.sh
./run.sh
```

### ⚙️ **.streamlit/config.toml**
- **Função**: Configurações do Streamlit
- **Define**:
  - Cores do tema (primária, secundária)
  - Fonte padrão
  - Modo de execução
  - Porta (8501)

## 🔄 Fluxo de Funcionamento

```
Usuario Acessa app.streamlit.app
         ↓
   [Interface Carrega]
   - Header com logo
   - 7 Botões de plataformas
         ↓
Usuario Clica em Plataforma
         ↓
   [Dados Carregam]
   - Score de risco
   - Análise Gemini (opcional)
   - Nuvem de palavras
   - Dicas de proteção
   - Gráfico comparativo
   - Notícias Google
         ↓
Usuario Interage com Conteúdo
   - Clica em links de notícias
   - Vê gráficos interativos
   - Lê recomendações
         ↓
   [Experiência Completa]
```

## 📊 Dados do Projeto

### Plataformas Analisadas
1. **WhatsApp** - Risk Score: 35 (Baixo)
2. **Snapchat** - Risk Score: 62 (Médio)
3. **YouTube** - Risk Score: 58 (Médio)
4. **Facebook** - Risk Score: 72 (Alto)
5. **Instagram** - Risk Score: 68 (Alto)
6. **Twitter** - Risk Score: 55 (Médio)
7. **TikTok** - Risk Score: 85 (Muito Alto)

### Dados por Plataforma
Para cada plataforma, contemos:
- Score de risco (0-100)
- 5-7 palavras-chave de risco
- 5 dicas práticas de proteção

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.8+** - Linguagem
- **Streamlit** - Framework web
- **Pandas** - Manipulação de dados
- **Numpy** - Cálculos numéricos

### Visualização
- **Matplotlib** - Gráficos estáticos
- **Plotly** - Gráficos interativos
- **WordCloud** - Nuvem de palavras

### APIs e Integração
- **Google Generative AI (Gemini)** - Análise com IA
- **Google News RSS** - Notícias atualizadas
- **Requests** - Requisições HTTP

### DevOps
- **Git/GitHub** - Versionamento
- **Streamlit Cloud** - Hospedagem
- **Streamlit Secrets** - Gerenciamento de credenciais

## 🔐 Segurança

### Dados Sensíveis
- **Nunca** coloque API keys no código
- **Use** `.env.example` como template
- **Configure** secrets no Streamlit Cloud
- **Ignore** `.env` com `.gitignore`

### Autenticação
- App é público (sem login requerido)
- Pode ser expandido com autenticação
- Veja `CUSTOMIZATION.md` para detalhes

## 📈 Performance

### Otimizações Implementadas
- Cache de dados com `@st.cache_data`
- CSS inline ao invés de arquivo externo
- Lazy loading de notícias
- Reuso de componentes

### Tempo de Carregamento
- Página inicial: ~2-3 segundos
- Análise de plataforma: ~1-2 segundos
- Notícias: ~3-5 segundos
- Gráfico: ~1 segundo

## 📱 Responsividade

### Dispositivos Suportados
- ✅ Desktop (1920x1080+)
- ✅ Tablet (768px+)
- ✅ Mobile (375px+)

### Layout Adaptativo
- Colunas ajustam automaticamente
- Fonte responsiva
- Imagens escaláveis

## 🌐 Compatibilidade

### Navegadores
- ✅ Chrome (recomendado)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

### Sistemas Operacionais
- ✅ Windows 10+
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu 18.04+)

## 📞 Suporte

### Ficheiros Inclusionais

```
├── Documentação completa em README.md
├── Guia de deployment em DEPLOYMENT.md
├── Exemplos de customização em CUSTOMIZATION.md
└── Este arquivo (estrutura do projeto)
```

### Recursos Externos
- [Documentação Streamlit](https://docs.streamlit.io)
- [API Gemini Google](https://ai.google.dev)
- [Tutoriais Python](https://python.org/tutorial)

---

**Estrutura organizada para fácil manutenção e escalabilidade! 🎯**
