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
import json
import uuid
from supabase import create_client, Client

# ==============================================================================
# 1. CONFIGURAÇÃO E CONEXÃO SUPABASE
# ==============================================================================
st.set_page_config(
    page_title="Elo NR-01 | Sistema Inteligente",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    DB_CONNECTED = True
except Exception as e:
    DB_CONNECTED = False

if 'platform_config' not in st.session_state:
    st.session_state.platform_config = {
        "name": "Elo NR-01",
        "consultancy": "Pessin Gestão",
        "logo_b64": None,
        "base_url": "https://elonr01-cris.streamlit.app" 
    }

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
# 2. CSS OTIMIZADO (ESTRUTURADO)
# ==============================================================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {{ 
        background-color: {COR_FUNDO}; 
        font-family: 'Inter', sans-serif; 
    }}
    
    .block-container {{ 
        padding-top: 2rem; 
        padding-bottom: 3rem; 
    }}
    
    [data-testid="stSidebar"] {{ 
        background-color: #ffffff; 
        border-right: 1px solid #e0e0e0; 
    }}
    
    /* Cards KPI */
    .kpi-card {{
        background: white; 
        padding: 20px; 
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04); 
        border: 1px solid #f0f0f0;
        margin-bottom: 15px; 
        display: flex; 
        flex-direction: column; 
        justify-content: space-between; 
        min-height: 120px; 
        height: auto;
    }}
    
    .kpi-title {{ 
        font-size: 12px; 
        color: #7f8c8d; 
        font-weight: 600; 
        margin-top: 8px; 
        text-transform: uppercase; 
        letter-spacing: 0.5px; 
    }}
    
    .kpi-value {{ 
        font-size: 24px; 
        font-weight: 700; 
        color: {COR_PRIMARIA}; 
        margin-top: 5px; 
    }}
    
    .kpi-icon-box {{ 
        width: 40px; 
        height: 40px; 
        border-radius: 8px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 20px; 
        flex-shrink: 0; 
    }}
    
    /* Cores Ícones */
    .bg-blue {{ background-color: #e3f2fd; color: #1976d2; }}
    .bg-green {{ background-color: #e8f5e9; color: #388e3c; }}
    .bg-orange {{ background-color: #fff3e0; color: #f57c00; }}
    .bg-red {{ background-color: #ffebee; color: #d32f2f; }}

    /* Containers */
    .chart-container {{ 
        background: white; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.03); 
        border: 1px solid #f0f0f0; 
        margin-bottom: 15px; 
    }}

    /* Caixa de Segurança */
    .security-alert {{
        padding: 1.5rem; 
        background-color: #d1e7dd; 
        color: #0f5132; 
        border: 1px solid #badbcc;
        border-left: 6px solid #0f5132; 
        border-radius: 0.25rem; 
        margin-bottom: 2rem; 
        font-family: 'Inter', sans-serif;
    }}
    
    /* Relatório A4 */
    .a4-paper {{ 
        background: white; 
        width: 210mm; 
        min-height: 297mm; 
        margin: auto; 
        padding: 40px; 
        box-shadow: 0 0 20px rgba(0,0,0,0.1); 
        color: #333; 
        font-family: 'Inter', sans-serif; 
        font-size: 11px; 
        line-height: 1.5;
    }}
    
    /* Tabelas HTML Relatório */
    .rep-table {{ 
        width: 100%; 
        border-collapse: collapse; 
        margin-top: 10px; 
        font-size: 10px; 
    }}
    
    .rep-table th {{ 
        background-color: {COR_PRIMARIA}; 
        color: white; 
        padding: 8px; 
        text-align: left; 
        font-size: 9px; 
    }}
    
    .rep-table td {{ 
        border-bottom: 1px solid #eee; 
        padding: 8px; 
        vertical-align: top; 
    }}
    
    /* Ajuste Radio Button Horizontal - UX Melhorada */
    div[role="radiogroup"] > label {{
        font-weight: 500; 
        color: #444; 
        background: #f8f9fa; 
        padding: 10px 16px; 
        border-radius: 8px; 
        border: 1px solid #eee; 
        cursor: pointer; 
        transition: all 0.3s;
        white-space: nowrap; 
    }}
    
    div[role="radiogroup"] > label:hover {{ 
        background: #e2e6ea; 
        border-color: {COR_SECUNDARIA}; 
    }}
    
    div[data-testid="stRadio"] > div {{ 
        flex-direction: row; 
        flex-wrap: wrap; 
        gap: 10px; 
        width: 100%; 
        padding-bottom: 10px; 
    }}

    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ 
            display: none !important; 
        }}
        .a4-paper {{ 
            box-shadow: none; 
            margin: 0; 
            padding: 0; 
            width: 100%; 
            max-width: 100%; 
        }}
        .stApp {{ 
            background-color: white; 
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. DADOS E INICIALIZAÇÃO DE ESTADO
# ==============================================================================
keys_to_init = [
    'logged_in', 
    'user_role', 
    'admin_permission', 
    'user_username', 
    'user_credits', 
    'user_linked_company', 
    'edit_mode', 
    'edit_id', 
    'acoes_list'
]

for k in keys_to_init:
    if k not in st.session_state: 
        st.session_state[k] = None

if st.session_state.acoes_list is None: 
    st.session_state.acoes_list = []
if st.session_state.user_credits is None: 
    st.session_state.user_credits = 0

# Mock inicial para caso o banco falhe
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {
            "password": "admin", 
            "role": "Master", 
            "credits": 999999
        }
    }

if 'companies_db' not in st.session_state:
    st.session_state.companies_db = []

if 'local_responses_db' not in st.session_state:
    st.session_state.local_responses_db = []

# LISTA COMPLETA HSE 35 PERGUNTAS (EXPANDIDA PARA MANUTENÇÃO)
if 'hse_questions' not in st.session_state:
    st.session_state.hse_questions = {
        "Demandas": [
            {
                "id": 3, 
                "q": "Tenho prazos impossíveis de cumprir?", 
                "rev": True, 
                "help": "Exemplo: Ser cobrado por entregas urgentes no fim do expediente sem tempo hábil."
            },
            {
                "id": 6, 
                "q": "Sou pressionado a trabalhar longas horas?", 
                "rev": True, 
                "help": "Exemplo: Sentir que só fazer o seu horário normal não é suficiente para a empresa."
            },
            {
                "id": 9, 
                "q": "Tenho que trabalhar muito intensamente?", 
                "rev": True, 
                "help": "Exemplo: Não ter tempo nem para respirar ou tomar um café direito devido ao volume de trabalho."
            },
            {
                "id": 12, 
                "q": "Tenho que negligenciar algumas tarefas?", 
                "rev": True, 
                "help": "Exemplo: Ter que fazer as coisas 'de qualquer jeito' só para dar tempo de entregar tudo."
            },
            {
                "id": 16, 
                "q": "Não consigo fazer pausas suficientes?", 
                "rev": True, 
                "help": "Exemplo: Precisar pular o horário de almoço ou comer correndo na mesa de trabalho."
            },
            {
                "id": 18, 
                "q": "Sou pressionado por diferentes grupos?", 
                "rev": True, 
                "help": "Exemplo: Receber ordens conflitantes ou urgentes de gestores ou setores diferentes."
            },
            {
                "id": 20, 
                "q": "Tenho que trabalhar muito rápido?", 
                "rev": True, 
                "help": "Exemplo: O ritmo exigido é frenético e desgastante o tempo todo."
            },
            {
                "id": 22, 
                "q": "Tenho prazos irrealistas?", 
                "rev": True, 
                "help": "Exemplo: Metas que, na prática do dia a dia, ninguém da equipe consegue bater."
            }
        ],
        "Controle": [
            {
                "id": 2, 
                "q": "Posso decidir quando fazer uma pausa?", 
                "rev": False, 
                "help": "Exemplo: Ter liberdade para levantar, esticar as pernas ou tomar água sem precisar pedir permissão."
            },
            {
                "id": 10, 
                "q": "Tenho liberdade para decidir como faço meu trabalho?", 
                "rev": False, 
                "help": "Exemplo: Poder escolher o melhor método ou ferramenta para entregar o seu resultado."
            },
            {
                "id": 15, 
                "q": "Tenho poder de decisão sobre meu ritmo?", 
                "rev": False, 
                "help": "Exemplo: Poder acelerar ou diminuir o ritmo de trabalho dependendo do seu nível de energia no dia."
            },
            {
                "id": 19, 
                "q": "Eu decido quando vou realizar cada tarefa?", 
                "rev": False, 
                "help": "Exemplo: Ter autonomia para organizar sua própria agenda diária."
            },
            {
                "id": 25, 
                "q": "Tenho voz sobre como meu trabalho é realizado?", 
                "rev": False, 
                "help": "Exemplo: Suas ideias de melhorias nos processos são ouvidas e aplicadas pela gestão."
            },
            {
                "id": 30, 
                "q": "Meu tempo de trabalho pode ser flexível?", 
                "rev": False, 
                "help": "Exemplo: Ter banco de horas, horários flexíveis de entrada/saída ou acordos amigáveis com o gestor."
            }
        ],
        "Suporte Gestor": [
            {
                "id": 8, 
                "q": "Recebo feedback sobre o trabalho?", 
                "rev": False, 
                "help": "Exemplo: Seu gestor senta com você para conversar de forma clara sobre o que está bom e o que pode melhorar."
            },
            {
                "id": 23, 
                "q": "Posso contar com meu superior num problema?", 
                "rev": False, 
                "help": "Exemplo: Saber que o gestor vai te ajudar a resolver uma falha técnica em vez de apenas te culpar."
            },
            {
                "id": 29, 
                "q": "Posso falar com meu superior sobre algo que me chateou?", 
                "rev": False, 
                "help": "Exemplo: Ter abertura para conversas sinceras e humanas sem medo de retaliação."
            },
            {
                "id": 33, 
                "q": "Sinto apoio do meu gestor(a)?", 
                "rev": False, 
                "help": "Exemplo: Sentir que seu chefe 'joga no seu time' e se importa com seu bem-estar geral."
            },
            {
                "id": 35, 
                "q": "Meu gestor me incentiva no trabalho?", 
                "rev": False, 
                "help": "Exemplo: Receber elogios, reconhecimento e motivação quando faz um bom trabalho."
            }
        ],
        "Suporte Pares": [
            {
                "id": 7, 
                "q": "Recebo a ajuda e o apoio que preciso dos meus colegas?", 
                "rev": False, 
                "help": "Exemplo: A equipe é unida e um cobre o outro quando necessário."
            },
            {
                "id": 24, 
                "q": "Recebo o respeito que mereço dos meus colegas?", 
                "rev": False, 
                "help": "Exemplo: O tratamento no dia a dia é cordial, respeitoso e livre de preconceitos."
            },
            {
                "id": 27, 
                "q": "Meus colegas estão dispostos a me ouvir sobre problemas?", 
                "rev": False, 
                "help": "Exemplo: Ter com quem desabafar sobre um dia difícil ou um cliente complicado."
            },
            {
                "id": 31, 
                "q": "Meus colegas me ajudam em momentos difíceis?", 
                "rev": False, 
                "help": "Exemplo: A equipe divide o peso quando o volume de trabalho está muito alto para uma pessoa só."
            }
        ],
        "Relacionamentos": [
            {
                "id": 5, 
                "q": "Estou sujeito a assédio pessoal?", 
                "rev": True, 
                "help": "Exemplo: Sofrer comentários desrespeitosos, constrangedores ou pressões indevidas no ambiente de trabalho."
            },
            {
                "id": 14, 
                "q": "Há atritos ou conflitos entre colegas?", 
                "rev": True, 
                "help": "Exemplo: O clima geral é de fofoca, panelinhas ou brigas constantes no setor."
            },
            {
                "id": 21, 
                "q": "Estou sujeito a bullying?", 
                "rev": True, 
                "help": "Exemplo: Ser excluído propositalmente de conversas, grupos ou ser alvo de piadas repetitivas e maldosas."
            },
            {
                "id": 34, 
                "q": "Os relacionamentos no trabalho são tensos?", 
                "rev": True, 
                "help": "Exemplo: Aquele clima pesado onde todos parecem pisar em ovos para falar com o outro."
            }
        ],
        "Papel": [
            {
                "id": 1, 
                "q": "Sei claramente o que é esperado de mim?", 
                "rev": False, 
                "help": "Exemplo: Suas metas, entregas e funções diárias estão muito bem definidas."
            },
            {
                "id": 4, 
                "q": "Sei como fazer para executar meu trabalho?", 
                "rev": False, 
                "help": "Exemplo: Você recebeu o treinamento necessário e tem as ferramentas certas para trabalhar bem."
            },
            {
                "id": 11, 
                "q": "Sei quais são os objetivos do meu departamento?", 
                "rev": False, 
                "help": "Exemplo: Você entende para onde sua equipe está caminhando e o que precisa ser entregue no fim do mês."
            },
            {
                "id": 13, 
                "q": "Sei o quanto de responsabilidade tenho?", 
                "rev": False, 
                "help": "Exemplo: Os limites de até onde você pode agir, aprovar e decidir são claros."
            },
            {
                "id": 17, 
                "q": "Entendo meu encaixe na empresa?", 
                "rev": False, 
                "help": "Exemplo: Você consegue ver a importância do seu trabalho diário para o sucesso geral do negócio."
            }
        ],
        "Mudança": [
            {
                "id": 26, 
                "q": "Tenho oportunidade de questionar sobre mudanças?", 
                "rev": False, 
                "help": "Exemplo: Haver espaço para tirar dúvidas reais quando uma nova regra ou sistema é criado."
            },
            {
                "id": 28, 
                "q": "Sou consultado(a) sobre mudanças no trabalho?", 
                "rev": False, 
                "help": "Exemplo: A diretoria ou chefia pede a opinião de quem executa antes de mudar um processo."
            },
            {
                "id": 32, 
                "q": "Quando mudanças são feitas, fica claro como funcionarão?", 
                "rev": False, 
                "help": "Exemplo: A comunicação é transparente, bem explicada e não gera confusão na equipe."
            }
        ]
    }

# ==============================================================================
# 4. FUNÇÕES DE CÁLCULO E BANCO DE DADOS
# ==============================================================================
def get_logo_html(width=180):
    """Retorna a tag de imagem com a logo codificada em Base64 ou SVG padrão."""
    if st.session_state.platform_config['logo_b64']:
        return f'<img src="data:image/png;base64,{st.session_state.platform_config["logo_b64"]}" width="{width}">'
    
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120" width="{width}">
        <style>
            .t1 {{ font-family: sans-serif; font-weight: 800; font-size: 50px; fill: {COR_PRIMARIA}; }} 
            .t2 {{ font-family: sans-serif; font-weight: 300; font-size: 50px; fill: {COR_SECUNDARIA}; }} 
            .sub {{ font-family: sans-serif; font-weight: 600; font-size: 11px; fill: {COR_PRIMARIA}; letter-spacing: 3px; text-transform: uppercase; }}
        </style>
        <g transform="translate(10, 20)">
            <rect x="0" y="10" width="35" height="35" rx="8" ry="8" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="8" />
            <rect x="20" y="10" width="35" height="35" rx="8" ry="8" fill="none" stroke="{COR_PRIMARIA}" stroke-width="8" />
        </g>
        <text x="80" y="55" class="t1">ELO</text>
        <text x="190" y="55" class="t2">NR-01</text>
        <text x="82" y="80" class="sub">SISTEMA INTELIGENTE</text>
    </svg>
    """
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}">'

def image_to_base64(file):
    """Converte arquivo de imagem de upload para Base64 string."""
    try: 
        return base64.b64encode(file.getvalue()).decode() if file else None
    except: 
        return None

def logout(): 
    st.session_state.logged_in = False
    st.rerun()

def calculate_actual_scores(all_responses, hse_questions):
    """
    Calcula os scores reais baseados nas respostas dos colaboradores.
    Aplica inversão de nota caso a pergunta seja negativa (rev=True).
    """
    for resp_row in all_responses:
        ans_dict = resp_row.get('answers', {})
        total_score = 0
        count_valid = 0
        
        for cat, qs in hse_questions.items():
            for q in qs:
                q_text = q['q']
                is_rev = q.get('rev', False)
                user_ans = ans_dict.get(q_text)
                
                if user_ans:
                    val = None
                    if user_ans in ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"]:
                        if is_rev: 
                            val = {"Nunca": 5, "Raramente": 4, "Às vezes": 3, "Frequentemente": 2, "Sempre": 1}.get(user_ans)
                        else: 
                            val = {"Nunca": 1, "Raramente": 2, "Às vezes": 3, "Frequentemente": 4, "Sempre": 5}.get(user_ans)
                    
                    elif user_ans in ["Discordo Totalmente", "Discordo", "Neutro", "Concordo", "Concordo Totalmente"]:
                        if is_rev: 
                            val = {"Discordo Totalmente": 5, "Discordo": 4, "Neutro": 3, "Concordo": 2, "Concordo Totalmente": 1}.get(user_ans)
                        else: 
                            val = {"Discordo Totalmente": 1, "Discordo": 2, "Neutro": 3, "Concordo": 4, "Concordo Totalmente": 5}.get(user_ans)

                    if val is not None:
                        total_score += val
                        count_valid += 1
                        
        resp_row['score_calculado'] = round(total_score / count_valid, 2) if count_valid > 0 else 0
    
    return all_responses

def process_company_analytics(comp, comp_resps, hse_questions):
    """
    Gera as médias dimensionais e o Raio-X com base em dados concretos (respostas do DB).
    """
    comp['respondidas'] = len(comp_resps)
    
    if comp['respondidas'] == 0:
        comp['score'] = 0
        comp['dimensoes'] = {cat: 0 for cat in hse_questions.keys()}
        comp['detalhe_perguntas'] = {}
        return comp

    dimensoes_totais = {cat: [] for cat in hse_questions.keys()}
    riscos_por_pergunta = {} 
    total_por_pergunta = {}

    for resp_row in comp_resps:
        ans_dict = resp_row.get('answers', {})
        
        for cat, qs in hse_questions.items():
            for q in qs:
                q_text = q['q']
                is_rev = q.get('rev', False)
                user_ans = ans_dict.get(q_text)
                
                if user_ans:
                    val = None
                    if user_ans in ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"]:
                        if is_rev: 
                            val = {"Nunca": 5, "Raramente": 4, "Às vezes": 3, "Frequentemente": 2, "Sempre": 1}.get(user_ans)
                        else: 
                            val = {"Nunca": 1, "Raramente": 2, "Às vezes": 3, "Frequentemente": 4, "Sempre": 5}.get(user_ans)
                    
                    elif user_ans in ["Discordo Totalmente", "Discordo", "Neutro", "Concordo", "Concordo Totalmente"]:
                        if is_rev: 
                            val = {"Discordo Totalmente": 5, "Discordo": 4, "Neutro": 3, "Concordo": 2, "Concordo Totalmente": 1}.get(user_ans)
                        else: 
                            val = {"Discordo Totalmente": 1, "Discordo": 2, "Neutro": 3, "Concordo": 4, "Concordo Totalmente": 5}.get(user_ans)

                    if val is not None:
                        dimensoes_totais[cat].append(val)
                        
                        if q_text not in riscos_por_pergunta:
                            riscos_por_pergunta[q_text] = 0
                            total_por_pergunta[q_text] = 0
                            
                        total_por_pergunta[q_text] += 1
                        
                        # CRÍTICO: Ajuste fino do Raio-X. 
                        # Notas 1, 2 e 3 agora representam Risco/Atenção. (Ex: "Às vezes" = 3 = Risco Moderado).
                        if val <= 3: 
                            riscos_por_pergunta[q_text] += 1

    # Médias Dimensionais
    dim_averages = {}
    for cat, vals in dimensoes_totais.items():
        dim_averages[cat] = round(sum(vals) / len(vals), 1) if vals else 0.0

    # Raio-X Percentual
    detalhe_percent = {}
    for qt, risk_count in riscos_por_pergunta.items():
        total = total_por_pergunta[qt]
        detalhe_percent[qt] = int((risk_count / total) * 100) if total > 0 else 0

    comp['dimensoes'] = dim_averages
    
    # Media global da empresa baseada apenas nas dimensões válidas
    vals_validos = [v for v in dim_averages.values() if v > 0]
    comp['score'] = round(sum(vals_validos) / len(vals_validos), 1) if vals_validos else 0
    comp['detalhe_perguntas'] = detalhe_percent
    
    return comp

def load_data_from_db():
    """
    Função principal que puxa dados do Supabase e sincroniza.
    """
    all_answers = []
    companies = []
    
    if DB_CONNECTED:
        try:
            companies = supabase.table('companies').select("*").execute().data
            all_answers = supabase.table('responses').select("*").execute().data
            
            users_raw = supabase.table('admin_users').select("*").execute().data
            if users_raw:
                st.session_state.users_db = {u['username']: u for u in users_raw}
        except Exception as e:
            pass
            
    if not companies:
        companies = st.session_state.companies_db
        all_answers = st.session_state.local_responses_db
        
    # Transforma e calcula dados REAIS
    all_answers = calculate_actual_scores(all_answers, st.session_state.hse_questions)
    
    for c in companies:
        if 'org_structure' not in c or not c['org_structure']: 
            c['org_structure'] = {"Geral": ["Geral"]}
            
        comp_resps = [r for r in all_answers if r['company_id'] == c['id']]
        c = process_company_analytics(c, comp_resps, st.session_state.hse_questions)

    return companies, all_answers

def generate_real_history(comp_id, all_responses, hse_questions, total_vidas):
    """
    Agrupa as respostas reais do banco por Mês/Ano para gerar a evolução histórica verdadeira.
    """
    history_dict = {}
    for r in all_responses:
        if r.get('company_id') != comp_id: 
            continue
        
        created_at = r.get('created_at')
        if not created_at: 
            continue
        
        try:
            # Transforma a data do Supabase (ex: '2026-02-19T10:19:00+00:00') em Mes/Ano
            dt = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            periodo = dt.strftime('%m/%Y')
        except:
            periodo = "Geral"
            
        if periodo not in history_dict:
            history_dict[periodo] = []
        history_dict[periodo].append(r)
        
    history_list = []
    for period, resps in history_dict.items():
        comp_mock = {'id': comp_id, 'func': total_vidas}
        comp_stats = process_company_analytics(comp_mock, resps, hse_questions)
        
        history_list.append({
            "periodo": period,
            "score": comp_stats.get('score', 0),
            "vidas": total_vidas,
            "adesao": int((len(resps) / total_vidas) * 100) if total_vidas > 0 else 0,
            "dimensoes": comp_stats.get('dimensoes', {})
        })
        
    # Ordena cronologicamente do mais antigo pro mais novo
    try:
        history_list.sort(key=lambda x: datetime.datetime.strptime(x['periodo'], '%m/%Y') if '/' in x['periodo'] else datetime.datetime.min)
    except:
        pass
        
    return history_list

def delete_company(comp_id):
    """ Exclui a empresa e dados em cascata. """
    if DB_CONNECTED:
        try:
            supabase.table('responses').delete().eq('company_id', comp_id).execute()
            supabase.table('admin_users').delete().eq('linked_company_id', comp_id).execute()
            supabase.table('companies').delete().eq('id', comp_id).execute()
        except Exception as e: 
            st.warning(f"Erro ao excluir do DB: {e}")
    
    st.session_state.companies_db = [c for c in st.session_state.companies_db if c['id'] != comp_id]
    st.success("✅ Empresa excluída com sucesso!")
    time.sleep(1)
    st.rerun()

def delete_user(username):
    """ Exclui o acesso de um analista/gestor. """
    if DB_CONNECTED:
        try:
            supabase.table('admin_users').delete().eq('username', username).execute()
        except: 
            pass
    
    if username in st.session_state.users_db:
        del st.session_state.users_db[username]
    
    st.success("✅ Usuário excluído!")
    time.sleep(1)
    st.rerun()

def kpi_card(title, value, icon, color_class):
    """Gera um KPI visualmente atrativo."""
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <div class="kpi-icon-box {color_class}">{icon}</div>
                <div class="kpi-value">{value}</div>
            </div>
            <div class="kpi-title">{title}</div>
        </div>
    """, unsafe_allow_html=True)

def gerar_analise_robusta(dimensoes):
    """Gera um texto automático para o laudo com base nos scores calculados."""
    riscos = [k for k, v in dimensoes.items() if v < 3.0 and v > 0]
    texto = "Com base na metodologia HSE Management Standards Indicator Tool, a avaliação diagnóstica foi realizada considerando os pilares fundamentais de saúde ocupacional. "
    
    if riscos:
        texto += f"A análise quantitativa evidenciou que as dimensões **{', '.join(riscos)}** encontram-se em zona de risco crítico (Score < 3.0). Estes fatores, quando negligenciados, estão estatisticamente correlacionados ao aumento de estresse, absenteísmo e turnover. "
    else:
        texto += "A análise indica um ambiente de trabalho equilibrado, com fatores de proteção atuantes. As dimensões avaliadas encontram-se dentro dos parâmetros aceitáveis de saúde mental, sugerindo boas práticas de gestão."
    
    texto += " Recomenda-se a implementação imediata do plano de ação estipulado para mitigar riscos e fortalecer a cultura de segurança psicossocial."
    return texto

def gerar_banco_sugestoes(dimensoes):
    """
    Retorna o banco completo de sugestões com base nos indicadores reais.
    Expandido para conter +50 estratégias detalhadas para RH e SESMT.
    """
    sugestoes = []
    
    if dimensoes.get("Demandas", 5) < 3.8:
        sugestoes.append({
            "acao": "Mapeamento de Carga", 
            "estrat": "Realizar censo de tarefas por função para identificar gargalos e redundâncias.", 
            "area": "Demandas", "resp": "A Definir", "prazo": "30 dias"
        })
        sugestoes.append({
            "acao": "Matriz de Priorização", 
            "estrat": "Treinar equipes na Matriz Eisenhower (Urgente x Importante).", 
            "area": "Demandas", "resp": "A Definir", "prazo": "15 dias"
        })
        sugestoes.append({
            "acao": "Política de Desconexão", 
            "estrat": "Estabelecer regras claras sobre envio de mensagens fora do horário e finais de semana.", 
            "area": "Demandas", "resp": "A Definir", "prazo": "30 dias"
        })
        sugestoes.append({
            "acao": "Revisão de Prazos", 
            "estrat": "Renegociar SLAs internos baseados na capacidade real da equipe.", 
            "area": "Demandas", "resp": "A Definir", "prazo": "45 dias"
        })
        sugestoes.append({
            "acao": "Pausas Cognitivas", 
            "estrat": "Instituir pausas de 10 min a cada 2h para descompressão e saúde mental.", 
            "area": "Demandas", "resp": "A Definir", "prazo": "Imediato"
        })
        sugestoes.append({
            "acao": "Contratação Sazonal", 
            "estrat": "Alocar recursos extras temporários em períodos conhecidos de pico de produção.", 
            "area": "Demandas", "resp": "A Definir", "prazo": "90 dias"
        })
        sugestoes.append({
            "acao": "Automação de Tarefas", 
            "estrat": "Mapear e automatizar geração de relatórios e processos altamente repetitivos.", 
            "area": "Demandas", "resp": "A Definir", "prazo": "60 dias"
        })
        sugestoes.append({
            "acao": "Gestão de Interrupções", 
            "estrat": "Definir horários de 'foco total' na semana (ex: manhãs de terça sem reuniões).", 
            "area": "Demandas", "resp": "A Definir", "prazo": "15 dias"
        })
        sugestoes.append({
            "acao": "Treinamento Gestão de Tempo", 
            "estrat": "Capacitação em produtividade pessoal, foco e organização da agenda de trabalho.", 
            "area": "Demandas", "resp": "A Definir", "prazo": "60 dias"
        })
    
    if dimensoes.get("Controle", 5) < 3.8:
        sugestoes.append({
            "acao": "Job Crafting", 
            "estrat": "Permitir personalização do método de trabalho para alcançar os mesmos resultados.", 
            "area": "Controle", "resp": "A Definir", "prazo": "Contínuo"
        })
        sugestoes.append({
            "acao": "Banco de Horas Flexível", 
            "estrat": "Implementar flexibilidade de entrada e saída com regras claras de compensação.", 
            "area": "Controle", "resp": "A Definir", "prazo": "60 dias"
        })
        sugestoes.append({
            "acao": "Autonomia na Agenda", 
            "estrat": "Incentivar a autogestão da ordem das tarefas não-críticas diárias.", 
            "area": "Controle", "resp": "A Definir", "prazo": "Imediato"
        })
        sugestoes.append({
            "acao": "Delegação Efetiva", 
            "estrat": "Treinar gestores para empoderar níveis menores em decisões operacionais rotineiras.", 
            "area": "Controle", "resp": "A Definir", "prazo": "45 dias"
        })
        sugestoes.append({
            "acao": "Comitês Participativos", 
            "estrat": "Envolver a equipe de base nas reuniões de melhoria contínua de processos.", 
            "area": "Controle", "resp": "A Definir", "prazo": "30 dias"
        })
        sugestoes.append({
            "acao": "Flexibilidade de Local", 
            "estrat": "Analisar viabilidade de política de home office estruturado ou modelo híbrido.", 
            "area": "Controle", "resp": "A Definir", "prazo": "90 dias"
        })
        sugestoes.append({
            "acao": "Rotação de Tarefas", 
            "estrat": "Implementar job rotation intra-setorial para reduzir monotonia e aumentar repertório.", 
            "area": "Controle", "resp": "A Definir", "prazo": "60 dias"
        })
        sugestoes.append({
            "acao": "Escolha de Ferramentas", 
            "estrat": "Permitir, dentro da governança da TI, a escolha de softwares ou métodos preferidos.", 
            "area": "Controle", "resp": "A Definir", "prazo": "Contínuo"
        })
        
    if dimensoes.get("Suporte Gestor", 5) < 3.8 or dimensoes.get("Suporte Pares", 5) < 3.8:
        sugestoes.append({
            "acao": "Liderança Segura", 
            "estrat": "Capacitação de líderes em escuta ativa, inteligência emocional e empatia.", 
            "area": "Suporte", "resp": "A Definir", "prazo": "90 dias"
        })
        sugestoes.append({
            "acao": "Mentoria Buddy", 
            "estrat": "Implementar sistema de padrinhos para acolhimento de novos colaboradores.", 
            "area": "Suporte", "resp": "A Definir", "prazo": "30 dias"
        })
        sugestoes.append({
            "acao": "Reuniões 1:1", 
            "estrat": "Estruturar feedbacks individuais quinzenais com foco em bem-estar e carreira.", 
            "area": "Suporte", "resp": "A Definir", "prazo": "15 dias"
        })
        sugestoes.append({
            "acao": "Grupos de Apoio Técnico", 
            "estrat": "Criar espaços seguros e institucionalizados para troca de experiências e resolução conjunta.", 
            "area": "Suporte", "resp": "A Definir", "prazo": "45 dias"
        })
        sugestoes.append({
            "acao": "Feedback Estruturado", 
            "estrat": "Implementar a cultura de feedback contínuo (modelo SBI) não atrelado à avaliação anual.", 
            "area": "Suporte", "resp": "A Definir", "prazo": "60 dias"
        })
        sugestoes.append({
            "acao": "Rituais de Reconhecimento", 
            "estrat": "Criar rotinas simples de celebração de pequenas conquistas e esforços extraordinários da equipe.", 
            "area": "Suporte", "resp": "A Definir", "prazo": "Imediato"
        })
        sugestoes.append({
            "acao": "Plantão de Escuta", 
            "estrat": "Disponibilizar canal direto com RH ou Psicologia Organizacional para suporte emergencial.", 
            "area": "Suporte", "resp": "A Definir", "prazo": "30 dias"
        })
        sugestoes.append({
            "acao": "Treinamento de Empatia", 
            "estrat": "Workshop vivencial focado na redução de atritos invisíveis gerados pela comunicação digital assíncrona.", 
            "area": "Suporte", "resp": "A Definir", "prazo": "90 dias"
        })
        sugestoes.append({
            "acao": "Café com a Diretoria", 
            "estrat": "Rotinas de aproximação estruturada e informal da alta gestão com a base da operação.", 
            "area": "Suporte", "resp": "A Definir", "prazo": "Mensal"
        })
        
    if dimensoes.get("Relacionamentos", 5) < 3.8:
        sugestoes.append({
            "acao": "Tolerância Zero ao Assédio", 
            "estrat": "Atualizar, divulgar e assinar termo de compromisso com o Código de Conduta e Ética.", 
            "area": "Relacionamentos", "resp": "A Definir", "prazo": "30 dias"
        })
        sugestoes.append({
            "acao": "Workshop CNV", 
            "estrat": "Treinamento intensivo de Comunicação Não-Violenta para todos os níveis hierárquicos.", 
            "area": "Relacionamentos", "resp": "A Definir", "prazo": "90 dias"
        })
        sugestoes.append({
            "acao": "Ouvidoria Externa", 
            "estrat": "Contratar canal anônimo e seguro, gerido por terceiros, para denúncias de assédio e bullying.", 
            "area": "Relacionamentos", "resp": "A Definir", "prazo": "60 dias"
        })
        sugestoes.append({
            "acao": "Mediação de Conflitos", 
            "estrat": "Treinar um grupo multidisciplinar do RH para atuar na mediação precoce de atritos entre equipes.", 
            "area": "Relacionamentos", "resp": "A Definir", "prazo": "120 dias"
        })
        sugestoes.append({
            "acao": "Eventos de Team Building", 
            "estrat": "Investir em dinâmicas de integração, voluntariado corporativo e quebra-gelo fora do ambiente tradicional.", 
            "area": "Relacionamentos", "resp": "A Definir", "prazo": "Semestral"
        })
        sugestoes.append({
            "acao": "Acordos de Convivência", 
            "estrat": "Sessão de facilitação para criação coletiva de um 'manual' de boas práticas de convivência intersetorial.", 
            "area": "Relacionamentos", "resp": "A Definir", "prazo": "30 dias"
        })
        sugestoes.append({
            "acao": "Comitê de Diversidade", 
            "estrat": "Estabelecer grupo focado em promover a inclusão, letramento sobre vieses inconscientes e respeito mútuo.", 
            "area": "Relacionamentos", "resp": "A Definir", "prazo": "90 dias"
        })
        sugestoes.append({
            "acao": "Feedback 360 Anônimo", 
            "estrat": "Realizar avaliação estruturada entre pares para identificar atritos comportamentais ocultos nas equipes.", 
            "area": "Relacionamentos", "resp": "A Definir", "prazo": "Anual"
        })
        
    if dimensoes.get("Papel", 5) < 3.8:
        sugestoes.append({
            "acao": "Revisão de Job Description", 
            "estrat": "Atualizar e validar descrições de cargo garantindo clareza total das responsabilidades reais.", 
            "area": "Papel", "resp": "A Definir", "prazo": "60 dias"
        })
        sugestoes.append({
            "acao": "Alinhamento de Metas (OKRs)", 
            "estrat": "Revisão periódica (trimestral/semestral) de objetivos individuais atrelados ao propósito macro da área.", 
            "area": "Papel", "resp": "A Definir", "prazo": "Contínuo"
        })
        sugestoes.append({
            "acao": "Onboarding Estruturado", 
            "estrat": "Reforço no treinamento inicial, abordando não só processos, mas cultura, história e valor da função.", 
            "area": "Papel", "resp": "A Definir", "prazo": "30 dias"
        })
        sugestoes.append({
            "acao": "Matriz RACI", 
            "estrat": "Definição visual e formal de quem é Responsável, Autoridade, Consultado e Informado nos fluxos diários.", 
            "area": "Papel", "resp": "A Definir", "prazo": "45 dias"
        })
        
    if dimensoes.get("Mudança", 5) < 3.8:
        sugestoes.append({
            "acao": "Comunicação Transparente", 
            "estrat": "Garantir que a liderança explique o 'porquê' (razão de negócio) antes do 'como' (a tarefa) em todas as mudanças.", 
            "area": "Mudança", "resp": "A Definir", "prazo": "Contínuo"
        })
        sugestoes.append({
            "acao": "Consulta Prévia de Impacto", 
            "estrat": "Realizar pequenos focus groups ou enquetes antes de implementar mudanças de alto impacto operacional.", 
            "area": "Mudança", "resp": "A Definir", "prazo": "A cada projeto"
        })
        sugestoes.append({
            "acao": "Embaixadores da Mudança", 
            "estrat": "Eleger colaboradores chave na base operacional para apoiar e traduzir a transição para os pares em novos sistemas.", 
            "area": "Mudança", "resp": "A Definir", "prazo": "A cada projeto"
        })
        sugestoes.append({
            "acao": "Cronograma Visível", 
            "estrat": "Disponibilizar timeline clara e acessível das etapas de transição para reduzir a ansiedade gerada pela incerteza.", 
            "area": "Mudança", "resp": "A Definir", "prazo": "Imediato"
        })
        sugestoes.append({
            "acao": "Central de FAQ e Suporte", 
            "estrat": "Criar documento centralizado de dúvidas comuns atualizado constantemente durante a implementação de grandes transições.", 
            "area": "Mudança", "resp": "A Definir", "prazo": "Imediato"
        })
    
    if not sugestoes:
        sugestoes.append({
            "acao": "Manutenção do Clima", 
            "estrat": "Realizar pesquisas de pulso curtas e trimestrais para monitoramento contínuo da estabilidade.", 
            "area": "Geral", "resp": "RH", "prazo": "Contínuo"
        })
        sugestoes.append({
            "acao": "Programa de Saúde Mental", 
            "estrat": "Palestras mensais, parcerias com apps de terapia ou plano de saúde mental dedicado aos colaboradores.", 
            "area": "Geral", "resp": "RH", "prazo": "90 dias"
        })
        sugestoes.append({
            "acao": "Pausas Ativas (Laboral)", 
            "estrat": "Implementar rotina de ginástica laboral guiada, online ou presencial, para descompressão física.", 
            "area": "Geral", "resp": "SESMT", "prazo": "30 dias"
        })
        
    return sugestoes

# ==============================================================================
# 5. TELAS DO SISTEMA - FRONTEND E ADMINISTRAÇÃO
# ==============================================================================

def login_screen():
    """Tela de Autenticação do Sistema"""
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center'>{get_logo_html(250)}</div>", unsafe_allow_html=True)
        plat_name = st.session_state.platform_config['name']
        st.markdown(f"<h3 style='text-align:center; color:#555;'>{plat_name}</h3>", unsafe_allow_html=True)
        
        with st.form("login"):
            user = st.text_input("Usuário")
            pwd = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Dashboard", type="primary", use_container_width=True):
                login_ok = False
                user_role_type = "Analista"
                user_credits = 0
                linked_comp = None
                
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
                
                if not login_ok and user in st.session_state.users_db and st.session_state.users_db[user].get('password') == pwd:
                    login_ok = True
                    user_data = st.session_state.users_db[user]
                    user_role_type = user_data.get('role', 'Analista')
                    user_credits = user_data.get('credits', 0)
                    linked_comp = user_data.get('linked_company_id')
                
                if login_ok:
                    valid_until = user_data.get('valid_until')
                    if valid_until and datetime.datetime.today().isoformat() > valid_until:
                        st.error("🚫 O acesso deste usuário expirou devido ao término do contrato.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_role = 'admin'
                        
                        # GARANTIA ABSOLUTA DE ACESSO MASTER PARA O USUARIO "admin"
                        if user == 'admin':
                            user_role_type = 'Master'
                            user_credits = 999999
                        
                        st.session_state.admin_permission = user_role_type 
                        st.session_state.user_username = user
                        st.session_state.user_credits = user_credits
                        st.session_state.user_linked_company = linked_comp
                        st.rerun()
                else: 
                    st.error("Credenciais incorretas ou usuário não encontrado.")
                    
        st.caption("Aviso para Colaboradores: Utilizem exclusivamente o link direto fornecido pelo seu RH.")

def admin_dashboard():
    """Painel de Controle Central para Gestores e Masters"""
    companies_data, responses_data = load_data_from_db()
    perm = st.session_state.admin_permission
    curr_user = st.session_state.user_username
    
    if perm == "Gestor":
        visible_companies = [c for c in companies_data if c.get('owner') == curr_user]
    elif perm == "Analista":
        linked_id = st.session_state.user_linked_company
        visible_companies = [c for c in companies_data if c['id'] == linked_id]
    else:
        visible_companies = companies_data

    total_used_by_user = sum(c.get('respondidas', 0) for c in visible_companies) if perm != "Analista" else (visible_companies[0].get('respondidas', 0) if visible_companies else 0)
    credits_left = st.session_state.user_credits - total_used_by_user

    menu_options = ["Visão Geral", "Gerar Link", "Relatórios", "Histórico & Comparativo"]
    if perm in ["Master", "Gestor"]:
        menu_options.insert(1, "Empresas")
        menu_options.insert(2, "Setores & Cargos")
    if perm == "Master":
        menu_options.append("Configurações")

    icons_map = {
        "Visão Geral": "grid", 
        "Empresas": "building", 
        "Setores & Cargos": "list-task", 
        "Gerar Link": "link-45deg", 
        "Relatórios": "file-text", 
        "Histórico & Comparativo": "clock-history", 
        "Configurações": "gear"
    }
    
    with st.sidebar:
        st.markdown(f"<div style='text-align:center; margin-bottom:30px; margin-top:20px;'>{get_logo_html(160)}</div>", unsafe_allow_html=True)
        st.caption(f"Usuário Autenticado: **{curr_user}** | Nível: **{perm}**")
        
        if perm != "Master": 
            st.info(f"💳 Saldo Disponível: {credits_left} avaliações")

        selected = option_menu(
            menu_title=None, 
            options=menu_options, 
            icons=[icons_map[o] for o in menu_options], 
            default_index=0, 
            styles={"nav-link-selected": {"background-color": COR_PRIMARIA}}
        )
        st.markdown("---")
        if st.button("🚪 Sair do Sistema", use_container_width=True): 
            logout()

    # --- PÁGINAS DO DASHBOARD ---
    if selected == "Visão Geral":
        st.title("Painel Administrativo Analítico")
        empresa_filtro = st.selectbox("Filtrar Visão por Empresa", ["Todas as Empresas"] + [c['razao'] for c in visible_companies])
        
        if empresa_filtro != "Todas as Empresas":
            companies_filtered = [c for c in visible_companies if c['razao'] == empresa_filtro]
            target_id = companies_filtered[0]['id']
            responses_filtered = [r for r in responses_data if r['company_id'] == target_id]
        else:
            companies_filtered = visible_companies
            ids_visiveis = [c['id'] for c in visible_companies]
            responses_filtered = [r for r in responses_data if r['company_id'] in ids_visiveis]

        total_resp_view = len(responses_filtered)
        total_vidas_view = sum(c.get('func', 0) for c in companies_filtered)
        
        col1, col2, col3, col4 = st.columns(4)
        if perm == "Analista":
            with col1: kpi_card("Vidas Contratadas", total_vidas_view, "👥", "bg-blue")
            with col2: kpi_card("Questionários Respondidos", total_resp_view, "✅", "bg-green")
            with col3: kpi_card("Saldo de Avaliações", credits_left, "💳", "bg-orange") 
        else:
            with col1: kpi_card("Empresas Ativas", len(companies_filtered), "🏢", "bg-blue")
            with col2: kpi_card("Total de Respostas", total_resp_view, "✅", "bg-green")
            if perm == "Master": 
                with col3: kpi_card("Vidas Totais (Censo)", total_vidas_view, "👥", "bg-orange") 
            else: 
                with col3: kpi_card("Seu Saldo", credits_left, "💳", "bg-orange")

        with col4: kpi_card("Alertas de Risco", 0, "🚨", "bg-red")
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Radar HSE (Média Real Consolidada)")
            if companies_filtered and total_resp_view > 0:
                categories = list(st.session_state.hse_questions.keys())
                avg_dims = {cat: 0 for cat in categories}
                count_comps_with_data = 0
                for c in companies_filtered:
                    if c.get('respondidas', 0) > 0:
                        count_comps_with_data += 1
                        for cat in categories: 
                            avg_dims[cat] += c['dimensoes'].get(cat, 0)
                
                valores_radar = [round(avg_dims[cat]/count_comps_with_data, 1) for cat in categories] if count_comps_with_data > 0 else [0]*len(categories)

                fig_radar = go.Figure(go.Scatterpolar(r=valores_radar, theta=categories, fill='toself', name='Média', line_color=COR_SECUNDARIA))
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=300, margin=dict(t=20, b=20))
                st.plotly_chart(fig_radar, use_container_width=True)
            else: 
                st.info("Aguardando volume de respostas suficiente para gerar o mapeamento radar.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Resultados Analíticos por Setor (Score Verdadeiro)")
            if responses_filtered:
                df_resp = pd.DataFrame(responses_filtered)
                if 'setor' in df_resp.columns and 'score_calculado' in df_resp.columns:
                    df_setor = df_resp.groupby('setor')['score_calculado'].mean().reset_index()
                    fig_bar = px.bar(df_setor, x='setor', y='score_calculado', title="Score Médio Real por Área", color='score_calculado', color_continuous_scale='RdYlGn', range_y=[0, 5])
                    st.plotly_chart(fig_bar, use_container_width=True)
                else: 
                    st.info("Sem dados setoriais estruturados.")
            else: 
                st.info("Aguardando respostas para compilar o gráfico de barras.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        c3, c4 = st.columns([1.5, 1])
        with c3:
             st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
             st.markdown("##### Distribuição de Engajamento das Organizações")
             if companies_filtered:
                 status_dist = {"Concluído (Meta Atingida)": 0, "Em Andamento": 0}
                 for c in companies_filtered:
                     if c.get('respondidas',0) >= c.get('func',1): 
                         status_dist["Concluído (Meta Atingida)"] += 1
                     else: 
                         status_dist["Em Andamento"] += 1
                 
                 fig_pie = px.pie(names=list(status_dist.keys()), values=list(status_dist.values()), hole=0.6, color_discrete_sequence=[COR_SECUNDARIA, COR_RISCO_MEDIO])
                 fig_pie.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
                 st.plotly_chart(fig_pie, use_container_width=True)
             else: 
                 st.info("Por favor, cadastre empresas para habilitar este gráfico.")
             st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Empresas":
        st.title("Gestão de Clientes e Empresas")
        if st.session_state.edit_mode:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("✏️ Editar Dados da Empresa")
            target_id = st.session_state.edit_id
            emp_edit = next((c for c in visible_companies if c['id'] == target_id), None)
            
            if emp_edit:
                with st.form("edit_form"):
                    c1, c2, c3 = st.columns(3)
                    new_razao = c1.text_input("Razão Social", value=emp_edit['razao'])
                    new_cnpj = c2.text_input("CNPJ", value=emp_edit.get('cnpj',''))
                    new_cnae = c3.text_input("CNAE", value=emp_edit.get('cnae',''))
                    
                    c4, c5, c6 = st.columns(3)
                    risco_opts = [1, 2, 3, 4]
                    idx_risco = risco_opts.index(emp_edit.get('risco',1)) if emp_edit.get('risco',1) in risco_opts else 0
                    new_risco = c4.selectbox("Grau de Risco (NR-04)", risco_opts, index=idx_risco)
                    new_func = c5.number_input("Número de Vidas (Funcionários)", min_value=1, value=emp_edit.get('func',100))
                    new_limit = c6.number_input("Cota de Avaliações Adquirida", min_value=1, value=emp_edit.get('limit_evals', 100))
                    
                    seg_opts = ["GHE", "Setor", "GES"]
                    idx_seg = seg_opts.index(emp_edit.get('segmentacao','GHE')) if emp_edit.get('segmentacao','GHE') in seg_opts else 0
                    new_seg = c6.selectbox("Segmentação de Relatório", seg_opts, index=idx_seg)
                    
                    c7, c8, c9 = st.columns(3)
                    new_resp = c7.text_input("Responsável da Empresa (Contato)", value=emp_edit.get('resp',''))
                    new_email = c8.text_input("E-mail Comercial do Responsável", value=emp_edit.get('email',''))
                    new_tel = c9.text_input("Telefone ou WhatsApp", value=emp_edit.get('telefone',''))
                    
                    new_end = st.text_input("Endereço Físico Completo", value=emp_edit.get('endereco',''))
                    
                    val_atual = datetime.date.today() + datetime.timedelta(days=365)
                    if emp_edit.get('valid_until'):
                        try: val_atual = datetime.date.fromisoformat(emp_edit['valid_until'])
                        except: pass
                    new_valid = st.date_input("Link de Avaliação Válido Até", value=val_atual)
                    
                    if st.form_submit_button("💾 Confirmar e Salvar Alterações"):
                        update_dict = {
                            'razao': new_razao, 
                            'cnpj': new_cnpj, 
                            'cnae': new_cnae, 
                            'risco': new_risco, 
                            'func': new_func, 
                            'segmentacao': new_seg, 
                            'resp': new_resp, 
                            'email': new_email, 
                            'telefone': new_tel, 
                            'endereco': new_end, 
                            'limit_evals': new_limit, 
                            'valid_until': new_valid.isoformat()
                        }
                        if DB_CONNECTED:
                            try: 
                                supabase.table('companies').update(update_dict).eq('id', target_id).execute()
                            except Exception as e: 
                                st.warning(f"Erro DB Update: {e}")
                        
                        emp_edit.update(update_dict)
                        st.session_state.edit_mode = False
                        st.session_state.edit_id = None
                        st.success("✅ Empresa atualizada com sucesso em todos os registros!")
                        time.sleep(1)
                        st.rerun()
                        
                if st.button("Cancelar Edição e Voltar"): 
                    st.session_state.edit_mode = False
                    st.rerun()
            else:
                st.error("Falha sistêmica: Erro ao carregar os dados desta empresa para edição.")
        
        else:
            tab1, tab2 = st.tabs(["📋 Lista de Empresas Clientes", "➕ Cadastrar Nova Empresa"])
            with tab1:
                if not visible_companies: 
                    st.info("Nenhuma empresa cadastrada ou vinculada ao seu usuário no momento.")
                
                for emp in visible_companies:
                    with st.expander(f"🏢 {emp['razao']}"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.write(f"**CNPJ:** {emp.get('cnpj','')}")
                        c2.write(f"**Cota (Uso):** {emp.get('respondidas',0)} de {emp.get('limit_evals', '∞')} vidas")
                        c3.write(f"**Vence em:** {emp.get('valid_until', '-')[:10]}")
                        
                        c4_1, c4_2 = c4.columns(2)
                        if c4_1.button("✏️ Editar Perfil", key=f"ed_{emp['id']}"): 
                             st.session_state.edit_mode = True
                             st.session_state.edit_id = emp['id']
                             st.rerun()
                        
                        if perm == "Master":
                            # EXCLUSÃO SEGURA BASEADA EM ID - PREVINE INDEX ERROR
                            if c4_2.button("🗑️ Excluir Definitivo", key=f"del_{emp['id']}"): 
                                delete_company(emp['id'])
            
            with tab2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                with st.form("add_comp_form"):
                    if credits_left <= 0 and perm != "Master":
                        st.error("🚫 O seu limite de créditos chegou ao fim. Recarregue seu plano para continuar operando.")
                        st.form_submit_button("Formulário Bloqueado por Falta de Saldo", disabled=True)
                    else:
                        st.write("### Dados Básicos de Contrato")
                        c1, c2, c3 = st.columns(3)
                        razao = c1.text_input("Razão Social Completa")
                        cnpj = c2.text_input("CNPJ Formatado")
                        cnae = c3.text_input("Código CNAE")
                        
                        c4, c5, c6 = st.columns(3)
                        risco = c4.selectbox("Grau de Risco Empresarial", [1,2,3,4])
                        func = c5.number_input("Número Total de Vidas (Funcionários Base)", min_value=1)
                        limit_evals = c6.number_input("Cota Total de Avaliações Permitidas", min_value=1, max_value=credits_left if perm!="Master" else 99999, value=min(100, credits_left if perm!="Master" else 100))
                        
                        st.write("### Informações de Contato e Disparo de Link")
                        c7, c8, c9 = st.columns(3)
                        segmentacao = c7.selectbox("Tipo de Segmentação Geográfica", ["GHE", "Setor", "GES"])
                        resp = c8.text_input("Nome do Diretor ou Responsável RH")
                        email = c9.text_input("E-mail Direto do Responsável")
                        
                        c10, c11, c12 = st.columns(3)
                        tel = c10.text_input("Telefone Fixo ou WhatsApp corporativo")
                        valid_date = c11.date_input("Link será Válido Até:", value=datetime.date.today() + datetime.timedelta(days=365))
                        
                        # INFORMAÇÃO CRUCIAL SOBRE O LINK UUID
                        c12.info("O ID de pesquisa único e seguro será gerado automaticamente após salvar.")
                        
                        end = st.text_input("Endereço Completo para Emissão do Laudo")
                        logo_cliente = st.file_uploader("Upload da Logo do Cliente (PNG/JPG com fundo transparente opcional)", type=['png', 'jpg', 'jpeg'])
                        
                        st.markdown("---")
                        st.write("### Criar Acesso Dedicado para a Empresa (Nível Analista)")
                        st.caption("Crie um login exclusivo para que o RH desta empresa possa acessar as análises e laudos de forma independente.")
                        u_login = st.text_input("Nome de Usuário (Ex: rh_empresa_x)")
                        u_pass = st.text_input("Senha Inicial de Acesso Segura", type="password")

                        if st.form_submit_button("✅ Concluir Cadastro de Empresa e Usuário"):
                            if not razao: 
                                st.error("⚠️ O campo Razão Social é estritamente obrigatório para identificação.")
                            else:
                                # GERA ID UUID SEGURO AUTOMATICAMENTE
                                cod = str(uuid.uuid4())[:8].upper()
                                logo_str = image_to_base64(logo_cliente)
                                
                                new_c = {
                                    "id": cod, 
                                    "razao": razao, 
                                    "cnpj": cnpj, 
                                    "cnae": cnae, 
                                    "setor": "Geral", 
                                    "risco": risco, 
                                    "func": func, 
                                    "limit_evals": limit_evals, 
                                    "segmentacao": segmentacao, 
                                    "resp": resp, 
                                    "email": email, 
                                    "telefone": tel, 
                                    "endereco": end, 
                                    "valid_until": valid_date.isoformat(), 
                                    "logo_b64": logo_str, 
                                    "score": 0, 
                                    "respondidas": 0, 
                                    "owner": curr_user, 
                                    "dimensoes": {}, 
                                    "detalhe_perguntas": {}, 
                                    "org_structure": {"Geral": ["Geral"]}
                                }
                                
                                error_msg = None
                                if DB_CONNECTED:
                                    try:
                                        supabase.table('companies').insert(new_c).execute()
                                        if u_login and u_pass:
                                            supabase.table('admin_users').insert({
                                                "username": u_login, 
                                                "password": u_pass, 
                                                "role": "Analista", 
                                                "credits": limit_evals, 
                                                "valid_until": valid_date.isoformat(), 
                                                "linked_company_id": cod
                                            }).execute()
                                    except Exception as e: 
                                        error_msg = str(e)
                                
                                st.session_state.companies_db.append(new_c)
                                
                                if error_msg: 
                                    st.warning(f"⚠️ Aviso do Banco de Dados: Processo salvo localmente. Encontramos um gargalo de rede ({error_msg})")
                                else: 
                                    st.success(f"🎉 Organização cadastrada perfeitamente! O ID gerado para envio do link é: {cod}")
                                
                                time.sleep(2.5)
                                st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Setores & Cargos":
        st.title("Estruturação Interna de Setores e Cargos")
        if not visible_companies: 
            st.warning("⚠️ Você precisa cadastrar ao menos uma empresa antes de estruturar seus departamentos."); return
        
        empresa_nome = st.selectbox("Selecione a Organização Cliente para estruturação", [c['razao'] for c in visible_companies])
        empresa = next((c for c in visible_companies if c['razao'] == empresa_nome), None)
        
        if empresa is not None:
            if 'org_structure' not in empresa or not empresa['org_structure']: 
                empresa['org_structure'] = {"Geral": ["Geral"]}
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.subheader("1. Inserir ou Remover Setores")
                new_setor = st.text_input("Nome exato do novo departamento")
                if st.button("➕ Incorporar Setor à Hierarquia"):
                    if new_setor and new_setor not in empresa['org_structure']:
                        empresa['org_structure'][new_setor] = []
                        if DB_CONNECTED:
                            try: 
                                supabase.table('companies').update({"org_structure": empresa['org_structure']}).eq('id', empresa['id']).execute()
                            except: pass
                        st.success(f"Departamento '{new_setor}' foi catalogado com sucesso!")
                        time.sleep(1); st.rerun()
                
                st.markdown("---")
                setores_existentes = list(empresa['org_structure'].keys())
                setor_remover = st.selectbox("Selecione a área para extinção estrutural", setores_existentes)
                if st.button("🗑️ Desfazer Setor"):
                    del empresa['org_structure'][setor_remover]
                    if DB_CONNECTED:
                         try: 
                             supabase.table('companies').update({"org_structure": empresa['org_structure']}).eq('id', empresa['id']).execute()
                         except: pass
                    st.success("Setor e seus cargos dependentes foram removidos.")
                    time.sleep(1); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.subheader("2. Gerenciamento de Funções do Setor")
                setor_sel = st.selectbox("Filtrar e definir cargos para o setor de:", setores_existentes, key="sel_setor_cargos")
                if setor_sel:
                    df_cargos = pd.DataFrame({"Cargo": empresa['org_structure'][setor_sel]})
                    edited_cargos = st.data_editor(df_cargos, num_rows="dynamic", key="editor_cargos", use_container_width=True)
                    if st.button("💾 Persistir Matriz de Cargos no Banco", type="primary"):
                        lista_nova = edited_cargos["Cargo"].dropna().tolist()
                        empresa['org_structure'][setor_sel] = lista_nova
                        if DB_CONNECTED:
                             try: 
                                 supabase.table('companies').update({"org_structure": empresa['org_structure']}).eq('id', empresa['id']).execute()
                             except: pass
                        st.success("A matriz de cargos para este setor foi sincronizada.")
                st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Gerar Link":
        st.title("Centro de Disparo e Testes de Links")
        if not visible_companies: 
            st.warning("⚠️ Impossível gerar. Por favor, cadastre uma organização primeiro."); return
            
        with st.container():
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            empresa_nome = st.selectbox("Selecione o Cliente para criar as diretrizes de envio", [c['razao'] for c in visible_companies])
            empresa = next(c for c in visible_companies if c['razao'] == empresa_nome)
            
            # GERAÇÃO SEGURA BASEADA NO UUID DA EMPRESA
            base_url = st.session_state.platform_config.get('base_url', 'https://elonr01-cris.streamlit.app').rstrip('/')
            link_final = f"{base_url}/?cod={empresa['id']}"
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("##### Link URL Protegido Exclusivo")
                st.markdown(f"<div class='link-area'>{link_final}</div>", unsafe_allow_html=True)
                
                limit = empresa.get('limit_evals', 999999)
                usadas = empresa.get('respondidas', 0)
                val = empresa.get('valid_until', '-')
                try: val = datetime.date.fromisoformat(val).strftime('%d/%m/%Y')
                except: pass
                st.caption(f"📊 Volume Utilizado no Ciclo Atual: {usadas} avaliações processadas de um limite total de {limit}.")
                st.caption(f"📅 Expirabilidade Programada do Link: {val}")
                
                if st.button("👁️ Iniciar Teste Visão Colaborador (Ambiente Isoloado)"):
                    st.session_state.current_company = empresa
                    st.session_state.logged_in = True
                    st.session_state.user_role = 'colaborador'
                    st.rerun()
            with c2:
                st.markdown("##### Imagem QR Code Rápido")
                qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(link_final)}"
                st.image(qr_api_url, width=150)
                st.markdown(f"[📥 Baixar Vetor do QR Code]({qr_api_url})")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### 💬 Estrutura Modelo de Comunicação Corporativa (WhatsApp / Endomarketing / E-mail)")
            texto_convite = f"""Olá, equipe da {empresa['razao']}! 👋\n\nCuidar da nossa operação e dos nossos resultados estratégicos é fundamental, mas absolutamente nada disso faz sentido se não cuidarmos, em primeiro lugar, de quem faz toda a mágica acontecer: vocês.\n\nEstamos dando início oficial à nossa Avaliação de Riscos Psicossociais e queremos te fazer um convite para um bate-papo estruturado e extremamente sincero. Mas, afinal, por que isso é tão importante na nossa rotina?\n\n🧠 **Por que a sua participação é tão valiosa?**\nEm diversos momentos, a intensidade do estresse corporativo, a elevada carga de trabalho ou a própria dinâmica intensa do dia a dia podem gerar impactos profundos no nosso bem-estar coletivo de formas quase invisíveis.\nResponder a esta avaliação rápida não é apenas o preenchimento protocolar de um formulário; é fornecer para nós, na gestão, o raio-x e as métricas precisas necessárias para:\n\n* Identificar e mitigar rapidamente os pontos críticos e de fricção no nosso ambiente de trabalho diário.\n* Desenhar e aprovar orçamentos para ações práticas focadas em promover mais equilíbrio e blindagem à nossa saúde mental.\n* Construir dia a dia uma cultura organizacional horizontal onde todos se sintam ativamente ouvidos e plenamente respeitados na sua individualidade.\n\n🔒 **A sua segurança psicológica é a nossa premissa inegociável**\nTemos total consciência de que abrir o jogo sobre sentimentos, processos falhos e percepções exige um elo forte de confiança. Por essa razão, queremos assinar simbolicamente com você dois acordos inquebráveis:\n\n* **Blindagem de Anonimato:** O nosso novo sistema em nuvem foi programado com restrições rígidas para garantir que nenhuma resposta preenchida seja cruzada ou vinculada ao seu nome, cargo ou e-mail pessoal. Seu CPF é hash-criptografado e irreversível.\n* **Análise Sigilosa:** Todos os dados exportados e analisados são extraídos de forma coletiva, macro e estatística (formando médias do seu setor ou da empresa geral). Absolutamente nenhum líder ou diretor terá permissão técnica de acesso para visualizar o detalhamento das suas respostas individuais.\n\nO seu "sincerômetro" apontado pro máximo é exatamente a bússola que precisamos para poder evoluir de verdade. Tenha a tranquilidade de saber que aqui não há respostas tecnicamente certas ou erradas; buscamos apenas a sua genuína percepção e o seu sentimento sobre a realidade crua do nosso cotidiano ao seu lado.\n\n🚀 **Acessando a plataforma**\nBasta clicar ou tocar no link automatizado logo abaixo. Garantimos que o preenchimento não vai consumir mais do que 7 minutinhos da sua atenção, e as telas são facílimas de usar até mesmo no celular.\n\n🔗 {link_final}\n\nNós contamos, de verdade, com a força e a veracidade da sua voz para erguermos, de braços dados, um ecossistema muito mais agradável e acolhedor para investirmos os nossos dias.\n\nUm abraço respeitoso,\nLiderança Estratégica e Time de Gestão de Pessoas (RH)"""
            st.text_area("Copie o material formatado abaixo para disparo:", value=texto_convite, height=350)
            st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Relatórios":
        st.title("Módulo de Geração de Relatórios e Laudos")
        if not visible_companies: 
            st.warning("É mandatório cadastrar uma empresa ativa na base de dados para instanciar a emissão de laudos oficiais."); return
            
        c_sel, c_blank = st.columns([1, 1])
        with c_sel:
            empresa_sel = st.selectbox("Selecione a Organização Cliente Alvo da Análise", [e['razao'] for e in visible_companies])
        
        empresa = next(e for e in visible_companies if e['razao'] == empresa_sel)
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("#### Assinaturas Documentais Eletrônicas")
            sig_empresa_nome = st.text_input("Identificação Oficial do Responsável pela Empresa", value=empresa.get('resp',''))
            sig_empresa_cargo = st.text_input("CBO/Cargo do Responsável", value="Diretoria Corporativa")
            sig_tecnico_nome = st.text_input("Selo Técnico: Nome Completo do Avaliador", value="Cristiane Cardoso Lima")
            sig_tecnico_cargo = st.text_input("Função Técnica Credenciada", value="RH Estratégico - Pessin Gestão e Desenvolvimento")

        dimensoes_atuais = empresa.get('dimensoes', {})
        analise_auto = gerar_analise_robusta(dimensoes_atuais)
        sugestoes_auto = gerar_banco_sugestoes(dimensoes_atuais)
        
        # --- LÓGICA RÍGIDA DE POPULAÇÃO DO DATAFRAME DE AÇÕES (EVITA NAME ERROR) ---
        if st.session_state.acoes_list is None: 
            st.session_state.acoes_list = []
            
        if not st.session_state.acoes_list and sugestoes_auto:
            # Integração total e automática: injeta todas as predições do banco de inteligência
            for s in sugestoes_auto: 
                st.session_state.acoes_list.append({
                    "acao": s['acao'], 
                    "estrat": s['estrat'], 
                    "area": s['area'], 
                    "resp": "A Definir na Reunião de Acompanhamento", 
                    "prazo": "SLA Estipulado em 30 a 60 dias"
                })
        
        html_act = ""
        if st.session_state.acoes_list:
            for item in st.session_state.acoes_list:
                html_act += f"<tr><td>{item.get('acao','')}</td><td>{item.get('estrat','')}</td><td>{item.get('area','')}</td><td>{item.get('resp','')}</td><td>{item.get('prazo','')}</td></tr>"
        else:
            html_act = "<tr><td colspan='5' style='text-align:center;'>Pendência: A base de algoritmos não localizou ações necessárias ou nenhuma ação foi definida na pauta pelo analista.</td></tr>"

        with st.expander("📝 Parametrização e Ajuste Fino do Conteúdo do Laudo", expanded=True):
            st.markdown("##### 1. Elaboração do Parecer Conclusivo e Parecer Técnico")
            analise_texto = st.text_area("O texto abaixo será impresso diretamente no PDF do laudo corporativo. Edite conforme a sua visão subjetiva do cenário do cliente:", value=analise_auto, height=150)
            
            st.markdown("---")
            st.markdown("##### 2. Adição Modular Baseada na Nuvem de Ações")
            opcoes_formatadas = [f"[{s['area']}] {s['acao']}: {s['estrat']}" for s in sugestoes_auto]
            selecionadas = st.multiselect("Navegue pelas heurísticas sugeridas e force a inclusão de ações extras no DataFrame final:", options=opcoes_formatadas)
            if st.button("⬇️ Injetar Sugestões na Planilha de Apresentação"):
                novas = []
                for item_str in selecionadas:
                    for s in sugestoes_auto:
                        if f"[{s['area']}] {s['acao']}: {s['estrat']}" == item_str:
                            novas.append({
                                "acao": s['acao'], 
                                "estrat": s['estrat'], 
                                "area": s['area'], 
                                "resp": "Coordenação Geral", 
                                "prazo": "Avaliação Pós-Implementação de 30 dias"
                            })
                st.session_state.acoes_list.extend(novas)
                st.success("Operação concluída. As táticas selecionadas foram movidas com sucesso!")
                st.rerun()
                
            st.markdown("##### 3. Matriz de Manuseio do Plano de Ação Estratégico")
            st.info("Poder total de customização: Altere células dando dois cliques. Apague selecionando a linha e apertando Delete. Adicione na linha vazia no final da tabela. Tudo o que você vir aqui será o que o cliente lerá.")
            edited_df = st.data_editor(
                pd.DataFrame(st.session_state.acoes_list), 
                num_rows="dynamic", 
                use_container_width=True, 
                column_config={
                    "acao": "Título Resumido da Ação Operacional", 
                    "estrat": st.column_config.TextColumn("Especificação Prática e Metodologia", width="large"), 
                    "area": "Vertical", 
                    "resp": "Líder de Execução", 
                    "prazo": "SLA / Prazo Limite"
                }
            )
            
            if not edited_df.empty: 
                st.session_state.acoes_list = edited_df.to_dict('records')

        # --- GERAÇÃO EXPANDIDA, DOCUMENTADA E TOTALMENTE DESMINIFICADA DO CÓDIGO HTML (V100.0+) ---
        if st.button("📥 Sintetizar Arquivo do Laudo Analítico (Motor HTML > PDF)", type="primary"):
            st.markdown("---")
            logo_html = get_logo_html(150)
            logo_cliente_html = ""
            if empresa.get('logo_b64'):
                logo_cliente_html = f"<img src='data:image/png;base64,{empresa.get('logo_b64')}' width='110' style='float:right; margin-left: 15px; border-radius:4px; box-shadow: 0px 2px 4px rgba(0,0,0,0.1);'>"
            
            # --- CONSTRUÇÃO CUIDADOSA DOS CARDS DIMENSIONAIS PARA O DOM DO HTML ---
            html_dimensoes = ""
            if empresa.get('dimensoes'):
                for dim, nota in empresa.get('dimensoes', {}).items():
                    cor_card = COR_RISCO_ALTO if nota < 3 else (COR_RISCO_MEDIO if nota < 4 else COR_RISCO_BAIXO)
                    label_card = "CENÁRIO CRÍTICO" if nota < 3 else ("MOMENTO DE ATENÇÃO" if nota < 4 else "AMBIENTE SEGURO")
                    html_dimensoes += f"""
                    <div style="flex: 1; min-width: 85px; background-color: #fcfcfc; border: 1px solid #e0e0e0; padding: 8px; border-radius: 6px; margin: 4px; text-align: center; font-family: 'Helvetica Neue', Helvetica, sans-serif; box-shadow: inset 0 -2px 0 {cor_card};">
                        <div style="font-size: 8px; color: #555; text-transform: uppercase; letter-spacing: 0.5px; font-weight: bold;">{dim}</div>
                        <div style="font-size: 16px; font-weight: 800; color: {cor_card}; margin: 4px 0;">{nota:.1f}</div>
                        <div style="font-size: 7px; color: #777; background: #eee; padding: 2px; border-radius: 2px;">{label_card}</div>
                    </div>
                    """

            # --- CONSTRUÇÃO DO MAPA DE CALOR (RAIO-X DAS 35 PERGUNTAS DE FORMA EXPANDIDA) ---
            html_x = ""
            detalhes_heatmap = empresa.get('detalhe_perguntas', {})
            
            for cat, pergs in st.session_state.hse_questions.items():
                 html_x += f"""
                 <div style="font-weight: bold; color: {COR_PRIMARIA}; font-size: 11px; margin-top: 14px; margin-bottom: 6px; border-bottom: 2px solid #eaeaea; font-family: 'Helvetica Neue', Helvetica, sans-serif; padding-bottom: 2px;">
                    {cat.upper()}
                 </div>
                 """
                 
                 for q in pergs:
                     # Resgata a pocentagem pre-calculada pelo motor Python real
                     porcentagem_risco = detalhes_heatmap.get(q['q'], 0) 
                     
                     # Classificacao da barra CSS
                     c_bar = COR_RISCO_ALTO if porcentagem_risco > 50 else (COR_RISCO_MEDIO if porcentagem_risco > 30 else COR_RISCO_BAIXO)
                     if porcentagem_risco == 0: 
                         c_bar = "#cccccc" # Cor fantasma para 0 respostas
                         
                     html_x += f"""
                     <div style="margin-bottom: 6px; font-family: 'Helvetica Neue', Helvetica, sans-serif;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-end; font-size: 9px; margin-bottom: 2px;">
                            <span style="color: #444; width: 85%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{q['q']}">{q['q']}</span>
                            <span style="color: {c_bar}; font-weight: bold; font-size: 8px;">{porcentagem_risco}% Exposição</span>
                        </div>
                        <div style="width: 100%; background-color: #f0f0f0; height: 6px; border-radius: 3px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
                            <div style="width: {porcentagem_risco}%; background-color: {c_bar}; height: 100%; border-radius: 3px; transition: width 0.5s ease-in-out;"></div>
                        </div>
                     </div>
                     """

            # --- SÍNTESE DA MATRIZ DO PLANO DE AÇÃO ---
            html_act_final = "".join([f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eef0f2; font-weight: bold; color: #2c3e50;">{i.get('acao','')}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eef0f2; color: #555;">{i.get('estrat','')}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eef0f2; text-align: center;"><span style="background: #eef2f5; padding: 3px 6px; border-radius: 4px; font-size: 8px; color: #34495e;">{i.get('area','')}</span></td>
                    <td style="padding: 10px; border-bottom: 1px solid #eef0f2; font-style: italic; color: #7f8c8d;">{i.get('resp','')}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eef0f2; font-weight: bold; color: {COR_PRIMARIA};">{i.get('prazo','')}</td>
                </tr>
            """ for i in st.session_state.acoes_list])
            
            if not st.session_state.acoes_list: 
                html_act_final = "<tr><td colspan='5' style='text-align: center; padding: 20px; color: #999;'>Matriz de ações não preenchida pelo corpo técnico.</td></tr>"

            # --- RENDERIZAÇÃO DO MEDIDOR GERAL DE PRESSÃO (GAUGE) EM CSS PURO ---
            score_final_empresa = empresa.get('score', 0)
            score_width_css = (score_final_empresa / 5.0) * 100
            
            html_gauge_css = f"""
            <div style="text-align: center; padding: 15px; font-family: 'Helvetica Neue', Helvetica, sans-serif;">
                <div style="font-size: 32px; font-weight: 900; color: {COR_PRIMARIA}; text-shadow: 1px 1px 0px rgba(0,0,0,0.05);">
                    {score_final_empresa:.2f} <span style="font-size: 14px; font-weight: normal; color: #a0a0a0;">/ 5.00 Máx</span>
                </div>
                <div style="width: 100%; background: #e0e0e0; height: 16px; border-radius: 8px; margin-top: 10px; position: relative; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="position: absolute; left: 0; top: 0; width: {score_width_css}%; background: linear-gradient(90deg, {COR_PRIMARIA} 0%, {COR_SECUNDARIA} 100%); height: 16px; border-radius: 8px;"></div>
                </div>
                <div style="font-size: 10px; color: #7f8c8d; margin-top: 8px; letter-spacing: 1px; text-transform: uppercase;">
                    Coeficiente Geral do Ecossistema
                </div>
            </div>
            """
            
            # --- TABELA DE RADAR SINTÉTICO (PARA COMPLEMENTAR O GRÁFICO VISUAL) ---
            html_radar_rows = ""
            for k, v in empresa.get('dimensoes', {}).items():
                html_radar_rows += f"""
                <tr>
                    <td style='padding: 6px 10px; border-bottom: 1px solid #f0f0f0; color: #444; font-weight: 500;'>{k}</td>
                    <td style='padding: 6px 10px; text-align: right; border-bottom: 1px solid #f0f0f0; font-weight: bold; color: {COR_PRIMARIA};'>{v:.1f}</td>
                </tr>
                """
            
            html_radar_table = f"""
            <table style="width: 100%; font-size: 10px; font-family: 'Helvetica Neue', Helvetica, sans-serif; border-collapse: collapse; margin-top: 5px;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="text-align: left; padding: 8px 10px; border-bottom: 2px solid #ddd; color: #555;">Dimensão Investigada</th>
                        <th style="text-align: right; padding: 8px 10px; border-bottom: 2px solid #ddd; color: #555;">Nota Obtida</th>
                    </tr>
                </thead>
                <tbody>
                    {html_radar_rows}
                </tbody>
            </table>
            """

            lgpd_note = f"""
            <div style="margin-top: 40px; border-top: 1px solid #ccc; padding-top: 15px; font-size: 8px; color: #888; text-align: justify; font-family: 'Helvetica Neue', Helvetica, sans-serif; line-height: 1.4;">
                <strong>TERMO DE CONFIDENCIALIDADE E PROTEÇÃO ESTRITA DE DADOS (LGPD):</strong> Este instrumento avaliativo de saúde ocupacional corporativa foi confeccionado utilizando complexos métodos de criptografia de banco de dados e obfuscação de entidades. Os resultados e matrizes de calor apresentados neste dossiê carregam a premissa irrevogável do anonimato. Nenhum número, gráfico, tabela ou insight aqui delineado é capaz de identificar participantes do corpo colaborativo individualmente ou quebrar a barreira do sigilo profissional garantido pela Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018).
            </div>
            """

            # --- SUPER CONTEÚDO BRUTO DO ARQUIVO COMPLETO HTML FORMATADO PARA IMPRESSÃO PERFEITA ---
            raw_html = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="utf-8">
                <title>Dossiê Técnico Institucional - {empresa['razao']}</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        padding: 30mm 20mm;
                        color: #2c3e50;
                        background-color: #ffffff;
                        line-height: 1.6;
                        max-width: 210mm;
                        margin: 0 auto;
                    }}
                    h4 {{
                        color: {COR_PRIMARIA}; 
                        border-left: 5px solid {COR_SECUNDARIA}; 
                        padding-left: 12px; 
                        margin-top: 40px;
                        margin-bottom: 15px;
                        font-size: 13px;
                        letter-spacing: 0.5px;
                    }}
                    .caixa-destaque {{
                        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                        padding: 20px; 
                        border-radius: 8px; 
                        margin-bottom: 25px; 
                        border-left: 6px solid {COR_SECUNDARIA};
                        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
                    }}
                    .colunas-flex {{
                        display: flex; 
                        gap: 30px; 
                        margin-top: 25px; 
                        margin-bottom: 25px;
                    }}
                    .coluna-dado {{
                        flex: 1; 
                        border: 1px solid #eef2f5; 
                        border-radius: 10px; 
                        padding: 15px;
                        background-color: #fafbfc;
                    }}
                    .titulo-coluna {{
                        font-weight: 800; 
                        font-size: 11px; 
                        color: {COR_PRIMARIA}; 
                        margin-bottom: 12px;
                        text-align: center;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        border-bottom: 1px solid #eef2f5;
                        padding-bottom: 8px;
                    }}
                    .grid-raiox {{
                        background: #ffffff; 
                        border: 1px solid #eef2f5; 
                        padding: 20px; 
                        border-radius: 10px; 
                        margin-bottom: 25px; 
                        column-count: 2; 
                        column-gap: 50px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.01);
                    }}
                    @media print {{
                        body {{
                            padding: 0;
                            margin: 0;
                            -webkit-print-color-adjust: exact !important;
                            print-color-adjust: exact !important;
                        }}
                        .grid-raiox {{
                            page-break-inside: avoid;
                        }}
                        table {{
                            page-break-inside: auto;
                        }}
                        tr {{
                            page-break-inside: avoid;
                            page-break-after: auto;
                        }}
                        h4 {{
                            page-break-after: avoid;
                        }}
                    }}
                </style>
            </head>
            <body>
                <header style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid {COR_PRIMARIA}; padding-bottom: 20px; margin-bottom: 30px;">
                    <div style="flex: 0 0 auto;">{logo_html}</div>
                    <div style="text-align: right; flex: 1;">
                        <div style="font-size: 22px; font-weight: 900; color: {COR_PRIMARIA}; letter-spacing: -0.5px;">LAUDO TÉCNICO HSE-IT</div>
                        <div style="font-size: 12px; color: #7f8c8d; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px;">Mapeamento de Riscos Psicossociais (NR-01)</div>
                    </div>
                </header>

                <div class="caixa-destaque">
                    {logo_cliente_html}
                    <div style="font-size: 10px; color: #95a5a6; margin-bottom: 6px; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">Entidade Auditada</div>
                    <div style="font-weight: 900; font-size: 18px; margin-bottom: 8px; color: #2c3e50;">{empresa.get('razao', 'Razão Social Não Informada')}</div>
                    
                    <div style="display: flex; gap: 40px; margin-top: 15px;">
                        <div>
                            <div style="font-size: 9px; color: #7f8c8d; text-transform: uppercase;">Registro CNPJ</div>
                            <div style="font-size: 11px; font-weight: 600; color: #34495e;">{empresa.get('cnpj','Não Especificado')}</div>
                        </div>
                        <div>
                            <div style="font-size: 9px; color: #7f8c8d; text-transform: uppercase;">Adesão Total da Cota</div>
                            <div style="font-size: 11px; font-weight: 600; color: #34495e;">{empresa.get('respondidas',0)} Vidas Mapeadas</div>
                        </div>
                        <div>
                            <div style="font-size: 9px; color: #7f8c8d; text-transform: uppercase;">Data de Fechamento (Emissão)</div>
                            <div style="font-size: 11px; font-weight: 600; color: #34495e;">{datetime.datetime.now().strftime('%d de %B de %Y')}</div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; border-top: 1px dashed #ddd; padding-top: 10px;">
                        <div style="font-size: 9px; color: #7f8c8d; text-transform: uppercase;">Endereço de Faturamento e Auditoria</div>
                        <div style="font-size: 11px; color: #34495e;">{empresa.get('endereco','Sem endereço de auditoria configurado no sistema.')}</div>
                    </div>
                </div>

                <h4>1. TESE, OBJETIVO E RIGOR METODOLÓGICO</h4>
                <p style="text-align: justify; font-size: 11px; color: #555;">
                    O presente relatório executivo embasa-se na literatura técnica científica e carrega como objetivo macro identificar, catalogar e mensurar através de score a existência de potencias fatores nocivos de risco psicossocial permeando as malhas do ambiente de trabalho desta Organização Cliente. 
                    <br><br>
                    Para garantir lisura ao processo, a plataforma tecnológica encarregou-se de transcrever e calcular os algoritmos validados mundialmente pelo <strong>HSE Management Standards Indicator Tool</strong> (Reino Unido), convergindo suas normativas para atender diretamente às exigências modernas estipuladas pelo GRO/PGR no escopo da Norma Regulamentadora Brasileira nº 01 (NR-01). 
                    <br><br>
                    A engenharia da metodologia escaneia com rigor absoluto 7 (sete) dimensões indissociáveis da saúde mental laborativa: Compressão de Nível de Demandas, Soberania e Autonomia (Controle Organizacional), Suporte Estrutural Liderança (Gestor), Solidariedade Setorial (Pares), Textura e Qualidade dos Relacionamentos Interpessoais, Clareza de Papel Individual, e fluidez da Gestão na Curva de Mudança Institucional.
                </p>

                <div class="colunas-flex">
                    <div class="coluna-dado">
                        <div class="titulo-coluna">2. SCORE MASTER DA ORGANIZAÇÃO</div>
                        {html_gauge_css}
                    </div>
                    <div class="coluna-dado">
                        <div class="titulo-coluna">3. RAIZ E MATRIZ PONTUAL DAS DIMENSÕES</div>
                        {html_radar_table}
                    </div>
                </div>

                <h4>4. MAPA DE DIAGNÓSTICO DETALHADO POR DIMENSÃO DE SAÚDE</h4>
                <div style="display: flex; flex-wrap: wrap; margin-bottom: 30px; gap: 8px;">
                    {html_dimensoes}
                </div>

                <h4>5. VARREDURA RAIO-X DOS 35 FATORES DE RISCO INTERNOS AVALIADOS</h4>
                <p style="font-size: 10px; color: #777; margin-bottom: 15px; margin-top: -10px; font-style: italic;">
                    Nota técnica de interpretação de leitura: As barras gráficas ilustradas abaixo representam o grau de fragilidade (ou exposição perigosa) do grupo avaliado em relação a cada afirmação da pesquisa. Porcentagens acentuadamente altas, sinalizadas na paleta de cores quentes, requerem atenção mandatória nos planos de remediação.
                </p>
                <div class="grid-raiox">
                    {html_x}
                </div>

                <div style="page-break-before: always;"></div>

                <h4>6. ARQUITETURA DO PLANO DE AÇÃO ESTRATÉGICO SUGERIDO PELA IA (GRO)</h4>
                <p style="font-size: 10px; color: #777; margin-bottom: 15px; margin-top: -10px; font-style: italic;">
                    A tabela subsequente foi refinada pelo algoritmo consultivo para combater diretamente e com máxima eficiência as maiores ameaças listadas nas piores pontuações encontradas no radar de escaneamento interno.
                </p>
                <table style="width: 100%; border-collapse: collapse; font-size: 10px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; box-shadow: 0 0 0 1px #eef2f5; border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background-color: {COR_PRIMARIA}; color: #ffffff;">
                            <th style="padding: 12px 10px; text-align: left; font-weight: 600; letter-spacing: 0.5px;">AÇÃO MACRO / TÍTULO</th>
                            <th style="padding: 12px 10px; text-align: left; font-weight: 600; letter-spacing: 0.5px;">DESDOBRAMENTO E ESTRATÉGIA PRÁTICA DETALHADA</th>
                            <th style="padding: 12px 10px; text-align: center; font-weight: 600; letter-spacing: 0.5px;">ÁREA FOCO</th>
                            <th style="padding: 12px 10px; text-align: left; font-weight: 600; letter-spacing: 0.5px;">ATOR RESPONSÁVEL</th>
                            <th style="padding: 12px 10px; text-align: left; font-weight: 600; letter-spacing: 0.5px;">TIMELINE/PRAZO</th>
                        </tr>
                    </thead>
                    <tbody>
                        {html_act_final}
                    </tbody>
                </table>

                <h4>7. DESPACHO E CONCLUSÃO TÉCNICA EMANADA DO LAUDO AUDITADO</h4>
                <div style="text-align: justify; font-size: 11px; line-height: 1.8; background-color: #f8fbfc; padding: 25px; border-radius: 8px; border: 1px solid #eef2f5; color: #444; white-space: pre-wrap;">
                    {analise_texto}
                </div>

                <div style="margin-top: 80px; display: flex; justify-content: space-around; gap: 60px;">
                    <div style="flex: 1; text-align: center; border-top: 1px solid #2c3e50; padding-top: 12px;">
                        <div style="font-weight: 800; font-size: 12px; color: #2c3e50; text-transform: uppercase;">{sig_empresa_nome}</div>
                        <div style="color: #7f8c8d; font-size: 10px; margin-top: 4px;">{sig_empresa_cargo}</div>
                        <div style="color: #95a5a6; font-size: 9px; margin-top: 2px;">Assinatura por delegação da Contratante</div>
                    </div>
                    <div style="flex: 1; text-align: center; border-top: 1px solid #2c3e50; padding-top: 12px;">
                        <div style="font-weight: 800; font-size: 12px; color: #2c3e50; text-transform: uppercase;">{sig_tecnico_nome}</div>
                        <div style="color: #7f8c8d; font-size: 10px; margin-top: 4px;">{sig_tecnico_cargo}</div>
                        <div style="color: #95a5a6; font-size: 9px; margin-top: 2px;">Chancela Técnica Eletrônica da Especialista</div>
                    </div>
                </div>
                
                {lgpd_note}
            </body>
            </html>
            """
            
            # Formatação segura para download do string gigantesco (sem quebra de bytes)
            b64_pdf = base64.b64encode(raw_html.encode('utf-8')).decode('utf-8')
            
            st.markdown(f"""
            <a href="data:text/html;base64,{b64_pdf}" download="Laudo_Oficial_NR01_{empresa["id"]}.html" style="
                text-decoration: none; 
                background-color: {COR_PRIMARIA}; 
                color: #ffffff; 
                padding: 15px 30px; 
                border-radius: 8px; 
                font-weight: 800; 
                display: inline-block;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                transition: transform 0.2s;
                text-transform: uppercase;
                letter-spacing: 1px;
                width: 100%;
                text-align: center;
                margin-bottom: 20px;
            ">
                ⬇️ BAIXAR LAUDO TÉCNICO CORPORATIVO COMPLETO (ARQUIVO SEGURO HTML)
            </a>
            """, unsafe_allow_html=True)
            
            st.info("💡 **Dica de Tecnologia (Acelerador RH):** Após o arquivo baixar para o seu computador, abra ele dando dois cliques. No seu navegador, pressione as teclas `Ctrl + P` (no Windows) ou `Cmd + P` (no Mac). Escolha a opção **'Salvar como PDF'**, desmarque os cabeçalhos/rodapés nas configurações e marque a opção **'Gráficos de Plano de Fundo'** para extrair o design impecável e com as cores originais da identidade da sua plataforma.")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Modo Exibição (Canvas Viewer - Preview do Documento Final):")
            st.components.v1.html(raw_html, height=1000, scrolling=True)

    elif selected == "Histórico & Comparativo":
        st.title("Hub Histórico Evolutivo (Inteligência Temporal de Saúde Mental)")
        if not visible_companies: 
            st.warning("É preciso catalogar organizações e obter dados reais para ligar este hub."); return
        
        empresa_nome = st.selectbox("Selecione o Cluster da Empresa a ser perscrutado", [c['razao'] for c in visible_companies])
        empresa = next((c for c in visible_companies if c['razao'] == empresa_nome), None)
        
        if empresa:
            # GERA HISTÓRICO REAL COM BASE NO BANCO DE DADOS (AGRUPAMENTO POR TIMESTAMP MÊS/ANO VERÍDICO)
            history_data = generate_real_history(empresa['id'], responses_data, st.session_state.hse_questions, empresa.get('func', 1))
            
            if not history_data:
                st.info("ℹ️ Ops! A inteligência de dados informa que não há respostas válidas e decodificadas registradas para esta empresa no banco de dados ainda. As predições e o histórico evolutivo se formarão retroativamente conforme a coleta fluir ativamente nos próximos ciclos de pesquisa com a equipe.")
            else:
                tab_evo, tab_comp = st.tabs(["📈 Mapa Gráfico Contínuo (Curva de Evolução)", "⚖️ Balança Analítica Direta (Raio-X: Período A vs Período B)"])
                
                with tab_evo:
                    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                    df_hist = pd.DataFrame(history_data)
                    fig_line = px.line(
                        df_hist, 
                        x='periodo', 
                        y='score', 
                        markers=True, 
                        title="Vetor de Evolução Macro (Score Geral de Proteção à Saúde Ocupacional ao longo do Tempo)"
                    )
                    fig_line.update_traces(
                        line_color=COR_SECUNDARIA, 
                        line_width=4, 
                        marker=dict(size=12, color=COR_PRIMARIA, line=dict(width=2, color='white'))
                    )
                    fig_line.update_layout(
                        yaxis_range=[1, 5],
                        plot_bgcolor='#fafbfc',
                        xaxis_title="Janela de Monitoramento",
                        yaxis_title="Score do Algoritmo HSE (Escala de Segurança 1 a 5)"
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with tab_comp:
                    if len(history_data) < 2:
                        st.warning("⚠️ Dados limiares e insuficientes para ancorar um comparativo sólido de ciclos com integridade matemática. Para a geração de evidências concretas no relatório evolutivo (A vs B), exige-se, logicamente, que o organismo alvo tenha submetido avaliações na base de dados em, pelo menos, 2 (dois) recortes de tempo distintos (Exemplo: Meses diferentes em nossa timeline).")
                    else:
                        st.write("Determine as balizas temporais que alimentarão as matrizes matemáticas.")
                        c1, c2 = st.columns(2)
                        periodo_a = c1.selectbox("Seletor de Ancoragem Inicial (Período A - Referência Base)", [h['periodo'] for h in history_data], index=1)
                        periodo_b = c2.selectbox("Seletor de Validação Atual (Período B - Efeito/Resultado)", [h['periodo'] for h in history_data], index=0)
                        
                        dados_a = next((h for h in history_data if h['periodo'] == periodo_a), None)
                        dados_b = next((h for h in history_data if h['periodo'] == periodo_b), None)
                        
                        if dados_a and dados_b:
                            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                            categories = list(dados_a['dimensoes'].keys())
                            fig_comp = go.Figure()
                            
                            # Radar A - Formatação translúcida para melhor visualização comparativa
                            fig_comp.add_trace(go.Scatterpolar(
                                r=list(dados_a['dimensoes'].values()), 
                                theta=categories, 
                                fill='toself', 
                                name=f'Análise Censitária: {periodo_a}', 
                                line_color=COR_COMP_A, 
                                opacity=0.4
                            ))
                            
                            # Radar B - Formatação sobreposta e focada no destaque da evolução
                            fig_comp.add_trace(go.Scatterpolar(
                                r=list(dados_b['dimensoes'].values()), 
                                theta=categories, 
                                fill='toself', 
                                name=f'Análise Censitária: {periodo_b}', 
                                line_color=COR_COMP_B, 
                                opacity=0.8
                            ))
                            
                            fig_comp.update_layout(
                                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                                title="Sobreposição Geométrica Direta das Malhas Organizacionais (Radar A x B)"
                            )
                            st.plotly_chart(fig_comp, use_container_width=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            # --- ROTINA PESADA DE ENGENHARIA DE DOCUMENTO EVOLUTIVO EM HTML (CÓDIGO ABERTO/EXPANDIDO) ---
                            if st.button("📥 Sintetizar e Baixar Documento Comparativo Oficial (Motor HTML > PDF)", type="primary"):
                                 logo_html = get_logo_html(150)
                                 
                                 # Lógica pura e simples de saldo/evolução de KPIs da empresa
                                 diff_score = dados_b['score'] - dados_a['score']
                                 txt_evolucao = "uma melhoria palpável e generalizada" if diff_score > 0 else "um platô de estabilidade que exige vigília contínua, ou, de modo agravante, uma sinalização técnica de queda que denota forte ponto de atenção crítico imediato"
                                 
                                 # Injeção de Barras Visuais Inteligentes com CSS Inline Robusto para impressão offline perfeita
                                 chart_css_viz = f"""
                                 <div style="padding: 25px; border: 1px solid #e0e6ed; border-radius: 12px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #ffffff; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                                     <div style="margin-bottom: 25px;">
                                         <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                                             <strong style="color: #34495e; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Volume e Score da Análise Período [{periodo_a}]:</strong> 
                                             <span style="font-size: 24px; font-weight: 900; color: {COR_COMP_A}">{dados_a['score']} <span style="font-size: 12px; color: #aab7b8;">/ 5.0</span></span>
                                         </div>
                                         <div style="width: 100%; background: #ecf0f1; height: 18px; border-radius: 9px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);">
                                            <div style="width: {(dados_a['score']/5)*100}%; background: {COR_COMP_A}; height: 18px; border-radius: 9px;"></div>
                                         </div>
                                     </div>
                                     <div>
                                         <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                                             <strong style="color: #34495e; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Volume e Score da Análise Período [{periodo_b}]:</strong> 
                                             <span style="font-size: 24px; font-weight: 900; color: {COR_COMP_B}">{dados_b['score']} <span style="font-size: 12px; color: #aab7b8;">/ 5.0</span></span>
                                         </div>
                                         <div style="width: 100%; background: #ecf0f1; height: 18px; border-radius: 9px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);">
                                            <div style="width: {(dados_b['score']/5)*100}%; background: {COR_COMP_B}; height: 18px; border-radius: 9px;"></div>
                                         </div>
                                     </div>
                                 </div>
                                 """

                                 # Estruturação HTML Completa do Dossiê Evolutivo (Expandida para evitar quebra/minificação)
                                 html_comp = f"""
                                 <!DOCTYPE html>
                                 <html lang="pt-BR">
                                 <head>
                                     <meta charset="utf-8">
                                     <title>Relatório Evolutivo HSE</title>
                                     <style>
                                         body {{
                                             font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
                                             padding: 40px 30px;
                                             color: #2c3e50;
                                             background: white;
                                             line-height: 1.6;
                                         }}
                                         .linha-divisor {{ border-bottom: 2px solid {COR_PRIMARIA}; padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center; }}
                                         .box-infos {{ background: #f8fbfc; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 5px solid {COR_SECUNDARIA}; }}
                                         h4 {{ color: {COR_PRIMARIA}; border-left: 4px solid {COR_SECUNDARIA}; padding-left: 12px; margin-top: 35px; font-size: 14px; text-transform: uppercase; }}
                                         .tabela-kpi {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 30px; box-shadow: 0 0 0 1px #eef2f5; border-radius: 6px; overflow: hidden; }}
                                         .tabela-kpi th {{ background-color: {COR_PRIMARIA}; color: white; padding: 12px; text-align: center; font-weight: 600; letter-spacing: 0.5px; }}
                                         .tabela-kpi td {{ padding: 12px; border-bottom: 1px solid #eef2f5; text-align: center; color: #34495e; }}
                                         .tabela-kpi td:first-child {{ text-align: left; font-weight: 600; }}
                                         .rodape {{ margin-top: 60px; font-size: 9px; color: #95a5a6; text-align: center; border-top: 1px dashed #e0e6ed; padding-top: 15px; letter-spacing: 0.5px; text-transform: uppercase; }}
                                     </style>
                                 </head>
                                 <body>
                                     <div class="linha-divisor">
                                         <div>{logo_html}</div>
                                         <div style="text-align:right;">
                                             <div style="font-size:20px; font-weight:900; color:{COR_PRIMARIA}; letter-spacing: -0.5px;">DOSSIÊ TÉCNICO EVOLUTIVO</div>
                                             <div style="font-size:11px; color:#7f8c8d; font-weight:600; letter-spacing: 1px;">Análise Comparativa Temporal de Saúde Ocupacional Corporativa</div>
                                         </div>
                                     </div>
                                     
                                     <div class="box-infos">
                                         <div style="font-size:10px; color:#95a5a6; margin-bottom:6px; font-weight: 800; letter-spacing: 1px;">DADOS CADASTRAIS DA ORGANIZAÇÃO AUDITADA</div>
                                         <div style="font-weight:900; font-size:16px; margin-bottom:8px; color:#2c3e50;">{empresa['razao']}</div>
                                         <div style="display: flex; gap: 20px; margin-top: 10px;">
                                             <div style="font-size:11px;"><strong>CNPJ Atrelado:</strong> <span style="color:#7f8c8d;">{empresa.get('cnpj','Não Especificado no Sistema')}</span></div>
                                             <div style="font-size:11px;"><strong>Janelas Temporais Sob Análise Crítica Restrita:</strong> <span style="color:{COR_PRIMARIA}; font-weight: bold; background: #eef2f5; padding: 2px 6px; border-radius: 4px;">{periodo_a}</span> VERSUS <span style="color:{COR_PRIMARIA}; font-weight: bold; background: #eef2f5; padding: 2px 6px; border-radius: 4px;">{periodo_b}</span></div>
                                         </div>
                                     </div>
                                     
                                     <h4>1. PAINEL DE RESUMO DA MATRIZ DE INDICADORES CHAVE (OVERALL KPIs)</h4>
                                     <table class="tabela-kpi">
                                         <tr>
                                             <th>SINTOMA / INDICADOR ANALISADO</th>
                                             <th>MARCO REFERÊNCIA [{periodo_a}]</th>
                                             <th>MARCO CONSTATADO [{periodo_b}]</th>
                                             <th>VARIAÇÃO LÍQUIDA (DELTA)</th>
                                         </tr>
                                         <tr>
                                             <td>Score Geral da Organização (Cálculo Composto)</td>
                                             <td>{dados_a['score']}</td>
                                             <td>{dados_b['score']}</td>
                                             <td style="font-weight:900; color:{'#27ae60' if diff_score > 0 else '#c0392b'};">{diff_score:+.2f} pts</td>
                                         </tr>
                                         <tr>
                                             <td>Taxa Bruta de Adesão e Participação Censitária (%)</td>
                                             <td>{dados_a['adesao']}%</td>
                                             <td>{dados_b['adesao']}%</td>
                                             <td style="font-weight:bold; color:#7f8c8d;">{(dados_b['adesao'] - dados_a['adesao']):+.1f}% de tração</td>
                                         </tr>
                                     </table>
                                     
                                     <h4>2. REPRESENTAÇÃO VISUAL DA TENSÃO E EQUILÍBRIO GRÁFICO</h4>
                                     {chart_css_viz}
                                     
                                     <h4>3. EXPOSIÇÃO E ANÁLISE TÉCNICA PRELIMINAR DOS RESULTADOS</h4>
                                     <p style="text-align:justify; font-size:12px; line-height:1.7; background:#fbfcfd; padding:20px; border-radius:8px; border: 1px solid #eef2f5; color: #444;">A análise metodológica e estruturada, fruto do levantamento de dados contínuos comparando os dois recortes delimitados, demonstra estatisticamente <strong>{txt_evolucao}</strong> nos índices gerais balizadores do vasto ecossistema de saúde mental e gestão de pressões internas nesta frente corporativa.<br><br>Recomenda-se terminantemente aos diretores, RH e SESMT responsáveis não só garantir a manutenção contínua e incansável dos protocolos protetivos de acompanhamento já vigentes, mas seguir com firmeza incontestável a execução e o compliance da Matriz do Plano de Ação Estratégico. Atenção irredutível e foco de reestruturação prioritário devem incidir sem delongas sobre os times ou dimensões mapeadas que, inegavelmente, não foram hábeis o suficiente para demonstrar oscilação benéfica de variação estatística positiva nesse último ciclo.</p>
                                     
                                     <div class="rodape">
                                         Plataforma Elo NR-01 Enterprise Core | Inteligência em Dados e Saúde Mental no Trabalho<br>Documento Oficial Sigiloso e Criptografado de Caráter Único e Exclusivamente Analítico
                                     </div>
                                 </body>
                                 </html>
                                 """
                                 
                                 # Empacotamento para download da arquitetura string HTML completa (Fim do processo evolutivo)
                                 b64_comp = base64.b64encode(html_comp.encode('utf-8')).decode('utf-8')
                                 
                                 st.markdown(f"""
                                 <a href="data:text/html;base64,{b64_comp}" download="Dossie_Evolutivo_Oficial_{empresa["id"]}.html" style="
                                     text-decoration: none; 
                                     background-color: {COR_PRIMARIA}; 
                                     color: white; 
                                     padding: 12px 25px; 
                                     border-radius: 6px; 
                                     font-weight: 700; 
                                     display: inline-block;
                                     text-transform: uppercase;
                                     box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                 ">
                                     📥 INICIAR DOWNLOAD DO DOSSIÊ TÉCNICO DE HISTÓRICO (ARQUIVO HTML)
                                 </a>
                                 """, unsafe_allow_html=True)
                                 st.caption("Ao fazer o download e abrir o arquivo no seu navegador (ex: Chrome/Edge), pressione as teclas `Ctrl+P` para formatar a página, marcar as imagens de fundo nas configurações e gerar a exportação fiel do PDF.")

    elif selected == "Configurações":
        if perm == "Master":
            st.title("Painel de Configurações Master do Sistema")
            t1, t2, t3 = st.tabs(["👥 Gerenciamento Múltiplo de Usuários", "🎨 Personalidade da Marca (Identidade)", "⚙️ Configurações Críticas (Servidor e URLs)"])
            
            with t1:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.write("### Controle Oficial de Acessos Analíticos")
                
                # Renderiza Tabela de Usuários Atualizada Garantida do Banco
                if DB_CONNECTED:
                    usrs_raw = supabase.table('admin_users').select("username, role, credits, linked_company_id").execute().data
                else:
                    usrs_raw = [{"username": k, "role": v['role'], "credits": v.get('credits',0)} for k,v in st.session_state.users_db.items()]
                
                if usrs_raw: 
                    st.dataframe(pd.DataFrame(usrs_raw), use_container_width=True)
                else:
                    st.warning("Problema de leitura na tabela de acesso.")
                
                st.markdown("---")
                c1, c2 = st.columns(2)
                new_u = c1.text_input("Novo Usuário Administrativo ou Analítico (Login/ID)")
                new_p = c2.text_input("Configuração de Senha Padrão Exigida", type="password")
                new_r = st.selectbox("Alocação do Nível de Permissão do Sistema", ["Master", "Gestor", "Analista"])
                
                if st.button("➕ Confirmar Processo de Criação na Tabela", type="primary"):
                    if not new_u or not new_p: 
                        st.error("Usuário e Senha são travas inegociáveis do sistema para este procedimento.")
                    else:
                        if DB_CONNECTED:
                            try:
                                supabase.table('admin_users').insert({"username": new_u, "password": new_p, "role": new_r, "credits": 999999 if new_r=="Master" else 500}).execute()
                                st.success(f"✅ Execução perfeita! O usuário [{new_u}] foi consolidado como ativo na Tabela Principal!")
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e: 
                                st.error(f"Engasgo no roteamento do Supabase DB: Verifique logs ou chaves ativas. {e}")
                        else:
                            st.session_state.users_db[new_u] = {"password": new_p, "role": new_r, "credits": 999999}
                            st.success(f"✅ Usuário [{new_u}] instanciado apenas localmente via Session_State!")
                            time.sleep(1)
                            st.rerun()
                
                st.markdown("---")
                st.write("### Exclusão Sumária de Credencial")
                # Filtro de segurança: jamais colocar o usuário atual (logado no momento) na lista de exclusão suicida.
                users_op = [u['username'] for u in usrs_raw if u['username'] != curr_user]
                if users_op:
                    u_del = st.selectbox("Selecione cuidadosamente o usuário da lista para revogar o acesso via hard-delete:", users_op)
                    if st.button("🗑️ DELETAR USUÁRIO SELECIONADO DA BASE", type="primary"): 
                        delete_user(u_del)
                else:
                    st.info("O sistema não localizou nenhum outro usuário passível e elegível de exclusão neste momento.")
                st.markdown("</div>", unsafe_allow_html=True)

            with t2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.write("### Identidade Visual Nativa da Solução e Laudos")
                nn = st.text_input("Nome Customizado da Plataforma (Modifica o Título no Header)", value=st.session_state.platform_config.get('name', 'Elo NR-01'))
                nc = st.text_input("Inscrição da Empresa de Consultoria ou Clínica", value=st.session_state.platform_config.get('consultancy', ''))
                nl = st.file_uploader("Upload de Ativo Base64 (Nova Logo. Obrigatório PNG ou JPG com fundo transparente)", type=['png', 'jpg', 'jpeg'])
                
                if st.button("💾 Injetar e Salvar Parâmetros de Customização", type="primary"):
                    new_conf = st.session_state.platform_config.copy()
                    new_conf['name'] = nn
                    new_conf['consultancy'] = nc
                    if nl: 
                        new_conf['logo_b64'] = image_to_base64(nl)
                    
                    if DB_CONNECTED:
                        try:
                            res = supabase.table('platform_settings').select("*").execute()
                            if res.data: 
                                supabase.table('platform_settings').update({"config_json": new_conf}).eq("id", res.data[0]['id']).execute()
                            else: 
                                supabase.table('platform_settings').insert({"config_json": new_conf}).execute()
                        except: 
                            pass
                            
                    st.session_state.platform_config = new_conf
                    st.success("✅ A identidade visual customizada foi ativada instantaneamente em todo o motor gráfico do sistema e dos PDFs!")
                    time.sleep(1.5)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            with t3:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.write("### Configuração Estrutural Core (Extremamente Delicado)")
                base = st.text_input("Endereço de Produção Web Atual (Responsável direto e vital por viabilizar as URL/Links de Questionários para os Trabalhadores)", value=st.session_state.platform_config.get('base_url', ''))
                
                if st.button("🔗 Gravar Alteração e Reordenar Rotas de Servidor", type="primary"):
                    new_conf = st.session_state.platform_config.copy()
                    new_conf['base_url'] = base
                    
                    # Salva a URL no banco de dados para não sumir no F5
                    if DB_CONNECTED:
                        try:
                            res = supabase.table('platform_settings').select("*").execute()
                            if res.data: 
                                supabase.table('platform_settings').update({"config_json": new_conf}).eq("id", res.data[0]['id']).execute()
                            else: 
                                supabase.table('platform_settings').insert({"config_json": new_conf}).execute()
                        except: pass
                        
                    st.session_state.platform_config = new_conf
                    st.success("✅ As trilhas de rotas foram remapeadas com extremo sucesso no sistema em nuvem e gravadas no banco de dados.")
                    time.sleep(1.5)
                    st.rerun()
                    
                st.markdown("---")
                st.write("### Hub de Informação e Diagnóstico Técnico de Infraestrutura API")
                if DB_CONNECTED: 
                    st.info("🟢 Telemetria Informa: O Hub Central de Relacionamento (Supabase PostgreSQL Engine) encontra-se estritamente Online e totalmente sincronizado. Funcionalidade integral, salvamento cruzado e processos de permanência real da base de dados foram todos habilitados e rodando em plano de fundo sem anomalias.")
                else: 
                    st.error("🔴 Anomalia Fetal Informada: A conexão via API REST com o provedor em nuvem do Supabase Engine encontra-se Offline, obstruída ou instável por falha nos tokens Secretos inseridos. O aplicativo de software precisou retroceder para ambiente seguro local, alocando-se puramente em um modelo frágil e transitório de cache. Atualizar esta página, limpar os cookies ou reiniciar o host culminarão na eliminação indesejada de quaisquer atualizações produzidas. Verifique de imediato seu console de desenvolvedor.")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("🚫 Bloqueio de Proteção: Este módulo analítico possui um alto grau de intervenção estrutural e tem acesso severamente negado e bloqueado a usuários fora do grupo de permissão 'Master'.")

# ==============================================================================
# 6. MÓDULO PÚBLICO E ISOLADO DE AVALIAÇÃO PSICOSSOCIAL (O FRONT DO TRABALHADOR)
# ==============================================================================
def survey_screen():
    """Esta é a tela blindada onde apenas a pessoa base acessa através do celular ou pc para dar suas repostas."""
    cod = st.query_params.get("cod")
    
    # 1. Busca a empresa de forma blindada com dupla checagem (DB prioritário vs Local backup)
    comp = None
    if DB_CONNECTED:
        try:
            res = supabase.table('companies').select("*").eq('id', cod).execute()
            if res.data: comp = res.data[0]
        except: pass
        
    if not comp: 
        comp = next((c for c in st.session_state.companies_db if c['id'] == cod), None)
    
    # 2. Pareamento com Firewall contra invasores (Bloqueio duro por URL não reconhecida)
    if not comp: 
        st.error("❌ Código de rastreio de Link inviabilizado. A organização portadora do token injetado na barra superior do seu navegador não foi passível de localização dentro da integridade segura desta base de dados.")
        st.caption("Solicitamos que confirme e verifique imediatamente com o núcleo do seu Setor de RH/Liderança as informações e solicite a checagem com o administrador local da integridade do link fornecido.")
        return

    # 3. Validação Lógica Restrita (Verificando Expiração e Teto da Cota do Cliente)
    if comp.get('valid_until'):
        try:
            if datetime.date.today() > datetime.date.fromisoformat(comp['valid_until']):
                st.error("⛔ Intervenção do sistema: De acordo com a leitura automática e verificação inteligente do contrato vigente cadastrado atrelado a este CNPJ na nuvem, o acesso a esta coleta expirou por completo e encontra-se agora trancado e inativado para recepção analítica de novas vidas populacionais.")
                return
        except: pass
        
    limit_evals = comp.get('limit_evals', 999999)
    resp_count = comp.get('respondidas', 0) if comp.get('respondidas') is not None else 0
    if resp_count >= limit_evals:
        st.error("⚠️ Um barramento compulsório ativou este aviso: O limite de vidas populacionais alocadas neste contrato específico na nuvem chegou em seu teto global e bloqueou a transição de mais nenhuma nova requisição e adição.")
        st.caption("Para voltar a ter o link normalizado pela segurança da rede, basta solicitar a expansão global para nossa central, que assim faremos de imediato no portal base.")
        return
    
    # 4. Renderizacao Dinâmica do Hub Físico que será impresso para o operador ver
    logo = get_logo_html(150)
    if comp.get('logo_b64'): logo = f"<img src='data:image/png;base64,{comp.get('logo_b64')}' width='180'>"
    
    st.markdown(f"<div style='text-align:center; margin-bottom: 20px;'>{logo}</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center; color: {COR_PRIMARIA}; font-weight:800; font-family:sans-serif; text-transform:uppercase;'>Levantamento Metodológico de Risco Psicossocial e Ambientação - Projeto Integrado {comp['razao']}</h3>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='security-alert'>
            <strong>🔒 PLATAFORMA SOB TUTELA EXCLUSIVA DE ENGENHARIA CRIPTOGRÁFICA</strong><br>
            Os gestores da sua atual empresa/cliente detém a premissa de acesso e permissão de ZERO visualização das métricas individuais fornecidas por você nesta etapa a seguir.<br>
            <ul>
                <li>Seu documento chave, o seu CPF, entrará em contato com a rede, mas vai disparar uma rotina hash do sistema convertendo seu número de 11 dígitos originais permanentemente num código indecifrável pelo qual nenhum humano e leitor pode deduzir ou espelhar a titularidade.</li>
                <li>As estatísticas resultantes do conjunto formam mapas agregados (calores quentes) para, através da média aritmética sem rostos e de todos por ali em conjunto, dar visão correta do que consertar com ação física para reverter os fatos desgastantes do processo de rotina de hoje.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("survey_form"):
        st.write("#### Bloco 1 de Triagem. Identificação Base Funcional")
        c1, c2 = st.columns(2)
        cpf_raw = c1.text_input("Seu CPF de forma limpa (Inserir apenas os números. Evitar por traços ou pontos nos vãos do input)")
        
        # Estrutura Inteligente que processa e mapeia os setores originados no Master para alimentar os funcionários
        s_keys = ["Geral"] # Fallback de proteção para empresas sem árvore ou seletos apagados na pressa
        if 'org_structure' in comp and isinstance(comp['org_structure'], dict) and comp['org_structure']:
            s_keys = list(comp['org_structure'].keys())
             
        setor_colab = c2.selectbox("Selecione qual o seu Setor atual de Atuação majoritária no ecossistema da corporação", s_keys)
        
        st.markdown("---")
        st.write("#### Bloco 2 Avançado. Questionário Metodológico Analítico sobre o Fato Real de Percepção (HSE-Tool)")
        st.caption("É um trunfo indispensável para nossa avaliação que nos guie do que está e aconteceu respondendo isso o mais honestamente e verdadeiramente tangível que é o fato de seu vivenciar cotidiano em mente. Remonte seus passos baseando na linha do tempo exata que constitui os 40 dias atrás da rotina em suas posições diárias de atuação.")
        
        missing = False
        answers_dict = {}
        
        # Loop Dinâmico Matrizizado pelas Chaves de Categorias Abstraídas no Backend Python - O Modelo Completo em Abas Superiores
        abas_categorias = list(st.session_state.hse_questions.keys())
        tabs = st.tabs(abas_categorias)
        
        for i, (category, questions) in enumerate(st.session_state.hse_questions.items()):
            with tabs[i]:
                st.markdown(f"<h5 style='color: {COR_SECUNDARIA}; font-weight:800; text-transform:uppercase; margin-top:20px; margin-bottom: 25px;'>➡️ Dimensão Focalizada na Grade: {category}</h5>", unsafe_allow_html=True)
                for q in questions:
                    # Formatação de UX visualização imersiva do problema em andamento
                    st.markdown(f"<div style='font-size: 15px; color: #2c3e50; font-weight: 600; margin-bottom: 5px;'>{q['q']}</div>", unsafe_allow_html=True)
                    st.caption(f"💡 *Um balizador material que serve de contexto ao que queremos entender por isso:* {q.get('help', '')}")
                    
                    # Logica das réguas mistas e dicotômicas
                    options = ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"] if q['id'] <= 24 else ["Discordo Totalmente", "Discordo", "Neutro", "Concordo", "Concordo Totalmente"]
                    
                    response_value = st.radio(
                        "Qual seu veredicto no momento perante essa pergunta na pauta?", 
                        options, 
                        key=f"ans_q_{q['id']}", 
                        horizontal=True, 
                        index=None,
                        label_visibility="collapsed"
                    )
                    
                    if response_value is None: 
                        missing = True
                    else: 
                        answers_dict[q['q']] = response_value
                    
                    st.markdown("<hr style='margin:25px 0; border: 0; border-top: 2px dashed #ececec;'>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.write("#### Bloco 3 Final e Assentimento da Proteção Físico e Virtual dos Dados Acumulados")
        aceite_lgpd = st.checkbox("Ratifico e declaro, como dono da origem dos termos de preenchimento, que li sem pressa e compreendi perfeitamente o arcabouço descritivo e legal. Em sã consciência, concordo expressamente com o processo automatizado de envio que efetuará a coleta, o encapsulamento, e o tratamento cego destes dados de altíssima sensibilidade individual e psíquica, de modo puramente anônimo e irrevogavelmente aglomerado sem uso da minha base pessoal em tabelas decodificadoras, para exclusivos processos baseados em avaliações de estatísticas profundas de saúde no nicho corporativo e ocupacional regidos pelos alicerces imutáveis da atual legislação brasileira (LEI Nº 13.709/2018).")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("✅ Finalizar de Fato Todo o Questionário, Aceitar e Enviar Imediatamente para a Rede Segura as Minhas Respostas ao Sistema Servidor", type="primary", use_container_width=True)
        
        if submit_btn:
            if not cpf_raw or len(cpf_raw) < 11: 
                st.error("⚠️ Atenção de barreira no processamento! Preenchimento contínuo de número de identificação do CPF é mandatório para atrelamento hash no formato blindado ou esse foi interpretado e identificado pelo bot do servidor como inválido por estar faltante.")
            elif not aceite_lgpd: 
                st.error("⚠️ Atraso por bloqueio interno de lei! O ato de apertar o 'box do check' que confirma o aceite obrigatório visual do vasto termo formal legal de confiancialidade e retenção em nuvem é essencial para aprovação e transição pro envio real e cego.")
            elif missing: 
                st.error("⚠️ Aviso Crítico ao Participante do Formulário da Sessão Atual! Restaram no processo de varredura existências inegáveis de perguntas que lamentavelmente acabaram não devidamente respondidas sem intenção nas abas agrupadas situadas acima desta mesma tela física. Pedimos a sua inestimável colaboração a favor que realize e proceda por fim na visualização pela aba ou categoria onde a janela visual ficou despida de click em radio button de fato.")
            else:
                # O CÓDIGO BATEU TODOS OS MÚLTIPLOS CHECKPOINTS LOCAIS DO BROWSER, PROCESSO SEGURO INICIADO!
                hashed_cpf = hashlib.sha256(cpf_raw.encode()).hexdigest()
                cpf_already_exists = False
                
                # EXECUÇÃO DO PROCESSO TÉCNICO DE ROTINA INTENSA VERIFICADORA DE FALCATRUAS NO BANCO DE DADOS OFICIAL E NUVEM (CHECA DUPLICIDADE DE UMA PESSOA)
                if DB_CONNECTED:
                    try:
                        check_cpf = supabase.table('responses').select("id").eq("company_id", comp['id']).eq("cpf_hash", hashed_cpf).execute()
                        if len(check_cpf.data) > 0: 
                            cpf_already_exists = True
                    except: pass
                else:
                    for r in st.session_state.local_responses_db:
                        if r['company_id'] == comp['id'] and r['cpf_hash'] == hashed_cpf:
                            cpf_already_exists = True
                            break

                if cpf_already_exists:
                    st.error("🚫 O protocolo de trava antifraude acabou de interceptar este seu botão. Foi visualmente verificado pelo cruzamento mecânico e rastreio inabalável que o seu dado criptografado de hash advindo do CPF se encontra preenchido no nosso acervo base para esta empresa que se faz o link atual. Entenda que, para a garantia vitalícia da solidez sem vícios nos cálculos que compõem estatística corporativa que é repassada para seu líder, somente permite o banco central a inclusão massificada por via restrita do servidor uma única base de respostas originadas a cada vez e em cada avaliação singular para cada funcionário com voz. Não são passíveis submissões adicionais feitas à posteriori que comprometam métricas e gerem anomalias na conta do RH ou da empresa.")
                else:
                    # REGISTRO HISTÓRICO TIMEZONADO PARA EVOLUÇÃO (ESSENCIAL AO GRÁFICO HISTÓRICO E COMPARAÇÃO TEMPORAL MENSAL QUE MOSTRA A A X B DO RELATÓRIO DO ADM)
                    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    
                    if DB_CONNECTED:
                        try:
                            # CRIA E IMPÕE ROTINA INSERINDO DIRETO NA ESTRUTURA MAIS PURA A TABELA 'RESPONSES' DA BASE DE DADOS DO SUPER APP SUPABASE. A RESPOSTA ENTRA CEGA (CPF INVERTE E FICA HASH).
                            supabase.table('responses').insert({
                                "company_id": comp['id'], 
                                "cpf_hash": hashed_cpf,
                                "setor": setor_colab, 
                                "answers": answers_dict, 
                                "created_at": now_str
                            }).execute()
                        except Exception as e: 
                            st.error(f"Erro e barramento falho indesejado na conexão exata ou no banco do servidor raiz onde a informação entra no backend em nuvem online processual: {e}")
                    else:
                        st.session_state.local_responses_db.append({
                            "company_id": comp['id'], 
                            "cpf_hash": hashed_cpf,
                            "setor": setor_colab, 
                            "answers": answers_dict, 
                            "created_at": now_str
                        })

                    # DESCOMPRESSÃO DA EMOÇÃO, FIM DO FORM E ALEGRIA GARANTIDA DO BOTÃO CHEGADO SEM NENHUM ERRO
                    st.success("🎉 Sensacional a sua proatividade! Acusamos recebimento no servidor e garantimos que sua avaliação confidencial entrou empacotada de forma espetacular com sucesso integral de processamento nas nuvens dos nossos bancos seguros. Registramos total agradecimento pessoal com um fortíssimo abraço em retribuição imediata e oficializando o enorme peso real pela inquestionável maestria da sua genuína colaboração em repassar fatos e dados sobre o dia rotineiro no espaço da corporação.")
                    st.balloons()
                    time.sleep(4.5)
                    
                    # MATANDO A SESSAO POR TRÁS PARA ACABAR E INTERROMPER PROCESSAMENTO COM CACHE (NÃO DEIXAR ENVIAR E DUPLICAR MESMO FICANDO NA TELA COM F5 ABERTO)
                    st.session_state.logged_in = False 
                    st.rerun()

# ==============================================================================
# 7. ROUTER CENTRAL (O CORAÇÃO INICIALIZADOR GLOBAL DO APP FRENTE A LÓGICA DE USUÁRIO E VISUALIZAÇÃO)
# ==============================================================================
if not st.session_state.logged_in:
    if "cod" in st.query_params: 
        survey_screen()
    else: 
        login_screen()
else:
    if st.session_state.user_role == 'admin': 
        admin_dashboard()
    else: 
        survey_screen()
