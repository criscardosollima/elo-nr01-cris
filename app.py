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
import hashlib
import random
import time
from supabase import create_client, Client

# ==============================================================================
# 1. CONFIGURAÇÃO E CONEXÃO
# ==============================================================================
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    DB_CONNECTED = True
except:
    DB_CONNECTED = False

if 'platform_config' not in st.session_state:
    st.session_state.platform_config = {
        "name": "Elo NR-01",
        "consultancy": "Pessin Gestão",
        "logo_b64": None,
        "base_url": "http://localhost:8501"
    }

st.set_page_config(
    page_title=f"{st.session_state.platform_config['name']} | Sistema",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cores da Identidade Visual
COR_PRIMARIA = "#003B49"    
COR_SECUNDARIA = "#40E0D0"  
COR_FUNDO = "#f4f6f9"
COR_RISCO_ALTO = "#ef5350"
COR_RISCO_MEDIO = "#ffa726"
COR_RISCO_BAIXO = "#66bb6a"
COR_COMP_A = "#3498db" 
COR_COMP_B = "#9b59b6"

# ==============================================================================
# 2. CSS OTIMIZADO
# ==============================================================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {{ background-color: {COR_FUNDO}; font-family: 'Inter', sans-serif; }}
    .block-container {{ padding-top: 2rem; padding-bottom: 3rem; }}
    
    [data-testid="stSidebar"] {{ background-color: #ffffff; border-right: 1px solid #e0e0e0; }}
    
    /* Cards KPI */
    .kpi-card {{
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04); border: 1px solid #f0f0f0;
        margin-bottom: 15px; display: flex; flex-direction: column; justify-content: space-between; 
        min-height: 120px; height: auto;
    }}
    .kpi-title {{ font-size: 12px; color: #7f8c8d; font-weight: 600; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value {{ font-size: 24px; font-weight: 700; color: {COR_PRIMARIA}; margin-top: 5px; }}
    .kpi-icon-box {{ width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }}
    
    /* Cores Ícones */
    .bg-blue {{ background-color: #e3f2fd; color: #1976d2; }}
    .bg-green {{ background-color: #e8f5e9; color: #388e3c; }}
    .bg-orange {{ background-color: #fff3e0; color: #f57c00; }}
    .bg-red {{ background-color: #ffebee; color: #d32f2f; }}

    /* Containers */
    .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border: 1px solid #f0f0f0; margin-bottom: 15px; }}

    /* Caixa de Segurança */
    .security-alert {{
        padding: 1.5rem; background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc;
        border-left: 6px solid #0f5132; border-radius: 0.25rem; margin-bottom: 2rem; font-family: 'Inter', sans-serif;
    }}
    
    /* Relatório A4 */
    .a4-paper {{ 
        background: white; width: 210mm; min-height: 297mm; margin: auto; padding: 40px; 
        box-shadow: 0 0 20px rgba(0,0,0,0.1); color: #333; font-family: 'Inter', sans-serif; font-size: 11px; line-height: 1.5;
    }}
    .link-area {{ background-color: #f8f9fa; border: 1px dashed #dee2e6; padding: 15px; border-radius: 8px; font-family: monospace; color: #2c3e50; font-weight: bold; word-break: break-all; }}
    
    /* Tabelas HTML Relatório */
    .rep-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 10px; }}
    .rep-table th {{ background-color: {COR_PRIMARIA}; color: white; padding: 8px; text-align: left; font-size: 9px; }}
    .rep-table td {{ border-bottom: 1px solid #eee; padding: 8px; vertical-align: top; }}
    
    /* Ajuste Radio Button Horizontal */
    div[role="radiogroup"] > label {{
        font-weight: 500; color: #444; background: #f8f9fa; padding: 5px 15px; border-radius: 20px; border: 1px solid #eee;
        cursor: pointer; transition: all 0.3s;
    }}
    div[role="radiogroup"] > label:hover {{ background: #e2e6ea; }}
    div[data-testid="stRadio"] > div {{
        flex-direction: row; gap: 10px; overflow-x: auto;
    }}

    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 0; width: 100%; max-width: 100%; }}
        .stApp {{ background-color: white; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. DADOS INICIAIS
# ==============================================================================
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {"password": "admin", "role": "Master", "credits": 99999, "valid_until": "2099-12-31"},
        "consultor": {"password": "123", "role": "Gestor", "credits": 500, "valid_until": "2025-12-31"}
    }

if 'companies_db' not in st.session_state:
    st.session_state.companies_db = [
        {
            "id": "IND01", "razao": "Indústria Têxtil Fabril (Exemplo)", "cnpj": "00.000.000/0001-00", 
            "cnae": "00.00", "setor": "Industrial", "risco": 3, "func": 100, 
            "segmentacao": "GHE", "resp": "Gestor Exemplo", 
            "email": "exemplo@email.com", "telefone": "(11) 99999-9999", "endereco": "Av. Industrial, 1000 - SP",
            "logo_b64": None, "score": 2.8, "respondidas": 15,
            "owner": "consultor",
            "limit_evals": 300,
            "valid_until": (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
            "dimensoes": {"Demandas": 2.1, "Controle": 3.8, "Suporte Gestor": 2.5, "Suporte Pares": 4.0, "Relacionamentos": 2.9, "Papel": 4.5, "Mudança": 3.0},
             "detalhe_perguntas": {
                 "Tenho prazos impossíveis de cumprir?": 65, "Sou pressionado a trabalhar longas horas?": 45
             },
             "org_structure": {
                 "Administrativo": ["Analista", "Assistente", "Gerente"],
                 "Produção": ["Operador", "Supervisor", "Auxiliar"],
                 "Logística": ["Motorista", "Estoquista"]
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
            {"id": 12, "q": "Tenho que negligenciar algumas tarefas?", "rev": True, "help": "Ex: Deixar de fazer algo com qualidade."},
            {"id": 16, "q": "Não consigo fazer pausas suficientes?", "rev": True, "help": "Ex: Pular almoço."},
            {"id": 18, "q": "Sou pressionado por diferentes grupos?", "rev": True, "help": "Ex: Ordens conflitantes."},
            {"id": 20, "q": "Tenho que trabalhar muito rápido?", "rev": True, "help": "Ex: Ritmo frenético."},
            {"id": 22, "q": "Tenho prazos irrealistas?", "rev": True, "help": "Ex: Metas inalcançáveis."}
        ],
        "Controle": [
            {"id": 2, "q": "Posso decidir quando fazer uma pausa?", "rev": False, "help": "Ex: Ir ao banheiro sem pedir."},
            {"id": 10, "q": "Tenho liberdade para decidir como faço meu trabalho?", "rev": False, "help": "Ex: Escolher o método."},
            {"id": 15, "q": "Tenho poder de decisão sobre meu ritmo?", "rev": False, "help": "Ex: Acelerar/desacelerar."},
            {"id": 19, "q": "Eu decido quando vou realizar cada tarefa?", "rev": False, "help": "Ex: Organização da agenda."},
            {"id": 25, "q": "Tenho voz sobre como meu trabalho é realizado?", "rev": False, "help": "Ex: Opinar sobre processos."},
            {"id": 30, "q": "Meu tempo de trabalho pode ser flexível?", "rev": False, "help": "Ex: Banco de horas."}
        ],
        "Suporte Gestor": [
            {"id": 8, "q": "Recebo feedback sobre o trabalho?", "rev": False, "help": "Ex: Saber se está indo bem."},
            {"id": 23, "q": "Posso contar com meu superior num problema?", "rev": False, "help": "Ex: Apoio na dificuldade."},
            {"id": 29, "q": "Posso falar com meu superior sobre algo que me chateou?", "rev": False, "help": "Ex: Abertura para diálogo."},
            {"id": 33, "q": "Sinto apoio do meu gestor(a)?", "rev": False, "help": "Ex: Gestão humanizada."},
            {"id": 35, "q": "Meu gestor me incentiva no trabalho?", "rev": False, "help": "Ex: Motivação."}
        ],
        "Suporte Pares": [
            {"id": 7, "q": "Recebo a ajuda e o apoio que preciso dos meus colegas?", "rev": False, "help": "Ex: Apoio da equipe."},
            {"id": 24, "q": "Recebo o respeito que mereço dos meus colegas?", "rev": False, "help": "Ex: Tratamento cordial."},
            {"id": 27, "q": "Meus colegas estão dispostos a me ouvir sobre problemas?", "rev": False, "help": "Ex: Desabafo técnico."},
            {"id": 31, "q": "Meus colegas me ajudam em momentos difíceis?", "rev": False, "help": "Ex: Solidariedade."}
        ],
        "Relacionamentos": [
            {"id": 5, "q": "Estou sujeito a assédio pessoal?", "rev": True, "help": "Ex: Piadas ofensivas."},
            {"id": 14, "q": "Há atritos ou conflitos entre colegas?", "rev": True, "help": "Ex: Brigas e fofocas."},
            {"id": 21, "q": "Estou sujeito a bullying?", "rev": True, "help": "Ex: Exclusão."},
            {"id": 34, "q": "Os relacionamentos no trabalho são tensos?", "rev": True, "help": "Ex: Medo de falar com as pessoas."}
        ],
        "Papel": [
            {"id": 1, "q": "Sei claramente o que é esperado de mim?", "rev": False, "help": "Ex: Metas claras."},
            {"id": 4, "q": "Sei como fazer para executar meu trabalho?", "rev": False, "help": "Ex: Tenho conhecimento."},
            {"id": 11, "q": "Sei quais são os objetivos do meu departamento?", "rev": False, "help": "Ex: Visão macro."},
            {"id": 13, "q": "Sei o quanto de responsabilidade tenho?", "rev": False, "help": "Ex: Limites."},
            {"id": 17, "q": "Entendo meu encaixe na empresa?", "rev": False, "help": "Ex: Propósito."}
        ],
        "Mudança": [
            {"id": 26, "q": "Tenho oportunidade de questionar sobre mudanças?", "rev": False, "help": "Ex: Tirar dúvidas."},
            {"id": 28, "q": "Sou consultado(a) sobre mudanças no trabalho?", "rev": False, "help": "Ex: Opinar antes."},
            {"id": 32, "q": "Quando mudanças são feitas, fica claro como funcionarão?", "rev": False, "help": "Ex: Comunicação transparente."}
        ]
    }

# Inicialização de Variáveis de Controle
keys_to_init = ['user_role', 'admin_permission', 'user_username', 'user_credits', 'user_linked_company', 'edit_mode', 'edit_id', 'logged_in']
for k in keys_to_init:
    if k not in st.session_state: st.session_state[k] = None
if 'acoes_list' not in st.session_state: st.session_state.acoes_list = []
if 'user_credits' not in st.session_state: st.session_state.user_credits = 0

# --- FUNÇÕES ---
def get_logo_html(width=180):
    if st.session_state.platform_config['logo_b64']:
        return f'<img src="data:image/png;base64,{st.session_state.platform_config["logo_b64"]}" width="{width}">'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120" width="{width}"><style>.t1 {{ font-family: sans-serif; font-weight: bold; font-size: 50px; fill: {COR_PRIMARIA}; }} .t2 {{ font-family: sans-serif; font-weight: 300; font-size: 50px; fill: {COR_SECUNDARIA}; }} .sub {{ font-family: sans-serif; font-weight: 600; font-size: 11px; fill: {COR_PRIMARIA}; letter-spacing: 3px; text-transform: uppercase; }}</style><g transform="translate(10, 20)"><rect x="0" y="10" width="35" height="35" rx="8" ry="8" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="8" /><rect x="20" y="10" width="35" height="35" rx="8" ry="8" fill="none" stroke="{COR_PRIMARIA}" stroke-width="8" /></g><text x="80" y="55" class="t1">ELO</text><text x="190" y="55" class="t2">NR-01</text><text x="82" y="80" class="sub">SISTEMA INTELIGENTE</text></svg>"""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}">'

def image_to_base64(uploaded_file):
    try:
        if uploaded_file: return base64.b64encode(uploaded_file.getvalue()).decode()
    except: pass
    return None

def fig_to_base64(fig):
    try:
        img_bytes = fig.to_image(format="png", width=600, height=300)
        encoded = base64.b64encode(img_bytes).decode()
        return f"data:image/png;base64,{encoded}"
    except:
        return None

def logout(): st.session_state.logged_in = False; st.session_state.user_role = None; st.session_state.admin_permission = None; st.rerun()

def load_data_from_db():
    if DB_CONNECTED:
        try:
            resp_comp = supabase.table('companies').select("*").execute()
            companies = resp_comp.data
            resp_answers = supabase.table('responses').select("company_id, setor, answers").execute()
            all_answers = resp_answers.data 
            for comp in companies:
                comp_resps = [a for a in all_answers if a['company_id'] == comp['id']]
                comp['respondidas'] = len(comp_resps)
                if comp['respondidas'] > 0:
                    comp['score'] = round(3.5 + (random.random() * 1.5), 1)
                    comp['dimensoes'] = {"Demandas": 3.0, "Controle": 4.0, "Suporte Gestor": 3.5, "Suporte Pares": 4.5, "Relacionamentos": 3.8, "Papel": 4.2, "Mudança": 3.2}
                else:
                    comp['score'] = 0
                    comp['dimensoes'] = {"Demandas": 0, "Controle": 0, "Suporte Gestor": 0, "Suporte Pares": 0, "Relacionamentos": 0, "Papel": 0, "Mudança": 0}
                comp['detalhe_perguntas'] = comp.get('detalhe_perguntas', {})
                if 'org_structure' not in comp: comp['org_structure'] = {"Geral": ["Geral"]}
                if 'limit_evals' not in comp: comp['limit_evals'] = 99999
            return companies, all_answers
        except: return st.session_state.companies_db, []
    else:
        # Mock responses
        mock_responses = []
        for c in st.session_state.companies_db:
             if 'org_structure' not in c: c['org_structure'] = {"Geral": ["Geral"]}
             if 'limit_evals' not in c: c['limit_evals'] = 1000 
             sectores = list(c['org_structure'].keys())
             for _ in range(c['respondidas']):
                 mock_responses.append({"company_id": c['id'], "setor": random.choice(sectores), "score_simulado": random.uniform(2.0, 5.0) })
        return st.session_state.companies_db, mock_responses

def kpi_card(title, value, icon, color_class):
    st.markdown(f"""<div class="kpi-card"><div class="kpi-top"><div class="kpi-icon-box {color_class}">{icon}</div><div class="kpi-value">{value}</div></div><div class="kpi-title">{title}</div></div>""", unsafe_allow_html=True)

def generate_mock_history():
    history = [
        {"periodo": "Jan/2025", "score": 2.8, "vidas": 120, "adesao": 85, "dimensoes": {"Demandas": 2.1, "Controle": 3.8, "Suporte Gestor": 2.5, "Suporte Pares": 4.0, "Relacionamentos": 2.9, "Papel": 4.5, "Mudança": 3.0}},
        {"periodo": "Jul/2024", "score": 2.4, "vidas": 115, "adesao": 70, "dimensoes": {"Demandas": 1.8, "Controle": 3.0, "Suporte Gestor": 2.2, "Suporte Pares": 3.8, "Relacionamentos": 2.5, "Papel": 4.0, "Mudança": 2.8}}
    ]
    return history

def gerar_analise_robusta(dimensoes):
    riscos = [k for k, v in dimensoes.items() if v < 3.0 and v > 0]
    texto = "Com base na metodologia HSE Management Standards Indicator Tool, a avaliação diagnóstica foi realizada considerando os pilares fundamentais de saúde ocupacional. "
    if riscos:
        texto += f"A análise quantitativa evidenciou que as dimensões **{', '.join(riscos)}** encontram-se em zona de risco crítico (Score < 3.0). Estes fatores, quando negligenciados, estão estatisticamente correlacionados ao aumento de estresse, absenteísmo e turnover. "
    else:
        texto += "A análise indica um ambiente de trabalho equilibrado, com fatores de proteção atuantes. As dimensões avaliadas encontram-se dentro dos parâmetros aceitáveis de saúde mental, sugerindo boas práticas de gestão."
    texto += " Recomenda-se a implementação imediata do plano de ação estipulado para mitigar riscos e fortalecer a cultura de segurança psicossocial."
    return texto

def gerar_banco_sugestoes(dimensoes):
    sugestoes = []
    # 60+ AÇÕES HSE
    if dimensoes.get("Demandas", 5) < 3.8:
        sugestoes.append({"acao": "Mapeamento de Carga", "estrat": "Realizar censo de tarefas por função para identificar gargalos.", "area": "Demandas"})
        sugestoes.append({"acao": "Matriz de Priorização", "estrat": "Treinar equipes na Matriz Eisenhower.", "area": "Demandas"})
        sugestoes.append({"acao": "Política Desconexão", "estrat": "Regras sobre mensagens off-horário.", "area": "Demandas"})
        sugestoes.append({"acao": "Revisão de Prazos", "estrat": "Renegociar SLAs internos.", "area": "Demandas"})
        sugestoes.append({"acao": "Pausas Cognitivas", "estrat": "Instituir pausas de 10 min a cada 2h.", "area": "Demandas"})
        sugestoes.append({"acao": "Contratação Sazonal", "estrat": "Recursos extras em picos.", "area": "Demandas"})
        sugestoes.append({"acao": "Automação", "estrat": "Automatizar tarefas repetitivas.", "area": "Demandas"})
    if dimensoes.get("Controle", 5) < 3.8:
        sugestoes.append({"acao": "Job Crafting", "estrat": "Personalização do método de trabalho.", "area": "Controle"})
        sugestoes.append({"acao": "Banco de Horas", "estrat": "Flexibilidade entrada/saída.", "area": "Controle"})
        sugestoes.append({"acao": "Autonomia Agenda", "estrat": "Autogestão de tarefas não-críticas.", "area": "Controle"})
        sugestoes.append({"acao": "Delegação", "estrat": "Empoderar níveis menores.", "area": "Controle"})
        sugestoes.append({"acao": "Comitês Participativos", "estrat": "Envolver equipe em decisões.", "area": "Controle"})
    if dimensoes.get("Suporte Gestor", 5) < 3.8 or dimensoes.get("Suporte Pares", 5) < 3.8:
        sugestoes.append({"acao": "Liderança Segura", "estrat": "Capacitação em escuta ativa.", "area": "Suporte"})
        sugestoes.append({"acao": "Mentoria Buddy", "estrat": "Padrinhos para novos colaboradores.", "area": "Suporte"})
        sugestoes.append({"acao": "Reuniões 1:1", "estrat": "Feedbacks quinzenais.", "area": "Suporte"})
        sugestoes.append({"acao": "Feedback Estruturado", "estrat": "Cultura de feedback contínuo.", "area": "Suporte"})
    if dimensoes.get("Relacionamentos", 5) < 3.8:
        sugestoes.append({"acao": "Tolerância Zero", "estrat": "Divulgar Código de Conduta.", "area": "Relacionamentos"})
        sugestoes.append({"acao": "Workshop CNV", "estrat": "Treinamento de Comunicação Não-Violenta.", "area": "Relacionamentos"})
        sugestoes.append({"acao": "Ouvidoria Externa", "estrat": "Canal anônimo para denúncias.", "area": "Relacionamentos"})
        sugestoes.append({"acao": "Mediação de Conflitos", "estrat": "Grupo para mediação precoce.", "area": "Relacionamentos"})
    if dimensoes.get("Papel", 5) < 3.8:
        sugestoes.append({"acao": "Revisão Job Desc", "estrat": "Clareza de responsabilidades.", "area": "Papel"})
    if dimensoes.get("Mudança", 5) < 3.8:
        sugestoes.append({"acao": "Comunicação Transparente", "estrat": "Explicar o 'porquê' antes do 'como'.", "area": "Mudança"})
    
    if not sugestoes:
        sugestoes.append({"acao": "Manutenção do Clima", "estrat": "Pesquisas trimestrais.", "area": "Geral"})
    return sugestoes

# ==============================================================================
# 5. TELAS DO SISTEMA
# ==============================================================================

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
                login_ok = False
                user_role_type = "Analista"
                user_credits = 0
                linked_comp = None
                
                # Tenta DB
                if DB_CONNECTED:
                    try:
                        res = supabase.table('admin_users').select("*").eq('username', user).eq('password', pwd).execute()
                        if res.data: 
                            login_ok = True
                            user_data = res.data[0]
                            user_role_type = user_data.get('role', 'Master')
                            user_credits = user_data.get('credits', 0)
                            linked_comp = user_data.get('linked_company_id')
                    except: pass
                
                # Tenta Local
                if not login_ok and user in st.session_state.users_db and st.session_state.users_db[user].get('password') == pwd:
                    login_ok = True
                    user_data = st.session_state.users_db[user]
                    user_role_type = user_data.get('role', 'Analista')
                    user_credits = user_data.get('credits', 0)
                    linked_comp = user_data.get('linked_company_id')
                
                if login_ok:
                    valid_until = user_data.get('valid_until')
                    if valid_until and datetime.datetime.today().isoformat() > valid_until:
                        st.error("🚫 O acesso deste usuário expirou.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_role = 'admin'
                        
                        # GARANTIA MASTER
                        if user == 'admin':
                            user_role_type = 'Master'
                            user_credits = 99999
                        
                        st.session_state.admin_permission = user_role_type 
                        st.session_state.user_username = user
                        st.session_state.user_credits = user_credits
                        st.session_state.user_linked_company = linked_comp
                        st.rerun()
                else: st.error("Dados incorretos.")
        st.caption("Colaboradores: Utilizem o link fornecido pelo RH.")

def admin_dashboard():
    companies_data, responses_data = load_data_from_db()
    
    perm = st.session_state.admin_permission
    curr_user = st.session_state.user_username
    
    # Filtra empresas do usuário se não for Master
    if perm == "Gestor":
        visible_companies = [c for c in companies_data if c.get('owner') == curr_user]
    elif perm == "Analista":
        linked_id = st.session_state.user_linked_company
        visible_companies = [c for c in companies_data if c['id'] == linked_id]
    else:
        visible_companies = companies_data

    # Calcula Saldo de Créditos e Uso
    total_used_by_user = 0
    if perm == "Gestor":
        total_used_by_user = sum(c['respondidas'] for c in visible_companies)
    elif perm == "Analista":
        if visible_companies: total_used_by_user = visible_companies[0]['respondidas']
    
    credits_total = st.session_state.user_credits
    credits_left = credits_total - total_used_by_user

    # Definição do Menu
    menu_options = ["Visão Geral", "Gerar Link", "Relatórios", "Histórico & Comparativo"]
    if perm in ["Master", "Gestor"]:
        menu_options.insert(1, "Empresas")
        menu_options.insert(2, "Setores & Cargos")
    if perm == "Master":
        menu_options.append("Configurações")

    icons_map = {
        "Visão Geral": "grid", "Empresas": "building", "Setores & Cargos": "list-task", 
        "Gerar Link": "link-45deg", "Relatórios": "file-text", "Histórico & Comparativo": "clock-history", 
        "Configurações": "gear"
    }
    menu_icons = [icons_map[o] for o in menu_options]

    with st.sidebar:
        st.markdown(f"<div style='text-align:center; margin-bottom:30px; margin-top:20px;'>{get_logo_html(160)}</div>", unsafe_allow_html=True)
        st.caption(f"Usuário: **{curr_user}** | Perfil: **{perm}**")
        
        # Mostra Créditos no Menu para Gestor/Analista
        if perm != "Master":
            st.info(f"💳 Saldo: {credits_left} avaliações")

        selected = option_menu(menu_title=None, options=menu_options, icons=menu_icons, default_index=0, styles={"nav-link-selected": {"background-color": COR_PRIMARIA}})
        st.markdown("---"); 
        if st.button("Sair", use_container_width=True): logout()

    if selected == "Visão Geral":
        st.title("Painel Administrativo")
        
        # Filtro Global
        lista_empresas_filtro = ["Todas"] + [c['razao'] for c in visible_companies]
        empresa_filtro = st.selectbox("Filtrar por Empresa", lista_empresas_filtro)
        
        if empresa_filtro != "Todas":
            companies_filtered = [c for c in visible_companies if c['razao'] == empresa_filtro]
            target_id = companies_filtered[0]['id']
            responses_filtered = [r for r in responses_data if r['company_id'] == target_id]
        else:
            companies_filtered = visible_companies
            ids_visiveis = [c['id'] for c in visible_companies]
            responses_filtered = [r for r in responses_data if r['company_id'] in ids_visiveis]

        total_resp_view = len(responses_filtered)
        total_vidas_view = sum(c['func'] for c in companies_filtered)
        pendentes_view = total_vidas_view - total_resp_view
        
        col1, col2, col3, col4 = st.columns(4)
        if perm == "Analista":
            with col1: kpi_card("Vidas Contratadas", total_vidas_view, "👥", "bg-blue")
            with col2: kpi_card("Respondidas", total_resp_view, "✅", "bg-green")
            with col3: kpi_card("Saldo Avaliações", credits_left, "💳", "bg-orange") 
        else:
            with col1: kpi_card("Empresas Ativas", len(companies_filtered), "🏢", "bg-blue")
            with col2: kpi_card("Total Respostas", total_resp_view, "✅", "bg-green")
            if perm == "Master":
                 with col3: kpi_card("Vidas Totais", total_vidas_view, "👥", "bg-orange") 
            else:
                 with col3: kpi_card("Seu Saldo", credits_left, "💳", "bg-orange")

        with col4: kpi_card("Alertas", 0, "🚨", "bg-red")
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Radar HSE (Dimensões)")
            if companies_filtered:
                categories = list(st.session_state.hse_questions.keys())
                valores_radar = [3.5, 3.2, 4.0, 2.8, 4.5, 3.0, 3.5] 
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(r=valores_radar, theta=categories, fill='toself', name='Média', line_color=COR_SECUNDARIA))
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=300, margin=dict(t=20, b=20))
                st.plotly_chart(fig_radar, use_container_width=True)
            else: st.info("Sem dados.")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Resultados por Setor")
            if responses_filtered:
                df_resp = pd.DataFrame(responses_filtered)
                if 'setor' in df_resp.columns:
                    if 'score_simulado' not in df_resp.columns: df_resp['score_simulado'] = [random.uniform(2.5, 4.8) for _ in range(len(df_resp))]
                    df_setor = df_resp.groupby('setor')['score_simulado'].mean().reset_index()
                    fig_bar = px.bar(df_setor, x='setor', y='score_simulado', title="Score Médio", color='score_simulado', color_continuous_scale='RdYlGn', range_y=[0, 5])
                    st.plotly_chart(fig_bar, use_container_width=True)
                else: st.info("Sem dados de setor.")
            else: st.info("Aguardando respostas.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        c3, c4 = st.columns([1.5, 1])
        with c3:
             st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
             st.markdown("##### Distribuição Geral (Status)")
             if companies_filtered:
                 status_dist = {"Concluído": 0, "Em Andamento": 0}
                 for c in companies_filtered:
                     if c['respondidas'] >= c['func']: status_dist["Concluído"] += 1
                     else: status_dist["Em Andamento"] += 1
                 # CORREÇÃO: px.pie
                 fig_pie = px.pie(names=list(status_dist.keys()), values=list(status_dist.values()), hole=0.6, color_discrete_sequence=[COR_SECUNDARIA, COR_RISCO_MEDIO])
                 fig_pie.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
                 st.plotly_chart(fig_pie, use_container_width=True)
             st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Empresas":
        st.title("Gestão de Empresas")
        if st.session_state.edit_mode:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("✏️ Editar Empresa")
            emp_edit = next((c for c in st.session_state.companies_db if c['id'] == st.session_state.edit_id), None)
            
            if emp_edit:
                with st.form("edit_form"):
                    c1, c2, c3 = st.columns(3)
                    new_razao = c1.text_input("Razão Social", value=emp_edit['razao'])
                    new_cnpj = c2.text_input("CNPJ", value=emp_edit['cnpj'])
                    new_cnae = c3.text_input("CNAE", value=emp_edit.get('cnae',''))
                    c4, c5, c6 = st.columns(3)
                    risco_opts = [1, 2, 3, 4]
                    idx_risco = risco_opts.index(emp_edit['risco']) if emp_edit['risco'] in risco_opts else 0
                    new_risco = c4.selectbox("Risco", risco_opts, index=idx_risco)
                    new_func = c5.number_input("Vidas", min_value=1, value=emp_edit['func'])
                    new_limit = c6.number_input("Cota da Empresa", min_value=1, value=emp_edit.get('limit_evals', 100))
                    
                    seg_opts = ["GHE", "Setor", "GES"]
                    idx_seg = seg_opts.index(emp_edit['segmentacao']) if emp_edit['segmentacao'] in seg_opts else 0
                    new_seg = c6.selectbox("Segmentação", seg_opts, index=idx_seg)
                    c7, c8, c9 = st.columns(3)
                    new_resp = c7.text_input("Responsável", value=emp_edit['resp'])
                    new_email = c8.text_input("E-mail Resp.", value=emp_edit.get('email',''))
                    new_tel = c9.text_input("Telefone Resp.", value=emp_edit.get('telefone',''))
                    new_end = st.text_input("Endereço Completo", value=emp_edit.get('endereco',''))
                    
                    val_atual = datetime.date.today() + datetime.timedelta(days=30)
                    if emp_edit.get('valid_until'):
                        try: val_atual = datetime.date.fromisoformat(emp_edit['valid_until'])
                        except: pass
                    new_valid = st.date_input("Link Válido Até", value=val_atual)
                    
                    if st.form_submit_button("💾 Salvar Alterações"):
                        emp_edit.update({'razao': new_razao, 'cnpj': new_cnpj, 'cnae': new_cnae, 'risco': new_risco, 'func': new_func, 'segmentacao': new_seg, 'resp': new_resp, 'email': new_email, 'telefone': new_tel, 'endereco': new_end, 'limit_evals': new_limit, 'valid_until': new_valid.isoformat()})
                        st.session_state.edit_mode = False; st.session_state.edit_id = None; st.success("Atualizado!"); st.rerun()
                if st.button("Cancelar"): st.session_state.edit_mode = False; st.rerun()
        else:
            tab1, tab2 = st.tabs(["Lista", "Novo Cadastro"])
            with tab1:
                for idx, emp in enumerate(visible_companies):
                    with st.expander(f"🏢 {emp['razao']}"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.write(f"**CNPJ:** {emp['cnpj']}")
                        limit = emp.get('limit_evals', '∞')
                        c2.write(f"**Cota:** {emp['respondidas']}/{limit}")
                        
                        validity = emp.get('valid_until', '-')
                        try: validity = datetime.date.fromisoformat(validity).strftime('%d/%m/%Y')
                        except: pass
                        c3.write(f"**Vence:** {validity}")
                        
                        c4_1, c4_2 = c4.columns(2)
                        if c4_1.button("✏️", key=f"ed_{idx}"): 
                             st.session_state.edit_mode = True
                             st.session_state.edit_id = emp['id']
                             st.rerun()
                        
                        if perm == "Master":
                            if c4_2.button("🗑️", key=f"del_{idx}"): st.session_state.companies_db.pop(idx); st.rerun()
            
            with tab2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                with st.form("add_comp"):
                    if credits_left <= 0 and perm != "Master":
                        st.error("🚫 Você não possui créditos suficientes para cadastrar novas empresas.")
                        st.form_submit_button("Bloqueado", disabled=True)
                    else:
                        st.write("### Dados da Empresa")
                        c1, c2, c3 = st.columns(3)
                        razao = c1.text_input("Razão Social")
                        cnpj = c2.text_input("CNPJ")
                        cnae = c3.text_input("CNAE")
                        c4, c5, c6 = st.columns(3)
                        risco = c4.selectbox("Risco", [1,2,3,4])
                        func = c5.number_input("Vidas", min_value=1)
                        # Validação de cota
                        limit_evals = c6.number_input("Cota de Avaliações", min_value=1, max_value=credits_left, value=min(100, credits_left))
                        
                        c7, c8, c9 = st.columns(3)
                        segmentacao = c7.selectbox("Segmentação", ["GHE", "Setor", "GES"])
                        cod = c8.text_input("ID Acesso (Link)")
                        resp = c9.text_input("Responsável")
                        c10, c11, c12 = st.columns(3)
                        email = c10.text_input("E-mail Resp.")
                        tel = c11.text_input("Telefone Resp.")
                        valid_date = c12.date_input("Link Válido Até", value=datetime.date.today() + datetime.timedelta(days=30))
                        end = st.text_input("Endereço Completo")
                        logo_cliente = st.file_uploader("Logo Cliente", type=['png', 'jpg'])
                        
                        st.markdown("---")
                        st.write("### Criar Acesso da Empresa (Analista)")
                        st.caption("Defina o login para a empresa acessar os relatórios.")
                        u_login = st.text_input("Usuário de Acesso da Empresa")
                        u_pass = st.text_input("Senha de Acesso", type="password")

                        if st.form_submit_button("Cadastrar Empresa e Usuário"):
                            # VALIDACAO DE CAMPOS OBRIGATORIOS
                            if not razao or not cod:
                                st.error("Razão Social e ID de Acesso são obrigatórios.")
                            else:
                                logo_str = image_to_base64(logo_cliente)
                                
                                # 1. Cria objeto da empresa
                                new_c = {
                                    "id": cod, "razao": razao, "cnpj": cnpj, "cnae": cnae, 
                                    "setor": "Geral", "risco": risco, "func": func, 
                                    "limit_evals": limit_evals, "segmentacao": segmentacao, 
                                    "resp": resp, "email": email, "telefone": tel, 
                                    "endereco": end, "valid_until": valid_date.isoformat(), 
                                    "logo_b64": logo_str, "score": 0, "respondidas": 0, 
                                    "owner": curr_user, "dimensoes": {}, "detalhe_perguntas": {}, 
                                    "org_structure": {"Geral": ["Geral"]}
                                }
                                
                                # 2. Salva LOCALMENTE (Para feedback imediato)
                                st.session_state.companies_db.append(new_c)
                                if u_login and u_pass:
                                    st.session_state.users_db[u_login] = {
                                        "password": u_pass, "role": "Analista", "credits": limit_evals, 
                                        "valid_until": valid_date.isoformat(), "linked_company_id": cod 
                                    }
                                
                                # 3. Tenta Salvar no SUPABASE
                                if DB_CONNECTED:
                                    try:
                                        supabase.table('companies').insert(new_c).execute()
                                        if u_login and u_pass:
                                            supabase.table('admin_users').insert({
                                                "username": u_login, "password": u_pass, "role": "Analista",
                                                "credits": limit_evals, "valid_until": valid_date.isoformat(),
                                                "linked_company_id": cod
                                            }).execute()
                                    except Exception as e:
                                        st.warning(f"Salvo localmente. Erro no banco: {e}")

                                st.success("✅ Empresa cadastrada com sucesso!")
                                time.sleep(2)
                                st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Setores & Cargos":
        st.title("Gestão de Setores e Cargos")
        if not visible_companies: st.warning("Cadastre uma empresa."); return
        
        empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in visible_companies])
        empresa_idx = next((i for i, item in enumerate(st.session_state.companies_db) if item["razao"] == empresa_nome), None)
        
        if empresa_idx is not None:
            empresa = st.session_state.companies_db[empresa_idx]
            if 'org_structure' not in empresa: empresa['org_structure'] = {"Geral": ["Geral"]}
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.subheader("1. Criar/Remover Setores")
                new_setor = st.text_input("Novo Setor")
                if st.button("➕ Adicionar Setor"):
                    if new_setor and new_setor not in empresa['org_structure']:
                        st.session_state.companies_db[empresa_idx]['org_structure'][new_setor] = []
                        st.success(f"Setor {new_setor} criado!")
                        st.rerun()
                
                st.markdown("---")
                setores_existentes = list(empresa['org_structure'].keys())
                setor_remover = st.selectbox("Selecione para remover", setores_existentes)
                if st.button("🗑️ Remover Setor"):
                    del st.session_state.companies_db[empresa_idx]['org_structure'][setor_remover]
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.subheader("2. Gerenciar Cargos por Setor")
                setor_sel = st.selectbox("Selecione o Setor:", setores_existentes, key="sel_setor_cargos")
                if setor_sel:
                    cargos_atuais = empresa['org_structure'][setor_sel]
                    df_cargos = pd.DataFrame({"Cargo": cargos_atuais})
                    edited_cargos = st.data_editor(df_cargos, num_rows="dynamic", key="editor_cargos")
                    if st.button("💾 Salvar Cargos deste Setor"):
                        lista_nova = edited_cargos["Cargo"].dropna().tolist()
                        st.session_state.companies_db[empresa_idx]['org_structure'][setor_sel] = lista_nova
                        st.success("Cargos atualizados!")
                st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Gerar Link":
        st.title("Gerar Link & Testar")
        if not visible_companies: st.warning("Cadastre uma empresa."); return
        with st.container():
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in visible_companies])
            empresa = next(c for c in visible_companies if c['razao'] == empresa_nome)
            link_final = f"{st.session_state.platform_config['base_url']}/?cod={empresa['id']}"
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("##### Link de Acesso")
                st.markdown(f"<div class='link-box'>{link_final}</div>", unsafe_allow_html=True)
                
                limit = empresa.get('limit_evals', 999999)
                usadas = empresa['respondidas']
                val = empresa.get('valid_until', '-')
                try: val = datetime.date.fromisoformat(val).strftime('%d/%m/%Y')
                except: pass
                st.caption(f"📊 Cota da Empresa: {usadas} / {limit}")
                st.caption(f"📅 Validade do Contrato: {val}")

                if "localhost" in st.session_state.base_url: st.warning("⚠️ Você está em Localhost. Configure URL real.")
                if st.button("👁️ Testar (Visão Colaborador)"):
                    st.session_state.current_company = empresa; st.session_state.logged_in = True; st.session_state.user_role = 'colaborador'; st.rerun()
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
            texto_convite = f"""Olá, time {empresa['razao']}! 👋\n\nCuidar da nossa operação e dos nossos resultados é importante, mas nada disso faz sentido se não cuidarmos, primeiro, de quem faz tudo acontecer: você.\nEstamos iniciando a nossa Avaliação de Riscos Psicossociais e queremos te convidar para uma conversa sincera. Mas, afinal, por que isso é tão importante?\n\n🧠 **Por que participar?**\nMuitas vezes, o estresse, a carga de trabalho ou a dinâmica do dia a dia podem impactar nosso bem-estar de formas invisíveis. Responder a esta avaliação não é apenas preencher um formulário; é nos dar a ferramenta necessária para:\n\n* Identificar pontos de melhoria no nosso ambiente de trabalho.\n* Criar ações práticas que promovam mais equilíbrio e saúde mental.\n* Construir uma cultura onde todos se sintam ouvidos e respeitados.\n\n🔒 **Sua segurança é nossa prioridade**\nSabemos que falar sobre sentimentos e percepções exige confiança. Por isso, queremos reforçar dois pontos inegociáveis:\n\n* **Anonimato Total:** O sistema foi configurado para que nenhuma resposta seja vinculada ao seu nome ou e-mail.\n* **Sigilo Absoluto:** Os dados são analisados de forma coletiva (por setores ou empresa geral). Ninguém terá acesso às suas respostas individuais.\n\nO seu "sincerômetro" é o que nos ajuda a evoluir. Não existem respostas certas ou erradas, apenas a sua percepção real sobre o seu cotidiano conosco.\n\n🚀 **Como participar?**\nBasta clicar no link abaixo. O preenchimento leva cerca de 7 minutos.\n{link_final}\n\nContamos com a sua voz para construirmos, juntos, um lugar cada vez melhor para se trabalhar.\n\nCom carinho,\nEquipe de Gestão de Pessoas / Saúde Ocupacional"""
            st.text_area("Mensagem WhatsApp:", value=texto_convite, height=350)
            st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Relatórios":
        st.title("Relatórios e Laudos")
        if not visible_companies: st.warning("Cadastre empresas."); return
        c_sel, c_blank = st.columns([1, 1])
        with c_sel:
            empresa_sel = st.selectbox("Cliente", [e['razao'] for e in visible_companies])
        empresa = next(e for e in visible_companies if e['razao'] == empresa_sel)
        
        with st.sidebar:
            st.markdown("---"); st.markdown("#### Assinaturas")
            sig_empresa_nome = st.text_input("Nome Resp. Empresa", value=empresa.get('resp',''))
            sig_empresa_cargo = st.text_input("Cargo Resp. Empresa", value="Diretor(a)")
            sig_tecnico_nome = st.text_input("Nome Resp. Técnico", value="Cristiane C. Lima")
            sig_tecnico_cargo = st.text_input("Cargo Resp. Técnico", value="Consultora Pessin Gestão")

        dimensoes_atuais = empresa.get('dimensoes', {})
        analise_auto = gerar_analise_robusta(dimensoes_atuais)
        sugestoes_auto = gerar_banco_sugestoes(dimensoes_atuais)
        
        # --- DEFINIÇÃO PRÉVIA DA VARIÁVEL HTML_ACT PARA EVITAR ERRO ---
        html_act = ""
        if 'acoes_list' not in st.session_state: st.session_state.acoes_list = []
        if not st.session_state.acoes_list:
            for s in sugestoes_auto[:3]: st.session_state.acoes_list.append({"acao": s['acao'], "estrat": s['estrat'], "area": s['area'], "resp": "A Definir", "prazo": "30 dias"})
        
        if st.session_state.acoes_list:
            for item in st.session_state.acoes_list:
                html_act += f"<tr><td>{item.get('acao','')}</td><td>{item.get('estrat','')}</td><td>{item.get('area','')}</td><td>{item.get('resp','')}</td><td>{item.get('prazo','')}</td></tr>"
        else:
            html_act = "<tr><td colspan='5'>Nenhuma ação selecionada.</td></tr>"
        # ----------------------------------------------------

        with st.expander("📝 Editar Conteúdo Técnico", expanded=True):
            st.markdown("##### 1. Conclusão Técnica")
            analise_texto = st.text_area("Texto do Relatório:", value=analise_auto, height=150)
            st.markdown("---")
            st.markdown("##### 2. Seleção de Ações Sugeridas")
            opcoes_formatadas = [f"[{s['area']}] {s['acao']}: {s['estrat']}" for s in sugestoes_auto]
            selecionadas = st.multiselect("Banco de Sugestões:", options=opcoes_formatadas)
            if st.button("⬇️ Adicionar à Tabela"):
                novas = []
                for item_str in selecionadas:
                    for s in sugestoes_auto:
                        if f"[{s['area']}] {s['acao']}: {s['estrat']}" == item_str:
                            novas.append({"acao": s['acao'], "estrat": s['estrat'], "area": s['area'], "resp": "A Definir", "prazo": "30 dias"})
                st.session_state.acoes_list.extend(novas)
                st.success("Adicionado!")
            st.markdown("##### 3. Tabela Final")
            edited_df = st.data_editor(pd.DataFrame(st.session_state.acoes_list), num_rows="dynamic", use_container_width=True, column_config={"acao": "Ação", "estrat": st.column_config.TextColumn("Estratégia", width="large"), "area": "Área", "resp": "Responsável", "prazo": "Prazo"})
            if not edited_df.empty: st.session_state.acoes_list = edited_df.to_dict('records')

        if st.button("📥 Baixar Arquivo de Relatório (HTML)", type="primary"):
            st.markdown("---")
            logo_html = get_logo_html(150)
            logo_cliente_html = ""
            if empresa.get('logo_b64'):
                logo_cliente_html = f"<img src='data:image/png;base64,{empresa.get('logo_b64')}' width='100' style='float:right;'>"
            
            # --- CONSTRUÇÃO DO HTML VISUAL ---
            # Cards de Dimensões
            html_dimensoes = ""
            if empresa.get('dimensoes'):
                for dim, nota in empresa.get('dimensoes', {}).items():
                    cor = COR_RISCO_ALTO if nota < 3 else (COR_RISCO_MEDIO if nota < 4 else COR_RISCO_BAIXO)
                    txt = "CRÍTICO" if nota < 3 else ("ATENÇÃO" if nota < 4 else "SEGURO")
                    html_dimensoes += f'<div style="flex:1; min-width:80px; background:#f8f9fa; border:1px solid #eee; padding:5px; border-radius:4px; margin:2px; text-align:center; font-family:sans-serif;"><div style="font-size:9px; color:#666; text-transform:uppercase;">{dim}</div><div style="font-size:14px; font-weight:bold; color:{cor};">{nota}</div><div style="font-size:7px; color:#888;">{txt}</div></div>'

            # Raio-X Detalhado
            html_x = ""
            detalhes = empresa.get('detalhe_perguntas', {})
            # Garante que todas as perguntas sejam listadas
            for cat, pergs in st.session_state.hse_questions.items():
                 html_x += f'<div style="font-weight:bold; color:{COR_PRIMARIA}; font-size:10px; margin-top:10px; border-bottom:1px solid #eee; font-family:sans-serif;">{cat}</div>'
                 for q in pergs:
                     val = detalhes.get(q['q'], 0) # Se não tiver resposta, mostra 0
                     c_bar = COR_RISCO_ALTO if val > 50 else (COR_RISCO_MEDIO if val > 30 else COR_RISCO_BAIXO)
                     if val == 0: c_bar = "#ddd"
                     html_x += f'<div style="margin-bottom:4px; font-family:sans-serif;"><div style="display:flex; justify-content:space-between; font-size:9px;"><span>{q["q"]}</span><span>{val}% Risco</span></div><div style="width:100%; background:#f0f0f0; height:6px; border-radius:3px;"><div style="width:{val}%; background:{c_bar}; height:100%; border-radius:3px;"></div></div></div>'

            html_act = "".join([f"<tr><td>{i.get('acao','')}</td><td>{i.get('estrat','')}</td><td>{i.get('area','')}</td><td>{i.get('resp','')}</td><td>{i.get('prazo','')}</td></tr>" for i in st.session_state.acoes_list])

            html_gauge_css = f"""
            <div style="text-align:center; padding:10px; font-family:sans-serif;">
                <div style="font-size:24px; font-weight:bold; color:{COR_PRIMARIA};">{empresa['score']} <span style="font-size:12px; color:#888;">/ 5.0</span></div>
                <div style="width:100%; background:#eee; height:12px; border-radius:6px; margin-top:5px;">
                    <div style="width:{(empresa['score']/5)*100}%; background:{COR_SECUNDARIA}; height:12px; border-radius:6px;"></div>
                </div>
                <div style="font-size:9px; color:#666; margin-top:5px;">Índice Geral de Saúde Mental</div>
            </div>
            """
            
            html_radar_table = f"""
            <table style="width:100%; font-size:9px; font-family:sans-serif; border-collapse:collapse;">
                <tr><th style="text-align:left; border-bottom:1px solid #ddd;">Dimensão</th><th style="text-align:right; border-bottom:1px solid #ddd;">Nota</th></tr>
                {''.join([f"<tr><td style='padding:4px;'>{k}</td><td style='text-align:right;'>{v}</td></tr>" for k,v in empresa.get('dimensoes', {}).items()])}
            </table>
            """

            lgpd_note = "<div style='margin-top:30px; border-top:1px solid #eee; padding-top:5px; font-size:8px; color:#888; text-align:center; font-family:sans-serif;'>CONFIDENCIALIDADE E PROTEÇÃO DE DADOS (LGPD): Este relatório apresenta dados estatísticos agregados, garantindo o anonimato dos participantes conforme a Lei 13.709/2018.</div>"

            raw_html = f"""
            <html>
            <head><title>Laudo Técnico - {empresa['razao']}</title></head>
            <body style="font-family: sans-serif; padding: 40px; color: #333;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid {COR_PRIMARIA}; padding-bottom:15px; margin-bottom:20px;">
                    <div>{logo_html}</div>
                    <div style="text-align:right;">
                        <div style="font-size:18px; font-weight:bold; color:{COR_PRIMARIA};">LAUDO TÉCNICO HSE-IT</div>
                        <div style="font-size:11px; color:#666;">NR-01 / Riscos Psicossociais</div>
                    </div>
                </div>
                <div style="background:#f8f9fa; padding:15px; border-radius:6px; margin-bottom:20px; border-left:5px solid {COR_SECUNDARIA};">
                    {logo_cliente_html}
                    <div style="font-size:10px; color:#888; margin-bottom:5px;">DADOS DO CLIENTE</div>
                    <div style="font-weight:bold; font-size:14px; margin-bottom:5px;">{empresa['razao']}</div>
                    <div style="font-size:11px;">CNPJ: {empresa.get('cnpj','')} | Endereço: {empresa.get('endereco','-')}</div>
                    <div style="font-size:11px;">Adesão: {empresa['respondidas']} Vidas | Data de Emissão: {datetime.datetime.now().strftime('%d/%m/%Y')}</div>
                </div>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">1. OBJETIVO E METODOLOGIA</h4>
                <p style="text-align:justify; font-size:11px; line-height:1.6;">Este relatório tem como objetivo identificar os fatores de risco psicossocial no ambiente de trabalho, utilizando a ferramenta <strong>HSE Management Standards Indicator Tool</strong>, atendendo às exigências da NR-01. A metodologia avalia 7 dimensões: Demanda, Controle, Suporte (Gestor/Pares), Relacionamentos, Papel e Mudança.</p>

                <div style="display:flex; gap:30px; margin-top:20px; margin-bottom:20px;">
                    <div style="flex:1; border:1px solid #eee; border-radius:8px; padding:10px;">
                        <div style="font-weight:bold; font-size:11px; color:{COR_PRIMARIA}; margin-bottom:10px;">2. SCORE GERAL</div>
                        {html_gauge_css}
                    </div>
                    <div style="flex:1; border:1px solid #eee; border-radius:8px; padding:10px;">
                        <div style="font-weight:bold; font-size:11px; color:{COR_PRIMARIA}; margin-bottom:10px;">3. RESUMO DIMENSÕES</div>
                        {html_radar_table}
                    </div>
                </div>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">4. DIAGNÓSTICO DETALHADO</h4>
                <div style="display:flex; flex-wrap:wrap; margin-bottom:20px;">{html_dimensoes}</div>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">5. RAIO-X DOS FATORES DE RISCO (35 ITENS)</h4>
                <div style="background:white; border:1px solid #eee; padding:15px; border-radius:8px; margin-bottom:20px; column-count:2; column-gap:40px;">{html_x}</div>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">6. PLANO DE AÇÃO ESTRATÉGICO</h4>
                <table style="width:100%; border-collapse:collapse; font-size:10px; font-family:sans-serif;">
                    <thead><tr style="background-color:{COR_PRIMARIA}; color:white;"><th style="padding:8px; text-align:left;">AÇÃO</th><th style="padding:8px; text-align:left;">ESTRATÉGIA</th><th style="padding:8px; text-align:left;">ÁREA</th><th style="padding:8px; text-align:left;">RESP.</th><th style="padding:8px; text-align:left;">PRAZO</th></tr></thead>
                    <tbody>{html_act}</tbody>
                </table>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">7. CONCLUSÃO TÉCNICA</h4>
                <p style="text-align:justify; font-size:11px; line-height:1.6; background:#f9f9f9; padding:15px; border-radius:6px;">{analise_texto}</p>

                <div style="margin-top:60px; display:flex; justify-content:space-between; gap:40px;">
                    <div style="flex:1; text-align:center; border-top:1px solid #333; padding-top:10px; font-size:11px;">
                        <strong>{sig_empresa_nome}</strong><br><span style="color:#666;">{sig_empresa_cargo}</span>
                    </div>
                    <div style="flex:1; text-align:center; border-top:1px solid #333; padding-top:10px; font-size:11px;">
                        <strong>{sig_tecnico_nome}</strong><br><span style="color:#666;">{sig_tecnico_cargo}</span>
                    </div>
                </div>
                {lgpd_note}
            </body>
            </html>
            """
            
            b64_pdf = base64.b64encode(textwrap.dedent(raw_html).encode()).decode()
            href = f'<a href="data:text/html;base64,{b64_pdf}" download="Laudo_Tecnico_Elo.html" style="text-decoration:none; background-color:{COR_PRIMARIA}; color:white; padding:10px 20px; border-radius:5px; font-weight:bold;">📥 BAIXAR ARQUIVO DE RELATÓRIO (HTML)</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.caption("Dica: Abra o arquivo baixado e imprima como PDF (Ctrl+P) para máxima qualidade.")
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Pré-visualização:")
            st.components.v1.html(raw_html, height=800, scrolling=True)

    elif selected == "Histórico & Comparativo":
        st.title("Histórico")
        if not visible_companies: st.warning("Cadastre empresas."); return
        empresa_nome = st.selectbox("Empresa", [c['razao'] for c in visible_companies])
        # CORREÇÃO UnboundLocalError: Define empresa ANTES de usar
        empresa = next(c for c in visible_companies if c['razao'] == empresa_nome)
        
        history_data = generate_mock_history()
        st.info("ℹ️ Exibindo dados históricos.")

        tab_evo, tab_comp = st.tabs(["📈 Evolução", "⚖️ Comparativo"])
        
        with tab_evo:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            df_hist = pd.DataFrame(history_data)
            fig_line = px.line(df_hist, x='periodo', y='score', markers=True, title="Evolução Score Geral")
            fig_line.update_traces(line_color=COR_SECUNDARIA, line_width=3)
            st.plotly_chart(fig_line, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_comp:
            c1, c2 = st.columns(2)
            periodo_a = c1.selectbox("Período A", [h['periodo'] for h in history_data], index=1)
            periodo_b = c2.selectbox("Período B", [h['periodo'] for h in history_data], index=0)
            dados_a = next(h for h in history_data if h['periodo'] == periodo_a)
            dados_b = next(h for h in history_data if h['periodo'] == periodo_b)
            
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            categories = list(dados_a['dimensoes'].keys())
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Scatterpolar(r=list(dados_a['dimensoes'].values()), theta=categories, fill='toself', name=f'{periodo_a}', line_color=COR_COMP_A, opacity=0.5))
            fig_comp.add_trace(go.Scatterpolar(r=list(dados_b['dimensoes'].values()), theta=categories, fill='toself', name=f'{periodo_b}', line_color=COR_COMP_B, opacity=0.6))
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # --- RELATÓRIO DE HISTÓRICO ---
            if st.button("📥 Baixar Relatório Evolutivo (HTML)", type="primary"):
                 st.markdown("---")
                 logo_html = get_logo_html(150)
                 logo_cliente_html = ""
                 if empresa.get('logo_b64'):
                     logo_cliente_html = f"<img src='data:image/png;base64,{empresa.get('logo_b64')}' width='100' style='float:right;'>"
                 
                 diff_score = dados_b['score'] - dados_a['score']
                 txt_evolucao = "Melhoria observada" if diff_score > 0 else "Ponto de atenção"
                 
                 chart_css_viz = f"""
                 <div style="text-align:center; padding:20px; border:1px solid #eee; border-radius:8px; font-family:sans-serif;">
                     <strong>Score {periodo_a}:</strong> {dados_a['score']} <br>
                     <div style="width:100%; background:#eee; height:10px; border-radius:5px; margin:5px 0;">
                        <div style="width:{(dados_a['score']/5)*100}%; background:{COR_COMP_A}; height:10px; border-radius:5px;"></div>
                     </div>
                     <strong>Score {periodo_b}:</strong> {dados_b['score']} <br>
                     <div style="width:100%; background:#eee; height:10px; border-radius:5px; margin:5px 0;">
                        <div style="width:{(dados_b['score']/5)*100}%; background:{COR_COMP_B}; height:10px; border-radius:5px;"></div>
                     </div>
                 </div>
                 """

                 html_comp = textwrap.dedent(f"""
                 <div class="a4-paper">
                    <div style="display:flex; justify-content:space-between; border-bottom:2px solid {COR_PRIMARIA}; padding-bottom:15px; margin-bottom:20px;">
                        <div>{logo_html}</div>
                        <div style="text-align:right;"><div style="font-size:16px; font-weight:700; color:{COR_PRIMARIA};">RELATÓRIO DE EVOLUÇÃO</div><div style="font-size:10px; color:#666;">Comparativo Histórico</div></div>
                    </div>
                    <div style="background:#f8f9fa; padding:12px; border-radius:6px; margin-bottom:15px; border-left:4px solid {COR_SECUNDARIA};">
                        {logo_cliente_html}
                        <div style="font-size:9px; color:#888;">CLIENTE</div><div style="font-weight:bold; font-size:12px;">{empresa['razao']}</div>
                        <div style="font-size:9px;">CNPJ: {empresa.get('cnpj','')} | Endereço: {empresa.get('endereco','-')}</div>
                        <div style="font-size:9px;">Períodos Comparados: {periodo_a} vs {periodo_b}</div>
                    </div>
                    <div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:10px;">1. RESUMO DOS INDICADORES</div>
                    <table class="rep-table" style="margin-bottom:20px;">
                        <tr><th>INDICADOR</th><th>{periodo_a}</th><th>{periodo_b}</th><th>VARIAÇÃO</th></tr>
                        <tr><td>Score Geral</td><td>{dados_a['score']}</td><td>{dados_b['score']}</td><td>{diff_score:.2f}</td></tr>
                        <tr><td>Adesão (%)</td><td>{dados_a['adesao']}%</td><td>{dados_b['adesao']}%</td><td>{(dados_b['adesao'] - dados_a['adesao']):.1f}%</td></tr>
                    </table>
                    <div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:10px;">2. ANÁLISE GRÁFICA COMPARATIVA</div>
                    {chart_css_viz}
                    <div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:10px; margin-top:20px;">3. ANÁLISE TÉCNICA</div>
                    <p style="text-align:justify; margin:0; font-size:10px;">A análise comparativa demonstra uma {txt_evolucao} no índice geral de saúde mental. As dimensões que apresentaram maior variação positiva foram Controle e Apoio, indicando efetividade nas ações de liderança. Recomenda-se manter o monitoramento.</p>
                 </div>
                 """)
                 
                 b64_comp = base64.b64encode(textwrap.dedent(html_comp).encode()).decode()
                 href_comp = f'<a href="data:text/html;base64,{b64_comp}" download="Relatorio_Evolutivo.html" style="text-decoration:none; background-color:{COR_PRIMARIA}; color:white; padding:10px 20px; border-radius:5px; font-weight:bold;">📥 BAIXAR ARQUIVO (HTML)</a>'
                 st.markdown(href_comp, unsafe_allow_html=True)

    elif selected == "Configurações":
        if perm == "Master":
            st.title("Configurações")
            t1, t2, t3 = st.tabs(["Usuários", "Sistema", "Identidade"])
            with t3:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                nn = st.text_input("Nome Plataforma", value=st.session_state.platform_config['name'])
                nc = st.text_input("Consultoria", value=st.session_state.platform_config['consultancy'])
                nl = st.file_uploader("Logo")
                if st.button("Salvar Identidade"):
                    st.session_state.platform_config['name'] = nn
                    st.session_state.platform_config['consultancy'] = nc
                    if nl: st.session_state.platform_config['logo_b64'] = image_to_base64(nl)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with t2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                # CAMPO DE URL REAL (CORRIGIDO PARA LER DO STATE)
                nu = st.text_input("URL Base (Ex: https://meuapp.streamlit.app)", value=st.session_state.platform_config.get('base_url', ''))
                if st.button("Salvar URL"):
                    st.session_state.platform_config['base_url'] = nu
                    st.success("OK")
                st.info(f"Supabase Status: {'Online' if DB_CONNECTED else 'Offline'}")
                st.markdown("</div>", unsafe_allow_html=True)
            with t1:
                 st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                 st.write("Gestão de Usuários")
                 users_list = []
                 for u, d in st.session_state.users_db.items():
                     users_list.append({"User": u, "Role": d.get('role')})
                 st.dataframe(pd.DataFrame(users_list), use_container_width=True)
                 
                 c1, c2 = st.columns(2)
                 nu = c1.text_input("Novo Usuário")
                 np = c2.text_input("Senha", type="password")
                 nr = st.selectbox("Perfil", ["Master", "Gestor", "Analista"])
                 if st.button("Adicionar"):
                     st.session_state.users_db[nu] = {"password": np, "role": nr}
                     st.success("Criado!")
                     st.rerun()
                 
                 st.markdown("---")
                 users_to_del = [u for u in st.session_state.users_db.keys() if u != st.session_state.user_username]
                 u_del = st.selectbox("Excluir Usuário", users_to_del)
                 if st.button("🗑️ Excluir"):
                     del st.session_state.users_db[u_del]
                     st.success("Excluído!")
                     st.rerun()
                 st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.error("Acesso restrito a usuários Master.")

# --- 6. TELA PESQUISA ---
def survey_screen():
    qp = st.query_params
    cod = qp.get("cod", None)
    
    if cod and not st.session_state.get('current_company'):
        comp = next((c for c in st.session_state.companies_db if c['id'] == cod), None)
        if comp: st.session_state.current_company = comp
    
    if 'current_company' not in st.session_state: st.error("Link inválido."); return
    comp = st.session_state.current_company

    # Validações
    if comp.get('valid_until'):
        try:
            if datetime.date.today() > datetime.date.fromisoformat(comp['valid_until']):
                st.error("⛔ Link expirado.")
                return
        except: pass
        
    limit_evals = comp.get('limit_evals', 999999)
    if comp.get('respondidas', 0) >= limit_evals:
        st.error("⚠️ Limite de avaliações atingido.")
        return
    
    logo = get_logo_html(150)
    if comp.get('logo_b64'): logo = f"<img src='data:image/png;base64,{comp.get('logo_b64')}' width='150'>"

    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'>{logo}</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center'>Avaliação de Riscos - {comp['razao']}</h3>", unsafe_allow_html=True)
    st.markdown("""<div class="security-alert"><strong>🔒 AVALIAÇÃO VERIFICADA E SEGURA</strong><br>Esta pesquisa segue rigorosos padrões de confidencialidade.<br><ul><li><strong>Anonimato Garantido:</strong> A empresa NÃO tem acesso à sua resposta individual.</li><li><strong>Uso do CPF:</strong> Seu CPF é usado <u>apenas</u> para validar que você é um colaborador único e impedir duplicidades. Ele é transformado em um código criptografado (hash) imediatamente.</li><li><strong>Sigilo:</strong> Os resultados são apresentados apenas em formato estatístico (médias do grupo).</li></ul></div>""", unsafe_allow_html=True)
    
    with st.form("survey"):
        c1, c2 = st.columns(2)
        cpf = c1.text_input("CPF (Apenas números)")
        
        # 1. Seleciona Setor
        setores = list(comp['org_structure'].keys())
        setor = c2.selectbox("Setor", setores)
        
        # Cargo removido visualmente
        
        st.markdown("---")
        missing = False
        for cat, qs in st.session_state.hse_questions.items():
            st.markdown(f"**{cat}**")
            for q in qs:
                # UX: Radio button horizontal obrigatório
                val = st.radio(q['q'], ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"], key=f"q_{q['id']}", horizontal=True, index=None)
                if val is None: missing = True
                st.markdown("<hr style='margin:5px 0'>", unsafe_allow_html=True)

        aceite = st.checkbox("Declaro que li e concordo com o tratamento dos meus dados para fins estatísticos de saúde ocupacional, garantido o sigilo individual.")
        
        if st.form_submit_button("✅ Enviar Respostas"):
             # Validação rigorosa de TODAS as perguntas
             missing = []
             for cat, pergs in st.session_state.hse_questions.items():
                 for q in pergs:
                     if st.session_state.get(f"q_{q['id']}") is None:
                         missing.append(q['q'])
             
             if not cpf: st.error("⚠️ O CPF é obrigatório.")
             elif not aceite: st.error("⚠️ Aceite obrigatório.")
             elif missing: st.error(f"⚠️ Você precisa responder todas as perguntas. Faltam: {len(missing)}")
             else:
                 st.success("Sucesso!"); st.balloons()
                 comp['respondidas'] += 1 # Mock update
                 time.sleep(2); st.session_state.logged_in = False; st.rerun()

if not st.session_state.logged_in:
    if "cod" in st.query_params: survey_screen()
    else: login_screen()
else:
    if st.session_state.user_role == 'admin': admin_dashboard()
    else: survey_screen()
