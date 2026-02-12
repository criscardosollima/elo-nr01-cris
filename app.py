import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import base64
import urllib.parse
from streamlit_option_menu import option_menu
import textwrap

# --- 1. GESTÃO DE ESTADO E CONFIGURAÇÃO INICIAL ---
if 'platform_config' not in st.session_state:
    st.session_state.platform_config = {
        "name": "Elo NR-01",
        "consultancy": "Pessin Gestão",
        "logo_b64": None
    }

st.set_page_config(
    page_title=f"{st.session_state.platform_config['name']} | Sistema",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

COR_PRIMARIA = "#2c3e50"
COR_SECUNDARIA = "#1abc9c"
COR_FUNDO = "#f4f6f9"

# --- 2. CSS PROFISSIONAL ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    .stApp {{ background-color: {COR_FUNDO}; font-family: 'Inter', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: #ffffff; border-right: 1px solid #e0e0e0; }}
    
    /* Cards KPI */
    .kpi-card {{
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;
        margin-bottom: 15px; display: flex; flex-direction: column; justify-content: space-between; height: 140px;
    }}
    .kpi-top {{ display: flex; justify-content: space-between; align-items: start; }}
    .kpi-icon-box {{ width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
    .kpi-title {{ font-size: 13px; color: #7f8c8d; font-weight: 600; margin-top: 10px; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; color: {COR_PRIMARIA}; margin-top: 5px; }}
    
    /* Cores Ícones */
    .bg-blue {{ background-color: #e3f2fd; color: #1976d2; }}
    .bg-green {{ background-color: #e8f5e9; color: #388e3c; }}
    .bg-orange {{ background-color: #fff3e0; color: #f57c00; }}
    .bg-purple {{ background-color: #f3e5f5; color: #7b1fa2; }}
    .bg-red {{ background-color: #ffebee; color: #d32f2f; }}

    /* Containers */
    .chart-container {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; height: 100%; }}
    
    /* Relatório A4 */
    .a4-paper {{ 
        background: white; width: 210mm; min-height: 297mm; margin: auto; padding: 40px; 
        box-shadow: 0 0 20px rgba(0,0,0,0.1); color: #333; font-family: 'Arial', sans-serif; 
    }}
    .link-area {{ background-color: #f8f9fa; border: 1px dashed #dee2e6; padding: 15px; border-radius: 8px; font-family: monospace; color: #2c3e50; font-weight: bold; word-break: break-all; }}
    
    /* Tabelas do Relatório */
    .hse-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 0.85em; }}
    .hse-table th {{ background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left; font-weight: bold; }}
    .hse-table td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    
    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 0; width: 100%; }}
        .stApp {{ background-color: white; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS (MOCKUP) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": "admin", "cris": "123"}

if 'companies_db' not in st.session_state:
    st.session_state.companies_db = [
        {
            "id": "IND01", "razao": "Indústria Têxtil Fabril", "cnpj": "12.345.678/0001-90", 
            "cnae": "13.51-1-00", "setor": "Industrial", "risco": 3, "func": 150, 
            "segmentacao": "GHE (Grupo Homogêneo)", "resp": "Cristiane C. Lima", 
            "email": "cris@pessin.com.br", "logo": None, "score": 2.8, "respondidas": 120
        },
    ]

if 'base_url' not in st.session_state: st.session_state.base_url = "http://localhost:8501" 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- 4. FUNÇÕES AUXILIARES ---
def get_logo_html(width=180):
    if st.session_state.platform_config['logo_b64']:
        return f'<img src="data:image/png;base64,{st.session_state.platform_config["logo_b64"]}" width="{width}">'
    
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 100" width="{width}">
      <style>
        .t1 {{ font-family: sans-serif; font-weight: bold; font-size: 45px; fill: {COR_PRIMARIA}; }}
        .t2 {{ font-family: sans-serif; font-weight: 300; font-size: 45px; fill: {COR_SECUNDARIA}; }}
      </style>
      <path d="M20,35 L50,35 A15,15 0 0 1 50,65 L20,65 A15,15 0 0 1 20,35 Z" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="8" />
      <path d="M45,35 L75,35 A15,15 0 0 1 75,65 L45,65 A15,15 0 0 1 45,35 Z" fill="none" stroke="{COR_PRIMARIA}" stroke-width="8" />
      <text x="100" y="68" class="t1">Elo</text>
      <text x="180" y="68" class="t2">NR-01</text>
    </svg>
    """
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}">'

def image_to_base64(uploaded_file):
    try:
        if uploaded_file: return base64.b64encode(uploaded_file.getvalue()).decode()
    except: pass
    return None

def logout():
    st.session_state.logged_in = False
    st.rerun()

def kpi_card(title, value, icon, color_class):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-top"><div class="kpi-icon-box {color_class}">{icon}</div></div>
        <div><div class="kpi-value">{value}</div><div class="kpi-title">{title}</div></div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. TELAS DO SISTEMA ---

def login_screen():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center'>{get_logo_html(250)}</div>", unsafe_allow_html=True)
        plat_name = st.session_state.platform_config['name']
        st.markdown(f"<h3 style='text-align:center; color:#555;'>{plat_name}</h3>", unsafe_allow_html=True)
        
        with st.form("login"):
            user = st.text_input("Usuário")
            pwd = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                if user in st.session_state.users_db and st.session_state.users_db[user] == pwd:
                    st.session_state.logged_in = True
                    st.session_state.user_role = 'admin'
                    st.rerun()
                else:
                    st.error("Dados incorretos.")

def admin_dashboard():
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; margin-bottom:30px; margin-top:20px;'>{get_logo_html(160)}</div>", unsafe_allow_html=True)
        selected = option_menu(
            menu_title=None,
            options=["Visão Geral", "Gerar Link", "Empresas", "Relatórios", "Configurações"],
            icons=["grid", "link-45deg", "building", "file-text", "gear"],
            default_index=3,
            styles={"nav-link-selected": {"background-color": COR_PRIMARIA}}
        )
        st.markdown("---")
        if st.button("Sair", use_container_width=True): logout()

    # --- 1. VISÃO GERAL ---
    if selected == "Visão Geral":
        st.title("Painel Administrativo")
        total_empresas = len(st.session_state.companies_db)
        total_respondidas = sum(c['respondidas'] for c in st.session_state.companies_db)
        col1, col2, col3, col4 = st.columns(4)
        with col1: kpi_card("Empresas", total_empresas, "🏢", "bg-blue")
        with col2: kpi_card("Respondidas", total_respondidas, "✅", "bg-green")
        with col3: kpi_card("Pendentes", 67, "⏳", "bg-orange")
        with col4: kpi_card("Alertas", "3", "🚨", "bg-red")
        df = pd.DataFrame(st.session_state.companies_db)
        fig_pie = px.pie(df, names='setor', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 2. GERAR LINK ---
    elif selected == "Gerar Link":
        st.title("Gerar Link")
        empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
        empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_nome)
        link_final = f"{st.session_state.base_url}/?cod={empresa['id']}"
        st.markdown(f"<div class='link-area'>{link_final}</div>", unsafe_allow_html=True)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(link_final)}"
        st.image(qr_url, width=150)

    # --- 3. EMPRESAS ---
    elif selected == "Empresas":
        st.title("Gestão de Empresas")
        tab1, tab2 = st.tabs(["Monitoramento", "Novo Cadastro"])
        with tab1:
            df_view = pd.DataFrame(st.session_state.companies_db)
            st.dataframe(df_view[['razao', 'cnpj', 'risco', 'segmentacao', 'func', 'respondidas']], use_container_width=True)
        with tab2:
            with st.form("add_comp"):
                c1, c2, c3 = st.columns(3)
                razao = c1.text_input("Razão Social")
                cnpj = c2.text_input("CNPJ")
                cnae = c3.text_input("CNAE Principal")
                risco = st.selectbox("Grau de Risco", [1, 2, 3, 4])
                func = st.number_input("Nº Vidas", min_value=1)
                segmentacao = st.selectbox("Segmentação", ["Setor", "GHE", "GES", "Ambiente"])
                cod = st.text_input("Código ID")
                resp = st.text_input("Responsável")
                logo_file = st.file_uploader("Logo Empresa", type=['png', 'jpg'])
                if st.form_submit_button("Salvar"):
                    new_c = {"id": cod, "razao": razao, "cnpj": cnpj, "cnae": cnae, "setor": "Geral", "risco": risco, "func": func, "segmentacao": segmentacao, "resp": resp, "logo": logo_file, "score": 0, "respondidas": 0}
                    st.session_state.companies_db.append(new_c)
                    st.rerun()

    # --- 4. RELATÓRIOS (MODELO HSE-IT EXCLUSIVO) ---
    elif selected == "Relatórios":
        st.title("Relatórios de Avaliação de Riscos Psicossociais (HSE-IT)")
        
        empresa_sel = st.selectbox("Selecione o Cliente", [c['razao'] for c in st.session_state.companies_db])
        empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_sel)
        
        # --- CAMPOS DE EDIÇÃO PARA O CONSULTOR ---
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("📝 Parecer e Análise do Especialista")
        
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            pontos_criticos = st.text_area("Pontos Críticos Identificados:", "Ex: 70% dos funcionários relatam 'raramente' receber suporte da chefia imediata.")
            pontos_fortes = st.text_area("Pontos Fortes Identificados:", "Ex: Bom relacionamento entre pares e clareza no papel desempenhado.")
        with col_ed2:
            analise_interpretativa = st.text_area("Análise dos Riscos (Interpretação):", 
                "Observou-se uma alta demanda de trabalho, indicando que os funcionários frequentemente 'nunca' têm tempo para pausas adequadas. "
                "Identificados indícios de conflitos interpessoais e percepção de assédio em setores de alta pressão.")

        st.markdown("---")
        st.subheader("🛠️ Construção do Plano de Ação")
        
        # Gerenciamento de ações dinâmicas para o laudo
        if 'actions_list' not in st.session_state:
            st.session_state.actions_list = [
                {"acao": "Treinamento de liderança focada em suporte", "area": "Suporte/Gestor", "resp": "RH", "prazo": "30 dias"},
                {"acao": "Reestruturação das metas/jornada", "area": "Demanda/Papel", "resp": "Gestão/SST", "prazo": "60 dias"}
            ]
        
        with st.expander("Gerenciar Ações do Plano"):
            c_a1, c_a2, c_a3, c_a4 = st.columns([3, 2, 1, 1])
            new_ac = c_a1.text_input("Ação Recomendada")
            new_ar = c_a2.text_input("Área HSE")
            new_re = c_a3.text_input("Resp.")
            new_pr = c_a4.text_input("Prazo")
            if st.button("➕ Adicionar Ação"):
                st.session_state.actions_list.append({"acao": new_ac, "area": new_ar, "resp": new_re, "prazo": new_pr})
                st.rerun()
            if st.button("🗑️ Limpar Lista"):
                st.session_state.actions_list = []
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        
        # --- G
