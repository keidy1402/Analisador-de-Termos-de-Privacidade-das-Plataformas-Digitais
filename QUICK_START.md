# 🚀 GUIA RÁPIDO - Analisador de Privacidade Digital

## ⚡ Comece em 3 Minutos

### Opção 1: Windows (Mais Fácil)

1. **Extraia os arquivos** em uma pasta
2. **Duplo clique em `run.bat`**
3. **Aguarde ~30 segundos** enquanto dependências são instaladas
4. **O navegador abrirá automaticamente** em http://localhost:8501

✅ **Pronto! Seu app está rodando!**

---

### Opção 2: Linux/Mac (Terminal)

```bash
# 1. Vá para a pasta do projeto
cd analisador-privacidade

# 2. Dê permissão de execução
chmod +x run.sh

# 3. Execute
./run.sh

# 4. Acesse http://localhost:8501
```

---

### Opção 3: Manual (Qualquer Sistema)

```bash
# 1. Instale dependências
pip install -r requirements.txt

# 2. Inicie Streamlit
streamlit run app.py

# 3. Acesse http://localhost:8501
```

---

## 🌐 Deploy no Streamlit Cloud (Gratuito)

### Passo 1: Prepare no GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/SEU_USUARIO/analisador-privacidade.git
git push -u origin main
```

### Passo 2: Deploy

1. Acesse https://streamlit.io/cloud
2. Clique em "New app"
3. Selecione seu repositório e `app.py`
4. Clique em "Deploy"

**Seu app estará em:**
```
https://seu-usuario-analisador-privacidade.streamlit.app
```

---

## 📋 O Que o App Faz

### 🔴 Seção 1: Escolha Plataforma
- Selecione entre 7 redes sociais
- Interface intuitiva com botões coloridos

### 📊 Seção 2: Score de Risco
- Visualiza nível de risco (0-100)
- Verde (baixo) → Laranja (médio) → Vermelho (alto)

### ☁️ Seção 3: Palavras de Risco
- Nuvem de palavras destacando termos perigosos
- Maior = mais frequente nos termos

### 🛡️ Seção 4: Dicas de Proteção
- 5 dicas práticas e específicas
- Medidas que você pode tomar hoje

### 📈 Seção 5: Comparação
- Gráfico comparando riscos entre plataformas
- Veja qual é mais segura

### 📰 Seção 6: Notícias Atualizadas
- Últimas notícias sobre privacidade
- Integrado com Google News

---

## 🔧 Configurar API Gemini (Opcional)

**Por quê?** Para análises com Inteligência Artificial ainda melhores.

### 1. Obtenha a Chave

1. Acesse https://makersuite.google.com/app/apikey
2. Clique em "Create API Key"
3. Copie a chave

### 2. Configure Localmente

**Windows:**
```bash
setx GEMINI_API_KEY "sua_chave_aqui"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="sua_chave_aqui"
```

### 3. Configure no Streamlit Cloud

1. Acesse seu app em https://streamlit.io/cloud
2. Clique nos "⋮" → "Edit secrets"
3. Cole:
```
GEMINI_API_KEY = "sua_chave_aqui"
```

---

## 🐛 Problemas Comuns

### "Python não encontrado"
- Instale Python de https://python.org
- Marque "Add Python to PATH"
- Reinicie o computador

### "Módulo não encontrado"
```bash
pip install -r requirements.txt
```

### "Streamlit não executa"
```bash
pip install streamlit --upgrade
streamlit run app.py
```

### Notícias não carregam
- É normal às vezes
- Google News pode estar indisponível
- O app tem fallback automático
- Tente novamente em alguns minutos

---

## 🎨 Personalizações Simples

### Mudar Cores (Fácil)

No arquivo `app.py`, procure por:
```python
background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8c 100%);
```

Altere os códigos HEX das cores.

### Adicionar Mais Plataformas

No dicionário `RISK_DATA`, adicione:
```python
"TikTok": {
    "risk_score": 85,
    "palavras_risco": ["localização", "biometria"],
    "dicas": ["✓ Dica 1", "✓ Dica 2"]
}
```

### Mudar Textos

Procure pelos textos no `app.py` e altere.

---

## 📚 Documentação Completa

- **README.md** - Documentação detalhada
- **DEPLOYMENT.md** - Como fazer deploy
- **CUSTOMIZATION.md** - Como personalizar
- **PROJECT_STRUCTURE.md** - Estrutura de arquivos

---

## ✅ Checklist de Setup

- [ ] Baixei os arquivos
- [ ] Executei `run.bat` ou `run.sh`
- [ ] App abriu em http://localhost:8501
- [ ] Testei as 6 seções
- [ ] Criei repositório no GitHub
- [ ] Fiz deploy no Streamlit Cloud
- [ ] Configurei a chave do Gemini (opcional)
- [ ] Compartilhei o link com amigos!

---

## 🚀 Próximos Passos

1. **Teste localmente** com `run.bat`/`run.sh`
2. **Personalize** cores e textos
3. **Envie para GitHub**
4. **Deploy no Streamlit Cloud**
5. **Compartilhe com seus amigos**
6. **Veja em CUSTOMIZATION.md** para mais ideias

---

## 💡 Dicas Pro

- 🔐 Nunca compartilhe sua `GEMINI_API_KEY`
- 📱 Teste em mobile também
- 🔄 Sempre mantenha `requirements.txt` atualizado
- 💾 Faça commits regulares no Git
- 📊 Monitore seu app no Streamlit Cloud

---

## 🆘 Precisa de Ajuda?

### Documentação
- [Streamlit Docs](https://docs.streamlit.io)
- [Google Gemini API](https://ai.google.dev)
- [GitHub Help](https://docs.github.com)

### Comunidades
- [Streamlit Community](https://discuss.streamlit.io)
- [Stack Overflow - Python](https://stackoverflow.com/questions/tagged/python)
- [Reddit - r/Python](https://reddit.com/r/Python)

---

## 🎉 Parabéns!

Você agora tem um app profissional de análise de privacidade pronto para usar!

**Divirta-se e proteja-se digitalmente! 🔐**

---

**Última atualização: 2024**
**Versão: 1.0.0**
