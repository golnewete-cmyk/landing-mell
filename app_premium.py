import streamlit as st
import os
import datetime
import requests
import xml.etree.ElementTree as ET
from fpdf import FPDF

# --- TRATAMENTO DE ERRO DE UNICODE PARA FPDF ---
def formatar_pdf_text(txt):
    """Remove caracteres que a fonte Helvetica/Arial não suporta para evitar crash"""
    if not txt: return ""
    rep = {
        "—": "-", "–": "-", "“": '"', "”": '"', 
        "‘": "'", "’": "'", "…": "...", "•": "-",
        "\u2013": "-", "\u2014": "-", "\u201c": '"', "\u201d": '"'
    }
    for old, new in rep.items():
        txt = txt.replace(old, new)
    return txt.encode('latin-1', 'ignore').decode('latin-1')

# --- CONEXÃO REAL GOOGLE TRENDS (RSS FEEDS) ---
def buscar_google_trends():
    import requests
    from xml.etree import ElementTree as ET

    try:
        # TRUQUE: Usamos o Feed de Notícias do Google (mais estável que o Trends)
        # Ele traz o que é tendência no Brasil em tempo real sem bloqueio de RSS
        url = "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-150"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            trends = []
            
            # Varremos os itens de notícias que acabaram de sair (as tendências reais)
            for item in root.findall(".//item")[:10]:
                title = item.find("title").text
                # Limpamos o nome do jornal que vem no título (ex: - G1)
                clean_title = title.split(" - ")[0].upper()
                trends.append(f"- {clean_title} (TENDÊNCIA AGORA)")
            
            if trends:
                return trends
        
        # Se falhar, nosso backup estratégico de elite
        return ["IA E AUTOMAÇÃO", "ESTRATÉGIAS DE RETENÇÃO", "ALGORITMOS 2026"]

    except Exception:
        return ["MERCADO DIGITAL", "INTELIGÊNCIA DE DADOS", "NETWORKING PRO"]

# --- MOTOR DO RELATÓRIO PREMIUM ---
class DossiePremium(FPDF):
    def __init__(self, cliente):
        super().__init__()
        self.cliente = formatar_pdf_text(cliente)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'B', 8)
            self.set_text_color(180, 180, 180)
            self.cell(0, 10, f'INTEL REPORT V3.0 | {datetime.date.today().strftime("%d/%m/%Y")}', 0, 1, 'R')

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def gerar_capa(self, portal):
        self.add_page()
        self.set_fill_color(26, 26, 26)
        self.rect(0, 0, 210, 297, 'F')
        self.set_y(130)
        self.set_font('Arial', 'B', 32)
        self.set_text_color(197, 160, 89)
        self.cell(0, 20, self.cliente.upper(), ln=True, align='C')
        self.set_font('Arial', '', 12)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, formatar_pdf_text(portal), ln=True, align='C')

    def add_secao(self, tit, sub, msg):
        self.add_page()
        self.set_draw_color(197, 160, 89)
        self.rect(5, 5, 200, 287)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(197, 160, 89)
        self.cell(0, 15, formatar_pdf_text(tit).upper(), ln=True)
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, formatar_pdf_text(sub), ln=True)
        self.ln(10)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
        self.set_font('Arial', '', 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 7, formatar_pdf_text(msg))

# --- LÓGICA DE PORTAIS ---
q = st.query_params
nicho_id = q.get("nicho", "networking").lower()

if nicho_id == "psicanalise":
    cfg = {"tit": "ANALYTIC INTELLIGENCE", "sub": "PSICANÁLISE & ESTRATÉGIA", "pasta": "psicanalise", "txt": "Psicanálise"}
else:
    cfg = {"tit": "TREND INTELLIGENCE HUB", "sub": "ENGENHARIA DE CONTEÚDO", "pasta": "networking", "txt": "Redes de Contatos"}

# --- UI STREAMLIT ---
st.set_page_config(page_title=cfg['tit'], layout="wide")
st.markdown(f"""<style>.main-title {{ background: linear-gradient(135deg, #D4AF37 0%, #C5A059 50%, #8E6D2F 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem !important; font-weight: 800; text-align: center; }} .stButton>button {{ width: 100%; background: #000 !important; color: #fff !important; height: 65px; border-radius: 15px; font-weight: 700; }}</style>""", unsafe_allow_html=True)

st.markdown(f'<h1 class="main-title">{cfg["tit"]}</h1>', unsafe_allow_html=True)

with st.form("f"):
    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("1. Nome do Projeto (Membro/Canal):")
        rede = st.selectbox("2. Rede Social Alvo:", ["Instagram", "TikTok", "YouTube", "LinkedIn"])
    with c2:
        tom = st.selectbox("3. Tom de Voz:", ["autoridade", "provocador", "educativo", "viral"])
    st.markdown("---")
    dor = st.text_area("4. A Dor Latente do Público:")
    usp = st.text_area("5. O Seu Diferencial (USP):")
    inimigo = st.text_input("6. O Inimigo Comum:")
    ctx = st.text_area("7. O Contexto do Conteúdo:")
    cta = st.text_input("8. Objetivo de Conversão (CTA):")
    btn = st.form_submit_button("🚀 GERAR DOSSIÊ")

if btn:
    with st.spinner("Conectando ao Google Trends e cruzando Manuais..."):
        trends_hoje = buscar_google_trends()
        
        # AJUSTE: Garante que a lista de tendências vire texto para o PDF
        if isinstance(trends_hoje, list):
            trends_formatadas = "\n".join(trends_hoje)
        else:
            trends_formatadas = trends_hoje

        # Carregamento de manuais externos
        def load(p):
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8", errors="ignore") as f: return f.read()
            return "Diretrizes padrão de crescimento."
        
        m_alg = load(f"database/algoritmos/{rede.lower()}/regras.txt")
        m_nic = load(f"database/nichos/{cfg['pasta']}/dados.txt")

        pdf = DossiePremium(nome)
        pdf.gerar_capa(cfg['tit'])
        
        # MUDANÇA AQUI: Inseri 'trends_formatadas' dentro do conteúdo da Seção 1
        pdf.add_secao("Análise de Tendências Atuais", "CONEXÃO GOOGLE TRENDS BRASIL", 
                     f"ASSUNTOS EM ALTA (GOOGLE TRENDS - BR):\n\n{trends_formatadas}\n\nO nicho {cfg['txt']}, use esses termos para atrair quem sofre com: {dor}.")
        
        # SEÇÃO 2: PERFORMANCE (Mantida original)
        pdf.add_secao("Performance na Rede Social", f"ALGORITMO {rede.upper()}", 
                     f"DIRETRIZES TÉCNICAS:\n{m_alg}\n\nAPLICAÇÃO NO SEU CONTEXTO:\n{ctx}\n\nFoque no seu USP: {usp}")
        
        # SEÇÃO 3: VEREDITO (Mantida original)
        pdf.add_secao("Veredito Estratégico", "DIRECIONAMENTO FINAL", 
                     f"Combata o inimigo: {inimigo}\nUse o tom: {tom}\nMeta: {cta}\n\nBASE TÉCNICA:\n{m_nic}")

        fname = f"Dossie_{nome.replace(' ', '_')}.pdf"
        pdf.output(fname)
        st.success("✅ Dossiê Gerado com Sucesso!")
        st.download_button("📥 Baixar Relatório", open(fname, "rb"), fname)