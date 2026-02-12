import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import base64
import urllib.parse
from streamlit_option_menu import option_menu
import random

# --- 1. CONFIGURAÇÃO GERAL ---
NOME_SISTEMA = "Elo NR-01"
COR_PRIMARIA = "#2c3e50"  # Azul Escuro Profissional
COR_SECUNDARIA = "#1abc9c" # Verde "Safe"
COR_CARD_BG = "#ffffff"
COR_FUNDO = "#f4f6f9"

st.set_page_config(
    page_title=f"{NOME_SISTEMA} | Pessin Gestão",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PROFISSIONAL (Estilo Medseg) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    .stApp {{ background-color: {COR_FUNDO}; font-family: 'Inter', sans-serif; }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{ background-color: #ffffff; border-right: 1px solid #e0e0e0; }}
    
    /* Cards de KPI (Topo) */
    .kpi-card {{
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03); border: 1px solid #f0f0f0;
        margin-bottom: 15px; transition: all 0.3s ease;
    }}
    .kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
    .kpi-title {{ font-size: 14px; color: #7f8c8d; font-weight: 500; margin-bottom: 5px; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; color: {COR_PRIMARIA}; }}
    .kpi-icon {{ float: right; font-size: 24px; padding: 10px; border-radius: 10px; }}
    
    /* Cores dos ícones */
    .bg-blue {{ background-color: #e3f2fd; color: #1976d2; }}
    .bg-green {{ background-color: #e8f5e9; color: #388e3c; }}
    .bg-orange {{ background-color: #fff3e0; color: #f57c00; }}
    .bg-purple {{ background-color: #f3e5f5; color: #7b1fa2; }}
    .bg-red {{ background-color: #ffebee; color: #d32f2f; }}

    /* Gráficos Container */
    .chart-container {{
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03); border: 1px solid #f0f0f0; height: 100%;
    }}

    /* Barra de Progresso */
    .progress-wrapper {{ background-color: #eee; border-radius: 10px; height: 10px; width: 100%; margin-top: 5px; }}
    .progress-fill {{ height: 100%; border-radius: 10px; transition: width 0.5s ease; }}

    /* Estilo do Plano de Ação (Seleção) */
    .action-box {{
        background-color: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
        padding: 15px; margin-bottom: 10px; border-left: 4px solid {COR_SECUNDARIA};
    }}

    /* Relatório A4 */
    .a4-paper {{
        background: white; width: 210mm; min-height: 297mm;
        margin: auto; padding: 40px; box-shadow: 0 0 20px rgba(0,0,0,0.1);
        color: #333; font-family: 'Arial', sans-serif;
    }}
    
    /* Link Area */
    .link-area {{
        background-color: #f8f9fa; border: 1px dashed #dee2e6;
        padding: 15px; border-radius: 8px; font-family: monospace;
        color: #2c3e50; font-weight: bold; word-break: break-all;
    }}
    
    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 0; width: 100%; }}
        .stApp {{ background-color: white; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS E ESTADO ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": "admin", "cris": "123"}

if 'companies_db' not in st.session_state:
    st.session_state.companies_db = [
        {"id": "IND01", "razao": "Indústria Têxtil Fabril", "cnpj": "12.345.678/0001-90", "setor": "Industrial", "risco": 3, "func": 150, "resp": "Carlos Silva", "logo": None, "score": 2.8, "respondidas": 120},
        {"id": "TEC02", "razao": "TechSolutions S.A.", "cnpj": "98.765.432/0001-10", "setor": "Tecnologia", "risco": 1, "func": 50, "resp": "Ana Souza", "logo": None, "score": 4.1, "respondidas": 15},
        {"id": "LOG03", "razao": "Transportadora Rápido", "cnpj": "45.123.456/0001-55", "setor": "Logística", "risco": 4, "func": 80, "resp": "Roberto Dias", "logo": None, "score": 3.2, "respondidas": 78},
    ]

if 'base_url' not in st.session_state: st.session_state.base_url = "http://localhost:8501" 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# --- 4. FUNÇÕES AUXILIARES ---
def render_svg_logo(width=180):
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
    return base64.b64encode(svg.encode("utf-8")).decode("utf-8")

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
        <div class="kpi-icon {color_class}">{icon}</div>
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. TELAS DO SISTEMA ---

def login_screen():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center'><img src='data:image/svg+xml;base64,{render_svg_logo(250)}'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; color:#555;'>Painel Administrativo</h3>", unsafe_allow_html=True)
        
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
        st.markdown(f"<div style='text-align:center; margin-bottom:30px; margin-top:20px;'><img src='data:image/svg+xml;base64,{render_svg_logo(160)}'></div>", unsafe_allow_html=True)
        selected = option_menu(
            menu_title=None,
            options=["Visão Geral", "Gerar Link", "Empresas", "Relatórios", "Configurações"],
            icons=["grid", "link-45deg", "building", "file-text", "gear"],
            default_index=3, # Foco na aba Relatórios para teste
            styles={"nav-link-selected": {"background-color": COR_PRIMARIA}}
        )
        st.markdown("---")
        if st.button("Sair", use_container_width=True): logout()

    # --- 1. VISÃO GERAL ---
    if selected == "Visão Geral":
        st.title("Painel Administrativo")
        st.markdown(f"Bem-vinda, **Cris**")
        
        total_empresas = len(st.session_state.companies_db)
        total_colaboradores = sum(c['func'] for c in st.session_state.companies_db)
        total_respondidas = sum(c['respondidas'] for c in st.session_state.companies_db)
        avaliacoes_restantes = total_colaboradores - total_respondidas
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: kpi_card("Total Empresas", total_empresas, "🏢", "bg-blue")
        with col2: kpi_card("Total Vidas", total_colaboradores, "👥", "bg-purple")
        with col3: kpi_card("Respondidas", total_respondidas, "✅", "bg-green")
        with col4: kpi_card("Pendentes", avaliacoes_restantes, "⏳", "bg-orange")
        with col5: kpi_card("Alertas", "3", "🚨", "bg-red")

        st.markdown("<br>", unsafe_allow_html=True)
        c_chart1, c_chart2 = st.columns([1, 1.5])
        with c_chart1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Distribuição por Setor")
            df = pd.DataFrame(st.session_state.companies_db)
            fig_pie = px.donut(df, names='setor', hole=0.5, color_discrete_sequence=px.colors.qualitative.Prism)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with c_chart2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Evolução - Respostas")
            dates = pd.date_range(start='2025-01-01', periods=6, freq='M')
            vals = [10, 45, 80, 150, 200, total_respondidas]
            df_evo = pd.DataFrame({'Data': dates, 'Respostas': vals})
            fig_area = px.area(df_evo, x='Data', y='Respostas', color_discrete_sequence=[COR_SECUNDARIA])
            fig_area.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig_area, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 2. GERAR LINK ---
    elif selected == "Gerar Link":
        st.title("Gerar Link de Avaliação")
        with st.container():
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            c_sel, c_blank = st.columns([3, 1])
            with c_sel:
                empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
            
            empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_nome)
            link_final = f"{st.session_state.base_url}/?cod={empresa['id']}"
            
            col_dados, col_qr = st.columns([2, 1])
            with col_dados:
                st.markdown("##### Link da Avaliação")
                st.markdown(f"<div class='link-area'>{link_final}</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                b1, b2 = st.columns([1, 1])
                b1.info("Copie o link acima 👆")
                b2.link_button("Abrir Link ↗", link_final)
                st.markdown("---")
                st.markdown(f"**Adesão Atual:** {empresa['respondidas']} de {empresa['func']}")
                progresso = empresa['respondidas'] / empresa['func']
                st.markdown(f"""<div class="progress-wrapper"><div class="progress-fill" style="width: {progresso*100}%; background-color: {COR_SECUNDARIA if progresso > 0.7 else '#f1c40f'};"></div></div>""", unsafe_allow_html=True)

            with col_qr:
                st.markdown("##### QR Code")
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(link_final)}"
                st.image(qr_url, width=180)
                st.caption("Baixar QR Code")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.markdown("##### 💬 Mensagem de Convite")
            texto_base = f"""Olá time {empresa['razao']}! 👋\n\nA **Pessin Gestão** iniciou o programa *Elo NR-01*. Sua participação é o elo que fortalece nossa equipe.\n\n👇 **Clique para responder:**\n{link_final}"""
            st.text_area("Edite a mensagem:", value=texto_base, height=200)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 3. EMPRESAS ---
    elif selected == "Empresas":
        st.title("Empresas & Monitoramento")
        tab1, tab2 = st.tabs(["Monitoramento", "Novo Cadastro"])
        with tab1:
            st.write("Acompanhe em tempo real.")
            header_cols = st.columns([2, 1, 1, 1, 2])
            header_cols[0].write("**Empresa**")
            header_cols[1].write("**Setor**")
            header_cols[2].write("**Total Vidas**")
            header_cols[3].write("**Resp.**")
            header_cols[4].write("**Progresso**")
            st.markdown("---")
            for emp in st.session_state.companies_db:
                cols = st.columns([2, 1, 1, 1, 2])
                cols[0].write(emp['razao'])
                cols[1].write(emp['setor'])
                cols[2].write(str(emp['func']))
                cols[3].write(str(emp['respondidas']))
                cols[4].progress(emp['respondidas'] / emp['func'])
        with tab2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            with st.form("add_comp"):
                c1, c2 = st.columns(2)
                razao = c1.text_input("Razão Social")
                cnpj = c2.text_input("CNPJ")
                c3, c4, c5 = st.columns(3)
                risco = c3.selectbox("Grau de Risco", [1, 2, 3, 4])
                func = c4.number_input("Nº Funcionários", min_value=1)
                cod = c5.text_input("Código ID", placeholder="Ex: CLI-01")
                logo_file = st.file_uploader("Logo da Empresa", type=['png', 'jpg'])
                if st.form_submit_button("Salvar Cadastro"):
                    new_c = {"id": cod, "razao": razao, "cnpj": cnpj, "setor": "Geral", "risco": risco, "func": func, "resp": "A Definir", "logo": logo_file, "score": 0, "respondidas": 0}
                    st.session_state.companies_db.append(new_c)
                    st.success("Salvo com sucesso!")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- 4. RELATÓRIOS (NOVO PLANO DE AÇÃO INTERATIVO) ---
    elif selected == "Relatórios":
        st.title("Relatórios e Laudos")
        
        empresa_sel = st.selectbox("Selecione o Cliente", [c['razao'] for c in st.session_state.companies_db])
        empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_sel)
        
        col_res, col_plan = st.columns([1, 1])
        
        # Área de Diagnóstico (Visualização Rápida)
        with col_res:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Diagnóstico Preliminar")
            st.info(f"Score Atual: **{empresa['score']} / 5.0**")
            
            # Dados Mockados para o exemplo
            fator_critico = "Demandas" if empresa['score'] < 3 else "Controle"
            st.write(f"⚠️ **Fator Crítico:** {fator_critico}")
            st.markdown("</div>", unsafe_allow_html=True)

        # --- PLANO DE AÇÃO INTERATIVO ---
        with col_plan:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("🛠️ Plano de Ação Recomendado")
            st.caption("Selecione as medidas para incluir no laudo.")
            
            # Sugestões Baseadas no Fator Crítico
            sugestoes = {
                "Demandas": ["Revisão de Job Description", "Redistribuição de tarefas", "Ajuste de prazos com clientes", "Contratação de apoio temporário"],
                "Controle": ["Implementar horário flexível", "Aumentar autonomia na tarefa", "Participação na tomada de decisão"],
                "Apoio": ["Treinamento de Liderança", "Reuniões 1:1 quinzenais", "Feedback estruturado"]
            }
            
            lista_sugestoes = sugestoes.get(fator_critico, sugestoes["Demandas"])
            acoes_selecionadas = []
            
            # 1. Checklist Interativo
            st.markdown(f"**Medidas para: {fator_critico}**")
            for i, acao in enumerate(lista_sugestoes):
                # Usando checkbox como 'toggle' visual
                if st.checkbox(acao, key=f"act_{i}", value=(i==0)):
                    acoes_selecionadas.append(acao)
            
            st.markdown("---")
            
            # 2. Campo para Adicionar
            nova_acao = st.text_input("➕ Adicionar medida personalizada:")
            if nova_acao:
                acoes_selecionadas.append(nova_acao)
            
            st.markdown("---")
            
            # 3. Prazos (Cronograma)
            st.markdown("**Cronograma de Execução:**")
            c_d1, c_d2 = st.columns(2)
            data_inicio = c_d1.date_input("Início", datetime.date.today())
            data_fim = c_d2.date_input("Previsão de Conclusão", datetime.date.today() + datetime.timedelta(days=30))
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Botão de Geração
        if st.button("🖨️ Gerar Relatório Completo (A4)", type="primary", use_container_width=True):
            st.markdown("---")
            logo_html = render_svg_logo(120)
            if empresa.get('logo'):
                b64 = image_to_base64(empresa.get('logo'))
                if b64: logo_html = f"<img src='data:image/png;base64,{b64}' width='120'>"

            # Lista HTML das ações selecionadas
            html_acoes = "".join([f"<li style='margin-bottom:5px;'>{a}</li>" for a in acoes_selecionadas])

            html_content = f"""
            <div class="a4-paper">
                <div style="display:flex; justify-content:space-between; border-bottom: 2px solid {COR_PRIMARIA}; padding-bottom:20px; margin-bottom:20px;">
                    <div>{logo_html}</div>
                    <div style="text-align:right;">
                        <h2 style="color:{COR_PRIMARIA}; margin:0;">LAUDO TÉCNICO NR-01</h2>
                        <span style="color:#666;">Avaliação de Riscos Psicossociais</span>
                    </div>
                </div>

                <div style="background-color:#f8f9fa; padding:15px; border-radius:5px; border-left:5px solid {COR_SECUNDARIA};">
                    <strong>Empresa:</strong> {empresa['razao']}<br>
                    <strong>CNPJ:</strong> {empresa['cnpj']} | <strong>Grau de Risco:</strong> {empresa['risco']}<br>
                    <strong>Adesão:</strong> {empresa['respondidas']} de {empresa['func']} colaboradores.
                </div>

                <h4 style="color:{COR_PRIMARIA}; margin-top:30px;">1. Diagnóstico Executivo</h4>
                <p>O Score Global de Saúde Mental da organização é de <strong>{empresa['score']}/5.0</strong>.</p>
                <p>O fator crítico identificado foi: <strong style="color:#d32f2f;">{fator_critico.upper()}</strong>.</p>
                
                <h4 style="color:{COR_PRIMARIA}; background-color:#eef2f3; padding:5px;">2. Plano de Ação Definido</h4>
                <div style="border:1px solid #ddd; padding:15px; border-radius:5px;">
                    <p><strong>Medidas de Prevenção e Controle:</strong></p>
                    <ul>{html_acoes}</ul>
                    <hr style="border-top:1px dashed #ccc;">
                    <p><strong>Cronograma:</strong></p>
                    <table style="width:100%; font-size:0.9em;">
                        <tr>
                            <td><strong>Início:</strong> {data_inicio.strftime('%d/%m/%Y')}</td>
                            <td><strong>Conclusão Prevista:</strong> {data_fim.strftime('%d/%m/%Y')}</td>
                        </tr>
                    </table>
                </div>

                <h4 style="color:{COR_PRIMARIA}; margin-top:30px;">3. Parecer Técnico</h4>
                <p style="text-align:justify;">A organização demonstra proatividade na identificação dos riscos. As medidas acima visam mitigar o impacto do fator '{fator_critico}' na saúde dos trabalhadores, em conformidade com o item 1.5.3.1.1 da NR-01.</p>

                <div style="margin-top:80px; display:flex; justify-content:space-between;">
                    <div style="text-align:center; width:45%; border-top:1px solid #333; padding-top:10px;">
                        <strong>{empresa['resp']}</strong><br>Resp. Legal da Empresa
                    </div>
                    <div style="text-align:center; width:45%; border-top:1px solid #333; padding-top:10px;">
                        <strong>Cristiane C. Lima</strong><br>Consultora Pessin Gestão
                    </div>
                </div>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            st.info("Pressione Ctrl+P para salvar como PDF.")

    # --- 5. CONFIGURAÇÕES ---
    elif selected == "Configurações":
        st.title("Configurações")
        st.info("Ajuste aqui o link real do seu aplicativo quando fizer o deploy.")
        nova_url = st.text_input("URL do Sistema", value=st.session_state.base_url)
        if st.button("Salvar URL"):
            st.session_state.base_url = nova_url
            st.success("URL Atualizada.")

# --- 6. TELA DE PESQUISA (USUÁRIO) ---
def survey_screen():
    query_params = st.query_params
    cod_url = query_params.get("cod", None)
    
    if cod_url and not st.session_state.get('current_company'):
        company = next((c for c in st.session_state.companies_db if c['id'] == cod_url), None)
        if company: st.session_state.current_company = company
    
    if 'current_company' not in st.session_state:
        st.error("Link inválido. Tente novamente.")
        if st.button("Ir para Login"): 
            st.session_state.logged_in = False
            st.rerun()
        return

    comp = st.session_state.current_company
    logo_show = render_svg_logo(150)
    if comp.get('logo'):
        b64 = image_to_base64(comp.get('logo'))
        if b64: logo_show = f"<img src='data:image/png;base64,{b64}' width='150'>"
    
    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'>{logo_show}</div>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center;'>Avaliação - {comp['razao']}</h2>", unsafe_allow_html=True)
    
    with st.form("survey"):
        st.write("**1. Tenho prazos impossíveis de cumprir?**")
        st.select_slider("", ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"], key="q1")
        st.write("**2. Tenho autonomia no meu trabalho?**")
        st.select_slider("", ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"], key="q2")
        
        if st.form_submit_button("✅ Enviar Respostas", type="primary"):
            for c in st.session_state.companies_db:
                if c['id'] == comp['id']: c['respondidas'] += 1
            st.balloons()
            st.success("Respostas enviadas com sucesso!")
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
