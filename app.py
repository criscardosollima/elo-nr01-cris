import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
import base64
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA E IDENTIDADE VISUAL ---
NOME_PLATAFORMA = "Elo NR-01"
COR_PRIMARIA = "#2980b9" # Azul Elo
COR_SECUNDARIA = "#2c3e50" # Azul Corporativo
COR_FUNDO = "#f4f6f7"

st.set_page_config(
    page_title=f"{NOME_PLATAFORMA} | by Pessin",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO CSS (Design System) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');
    
    .main {{background-color: {COR_FUNDO}; font-family: 'Nunito', sans-serif;}}
    
    /* Tipografia */
    h1, h2, h3 {{color: {COR_SECUNDARIA}; font-family: 'Nunito', sans-serif;}}
    .destaque {{color: {COR_PRIMARIA}; font-weight: bold;}}
    
    /* Botões */
    .stButton>button {{
        width: 100%; border-radius: 8px; height: 3em; font-weight: bold;
        background-color: {COR_SECUNDARIA}; color: white; border: none;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: {COR_PRIMARIA}; transform: translateY(-2px);
    }}
    
    /* Cards do Dashboard */
    .metric-card {{
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;
        border-bottom: 4px solid {COR_PRIMARIA};
    }}
    .metric-value {{font-size: 2em; font-weight: 800; color: {COR_SECUNDARIA};}}
    .metric-label {{color: #7f8c8d; font-size: 0.85em; text-transform: uppercase; letter-spacing: 1px;}}
    
    /* Área de Impressão (Relatório) */
    @media print {{
        .stSidebar, .stButton, .no-print {{display: none !important;}}
        .report-header {{text-align: center; margin-bottom: 30px;}}
        .signature-line {{border-top: 1px solid #000; width: 80%; margin: 60px auto 10px auto;}}
        .citation-box {{border: 1px solid #ccc; padding: 10px; font-style: italic; font-size: 0.9em; page-break-inside: avoid;}}
        .action-plan {{border-left: 5px solid {COR_PRIMARIA}; padding-left: 15px; margin-top: 20px; page-break-inside: avoid;}}
    }}
    
    /* Elementos Visuais */
    .link-box {{
        background-color: white; border: 2px dashed {COR_PRIMARIA};
        padding: 15px; border-radius: 8px; text-align: center;
        font-family: monospace; color: {COR_SECUNDARIA}; font-weight: bold;
    }}
    .nr01-citation {{
        background-color: #e8f8f5; border-left: 5px solid {COR_PRIMARIA};
        padding: 15px; margin-bottom: 20px; border-radius: 5px;
        font-size: 0.95em; color: {COR_SECUNDARIA};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- DADOS MOCKADOS (SIMULAÇÃO DE BANCO DE DADOS) ---
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'mock_companies' not in st.session_state:
    st.session_state.mock_companies = [
        {"id": "IND01", "Nome": "Indústria Têxtil A", "Setor": "Industrial", "Risco": 3, "Func": 150, "Logo": None, "Resp": "Carlos Silva", "Score": 2.8, "FatorCritico": "Demandas"},
        {"id": "TECH02", "Nome": "Tech Solutions", "Setor": "Serviços", "Risco": 1, "Func": 45, "Logo": None, "Resp": "Ana Souza", "Score": 4.2, "FatorCritico": "Controle"},
    ]

# --- FUNÇÕES DE LÓGICA DE NEGÓCIO ---

def show_logo_svg(width=300):
    """Renderiza a logo vetorial Elo NR-01"""
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120" width="{width}">
      <style>
        .texto-elo {{ font-family: 'Helvetica', sans-serif; font-weight: bold; font-size: 60px; fill: {COR_SECUNDARIA}; }}
        .texto-nr {{ font-family: 'Helvetica', sans-serif; font-weight: normal; font-size: 60px; fill: {COR_PRIMARIA}; }}
        .icone {{ fill: none; stroke: {COR_PRIMARIA}; stroke-width: 12; stroke-linecap: round; }}
      </style>
      <g transform="translate(30, 35)">
        <path class="icone" d="M15,25 L45,25 A15,15 0 0 1 45,55 L15,55 A15,15 0 0 1 15,25 Z" />
        <path class="icone" d="M40,25 L70,25 A15,15 0 0 1 70,55 L40,55 A15,15 0 0 1 40,25 Z" transform="translate(25, 0)" />
      </g>
      <text x="140" y="80" class="texto-elo">Elo</text>
      <text x="245" y="80" class="texto-nr">NR-01</text>
    </svg>
    """
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    st.markdown(f'<div style="display:flex;justify-content:center;"><img src="data:image/svg+xml;base64,{b64}"></div>', unsafe_allow_html=True)

def get_hse_actions(fator):
    """Retorna sugestões técnicas baseadas no HSE Workbook"""
    acoes = {
        "Demandas": [
            "Revisão da distribuição de carga de trabalho entre a equipe.",
            "Implementação de matriz de priorização de tarefas.",
            "Renegociação de prazos irrealistas com clientes internos."
        ],
        "Controle": [
            "Aumentar autonomia sobre o ritmo de trabalho.",
            "Permitir micro-decisões sobre a ordem das tarefas.",
            "Criar fóruns de participação para melhorias de processo."
        ],
        "Apoio Gestão": [
            "Treinamento de liderança em escuta ativa e feedback.",
            "Estabelecer reuniões 1:1 focadas em desenvolvimento.",
            "Clarificar canais de suporte técnico e emocional."
        ],
        "Relacionamentos": [
            "Reforço das políticas de combate ao assédio e discriminação.",
            "Workshop de Comunicação Não-Violenta (CNV).",
            "Mediação de conflitos interpessoais identificados."
        ]
    }
    return acoes.get(fator, ["Realizar diagnóstico aprofundado."])

def navbar():
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("🏠 Home"):
            st.session_state.page = 'login'
            st.rerun()

# --- TELA 1: LOGIN ---
def show_login():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        show_logo_svg(350)
        st.markdown("<p style='text-align: center; color: #7f8c8d;'>Gestão Inteligente de Riscos Psicossociais</p><br>", unsafe_allow_html=True)
        
        tab_colab, tab_admin = st.tabs(["Sou Colaborador", "Área do Cliente / RH"])
        
        with tab_colab:
            st.info("Digite o código recebido para iniciar sua avaliação anônima.")
            cod = st.text_input("Código da Empresa", placeholder="Ex: PESSIN25", key="login_cod")
            if st.button("Iniciar Avaliação", type="primary"):
                company = next((c for c in st.session_state.mock_companies if c['id'] == cod), None)
                if company:
                    st.session_state.current_company = company
                    st.session_state.page = 'survey'
                    st.rerun()
                else:
                    st.error("Código inválido.")
        
        with tab_admin:
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            if st.button("Entrar no Painel"):
                if email == "admin" and senha == "admin":
                    st.session_state.page = 'admin'
                    st.rerun()
                else:
                    st.error("Login incorreto. Tente admin / admin")

# --- TELA 2: DASHBOARD ADMIN (Consultor Pessin) ---
def show_admin():
    navbar()
    col_h1, col_h2 = st.columns([1, 15])
    with col_h1: st.markdown("## 📊")
    with col_h2: st.markdown("## Painel de Controle Elo NR-01")
    
    tab1, tab2, tab3 = st.tabs(["Visão Geral", "Cadastrar & Divulgar", "Relatórios & Planos de Ação"])
    
    # 1. VISÃO GERAL
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.mock_companies)}</div><div class='metric-label'>Empresas</div></div>", unsafe_allow_html=True)
        c2.markdown("<div class='metric-card'><div class='metric-value'>342</div><div class='metric-label'>Vidas Impactadas</div></div>", unsafe_allow_html=True)
        c3.markdown("<div class='metric-card'><div class='metric-value'>12</div><div class='metric-label'>Laudos Gerados</div></div>", unsafe_allow_html=True)
        c4.markdown("<div class='metric-card'><div class='metric-value'>98%</div><div class='metric-label'>Conformidade</div></div>", unsafe_allow_html=True)
        
        st.markdown("### Empresas Ativas")
        st.dataframe(pd.DataFrame(st.session_state.mock_companies).drop(columns=['Logo'], errors='ignore'), use_container_width=True)

    # 2. CADASTRO & DIVULGAÇÃO
    with tab2:
        c_form, c_link = st.columns([1.5, 1])
        with c_form:
            st.subheader("Cadastrar Nova Empresa")
            with st.form("new_company"):
                nome = st.text_input("Razão Social")
                c_a, c_b = st.columns(2)
                with c_a:
                    cod_id = st.text_input("Código de Acesso (ID)", placeholder="Ex: CLIENTE01")
                    resp = st.text_input("Responsável Legal")
                with c_b:
                    risco = st.selectbox("Grau de Risco (NR-04)", [1, 2, 3, 4])
                    logo = st.file_uploader("Logo da Empresa (Opcional)", type=['png', 'jpg'])
                
                if st.form_submit_button("💾 Salvar Cadastro"):
                    new_c = {"id": cod_id, "Nome": nome, "Setor": "Novo", "Risco": risco, "Func": 0, "Logo": logo, "Resp": resp, "Score": 0, "FatorCritico": "-"}
                    st.session_state.mock_companies.append(new_c)
                    st.session_state.last_created = new_c
                    st.success("Cadastro realizado!")
                    st.rerun()
        
        with c_link:
            st.subheader("Kit de Divulgação")
            if 'last_created' in st.session_state:
                comp = st.session_state.last_created
                link = f"https://elo-nr01.app/?cod={comp['id']}"
                
                st.markdown(f"**Cliente:** {comp['Nome']}")
                st.markdown(f"<div class='link-box'>{link}</div>", unsafe_allow_html=True)
                
                msg_zap = f"""Olá time {comp['Nome']}! 🌟
A {NOME_PLATAFORMA} chegou para cuidarmos da nossa saúde mental.
Participe da avaliação de riscos psicossociais (NR-01). É anônimo e seguro.
Link: {link}"""
                st.text_area("Texto para WhatsApp:", value=msg_zap, height=150)
                
                # QR Code Fake
                qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(link)}"
                st.image(qr, caption="QR Code para Murais")
            else:
                st.info("Cadastre uma empresa ao lado para gerar o kit.")

    # 3. RELATÓRIOS E PLANOS DE AÇÃO (A "Cereja do Bolo")
    with tab3:
        st.subheader("Gerador de Laudo Técnico")
        empresa_nome = st.selectbox("Selecione o Cliente", [c['Nome'] for c in st.session_state.mock_companies])
        empresa = next(c for c in st.session_state.mock_companies if c['Nome'] == empresa_nome)
        
        # Simulando análise de dados
        fator_critico = empresa.get('Score', 3) < 3
        nome_fator = empresa.get('FatorCritico', 'Demandas')
        
        col_res, col_plan = st.columns([1, 1])
        
        with col_res:
            st.markdown("#### Diagnóstico Automático")
            st.metric("Score Geral", f"{empresa.get('Score', 0)}/5.0", delta="-0.5" if fator_critico else "0.2")
            if fator_critico:
                st.error(f"⚠️ Atenção Prioritária: **{nome_fator}**")
            else:
                st.success("✅ Indicadores em Conformidade")

        with col_plan:
            st.markdown("#### Construtor de Plano de Ação")
            st.caption("Selecione as ações para incluir no relatório final:")
            
            # Carrega sugestões HSE
            sugestoes = get_hse_actions(nome_fator)
            acoes_selecionadas = []
            
            for i, acao in enumerate(sugestoes):
                if st.checkbox(acao, value=True, key=f"act_{i}"):
                    acoes_selecionadas.append(acao)
            
            custom_action = st.text_input("Adicionar Ação Personalizada (+):")
            if custom_action:
                acoes_selecionadas.append(custom_action)

        if st.button("📄 Gerar Relatório PDF (Visualização)"):
            st.markdown("---")
            # --- ÁREA IMPRIMÍVEL ---
            with st.container():
                c_head1, c_head2 = st.columns([1, 4])
                with c_head1:
                    # Tenta mostrar logo do cliente, senão mostra SVG Elo
                    if empresa['Logo']: st.image(empresa['Logo'], width=100)
                    else: show_logo_svg(150)
                with c_head2:
                    st.markdown(f"### LAUDO TÉCNICO DE RISCOS PSICOSSOCIAIS")
                    st.markdown(f"**Empresa:** {empresa['Nome']} | **Data:** {datetime.now().strftime('%d/%m/%Y')}")

                st.markdown("#### 1. Fundamentação Legal")
                st.markdown("""
                <div class='citation-box'>
                "1.5.3.1.1 O gerenciamento de riscos ocupacionais deve constituir um Programa de Gerenciamento de Riscos (PGR) 
                e deve incluir [...] os fatores ergonômicos e psicossociais." (NR-01)
                </div>""", unsafe_allow_html=True)
                
                st.markdown(f"#### 2. Análise do Fator Crítico: {nome_fator}")
                st.write(f"A avaliação identificou que o fator '{nome_fator}' apresenta riscos à saúde dos colaboradores, exigindo intervenção imediata conforme metodologia HSE.")

                st.markdown("#### 3. Plano de Ação Recomendado")
                st.markdown("<div class='action-plan'>", unsafe_allow_html=True)
                for acao in acoes_selecionadas:
                    st.markdown(f"- {acao}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                s1, s2 = st.columns(2)
                with s1:
                    st.markdown("<div class='signature-line'></div>", unsafe_allow_html=True)
                    st.markdown(f"<center><b>{empresa['Resp']}</b><br>Responsável Legal</center>", unsafe_allow_html=True)
                with s2:
                    st.markdown("<div class='signature-line'></div>", unsafe_allow_html=True)
                    st.markdown(f"<center><b>Cristiane Cardoso Lima</b><br>Consultora Responsável (Pessin)</center>", unsafe_allow_html=True)
            
            st.info("Pressione Ctrl+P para salvar como PDF.")

# --- TELA 3: FORMULÁRIO COLABORADOR ---
def show_survey():
    comp = st.session_state.current_company
    
    # Header White Label
    c_back, c_logo = st.columns([6, 1])
    with c_back:
        if st.button("← Sair"): 
            st.session_state.page = 'login'
            st.session_state.current_company = None
            st.rerun()
    with c_logo:
        if comp['Logo']: st.image(comp['Logo'], width=100)
    
    st.markdown(f"### Avaliação de Clima | {comp['Nome']}")
    
    # Citação NR-01 para Colaborador
    st.markdown("""
    <div class='nr01-citation'>
    <b>🛡️ Segurança Legal (NR-01):</b> Esta pesquisa atende à norma regulamentadora que exige o cuidado com a saúde mental no trabalho.
    Seus dados são criptografados e confidenciais.
    </div>""", unsafe_allow_html=True)
    
    # Perguntas com Tooltips
    questions = [
        {"q": "Tenho prazos impossíveis?", "cat": "Demandas", "tip": "Ex: Tarefas chegam às 17h para entregar às 18h."},
        {"q": "Tenho autonomia no meu trabalho?", "cat": "Controle", "tip": "Ex: Você pode decidir a ordem das suas tarefas."},
        {"q": "Recebo apoio do meu gestor?", "cat": "Apoio", "tip": "Ex: Seu chefe ajuda quando você tem dificuldades?"}
    ]
    
    with st.form("survey_form"):
        for q in questions:
            st.markdown(f"**{q['q']}**")
            st.select_slider("Frequência", options=["Nunca", "Às vezes", "Sempre"], key=q['q'], help=q['tip'])
            st.markdown("---")
        
        if st.form_submit_button("Enviar Avaliação"):
            st.balloons()
            st.success("Respostas enviadas com sucesso! Obrigado por fortalecer o Elo.")
            time.sleep(3)
            st.session_state.page = 'login'
            st.rerun()

# --- ROTEADOR ---
if st.session_state.page == 'login': show_login()
elif st.session_state.page == 'admin': show_admin()
elif st.session_state.page == 'survey': show_survey()