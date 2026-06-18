# 🚀 Guia Completo: Deploy no Streamlit Cloud

## Pré-requisitos

1. Conta GitHub
2. Conta Streamlit Cloud (gratuita em https://streamlit.io/cloud)
3. Chave de API do Google Gemini (opcional, mas recomendado)

## Passo 1: Obter Chave do Google Gemini

### Por que usar Gemini?
A API do Gemini permite análises mais precisas dos termos de privacidade usando IA avançada.

### Como obter:

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Clique em "Create API Key"
3. Copie a chave gerada
4. Salve em um local seguro (você precisará dela no Streamlit Cloud)

## Passo 2: Preparar o Repositório GitHub

### Opção A: Se já tem o Git instalado

```bash
# 1. Crie uma pasta para o projeto
mkdir analisador-privacidade
cd analisador-privacidade

# 2. Inicialize o repositório
git init

# 3. Copie os arquivos do projeto para esta pasta:
# - app.py
# - requirements.txt
# - .streamlit/config.toml
# - README.md
# - .gitignore

# 4. Configure sua conta GitHub
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

# 5. Adicione os arquivos
git add .

# 6. Commit inicial
git commit -m "Initial commit: Privacy Analyzer App"

# 7. Crie um repositório no GitHub e configure o remote
git remote add origin https://github.com/seu-usuario/analisador-privacidade.git
git branch -M main
git push -u origin main
```

### Opção B: Pelo GitHub Web Interface

1. Acesse [github.com/new](https://github.com/new)
2. Crie um novo repositório chamado `analisador-privacidade`
3. Clique em "Upload files"
4. Arraste os arquivos (app.py, requirements.txt, etc)
5. Commit na main branch

## Passo 3: Deploy no Streamlit Cloud

### Configuração Inicial

1. Acesse [Streamlit Cloud](https://streamlit.io/cloud)
2. Clique em "Sign in with GitHub" (ou crie uma conta)
3. Autorize o Streamlit a acessar seus repositórios

### Criar a App

1. Clique em "New app"
2. Preencha:
   - **Repository:** seu-usuario/analisador-privacidade
   - **Branch:** main
   - **Main file path:** app.py

3. Clique em "Deploy"

O app estará disponível em:
```
https://seu-usuario-analisador-privacidade.streamlit.app
```

## Passo 4: Configurar Secrets (API Key)

### No Streamlit Cloud

1. Acesse seu painel de apps
2. Clique nos "⋮" (três pontos) ao lado do app
3. Selecione "Edit secrets"
4. Cole o conteúdo:

```
GEMINI_API_KEY = "sua_chave_aqui"
```

5. Salve
6. O app será reiniciado automaticamente

### Estrutura do Arquivo de Secrets

Local: `.streamlit/secrets.toml` (use este arquivo localmente, não envie para GitHub!)

```toml
GEMINI_API_KEY = "sua_chave_aqui"
```

## Passo 5: Teste o App

1. Acesse sua URL do Streamlit Cloud
2. Selecione uma plataforma
3. Verifique se as análises, gráficos e notícias carregam

## Troubleshooting

### Erro: "GEMINI_API_KEY não encontrado"

**Solução:**
- Verifique se adicionou o secret no Streamlit Cloud
- Aguarde 30 segundos e recarregue a página
- Revise se não há espaços extras na chave

### Erro: "Module not found"

**Solução:**
- Verifique se `requirements.txt` está no root do repositório
- Confirme que o arquivo está no formato correto (uma dependência por linha)

### Notícias não carregam

**Solução:**
- É normal se o Google News estar indisponível temporariamente
- O app possui fallback com links úteis
- Tente novamente em alguns minutos

### App muito lento

**Solução:**
- Isso é normal no primeiro carregamento
- Streamlit Cloud pode demorar alguns segundos
- Se persistir, reduza o tamanho da nuvem de palavras em `app.py`

## Atualizações Futuras

Sempre que fizer mudanças no código:

```bash
git add .
git commit -m "Descrição da alteração"
git push origin main
```

O Streamlit Cloud redeploya automaticamente!

## Segurança

✅ **Boas práticas implementadas:**

- Nunca coloque a chave de API no código
- Use secrets do Streamlit Cloud
- Adicione `.env` ao `.gitignore`
- Nunca faça push de `secrets.toml`
- Regenere a chave periodicamente

## Monitoramento

No painel do Streamlit Cloud você pode:
- Ver logs de erro
- Monitorar uso de recursos
- Ver número de visitantes
- Configurar alertas

## Dúvidas?

- [Documentação Streamlit Cloud](https://docs.streamlit.io/streamlit-cloud/get-started)
- [Documentação API Gemini](https://ai.google.dev/docs)
- [GitHub Guides](https://guides.github.com)

---

**Pronto! Seu app está no ar! 🎉**
