import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import base64
import urllib.parse
from streamlit_option_menu import option_menu

# --- 1. CONFIGURAÇÃO GERAL E BRANDING ---
NOME_SISTEMA = "Elo NR-01"
COR_PRIMARIA = "#005f73"  # Azul Petróleo (Sóbrio e Tech)
COR_SECUNDARIA = "#0a9396" # Verde Água (Saúde Mental)
COR_DESTAQUE = "#ee9b00"   # Amarelo Queimado (Atenção/Risco)
COR_FUNDO = "#f0f2f6"

st.set_page_config(
    page_title=f"{NOME_SISTEMA} | Pessin Gestão",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS AVANÇADO (LAYOUT PROFISSIONAL) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    /* Reset Geral */
    .stApp {{ background-color: {COR_FUNDO}; font-family: 'Roboto', sans-serif; }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{ background-color: #ffffff; border-right: 1px solid #ddd; }}
    
    /* Cards de KPI */
    .kpi-card {{
        background: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center;
        border-top: 4px solid {COR_PRIMARIA}; transition: transform 0.3s;
    }}
    .kpi-card:hover {{ transform: translateY(-5px); }}
    .kpi-val {{ font-size: 28px; font-weight: bold; color: {COR_PRIMARIA}; }}
    .kpi-lbl {{ font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px; }}

    /* Relatório (Simulação A4) */
    .a4-paper {{
        background: white; width: 100%; max-width: 210mm; min-height: 297mm;
        margin: auto; padding: 40px; box-shadow: 0 0 15px rgba(0,0,0,0.1);
        color: #333;
    }}
    
    /* Estilos de Impressão */
    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 20px; width: 100%; }}
        .break-page {{ page-break-after: always; }}
    }}
    
    /* Botões */
    .stButton>button {{
        border-radius: 6px; font-weight: 600; text-transform: uppercase;
        border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTÃO DE ESTADO (BANCO DE DADOS NA MEMÓRIA) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": "admin", "cris.pessin": "123456"} # Usuários Admin

if 'companies_db' not in st.session_state:
    # Dados iniciais para o dashboard não ficar vazio
    st.session_state.companies_db = [
        {"id": "IND01", "razao": "Indústria Têxtil Fabril Ltda", "cnpj": "12.345.678/0001-90", "setor": "Industrial", "risco": 3, "func": 150, "resp": "Carlos Silva", "email": "carlos@fabril.com", "score": 2.8, "status": "Concluído", "data": "10/02/2026"},
        {"id": "TEC02", "razao": "TechSolutions S.A.", "cnpj": "98.765.432/0001-10", "setor": "Tecnologia", "risco": 1, "func": 45, "resp": "Ana Souza", "email": "ana@tech.com", "score": 4.1, "status": "Em Andamento", "data": "12/02/2026"},
    ]

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'active_page' not in st.session_state: st.session_state.active_page = 'Login'

# --- 4. FUNÇÕES UTILITÁRIAS ---
def render_svg_logo(width=200):
    """Renderiza a logo vetorial Elo NR-01"""
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 100" width="{width}">
      <style>
        .t1 {{ font-family: sans-serif; font-weight: bold; font-size: 45px; fill: {COR_PRIMARIA}; }}
        .t2 {{ font-family: sans-serif; font-weight: 300; font-size: 45px; fill: {COR_SECUNDARIA}; }}
        .icon {{ fill: none; stroke: {COR_DESTAQUE}; stroke-width: 8; stroke-linecap: round; }}
      </style>
      <path class="icon" d="M20,35 L50,35 A15,15 0 0 1 50,65 L20,65 A15,15 0 0 1 20,35 Z" />
      <path class="icon" d="M45,35 L75,35 A15,15 0 0 1 75,65 L45,65 A15,15 0 0 1 45,35 Z" />
      <text x="100" y="68" class="t1">Elo</text>
      <text x="180" y="68" class="t2">NR-01</text>
    </svg>
    """
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}">'

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()

# --- 5. MÓDULOS DO SISTEMA ---

def login_screen():
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center'>{render_svg_logo(280)}</div>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center; color:#666;'>Gestão de Riscos Psicossociais</h4><br>", unsafe_allow_html=True)
        
        tab_colab, tab_admin = st.tabs(["Sou Colaborador", "Área Restrita (RH)"])
        
        with tab_colab:
            with st.form("login_colab"):
                cod = st.text_input("Insira o Código da Empresa", placeholder="Ex: IND01")
                if st.form_submit_button("Iniciar Avaliação", type="primary"):
                    company = next((c for c in st.session_state.companies_db if c['id'] == cod), None)
                    if company:
                        st.session_state.current_company = company
                        st.session_state.logged_in = True
                        st.session_state.user_role = 'colaborador'
                        st.rerun()
                    else:
                        st.error("Código não encontrado.")
        
        with tab_admin:
            with st.form("login_admin"):
                user = st.text_input("Usuário")
                pwd = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar no Painel"):
                    if user in st.session_state.users_db and st.session_state.users_db[user] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.user_role = 'admin'
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas.")

def admin_dashboard():
    # Menu Lateral Profissional
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; margin-bottom:20px'>{render_svg_logo(150)}</div>", unsafe_allow_html=True)
        selected = option_menu(
            "Menu Principal",
            ["Dashboard", "Empresas", "Relatórios", "Acessos", "Sair"],
            icons=['graph-up', 'building', 'file-earmark-pdf', 'key', 'box-arrow-right'],
            menu_icon="cast", default_index=0,
            styles={
                "nav-link-selected": {"background-color": COR_PRIMARIA},
            }
        )
        if selected == "Sair": logout()

    # --- PÁGINA: DASHBOARD ---
    if selected == "Dashboard":
        st.title("📊 Visão Geral da Carteira")
        st.markdown("---")
        
        # KPIs
        df = pd.DataFrame(st.session_state.companies_db)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='kpi-card'><div class='kpi-val'>{len(df)}</div><div class='kpi-lbl'>Empresas Ativas</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='kpi-card'><div class='kpi-val'>{df['func'].sum()}</div><div class='kpi-lbl'>Vidas Monitoradas</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='kpi-card'><div class='kpi-val'>4.2</div><div class='kpi-lbl'>Média Geral (Score)</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='kpi-card'><div class='kpi-val'>12</div><div class='kpi-lbl'>Alertas de Risco</div></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos Robustos (Plotly)
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Distribuição por Grau de Risco (NR-04)")
            fig_pie = px.pie(df, names='risco', title='Empresas por Risco', color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with g2:
            st.subheader("Média de Saúde por Setor")
            fig_bar = px.bar(df, x='setor', y='score', title='Índice HSE por Setor', color='score', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- PÁGINA: EMPRESAS ---
    elif selected == "Empresas":
        st.title("🏢 Gestão de Empresas")
        
        tab_list, tab_add = st.tabs(["Lista de Clientes", "Novo Cadastro & Links"])
        
        with tab_list:
            st.dataframe(pd.DataFrame(st.session_state.companies_db), use_container_width=True)
        
        with tab_add:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Dados Cadastrais")
                with st.form("new_company"):
                    razao = st.text_input("Razão Social")
                    cnpj = st.text_input("CNPJ")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        cod = st.text_input("Código ID (Ex: CLI01)")
                        cnae = st.text_input("CNAE Principal")
                        risco = st.selectbox("Grau de Risco", [1, 2, 3, 4])
                    with col_b:
                        resp = st.text_input("Nome Responsável")
                        email = st.text_input("E-mail Responsável")
                        func = st.number_input("Nº Funcionários", min_value=1)
                    
                    if st.form_submit_button("Salvar Empresa"):
                        new_data = {
                            "id": cod, "razao": razao, "cnpj": cnpj, "setor": "Geral", 
                            "risco": risco, "func": func, "resp": resp, "email": email,
                            "score": 0, "status": "Aguardando", "data": datetime.now().strftime("%d/%m/%Y")
                        }
                        st.session_state.companies_db.append(new_data)
                        st.success("Empresa cadastrada com sucesso!")
                        st.rerun()

            with c2:
                st.subheader("Gerador de Acesso")
                empresa_sel = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
                empresa_obj = next(c for c in st.session_state.companies_db if c['razao'] == empresa_sel)
                
                link = f"https://elo-nr01.app/?cod={empresa_obj['id']}"
                st.success(f"Link Ativo: {link}")
                
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(link)}"
                c_qr, c_txt = st.columns([1,2])
                c_qr.image(qr_url)
                c_txt.info(f"Código ID: **{empresa_obj['id']}**\n\nEnvie este código ou o link para os colaboradores.")

    # --- PÁGINA: ACESSOS (SOLICITADO POR CRIS) ---
    elif selected == "Acessos":
        st.title("🔐 Gestão de Administradores")
        st.markdown("Gerencie quem tem acesso ao painel de consultoria da Pessin.")
        
        c_list, c_edit = st.columns(2)
        with c_list:
            st.subheader("Usuários Ativos")
            df_users = pd.DataFrame(list(st.session_state.users_db.items()), columns=['Usuário', 'Senha (Hash)'])
            df_users['Senha (Hash)'] = "********" # Mascarar senha
            st.table(df_users)
        
        with c_edit:
            st.subheader("Adicionar / Alterar Senha")
            with st.form("user_mgmt"):
                u_login = st.text_input("Login (E-mail ou Usuário)")
                u_pass = st.text_input("Nova Senha", type="password")
                tipo = st.radio("Ação", ["Criar Novo", "Alterar Senha"])
                
                if st.form_submit_button("Executar"):
                    if u_login and u_pass:
                        st.session_state.users_db[u_login] = u_pass
                        st.success(f"Usuário {u_login} atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha todos os campos.")

    # --- PÁGINA: RELATÓRIOS ---
    elif selected == "Relatórios":
        st.title("📑 Emissão de Laudos Técnicos")
        
        col_sel, col_act = st.columns([3, 1])
        with col_sel:
            empresa_rel = st.selectbox("Selecione o Cliente para o Laudo", [c['razao'] for c in st.session_state.companies_db])
        
        empresa_obj = next(c for c in st.session_state.companies_db if c['razao'] == empresa_rel)
        
        # Simulação de dados para o relatório
        fator_critico = "Demandas Psicológicas" if empresa_obj['score'] < 3 else "Nenhum"
        
        with st.expander("🛠️ Personalizar Plano de Ação", expanded=False):
            st.write(f"Fator Crítico Identificado: **{fator_critico}**")
            acoes = st.multiselect("Selecione as ações recomendadas:", 
                                   ["Revisão de Job Description", "Treinamento de Liderança", "Programa de Pausas Ativas", "Mediação de Conflitos"],
                                   default=["Revisão de Job Description", "Treinamento de Liderança"])
            obs_consultor = st.text_area("Observações Técnicas da Consultora (Cris):", "A empresa apresenta boa adesão, porém necessita ajustes pontuais em cargas horárias.")

        if st.button("🖨️ Gerar Visualização de Impressão (A4)"):
            # --- RENDERIZAÇÃO DO RELATÓRIO TIPO "PAPEL" ---
            st.markdown("---")
            with st.container():
                st.markdown(f"""
                <div class="a4-paper">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid {COR_PRIMARIA}; padding-bottom:10px; margin-bottom:20px;">
                        <div>{render_svg_logo(120)}</div>
                        <div style="text-align:right;">
                            <h3 style="margin:0; color:{COR_PRIMARIA}">LAUDO TÉCNICO NR-01</h3>
                            <small>Ref: Riscos Psicossociais</small>
                        </div>
                    </div>
                    
                    <div style="background-color:#f9f9f9; padding:15px; border-radius:5px; margin-bottom:20px;">
                        <strong>Cliente:</strong> {empresa_obj['razao']}<br>
                        <strong>CNPJ:</strong> {empresa_obj['cnpj']} | <strong>Risco:</strong> {empresa_obj['risco']}<br>
                        <strong>Data da Emissão:</strong> {datetime.now().strftime('%d/%m/%Y')}
                    </div>
                    
                    <h4>1. Contexto Legal (NR-01)</h4>
                    <p style="text-align:justify; font-style:italic; font-size:0.9em; color:#555;">
                        "1.5.3.1.1 O gerenciamento de riscos ocupacionais deve constituir um Programa de Gerenciamento de Riscos (PGR) 
                        e deve incluir [...] os fatores ergonômicos e psicossociais."
                    </p>
                    
                    <h4>2. Diagnóstico Executivo (Metodologia HSE)</h4>
                    <p>Após análise dos dados coletados, o Score Global de Saúde Mental da organização é de <strong>{empresa_obj['score']}/5.0</strong>.</p>
                    <p><strong>Fator de Atenção:</strong> {fator_critico}</p>
                    
                    <h4>3. Plano de Ação Recomendado</h4>
                    <ul>
                        {''.join([f'<li>{a}</li>' for a in acoes])}
                    </ul>
                    
                    <h4>4. Parecer Técnico</h4>
                    <p>{obs_consultor}</p>
                    
                    <div style="margin-top:80px; display:flex; justify-content:space-between;">
                        <div style="text-align:center; width:45%; border-top:1px solid #000; padding-top:10px;">
                            <strong>{empresa_obj['resp']}</strong><br>Responsável Legal
                        </div>
                        <div style="text-align:center; width:45%; border-top:1px solid #000; padding-top:10px;">
                            <strong>Cristiane Cardoso Lima</strong><br>Consultora Responsável (Pessin)
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.info("Para salvar: Pressione Ctrl+P > Destino: Salvar como PDF.")

def user_survey():
    if 'current_company' not in st.session_state: st.rerun()
    comp = st.session_state.current_company
    
    # Header Limpo
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding:10px; background:white; border-radius:10px; margin-bottom:20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <div><small>Empresa:</small><br><strong>{comp['razao']}</strong></div>
        <div>{render_svg_logo(100)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🔒 Seus dados são anônimos e protegidos. A empresa recebe apenas estatísticas consolidadas.")
    
    with st.expander("ℹ️ Instruções de Preenchimento", expanded=False):
        st.write("Responda pensando nos últimos 6 meses. Não existem respostas certas ou erradas.")

    # Formulário Estilizado
    with st.form("survey"):
        st.markdown("### 1. Demandas do Trabalho")
        st.markdown("**Tenho prazos impossíveis de cumprir?**")
        st.select_slider("", options=["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"], key="q1")
        
        st.markdown("---")
        st.markdown("### 2. Controle e Autonomia")
        st.markdown("**Posso decidir quando fazer uma pausa?**")
        st.select_slider("", options=["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"], key="q2")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("✅ Enviar Respostas"):
            st.balloons()
            st.success("Obrigado! Sua participação fortalece nosso elo.")
            time.sleep(3)
            st.session_state.logged_in = False
            st.rerun()
            
    if st.button("Sair / Cancelar"): logout()

# --- 6. ROTEADOR DE PÁGINAS ---
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.user_role == 'admin':
        admin_dashboard()
    else:
        user_survey()
