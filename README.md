# 🔐 Analisador de Privacidade Digital

Um aplicativo web interativo que analisa os termos de privacidade e riscos de segurança digital das principais plataformas de redes sociais.

## 🎯 Funcionalidades

✅ **6 Seções Principais:**

1. **Seleção de Plataforma** - Escolha entre 7 plataformas (WhatsApp, Snapchat, YouTube, Facebook, Instagram, Twitter, TikTok)

2. **Resumo dos Termos** - Análise automática dos termos de privacidade com score de risco visual

3. **Nuvem de Palavras** - Visualização das palavras-chave de maior risco para cada plataforma

4. **Dicas de Proteção** - Recomendações práticas e específicas de como se proteger em cada plataforma

5. **Gráfico Comparativo** - Comparação visual do nível de risco entre todas as 7 plataformas

6. **Notícias Atualizadas** - Integração com Google News para trazer as últimas notícias sobre privacidade e segurança

## 🚀 Como Instalar Localmente

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes do Python)

### Passos de Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/analisador-privacidade.git
cd analisador-privacidade
```

2. **Crie um ambiente virtual (recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure a API do Gemini (Opcional):**

Para ativar a análise com IA do Gemini:

```bash
export GEMINI_API_KEY="sua_chave_aqui"  # Linux/Mac
set GEMINI_API_KEY=sua_chave_aqui       # Windows
```

5. **Execute o aplicativo:**
```bash
streamlit run app.py
```

O app abrirá automaticamente no seu navegador em `http://localhost:8501`

## 📦 Deploy no Streamlit Cloud

### Passo 1: Prepare o Repositório

1. Crie um repositório GitHub com os arquivos:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `README.md`

2. Faça commit e push:
```bash
git add .
git commit -m "Initial commit: Privacy Analyzer"
git push origin main
```

### Passo 2: Deploy no Streamlit Cloud

1. Acesse [Streamlit Cloud](https://streamlit.io/cloud)

2. Clique em "New app"

3. Selecione:
   - **Repository:** seu repositório GitHub
   - **Branch:** main
   - **Main file path:** app.py

4. Clique em "Deploy"

5. Configure as secrets (se usar API Gemini):
   - Na aba "Advanced settings"
   - Adicione: `GEMINI_API_KEY = "sua_chave_aqui"`

### Passo 3: Compartilhe

O app estará disponível em:
```
https://seu-usuario-analisador-privacidade.streamlit.app
```

## 🔧 Configurações Avançadas

### Adicionar Mais Plataformas

Edite o dicionário `RISK_DATA` em `app.py`:

```python
"NovaPlatforma": {
    "risk_score": 60,  # Score de 0-100
    "palavras_risco": ["palavra1", "palavra2", "palavra3"],
    "dicas": [
        "✓ Dica 1",
        "✓ Dica 2",
        "✓ Dica 3",
    ]
},
```

### Personalizar Cores

As cores estão definidas em:
- `#1e3a5f` - Azul primário
- `#e63946` - Vermelho (alto risco)
- `#f77f00` - Laranja (risco médio)
- `#06a77d` - Verde (baixo risco)

Altere no CSS customizado dentro de `st.markdown()`

### Integrar com Banco de Dados

O app pode ser expandido para:
- Armazenar histórico de análises
- Salvar preferências do usuário
- Rastrear mudanças nos scores de risco

## 📊 Dados e Fontes

Os dados de risco foram compilados a partir de:
- Termos de privacidade oficiais
- Relatórios de segurança OWASP
- Análises de privacidade independentes
- Regulações de proteção de dados (LGPD, GDPR)

## 🔐 Segurança

- ✅ Nenhum dado do usuário é armazenado
- ✅ Conexão HTTPS obrigatória no Streamlit Cloud
- ✅ Sem cookies rastreadores
- ✅ Sem integração com redes sociais (apenas análise informativa)

## 📝 Licença

Este projeto é de código aberto sob a licença MIT.

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 💬 Feedback

Se encontrar bugs ou tiver sugestões, abra uma [Issue](https://github.com/seu-usuario/analisador-privacidade/issues)

## 🎓 Objetivos Educacionais

Este projeto visa:
- 📚 Educar usuários sobre privacidade digital
- 🛡️ Aumentar a conscientização sobre segurança
- 📊 Fornecer dados comparativos sobre riscos
- 💡 Oferecer dicas práticas e acionáveis
- 🔍 Promover transparência no uso de dados

## 📞 Suporte

Para dúvidas técnicas ou sugestões, consulte a documentação:
- [Documentação Streamlit](https://docs.streamlit.io)
- [Guia da API Gemini](https://ai.google.dev/docs)

---

**Desenvolvido com ❤️ para a segurança digital do cidadão brasileiro**
