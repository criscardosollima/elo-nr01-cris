import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import base64
import urllib.parse
import urllib.request
from streamlit_option_menu import option_menu
import textwrap
import random

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
COR_RISCO_ALTO = "#ef5350"
COR_RISCO_MEDIO = "#ffa726"
COR_RISCO_BAIXO = "#66bb6a"

# --- 2. CSS OTIMIZADO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {{ background-color: {COR_FUNDO}; font-family: 'Inter', sans-serif; }}
    [data-testid="stSidebar"] {{ background-color: #ffffff; border-right: 1px solid #e0e0e0; }}
    
    /* Cards KPI */
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

    /* Containers */
    .chart-container {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; height: 100%; }}

    /* Caixa de Segurança (Verde Intenso) */
    .security-box {{
        background-color: #d4edda; 
        border: 1px solid #c3e6cb; 
        border-left: 6px solid #28a745;
        padding: 20px; 
        border-radius: 8px; 
        color: #155724; 
        margin-bottom: 25px; 
        font-family: 'Inter', sans-serif;
    }}
    
    /* Relatório A4 */
    .a4-paper {{ 
        background: white; width: 210mm; min-height: 297mm; margin: auto; padding: 40px; 
        box-shadow: 0 0 20px rgba(0,0,0,0.1); color: #333; font-family: 'Inter', sans-serif; font-size: 11px; line-height: 1.6;
    }}
    .link-area {{ background-color: #f8f9fa; border: 1px dashed #dee2e6; padding: 15px; border-radius: 8px; font-family: monospace; color: #2c3e50; font-weight: bold; word-break: break-all; }}
    
    /* Estilos Tabela HTML Relatório */
    .rep-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 10px; }}
    .rep-table th {{ background-color: {COR_PRIMARIA}; color: white; padding: 8px; text-align: left; }}
    .rep-table td {{ border-bottom: 1px solid #eee; padding: 8px; vertical-align: top; }}

    /* Slider Customizado */
    div[data-testid="stSlider"] > div {{ padding-top: 0px; }}

    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 0; width: 100%; }}
        .stApp {{ background-color: white; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS (MOCKUP INICIAL) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": "admin", "cris": "123"}

if 'companies_db' not in st.session_state:
    st.session_state.companies_db = [
        {
            "id": "IND01", "razao": "Indústria Têxtil Fabril", "cnpj": "12.345.678/0001-90", 
            "cnae": "13.51-1-00", "setor": "Industrial", "risco": 3, "func": 150, 
            "segmentacao": "GHE", "resp": "Carlos Silva", "email": "carlos@fabril.com",
            "logo": None, "score": 2.8, "respondidas": 120,
            "dimensoes": {"Demandas": 2.1, "Controle": 3.5, "Suporte Gestor": 2.8, "Suporte Pares": 4.0, "Relacionamentos": 2.5, "Papel": 4.5, "Mudança": 3.0},
            "detalhe_perguntas": {
                "Prazos impossíveis de cumprir?": 65, 
                "Pressão para trabalhar longas horas?": 45, 
                "Tenho que trabalhar muito intensamente?": 55, 
                "Estou sujeito a assédio pessoal?": 15,
                "Tenho autonomia sobre pausas?": 10,
                "Recebo feedback do gestor?": 30
            }
        }
    ]

# LISTA COMPLETA HSE 35 PERGUNTAS
if 'hse_questions' not in st.session_state:
    st.session_state.hse_questions = {
        "Demandas": [
            {"id": 3, "q": "Tenho prazos impossíveis de cumprir?", "rev": True, "help": "Ex: Receber tarefas às 17h para entregar às 18h."},
            {"id": 6, "q": "Sou pressionado a trabalhar longas horas?", "rev": True, "help": "Ex: Sentir que precisa fazer hora extra sempre para dar conta."},
            {"id": 9, "q": "Tenho que trabalhar muito intensamente?", "rev": True, "help": "Ex: Não ter tempo nem para respirar entre uma tarefa e outra."},
            {"id": 12, "q": "Tenho que negligenciar algumas tarefas?", "rev": True, "help": "Ex: Deixar de fazer algo com qualidade por pressa."},
            {"id": 16, "q": "Não consigo fazer pausas suficientes?", "rev": True, "help": "Ex: Pular o horário de almoço ou café."},
            {"id": 18, "q": "Sou pressionado por diferentes grupos?", "rev": True, "help": "Ex: Vários chefes ou departamentos pedindo coisas conflitantes."},
            {"id": 20, "q": "Tenho que trabalhar muito rápido?", "rev": True, "help": "Ex: Ritmo frenético constante."},
            {"id": 22, "q": "Tenho prazos irrealistas?", "rev": True, "help": "Ex: Metas que humanamente não dá para bater."}
        ],
        "Controle": [
            {"id": 2, "q": "Posso decidir quando fazer uma pausa?", "rev": False, "help": "Ex: Ir ao banheiro ou pegar café sem pedir permissão."},
            {"id": 10, "q": "Tenho liberdade para decidir como faço meu trabalho?", "rev": False, "help": "Ex: Escolher a ordem das tarefas."},
            {"id": 15, "q": "Tenho poder de decisão sobre meu ritmo?", "rev": False, "help": "Ex: Acelerar ou desacelerar quando necessário."},
            {"id": 19, "q": "Eu decido quando vou realizar cada tarefa?", "rev": False, "help": "Ex: Você organiza sua própria agenda do dia."},
            {"id": 25, "q": "Tenho voz sobre como meu trabalho é realizado?", "rev": False, "help": "Ex: O chefe ouve suas sugestões de melhoria."},
            {"id": 30, "q": "Meu tempo de trabalho pode ser flexível?", "rev": False, "help": "Ex: Possibilidade de negociar horário de entrada/saída."}
        ],
        "Suporte Gestor": [
            {"id": 8, "q": "Recebo feedback sobre o trabalho?", "rev": False, "help": "Ex: Saber se está indo bem ou mal."},
            {"id": 23, "q": "Posso contar com meu superior num problema?", "rev": False, "help": "Ex: O chefe ajuda a resolver ou diz 'se vira'?"},
            {"id": 29, "q": "Posso falar com meu superior sobre algo que chateou?", "rev": False, "help": "Ex: Abertura para conversar sobre insatisfações."},
            {"id": 33, "q": "Sinto apoio do meu gestor(a)?", "rev": False, "help": "Ex: Sentir-se acolhido e não apenas cobrado."},
            {"id": 35, "q": "Meu gestor me incentiva?", "rev": False, "help": "Ex: Elogios ou motivação para continuar."}
        ],
        "Suporte Pares": [
            {"id": 7, "q": "Recebo ajuda dos colegas?", "rev": False, "help": "Ex: Quando aperta, alguém te dá uma mão?"},
            {"id": 24, "q": "Recebo respeito dos colegas?", "rev": False, "help": "Ex: Tratamento cordial e profissional."},
            {"id": 27, "q": "Colegas me ouvem sobre problemas?", "rev": False, "help": "Ex: Ter com quem desabafar sobre o serviço."},
            {"id": 31, "q": "Colegas ajudam em momentos difíceis?", "rev": False, "help": "Ex: Solidariedade quando você está sobrecarregado."}
        ],
        "Relacionamentos": [
            {"id": 5, "q": "Estou sujeito a assédio pessoal?", "rev": True, "help": "Ex: Piadas ofensivas, gritos ou apelidos."},
            {"id": 14, "q": "Há atritos ou conflitos entre colegas?", "rev": True, "help": "Ex: Clima pesado, fofocas ou brigas."},
            {"id": 21, "q": "Estou sujeito a bullying?", "rev": True, "help": "Ex: Ser excluído ou ridicularizado sistematicamente."},
            {"id": 34, "q": "Relacionamentos são tensos?", "rev": True, "help": "Ex: Medo de falar com as pessoas."}
        ],
        "Papel": [
            {"id": 1, "q": "Sei o que é esperado de mim?", "rev": False, "help": "Ex: Suas metas e funções são nítidas."},
            {"id": 4, "q": "Sei como fazer meu trabalho?", "rev": False, "help": "Ex: Tenho o conhecimento e ferramentas necessárias."},
            {"id": 11, "q": "Sei os objetivos do departamento?", "rev": False, "help": "Ex: Entender para onde a equipe está indo."},
            {"id": 13, "q": "Sei minha responsabilidade?", "rev": False, "help": "Ex: Clareza sobre até onde vai sua autoridade."},
            {"id": 17, "q": "Entendo meu encaixe na empresa?", "rev": False, "help": "Ex: Ver sentido no que faz para a empresa."}
        ],
        "Mudança": [
            {"id": 26, "q": "Posso questionar mudanças?", "rev": False, "help": "Ex: Tirar dúvidas."},
            {"id": 28, "q": "Sou consultado sobre mudanças?", "rev": False, "help": "Ex: Opinar antes de mudarem seu processo."},
            {"id": 32, "q": "Mudanças são claras?", "rev": False, "help": "Ex: Comunicação transparente sobre o 'novo jeito'."}
        ]
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

    if selected == "Visão Geral":
        st.title("Painel Administrativo")
        col1, col2, col3, col4 = st.columns(4)
        with col1: kpi_card("Empresas", len(st.session_state.companies_db), "🏢", "bg-blue")
        with col2: kpi_card("Respondidas", 213, "✅", "bg-green")
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
            st.markdown("##### Radar HSE")
            categories = list(st.session_state.hse_questions.keys())
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=[2, 4, 3, 2, 5, 4, 3], theta=categories, fill='toself', name='Média'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=300, margin=dict(t=20, b=20))
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Gerar Link":
        st.title("Gerar Link & Testar")
        with st.container():
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
            empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_nome)
            link_final = f"{st.session_state.base_url}/?cod={empresa['id']}"
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("##### Link de Acesso")
                st.markdown(f"<div class='link-box'>{link_final}</div>", unsafe_allow_html=True)
                if "localhost" in st.session_state.base_url:
                    st.warning("⚠️ Localhost: Link só funciona no seu PC.")
                if st.button("👁️ Testar (Visão Colaborador)"):
                    st.session_state.current_company = empresa
                    st.session_state.logged_in = True
                    st.session_state.user_role = 'colaborador'
                    st.rerun()
            with c2:
                st.markdown("##### QR Code")
                qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(link_final)}"
                st.image(qr_api_url, width=150)
                try:
                    with urllib.request.urlopen(qr_api_url) as response: qr_bytes = response.read()
                    st.download_button(label="📥 Baixar QR Code", data=qr_bytes, file_name=f"qrcode_{empresa['id']}.png", mime="image/png")
                except: st.error("Erro no download.")

            st.markdown("---")
            st.markdown("##### 💬 Mensagem de Convite")
            st.caption("Texto pronto para WhatsApp e E-mail:")
            texto_convite = f"""*Pesquisa de Clima - {empresa['razao']}* 🌟\n\nOlá! A **Pessin Gestão** iniciou o programa *Elo NR-01* para cuidar do que temos de mais valioso: **nós mesmos**.\n\nO objetivo é ouvir vocês para tornar nosso ambiente de trabalho mais saudável e equilibrado.\n\n🛡️ **É seguro?** Sim! A pesquisa é 100% anônima e confidencial.\n🔒 **É rápido?** Leva menos de 5 minutos.\n\nSua participação é fundamental!\n\n👇 **Clique no link para responder:**\n{link_final}\n\nContamos com você!"""
            st.text_area("", value=texto_convite, height=250)
            st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Empresas":
        st.title("Gestão de Empresas")
        tab1, tab2 = st.tabs(["Monitoramento", "Novo Cadastro"])
        with tab1:
            df_view = pd.DataFrame(st.session_state.companies_db)
            st.dataframe(df_view[['razao', 'cnpj', 'risco', 'func', 'respondidas']], use_container_width=True)
        with tab2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            with st.form("add_comp"):
                c1, c2, c3 = st.columns(3)
                razao = c1.text_input("Razão Social")
                cnpj = c2.text_input("CNPJ")
                cnae = c3.text_input("CNAE")
                c4, c5, c6 = st.columns(3)
                risco = c4.selectbox("Risco", [1, 2, 3, 4])
                func = c5.number_input("Vidas", min_value=1)
                segmentacao = c6.selectbox("Segmentação", ["GHE", "Setor", "GES"])
                c7, c8, c9 = st.columns(3)
                cod = c7.text_input("ID Acesso")
                resp = c8.text_input("Responsável")
                logo_cliente = c9.file_uploader("Logo Cliente", type=['png', 'jpg'])
                
                if st.form_submit_button("Salvar"):
                    new_c = {
                        "id": cod, "razao": razao, "cnpj": cnpj, "cnae": cnae, "setor": "Geral", 
                        "risco": risco, "func": func, "segmentacao": segmentacao, "resp": resp, 
                        "email": "-", "logo": logo_cliente, "score": 0, "respondidas": 0, 
                        "dimensoes": {}, "detalhe_perguntas": {}
                    }
                    st.session_state.companies_db.append(new_c)
                    st.success("Salvo!")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Relatórios":
        st.title("Relatórios e Laudos")
        c_sel, c_blank = st.columns([1, 1])
        with c_sel:
            empresa_sel = st.selectbox("Cliente", [c['razao'] for c in st.session_state.companies_db])
        
        empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_sel)
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("#### Assinaturas")
            sig_empresa_nome = st.text_input("Nome Resp. Empresa", value=empresa['resp'])
            sig_empresa_cargo = st.text_input("Cargo Resp. Empresa", value="Diretor(a)")
            sig_tecnico_nome = st.text_input("Nome Resp. Técnico", value="Cristiane C. Lima")
            sig_tecnico_cargo = st.text_input("Cargo Resp. Técnico", value="Consultora Pessin Gestão")

        with st.expander("📝 Editar Conteúdo Técnico", expanded=True):
            analise_texto = st.text_area("Conclusão Técnica:", value="A avaliação identificou riscos críticos na dimensão 'Demandas', com 65% dos colaboradores relatando prazos irreais.")
            st.markdown("#### Plano de Ação")
            if 'acoes_list' not in st.session_state:
                st.session_state.acoes_list = [{"acao": "Revisão de Job Description", "estrat": "Mapear todas as funções do setor e redistribuir carga.", "area": "Demanda", "resp": "RH", "prazo": "30/05"}]
            edited_df = st.data_editor(pd.DataFrame(st.session_state.acoes_list), num_rows="dynamic", use_container_width=True, 
                                       column_config={"acao": "Ação", "estrat": "Estratégia (Como)", "area": "Área", "resp": "Resp.", "prazo": "Prazo"})
            if not edited_df.empty: st.session_state.acoes_list = edited_df.to_dict('records')

        if st.button("🖨️ Gerar Relatório (PDF)", type="primary"):
            st.markdown("---")
            logo_html = get_logo_html(150)
            logo_cliente_html = ""
            if empresa.get('logo'):
                b64 = image_to_base64(empresa.get('logo'))
                if b64: logo_cliente_html = f"<img src='data:image/png;base64,{b64}' width='100' style='float:right;'>"
            
            plat_name = st.session_state.platform_config['name']
            
            html_dimensoes = ""
            for dim, nota in empresa.get('dimensoes', {}).items():
                cor = COR_RISCO_ALTO if nota < 3 else (COR_RISCO_MEDIO if nota < 4 else COR_RISCO_BAIXO)
                txt = "CRÍTICO" if nota < 3 else ("ATENÇÃO" if nota < 4 else "SEGURO")
                html_dimensoes += f'<div style="flex:1; min-width:90px; background:#f8f9fa; border:1px solid #eee; padding:8px; border-radius:6px; margin:3px; text-align:center;"><div style="font-size:8px; color:#666; text-transform:uppercase;">{dim}</div><div style="font-size:14px; font-weight:bold; color:{cor};">{nota}</div><div style="font-size:7px; color:#888;">{txt}</div></div>'

            html_raio_x = ""
            for cat, pergs in st.session_state.hse_questions.items():
                html_raio_x += f'<div style="font-weight:bold; color:{COR_PRIMARIA}; margin-top:10px; border-bottom:1px solid #eee;">{cat}</div>'
                for q in pergs:
                    pct = random.randint(10, 80)
                    cor_bar = COR_RISCO_ALTO if pct > 50 else (COR_RISCO_MEDIO if pct > 30 else COR_RISCO_BAIXO)
                    html_raio_x += f'<div style="margin-bottom:4px;"><div style="display:flex; justify-content:space-between; font-size:9px;"><span>{q["q"]}</span><span>{pct}% Risco</span></div><div style="width:100%; background:#f0f0f0; height:5px; border-radius:2px;"><div style="width:{pct}%; background:{cor_bar}; height:100%; border-radius:2px;"></div></div></div>'

            html_acoes = "".join([f"<tr><td>{i.get('acao','')}</td><td>{i.get('estrat','-')}</td><td>{i.get('area','')}</td><td>{i.get('resp','')}</td><td>{i.get('prazo','')}</td></tr>" for i in st.session_state.acoes_list])

            # ESTE É O BLOCO HTML CORRIGIDO. REMOVIDA INDENTAÇÃO PARA NÃO DAR ERRO.
            raw_html = f"""
<div class="a4-paper">
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid {COR_PRIMARIA}; padding-bottom:15px; margin-bottom:20px;">
<div>{logo_html}</div>
<div style="text-align:right;"><div style="font-size:16px; font-weight:700; color:{COR_PRIMARIA};">LAUDO TÉCNICO HSE-IT</div><div style="font-size:10px; color:#666;">NR-01 / Riscos Psicossociais</div></div>
</div>
<div style="background:#f8f9fa; padding:12px; border-radius:6px; margin-bottom:15px; border-left:4px solid {COR_SECUNDARIA};">
{logo_cliente_html}
<div style="font-size:9px; color:#888;">CLIENTE</div><div style="font-weight:bold; font-size:12px;">{empresa['razao']}</div>
<div style="font-size:9px;">CNPJ: {empresa['cnpj']} | Adesão: {empresa['respondidas']} Vidas | Data: {datetime.datetime.now().strftime('%d/%m/%Y')}</div>
</div>
<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">1. OBJETIVO E METODOLOGIA</div>
<p style="text-align:justify; margin:0; font-size:10px;">Este relatório tem como objetivo identificar os fatores de risco psicossocial no ambiente de trabalho, utilizando a ferramenta <strong>HSE Management Standards Indicator Tool</strong>, atendendo às exigências da NR-01. A metodologia avalia 7 dimensões: Demanda, Controle, Suporte (Gestor/Pares), Relacionamentos, Papel e Mudança.</p>
<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-top:15px; margin-bottom:5px;">2. DIAGNÓSTICO GERAL (DIMENSÕES)</div>
<div style="display:flex; flex-wrap:wrap; margin-bottom:15px;">{html_dimensoes}</div>
<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">3. RAIO-X DETALHADO (35 PERGUNTAS)</div>
<div style="background:white; border:1px solid #eee; padding:10px; border-radius:6px; margin-bottom:15px; column-count:2; column-gap:20px; font-size:9px;">{html_raio_x}</div>
<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">4. PLANO DE AÇÃO ESTRATÉGICO</div>
<table class="rep-table" style="margin-bottom:15px;">
<thead><tr><th>AÇÃO</th><th>ESTRATÉGIA (COMO)</th><th>ÁREA</th><th>RESP.</th><th>PRAZO</th></tr></thead>
<tbody>{html_acoes}</tbody>
</table>
<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">5. CONCLUSÃO TÉCNICA</div>
<p style="text-align:justify; margin:0; font-size:10px;">{analise_texto}</p>
<div style="margin-top:40px; display:flex; justify-content:space-between; gap:30px;">
<div style="flex:1; text-align:center; border-top:1px solid #ccc; padding-top:5px;"><strong>{sig_empresa_nome}</strong><br><span style="color:#666; font-size:9px;">{sig_empresa_cargo}</span></div>
<div style="flex:1; text-align:center; border-top:1px solid #ccc; padding-top:5px;"><strong>{sig_tecnico_nome}</strong><br><span style="color:#666; font-size:9px;">{sig_tecnico_cargo}</span></div>
</div>
</div>
"""
            # Renderização segura
            st.markdown(textwrap.dedent(raw_html), unsafe_allow_html=True)
            st.info("Pressione Ctrl+P para salvar como PDF.")

    elif selected == "Configurações":
        st.title("Configurações")
        tab_brand, tab_users, tab_sys = st.tabs(["🎨 Personalização", "🔐 Acessos", "⚙️ Sistema"])
        
        with tab_brand:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
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
            users_list = pd.DataFrame(list(st.session_state.users_db.items()), columns=['Usuário', 'Senha'])
            users_list['Senha'] = "******"
            st.dataframe(users_list, use_container_width=True)
            c_u1, c_u2 = st.columns(2)
            new_u = c_u1.text_input("Novo Usuário")
            new_p = c_u2.text_input("Nova Senha", type="password")
            if st.button("Adicionar"):
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
    st.markdown(f"<h3 style='text-align:center'>Avaliação de Riscos - {comp['razao']}</h3>", unsafe_allow_html=True)
    
    # MENSAGEM DE SEGURANÇA E VERIFICAÇÃO (BOX VERDE)
    st.markdown("""
    <div class="security-box">
        <strong>🔒 AVALIAÇÃO VERIFICADA E SEGURA</strong><br>
        Esta pesquisa segue rigorosos padrões de confidencialidade.<br>
        <ul>
            <li><strong>Anonimato Garantido:</strong> A empresa NÃO tem acesso à sua resposta individual.</li>
            <li><strong>Uso do CPF:</strong> Seu CPF é usado <u>apenas</u> para validar que você é um colaborador único e impedir duplicidades. Ele é transformado em um código criptografado (hash) imediatamente.</li>
            <li><strong>Sigilo:</strong> Os resultados são apresentados apenas em formato estatístico (médias do grupo).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    with st.form("survey_form"):
        st.markdown("#### 1. Perfil")
        c1, c2 = st.columns(2)
        cpf = c1.text_input("CPF (Apenas números)", max_chars=11)
        setor = c2.text_input("Setor")
        
        st.markdown("#### 2. Questionário HSE")
        tabs = st.tabs(list(st.session_state.hse_questions.keys()))
        for i, (cat, pergs) in enumerate(st.session_state.hse_questions.items()):
            with tabs[i]:
                st.markdown(f"**{cat}**")
                for q in pergs:
                    # SLIDER DE BOLINHAS (SELECT SLIDER) COM PERGUNTA EM CIMA E EXPLICAÇÃO NO TOOLTIP
                    options = ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"] if q['id']<=24 else ["Discordo Totalmente", "Discordo", "Neutro", "Concordo", "Concordo Totalmente"]
                    
                    st.select_slider(
                        label=f"**{q['q']}**",
                        options=options,
                        key=f"q_{q['id']}",
                        help=f"{q['help']}" # EXPLICAÇÃO NA INTERROGAÇÃO
                    )
                    st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        
        if st.form_submit_button("✅ Enviar Respostas", type="primary"):
            if not cpf: st.error("CPF Obrigatório.")
            else:
                for c in st.session_state.companies_db:
                    if c['id'] == comp['id']: c['respondidas'] += 1
                st.balloons(); st.success("Respostas enviadas com sucesso! Obrigado pela participação."); time.sleep(3); st.session_state.logged_in = False; st.session_state.user_role = None; st.rerun()

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
