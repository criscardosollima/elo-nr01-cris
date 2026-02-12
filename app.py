import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import base64
import urllib.parse
from streamlit_option_menu import option_menu
import textwrap

# --- 1. CONFIGURAÇÃO INICIAL ---
if 'platform_config' not in st.session_state:
    st.session_state.platform_config = {
        "name": "Elo NR-01",
        "consultancy": "Pessin Gestão",
        "logo_b64": None # Logo da Consultoria (Whitelabel)
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
COR_RISCO_ALTO = "#ef5350"
COR_RISCO_MEDIO = "#ffa726"
COR_RISCO_BAIXO = "#66bb6a"

# --- 2. CSS OTIMIZADO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {{ background-color: {COR_FUNDO}; font-family: 'Inter', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: #ffffff; border-right: 1px solid #e0e0e0; }}
    
    /* Cards do Dashboard */
    .kpi-card {{
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04); border: 1px solid #f0f0f0;
        margin-bottom: 15px; display: flex; flex-direction: column; justify-content: space-between; height: 140px;
    }}
    .kpi-icon-box {{ width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
    .kpi-title {{ font-size: 13px; color: #7f8c8d; font-weight: 600; margin-top: 10px; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; color: {COR_PRIMARIA}; margin-top: 5px; }}
    
    /* Cores Ícones */
    .bg-blue {{ background-color: #e3f2fd; color: #1976d2; }}
    .bg-green {{ background-color: #e8f5e9; color: #388e3c; }}
    .bg-orange {{ background-color: #fff3e0; color: #f57c00; }}
    .bg-red {{ background-color: #ffebee; color: #d32f2f; }}

    /* Containers de Gráficos */
    .chart-container {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; height: 100%; }}

    /* Radio Buttons */
    div[role="radiogroup"] > label > div:first-of-type {{
        background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 8px 12px;
    }}
    div[role="radiogroup"] > label > div:first-of-type:hover {{
        border-color: {COR_SECUNDARIA}; background-color: #e0f2f1;
    }}
    
    /* Relatório A4 Moderno */
    .a4-paper {{ 
        background: white; width: 210mm; min-height: 297mm; margin: auto; padding: 40px; 
        box-shadow: 0 0 20px rgba(0,0,0,0.1); color: #333; font-family: 'Inter', sans-serif; font-size: 11px; line-height: 1.6;
    }}
    
    /* Link Box */
    .link-box {{
        padding: 15px; background-color: #e8f4f8; border: 2px dashed {COR_PRIMARIA};
        border-radius: 8px; text-align: center; font-family: monospace; font-weight: bold;
        color: {COR_PRIMARIA}; word-break: break-all;
    }}

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
            "segmentacao": "GHE", "resp": "Carlos Silva", "email": "carlos@fabril.com",
            "logo": None, "score": 2.8, "respondidas": 120,
            "dimensoes": {"Demanda": 2.1, "Controle": 3.5, "Suporte": 2.8, "Relacionamentos": 2.5, "Papel": 4.5, "Mudança": 3.0},
            "detalhe_perguntas": {"Prazos impossíveis": 65, "Pressão longas horas": 45, "Trabalho intenso": 55, "Assédio pessoal": 15}
        }
    ]

# LISTA COMPLETA HSE
if 'hse_questions' not in st.session_state:
    st.session_state.hse_questions = {
        "Demandas": [
            {"id": 3, "q": "Tenho prazos impossíveis de cumprir?", "rev": True, "help": "Ex: Receber tarefas às 17h para entregar às 18h."},
            {"id": 6, "q": "Sou pressionado a trabalhar longas horas?", "rev": True, "help": "Ex: Hora extra constante."},
            {"id": 9, "q": "Tenho que trabalhar muito intensamente?", "rev": True, "help": "Ex: Sem tempo para respirar."}
        ],
        "Controle": [{"id": 2, "q": "Posso decidir quando fazer uma pausa?", "rev": False, "help": "Ex: Ir ao banheiro sem pedir."}],
        "Suporte": [{"id": 8, "q": "Recebo feedback sobre o trabalho?", "rev": False, "help": "Ex: Saber se está indo bem."}],
        "Relacionamentos": [{"id": 5, "q": "Estou sujeito a assédio pessoal?", "rev": True, "help": "Ex: Piadas ofensivas."}]
    }

if 'base_url' not in st.session_state: st.session_state.base_url = "http://localhost:8501" 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- 4. FUNÇÕES AUXILIARES ---
def get_logo_html(width=180):
    """Retorna a Logo do Sistema ou da Consultoria (Whitelabel)"""
    if st.session_state.platform_config['logo_b64']:
        return f'<img src="data:image/png;base64,{st.session_state.platform_config["logo_b64"]}" width="{width}">'
    
    # Logo Padrão SVG (Elo NR-01)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 100" width="{width}"><style>.t1 {{ font-family: sans-serif; font-weight: bold; font-size: 45px; fill: {COR_PRIMARIA}; }} .t2 {{ font-family: sans-serif; font-weight: 300; font-size: 45px; fill: {COR_SECUNDARIA}; }}</style><path d="M20,35 L50,35 A15,15 0 0 1 50,65 L20,65 A15,15 0 0 1 20,35 Z" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="8" /><path d="M45,35 L75,35 A15,15 0 0 1 75,65 L45,65 A15,15 0 0 1 45,35 Z" fill="none" stroke="{COR_PRIMARIA}" stroke-width="8" /><text x="100" y="68" class="t1">Elo</text><text x="180" y="68" class="t2">NR-01</text></svg>"""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}">'

def image_to_base64(uploaded_file):
    try:
        if uploaded_file: return base64.b64encode(uploaded_file.getvalue()).decode()
    except: pass
    return None

def logout(): st.session_state.logged_in = False; st.session_state.user_role = None; st.rerun()

def kpi_card(title, value, icon, color_class):
    st.markdown(f"""<div class="kpi-card"><div class="kpi-top"><div class="kpi-icon-box {color_class}">{icon}</div></div><div><div class="kpi-value">{value}</div><div class="kpi-title">{title}</div></div></div>""", unsafe_allow_html=True)

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
                    st.error("Credenciais inválidas.")
        st.caption("Colaboradores: Utilizem o link fornecido pelo RH.")

def admin_dashboard():
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; margin-bottom:30px; margin-top:20px;'>{get_logo_html(160)}</div>", unsafe_allow_html=True)
        selected = option_menu(menu_title=None, options=["Visão Geral", "Gerar Link", "Empresas", "Relatórios", "Configurações"], icons=["grid", "link-45deg", "building", "file-text", "gear"], default_index=3, styles={"nav-link-selected": {"background-color": COR_PRIMARIA}})
        st.markdown("---"); 
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
        with col4: kpi_card("Alertas", 3, "🚨", "bg-red")

        st.markdown("<br>", unsafe_allow_html=True)
        c_chart1, c_chart2 = st.columns([1, 1.5])
        
        with c_chart1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Distribuição de Risco")
            df = pd.DataFrame(st.session_state.companies_db)
            fig_pie = px.pie(df, names='setor', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c_chart2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Radar HSE (Dimensões)")
            categories = ['Demanda', 'Controle', 'Apoio', 'Relações', 'Papel', 'Mudança']
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=[2, 4, 3, 2, 5, 4], theta=categories, fill='toself', name='Média'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=300, margin=dict(t=20, b=20))
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 2. GERAR LINK ---
    elif selected == "Gerar Link":
        st.title("Gerar Link & Testar")
        with st.container():
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
            empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_nome)
            link_final = f"{st.session_state.base_url}/?cod={empresa['id']}"
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"<div class='link-box'>{link_final}</div>", unsafe_allow_html=True)
                if st.button("👁️ Testar Formulário (Colaborador)"):
                    st.session_state.current_company = empresa
                    st.session_state.logged_in = True
                    st.session_state.user_role = 'colaborador'
                    st.rerun()
            with c2:
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(link_final)}"
                st.image(qr_url, width=150)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 3. EMPRESAS ---
    elif selected == "Empresas":
        st.title("Gestão de Empresas")
        tab1, tab2 = st.tabs(["Monitoramento", "Novo Cadastro"])
        with tab1:
            df_view = pd.DataFrame(st.session_state.companies_db)
            st.dataframe(df_view[['razao', 'cnpj', 'risco', 'func', 'respondidas']], use_container_width=True)
        with tab2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            with st.form("add_comp"):
                c1, c2 = st.columns(2)
                razao = c1.text_input("Razão Social")
                cnpj = c2.text_input("CNPJ")
                c3, c4 = st.columns(2)
                risco = c3.selectbox("Grau de Risco", [1, 2, 3, 4])
                func = c4.number_input("Nº Vidas", min_value=1)
                cod = st.text_input("Código ID (Ex: IND01)")
                if st.form_submit_button("Salvar"):
                    new_c = {"id": cod, "razao": razao, "cnpj": cnpj, "setor": "Geral", "risco": risco, "func": func, "segmentacao": "GHE", "resp": "RH", "email": "-", "logo": None, "score": 0, "respondidas": 0, "dimensoes": {}, "detalhe_perguntas": {}}
                    st.session_state.companies_db.append(new_c)
                    st.success("Salvo!")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 4. RELATÓRIOS (CORRIGIDO SEM INDENTAÇÃO) ---
    elif selected == "Relatórios":
        st.title("Relatórios e Laudos")
        
        c_sel, c_blank = st.columns([1, 1])
        with c_sel:
            empresa_sel = st.selectbox("Cliente", [c['razao'] for c in st.session_state.companies_db])
        
        empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_sel)
        
        # --- ÁREA DE EDIÇÃO DAS ASSINATURAS ---
        with st.sidebar:
            st.markdown("---")
            st.markdown("#### Assinaturas")
            sig_empresa_nome = st.text_input("Nome Resp. Empresa", value=empresa['resp'])
            sig_empresa_cargo = st.text_input("Cargo Resp. Empresa", value="Diretor(a) Administrativo")
            sig_tecnico_nome = st.text_input("Nome Resp. Técnico", value="Cristiane C. Lima")
            sig_tecnico_cargo = st.text_input("Cargo Resp. Técnico", value="Consultora Pessin Gestão")

        # --- ÁREA DE DADOS DO RELATÓRIO ---
        with st.expander("📝 Editar Conteúdo Técnico", expanded=True):
            analise_texto = st.text_area("Análise Executiva:", value="A avaliação identificou riscos críticos na dimensão 'Demandas', com 65% dos colaboradores relatando prazos irreais.")
            
            st.markdown("#### Plano de Ação")
            if 'acoes_list' not in st.session_state:
                st.session_state.acoes_list = [{"acao": "Revisão de Job Description", "area": "Demanda", "resp": "RH", "prazo": "30/05"}]
            
            edited_df = st.data_editor(pd.DataFrame(st.session_state.acoes_list), num_rows="dynamic", use_container_width=True)
            if not edited_df.empty: st.session_state.acoes_list = edited_df.to_dict('records')

        if st.button("🖨️ Gerar Relatório Moderno (PDF)", type="primary"):
            st.markdown("---")
            
            # 1. LOGO WHITELABEL NO CABEÇALHO (SUBSTITUI A ELO)
            logo_html = get_logo_html(150)
            
            # 2. LOGO DO CLIENTE (SE HOUVER) PARA A SEÇÃO DE DADOS
            logo_cliente_html = ""
            if empresa.get('logo'):
                b64 = image_to_base64(empresa.get('logo'))
                if b64: logo_cliente_html = f"<img src='data:image/png;base64,{b64}' width='100' style='float:right;'>"
            
            plat_name = st.session_state.platform_config['name']
            
            # Geração dos Cards de Dimensões
            html_dimensoes = ""
            for dim, nota in empresa.get('dimensoes', {}).items():
                cor_nota = COR_RISCO_ALTO if nota < 3 else (COR_RISCO_MEDIO if nota < 4 else COR_RISCO_BAIXO)
                risco_txt = "CRÍTICO" if nota < 3 else ("ATENÇÃO" if nota < 4 else "SEGURO")
                html_dimensoes += f'<div style="flex:1; min-width:140px; background:#f8f9fa; border-radius:8px; padding:10px; border:1px solid #eee; margin-right:10px; margin-bottom:10px;"><div style="font-size:10px; color:#666; text-transform:uppercase;">{dim}</div><div style="font-size:18px; font-weight:bold; color:{cor_nota};">{nota}</div><div style="font-size:9px; color:#888;">{risco_txt}</div></div>'
            
            # Geração do Detalhamento por Pergunta
            html_perguntas = ""
            detalhes = empresa.get('detalhe_perguntas', {})
            for perg, pct in detalhes.items():
                cor_bar = COR_RISCO_ALTO if pct > 50 else (COR_RISCO_MEDIO if pct > 30 else COR_RISCO_BAIXO)
                html_perguntas += f'<div style="margin-bottom:8px;"><div style="display:flex; justify-content:space-between; font-size:10px;"><span>{perg}</span><span>{pct}% Risco</span></div><div style="width:100%; background-color:#f0f0f0; border-radius:4px; height:8px;"><div style="height:100%; border-radius:4px; width:{pct}%; background-color:{cor_bar};"></div></div></div>'

            # Lista de Ações
            html_acoes = "".join([f"<li><strong>{item['acao']}</strong> ({item['area']}) - Prazo: {item['resp']}</li>" for item in st.session_state.acoes_list])

            # HTML COMPLETAMENTE SEM INDENTAÇÃO PARA EVITAR ERRO DE VISUALIZAÇÃO
            html_content = f"""
<div class="a4-paper">
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid {COR_PRIMARIA}; padding-bottom:20px; margin-bottom:30px;">
<div>{logo_html}</div>
<div style="text-align:right;"><div style="font-size:20px; font-weight:700; color:{COR_PRIMARIA};">LAUDO TÉCNICO HSE-IT</div><div style="font-size:12px; color:#666;">NR-01 / Gerenciamento de Riscos Psicossociais</div></div>
</div>
<div style="background:#f8f9fa; padding:15px; border-radius:8px; margin-bottom:20px; border-left:5px solid {COR_SECUNDARIA};">
{logo_cliente_html}
<div style="font-size:10px; text-transform:uppercase; color:#888;">Cliente</div>
<div style="font-weight:bold; font-size:14px;">{empresa['razao']}</div>
<div style="font-size:11px;">CNPJ: {empresa['cnpj']} | Adesão: {empresa['respondidas']} Vidas</div>
<div style="font-size:11px;">Data de Emissão: {datetime.datetime.now().strftime('%d/%m/%Y')}</div>
</div>
<div style="font-size:14px; font-weight:700; color:{COR_PRIMARIA}; text-transform:uppercase; margin-top:25px; margin-bottom:15px; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px;">1. Diagnóstico Geral (Dimensões HSE)</div>
<div style="display:flex; flex-wrap:wrap;">{html_dimensoes}</div>
<div style="font-size:14px; font-weight:700; color:{COR_PRIMARIA}; text-transform:uppercase; margin-top:25px; margin-bottom:15px; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px;">2. Raio-X dos Fatores de Risco</div>
<div style="background:white; border:1px solid #eee; padding:15px; border-radius:8px;">{html_perguntas}</div>
<div style="font-size:14px; font-weight:700; color:{COR_PRIMARIA}; text-transform:uppercase; margin-top:25px; margin-bottom:15px; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px;">3. Parecer Técnico</div>
<p style="text-align:justify;">{analise_texto}</p>
<div style="font-size:14px; font-weight:700; color:{COR_PRIMARIA}; text-transform:uppercase; margin-top:25px; margin-bottom:15px; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px;">4. Plano de Ação Recomendado</div>
<ul style="list-style-type:square; padding-left:20px;">{html_acoes}</ul>
<div style="margin-top:80px; display:flex; justify-content:space-between; gap:40px;">
<div style="flex:1; text-align:center; border-top:1px solid #333; padding-top:10px;"><strong>{sig_empresa_nome}</strong><br><span style="color:#666;">{sig_empresa_cargo}</span></div>
<div style="flex:1; text-align:center; border-top:1px solid #333; padding-top:10px;"><strong>{sig_tecnico_nome}</strong><br><span style="color:#666;">{sig_tecnico_cargo}</span></div>
</div>
</div>
"""
            st.markdown(html_content, unsafe_allow_html=True)
            st.info("Pressione Ctrl+P para salvar como PDF.")

    # --- 5. CONFIGURAÇÕES (ATUALIZADO) ---
    elif selected == "Configurações":
        st.title("Configurações")
        
        tab_brand, tab_users, tab_sys = st.tabs(["🎨 Personalização", "🔐 Gestão de Acessos", "⚙️ Sistema"])
        
        with tab_brand:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Identidade Visual")
            c_name, c_cons = st.columns(2)
            new_name = c_name.text_input("Nome Plataforma", value=st.session_state.platform_config['name'])
            new_cons = c_cons.text_input("Nome Consultoria", value=st.session_state.platform_config['consultancy'])
            new_logo = st.file_uploader("Logo Plataforma (Whitelabel)", type=['png', 'jpg'])
            if st.button("Salvar Identidade"):
                st.session_state.platform_config['name'] = new_name
                st.session_state.platform_config['consultancy'] = new_cons
                if new_logo: st.session_state.platform_config['logo_b64'] = image_to_base64(new_logo)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_users:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Administradores")
            users_list = pd.DataFrame(list(st.session_state.users_db.items()), columns=['Usuário', 'Senha'])
            users_list['Senha'] = "******"
            st.dataframe(users_list, use_container_width=True)
            
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
            new_url = st.text_input("URL Base (Link)", value=st.session_state.base_url)
            if st.button("Atualizar URL"):
                st.session_state.base_url = new_url
                st.success("Salvo!")
            st.markdown("</div>", unsafe_allow_html=True)

# --- 6. TELA PESQUISA ---
def survey_screen():
    query_params = st.query_params
    cod_url = query_params.get("cod", None)
    
    if cod_url and not st.session_state.get('current_company'):
        company = next((c for c in st.session_state.companies_db if c['id'] == cod_url), None)
        if company: st.session_state.current_company = company
    
    if 'current_company' not in st.session_state:
        st.error("Link inválido."); 
        if st.button("Ir para Login"): st.session_state.logged_in = False; st.session_state.user_role = None; st.rerun()
        return

    comp = st.session_state.current_company
    logo_show = get_logo_html(150)
    if comp.get('logo'):
        b64 = image_to_base64(comp.get('logo'))
        if b64: logo_show = f"<img src='data:image/png;base64,{b64}' width='150'>"
    
    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'>{logo_show}</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center'>Avaliação - {comp['razao']}</h3>", unsafe_allow_html=True)
    
    with st.form("survey"):
        st.markdown("#### 1. Perfil")
        c1, c2 = st.columns(2)
        cpf = c1.text_input("CPF", max_chars=11)
        setor = c2.text_input("Setor")
        
        st.markdown("#### 2. Questionário HSE")
        tabs = st.tabs(list(st.session_state.hse_questions.keys()))
        for i, (cat, pergs) in enumerate(st.session_state.hse_questions.items()):
            with tabs[i]:
                for q in pergs:
                    st.markdown(f"**{q['q']}**")
                    st.radio("Selecione:", ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"] if q['id']<=24 else ["Discordo", "Neutro", "Concordo"], key=f"q_{q['id']}", horizontal=True, label_visibility="collapsed")
                    st.markdown("<hr>", unsafe_allow_html=True)
        
        if st.form_submit_button("Enviar"):
            if not cpf: st.error("CPF Obrigatório.")
            else:
                for c in st.session_state.companies_db:
                    if c['id'] == comp['id']: c['respondidas'] += 1
                st.balloons(); st.success("Sucesso!"); time.sleep(2); st.session_state.logged_in = False; st.rerun()

if not st.session_state.logged_in:
    if "cod" in st.query_params: survey_screen()
    else: login_screen()
else:
    if st.session_state.user_role == 'admin': admin_dashboard()
    else: survey_screen()
