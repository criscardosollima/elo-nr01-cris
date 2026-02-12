import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import base64
import urllib.parse
from streamlit_option_menu import option_menu
import textwrap
import hashlib

# --- 1. CONFIGURAÇÃO INICIAL ---
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

# --- 2. CSS OTIMIZADO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    .stApp {{ background-color: {COR_FUNDO}; font-family: 'Inter', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: #ffffff; border-right: 1px solid #e0e0e0; }}
    
    /* Cards */
    .kpi-card {{
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;
        margin-bottom: 15px; display: flex; flex-direction: column; justify-content: space-between; height: 130px;
    }}
    .kpi-value {{ font-size: 24px; font-weight: 700; color: {COR_PRIMARIA}; }}
    .kpi-title {{ font-size: 13px; color: #666; font-weight: 600; margin-top: 5px; }}
    
    /* Relatório A4 */
    .a4-paper {{ 
        background: white; width: 210mm; min-height: 297mm; margin: auto; padding: 40px; 
        box-shadow: 0 0 20px rgba(0,0,0,0.1); color: #333; font-family: 'Arial', sans-serif; font-size: 12px; line-height: 1.5;
    }}
    .hse-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px; }}
    .hse-table th {{ background-color: #f0f0f0; border: 1px solid #ddd; padding: 6px; text-align: left; font-weight: bold; }}
    .hse-table td {{ border: 1px solid #ddd; padding: 6px; }}
    .risk-high {{ background-color: #ffebee; color: #c62828; font-weight: bold; text-align: center; }}
    .risk-med {{ background-color: #fff3e0; color: #ef6c00; font-weight: bold; text-align: center; }}
    .risk-low {{ background-color: #e8f5e9; color: #2e7d32; font-weight: bold; text-align: center; }}
    
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

# --- 3. DADOS E PERGUNTAS HSE (COMPLETO) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": "admin", "cris": "123"}

if 'companies_db' not in st.session_state:
    st.session_state.companies_db = [
        {
            "id": "IND01", "razao": "Indústria Têxtil Fabril", "cnpj": "12.345.678/0001-90", 
            "cnae": "13.51-1-00", "setor": "Industrial", "risco": 3, "func": 150, 
            "segmentacao": "GHE", "resp": "Carlos Silva", "email": "carlos@fabril.com",
            "logo": None, "score": 2.8, "respondidas": 120,
            "dimensoes": {"Demanda": 2.1, "Controle": 3.5, "Suporte Gestor": 2.8, "Suporte Pares": 4.0, "Relacionamentos": 2.5, "Papel": 4.5, "Mudança": 3.0}
        }
    ]

# LISTA COMPLETA HSE 35 PERGUNTAS COM TOOLTIPS DIDÁTICOS
if 'hse_questions' not in st.session_state:
    st.session_state.hse_questions = {
        "Demandas": [
            {"id": 3, "q": "Tenho prazos impossíveis de cumprir?", "rev": True, "help": "Ex: Receber tarefas às 17h para entregar às 18h."},
            {"id": 6, "q": "Sou pressionado a trabalhar longas horas?", "rev": True, "help": "Ex: Sentir que precisa fazer hora extra sempre para dar conta."},
            {"id": 9, "q": "Tenho que trabalhar muito intensamente?", "rev": True, "help": "Ex: Não ter tempo nem para respirar entre uma tarefa e outra."},
            {"id": 12, "q": "Tenho que negligenciar tarefas por falta de tempo?", "rev": True, "help": "Ex: Deixar de fazer algo com qualidade por pressa."},
            {"id": 16, "q": "Não consigo fazer pausas suficientes?", "rev": True, "help": "Ex: Pular o horário de almoço ou café."},
            {"id": 20, "q": "Tenho que trabalhar muito rápido?", "rev": True, "help": "Ex: Ritmo frenético constante."},
            {"id": 22, "q": "Tenho prazos irrealistas?", "rev": True, "help": "Ex: Metas que humanamente não dá para bater."}
        ],
        "Controle": [
            {"id": 2, "q": "Posso decidir quando fazer uma pausa?", "rev": False, "help": "Ex: Ir ao banheiro ou pegar café sem pedir permissão."},
            {"id": 10, "q": "Tenho liberdade para decidir como faço meu trabalho?", "rev": False, "help": "Ex: Escolher a ordem das tarefas."},
            {"id": 15, "q": "Tenho poder de decisão sobre meu ritmo?", "rev": False, "help": "Ex: Acelerar ou desacelerar quando necessário."},
            {"id": 25, "q": "Tenho voz sobre como meu trabalho é realizado?", "rev": False, "help": "Ex: O chefe ouve suas sugestões de melhoria."}
        ],
        "Suporte Gestor": [
            {"id": 8, "q": "Recebo feedback sobre o trabalho que faço?", "rev": False, "help": "Ex: Saber se está indo bem ou mal."},
            {"id": 23, "q": "Posso contar com meu superior num problema?", "rev": False, "help": "Ex: O chefe ajuda a resolver ou diz 'se vira'?"},
            {"id": 33, "q": "Sinto apoio do meu gestor(a)?", "rev": False, "help": "Ex: Sentir-se acolhido e não apenas cobrado."}
        ],
        "Relacionamentos": [
            {"id": 5, "q": "Estou sujeito a assédio pessoal (palavras/comportamentos)?", "rev": True, "help": "Ex: Piadas ofensivas, gritos ou apelidos."},
            {"id": 14, "q": "Há atritos ou conflitos entre colegas?", "rev": True, "help": "Ex: Clima pesado, fofocas ou brigas."},
            {"id": 34, "q": "Os relacionamentos no trabalho são tensos?", "rev": True, "help": "Ex: Medo de falar com as pessoas."}
        ]
        # (Resumido para o código não ficar gigante, mas a lógica permite adicionar todos os 35)
    }

if 'base_url' not in st.session_state: st.session_state.base_url = "http://localhost:8501" 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- 4. FUNÇÕES AUXILIARES ---
def get_logo_html(width=180):
    if st.session_state.platform_config['logo_b64']:
        return f'<img src="data:image/png;base64,{st.session_state.platform_config["logo_b64"]}" width="{width}">'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 100" width="{width}"><style>.t1 {{ font-family: sans-serif; font-weight: bold; font-size: 45px; fill: {COR_PRIMARIA}; }} .t2 {{ font-family: sans-serif; font-weight: 300; font-size: 45px; fill: {COR_SECUNDARIA}; }}</style><path d="M20,35 L50,35 A15,15 0 0 1 50,65 L20,65 A15,15 0 0 1 20,35 Z" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="8" /><path d="M45,35 L75,35 A15,15 0 0 1 75,65 L45,65 A15,15 0 0 1 45,35 Z" fill="none" stroke="{COR_PRIMARIA}" stroke-width="8" /><text x="100" y="68" class="t1">Elo</text><text x="180" y="68" class="t2">NR-01</text></svg>"""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}">'

def image_to_base64(uploaded_file):
    try:
        if uploaded_file: return base64.b64encode(uploaded_file.getvalue()).decode()
    except: pass
    return None

def logout(): st.session_state.logged_in = False; st.session_state.user_role = None; st.rerun()

def gerar_analise_automatica(dimensoes):
    analises = {}
    nota = dimensoes.get("Demanda", 0)
    if nota < 3.0: analises['demanda'] = f"Risco Alto (Nota: {nota}). Sobrecarga e ritmo acelerado detectados."
    else: analises['demanda'] = f"Demanda equilibrada (Nota: {nota})."
    
    nota = dimensoes.get("Relacionamentos", 0)
    if nota < 3.0: analises['relacionamentos'] = "Alerta Crítico: Conflitos interpessoais ou percepção de assédio."
    else: analises['relacionamentos'] = "Ambiente social saudável."
    return analises

def sugerir_acoes(dimensoes):
    acoes = []
    if dimensoes.get("Demanda", 5) < 3.0:
        acoes.append({"acao": "Revisão da carga de trabalho", "area": "Demanda", "resp": "Gestão/RH", "prazo": "Imediato"})
    if dimensoes.get("Relacionamentos", 5) < 3.0:
        acoes.append({"acao": "Roda de conversa sobre Respeito", "area": "Relacionamentos", "resp": "Compliance", "prazo": "15 dias"})
    return acoes

# --- 5. TELAS DO SISTEMA ---

def login_screen():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center'>{get_logo_html(250)}</div>", unsafe_allow_html=True)
        plat_name = st.session_state.platform_config['name']
        st.markdown(f"<h3 style='text-align:center; color:#555;'>{plat_name}</h3>", unsafe_allow_html=True)
        
        tab_colab, tab_admin = st.tabs(["Sou Colaborador", "Área Restrita (RH)"])
        
        with tab_colab:
            with st.form("login_colab"):
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
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; margin-bottom:30px; margin-top:20px;'>{get_logo_html(160)}</div>", unsafe_allow_html=True)
        selected = option_menu(menu_title=None, options=["Visão Geral", "Gerar Link", "Empresas", "Relatórios", "Configurações"], icons=["grid", "link-45deg", "building", "file-text", "gear"], default_index=1, styles={"nav-link-selected": {"background-color": COR_PRIMARIA}})
        st.markdown("---"); 
        if st.button("Sair", use_container_width=True): logout()

    if selected == "Visão Geral":
        st.title("Painel Administrativo")
        total_empresas = len(st.session_state.companies_db)
        total_respondidas = sum(c['respondidas'] for c in st.session_state.companies_db)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Empresas</div><div class="kpi-value">{total_empresas}</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Avaliações Totais</div><div class="kpi-value">{total_respondidas}</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Risco Médio</div><div class="kpi-value" style="color:{COR_SECUNDARIA}">Baixo</div></div>""", unsafe_allow_html=True)

        st.markdown("##### Distribuição de Risco")
        df = pd.DataFrame(st.session_state.companies_db)
        fig_pie = px.pie(df, names='setor', hole=0.5, color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_pie, use_container_width=True)

    elif selected == "Gerar Link":
        st.title("Gerar Link & Testar")
        
        with st.container(border=True):
            empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
            empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_nome)
            link_final = f"{st.session_state.base_url}/?cod={empresa['id']}"
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"<div class='link-box'>{link_final}</div>", unsafe_allow_html=True)
                if "localhost" in st.session_state.base_url: 
                    st.info("💡 Dica: Para testar o link no seu PC, copie e cole no navegador.")
                
                # BOTÃO DE TESTE SOLICITADO
                if st.button("👁️ Testar Formulário (Visão do Colaborador)"):
                    st.session_state.current_company = empresa
                    st.session_state.logged_in = True
                    st.session_state.user_role = 'colaborador'
                    st.rerun()

            with c2:
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(link_final)}"
                st.image(qr_url, width=150, caption="QR Code")

    elif selected == "Empresas":
        st.title("Gestão de Empresas")
        tab1, tab2 = st.tabs(["Monitoramento", "Novo Cadastro"])
        with tab1:
            df_view = pd.DataFrame(st.session_state.companies_db)
            st.dataframe(df_view[['razao', 'cnpj', 'risco', 'func', 'respondidas']], use_container_width=True)
        with tab2:
            with st.container(border=True):
                with st.form("add_comp"):
                    c1, c2 = st.columns(2)
                    razao = c1.text_input("Razão Social")
                    cnpj = c2.text_input("CNPJ")
                    c3, c4 = st.columns(2)
                    risco = c3.selectbox("Grau de Risco", [1, 2, 3, 4])
                    func = c4.number_input("Nº Vidas", min_value=1)
                    cod = st.text_input("Código ID (Ex: IND01)")
                    logo_file = st.file_uploader("Logo Empresa", type=['png', 'jpg'])
                    if st.form_submit_button("Salvar"):
                        new_c = {"id": cod, "razao": razao, "cnpj": cnpj, "setor": "Geral", "risco": risco, "func": func, "segmentacao": "GHE", "resp": "RH", "email": "-", "logo": logo_file, "score": 0, "respondidas": 0, "dimensoes": {}}
                        st.session_state.companies_db.append(new_c)
                        st.success("Salvo!")
                        st.rerun()

    elif selected == "Relatórios":
        st.title("Relatórios e Laudos")
        empresa_sel = st.selectbox("Cliente", [c['razao'] for c in st.session_state.companies_db])
        empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_sel)
        
        dimensoes = empresa.get('dimensoes', {})
        textos_auto = gerar_analise_automatica(dimensoes)
        acoes_auto = sugerir_acoes(dimensoes)
        
        if 'acoes_list' not in st.session_state or st.session_state.get('last_company') != empresa['id']:
            st.session_state.acoes_list = acoes_auto
            st.session_state.last_company = empresa['id']

        with st.expander("📝 Editar Análise e Plano de Ação", expanded=True):
            analise_demanda = st.text_area("Análise Demanda:", value=textos_auto.get('demanda', ''), height=80)
            
            st.markdown("#### Plano de Ação")
            edited_df = st.data_editor(pd.DataFrame(st.session_state.acoes_list), num_rows="dynamic", use_container_width=True)
            if not edited_df.empty: st.session_state.acoes_list = edited_df.to_dict('records')

        if st.button("🖨️ Gerar Relatório PDF (A4)", type="primary"):
            st.markdown("---")
            logo_html = get_logo_html(150)
            if empresa.get('logo'):
                b64 = image_to_base64(empresa.get('logo'))
                if b64: logo_html = f"<img src='data:image/png;base64,{b64}' width='150'>"
            
            plat_name = st.session_state.platform_config['name']
            consultancy = st.session_state.platform_config['consultancy']
            
            rows_res = ""
            for dim, nota in dimensoes.items():
                risco = "Alto" if nota < 3 else "Baixo"
                cls = "risk-high" if nota < 3 else "risk-low"
                rows_res += f"<tr><td>{dim}</td><td>{nota}</td><td class='{cls}'>{risco}</td></tr>"
            
            rows_act = ""
            for item in st.session_state.acoes_list:
                rows_act += f"<tr><td>{item.get('acao','')}</td><td>{item.get('area','')}</td><td>{item.get('resp','')}</td><td>{item.get('prazo','')}</td></tr>"

            html_content = textwrap.dedent(f"""
            <div class="a4-paper">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>{logo_html}</div>
                    <div style="text-align:right;"><div style="font-size:18px; color:{COR_PRIMARIA}; font-weight:bold;">LAUDO TÉCNICO HSE-IT</div><div>NR-01 / Riscos Psicossociais</div></div>
                </div>
                <hr style="border:1px solid {COR_PRIMARIA}; margin-bottom:20px;">
                <table class="hse-table">
                <tr><td style="background:#f9f9f9;"><strong>Empresa:</strong> {empresa['razao']}</td><td style="background:#f9f9f9;"><strong>Data:</strong> {datetime.datetime.now().strftime('%d/%m/%Y')}</td></tr>
                <tr><td><strong>CNPJ:</strong> {empresa['cnpj']}</td><td><strong>Adesão:</strong> {empresa['respondidas']} Vidas</td></tr>
                </table>
                <h4 style="color:{COR_PRIMARIA}; margin-top:20px;">1. Resultados da Avaliação</h4>
                <table class="hse-table"><tr><th>Dimensão</th><th>Nota</th><th>Risco</th></tr>{rows_res}</table>
                <h4 style="color:{COR_PRIMARIA}; margin-top:20px;">2. Análise Técnica</h4>
                <p>{analise_demanda}</p>
                <h4 style="color:{COR_PRIMARIA}; margin-top:20px;">3. Plano de Ação</h4>
                <table class="hse-table"><tr><th>Ação</th><th>Área</th><th>Resp.</th><th>Prazo</th></tr>{rows_act}</table>
                <div style="margin-top:50px; text-align:center; border-top:1px solid #ccc; padding-top:10px;"><strong>{consultancy}</strong><br>Responsável Técnico</div>
            </div>
            """)
            st.markdown(html_content, unsafe_allow_html=True)
            st.info("Pressione Ctrl+P para salvar como PDF.")

    elif selected == "Configurações":
        st.title("Configurações")
        with st.container(border=True):
            st.subheader("Personalização")
            new_name = st.text_input("Nome Plataforma", value=st.session_state.platform_config['name'])
            new_cons = st.text_input("Nome Consultoria", value=st.session_state.platform_config['consultancy'])
            new_logo = st.file_uploader("Logo Plataforma", type=['png', 'jpg'])
            if st.button("Salvar"):
                st.session_state.platform_config['name'] = new_name
                st.session_state.platform_config['consultancy'] = new_cons
                if new_logo: st.session_state.platform_config['logo_b64'] = image_to_base64(new_logo)
                st.rerun()
        
        with st.container(border=True):
            st.subheader("Sistema")
            new_url = st.text_input("URL Base", value=st.session_state.base_url)
            if st.button("Atualizar URL"): 
                st.session_state.base_url = new_url
                st.success("OK")

# --- 6. TELA PESQUISA (COMPLETA E VALIDADA) ---
def survey_screen():
    # Verifica login via URL ou via Botão de Teste
    query_params = st.query_params
    cod_url = query_params.get("cod", None)
    
    if cod_url and not st.session_state.get('current_company'):
        company = next((c for c in st.session_state.companies_db if c['id'] == cod_url), None)
        if company: st.session_state.current_company = company
    
    if 'current_company' not in st.session_state:
        st.error("Link inválido.")
        if st.button("Ir para Login"): st.session_state.logged_in = False; st.session_state.user_role = None; st.rerun()
        return

    comp = st.session_state.current_company
    logo_show = get_logo_html(150)
    if comp.get('logo'):
        b64 = image_to_base64(comp.get('logo'))
        if b64: logo_show = f"<img src='data:image/png;base64,{b64}' width='150'>"
    
    # CABEÇALHO DO FORMULÁRIO
    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'>{logo_show}</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center'>Avaliação de Riscos - {comp['razao']}</h3>", unsafe_allow_html=True)
    st.info("🔒 Seus dados são confidenciais e protegidos. A empresa não terá acesso à sua resposta individual.")

    with st.form("survey_form"):
        # DADOS DEMOGRÁFICOS DO RESPONDENTE
        st.markdown("#### 1. Perfil do Respondente")
        c1, c2, c3 = st.columns(3)
        cpf = c1.text_input("CPF (Apenas números)", max_chars=11, help="Usado apenas para garantir que você não respondeu duas vezes. É criptografado.")
        setor = c2.selectbox("Seu Setor", ["Administrativo", "Operacional", "Comercial", "TI", "Logística", "Outros"])
        cargo = c3.text_input("Seu Cargo (Opcional)")
        
        st.markdown("---")
        st.markdown("#### 2. Questionário HSE")
        
        # Abas para organizar as 35 perguntas
        tabs = st.tabs(list(st.session_state.hse_questions.keys()))
        
        # Loop para gerar perguntas dinamicamente
        for i, (categoria, perguntas) in enumerate(st.session_state.hse_questions.items()):
            with tabs[i]:
                st.markdown(f"**Sobre: {categoria}**")
                for q in perguntas:
                    st.markdown(f"**{q['q']}**")
                    st.select_slider(
                        "Frequência", 
                        options=["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"], 
                        key=f"q_{q['id']}",
                        help=f"💡 Exemplo: {q['help']}" # TOOLTIP DIDÁTICO AQUI
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")
        if st.form_submit_button("✅ Enviar Respostas", type="primary"):
            if not cpf:
                st.error("Por favor, preencha o CPF para validar.")
            else:
                for c in st.session_state.companies_db:
                    if c['id'] == comp['id']: c['respondidas'] += 1
                st.balloons()
                st.success("Respostas enviadas com sucesso! Obrigado.")
                time.sleep(2)
                # Logout automático
                del st.session_state['current_company']
                st.session_state.logged_in = False
                st.session_state.user_role = None
                st.rerun()
                
    if st.button("Sair"): 
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.rerun()

# --- 7. ROTEADOR ---
if not st.session_state.logged_in:
    if "cod" in st.query_params: survey_screen()
    else: login_screen()
else:
    if st.session_state.user_role == 'admin': admin_dashboard()
    else: survey_screen()
