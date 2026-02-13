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
from supabase import create_client, Client

# --- 1. CONEXÃO COM BANCO DE DADOS (SUPABASE) ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    DB_CONNECTED = True
except Exception as e:
    DB_CONNECTED = False

# --- CONFIGURAÇÃO INICIAL ---
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
COR_COMP_A = "#3498db" 
COR_COMP_B = "#9b59b6"

# --- 2. CSS OTIMIZADO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {{ background-color: {COR_FUNDO}; font-family: 'Inter', sans-serif; }}
    .block-container {{ padding-top: 2rem; padding-bottom: 3rem; }}
    [data-testid="stSidebar"] {{ background-color: #ffffff; border-right: 1px solid #e0e0e0; }}
    
    /* Cards KPI (Altura Automática) */
    .kpi-card {{
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04); border: 1px solid #f0f0f0;
        margin-bottom: 15px; display: flex; flex-direction: column; justify-content: space-between; 
        min-height: 120px; height: auto;
    }}
    .kpi-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }}
    .kpi-icon-box {{ width: 35px; height: 35px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }}
    .kpi-title {{ font-size: 12px; color: #7f8c8d; font-weight: 600; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value {{ font-size: 24px; font-weight: 700; color: {COR_PRIMARIA}; }}
    
    /* Cores Ícones */
    .bg-blue {{ background-color: #e3f2fd; color: #1976d2; }}
    .bg-green {{ background-color: #e8f5e9; color: #388e3c; }}
    .bg-orange {{ background-color: #fff3e0; color: #f57c00; }}
    .bg-red {{ background-color: #ffebee; color: #d32f2f; }}

    /* Containers */
    .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border: 1px solid #f0f0f0; margin-bottom: 15px; }}

    /* Caixa de Segurança */
    .security-alert {{
        padding: 1rem; background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc;
        border-left: 5px solid #0f5132; border-radius: 0.25rem; margin-bottom: 1.5rem; font-family: 'Inter', sans-serif;
    }}
    
    /* Relatório A4 */
    .a4-paper {{ 
        background: white; width: 210mm; min-height: 297mm; margin: auto; padding: 40px; 
        box-shadow: 0 0 20px rgba(0,0,0,0.1); color: #333; font-family: 'Inter', sans-serif; font-size: 11px; line-height: 1.5;
    }}
    .link-area {{ background-color: #f8f9fa; border: 1px dashed #dee2e6; padding: 15px; border-radius: 8px; font-family: monospace; color: #2c3e50; font-weight: bold; word-break: break-all; }}
    
    /* Tabelas Relatório */
    .rep-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 10px; }}
    .rep-table th {{ background-color: {COR_PRIMARIA}; color: white; padding: 8px; text-align: left; font-size: 9px; }}
    .rep-table td {{ border-bottom: 1px solid #eee; padding: 8px; vertical-align: top; }}
    
    /* Ajuste Slider (Régua) */
    div[data-testid="stSlider"] > div {{ padding-top: 0px; }}
    div[data-testid="stSlider"] label {{ font-size: 14px; font-weight: 600; color: {COR_PRIMARIA}; margin-bottom: 10px; }}

    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 0; width: 100%; }}
        .stApp {{ background-color: white; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DADOS (MOCKUP + SUPABASE) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": "admin", "cris": "123"}

if 'companies_db' not in st.session_state:
    st.session_state.companies_db = [
        {
            "id": "IND01", "razao": "Indústria Têxtil Fabril (Exemplo)", "cnpj": "00.000.000/0001-00", 
            "cnae": "00.00", "setor": "Industrial", "risco": 3, "func": 100, 
            "segmentacao": "GHE", "resp": "Gestor Exemplo", 
            "email": "exemplo@email.com", "telefone": "(11) 99999-9999", "endereco": "Av. Industrial, 1000 - SP",
            "logo_b64": None, "score": 2.8, "respondidas": 15,
            "dimensoes": {"Demandas": 2.1, "Controle": 3.8, "Suporte Gestor": 2.5, "Suporte Pares": 4.0, "Relacionamentos": 2.9, "Papel": 4.5, "Mudança": 3.0},
             "detalhe_perguntas": {},
             "setores_lista": ["Administrativo", "Produção", "Logística"],
             "cargos_lista": ["Analista", "Operador", "Gerente"]
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
            {"id": 18, "q": "Sou pressionado(a) por diferentes grupos?", "rev": True, "help": "Ex: Vários chefes ou departamentos pedindo coisas conflitantes."},
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
            {"id": 8, "q": "Recebo feedback sobre o trabalho que faço?", "rev": False, "help": "Ex: Saber se está indo bem ou mal."},
            {"id": 23, "q": "Posso contar com meu superior num problema?", "rev": False, "help": "Ex: O chefe ajuda a resolver ou diz 'se vira'?"},
            {"id": 29, "q": "Posso falar com meu superior sobre algo que me chateou?", "rev": False, "help": "Ex: Abertura para conversar sobre insatisfações."},
            {"id": 33, "q": "Sinto apoio do meu gestor(a)?", "rev": False, "help": "Ex: Sentir-se acolhido e não apenas cobrado."},
            {"id": 35, "q": "Meu gestor me incentiva no trabalho?", "rev": False, "help": "Ex: Elogios ou motivação para continuar."}
        ],
        "Suporte Pares": [
            {"id": 7, "q": "Recebo a ajuda e o apoio que preciso dos meus colegas?", "rev": False, "help": "Ex: Quando aperta, alguém te dá uma mão?"},
            {"id": 24, "q": "Recebo o respeito que mereço dos meus colegas?", "rev": False, "help": "Ex: Tratamento cordial e profissional."},
            {"id": 27, "q": "Meus colegas estão dispostos a me ouvir sobre problemas?", "rev": False, "help": "Ex: Ter com quem desabafar sobre o serviço."},
            {"id": 31, "q": "Meus colegas me ajudam em momentos difíceis?", "rev": False, "help": "Ex: Solidariedade quando você está sobrecarregado."}
        ],
        "Relacionamentos": [
            {"id": 5, "q": "Estou sujeito a assédio pessoal (palavras/comportamentos)?", "rev": True, "help": "Ex: Piadas ofensivas, gritos ou apelidos."},
            {"id": 14, "q": "Há atritos ou conflitos entre colegas?", "rev": True, "help": "Ex: Clima pesado, fofocas ou brigas."},
            {"id": 21, "q": "Estou sujeito a bullying?", "rev": True, "help": "Ex: Ser excluído ou ridicularizado sistematicamente."},
            {"id": 34, "q": "Os relacionamentos no trabalho são tensos?", "rev": True, "help": "Ex: Medo de falar com as pessoas."}
        ],
        "Papel": [
            {"id": 1, "q": "Sei claramente o que é esperado de mim?", "rev": False, "help": "Ex: Suas metas e funções são nítidas."},
            {"id": 4, "q": "Sei como fazer para executar meu trabalho?", "rev": False, "help": "Ex: Tenho o conhecimento e ferramentas necessárias."},
            {"id": 11, "q": "Sei quais são os objetivos do meu departamento?", "rev": False, "help": "Ex: Entender para onde a equipe está indo."},
            {"id": 13, "q": "Sei o quanto de responsabilidade tenho?", "rev": False, "help": "Ex: Clareza sobre até onde vai sua autoridade."},
            {"id": 17, "q": "Entendo como meu trabalho se encaixa no todo?", "rev": False, "help": "Ex: Ver sentido no que faz para a empresa."}
        ],
        "Mudança": [
            {"id": 26, "q": "Tenho oportunidade de questionar sobre mudanças?", "rev": False, "help": "Ex: Espaço para tirar dúvidas sobre novidades."},
            {"id": 28, "q": "Sou consultado(a) sobre mudanças no trabalho?", "rev": False, "help": "Ex: Opinar antes de mudarem seu processo."},
            {"id": 32, "q": "Quando mudanças são feitas, fica claro como funcionarão?", "rev": False, "help": "Ex: Comunicação clara sobre o 'novo jeito'."}
        ]
    }

if 'base_url' not in st.session_state: st.session_state.base_url = "http://localhost:8501" 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = None
if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False
if 'edit_id' not in st.session_state: st.session_state.edit_id = None

# --- 4. FUNÇÕES AUXILIARES ---
def generate_mock_history():
    """Gera dados históricos fictícios para a empresa IND01"""
    history = [
        {"periodo": "Jan/2025", "score": 2.8, "vidas": 120, "adesao": 85, "dimensoes": {"Demandas": 2.1, "Controle": 3.8, "Suporte Gestor": 2.5, "Suporte Pares": 4.0, "Relacionamentos": 2.9, "Papel": 4.5, "Mudança": 3.0}},
        {"periodo": "Jul/2024", "score": 2.4, "vidas": 115, "adesao": 70, "dimensoes": {"Demandas": 1.8, "Controle": 3.0, "Suporte Gestor": 2.2, "Suporte Pares": 3.8, "Relacionamentos": 2.5, "Papel": 4.0, "Mudança": 2.8}},
        {"periodo": "Jan/2024", "score": 3.1, "vidas": 110, "adesao": 90, "dimensoes": {"Demandas": 3.0, "Controle": 3.5, "Suporte Gestor": 3.0, "Suporte Pares": 3.5, "Relacionamentos": 3.2, "Papel": 3.5, "Mudança": 3.0}}
    ]
    return history

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
                if 'setores_lista' not in comp or not comp['setores_lista']: comp['setores_lista'] = ["Geral"]
                if 'cargos_lista' not in comp or not comp['cargos_lista']: comp['cargos_lista'] = ["Geral"]
            return companies, all_answers
        except: return st.session_state.companies_db, []
    else:
        # Mock responses
        mock_responses = []
        for c in st.session_state.companies_db:
             for _ in range(c['respondidas']):
                 mock_responses.append({"company_id": c['id'], "setor": random.choice(c.get('setores_lista', ['Geral'])), "score_simulado": random.uniform(2.0, 5.0) })
        return st.session_state.companies_db, mock_responses

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

# Função para converter gráfico Plotly em imagem base64
def fig_to_base64(fig):
    try:
        img_bytes = fig.to_image(format="png")
        encoded = base64.b64encode(img_bytes).decode()
        return f"data:image/png;base64,{encoded}"
    except:
        return None

def logout(): st.session_state.logged_in = False; st.session_state.user_role = None; st.rerun()

def kpi_card(title, value, icon, color_class):
    st.markdown(f"""<div class="kpi-card"><div class="kpi-top"><div class="kpi-icon-box {color_class}">{icon}</div><div class="kpi-value">{value}</div></div><div class="kpi-title">{title}</div></div>""", unsafe_allow_html=True)

# --- INTELIGÊNCIA HSE ---
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
    # 1. DEMANDAS
    if dimensoes.get("Demandas", 5) < 3.8:
        sugestoes.append({"acao": "Mapeamento de Carga", "estrat": "Realizar censo de tarefas por função para identificar gargalos.", "area": "Demandas"})
        sugestoes.append({"acao": "Matriz de Priorização", "estrat": "Treinar equipes na Matriz Eisenhower (Urgente x Importante).", "area": "Demandas"})
        sugestoes.append({"acao": "Política Desconexão", "estrat": "Regras sobre mensagens off-horário.", "area": "Demandas"})
        sugestoes.append({"acao": "Revisão de Prazos", "estrat": "Renegociar SLAs internos baseados na capacidade real.", "area": "Demandas"})
        sugestoes.append({"acao": "Pausas Cognitivas", "estrat": "Instituir pausas de 10 min a cada 2h.", "area": "Demandas"})
    # 2. CONTROLE
    if dimensoes.get("Controle", 5) < 3.8:
        sugestoes.append({"acao": "Job Crafting", "estrat": "Personalização do método de trabalho.", "area": "Controle"})
        sugestoes.append({"acao": "Banco de Horas Flexível", "estrat": "Flexibilidade entrada/saída.", "area": "Controle"})
        sugestoes.append({"acao": "Comitês Participativos", "estrat": "Incluir operacional no planejamento.", "area": "Controle"})
        sugestoes.append({"acao": "Autonomia na Agenda", "estrat": "Autogestão de tarefas não-críticas.", "area": "Controle"})
        sugestoes.append({"acao": "Delegação", "estrat": "Empoderar níveis menores para decisões.", "area": "Controle"})
    # 3. SUPORTE
    if dimensoes.get("Suporte Gestor", 5) < 3.8 or dimensoes.get("Suporte Pares", 5) < 3.8:
        sugestoes.append({"acao": "Liderança Segura", "estrat": "Capacitação em escuta ativa e empatia.", "area": "Suporte"})
        sugestoes.append({"acao": "Mentoria (Buddy System)", "estrat": "Padrinhos para novos colaboradores.", "area": "Suporte"})
        sugestoes.append({"acao": "Reuniões One-on-One", "estrat": "Feedbacks quinzenais de bem-estar.", "area": "Suporte"})
        sugestoes.append({"acao": "Grupos de Apoio", "estrat": "Troca de experiências entre pares.", "area": "Suporte"})
        sugestoes.append({"acao": "Feedback Estruturado", "estrat": "Cultura de feedback contínuo.", "area": "Suporte"})
    # 4. RELACIONAMENTOS
    if dimensoes.get("Relacionamentos", 5) < 3.8:
        sugestoes.append({"acao": "Tolerância Zero", "estrat": "Divulgar Código de Conduta e Ética.", "area": "Relacionamentos"})
        sugestoes.append({"acao": "Workshop CNV", "estrat": "Treinamento de Comunicação Não-Violenta.", "area": "Relacionamentos"})
        sugestoes.append({"acao": "Ouvidoria Externa", "estrat": "Canal anônimo para denúncias.", "area": "Relacionamentos"})
        sugestoes.append({"acao": "Mediação de Conflitos", "estrat": "Grupo para mediação precoce.", "area": "Relacionamentos"})
    # 5. PAPEL E MUDANÇA
    if dimensoes.get("Papel", 5) < 3.8:
        sugestoes.append({"acao": "Revisão Job Description", "estrat": "Clareza de responsabilidades.", "area": "Papel"})
        sugestoes.append({"acao": "Alinhamento de Metas", "estrat": "Revisão semestral de objetivos.", "area": "Papel"})
        sugestoes.append({"acao": "Onboarding", "estrat": "Reforço no treinamento inicial.", "area": "Papel"})
    if dimensoes.get("Mudança", 5) < 3.8:
        sugestoes.append({"acao": "Comunicação Transparente", "estrat": "Explicar o 'porquê' antes do 'como'.", "area": "Mudança"})
        sugestoes.append({"acao": "Consulta Prévia", "estrat": "Focus groups antes de mudanças.", "area": "Mudança"})
    
    if not sugestoes:
        sugestoes.append({"acao": "Manutenção do Clima", "estrat": "Pesquisas trimestrais.", "area": "Geral"})
        sugestoes.append({"acao": "Saúde Mental", "estrat": "Palestras sobre bem-estar.", "area": "Geral"})
    return sugestoes

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
                login_ok = False
                if DB_CONNECTED:
                    try:
                        res = supabase.table('admin_users').select("*").eq('username', user).eq('password', pwd).execute()
                        if res.data: login_ok = True
                    except: pass
                if not login_ok and user in st.session_state.users_db and st.session_state.users_db[user] == pwd:
                    login_ok = True
                
                if login_ok:
                    st.session_state.logged_in = True; st.session_state.user_role = 'admin'; st.rerun()
                else: st.error("Dados incorretos.")
        st.caption("Colaboradores: Utilizem o link fornecido pelo RH.")

def admin_dashboard():
    companies_data, responses_data = load_data_from_db()
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; margin-bottom:30px; margin-top:20px;'>{get_logo_html(160)}</div>", unsafe_allow_html=True)
        selected = option_menu(menu_title=None, options=["Visão Geral", "Empresas", "Gestão de Setores", "Gerar Link", "Relatórios", "Histórico & Comparativo", "Configurações"], icons=["grid", "building", "list-task", "link-45deg", "file-text", "clock-history", "gear"], default_index=0, styles={"nav-link-selected": {"background-color": COR_PRIMARIA}})
        st.markdown("---"); 
        if st.button("Sair", use_container_width=True): logout()

    if selected == "Visão Geral":
        st.title("Painel Administrativo")
        
        # Filtro Global
        lista_empresas = ["Todas"] + [c['razao'] for c in companies_data]
        empresa_filtro = st.selectbox("Filtrar por Empresa", lista_empresas)
        
        if empresa_filtro != "Todas":
            companies_filtered = [c for c in companies_data if c['razao'] == empresa_filtro]
            target_id = companies_filtered[0]['id']
            responses_filtered = [r for r in responses_data if r['company_id'] == target_id]
        else:
            companies_filtered = companies_data
            responses_filtered = responses_data

        total_resp = len(responses_filtered)
        total_vidas = sum(c['func'] for c in companies_filtered)
        pendentes = total_vidas - total_resp
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: kpi_card("Empresas", len(companies_filtered), "🏢", "bg-blue")
        with col2: kpi_card("Respondidas", total_resp, "✅", "bg-green")
        with col3: kpi_card("Pendentes", max(0, pendentes), "⏳", "bg-orange") 
        with col4: kpi_card("Alertas", 0, "🚨", "bg-red")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Radar HSE (Dimensões)")
            if companies_filtered:
                categories = list(st.session_state.hse_questions.keys())
                valores_radar = [3.5, 3.2, 4.0, 2.8, 4.5, 3.0, 3.5] # Mock visual ou média real
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(r=valores_radar, theta=categories, fill='toself', name='Média', line_color=COR_SECUNDARIA))
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=300, margin=dict(t=20, b=20))
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("Sem dados para exibir.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Resultados por Setor (Área)")
            if responses_filtered:
                df_resp = pd.DataFrame(responses_filtered)
                if 'setor' in df_resp.columns:
                    if 'score_simulado' not in df_resp.columns:
                        df_resp['score_simulado'] = [random.uniform(2.5, 4.8) for _ in range(len(df_resp))]
                    
                    df_setor = df_resp.groupby('setor')['score_simulado'].mean().reset_index()
                    fig_bar_setor = px.bar(df_setor, x='setor', y='score_simulado', title="Score Médio por Setor", color='score_simulado', color_continuous_scale='RdYlGn', range_y=[0, 5])
                    st.plotly_chart(fig_bar_setor, use_container_width=True)
                else:
                    st.info("Dados de setor não disponíveis.")
            else:
                st.info("Aguardando respostas para gerar gráficos.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c3, c4 = st.columns([1.5, 1])
        with c3:
             st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
             st.markdown("##### Distribuição Geral (Status)")
             if companies_filtered:
                 status_dist = {"Concluído": 0, "Em Andamento": 0}
                 for c in companies_filtered:
                     if c['respondidas'] >= c['func']: status_dist["Concluído"] += 1
                     else: status_dist["Em Andamento"] += 1
                 fig_pie = go.Figure(data=[go.Pie(labels=list(status_dist.keys()), values=list(status_dist.values()), hole=.6)])
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
                    seg_opts = ["GHE", "Setor", "GES"]
                    idx_seg = seg_opts.index(emp_edit['segmentacao']) if emp_edit['segmentacao'] in seg_opts else 0
                    new_seg = c6.selectbox("Segmentação", seg_opts, index=idx_seg)
                    c7, c8, c9 = st.columns(3)
                    new_resp = c7.text_input("Responsável", value=emp_edit['resp'])
                    new_email = c8.text_input("E-mail Resp.", value=emp_edit.get('email',''))
                    new_tel = c9.text_input("Telefone Resp.", value=emp_edit.get('telefone',''))
                    new_end = st.text_input("Endereço Completo", value=emp_edit.get('endereco',''))
                    if st.form_submit_button("💾 Salvar Alterações"):
                        emp_edit.update({'razao': new_razao, 'cnpj': new_cnpj, 'cnae': new_cnae, 'risco': new_risco, 'func': new_func, 'segmentacao': new_seg, 'resp': new_resp, 'email': new_email, 'telefone': new_tel, 'endereco': new_end})
                        st.session_state.edit_mode = False; st.session_state.edit_id = None; st.success("Atualizado!"); st.rerun()
                if st.button("Cancelar"): st.session_state.edit_mode = False; st.rerun()
        else:
            tab1, tab2 = st.tabs(["Lista", "Novo Cadastro"])
            with tab1:
                if st.session_state.companies_db:
                    for idx, emp in enumerate(st.session_state.companies_db):
                        with st.expander(f"🏢 {emp['razao']} (ID: {emp['id']})"):
                            c1, c2, c3, c4 = st.columns(4)
                            c1.write(f"**CNPJ:** {emp['cnpj']}")
                            c2.write(f"**Resp:** {emp['resp']}")
                            pendentes = emp['func'] - emp['respondidas']
                            c3.write(f"**Vidas:** {emp['func']} | **Pendentes:** {pendentes}")
                            c4_1, c4_2 = c4.columns(2)
                            if c4_1.button("✏️", key=f"ed_{idx}"): st.session_state.edit_mode = True; st.session_state.edit_id = emp['id']; st.rerun()
                            if c4_2.button("🗑️", key=f"del_{idx}"): st.session_state.companies_db.pop(idx); st.success("Excluído!"); st.rerun()
                else: st.info("Nenhuma empresa cadastrada.")
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
                    email = c9.text_input("E-mail Resp.")
                    c10, c11 = st.columns(2)
                    tel = c10.text_input("Telefone Resp.")
                    end = c11.text_input("Endereço Completo")
                    logo_cliente = st.file_uploader("Logo Cliente", type=['png', 'jpg'])
                    if st.form_submit_button("Salvar no Banco de Dados"):
                        logo_str = image_to_base64(logo_cliente)
                        new_c = {"id": cod, "razao": razao, "cnpj": cnpj, "cnae": cnae, "setor": "Geral", "risco": risco, "func": func, "segmentacao": segmentacao, "resp": resp, "email": email, "telefone": tel, "endereco": end, "logo_b64": logo_str, "score": 0, "respondidas": 0, "dimensoes": {}, "detalhe_perguntas": {}, "setores_lista": ["Geral"], "cargos_lista": ["Geral"]}
                        st.session_state.companies_db.append(new_c)
                        st.success("Salvo!"); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Gestão de Setores":
        st.title("Gestão de Setores")
        if not st.session_state.companies_db: st.warning("Cadastre uma empresa."); return
        empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
        empresa_idx = next((i for i, item in enumerate(st.session_state.companies_db) if item["razao"] == empresa_nome), None)
        if empresa_idx is not None:
            empresa = st.session_state.companies_db[empresa_idx]
            
            # Garante que as listas existam
            if 'setores_lista' not in empresa or not empresa['setores_lista']: empresa['setores_lista'] = ["Geral"]
            if 'cargos_lista' not in empresa or not empresa['cargos_lista']: empresa['cargos_lista'] = ["Geral"]

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.subheader("📂 Setores")
                edit_setores = st.data_editor(pd.DataFrame({"Setor": empresa['setores_lista']}), num_rows="dynamic", key="ed_set")
                if st.button("Salvar Setores"):
                    st.session_state.companies_db[empresa_idx]['setores_lista'] = edit_setores["Setor"].dropna().tolist()
                    st.success("Setores atualizados!")
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.subheader("💼 Cargos (Interno)")
                st.caption("Cargos são usados apenas para controle interno do RH.")
                edit_cargos = st.data_editor(pd.DataFrame({"Cargo": empresa['cargos_lista']}), num_rows="dynamic", key="ed_carg")
                if st.button("Salvar Cargos"):
                    st.session_state.companies_db[empresa_idx]['cargos_lista'] = edit_cargos["Cargo"].dropna().tolist()
                    st.success("Cargos atualizados!")
                st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Gerar Link":
        st.title("Gerar Link & Testar")
        if not st.session_state.companies_db: st.warning("Cadastre uma empresa."); return
        with st.container():
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
            empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_nome)
            link_final = f"{st.session_state.base_url}/?cod={empresa['id']}"
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("##### Link de Acesso")
                st.markdown(f"<div class='link-box'>{link_final}</div>", unsafe_allow_html=True)
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

    # --- HISTÓRICO & COMPARATIVO (MANTIDO E MELHORADO) ---
    elif selected == "Histórico & Comparativo":
        st.title("Histórico & Comparativo")
        if not st.session_state.companies_db: st.warning("Cadastre empresas."); return
        
        empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in st.session_state.companies_db])
        empresa = next(c for c in st.session_state.companies_db if c['razao'] == empresa_nome)
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
            
            # --- RELATÓRIO DE HISTÓRICO EM PDF (CORRIGIDO) ---
            if st.button("🖨️ Gerar Relatório Comparativo (PDF)", type="primary"):
                 st.markdown("---")
                 logo_html = get_logo_html(150)
                 logo_cliente_html = ""
                 if empresa.get('logo_b64'):
                     logo_cliente_html = f"<img src='data:image/png;base64,{empresa.get('logo_b64')}' width='100' style='float:right;'>"
                 
                 diff_score = dados_b['score'] - dados_a['score']
                 txt_evolucao = "Melhoria observada" if diff_score > 0 else "Ponto de atenção"

                 # HTML DEDENT PARA EVITAR ERRO DE RENDERIZAÇÃO
                 html_comp = textwrap.dedent(f"""
                 <div class="a4-paper">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid {COR_PRIMARIA}; padding-bottom:15px; margin-bottom:20px;">
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
                    <div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:10px;">2. ANÁLISE TÉCNICA</div>
                    <p style="text-align:justify; margin:0; font-size:10px;">A análise comparativa demonstra uma {txt_evolucao} no índice geral de saúde mental. As dimensões que apresentaram maior variação positiva foram Controle e Apoio, indicando efetividade nas ações de liderança. Recomenda-se manter o monitoramento.</p>
                 </div>
                 """)
                 st.markdown(html_comp, unsafe_allow_html=True)
                 st.info("Pressione Ctrl+P para salvar como PDF.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Relatórios":
        st.title("Relatórios e Laudos")
        if not st.session_state.companies_db: st.warning("Cadastre empresas."); return
        c_sel, c_blank = st.columns([1, 1])
        with c_sel:
            empresa_sel = st.selectbox("Cliente", [e['razao'] for e in st.session_state.companies_db])
        empresa = next(e for e in st.session_state.companies_db if e['razao'] == empresa_sel)
        
        with st.sidebar:
            st.markdown("---"); st.markdown("#### Assinaturas")
            sig_empresa_nome = st.text_input("Nome Resp. Empresa", value=empresa.get('resp',''))
            sig_empresa_cargo = st.text_input("Cargo Resp. Empresa", value="Diretor(a)")
            sig_tecnico_nome = st.text_input("Nome Resp. Técnico", value="Cristiane C. Lima")
            sig_tecnico_cargo = st.text_input("Cargo Resp. Técnico", value="Consultora Pessin Gestão")

        dimensoes_atuais = empresa.get('dimensoes', {})
        analise_auto = gerar_analise_robusta(dimensoes_atuais)
        sugestoes_auto = gerar_banco_sugestoes(dimensoes_atuais)

        with st.expander("📝 Editar Conteúdo Técnico", expanded=True):
            st.markdown("##### 1. Conclusão Técnica")
            analise_texto = st.text_area("Texto do Relatório:", value=analise_auto, height=150)
            st.markdown("---")
            st.markdown("##### 2. Seleção de Ações Sugeridas")
            opcoes_formatadas = [f"[{s['area']}] {s['acao']}: {s['estrat']}" for s in sugestoes_auto]
            selecionadas = st.multiselect("Banco de Sugestões:", options=opcoes_formatadas)
            if st.button("⬇️ Adicionar à Tabela"):
                novas = []
                for sel in selecionadas:
                    for s in sugestoes_auto:
                        if f"[{s['area']}] {s['acao']}: {s['estrat']}" == sel:
                            novas.append({"acao": s['acao'], "estrat": s['estrat'], "area": s['area'], "resp": "A Definir", "prazo": "30 dias"})
                if 'acoes_list' not in st.session_state: st.session_state.acoes_list = []
                st.session_state.acoes_list.extend(novas)
                st.success("Adicionado!")
            
            if 'acoes_list' not in st.session_state: st.session_state.acoes_list = []
            st.markdown("##### 3. Tabela Final")
            edited_df = st.data_editor(pd.DataFrame(st.session_state.acoes_list), num_rows="dynamic", use_container_width=True, column_config={"acao": "Ação", "estrat": st.column_config.TextColumn("Estratégia", width="large"), "area": "Área", "resp": "Responsável", "prazo": "Prazo"})
            if not edited_df.empty: st.session_state.acoes_list = edited_df.to_dict('records')

        if st.button("🖨️ Gerar Relatório (PDF)", type="primary"):
            st.markdown("---")
            logo_html = get_logo_html(150)
            logo_cliente_html = ""
            if empresa.get('logo_b64'):
                logo_cliente_html = f"<img src='data:image/png;base64,{empresa.get('logo_b64')}' width='100' style='float:right;'>"
            
            plat_name = st.session_state.platform_config['name']
            
            html_dimensoes = ""
            if empresa.get('dimensoes'):
                for dim, nota in empresa.get('dimensoes', {}).items():
                    cor = COR_RISCO_ALTO if nota < 3 else (COR_RISCO_MEDIO if nota < 4 else COR_RISCO_BAIXO)
                    txt = "CRÍTICO" if nota < 3 else ("ATENÇÃO" if nota < 4 else "SEGURO")
                    html_dimensoes += f'<div style="flex:1; min-width:90px; background:#f8f9fa; border:1px solid #eee; padding:8px; border-radius:6px; margin:3px; text-align:center;"><div style="font-size:8px; color:#666; text-transform:uppercase;">{dim}</div><div style="font-size:14px; font-weight:bold; color:{cor};">{nota}</div><div style="font-size:7px; color:#888;">{txt}</div></div>'

            html_raio_x = ""
            perguntas_exibicao = empresa.get('detalhe_perguntas', {})
            if not perguntas_exibicao:
                 for cat, pergs in st.session_state.hse_questions.items():
                    for q in pergs: perguntas_exibicao[q['q']] = random.randint(10, 60)
            
            for perg, pct in perguntas_exibicao.items():
                cor_bar = COR_RISCO_ALTO if pct > 50 else (COR_RISCO_MEDIO if pct > 30 else COR_RISCO_BAIXO)
                html_raio_x += f'<div style="margin-bottom:4px;"><div style="display:flex; justify-content:space-between; font-size:9px;"><span>{perg}</span><span>{pct}% Risco</span></div><div style="width:100%; background:#f0f0f0; height:5px; border-radius:2px;"><div style="width:{pct}%; background:{cor_bar}; height:100%; border-radius:2px;"></div></div></div>'

            html_acoes = "".join([f"<tr><td>{i.get('acao','')}</td><td>{i.get('estrat','-')}</td><td>{i.get('area','')}</td><td>{i.get('resp','')}</td><td>{i.get('prazo','')}</td></tr>" for i in st.session_state.acoes_list])

            # RENDERIZAÇÃO DE GRÁFICOS NO RELATÓRIO
            # Radar
            categories = list(empresa.get('dimensoes', {}).keys())
            values = list(empresa.get('dimensoes', {}).values())
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='Média', line_color=COR_SECUNDARIA))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=300, margin=dict(t=20, b=20))
            img_radar = fig_to_base64(fig_radar)
            html_radar = f'<img src="{img_radar}" width="100%">' if img_radar else "Gráfico indisponível"

            # Score Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = empresa['score'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 5], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': COR_SECUNDARIA},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 2.5], 'color': '#ffebee'},
                        {'range': [2.5, 3.5], 'color': '#fff3e0'},
                        {'range': [3.5, 5], 'color': '#e8f5e9'}],
                    }))
            fig_gauge.update_layout(height=250, margin=dict(t=0, b=0, l=20, r=20))
            img_gauge = fig_to_base64(fig_gauge)
            html_gauge = f'<img src="{img_gauge}" width="100%">' if img_gauge else "Gráfico indisponível"

            raw_html = f"""
<div class="a4-paper">
<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid {COR_PRIMARIA}; padding-bottom:15px; margin-bottom:20px;">
<div>{logo_html}</div>
<div style="text-align:right;"><div style="font-size:16px; font-weight:700; color:{COR_PRIMARIA};">LAUDO TÉCNICO HSE-IT</div><div style="font-size:10px; color:#666;">NR-01 / Riscos Psicossociais</div></div>
</div>
<div style="background:#f8f9fa; padding:12px; border-radius:6px; margin-bottom:15px; border-left:4px solid {COR_SECUNDARIA};">
{logo_cliente_html}
<div style="font-size:9px; color:#888;">CLIENTE</div><div style="font-weight:bold; font-size:12px;">{empresa['razao']}</div>
<div style="font-size:9px;">CNPJ: {empresa.get('cnpj','')} | Endereço: {empresa.get('endereco','-')}</div>
<div style="font-size:9px;">Adesão: {empresa['respondidas']} Vidas | Data: {datetime.datetime.now().strftime('%d/%m/%Y')}</div>
</div>
<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">1. OBJETIVO E METODOLOGIA</div>
<p style="text-align:justify; margin:0; font-size:10px;">Este relatório tem como objetivo identificar os fatores de risco psicossocial no ambiente de trabalho, utilizando a ferramenta <strong>HSE Management Standards Indicator Tool</strong>, atendendo às exigências da NR-01. A metodologia avalia 7 dimensões: Demanda, Controle, Suporte (Gestor/Pares), Relacionamentos, Papel e Mudança.</p>

<div style="display:flex; gap:20px; margin-top:15px;">
    <div style="flex:1;">
        <div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">2. SCORE GERAL</div>
        {html_gauge}
    </div>
    <div style="flex:1;">
        <div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">3. RADAR DAS DIMENSÕES</div>
        {html_radar}
    </div>
</div>

<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-top:15px; margin-bottom:5px;">4. DIAGNÓSTICO DETALHADO (DIMENSÕES)</div>
<div style="display:flex; flex-wrap:wrap; margin-bottom:15px;">{html_dimensoes}</div>
<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">5. RAIO-X (PERGUNTAS CRÍTICAS)</div>
<div style="background:white; border:1px solid #eee; padding:10px; border-radius:6px; margin-bottom:15px; column-count:2; column-gap:20px; font-size:9px;">{html_raio_x}</div>
<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">6. PLANO DE AÇÃO ESTRATÉGICO</div>
<table class="rep-table" style="margin-bottom:15px;">
<thead><tr><th>AÇÃO</th><th>ESTRATÉGIA (COMO)</th><th>ÁREA</th><th>RESP.</th><th>PRAZO</th></tr></thead>
<tbody>{html_acoes}</tbody>
</table>
<div style="font-size:11px; font-weight:700; color:{COR_PRIMARIA}; border-left:3px solid {COR_SECUNDARIA}; padding-left:5px; margin-bottom:5px;">7. CONCLUSÃO TÉCNICA</div>
<p style="text-align:justify; margin:0; font-size:10px;">{analise_texto}</p>
<div style="margin-top:40px; display:flex; justify-content:space-between; gap:30px;">
<div style="flex:1; text-align:center; border-top:1px solid #ccc; padding-top:5px;"><strong>{sig_empresa_nome}</strong><br><span style="color:#666; font-size:9px;">{sig_empresa_cargo}</span></div>
<div style="flex:1; text-align:center; border-top:1px solid #ccc; padding-top:5px;"><strong>{sig_tecnico_nome}</strong><br><span style="color:#666; font-size:9px;">{sig_tecnico_cargo}</span></div>
</div>
</div>
"""
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
                    st.success("Salvo (Local)!")
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
        if DB_CONNECTED:
            try:
                res = supabase.table('companies').select("*").eq('id', cod_url).execute()
                if res.data: st.session_state.current_company = res.data[0]
            except: pass
        else:
            company = next((c for c in st.session_state.companies_db if c['id'] == cod_url), None)
            if company: st.session_state.current_company = company
    
    if 'current_company' not in st.session_state:
        st.error("Link inválido."); return

    comp = st.session_state.current_company
    logo_show = get_logo_html(150)
    # Tenta pegar logo do banco ou local
    logo_cli = comp.get('logo_b64')
    if logo_cli:
        logo_show = f"<img src='data:image/png;base64,{logo_cli}' width='150'>"
    
    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'>{logo_show}</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center'>Avaliação de Riscos - {comp['razao']}</h3>", unsafe_allow_html=True)
    
    st.markdown("""<div class="security-alert"><strong>🔒 AVALIAÇÃO VERIFICADA E SEGURA</strong><br>Esta pesquisa segue rigorosos padrões de confidencialidade.<br><ul><li><strong>Anonimato Garantido:</strong> A empresa NÃO tem acesso à sua resposta individual.</li><li><strong>Uso do CPF:</strong> Seu CPF é usado <u>apenas</u> para validar que você é um colaborador único e impedir duplicidades. Ele é transformado em um código criptografado (hash) imediatamente.</li><li><strong>Sigilo:</strong> Os resultados são apresentados apenas em formato estatístico (médias do grupo).</li></ul></div>""", unsafe_allow_html=True)

    with st.form("survey_form"):
        c1, c2 = st.columns(2)
        cpf = c1.text_input("CPF (Apenas números)", max_chars=11)
        
        # CARREGAMENTO INTELIGENTE DE OPÇÕES
        lista_setores = comp.get('setores_lista', ["Geral"])
        if isinstance(lista_setores, str): lista_setores = ["Geral"] # Fallback se vier string

        setor = c2.selectbox("Setor", lista_setores)
        
        st.markdown("---")
        
        aceite_lgpd = st.checkbox("Declaro que li e concordo com o tratamento dos meus dados para fins estatísticos de saúde ocupacional, garantido o sigilo individual.")

        tabs = st.tabs(list(st.session_state.hse_questions.keys()))
        for i, (cat, pergs) in enumerate(st.session_state.hse_questions.items()):
            with tabs[i]:
                st.markdown(f"**{cat}**")
                for q in pergs:
                    options = ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"] if q['id']<=24 else ["Discordo Totalmente", "Discordo", "Neutro", "Concordo", "Concordo Totalmente"]
                    st.select_slider(
                        label=f"**{q['q']}**",
                        options=options,
                        key=f"q_{q['id']}",
                        help=f"{q['help']}" 
                    )
                    st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        
        if st.form_submit_button("✅ Enviar Respostas"):
            if not cpf: 
                st.error("⚠️ O CPF é obrigatório para validação.")
            elif not aceite_lgpd:
                st.error("⚠️ Você precisa concordar com o termo de consentimento LGPD para enviar.")
            else:
                if DB_CONNECTED:
                    try:
                        answers = {k: v for k,v in st.session_state.items() if k.startswith("q_")}
                        supabase.table('responses').insert({
                            "company_id": comp['id'],
                            "cpf_hash": hashlib.sha256(cpf.encode()).hexdigest(),
                            "setor": setor,
                            "answers": answers
                        }).execute()
                        st.success("Enviado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
                else:
                    st.success("Enviado (Simulação Local)!")
                
                time.sleep(2)
                st.session_state.logged_in = False
                st.rerun()

if not st.session_state.logged_in:
    if "cod" in st.query_params: survey_screen()
    else: login_screen()
else:
    if st.session_state.user_role == 'admin': admin_dashboard()
    else: survey_screen()
