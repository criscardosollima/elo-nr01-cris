import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import base64
import urllib.parse
from streamlit_option_menu import option_menu

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
    .a4-paper {{ background: white; width: 210mm; min-height: 297mm; margin: auto; padding: 40px; box-shadow: 0 0 20px rgba(0,0,0,0.1); color: #333; font-family: 'Arial', sans-serif; }}
    .link-area {{ background-color: #f8f9fa; border: 1px dashed #dee2e6; padding: 15px; border-radius: 8px; font-family: monospace; color: #2c3e50; font-weight: bold; word-break: break-all; }}
    
    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 0; width: 100%; }}
        .stApp {{ background-color: white; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS (MOCKUP ATUALIZADO) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": "admin", "cris": "123"}

if 'companies_db' not in st.session_state:
    # Estrutura atualizada com novos campos
    st.session_state.companies_db = [
        {
            "id": "IND01", 
            "razao": "Indústria Têxtil Fabril", 
            "cnpj": "12.345.678/0001-90", 
            "cnae": "13.51-1-00",
            "setor": "Industrial", 
            "risco": 3, 
            "func": 150, 
            "segmentacao": "GHE (Grupo Homogêneo)",
            "resp": "Carlos Silva", 
            "email": "carlos@fabril.com",
            "logo": None, 
            "score": 2.8, 
            "respondidas": 120
        },
        {
            "id": "TEC02", 
            "razao": "TechSolutions S.A.", 
            "cnpj": "98.765.432/0001-10", 
            "cnae": "62.01-5-01",
            "setor": "Tecnologia", 
            "risco": 1, 
            "func": 50, 
            "segmentacao": "Setor/Departamento",
            "resp": "Ana Souza", 
            "email": "ana@tech.com",
            "logo": None, 
            "score": 4.1, 
            "respondidas": 15
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
        st.caption("Colaboradores: Utilizem o link fornecido pelo RH.")

def admin_dashboard():
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; margin-bottom:30px; margin-top:20px;'>{get_logo_html(160)}</div>", unsafe_allow_html=True)
        selected = option_menu(
            menu_title=None,
            options=["Visão Geral", "Gerar Link", "Empresas", "Relatórios", "Configurações"],
            icons=["grid", "link-45deg", "building", "file-text", "gear"],
            default_index=2, # Foco na aba Empresas
            styles={"nav-link-selected": {"background-color": COR_PRIMARIA}}
        )
        st.markdown("---")
        if st.button("Sair", use_container_width=True): logout()

    # --- 1. VISÃO GERAL ---
    if selected == "Visão Geral":
        st.title("Painel Administrativo")
        st.markdown(f"Bem-vinda, **Cris**")
        
        total_empresas = len(st.session_state.companies_db)
        total_respondidas = sum(c['respondidas'] for c in st.session_state.companies_db)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: kpi_card("Empresas", total_empresas, "🏢", "bg-blue")
        with col2: kpi_card("Respondidas", total_respondidas, "✅", "bg-green")
        with col3: kpi_card("Pendentes", 67, "⏳", "bg-orange")
        with col4: kpi_card("Alertas", "3", "🚨", "bg-red")

        st.markdown("<br>", unsafe_allow_html=True)
        c_chart1, c_chart2 = st.columns([1, 1.5])
        with c_chart1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Distribuição")
            df = pd.DataFrame(st.session_state.companies_db)
            fig_pie = px.pie(df, names='setor', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 2. GERAR LINK ---
    elif selected == "Gerar Link":
        st.title("Gerar Link")
        with st.container():
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
            empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_nome)
            link_final = f"{st.session_state.base_url}/?cod={empresa['id']}"
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"<div class='link-area'>{link_final}</div>", unsafe_allow_html=True)
                st.markdown(f"**Adesão:** {empresa['respondidas']}/{empresa['func']}")
                prog = empresa['respondidas']/empresa['func'] if empresa['func'] > 0 else 0
                st.markdown(f"""<div style="background:#eee;height:8px;border-radius:4px;"><div style="width:{prog*100}%;background:{COR_SECUNDARIA};height:100%;border-radius:4px;"></div></div>""", unsafe_allow_html=True)
            with c2:
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(link_final)}"
                st.image(qr_url, width=150)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 3. EMPRESAS (CADASTRO COMPLETO) ---
    elif selected == "Empresas":
        st.title("Gestão de Empresas")
        
        tab1, tab2 = st.tabs(["Monitoramento", "Novo Cadastro"])
        
        with tab1:
            # Exibe tabela resumida, mas com dados relevantes
            df_view = pd.DataFrame(st.session_state.companies_db)
            # Renomear colunas para visualização
            df_view = df_view[['razao', 'cnpj', 'risco', 'segmentacao', 'func', 'respondidas']]
            df_view.columns = ['Empresa', 'CNPJ', 'Risco', 'Tipo Segmentação', 'Vidas', 'Resp.']
            st.dataframe(df_view, use_container_width=True)
            
        with tab2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Cadastro Técnico da Empresa")
            st.caption("Preencha os dados completos para garantir a conformidade da NR-01.")
            
            with st.form("add_comp"):
                st.markdown("##### 1. Dados Legais")
                c1, c2, c3 = st.columns(3)
                razao = c1.text_input("Razão Social")
                cnpj = c2.text_input("CNPJ")
                cnae = c3.text_input("CNAE Principal", placeholder="Ex: 62.01-5-01")
                
                st.markdown("##### 2. Parâmetros de SST & RH")
                c4, c5, c6 = st.columns(3)
                risco = c4.selectbox("Grau de Risco (NR-04)", [1, 2, 3, 4])
                func = c5.number_input("Quantidade de Colaboradores (Vidas)", min_value=1)
                segmentacao = c6.selectbox("Segmentação da Análise", ["Setor/Departamento", "GHE (Grupo Homogêneo)", "GES (Grupo Similar)", "Ambiente Físico"])
                
                st.markdown("##### 3. Acesso & Responsável")
                c7, c8, c9 = st.columns(3)
                cod = c7.text_input("Código ID (Acesso)", placeholder="Ex: CLI-01")
                resp = c8.text_input("Responsável Técnico/RH")
                email_resp = c9.text_input("E-mail Contato")
                
                logo_file = st.file_uploader("Logo da Empresa (Para Relatório)", type=['png', 'jpg'])
                
                if st.form_submit_button("💾 Salvar Cadastro Completo"):
                    if razao and cod:
                        new_c = {
                            "id": cod, 
                            "razao": razao, 
                            "cnpj": cnpj, 
                            "cnae": cnae,
                            "setor": "Geral", # Padrão, depois ajusta na análise
                            "risco": risco, 
                            "func": func, 
                            "segmentacao": segmentacao,
                            "resp": resp,
                            "email": email_resp,
                            "logo": logo_file, 
                            "score": 0, 
                            "respondidas": 0
                        }
                        st.session_state.companies_db.append(new_c)
                        st.success(f"Empresa '{razao}' cadastrada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha pelo menos a Razão Social e o Código ID.")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 4. RELATÓRIOS ---
    elif selected == "Relatórios":
        st.title("Relatórios e Laudos")
        empresa_sel = st.selectbox("Cliente", [c['razao'] for c in st.session_state.companies_db])
        empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_sel)
        
        # Simulação de dados para visualização
        fator_critico = "Demandas" if empresa['score'] < 3 else "Controle"
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Diagnóstico")
            st.info(f"Score: **{empresa['score']}** | Segmentação: **{empresa.get('segmentacao', 'Setor')}**")
            st.markdown(f"**CNAE:** {empresa.get('cnae', '-')} | **Risco:** {empresa['risco']}")
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Plano de Ação")
            acoes_sel = []
            for i, a in enumerate(["Revisão Job Description", "Treinamento Liderança", "Pausas"]):
                if st.checkbox(a, key=f"a_{i}", value=True): acoes_sel.append(a)
            
            st.markdown("**Cronograma:**")
            d1, d2 = st.columns(2)
            d_ini = d1.date_input("Início")
            d_fim = d2.date_input("Fim")
            st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🖨️ Gerar PDF (A4)", type="primary"):
            st.markdown("---")
            logo_html = get_logo_html(120)
            if empresa.get('logo'):
                b64 = image_to_base64(empresa.get('logo'))
                if b64: logo_html = f"<img src='data:image/png;base64,{b64}' width='120'>"
            
            plat_name = st.session_state.platform_config['name']
            consultancy = st.session_state.platform_config['consultancy']
            
            html_acoes = "".join([f"<li>{a}</li>" for a in acoes_sel])

            html_content = f"""
            <div class="a4-paper">
                <div style="display:flex; justify-content:space-between; border-bottom: 2px solid {COR_PRIMARIA}; padding-bottom:20px;">
                    <div>{logo_html}</div>
                    <div style="text-align:right;">
                        <h2 style="color:{COR_PRIMARIA}; margin:0;">LAUDO TÉCNICO</h2>
                        <span style="color:#666;">{plat_name}</span>
                    </div>
                </div>
                <br>
                <div style="background:#f8f9fa; padding:15px; border-radius:5px;">
                    <strong>Empresa:</strong> {empresa['razao']}<br>
                    <strong>CNPJ:</strong> {empresa['cnpj']} | <strong>CNAE:</strong> {empresa.get('cnae','-')}<br>
                    <strong>Grau de Risco:</strong> {empresa['risco']} | <strong>Segmentação:</strong> {empresa.get('segmentacao','-')}
                </div>
                <br>
                <h4>Plano de Ação ({d_ini.strftime('%d/%m')} a {d_fim.strftime('%d/%m')})</h4>
                <ul>{html_acoes}</ul>
                
                <div style="margin-top:100px; text-align:center; border-top:1px solid #ccc; padding-top:10px;">
                    <strong>{consultancy}</strong><br>Responsável Técnico
                </div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)

    # --- 5. CONFIGURAÇÕES ---
    elif selected == "Configurações":
        st.title("Configurações")
        
        tab_brand, tab_users, tab_sys = st.tabs(["🎨 Personalização", "🔐 Acessos", "⚙️ Sistema"])
        
        with tab_brand:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            c_name, c_cons = st.columns(2)
            new_name = c_name.text_input("Nome Plataforma", value=st.session_state.platform_config['name'])
            new_cons = c_cons.text_input("Nome Consultoria", value=st.session_state.platform_config['consultancy'])
            
            new_logo = st.file_uploader("Logo Plataforma", type=['png', 'jpg'])
            if st.button("Salvar Identidade"):
                st.session_state.platform_config['name'] = new_name
                st.session_state.platform_config['consultancy'] = new_cons
                if new_logo: st.session_state.platform_config['logo_b64'] = image_to_base64(new_logo)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_users:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Gestão de Usuários")
            users_df = pd.DataFrame(list(st.session_state.users_db.items()), columns=['Login', 'Senha'])
            users_df['Senha'] = '******'
            st.dataframe(users_df, use_container_width=True)
            
            c_u1, c_u2 = st.columns(2)
            new_u = c_u1.text_input("Novo Usuário")
            new_p = c_u2.text_input("Nova Senha", type="password")
            if st.button("Adicionar/Alterar"):
                if new_u and new_p:
                    st.session_state.users_db[new_u] = new_p
                    st.success("Salvo!")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_sys:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            new_url = st.text_input("URL Base", value=st.session_state.base_url)
            if st.button("Atualizar URL"):
                st.session_state.base_url = new_url
                st.success("OK")
            st.markdown("</div>", unsafe_allow_html=True)

# --- 6. TELA PESQUISA ---
def survey_screen():
    query_params = st.query_params
    cod_url = query_params.get("cod", None)
    
    if cod_url and not st.session_state.get('current_company'):
        company = next((c for c in st.session_state.companies_db if c['id'] == cod_url), None)
        if company: st.session_state.current_company = company
    
    if 'current_company' not in st.session_state:
        st.error("Link inválido.")
        if st.button("Ir para Login"): st.session_state.logged_in = False; st.rerun()
        return

    comp = st.session_state.current_company
    logo_show = get_logo_html(150)
    if comp.get('logo'):
        b64 = image_to_base64(comp.get('logo'))
        if b64: logo_show = f"<img src='data:image/png;base64,{b64}' width='150'>"
    
    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'>{logo_show}</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center'>Avaliação - {comp['razao']}</h3>", unsafe_allow_html=True)
    
    with st.form("survey"):
        st.write("**1. Tenho prazos impossíveis?**")
        st.select_slider("", ["Nunca", "Sempre"], key="q1")
        if st.form_submit_button("Enviar"):
            for c in st.session_state.companies_db:
                if c['id'] == comp['id']: c['respondidas'] += 1
            st.success("Enviado!")
            time.sleep(2)
            del st.session_state['current_company']
            st.rerun()

# --- 7. ROTEADOR ---
if not st.session_state.logged_in:
    if "cod" in st.query_params: survey_screen()
    else: login_screen()
else:
    if st.session_state.user_role == 'admin': admin_dashboard()
    else: survey_screen()
