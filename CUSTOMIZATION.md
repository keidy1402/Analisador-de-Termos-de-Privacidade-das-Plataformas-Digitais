# 🎨 Guia de Personalização e Melhorias

## Personalizações Fáceis (Sem Alterar Lógica)

### 1. Mudar Cores do App

No arquivo `app.py`, busque por `<style>` e altere os valores hex:

```css
/* Header Principal */
background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8c 100%);
/* Altere #1e3a5f e #2d5a8c para suas cores */
```

**Sugestões de paletas:**

- **Azul/Verde** (Segurança):
  - Primário: #0a7377
  - Secundário: #14919b

- **Roxo/Rosa** (Moderno):
  - Primário: #7209b7
  - Secundário: #c60c30

- **Preto/Ouro** (Premium):
  - Primário: #1a1a1a
  - Secundário: #d4af37

### 2. Adicionar Logo/Ícone Customizado

No header, após `<h1>`, adicione:

```python
st.markdown("![Logo](https://url-da-sua-logo.png)")
```

### 3. Mudar Textos e Mensagens

Busque pelas strings que deseja alterar:

```python
st.markdown("Seu novo texto aqui")
```

### 4. Alterar Ordem das Seções

Recorte as seções (blocos de código) e recoloque na ordem desejada no `app.py`.

---

## Melhorias Intermediárias

### 1. Adicionar Mais Plataformas

```python
RISK_DATA = {
    "LinkedIn": {
        "risk_score": 45,
        "palavras_risco": ["dados profissionais", "conexões", "histórico"],
        "dicas": ["✓ Dica 1", "✓ Dica 2"]
    },
    # Adicione mais aqui...
}
```

Depois, adicione botões na seção 1:

```python
with col_new:
    if st.button("💼 LinkedIn", key="linkedin", use_container_width=True):
        st.session_state.plataforma_selecionada = "LinkedIn"
```

### 2. Adicionar Análise de Múltiplas Plataformas Simultâneas

```python
# Na Seção 1, altere para:
plataformas_selecionadas = st.multiselect(
    "Selecione as plataformas:",
    plataformas
)

if plataformas_selecionadas:
    for platform in plataformas_selecionadas:
        # Executar análise para cada uma
```

### 3. Salvar Histórico de Análises

```python
import json
from datetime import datetime

# Adicionar ao session_state
if 'historico' not in st.session_state:
    st.session_state.historico = []

# Após análise, adicionar:
st.session_state.historico.append({
    "data": datetime.now().isoformat(),
    "plataforma": platform,
    "score": risk_score
})

# Salvar em arquivo JSON
with open("historico.json", "w") as f:
    json.dump(st.session_state.historico, f)
```

### 4. Adicionar Gráfico de Histórico

```python
import plotly.express as px

if st.session_state.historico:
    df_historico = pd.DataFrame(st.session_state.historico)
    fig = px.line(df_historico, x='data', y='score', color='plataforma')
    st.plotly_chart(fig)
```

### 5. Dark Mode Toggle

```python
# Na sidebar:
theme = st.sidebar.radio("Tema:", ["Claro", "Escuro"])

if theme == "Escuro":
    st.markdown("""
    <style>
        body { background-color: #1e1e1e; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)
```

---

## Melhorias Avançadas

### 1. Integração com Banco de Dados

```python
import sqlite3

# Criar conexão
conn = sqlite3.connect('privacidade.db')
c = conn.cursor()

# Criar tabela
c.execute('''CREATE TABLE IF NOT EXISTS analises
             (id INTEGER PRIMARY KEY, plataforma TEXT, score INTEGER, data TIMESTAMP)''')

# Inserir dados
c.execute("INSERT INTO analises VALUES (?, ?, ?, ?)", 
          (None, platform, risk_score, datetime.now()))

conn.commit()
```

### 2. Autenticação de Usuários

```python
import hashlib

# Hash de senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Na sidebar:
with st.sidebar.expander("👤 Login"):
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        # Verificar no banco de dados
        pass
```

### 3. Exportar Relatório em PDF

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def gerar_pdf(platform, risk_score, dicas):
    c = canvas.Canvas(f"relatorio_{platform}.pdf", pagesize=letter)
    c.drawString(100, 750, f"Análise de Privacidade: {platform}")
    c.drawString(100, 730, f"Score de Risco: {risk_score}/100")
    # Adicionar mais conteúdo...
    c.save()

# Botão no app:
if st.button("📥 Baixar Relatório"):
    gerar_pdf(platform, risk_score, risk_data["dicas"])
    st.success("Relatório gerado!")
```

### 4. Notificações em Tempo Real

```python
import firebase_admin
from firebase_admin import db

# Configurar Firebase
cred = firebase_admin.credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://seu-projeto.firebaseio.com'
})

# Buscar notificações
ref = db.reference('/noticias')
noticias_reais = ref.get()
```

### 5. Analytics e Tracking

```python
import plausible

# Rastrear eventos
plausible.track(
    event_name="platforma_analisada",
    props={
        "plataforma": platform,
        "score": risk_score
    }
)
```

---

## Melhorias de UX/UI

### 1. Adicionar Animações

```python
import streamlit.components.v1 as components

# Fade-in effect
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .fade-in { animation: fadeIn 0.5s; }
</style>
<div class="fade-in">Conteúdo animado</div>
""", unsafe_allow_html=True)
```

### 2. Progress Bar

```python
progress = st.progress(0)
for i in range(100):
    progress.progress(i + 1)
    # Fazer alguma coisa
```

### 3. Toast Notifications

```python
st.success("✅ Análise concluída!")
st.warning("⚠️ Aviso!")
st.error("❌ Erro!")
st.info("ℹ️ Informação")
```

### 4. Sidebar Interativa

```python
with st.sidebar:
    st.title("📋 Controles")
    
    seção = st.radio(
        "Ir para seção:",
        ["Análise", "Dicas", "Gráficos", "Notícias"]
    )
    
    if seção == "Análise":
        st.write("Conteúdo da seção de análise...")
```

### 5. Responsividade Melhorada

```python
# Detectar tamanho da tela
st.session_state.mobile = st.columns(1)

if len(st.columns(3)) > 2:
    # Desktop
    col1, col2, col3 = st.columns(3)
else:
    # Mobile
    col1 = st.columns(1)[0]
```

---

## Performance e Otimizações

### 1. Cache de Resultados

```python
@st.cache_data(ttl=3600)  # Cache por 1 hora
def fetch_risk_data(platform):
    # Buscar dados que não mudam frequentemente
    return RISK_DATA[platform]
```

### 2. Lazy Loading de Imagens

```python
from PIL import Image

@st.cache_resource
def load_logo():
    return Image.open("logo.png")

logo = load_logo()
st.image(logo, width=100)
```

### 3. Reduzir Tamanho do Bundle

```python
# Remover bibliotecas não usadas do requirements.txt
# Usar versões mais leves quando possível
```

---

## Checklist de Customização Completa

- [ ] Mudar cores e tema
- [ ] Adicionar logo
- [ ] Adicionar mais plataformas
- [ ] Implementar banco de dados
- [ ] Adicionar autenticação
- [ ] Gerar relatórios em PDF
- [ ] Adicionar analytics
- [ ] Melhorar responsividade mobile
- [ ] Otimizar performance
- [ ] Testar em todos os navegadores
- [ ] Deploy em staging antes de produção
- [ ] Monitorar erros com Sentry
- [ ] Configurar CI/CD com GitHub Actions

---

## Recursos Úteis

- 📚 [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- 🎨 [Streamlit Components Gallery](https://streamlit.io/components)
- 📊 [Plotly Documentation](https://plotly.com/python/)
- 🐍 [Python Best Practices](https://pep8.org/)
- 🚀 [GitHub Actions CI/CD](https://github.com/features/actions)

---

## Dúvidas Frequentes

**P: Como adicionar login?**
R: Veja a seção "Autenticação de Usuários" acima.

**P: Posso usar um banco de dados SQL?**
R: Sim! Recomendamos PostgreSQL com SQLAlchemy.

**P: Como publicar atualizações?**
R: Faça push para GitHub e Streamlit Cloud redeploya automaticamente.

**P: Qual a melhor prática para secrets?**
R: Nunca coloque no código. Use Streamlit Secrets ou variáveis de ambiente.

---

Boa sorte com suas customizações! 🚀
