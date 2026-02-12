import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import base64
import urllib.parse
from streamlit_option_menu import option_menu

# --- 1. CONFIGURAÇÃO GERAL ---
NOME_SISTEMA = "Elo NR-01"
COR_PRIMARIA = "#005f73"  
COR_SECUNDARIA = "#0a9396" 
COR_DESTAQUE = "#ee9b00"   
COR_FUNDO = "#f0f2f6"

st.set_page_config(
    page_title=f"{NOME_SISTEMA} | Pessin Gestão",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    .stApp {{ background-color: {COR_FUNDO}; font-family: 'Roboto', sans-serif; }}
    
    /* Card KPI */
    .kpi-card {{
        background: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center;
        border-top: 4px solid {COR_PRIMARIA};
    }}
    .kpi-val {{ font-size: 28px; font-weight: bold; color: {COR_PRIMARIA}; }}
    .kpi-lbl {{ font-size: 14px; color: #666; text-transform: uppercase; }}

    /* Relatório A4 */
    .a4-paper {{
        background: white; width: 210mm; min-height: 297mm;
        margin: auto; padding: 40px; box-shadow: 0 0 15px rgba(0,0,0,0.1);
        color: #333; font-family: 'Arial', sans-serif;
    }}
    
    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 20px; width: 100%; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS E ESTADO ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": "admin", "cris.pessin": "123456"}

if 'companies_db' not in st.session_state:
    st.session_state.companies_db = [
        {"id": "IND01", "razao": "Indústria Têxtil Fabril Ltda", "cnpj": "12.345.678/0001-90", "setor": "Industrial", "risco": 3, "func": 150, "resp": "Carlos Silva", "email": "carlos@fabril.com", "score": 2.8, "status": "Concluído", "data": "10/02/2026"},
        {"id": "TEC02", "razao": "TechSolutions S.A.", "cnpj": "98.765.432/0001-10", "setor": "Tecnologia", "risco": 1, "func": 45, "resp": "Ana Souza", "email": "ana@tech.com", "score": 4.1, "status": "Em Andamento", "data": "12/02/2026"},
    ]

if 'base_url' not in st.session_state:
    # URL Padrão Local. Se subir para a nuvem, o usuário altera no painel.
    st.session_state.base_url = "http://localhost:8501"

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- 4. FUNÇÕES ---
def render_svg_logo(width=200):
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

# --- 5. TELAS ---

def login_screen():
    c1, c2, c3 = st.columns([1,1.5,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center'>{render_svg_logo(280)}</div>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center; color:#666;'>Gestão de Riscos Psicossociais</h4><br>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sou Colaborador", "Área Restrita (RH)"])
        
        with tab1:
            with st.form("login_colab"):
                # Pega o código da URL se existir
                query_params = st.query_params
                default_cod = query_params.get("cod", "")
                
                cod = st.text_input("Código da Empresa", value=default_cod, placeholder="Ex: IND01")
                if st.form_submit_button("Iniciar Avaliação", type="primary"):
                    company = next((c for c in st.session_state.companies_db if c['id'] == cod), None)
                    if company:
                        st.session_state.current_company = company
                        st.session_state.logged_in = True
                        st.session_state.user_role = 'colaborador'
                        st.rerun()
                    else:
                        st.error("Código inválido.")

        with tab2:
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
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; margin-bottom:20px'>{render_svg_logo(150)}</div>", unsafe_allow_html=True)
        selected = option_menu(
            "Menu Principal",
            ["Dashboard", "Empresas", "Relatórios", "Configurações", "Sair"],
            icons=['graph-up', 'building', 'file-earmark-pdf', 'gear', 'box-arrow-right'],
            menu_icon="cast", default_index=0,
            styles={"nav-link-selected": {"background-color": COR_PRIMARIA}}
        )
        if selected == "Sair": logout()

    # --- DASHBOARD ---
    if selected == "Dashboard":
        st.title("📊 Visão Geral da Carteira")
        df = pd.DataFrame(st.session_state.companies_db)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='kpi-card'><div class='kpi-val'>{len(df)}</div><div class='kpi-lbl'>Empresas</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='kpi-card'><div class='kpi-val'>{df['func'].sum()}</div><div class='kpi-lbl'>Vidas</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='kpi-card'><div class='kpi-val'>4.2</div><div class='kpi-lbl'>Score Médio</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='kpi-card'><div class='kpi-val'>2</div><div class='kpi-lbl'>Alertas</div></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            fig_pie = px.pie(df, names='risco', title='Distribuição por Grau de Risco', color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            fig_bar = px.bar(df, x='setor', y='score', title='Saúde Mental por Setor', color='score', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- EMPRESAS (Link e Mensagem Corrigidos) ---
    elif selected == "Empresas":
        st.title("🏢 Gestão de Empresas")
        tab_list, tab_add = st.tabs(["Lista de Clientes", "Cadastrar & Divulgar"])
        
        with tab_list:
            st.dataframe(pd.DataFrame(st.session_state.companies_db), use_container_width=True)

        with tab_add:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("1. Novo Cadastro")
                with st.form("new_company"):
                    razao = st.text_input("Razão Social")
                    cnpj = st.text_input("CNPJ")
                    cod = st.text_input("Crie um Código de Acesso (Ex: PESSIN25)")
                    risco = st.selectbox("Grau de Risco", [1, 2, 3, 4])
                    func = st.number_input("Nº Funcionários", min_value=1)
                    resp = st.text_input("Nome Responsável")
                    
                    if st.form_submit_button("Salvar Empresa"):
                        new_data = {
                            "id": cod, "razao": razao, "cnpj": cnpj, "setor": "Geral", 
                            "risco": risco, "func": func, "resp": resp, "email": "-",
                            "score": 0, "status": "Aguardando", "data": datetime.datetime.now().strftime("%d/%m/%Y")
                        }
                        st.session_state.companies_db.append(new_data)
                        st.success("Empresa cadastrada!")
                        st.rerun()

            with c2:
                st.subheader("2. Kit de Divulgação")
                empresa_sel = st.selectbox("Selecione a Empresa para Gerar Link", [c['razao'] for c in st.session_state.companies_db])
                empresa_obj = next(c for c in st.session_state.companies_db if c['razao'] == empresa_sel)
                
                # LINK CORRIGIDO: Usa a URL base configurada
                link_real = f"{st.session_state.base_url}/?cod={empresa_obj['id']}"
                
                st.markdown(f"**Link de Acesso:**")
                st.code(link_real, language="text")
                
                # MENSAGEM DE WHATSAPP (AQUI ESTÁ!)
                st.markdown("**Mensagem para WhatsApp/E-mail:**")
                msg_texto = f"""Olá time {empresa_obj['razao']}! 👋

A Pessin Gestão iniciou o programa *Elo NR-01* para cuidar da nossa saúde mental.
Participe da avaliação de riscos psicossociais. É 100% anônimo.

🔗 *Clique para responder:*
{link_real}

Contamos com você!"""
                st.text_area("Copie o texto abaixo:", value=msg_texto, height=200)

    # --- RELATÓRIOS (Renderização Corrigida) ---
    elif selected == "Relatórios":
        st.title("📑 Laudo Técnico")
        empresa_rel = st.selectbox("Selecione o Cliente", [c['razao'] for c in st.session_state.companies_db])
        empresa_obj = next(c for c in st.session_state.companies_db if c['razao'] == empresa_rel)
        
        fator_critico = "Demandas Psicológicas" if empresa_obj['score'] < 3 else "Nenhum"
        
        with st.expander("Personalizar Parecer", expanded=True):
            obs = st.text_area("Observações da Consultora:", "A empresa apresenta conformidade legal, com pontos de atenção em ergonomia cognitiva.")
            acoes = st.multiselect("Plano de Ação", ["Revisão de Job Description", "Treinamento de Liderança", "Pausas Ativas"], default=["Treinamento de Liderança"])

        if st.button("🖨️ Gerar Visualização de Impressão (A4)"):
            st.markdown("---")
            
            # HTML CRU (SEM INDENTAÇÃO PYTHON) PARA EVITAR ERROS
            html = f"""
<div class="a4-paper">
<div style="display:flex; justify-content:space-between; border-bottom: 2px solid {COR_PRIMARIA}; padding-bottom:10px;">
    <div>{render_svg_logo(120)}</div>
    <div style="text-align:right;">
        <h3 style="margin:0; color:{COR_PRIMARIA}">LAUDO TÉCNICO NR-01</h3>
        <small>Avaliação Psicossocial</small>
    </div>
</div>
<br>
<div style="background:#f9f9f9; padding:15px; border-radius:5px;">
    <strong>Cliente:</strong> {empresa_obj['razao']}<br>
    <strong>CNPJ:</strong> {empresa_obj['cnpj']} | <strong>Risco:</strong> {empresa_obj['risco']}<br>
    <strong>Emissão:</strong> {datetime.datetime.now().strftime('%d/%m/%Y')}
</div>

<h4>1. Fundamentação Legal</h4>
<p style="font-style:italic; color:#555;">
"1.5.3.1.1 O gerenciamento de riscos ocupacionais deve constituir um PGR e incluir [...] os fatores ergonômicos e psicossociais." (NR-01)
</p>

<h4>2. Diagnóstico (Metodologia HSE)</h4>
<p>Score Global: <strong>{empresa_obj['score']}/5.0</strong></p>
<div style="background:#eee; width:100%; height:20px; border-radius:10px;">
    <div style="background:{COR_SECUNDARIA if empresa_obj['score'] >= 3 else COR_DESTAQUE}; width:{(empresa_obj['score']/5)*100}%; height:100%; border-radius:10px;"></div>
</div>
<p><strong>Fator Crítico:</strong> {fator_critico}</p>

<h4>3. Plano de Ação</h4>
<ul>
{''.join([f'<li>{a}</li>' for a in acoes])}
</ul>

<h4>4. Parecer Técnico</h4>
<p>{obs}</p>

<div style="margin-top:100px; display:flex; justify-content:space-between;">
    <div style="text-align:center; width:45%; border-top:1px solid #000; padding-top:5px;">
        <strong>{empresa_obj['resp']}</strong><br>Resp. Legal
    </div>
    <div style="text-align:center; width:45%; border-top:1px solid #000; padding-top:5px;">
        <strong>Cristiane C. Lima</strong><br>Consultora Pessin
    </div>
</div>
</div>
"""
            # Renderização com segurança de HTML ativada
            st.markdown(html, unsafe_allow_html=True)
            st.info("Pressione Ctrl+P para salvar como PDF.")

    # --- CONFIGURAÇÕES (URL BASE) ---
    elif selected == "Configurações":
        st.title("⚙️ Configurações do Sistema")
        st.write("Ajuste aqui o link de compartilhamento.")
        
        # Aqui você define o link real!
        nova_url = st.text_input("URL do Sistema (Seu Link Real)", value=st.session_state.base_url)
        if st.button("Atualizar Link"):
            st.session_state.base_url = nova_url
            st.success(f"Link base atualizado para: {nova_url}")

def user_survey():
    if 'current_company' not in st.session_state: st.rerun()
    comp = st.session_state.current_company
    
    st.markdown(f"<div style='text-align:center'>{render_svg_logo(150)}</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center'>Avaliação - {comp['razao']}</h3>", unsafe_allow_html=True)
    
    st.info("🔒 Seus dados são anônimos e protegidos. A empresa recebe apenas estatísticas consolidadas.")

    with st.form("survey"):
        st.write("**1. Tenho prazos impossíveis de cumprir?**")
        st.select_slider("", ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"], key="q1")
        
        st.write("**2. Posso decidir quando fazer uma pausa?**")
        st.select_slider("", ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"], key="q2")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("✅ Enviar Respostas"):
            st.balloons()
            st.success("Obrigado! Sua participação fortalece nosso elo.")
            time.sleep(3)
            st.session_state.logged_in = False
            st.rerun()

# --- 6. ROTEADOR ---
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.user_role == 'admin':
        admin_dashboard()
    else:
        user_survey()
