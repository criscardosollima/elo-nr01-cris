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
        box-shadow: 0 0 20px rgba(0,0,0,0.1); color: #333; font-family: 'Arial', sans-serif; font-size: 12px; line-height: 1.5;
    }}
    .report-title {{ font-size: 18px; color: {COR_PRIMARIA}; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }}
    .report-subtitle {{ font-size: 12px; color: #666; margin-bottom: 20px; border-bottom: 2px solid {COR_PRIMARIA}; padding-bottom: 10px; }}
    .section-title {{ 
        font-size: 14px; font-weight: bold; color: {COR_PRIMARIA}; 
        margin-top: 20px; margin-bottom: 10px; border-left: 4px solid {COR_SECUNDARIA}; padding-left: 10px; 
    }}
    .hse-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px; }}
    .hse-table th {{ background-color: #f0f0f0; border: 1px solid #ddd; padding: 6px; text-align: left; font-weight: bold; }}
    .hse-table td {{ border: 1px solid #ddd; padding: 6px; }}
    .risk-high {{ background-color: #ffebee; color: #c62828; font-weight: bold; text-align: center; }}
    .risk-med {{ background-color: #fff3e0; color: #ef6c00; font-weight: bold; text-align: center; }}
    .risk-low {{ background-color: #e8f5e9; color: #2e7d32; font-weight: bold; text-align: center; }}
    .link-area {{ background-color: #f8f9fa; border: 1px dashed #dee2e6; padding: 15px; border-radius: 8px; font-family: monospace; color: #2c3e50; font-weight: bold; word-break: break-all; }}
    
    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 0; width: 100%; }}
        .stApp {{ background-color: white; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS INTELIGENTES (MOCKUP EXPANDIDO) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": "admin", "cris": "123"}

if 'companies_db' not in st.session_state:
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
            "respondidas": 120,
            # Notas detalhadas por dimensão HSE (1 a 5)
            "dimensoes": {
                "Demanda": 2.1,
                "Controle": 3.5,
                "Suporte Gestor": 2.8,
                "Suporte Pares": 4.0,
                "Relacionamentos": 2.5,
                "Papel": 4.5,
                "Mudança": 3.0
            }
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
            "respondidas": 15,
            "dimensoes": {
                "Demanda": 3.8,
                "Controle": 4.5,
                "Suporte Gestor": 4.2,
                "Suporte Pares": 4.0,
                "Relacionamentos": 4.1,
                "Papel": 4.5,
                "Mudança": 3.9
            }
        },
    ]

if 'base_url' not in st.session_state: st.session_state.base_url = "http://localhost:8501" 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- 4. FUNÇÕES DE INTELIGÊNCIA HSE ---
def gerar_analise_automatica(dimensoes):
    """Gera textos interpretativos baseados nas notas"""
    analises = {}
    
    # Demanda
    nota = dimensoes.get("Demanda", 0)
    if nota < 3.0:
        analises['demanda'] = f"A dimensão Demanda apresenta Risco Alto (Nota: {nota}). Observa-se sobrecarga de trabalho, ritmo acelerado e prazos conflitantes, exigindo intervenção imediata para prevenir burnout."
    elif nota < 4.0:
        analises['demanda'] = f"A dimensão Demanda está em nível de Atenção (Nota: {nota}). Há picos de trabalho que podem ser melhor gerenciados."
    else:
        analises['demanda'] = f"A Demanda está equilibrada (Nota: {nota}), indicando que o volume de trabalho é compatível com o tempo disponível."

    # Controle
    nota = dimensoes.get("Controle", 0)
    if nota < 3.0:
        analises['controle'] = "Baixo nível de autonomia. Colaboradores sentem que têm pouca voz sobre como realizam suas tarefas."
    else:
        analises['controle'] = "Bom nível de autonomia. Colaboradores conseguem gerenciar suas pausas e métodos de trabalho."

    # Relacionamentos
    nota = dimensoes.get("Relacionamentos", 0)
    if nota < 3.0:
        analises['relacionamentos'] = "Alerta Crítico: Indicadores de conflitos interpessoais ou percepção de assédio moral. Requer ação do Compliance/RH."
    else:
        analises['relacionamentos'] = "Ambiente social saudável, com baixo índice de atritos reportados."

    return analises

def sugerir_acoes(dimensoes):
    """Gera lista de ações para o plano baseada nos riscos"""
    acoes = []
    
    if dimensoes.get("Demanda", 5) < 3.0:
        acoes.append({"acao": "Revisão e redistribuição da carga de trabalho", "area": "Demanda", "resp": "Gestão/RH", "prazo": "Imediato"})
        acoes.append({"acao": "Implementação de pausas ativas obrigatórias", "area": "Demanda", "resp": "SST", "prazo": "30 dias"})
    
    if dimensoes.get("Controle", 5) < 3.5:
        acoes.append({"acao": "Programa de Job Crafting (Autonomia na tarefa)", "area": "Controle", "resp": "RH", "prazo": "60 dias"})
    
    if dimensoes.get("Suporte Gestor", 5) < 3.5:
        acoes.append({"acao": "Treinamento de Liderança Humanizada", "area": "Suporte", "resp": "T&D", "prazo": "45 dias"})
    
    if dimensoes.get("Relacionamentos", 5) < 3.0:
        acoes.append({"acao": "Roda de conversa sobre Assédio e Respeito", "area": "Relacionamentos", "resp": "Compliance", "prazo": "Imediato"})
        acoes.append({"acao": "Divulgação do Canal de Ética/Denúncia", "area": "Relacionamentos", "resp": "Comunicação", "prazo": "15 dias"})
        
    return acoes

# --- 5. FUNÇÕES AUXILIARES VISUAIS ---
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

def logout(): st.session_state.logged_in = False; st.rerun()

def kpi_card(title, value, icon, color_class):
    st.markdown(f"""<div class="kpi-card"><div class="kpi-top"><div class="kpi-icon-box {color_class}">{icon}</div></div><div><div class="kpi-value">{value}</div><div class="kpi-title">{title}</div></div></div>""", unsafe_allow_html=True)

# --- 6. TELAS DO SISTEMA ---

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
                    st.session_state.logged_in = True; st.session_state.user_role = 'admin'; st.rerun()
                else: st.error("Dados incorretos.")
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
                if "localhost" in st.session_state.base_url: st.warning("⚠️ Você está em Localhost.")
                st.markdown(f"**Adesão:** {empresa['respondidas']}/{empresa['func']}")
                prog = empresa['respondidas']/empresa['func'] if empresa['func'] > 0 else 0
                st.markdown(f"""<div style="background:#eee;height:8px;border-radius:4px;"><div style="width:{prog*100}%;background:{COR_SECUNDARIA};height:100%;border-radius:4px;"></div></div>""", unsafe_allow_html=True)
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
            df_view = df_view[['razao', 'cnpj', 'risco', 'segmentacao', 'func', 'respondidas']]
            df_view.columns = ['Empresa', 'CNPJ', 'Risco', 'Tipo Segmentação', 'Vidas', 'Resp.']
            st.dataframe(df_view, use_container_width=True)
        with tab2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            with st.form("add_comp"):
                c1, c2, c3 = st.columns(3)
                razao = c1.text_input("Razão Social")
                cnpj = c2.text_input("CNPJ")
                cnae = c3.text_input("CNAE Principal")
                c4, c5, c6 = st.columns(3)
                risco = c4.selectbox("Grau de Risco", [1, 2, 3, 4])
                func = c5.number_input("Nº Vidas", min_value=1)
                segmentacao = c6.selectbox("Segmentação", ["Setor", "GHE", "GES", "Ambiente"])
                c7, c8, c9 = st.columns(3)
                cod = c7.text_input("Código ID")
                resp = c8.text_input("Responsável")
                logo_file = st.file_uploader("Logo Empresa", type=['png', 'jpg'])
                if st.form_submit_button("Salvar"):
                    new_c = {"id": cod, "razao": razao, "cnpj": cnpj, "cnae": cnae, "setor": "Geral", "risco": risco, "func": func, "segmentacao": segmentacao, "resp": resp, "email": "-", "logo": logo_file, "score": 0, "respondidas": 0, "dimensoes": {"Demanda":3,"Controle":3}}
                    st.session_state.companies_db.append(new_c)
                    st.success("Salvo!")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 4. RELATÓRIOS (INTELIGÊNCIA AUTOMATIZADA) ---
    elif selected == "Relatórios":
        st.title("Relatórios e Laudos")
        
        c_sel, c_blank = st.columns([1, 1])
        with c_sel:
            empresa_sel = st.selectbox("Cliente", [c['razao'] for c in st.session_state.companies_db])
        
        empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_sel)
        
        # 1. PROCESSAMENTO DE INTELIGÊNCIA
        # Se as notas existirem, gera a análise automática
        dimensoes = empresa.get('dimensoes', {})
        textos_auto = gerar_analise_automatica(dimensoes)
        acoes_auto = sugerir_acoes(dimensoes)
        
        # --- INPUTS EDITÁVEIS (O Humano revisa o Robô) ---
        with st.expander("📝 Editar Análise e Plano de Ação (Pré-Relatório)", expanded=True):
            col_a, col_b = st.columns(2)
            setores_avaliados = col_a.text_input("Setores Avaliados:", "Administrativo, Operacional")
            resp_tecnico = col_b.text_input("Responsável Técnico / CRP:", "Cristiane C. Lima / CRP 00/0000")
            
            st.markdown("#### 4. Análise dos Riscos (Editável)")
            st.info("O sistema gerou estas interpretações automaticamente. Edite conforme sua percepção.")
            
            analise_demanda = st.text_area("Análise de Demanda:", value=textos_auto.get('demanda', ''), height=100)
            analise_relacionamento = st.text_area("Análise de Relacionamentos:", value=textos_auto.get('relacionamentos', ''), height=100)
            analise_controle = st.text_area("Análise de Controle:", value=textos_auto.get('controle', ''), height=100)
            
            st.markdown("#### 5. Plano de Ação (Sugestões Automáticas)")
            st.caption("Abaixo estão as sugestões baseadas no diagnóstico. Adicione ou remova itens.")
            
            # Inicializa a lista de ações na sessão se ainda não existir ou se mudou a empresa
            if 'acoes_list' not in st.session_state or st.session_state.get('last_company') != empresa['id']:
                st.session_state.acoes_list = acoes_auto
                st.session_state.last_company = empresa['id']
            
            # Tabela de Edição das Ações
            acoes_df = pd.DataFrame(st.session_state.acoes_list)
            edited_df = st.data_editor(acoes_df, num_rows="dynamic", use_container_width=True, column_config={
                "acao": st.column_config.TextColumn("Ação Recomendada"),
                "area": st.column_config.SelectboxColumn("Área HSE", options=["Demanda", "Controle", "Suporte", "Relacionamentos"]),
                "resp": st.column_config.TextColumn("Responsável"),
                "prazo": st.column_config.TextColumn("Prazo")
            })
            
            # Atualiza a lista com o que foi editado na tabela
            if not edited_df.empty:
                st.session_state.acoes_list = edited_df.to_dict('records')

        # --- GERAÇÃO DO HTML (A4) ---
        if st.button("🖨️ Gerar Relatório HSE-IT (PDF)", type="primary"):
            st.markdown("---")
            logo_html = get_logo_html(150)
            if empresa.get('logo'):
                b64 = image_to_base64(empresa.get('logo'))
                if b64: logo_html = f"<img src='data:image/png;base64,{b64}' width='150'>"
            
            # Tabela de Resultados (Dashboard no PDF)
            rows_res = ""
            for dim, nota in dimensoes.items():
                risco = "Alto" if nota < 3 else ("Médio" if nota < 4 else "Baixo")
                classe = "risk-high" if nota < 3 else ("risk-med" if nota < 4 else "risk-low")
                foco = "Intervenção Imediata" if nota < 3 else "Monitorar"
                rows_res += f"<tr><td>{dim}</td><td>{nota}</td><td class='{classe}'>{risco}</td><td>{foco}</td></tr>"
            
            tabela_resultados = f"""<table class="hse-table"><tr><th>Dimensão</th><th>Nota</th><th>Risco</th><th>Foco</th></tr>{rows_res}</table>"""
            
            # Tabela de Ações (Vinda da edição do usuário)
            rows_acoes = ""
            for item in st.session_state.acoes_list:
                # Proteção caso a tabela editada venha com chaves vazias
                acao = item.get('acao', '')
                area = item.get('area', '')
                resp = item.get('resp', '')
                prazo = item.get('prazo', '')
                if acao:
                    rows_acoes += f"<tr><td>{acao}</td><td>{area}</td><td>{resp}</td><td>{prazo}</td></tr>"
            
            tabela_acoes = f"""<table class="hse-table"><tr><th>Ação</th><th>Área</th><th>Resp.</th><th>Prazo</th></tr>{rows_acoes}</table>"""

            html_content = textwrap.dedent(f"""
            <div class="a4-paper">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>{logo_html}</div>
                    <div style="text-align:right;">
                        <div class="report-title">RELATÓRIO DE AVALIAÇÃO DE RISCOS PSICOSSOCIAIS</div>
                        <div style="font-size:10px;">Metodologia HSE-IT</div>
                    </div>
                </div>
                <div class="report-subtitle">Ref: NR-01 / PGR</div>
                
                <table class="hse-table" style="margin-bottom:20px;">
                    <tr><td style="background:#f9f9f9;"><strong>Empresa:</strong> {empresa['razao']}</td><td style="background:#f9f9f9;"><strong>Data:</strong> {datetime.datetime.now().strftime('%d/%m/%Y')}</td></tr>
                    <tr><td><strong>Resp. Técnico:</strong> {resp_tecnico}</td><td><strong>Setores:</strong> {setores_avaliados}</td></tr>
                </table>

                <div class="section-title">1. Introdução e Metodologia</div>
                <p>Este relatório utiliza a ferramenta HSE Indicator Tool para mapear riscos psicossociais, atendendo à NR-01. Foram avaliadas 7 dimensões críticas para a saúde mental no trabalho.</p>

                <div class="section-title">2. Dashboard de Resultados</div>
                <p>Abaixo, a classificação de risco por dimensão baseada nas respostas coletadas:</p>
                {tabela_resultados}

                <div class="section-title">3. Análise Detalhada dos Riscos</div>
                <p><strong>Demanda:</strong> {analise_demanda}</p>
                <p><strong>Controle:</strong> {analise_controle}</p>
                <p><strong>Relacionamentos:</strong> {analise_relacionamento}</p>

                <div class="section-title">4. Plano de Ação (Gestão de Riscos)</div>
                <p>Medidas preventivas e corretivas definidas:</p>
                {tabela_acoes}

                <div class="section-title">5. Conclusão</div>
                <p>O diagnóstico aponta a necessidade de foco nas áreas classificadas como Alto Risco. A implementação destas ações visa a melhoria do clima e conformidade legal.</p>

                <br><br>
                <div style="display:flex; justify-content:space-between; margin-top:30px;">
                    <div style="text-align:center; width:45%; border-top:1px solid #000; padding-top:5px;"><strong>{empresa['resp']}</strong><br>Empresa</div>
                    <div style="text-align:center; width:45%; border-top:1px solid #000; padding-top:5px;"><strong>{resp_tecnico.split('/')[0]}</strong><br>Consultora</div>
                </div>
            </div>
            """)
            st.markdown(html_content, unsafe_allow_html=True)
            st.info("Pressione Ctrl+P para salvar como PDF.")

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
            new_url = st.text_input("URL Base do Sistema", value=st.session_state.base_url)
            if st.button("Atualizar URL"): st.session_state.base_url = new_url; st.success("OK")
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
