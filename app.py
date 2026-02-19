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
    
    /* Tabelas HTML Relatório */
    .rep-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 10px; }}
    .rep-table th {{ background-color: {COR_PRIMARIA}; color: white; padding: 8px; text-align: left; font-size: 9px; }}
    .rep-table td {{ border-bottom: 1px solid #eee; padding: 8px; vertical-align: top; }}
    
    /* Ajuste Radio Button Horizontal - UX Melhorada */
    div[role="radiogroup"] > label {{
        font-weight: 500; color: #444; background: #f8f9fa; padding: 10px 16px; 
        border-radius: 8px; border: 1px solid #eee; cursor: pointer; 
        transition: all 0.3s;
        white-space: nowrap; 
    }}
    div[role="radiogroup"] > label:hover {{ background: #e2e6ea; border-color: {COR_SECUNDARIA}; }}
    div[data-testid="stRadio"] > div {{ 
        flex-direction: row; flex-wrap: wrap; 
        gap: 10px; width: 100%; padding-bottom: 10px; 
    }}

    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, .no-print {{ display: none !important; }}
        .a4-paper {{ box-shadow: none; margin: 0; padding: 0; width: 100%; max-width: 100%; }}
        .stApp {{ background-color: white; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. DADOS E INICIALIZAÇÃO DE ESTADO
# ==============================================================================
keys_to_init = ['logged_in', 'user_role', 'admin_permission', 'user_username', 'user_credits', 'user_linked_company', 'edit_mode', 'edit_id', 'acoes_list']
for k in keys_to_init:
    if k not in st.session_state: st.session_state[k] = None

if st.session_state.acoes_list is None: st.session_state.acoes_list = []
if st.session_state.user_credits is None: st.session_state.user_credits = 0

# Mock inicial para caso o banco falhe
if 'users_db' not in st.session_state:
    st.session_state.users_db = {"admin": {"password": "admin", "role": "Master", "credits": 999999}}
if 'companies_db' not in st.session_state:
    st.session_state.companies_db = []
if 'local_responses_db' not in st.session_state:
    st.session_state.local_responses_db = []

# LISTA COMPLETA HSE 35 PERGUNTAS COM EXEMPLOS HUMANIZADOS E INVERSÃO DE NOTAS (rev: True/False)
if 'hse_questions' not in st.session_state:
    st.session_state.hse_questions = {
        "Demandas": [
            {"id": 3, "q": "Tenho prazos impossíveis de cumprir?", "rev": True, "help": "Exemplo: Ser cobrado por entregas urgentes no fim do expediente sem tempo hábil."},
            {"id": 6, "q": "Sou pressionado a trabalhar longas horas?", "rev": True, "help": "Exemplo: Sentir que só fazer o seu horário normal não é suficiente para a empresa."},
            {"id": 9, "q": "Tenho que trabalhar muito intensamente?", "rev": True, "help": "Exemplo: Não ter tempo nem para respirar ou tomar um café direito devido ao volume de trabalho."},
            {"id": 12, "q": "Tenho que negligenciar algumas tarefas?", "rev": True, "help": "Exemplo: Ter que fazer as coisas 'de qualquer jeito' só para dar tempo de entregar tudo."},
            {"id": 16, "q": "Não consigo fazer pausas suficientes?", "rev": True, "help": "Exemplo: Precisar pular o horário de almoço ou comer correndo na mesa de trabalho."},
            {"id": 18, "q": "Sou pressionado por diferentes grupos?", "rev": True, "help": "Exemplo: Receber ordens conflitantes ou urgentes de gestores ou setores diferentes."},
            {"id": 20, "q": "Tenho que trabalhar muito rápido?", "rev": True, "help": "Exemplo: O ritmo exigido é frenético e desgastante o tempo todo."},
            {"id": 22, "q": "Tenho prazos irrealistas?", "rev": True, "help": "Exemplo: Metas que, na prática do dia a dia, ninguém da equipe consegue bater."}
        ],
        "Controle": [
            {"id": 2, "q": "Posso decidir quando fazer uma pausa?", "rev": False, "help": "Exemplo: Ter liberdade para levantar, esticar as pernas ou tomar água sem precisar pedir permissão."},
            {"id": 10, "q": "Tenho liberdade para decidir como faço meu trabalho?", "rev": False, "help": "Exemplo: Poder escolher o melhor método ou ferramenta para entregar o seu resultado."},
            {"id": 15, "q": "Tenho poder de decisão sobre meu ritmo?", "rev": False, "help": "Exemplo: Poder acelerar ou diminuir o ritmo de trabalho dependendo do seu nível de energia no dia."},
            {"id": 19, "q": "Eu decido quando vou realizar cada tarefa?", "rev": False, "help": "Exemplo: Ter autonomia para organizar sua própria agenda diária."},
            {"id": 25, "q": "Tenho voz sobre como meu trabalho é realizado?", "rev": False, "help": "Exemplo: Suas ideias de melhorias nos processos são ouvidas e aplicadas pela gestão."},
            {"id": 30, "q": "Meu tempo de trabalho pode ser flexível?", "rev": False, "help": "Exemplo: Ter banco de horas, horários flexíveis de entrada/saída ou acordos amigáveis com o gestor."}
        ],
        "Suporte Gestor": [
            {"id": 8, "q": "Recebo feedback sobre o trabalho?", "rev": False, "help": "Exemplo: Seu gestor senta com você para conversar de forma clara sobre o que está bom e o que pode melhorar."},
            {"id": 23, "q": "Posso contar com meu superior num problema?", "rev": False, "help": "Exemplo: Saber que o gestor vai te ajudar a resolver uma falha técnica em vez de apenas te culpar."},
            {"id": 29, "q": "Posso falar com meu superior sobre algo que me chateou?", "rev": False, "help": "Exemplo: Ter abertura para conversas sinceras e humanas sem medo de retaliação."},
            {"id": 33, "q": "Sinto apoio do meu gestor(a)?", "rev": False, "help": "Exemplo: Sentir que seu chefe 'joga no seu time' e se importa com seu bem-estar geral."},
            {"id": 35, "q": "Meu gestor me incentiva no trabalho?", "rev": False, "help": "Exemplo: Receber elogios, reconhecimento e motivação quando faz um bom trabalho."}
        ],
        "Suporte Pares": [
            {"id": 7, "q": "Recebo a ajuda e o apoio que preciso dos meus colegas?", "rev": False, "help": "Exemplo: A equipe é unida e um cobre o outro quando necessário."},
            {"id": 24, "q": "Recebo o respeito que mereço dos meus colegas?", "rev": False, "help": "Exemplo: O tratamento no dia a dia é cordial, respeitoso e livre de preconceitos."},
            {"id": 27, "q": "Meus colegas estão dispostos a me ouvir sobre problemas?", "rev": False, "help": "Exemplo: Ter com quem desabafar sobre um dia difícil ou um cliente complicado."},
            {"id": 31, "q": "Meus colegas me ajudam em momentos difíceis?", "rev": False, "help": "Exemplo: A equipe divide o peso quando o volume de trabalho está muito alto para uma pessoa só."}
        ],
        "Relacionamentos": [
            {"id": 5, "q": "Estou sujeito a assédio pessoal?", "rev": True, "help": "Exemplo: Sofrer comentários desrespeitosos, constrangedores ou pressões indevidas no ambiente de trabalho."},
            {"id": 14, "q": "Há atritos ou conflitos entre colegas?", "rev": True, "help": "Exemplo: O clima geral é de fofoca, panelinhas ou brigas constantes no setor."},
            {"id": 21, "q": "Estou sujeito a bullying?", "rev": True, "help": "Exemplo: Ser excluído propositalmente de conversas, grupos ou ser alvo de piadas repetitivas e maldosas."},
            {"id": 34, "q": "Os relacionamentos no trabalho são tensos?", "rev": True, "help": "Exemplo: Aquele clima pesado onde todos parecem pisar em ovos para falar com o outro."}
        ],
        "Papel": [
            {"id": 1, "q": "Sei claramente o que é esperado de mim?", "rev": False, "help": "Exemplo: Suas metas, entregas e funções diárias estão muito bem definidas."},
            {"id": 4, "q": "Sei como fazer para executar meu trabalho?", "rev": False, "help": "Exemplo: Você recebeu o treinamento necessário e tem as ferramentas certas para trabalhar bem."},
            {"id": 11, "q": "Sei quais são os objetivos do meu departamento?", "rev": False, "help": "Exemplo: Você entende para onde sua equipe está caminhando e o que precisa ser entregue no fim do mês."},
            {"id": 13, "q": "Sei o quanto de responsabilidade tenho?", "rev": False, "help": "Exemplo: Os limites de até onde você pode agir, aprovar e decidir são claros."},
            {"id": 17, "q": "Entendo meu encaixe na empresa?", "rev": False, "help": "Exemplo: Você consegue ver a importância do seu trabalho diário para o sucesso geral do negócio."}
        ],
        "Mudança": [
            {"id": 26, "q": "Tenho oportunidade de questionar sobre mudanças?", "rev": False, "help": "Exemplo: Haver espaço para tirar dúvidas reais quando uma nova regra ou sistema é criado."},
            {"id": 28, "q": "Sou consultado(a) sobre mudanças no trabalho?", "rev": False, "help": "Exemplo: A diretoria ou chefia pede a opinião de quem executa antes de mudar um processo."},
            {"id": 32, "q": "Quando mudanças são feitas, fica claro como funcionarão?", "rev": False, "help": "Exemplo: A comunicação é transparente, bem explicada e não gera confusão na equipe."}
        ]
    }

# ==============================================================================
# 4. FUNÇÕES DE CÁLCULO E BANCO DE DADOS
# ==============================================================================
def get_logo_html(width=180):
    if st.session_state.platform_config['logo_b64']:
        return f'<img src="data:image/png;base64,{st.session_state.platform_config["logo_b64"]}" width="{width}">'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120" width="{width}"><style>.t1 {{ font-family: sans-serif; font-weight: 800; font-size: 50px; fill: {COR_PRIMARIA}; }} .t2 {{ font-family: sans-serif; font-weight: 300; font-size: 50px; fill: {COR_SECUNDARIA}; }} .sub {{ font-family: sans-serif; font-weight: 600; font-size: 11px; fill: {COR_PRIMARIA}; letter-spacing: 3px; text-transform: uppercase; }}</style><g transform="translate(10, 20)"><rect x="0" y="10" width="35" height="35" rx="8" ry="8" fill="none" stroke="{COR_SECUNDARIA}" stroke-width="8" /><rect x="20" y="10" width="35" height="35" rx="8" ry="8" fill="none" stroke="{COR_PRIMARIA}" stroke-width="8" /></g><text x="80" y="55" class="t1">ELO</text><text x="190" y="55" class="t2">NR-01</text><text x="82" y="80" class="sub">SISTEMA INTELIGENTE</text></svg>"""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}">'

def image_to_base64(file):
    try: return base64.b64encode(file.getvalue()).decode() if file else None
    except: return None

def logout(): 
    st.session_state.logged_in = False
    st.rerun()

def calculate_actual_scores(all_responses, hse_questions):
    """Calcula os scores reais baseados nas respostas dos colaboradores."""
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
                        # Se a pergunta é negativa (rev=True), Nunca = Bom(5). Se positiva, Sempre = Bom(5).
                        if is_rev: val = {"Nunca": 5, "Raramente": 4, "Às vezes": 3, "Frequentemente": 2, "Sempre": 1}.get(user_ans)
                        else: val = {"Nunca": 1, "Raramente": 2, "Às vezes": 3, "Frequentemente": 4, "Sempre": 5}.get(user_ans)
                    elif user_ans in ["Discordo", "Neutro", "Concordo"]:
                        if is_rev: val = {"Discordo": 5, "Neutro": 3, "Concordo": 1}.get(user_ans)
                        else: val = {"Discordo": 1, "Neutro": 3, "Concordo": 5}.get(user_ans)

                    if val is not None:
                        total_score += val
                        count_valid += 1
                        
        # Armazena o score calculado daquele individuo especifico na linha
        resp_row['score_calculado'] = round(total_score / count_valid, 2) if count_valid > 0 else 0
    return all_responses

def process_company_analytics(comp, comp_resps, hse_questions):
    """Gera as médias dimensionais e o Raio-X com base em dados concretos."""
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
                        if is_rev: val = {"Nunca": 5, "Raramente": 4, "Às vezes": 3, "Frequentemente": 2, "Sempre": 1}.get(user_ans)
                        else: val = {"Nunca": 1, "Raramente": 2, "Às vezes": 3, "Frequentemente": 4, "Sempre": 5}.get(user_ans)
                    elif user_ans in ["Discordo", "Neutro", "Concordo"]:
                        if is_rev: val = {"Discordo": 5, "Neutro": 3, "Concordo": 1}.get(user_ans)
                        else: val = {"Discordo": 1, "Neutro": 3, "Concordo": 5}.get(user_ans)

                    if val is not None:
                        dimensoes_totais[cat].append(val)
                        
                        # Calculo de Risco para o Raio-X: Se a pessoa pontuou 1 ou 2, é risco.
                        if q_text not in riscos_por_pergunta:
                            riscos_por_pergunta[q_text] = 0
                            total_por_pergunta[q_text] = 0
                            
                        total_por_pergunta[q_text] += 1
                        if val <= 2: 
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
    # Media global da empresa
    vals_validos = [v for v in dim_averages.values() if v > 0]
    comp['score'] = round(sum(vals_validos) / len(vals_validos), 1) if vals_validos else 0
    comp['detalhe_perguntas'] = detalhe_percent
    
    return comp

def load_data_from_db():
    all_answers = []
    companies = []
    
    if DB_CONNECTED:
        try:
            companies = supabase.table('companies').select("*").execute().data
            all_answers = supabase.table('responses').select("*").execute().data
            
            # Atualiza usuários também
            users_raw = supabase.table('admin_users').select("*").execute().data
            if users_raw:
                st.session_state.users_db = {u['username']: u for u in users_raw}
        except Exception as e:
            pass # Falha silenciosa cai pro local
            
    if not companies:
        companies = st.session_state.companies_db
        all_answers = st.session_state.local_responses_db
        
    # Processa DADOS REAIS
    all_answers = calculate_actual_scores(all_answers, st.session_state.hse_questions)
    
    for c in companies:
        if 'org_structure' not in c or not c['org_structure']: 
            c['org_structure'] = {"Geral": ["Geral"]}
            
        comp_resps = [r for r in all_answers if r['company_id'] == c['id']]
        c = process_company_analytics(c, comp_resps, st.session_state.hse_questions)

    return companies, all_answers

def delete_company(comp_id):
    if DB_CONNECTED:
        try:
            supabase.table('companies').delete().eq('id', comp_id).execute()
            supabase.table('admin_users').delete().eq('linked_company_id', comp_id).execute()
        except Exception as e: st.warning(f"Erro ao excluir do DB: {e}")
    
    # Proteção: Remove baseado no ID, não no índice
    st.session_state.companies_db = [c for c in st.session_state.companies_db if c['id'] != comp_id]
    st.success("✅ Empresa excluída com sucesso!")
    time.sleep(1)
    st.rerun()

def delete_user(username):
    if DB_CONNECTED:
        try:
            supabase.table('admin_users').delete().eq('username', username).execute()
        except: pass
    
    if username in st.session_state.users_db:
        del st.session_state.users_db[username]
    
    st.success("✅ Usuário excluído!")
    time.sleep(1)
    st.rerun()

def kpi_card(title, value, icon, color_class):
    st.markdown(f"""<div class="kpi-card"><div class="kpi-top"><div class="kpi-icon-box {color_class}">{icon}</div><div class="kpi-value">{value}</div></div><div class="kpi-title">{title}</div></div>""", unsafe_allow_html=True)

def generate_mock_history():
    return [
        {"periodo": "Jan/2025", "score": 2.8, "vidas": 120, "adesao": 85, "dimensoes": {"Demandas": 2.1, "Controle": 3.8, "Suporte Gestor": 2.5, "Suporte Pares": 4.0, "Relacionamentos": 2.9, "Papel": 4.5, "Mudança": 3.0}},
        {"periodo": "Jul/2024", "score": 2.4, "vidas": 115, "adesao": 70, "dimensoes": {"Demandas": 1.8, "Controle": 3.0, "Suporte Gestor": 2.2, "Suporte Pares": 3.8, "Relacionamentos": 2.5, "Papel": 4.0, "Mudança": 2.8}}
    ]

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
    # --- BANCO COMPLETO DE AÇÕES (TOTALMENTE EXPANDIDO) ---
    if dimensoes.get("Demandas", 5) < 3.8:
        sugestoes.append({"acao": "Mapeamento de Carga", "estrat": "Realizar censo de tarefas por função para identificar gargalos.", "area": "Demandas", "resp": "A Definir", "prazo": "30 dias"})
        sugestoes.append({"acao": "Matriz de Priorização", "estrat": "Treinar equipes na Matriz Eisenhower (Urgente x Importante).", "area": "Demandas", "resp": "A Definir", "prazo": "15 dias"})
        sugestoes.append({"acao": "Política Desconexão", "estrat": "Regras sobre mensagens off-horário e finais de semana.", "area": "Demandas", "resp": "A Definir", "prazo": "30 dias"})
        sugestoes.append({"acao": "Revisão de Prazos", "estrat": "Renegociar SLAs internos baseados na capacidade real da equipe.", "area": "Demandas", "resp": "A Definir", "prazo": "45 dias"})
        sugestoes.append({"acao": "Pausas Cognitivas", "estrat": "Instituir pausas de 10 min a cada 2h para descompressão.", "area": "Demandas", "resp": "A Definir", "prazo": "Imediato"})
        sugestoes.append({"acao": "Contratação Sazonal", "estrat": "Alocar recursos extras em períodos conhecidos de pico de produção.", "area": "Demandas", "resp": "A Definir", "prazo": "90 dias"})
        sugestoes.append({"acao": "Automação de Tarefas", "estrat": "Mapear e automatizar geração de relatórios e processos repetitivos.", "area": "Demandas", "resp": "A Definir", "prazo": "60 dias"})
        sugestoes.append({"acao": "Gestão de Interrupções", "estrat": "Definir horários de 'foco total' (ex: manhãs sem reuniões).", "area": "Demandas", "resp": "A Definir", "prazo": "15 dias"})
        sugestoes.append({"acao": "Treinamento Gestão Tempo", "estrat": "Capacitação em produtividade pessoal, foco e organização da agenda.", "area": "Demandas", "resp": "A Definir", "prazo": "60 dias"})
    
    if dimensoes.get("Controle", 5) < 3.8:
        sugestoes.append({"acao": "Job Crafting", "estrat": "Permitir personalização do método de trabalho para alcançar os mesmos resultados.", "area": "Controle", "resp": "A Definir", "prazo": "Contínuo"})
        sugestoes.append({"acao": "Banco de Horas Flexível", "estrat": "Implementar flexibilidade de entrada e saída com regras claras de compensação.", "area": "Controle", "resp": "A Definir", "prazo": "60 dias"})
        sugestoes.append({"acao": "Autonomia na Agenda", "estrat": "Incentivar a autogestão da ordem das tarefas não-críticas diárias.", "area": "Controle", "resp": "A Definir", "prazo": "Imediato"})
        sugestoes.append({"acao": "Delegação Efetiva", "estrat": "Treinar gestores para empoderar níveis menores em decisões operacionais rotineiras.", "area": "Controle", "resp": "A Definir", "prazo": "45 dias"})
        sugestoes.append({"acao": "Comitês Participativos", "estrat": "Envolver a equipe de base nas reuniões de melhoria de processos.", "area": "Controle", "resp": "A Definir", "prazo": "30 dias"})
        sugestoes.append({"acao": "Flexibilidade de Local", "estrat": "Analisar viabilidade de política de home office estruturado ou modelo híbrido.", "area": "Controle", "resp": "A Definir", "prazo": "90 dias"})
        sugestoes.append({"acao": "Rotação de Tarefas", "estrat": "Implementar job rotation para reduzir monotonia e aumentar o repertório de skills.", "area": "Controle", "resp": "A Definir", "prazo": "60 dias"})
        sugestoes.append({"acao": "Escolha de Ferramentas", "estrat": "Permitir, dentro da governança da TI, a escolha de softwares ou métodos preferidos.", "area": "Controle", "resp": "A Definir", "prazo": "Contínuo"})
        
    if dimensoes.get("Suporte Gestor", 5) < 3.8 or dimensoes.get("Suporte Pares", 5) < 3.8:
        sugestoes.append({"acao": "Liderança Segura", "estrat": "Capacitação de líderes em escuta ativa, inteligência emocional e empatia.", "area": "Suporte", "resp": "A Definir", "prazo": "90 dias"})
        sugestoes.append({"acao": "Mentoria Buddy", "estrat": "Implementar sistema de padrinhos para acolhimento de novos colaboradores.", "area": "Suporte", "resp": "A Definir", "prazo": "30 dias"})
        sugestoes.append({"acao": "Reuniões 1:1", "estrat": "Estruturar feedbacks individuais quinzenais com foco em bem-estar e carreira.", "area": "Suporte", "resp": "A Definir", "prazo": "15 dias"})
        sugestoes.append({"acao": "Grupos de Apoio Técnico", "estrat": "Criar espaços seguros e institucionalizados para troca de experiências e resolução conjunta.", "area": "Suporte", "resp": "A Definir", "prazo": "45 dias"})
        sugestoes.append({"acao": "Feedback Estruturado", "estrat": "Implementar e treinar a cultura de feedback contínuo (modelo SBI) não atrelado à avaliação anual.", "area": "Suporte", "resp": "A Definir", "prazo": "60 dias"})
        sugestoes.append({"acao": "Rituais de Reconhecimento", "estrat": "Criar rotinas simples de celebração de pequenas conquistas e esforços da equipe.", "area": "Suporte", "resp": "A Definir", "prazo": "Imediato"})
        sugestoes.append({"acao": "Plantão de Escuta", "estrat": "Disponibilizar canal direto com RH ou Psicologia Organizacional para suporte emergencial.", "area": "Suporte", "resp": "A Definir", "prazo": "30 dias"})
        sugestoes.append({"acao": "Treinamento de Empatia", "estrat": "Workshop vivencial focado na redução de atritos invisíveis gerados pela comunicação digital.", "area": "Suporte", "resp": "A Definir", "prazo": "90 dias"})
        sugestoes.append({"acao": "Café com a Diretoria", "estrat": "Rotinas de aproximação estruturada e informal da alta gestão com a base da operação.", "area": "Suporte", "resp": "A Definir", "prazo": "Mensal"})
        
    if dimensoes.get("Relacionamentos", 5) < 3.8:
        sugestoes.append({"acao": "Tolerância Zero ao Assédio", "estrat": "Atualizar, divulgar e assinar termo de compromisso com o Código de Conduta e Ética.", "area": "Relacionamentos", "resp": "A Definir", "prazo": "30 dias"})
        sugestoes.append({"acao": "Workshop CNV", "estrat": "Treinamento intensivo de Comunicação Não-Violenta para todos os níveis hierárquicos.", "area": "Relacionamentos", "resp": "A Definir", "prazo": "90 dias"})
        sugestoes.append({"acao": "Ouvidoria Externa", "estrat": "Contratar canal anônimo e seguro, gerido por terceiros, para denúncias de assédio/bullying.", "area": "Relacionamentos", "resp": "A Definir", "prazo": "60 dias"})
        sugestoes.append({"acao": "Mediação de Conflitos", "estrat": "Treinar um grupo multidisciplinar do RH para mediação precoce de atritos entre equipes.", "area": "Relacionamentos", "resp": "A Definir", "prazo": "120 dias"})
        sugestoes.append({"acao": "Eventos de Team Building", "estrat": "Investir em dinâmicas de integração, voluntariado corporativo e quebra-gelo fora do ambiente tradicional.", "area": "Relacionamentos", "resp": "A Definir", "prazo": "Semestral"})
        sugestoes.append({"acao": "Acordos de Convivência", "estrat": "Sessão de facilitação para criação coletiva de um 'manual' de boas práticas de convivência na área.", "area": "Relacionamentos", "resp": "A Definir", "prazo": "30 dias"})
        sugestoes.append({"acao": "Comitê de Diversidade", "estrat": "Estabelecer grupo focado em promover a inclusão, letramento sobre vieses inconscientes e respeito.", "area": "Relacionamentos", "resp": "A Definir", "prazo": "90 dias"})
        sugestoes.append({"acao": "Feedback 360 Anônimo", "estrat": "Realizar avaliação estruturada entre pares para identificar atritos comportamentais ocultos.", "area": "Relacionamentos", "resp": "A Definir", "prazo": "Anual"})
        
    if dimensoes.get("Papel", 5) < 3.8:
        sugestoes.append({"acao": "Revisão Job Description", "estrat": "Atualizar e validar descrições de cargo garantindo clareza total das responsabilidades.", "area": "Papel", "resp": "A Definir", "prazo": "60 dias"})
        sugestoes.append({"acao": "Alinhamento Metas (OKRs)", "estrat": "Revisão periódica (trimestral/semestral) de objetivos individuais atrelados ao propósito da área.", "area": "Papel", "resp": "A Definir", "prazo": "Contínuo"})
        sugestoes.append({"acao": "Onboarding Estruturado", "estrat": "Reforço no treinamento inicial, não só de processos, mas de cultura, história e valor da função.", "area": "Papel", "resp": "A Definir", "prazo": "30 dias"})
        sugestoes.append({"acao": "Implementação Matriz RACI", "estrat": "Definição visual e formal de quem é Responsável, Autoridade, Consultado e Informado em projetos.", "area": "Papel", "resp": "A Definir", "prazo": "45 dias"})
        
    if dimensoes.get("Mudança", 5) < 3.8:
        sugestoes.append({"acao": "Comunicação Transparente", "estrat": "Garantir que a liderança explique o 'porquê' (razão de negócio) antes do 'como' (a tarefa) em mudanças.", "area": "Mudança", "resp": "A Definir", "prazo": "Contínuo"})
        sugestoes.append({"acao": "Consulta Prévia", "estrat": "Realizar pequenos focus groups ou enquetes antes de implementar mudanças de alto impacto operacional.", "area": "Mudança", "resp": "A Definir", "prazo": "A cada projeto"})
        sugestoes.append({"acao": "Embaixadores da Mudança", "estrat": "Eleger colaboradores chave na base operacional para apoiar e traduzir a transição para os pares.", "area": "Mudança", "resp": "A Definir", "prazo": "A cada projeto"})
        sugestoes.append({"acao": "Cronograma Visível", "estrat": "Disponibilizar timeline clara e acessível das etapas de transição para reduzir ansiedade gerada pela incerteza.", "area": "Mudança", "resp": "A Definir", "prazo": "Imediato"})
        sugestoes.append({"acao": "Central de FAQ e Suporte", "estrat": "Criar documento centralizado de dúvidas comuns atualizado constantemente durante grandes transições.", "area": "Mudança", "resp": "A Definir", "prazo": "Imediato"})
    
    if not sugestoes:
        sugestoes.append({"acao": "Manutenção do Clima", "estrat": "Realizar pesquisas de pulso curtas e trimestrais para monitoramento.", "area": "Geral", "resp": "RH", "prazo": "Contínuo"})
        sugestoes.append({"acao": "Programa de Saúde Mental", "estrat": "Palestras mensais, parcerias com apps de terapia ou plano de saúde mental dedicado.", "area": "Geral", "resp": "RH", "prazo": "90 dias"})
        sugestoes.append({"acao": "Pausas Ativas (Laboral)", "estrat": "Implementar rotina de ginástica laboral guiada, online ou presencial.", "area": "Geral", "resp": "SESMT", "prazo": "30 dias"})
        
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
                        
                        # GARANTIA ABSOLUTA DE ACESSO MASTER PARA O USUARIO "admin"
                        if user == 'admin':
                            user_role_type = 'Master'
                            user_credits = 999999
                        
                        st.session_state.admin_permission = user_role_type 
                        st.session_state.user_username = user
                        st.session_state.user_credits = user_credits
                        st.session_state.user_linked_company = linked_comp
                        st.rerun()
                else: st.error("Dados incorretos.")
        st.caption("Colaboradores: Utilizem o link fornecido pelo RH.")

def admin_dashboard():
    # Carrega dados frescos a cada recarregamento
    companies_data, responses_data = load_data_from_db()
    
    perm = st.session_state.admin_permission
    curr_user = st.session_state.user_username
    
    # Filtro de acesso
    if perm == "Gestor":
        visible_companies = [c for c in companies_data if c.get('owner') == curr_user]
    elif perm == "Analista":
        linked_id = st.session_state.user_linked_company
        visible_companies = [c for c in companies_data if c['id'] == linked_id]
    else: # Master
        visible_companies = companies_data

    # Calcula Saldo de Créditos
    total_used_by_user = 0
    if perm == "Gestor":
        total_used_by_user = sum(c.get('respondidas', 0) for c in visible_companies)
    elif perm == "Analista":
        if visible_companies: total_used_by_user = visible_companies[0].get('respondidas', 0)
    
    credits_total = st.session_state.user_credits
    credits_left = credits_total - total_used_by_user

    # Menu Dinâmico
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
        
        if perm != "Master":
            st.info(f"💳 Saldo: {credits_left} avaliações")

        selected = option_menu(menu_title=None, options=menu_options, icons=menu_icons, default_index=0, styles={"nav-link-selected": {"background-color": COR_PRIMARIA}})
        st.markdown("---"); 
        if st.button("Sair", use_container_width=True): logout()

    # --- PÁGINAS ---
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
        total_vidas_view = sum(c.get('func', 0) for c in companies_filtered)
        
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
            st.markdown("##### Radar HSE (Média Real)")
            if companies_filtered and total_resp_view > 0:
                categories = list(st.session_state.hse_questions.keys())
                
                # CÁLCULO REAL DA MÉDIA DAS EMPRESAS FILTRADAS
                avg_dims = {cat: 0 for cat in categories}
                count_comps_with_data = 0
                for c in companies_filtered:
                    if c.get('respondidas', 0) > 0:
                        count_comps_with_data += 1
                        for cat in categories:
                            avg_dims[cat] += c['dimensoes'].get(cat, 0)
                
                if count_comps_with_data > 0:
                    valores_radar = [round(avg_dims[cat]/count_comps_with_data, 1) for cat in categories]
                else:
                    valores_radar = [0]*len(categories)

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(r=valores_radar, theta=categories, fill='toself', name='Média', line_color=COR_SECUNDARIA))
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), height=300, margin=dict(t=20, b=20))
                st.plotly_chart(fig_radar, use_container_width=True)
            else: st.info("Sem dados suficientes para gerar radar.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with c2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("##### Resultados por Setor (Calculado)")
            if responses_filtered:
                df_resp = pd.DataFrame(responses_filtered)
                if 'setor' in df_resp.columns and 'score_calculado' in df_resp.columns:
                    # Usa o Score REAL calculado no banco
                    df_setor = df_resp.groupby('setor')['score_calculado'].mean().reset_index()
                    fig_bar = px.bar(df_setor, x='setor', y='score_calculado', title="Score Médio Real", color='score_calculado', color_continuous_scale='RdYlGn', range_y=[0, 5])
                    st.plotly_chart(fig_bar, use_container_width=True)
                else: st.info("Sem dados de setor estruturados.")
            else: st.info("Aguardando respostas para gerar o gráfico.")
            st.markdown("</div>", unsafe_allow_html=True)
        
        c3, c4 = st.columns([1.5, 1])
        with c3:
             st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
             st.markdown("##### Distribuição de Engajamento")
             if companies_filtered:
                 status_dist = {"Concluído": 0, "Em Andamento": 0}
                 for c in companies_filtered:
                     if c.get('respondidas',0) >= c.get('func',1): status_dist["Concluído"] += 1
                     else: status_dist["Em Andamento"] += 1
                 
                 # Uso correto do px.pie para grafico de rosca
                 fig_pie = px.pie(names=list(status_dist.keys()), values=list(status_dist.values()), hole=0.6, color_discrete_sequence=[COR_SECUNDARIA, COR_RISCO_MEDIO])
                 fig_pie.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
                 st.plotly_chart(fig_pie, use_container_width=True)
             else:
                 st.info("Cadastre empresas para visualizar.")
             st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Empresas":
        st.title("Gestão de Empresas")
        
        if st.session_state.edit_mode:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("✏️ Editar Empresa")
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
                    new_risco = c4.selectbox("Grau de Risco", risco_opts, index=idx_risco)
                    new_func = c5.number_input("Vidas (Funcionários)", min_value=1, value=emp_edit.get('func',100))
                    new_limit = c6.number_input("Cota da Empresa", min_value=1, value=emp_edit.get('limit_evals', 100))
                    
                    seg_opts = ["GHE", "Setor", "GES"]
                    idx_seg = seg_opts.index(emp_edit.get('segmentacao','GHE')) if emp_edit.get('segmentacao','GHE') in seg_opts else 0
                    new_seg = c6.selectbox("Segmentação", seg_opts, index=idx_seg)
                    
                    c7, c8, c9 = st.columns(3)
                    new_resp = c7.text_input("Responsável da Empresa", value=emp_edit.get('resp',''))
                    new_email = c8.text_input("E-mail do Responsável", value=emp_edit.get('email',''))
                    new_tel = c9.text_input("Telefone do Responsável", value=emp_edit.get('telefone',''))
                    
                    new_end = st.text_input("Endereço Completo", value=emp_edit.get('endereco',''))
                    
                    val_atual = datetime.date.today() + datetime.timedelta(days=365)
                    if emp_edit.get('valid_until'):
                        try: val_atual = datetime.date.fromisoformat(emp_edit['valid_until'])
                        except: pass
                    new_valid = st.date_input("Link Válido Até", value=val_atual)
                    
                    if st.form_submit_button("💾 Salvar Alterações"):
                        update_dict = {
                            'razao': new_razao, 'cnpj': new_cnpj, 'cnae': new_cnae, 
                            'risco': new_risco, 'func': new_func, 'segmentacao': new_seg, 
                            'resp': new_resp, 'email': new_email, 'telefone': new_tel, 
                            'endereco': new_end, 'limit_evals': new_limit, 'valid_until': new_valid.isoformat()
                        }
                        
                        # Tenta atualizar no banco primeiro
                        if DB_CONNECTED:
                            try:
                                supabase.table('companies').update(update_dict).eq('id', target_id).execute()
                            except Exception as e: st.warning(f"Erro DB: {e}")
                        
                        # Atualiza localmente para refletir imediatamente
                        emp_edit.update(update_dict)
                        
                        st.session_state.edit_mode = False
                        st.session_state.edit_id = None
                        st.success("✅ Empresa atualizada com sucesso!")
                        time.sleep(1)
                        st.rerun()
                        
                if st.button("Cancelar Edição"): 
                    st.session_state.edit_mode = False
                    st.rerun()
            else:
                st.error("Erro ao carregar os dados para edição.")
        
        else:
            tab1, tab2 = st.tabs(["Lista de Empresas", "➕ Novo Cadastro"])
            with tab1:
                if not visible_companies:
                    st.info("Nenhuma empresa cadastrada no seu perfil ainda.")
                
                for emp in visible_companies:
                    with st.expander(f"🏢 {emp['razao']}"):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.write(f"**CNPJ:** {emp.get('cnpj','')}")
                        limit = emp.get('limit_evals', '∞')
                        c2.write(f"**Cota (Uso):** {emp.get('respondidas',0)}/{limit}")
                        
                        validity = emp.get('valid_until', '-')
                        try: validity = datetime.date.fromisoformat(validity).strftime('%d/%m/%Y')
                        except: pass
                        c3.write(f"**Vence em:** {validity}")
                        
                        c4_1, c4_2 = c4.columns(2)
                        if c4_1.button("✏️ Editar", key=f"ed_{emp['id']}"): 
                             st.session_state.edit_mode = True
                             st.session_state.edit_id = emp['id']
                             st.rerun()
                        
                        if perm == "Master":
                            # EXCLUSÃO POR ID
                            if c4_2.button("🗑️ Excluir", key=f"del_{emp['id']}"): 
                                delete_company(emp['id'])
            
            with tab2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                with st.form("add_comp"):
                    if credits_left <= 0 and perm != "Master":
                        st.error("🚫 Você não possui créditos suficientes para cadastrar novas empresas.")
                        st.form_submit_button("Bloqueado por falta de saldo", disabled=True)
                    else:
                        st.write("### Dados Básicos da Empresa")
                        c1, c2, c3 = st.columns(3)
                        razao = c1.text_input("Razão Social")
                        cnpj = c2.text_input("CNPJ")
                        cnae = c3.text_input("CNAE")
                        
                        c4, c5, c6 = st.columns(3)
                        risco = c4.selectbox("Grau de Risco", [1,2,3,4])
                        func = c5.number_input("Número de Vidas (Funcionários)", min_value=1)
                        limit_evals = c6.number_input("Cota de Avaliações Contratada", min_value=1, max_value=credits_left if perm!="Master" else 99999, value=min(100, credits_left if perm!="Master" else 100))
                        
                        st.write("### Informações de Contato e Link")
                        c7, c8, c9 = st.columns(3)
                        segmentacao = c7.selectbox("Tipo de Segmentação", ["GHE", "Setor", "GES"])
                        resp = c8.text_input("Nome do Responsável")
                        email = c9.text_input("E-mail Resp.")
                        
                        c10, c11, c12 = st.columns(3)
                        tel = c10.text_input("Telefone Resp.")
                        valid_date = c11.date_input("Link Válido Até", value=datetime.date.today() + datetime.timedelta(days=365))
                        # AVISO DE GERACAO DE LINK
                        c12.info("O ID (Link) será gerado automaticamente de forma segura.")
                        
                        end = st.text_input("Endereço Completo")
                        logo_cliente = st.file_uploader("Logo do Cliente (Opcional)", type=['png', 'jpg'])
                        
                        st.markdown("---")
                        st.write("### Criar Acesso para a Empresa (Perfil Analista)")
                        st.caption("Defina o login para a empresa acessar os relatórios gerados por você.")
                        u_login = st.text_input("Usuário de Acesso da Empresa")
                        u_pass = st.text_input("Senha de Acesso", type="password")

                        if st.form_submit_button("Cadastrar Empresa e Usuário"):
                            if not razao:
                                st.error("⚠️ A Razão Social é obrigatória.")
                            else:
                                # GERA ID SEGURO
                                cod = str(uuid.uuid4())[:8].upper()
                                logo_str = image_to_base64(logo_cliente)
                                
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
                                
                                # Salva no Banco se conectado
                                error_msg = None
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
                                        error_msg = str(e)
                                
                                # Salva Localmente independente (Garante fluxo)
                                st.session_state.companies_db.append(new_c)
                                if u_login and u_pass:
                                    st.session_state.users_db[u_login] = {
                                        "password": u_pass, "role": "Analista", "credits": limit_evals, 
                                        "valid_until": valid_date.isoformat(), "linked_company_id": cod 
                                    }
                                
                                if error_msg:
                                    st.warning(f"Salvo localmente na memória temporária. Erro de sincronização com banco: {error_msg}")
                                else:
                                    st.success(f"✅ Empresa cadastrada com sucesso! ID Gerado: {cod}")
                                
                                time.sleep(2)
                                st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Setores & Cargos":
        st.title("Gestão de Setores e Cargos")
        if not visible_companies: st.warning("Cadastre uma empresa primeiro."); return
        
        empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in visible_companies])
        
        # Encontra a empresa para atualização rápida
        empresa = next((c for c in visible_companies if c['razao'] == empresa_nome), None)
        
        if empresa is not None:
            if 'org_structure' not in empresa or not empresa['org_structure']: 
                empresa['org_structure'] = {"Geral": ["Geral"]}
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.subheader("1. Criar/Remover Setores")
                new_setor = st.text_input("Nome do Novo Setor")
                if st.button("➕ Adicionar Setor"):
                    if new_setor and new_setor not in empresa['org_structure']:
                        empresa['org_structure'][new_setor] = []
                        if DB_CONNECTED:
                            try: supabase.table('companies').update({"org_structure": empresa['org_structure']}).eq('id', empresa['id']).execute()
                            except: pass
                        st.success(f"Setor '{new_setor}' adicionado!")
                        time.sleep(1)
                        st.rerun()
                
                st.markdown("---")
                setores_existentes = list(empresa['org_structure'].keys())
                setor_remover = st.selectbox("Selecione para remover", setores_existentes)
                if st.button("🗑️ Remover Setor Selecionado"):
                    del empresa['org_structure'][setor_remover]
                    if DB_CONNECTED:
                         try: supabase.table('companies').update({"org_structure": empresa['org_structure']}).eq('id', empresa['id']).execute()
                         except: pass
                    st.success("Removido!")
                    time.sleep(1)
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
                    if st.button("💾 Salvar Lista de Cargos"):
                        lista_nova = edited_cargos["Cargo"].dropna().tolist()
                        empresa['org_structure'][setor_sel] = lista_nova
                        if DB_CONNECTED:
                             try: supabase.table('companies').update({"org_structure": empresa['org_structure']}).eq('id', empresa['id']).execute()
                             except: pass
                        st.success("Cargos atualizados!")
                st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Gerar Link":
        st.title("Gerar Link e Teste")
        if not visible_companies: st.warning("Cadastre uma empresa primeiro."); return
        with st.container():
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in visible_companies])
            empresa = next(c for c in visible_companies if c['razao'] == empresa_nome)
            
            # Garante que usamos a URL base correta configurada, eliminando a ultima barra duplicada
            base_url = st.session_state.platform_config.get('base_url', 'https://elonr01-cris.streamlit.app').rstrip('/')
            link_final = f"{base_url}/?cod={empresa['id']}"
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("##### Link de Acesso Exclusivo")
                st.markdown(f"<div class='link-area'>{link_final}</div>", unsafe_allow_html=True)
                
                limit = empresa.get('limit_evals', 999999)
                usadas = empresa.get('respondidas', 0)
                val = empresa.get('valid_until', '-')
                try: val = datetime.date.fromisoformat(val).strftime('%d/%m/%Y')
                except: pass
                st.caption(f"📊 Avaliações Utilizadas: {usadas} / {limit}")
                st.caption(f"📅 Validade do Contrato do Link: {val}")
                
                if st.button("👁️ Testar Visão do Colaborador"):
                    st.session_state.current_company = empresa
                    st.session_state.logged_in = True
                    st.session_state.user_role = 'colaborador'
                    st.rerun()
            with c2:
                st.markdown("##### QR Code")
                qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(link_final)}"
                st.image(qr_api_url, width=150)
                st.markdown(f"[📥 Baixar Imagem do QR Code]({qr_api_url})")
                
            st.markdown("---")
            st.markdown("##### 💬 Sugestão de Mensagem de Convite (WhatsApp / E-mail)")
            texto_convite = f"""Olá, time {empresa['razao']}! 👋\n\nCuidar da nossa operação e dos nossos resultados é importante, mas nada disso faz sentido se não cuidarmos, primeiro, de quem faz tudo acontecer: você.\nEstamos iniciando a nossa Avaliação de Riscos Psicossociais e queremos te convidar para uma conversa sincera. Mas, afinal, por que isso é tão importante?\n\n🧠 **Por que participar?**\nMuitas vezes, o estresse, a carga de trabalho ou a dinâmica do dia a dia podem impactar nosso bem-estar de formas invisíveis. Responder a esta avaliação não é apenas preencher um formulário; é nos dar a ferramenta necessária para:\n\n* Identificar pontos de melhoria no nosso ambiente de trabalho.\n* Criar ações práticas que promovam mais equilíbrio e saúde mental.\n* Construir uma cultura onde todos se sintam ouvidos e respeitados.\n\n🔒 **Sua segurança é nossa prioridade**\nSabemos que falar sobre sentimentos e percepções exige confiança. Por isso, queremos reforçar dois pontos inegociáveis:\n\n* **Anonimato Total:** O sistema foi configurado para que nenhuma resposta seja vinculada ao seu nome ou e-mail.\n* **Sigilo Absoluto:** Os dados são analisados de forma coletiva (por setores ou empresa geral). Ninguém terá acesso às suas respostas individuais.\n\nO seu "sincerômetro" é o que nos ajuda a evoluir. Não existem respostas certas ou erradas, apenas a sua percepção real sobre o seu cotidiano conosco.\n\n🚀 **Como participar?**\nBasta clicar no link abaixo. O preenchimento leva cerca de 7 minutos.\n{link_final}\n\nContamos com a sua voz para construirmos, juntos, um lugar cada vez melhor para se trabalhar.\n\nCom carinho,\nEquipe de Gestão de Pessoas / Saúde Ocupacional"""
            st.text_area("Copie o texto abaixo:", value=texto_convite, height=350)
            st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "Relatórios":
        st.title("Relatórios e Laudos")
        if not visible_companies: st.warning("Cadastre empresas para gerar relatórios."); return
        c_sel, c_blank = st.columns([1, 1])
        with c_sel:
            empresa_sel = st.selectbox("Selecione o Cliente", [e['razao'] for e in visible_companies])
        
        # Define a variavel global de empresa para uso nos botoes
        empresa = next(e for e in visible_companies if e['razao'] == empresa_sel)
        
        with st.sidebar:
            st.markdown("---"); st.markdown("#### Configurações de Assinatura")
            sig_empresa_nome = st.text_input("Nome Resp. Empresa", value=empresa.get('resp',''))
            sig_empresa_cargo = st.text_input("Cargo Resp. Empresa", value="Diretor(a)")
            sig_tecnico_nome = st.text_input("Nome Resp. Técnico", value="Cristiane C. Lima")
            sig_tecnico_cargo = st.text_input("Cargo Resp. Técnico", value="Consultora Pessin Gestão")

        dimensoes_atuais = empresa.get('dimensoes', {})
        analise_auto = gerar_analise_robusta(dimensoes_atuais)
        sugestoes_auto = gerar_banco_sugestoes(dimensoes_atuais)
        
        # --- PREPARAÇÃO SEGURA DA TABELA DE AÇÕES ---
        # Garante que html_act sempre existira para o botao nao falhar
        if st.session_state.acoes_list is None: st.session_state.acoes_list = []
        if not st.session_state.acoes_list and sugestoes_auto:
            # Puxa TODAS as recomendacoes do banco de acoes inteligente para iniciar
            for s in sugestoes_auto: 
                st.session_state.acoes_list.append({"acao": s['acao'], "estrat": s['estrat'], "area": s['area'], "resp": "A Definir", "prazo": "30 dias"})
        
        html_act = ""
        if st.session_state.acoes_list:
            for item in st.session_state.acoes_list:
                html_act += f"<tr><td>{item.get('acao','')}</td><td>{item.get('estrat','')}</td><td>{item.get('area','')}</td><td>{item.get('resp','')}</td><td>{item.get('prazo','')}</td></tr>"
        else:
            html_act = "<tr><td colspan='5'>Nenhuma ação selecionada ou definida.</td></tr>"

        with st.expander("📝 Editar Conteúdo Técnico do Relatório", expanded=True):
            st.markdown("##### 1. Conclusão Técnica Diagnóstica")
            analise_texto = st.text_area("Edite o texto que irá na página final do relatório:", value=analise_auto, height=150)
            
            st.markdown("---")
            st.markdown("##### 2. Seleção Rápida do Banco de Ações Inteligentes")
            opcoes_formatadas = [f"[{s['area']}] {s['acao']}: {s['estrat']}" for s in sugestoes_auto]
            selecionadas = st.multiselect("Selecione sugestões adicionais adequadas ao cenário da empresa:", options=opcoes_formatadas)
            if st.button("⬇️ Adicionar à Tabela de Ações"):
                novas = []
                for item_str in selecionadas:
                    for s in sugestoes_auto:
                        if f"[{s['area']}] {s['acao']}: {s['estrat']}" == item_str:
                            novas.append({"acao": s['acao'], "estrat": s['estrat'], "area": s['area'], "resp": "A Definir", "prazo": "30 dias"})
                st.session_state.acoes_list.extend(novas)
                st.success("Ações adicionadas com sucesso!")
                st.rerun()
                
            st.markdown("##### 3. Tabela Final do Plano de Ação Estratégico")
            st.info("Você pode adicionar, excluir ou modificar livremente as células abaixo.")
            edited_df = st.data_editor(pd.DataFrame(st.session_state.acoes_list), num_rows="dynamic", use_container_width=True, column_config={"acao": "Ação Proposta", "estrat": st.column_config.TextColumn("Estratégia Detalhada", width="large"), "area": "Área Foco", "resp": "Responsável", "prazo": "Prazo"})
            if not edited_df.empty: st.session_state.acoes_list = edited_df.to_dict('records')

        # --- GERAÇÃO DO HTML MASSIVO ---
        if st.button("📥 Baixar Arquivo de Relatório Analítico (HTML)", type="primary"):
            st.markdown("---")
            logo_html = get_logo_html(150)
            logo_cliente_html = ""
            if empresa.get('logo_b64'):
                logo_cliente_html = f"<img src='data:image/png;base64,{empresa.get('logo_b64')}' width='100' style='float:right;'>"
            
            # --- CONSTRUÇÃO DO CONTEÚDO VISUAL INTERNO ---
            html_dimensoes = ""
            if empresa.get('dimensoes'):
                for dim, nota in empresa.get('dimensoes', {}).items():
                    cor = COR_RISCO_ALTO if nota < 3 else (COR_RISCO_MEDIO if nota < 4 else COR_RISCO_BAIXO)
                    txt = "CRÍTICO" if nota < 3 else ("ATENÇÃO" if nota < 4 else "SEGURO")
                    html_dimensoes += f'<div style="flex:1; min-width:80px; background:#f8f9fa; border:1px solid #eee; padding:5px; border-radius:4px; margin:2px; text-align:center; font-family:sans-serif;"><div style="font-size:9px; color:#666; text-transform:uppercase;">{dim}</div><div style="font-size:14px; font-weight:bold; color:{cor};">{nota}</div><div style="font-size:7px; color:#888;">{txt}</div></div>'

            html_x = ""
            detalhes = empresa.get('detalhe_perguntas', {})
            # Garante iteração pelas 35 perguntas sem quebrar
            for cat, pergs in st.session_state.hse_questions.items():
                 html_x += f'<div style="font-weight:bold; color:{COR_PRIMARIA}; font-size:10px; margin-top:10px; border-bottom:1px solid #eee; font-family:sans-serif;">{cat}</div>'
                 for q in pergs:
                     val = detalhes.get(q['q'], 0) # Retorna 0 se pergunta nao respondida
                     c_bar = COR_RISCO_ALTO if val > 50 else (COR_RISCO_MEDIO if val > 30 else COR_RISCO_BAIXO)
                     if val == 0: c_bar = "#ddd"
                     html_x += f'<div style="margin-bottom:4px; font-family:sans-serif;"><div style="display:flex; justify-content:space-between; font-size:9px;"><span>{q["q"]}</span><span>{val}% Risco</span></div><div style="width:100%; background:#f0f0f0; height:6px; border-radius:3px;"><div style="width:{val}%; background:{c_bar}; height:100%; border-radius:3px;"></div></div></div>'

            # Recalcula string HTML Ações baseada nas ultimas edicoes da tabela
            html_act_final = "".join([f"<tr><td>{i.get('acao','')}</td><td>{i.get('estrat','')}</td><td>{i.get('area','')}</td><td>{i.get('resp','')}</td><td>{i.get('prazo','')}</td></tr>" for i in st.session_state.acoes_list])
            if not st.session_state.acoes_list: html_act_final = "<tr><td colspan='5'>Nenhuma ação selecionada.</td></tr>"

            html_gauge_css = f"""
            <div style="text-align:center; padding:10px; font-family:sans-serif;">
                <div style="font-size:24px; font-weight:bold; color:{COR_PRIMARIA};">{empresa.get('score', 0)} <span style="font-size:12px; color:#888;">/ 5.0</span></div>
                <div style="width:100%; background:#eee; height:12px; border-radius:6px; margin-top:5px;">
                    <div style="width:{(empresa.get('score',0)/5)*100}%; background:{COR_SECUNDARIA}; height:12px; border-radius:6px;"></div>
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

            lgpd_note = "<div style='margin-top:30px; border-top:1px solid #eee; padding-top:5px; font-size:8px; color:#888; text-align:center; font-family:sans-serif;'>CONFIDENCIALIDADE E PROTEÇÃO DE DADOS (LGPD): Este relatório apresenta dados estatísticos agregados, garantindo o anonimato dos participantes individuais conforme a Lei Geral de Proteção de Dados (13.709/2018).</div>"

            # CONTEÚDO BRUTO DO ARQUIVO COMPLETO
            raw_html = f"""
            <html>
            <head>
            <meta charset="utf-8">
            <title>Laudo Técnico - {empresa['razao']}</title>
            </head>
            <body style="font-family: sans-serif; padding: 40px; color: #333;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid {COR_PRIMARIA}; padding-bottom:15px; margin-bottom:20px;">
                    <div>{logo_html}</div>
                    <div style="text-align:right;">
                        <div style="font-size:18px; font-weight:bold; color:{COR_PRIMARIA};">LAUDO TÉCNICO HSE-IT</div>
                        <div style="font-size:11px; color:#666;">NR-01 / Diagnóstico de Riscos Psicossociais</div>
                    </div>
                </div>
                <div style="background:#f8f9fa; padding:15px; border-radius:6px; margin-bottom:20px; border-left:5px solid {COR_SECUNDARIA};">
                    {logo_cliente_html}
                    <div style="font-size:10px; color:#888; margin-bottom:5px;">DADOS DO CLIENTE AVALIADO</div>
                    <div style="font-weight:bold; font-size:14px; margin-bottom:5px;">{empresa['razao']}</div>
                    <div style="font-size:11px;">CNPJ: {empresa.get('cnpj','-')} | Endereço: {empresa.get('endereco','-')}</div>
                    <div style="font-size:11px;">Adesão Total: {empresa.get('respondidas',0)} Vidas | Data de Emissão Deste Relatório: {datetime.datetime.now().strftime('%d/%m/%Y')}</div>
                </div>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">1. OBJETIVO E METODOLOGIA CIENTÍFICA</h4>
                <p style="text-align:justify; font-size:11px; line-height:1.6;">Este relatório possui fundamentação técnica e tem como objetivo primário identificar, mapear e mensurar os fatores de risco psicossocial inerentes ao ambiente de trabalho deste cliente. Foi utilizada a ferramenta científica validada <strong>HSE Management Standards Indicator Tool</strong>, alinhada às melhores práticas exigidas pela NR-01. A metodologia avalia rigorosamente 7 dimensões cruciais da saúde mental ocupacional: Nível de Demanda, Autonomia (Controle), Suporte Estrutural (Gestor e Pares), Qualidade dos Relacionamentos, Clareza de Papel e Gestão da Mudança Institucional.</p>

                <div style="display:flex; gap:30px; margin-top:20px; margin-bottom:20px;">
                    <div style="flex:1; border:1px solid #eee; border-radius:8px; padding:10px;">
                        <div style="font-weight:bold; font-size:11px; color:{COR_PRIMARIA}; margin-bottom:10px;">2. SCORE GERAL DA ORGANIZAÇÃO</div>
                        {html_gauge_css}
                    </div>
                    <div style="flex:1; border:1px solid #eee; border-radius:8px; padding:10px;">
                        <div style="font-weight:bold; font-size:11px; color:{COR_PRIMARIA}; margin-bottom:10px;">3. RESUMO PONTUAL DAS DIMENSÕES</div>
                        {html_radar_table}
                    </div>
                </div>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">4. DIAGNÓSTICO DETALHADO POR DIMENSÃO (VISÃO MACRO)</h4>
                <div style="display:flex; flex-wrap:wrap; margin-bottom:20px;">{html_dimensoes}</div>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">5. RAIO-X DOS FATORES DE RISCO (35 ITENS AVALIADOS)</h4>
                <div style="background:white; border:1px solid #eee; padding:15px; border-radius:8px; margin-bottom:20px; column-count:2; column-gap:40px;">{html_x}</div>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">6. PLANO DE AÇÃO ESTRATÉGICO SUGERIDO</h4>
                <table style="width:100%; border-collapse:collapse; font-size:10px; font-family:sans-serif;">
                    <thead><tr style="background-color:{COR_PRIMARIA}; color:white;"><th style="padding:8px; text-align:left;">AÇÃO GERAL</th><th style="padding:8px; text-align:left;">ESTRATÉGIA DETALHADA</th><th style="padding:8px; text-align:left;">ÁREA</th><th style="padding:8px; text-align:left;">RESPONSÁVEL</th><th style="padding:8px; text-align:left;">PRAZO</th></tr></thead>
                    <tbody>{html_act_final}</tbody>
                </table>

                <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">7. CONCLUSÃO TÉCNICA DO LAUDO</h4>
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
            
            b64_pdf = base64.b64encode(textwrap.dedent(raw_html).encode('utf-8')).decode('utf-8')
            href = f'<a href="data:text/html;base64,{b64_pdf}" download="Laudo_Tecnico_Elo_{empresa["id"]}.html" style="text-decoration:none; background-color:{COR_PRIMARIA}; color:white; padding:10px 20px; border-radius:5px; font-weight:bold; display:inline-block;">📥 CLIQUE AQUI PARA BAIXAR O RELATÓRIO (HTML)</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.caption("💡 Dica Profissional: Após baixar o arquivo HTML, abra-o no seu navegador (Chrome/Edge) e aperte `Ctrl + P` ou `Cmd + P` para imprimir. Nas opções de impressão, selecione 'Salvar como PDF' e marque a opção 'Gráficos de Plano de Fundo' para garantir a cor exata da identidade visual.")
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Pré-visualização do Relatório:")
            st.components.v1.html(raw_html, height=800, scrolling=True)

    elif selected == "Histórico & Comparativo":
        st.title("Histórico Evolutivo de Saúde Mental")
        if not visible_companies: st.warning("Cadastre empresas primeiro."); return
        
        empresa_nome = st.selectbox("Selecione a Empresa", [c['razao'] for c in visible_companies])
        empresa = next((c for c in visible_companies if c['razao'] == empresa_nome), None)
        
        if empresa:
            history_data = generate_mock_history()
            st.info("ℹ️ Exibindo dados consolidados de histórico para fins de comparativo.")

            tab_evo, tab_comp = st.tabs(["📈 Gráfico de Evolução Contínua", "⚖️ Comparativo Direto A x B"])
            
            with tab_evo:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                df_hist = pd.DataFrame(history_data)
                fig_line = px.line(df_hist, x='periodo', y='score', markers=True, title="Evolução do Score Geral de Saúde Ocupacional")
                fig_line.update_traces(line_color=COR_SECUNDARIA, line_width=3, marker=dict(size=10, color=COR_PRIMARIA))
                st.plotly_chart(fig_line, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with tab_comp:
                c1, c2 = st.columns(2)
                periodo_a = c1.selectbox("Período de Análise A", [h['periodo'] for h in history_data], index=1)
                periodo_b = c2.selectbox("Período de Análise B", [h['periodo'] for h in history_data], index=0)
                
                dados_a = next((h for h in history_data if h['periodo'] == periodo_a), None)
                dados_b = next((h for h in history_data if h['periodo'] == periodo_b), None)
                
                if dados_a and dados_b:
                    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                    categories = list(dados_a['dimensoes'].keys())
                    fig_comp = go.Figure()
                    fig_comp.add_trace(go.Scatterpolar(r=list(dados_a['dimensoes'].values()), theta=categories, fill='toself', name=f'Análise {periodo_a}', line_color=COR_COMP_A, opacity=0.5))
                    fig_comp.add_trace(go.Scatterpolar(r=list(dados_b['dimensoes'].values()), theta=categories, fill='toself', name=f'Análise {periodo_b}', line_color=COR_COMP_B, opacity=0.6))
                    fig_comp.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
                    st.plotly_chart(fig_comp, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if st.button("📥 Baixar Relatório Evolutivo (HTML)", type="primary"):
                         st.markdown("---")
                         logo_html = get_logo_html(150)
                         logo_cliente_html = ""
                         if empresa.get('logo_b64'):
                             logo_cliente_html = f"<img src='data:image/png;base64,{empresa.get('logo_b64')}' width='100' style='float:right;'>"
                         
                         diff_score = dados_b['score'] - dados_a['score']
                         txt_evolucao = "Melhoria geral observada" if diff_score > 0 else "Estabilidade/Ponto de atenção crítico detectado"
                         
                         chart_css_viz = f"""
                         <div style="padding:20px; border:1px solid #eee; border-radius:8px; font-family:sans-serif; background:#fafafa;">
                             <div style="margin-bottom: 15px;">
                                 <strong>Score Final do Período {periodo_a}:</strong> <span style="font-size:18px; color:{COR_COMP_A}">{dados_a['score']}</span> <br>
                                 <div style="width:100%; background:#e0e0e0; height:14px; border-radius:7px; margin-top:8px;">
                                    <div style="width:{(dados_a['score']/5)*100}%; background:{COR_COMP_A}; height:14px; border-radius:7px;"></div>
                                 </div>
                             </div>
                             <div>
                                 <strong>Score Final do Período {periodo_b}:</strong> <span style="font-size:18px; color:{COR_COMP_B}">{dados_b['score']}</span> <br>
                                 <div style="width:100%; background:#e0e0e0; height:14px; border-radius:7px; margin-top:8px;">
                                    <div style="width:{(dados_b['score']/5)*100}%; background:{COR_COMP_B}; height:14px; border-radius:7px;"></div>
                                 </div>
                             </div>
                         </div>
                         """

                         html_comp = textwrap.dedent(f"""
                         <div class="a4-paper" style="font-family: sans-serif; padding: 40px; color: #333; background: white;">
                            <div style="display:flex; justify-content:space-between; border-bottom:2px solid {COR_PRIMARIA}; padding-bottom:15px; margin-bottom:20px;">
                                <div>{logo_html}</div>
                                <div style="text-align:right;">
                                    <div style="font-size:18px; font-weight:bold; color:{COR_PRIMARIA};">RELATÓRIO DE EVOLUÇÃO HSE</div>
                                    <div style="font-size:11px; color:#666;">Comparativo Histórico de Saúde Ocupacional</div>
                                </div>
                            </div>
                            
                            <div style="background:#f8f9fa; padding:15px; border-radius:6px; margin-bottom:20px; border-left:5px solid {COR_SECUNDARIA};">
                                {logo_cliente_html}
                                <div style="font-size:10px; color:#888; margin-bottom:5px;">DADOS DA ORGANIZAÇÃO</div>
                                <div style="font-weight:bold; font-size:14px; margin-bottom:5px;">{empresa['razao']}</div>
                                <div style="font-size:11px;">CNPJ: {empresa.get('cnpj','-')} | Endereço: {empresa.get('endereco','-')}</div>
                                <div style="font-size:11px;">Períodos Sob Análise Crítica: <b>{periodo_a}</b> versos <b>{periodo_b}</b></div>
                            </div>
                            
                            <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">1. RESUMO DOS INDICADORES CHAVE (KPIs)</h4>
                            <table style="width:100%; border-collapse:collapse; font-size:11px; margin-bottom:20px;">
                                <tr style="background-color:{COR_PRIMARIA}; color:white;">
                                    <th style="padding:10px; text-align:left;">INDICADOR ANALISADO</th>
                                    <th style="padding:10px; text-align:center;">{periodo_a}</th>
                                    <th style="padding:10px; text-align:center;">{periodo_b}</th>
                                    <th style="padding:10px; text-align:center;">VARIAÇÃO</th>
                                </tr>
                                <tr>
                                    <td style="padding:10px; border-bottom:1px solid #eee;">Score Geral da Organização</td>
                                    <td style="padding:10px; border-bottom:1px solid #eee; text-align:center;">{dados_a['score']}</td>
                                    <td style="padding:10px; border-bottom:1px solid #eee; text-align:center;">{dados_b['score']}</td>
                                    <td style="padding:10px; border-bottom:1px solid #eee; text-align:center; font-weight:bold; color:{'green' if diff_score > 0 else 'red'};">{diff_score:+.2f}</td>
                                </tr>
                                <tr>
                                    <td style="padding:10px; border-bottom:1px solid #eee;">Taxa de Adesão (%)</td>
                                    <td style="padding:10px; border-bottom:1px solid #eee; text-align:center;">{dados_a['adesao']}%</td>
                                    <td style="padding:10px; border-bottom:1px solid #eee; text-align:center;">{dados_b['adesao']}%</td>
                                    <td style="padding:10px; border-bottom:1px solid #eee; text-align:center;">{(dados_b['adesao'] - dados_a['adesao']):+.1f}%</td>
                                </tr>
                            </table>
                            
                            <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">2. REPRESENTAÇÃO GRÁFICA COMPARATIVA</h4>
                            {chart_css_viz}
                            
                            <h4 style="color:{COR_PRIMARIA}; border-left:4px solid {COR_SECUNDARIA}; padding-left:10px; margin-top:30px;">3. ANÁLISE TÉCNICA PRELIMINAR</h4>
                            <p style="text-align:justify; font-size:11px; line-height:1.6; background:#f9f9f9; padding:15px; border-radius:6px;">A análise estruturada comparativa entre os períodos demonstra uma <b>{txt_evolucao}</b> no índice geral do ecossistema de saúde mental corporativa. Recomenda-se fortemente manter os protocolos de monitoramento ativos e seguir firmemente com a execução do plano de ação contínuo, focando especialmente nas áreas que não apresentaram variação estatística positiva.</p>
                            
                            <div style="margin-top:50px; font-size:9px; color:#888; text-align:center; border-top:1px solid #ddd; padding-top:10px;">
                                Plataforma Elo NR-01 Enterprise - Documento de Caráter Analítico e Estratégico.
                            </div>
                         </div>
                         """)
                         
                         b64_comp = base64.b64encode(html_comp.encode('utf-8')).decode('utf-8')
                         href_comp = f'<a href="data:text/html;base64,{b64_comp}" download="Relatorio_Evolutivo_{empresa["id"]}.html" style="text-decoration:none; background-color:{COR_PRIMARIA}; color:white; padding:10px 20px; border-radius:5px; font-weight:bold; display:inline-block;">📥 BAIXAR ARQUIVO DE HISTÓRICO (HTML)</a>'
                         st.markdown(href_comp, unsafe_allow_html=True)

    elif selected == "Configurações":
        if perm == "Master":
            st.title("Configurações Master do Sistema")
            t1, t2, t3 = st.tabs(["👥 Gerenciamento de Usuários", "🎨 Identidade e Marca", "⚙️ Servidor e URLs"])
            
            with t1:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.write("### Controle de Acessos")
                
                # Renderiza Tabela de Usuários Atualizada
                if DB_CONNECTED:
                    usrs_raw = supabase.table('admin_users').select("username, role, credits, linked_company_id").execute().data
                else:
                    usrs_raw = [{"username": k, "role": v['role'], "credits": v.get('credits',0)} for k,v in st.session_state.users_db.items()]
                
                if usrs_raw:
                    st.dataframe(pd.DataFrame(usrs_raw), use_container_width=True)
                
                st.markdown("---")
                st.write("#### Criar Novo Usuário de Plataforma")
                c1, c2 = st.columns(2)
                new_u = c1.text_input("Novo Usuário (Login)")
                new_p = c2.text_input("Senha Padrão", type="password")
                new_r = st.selectbox("Nível de Permissão", ["Master", "Gestor"])
                
                if st.button("➕ Confirmar Criação"):
                    if not new_u or not new_p:
                        st.error("Usuário e Senha são obrigatórios.")
                    else:
                        if DB_CONNECTED:
                            try:
                                supabase.table('admin_users').insert({"username": new_u, "password": new_p, "role": new_r, "credits": 9999 if new_r=="Master" else 500}).execute()
                                st.success("✅ Usuário salvo no banco de dados!")
                                time.sleep(1); st.rerun()
                            except Exception as e: st.error(f"Erro no DB: {e}")
                        else:
                            st.session_state.users_db[new_u] = {"password": new_p, "role": new_r, "credits": 9999}
                            st.success("✅ Usuário criado no ambiente local!")
                            time.sleep(1); st.rerun()
                
                st.markdown("---")
                st.write("#### Exclusão de Acesso")
                # Exclusão segura (protege o admin atual de se deletar)
                users_op = [u['username'] for u in usrs_raw if u['username'] != curr_user]
                if users_op:
                    u_del = st.selectbox("Selecione o usuário para revogar acesso permanentemente", users_op)
                    if st.button("🗑️ Deletar Usuário", type="primary"):
                        delete_user(u_del)
                else:
                    st.info("Nenhum outro usuário disponível para exclusão.")
                st.markdown("</div>", unsafe_allow_html=True)

            with t2:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.write("### Identidade Visual do Sistema")
                nn = st.text_input("Nome da Plataforma (Header)", value=st.session_state.platform_config.get('name', 'Elo NR-01'))
                nc = st.text_input("Nome da Consultoria/Clínica", value=st.session_state.platform_config.get('consultancy', ''))
                nl = st.file_uploader("Upload da Nova Logo (PNG ou JPG transparente)", type=['png', 'jpg', 'jpeg'])
                
                if st.button("💾 Salvar Customização"):
                    new_conf = st.session_state.platform_config.copy()
                    new_conf['name'] = nn
                    new_conf['consultancy'] = nc
                    if nl: new_conf['logo_b64'] = image_to_base64(nl)
                    
                    # Logica de salvar configurações central
                    if DB_CONNECTED:
                        try:
                            # Checa se existe a config
                            res = supabase.table('platform_settings').select("*").execute()
                            if res.data:
                                supabase.table('platform_settings').update({"config_json": new_conf}).eq("id", res.data[0]['id']).execute()
                            else:
                                supabase.table('platform_settings').insert({"config_json": new_conf}).execute()
                        except: pass
                        
                    st.session_state.platform_config = new_conf
                    st.success("✅ Identidade visual atualizada em todo o sistema!")
                    time.sleep(1)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            with t3:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.write("### Configuração Estrutural e URL")
                base = st.text_input("URL Base de Produção (Extremamente importante para gerar os links de pesquisa corretos)", value=st.session_state.platform_config.get('base_url', ''))
                
                if st.button("🔗 Salvar Nova URL"):
                    new_conf = st.session_state.platform_config.copy()
                    new_conf['base_url'] = base
                    if DB_CONNECTED:
                        try:
                            res = supabase.table('platform_settings').select("*").execute()
                            if res.data: supabase.table('platform_settings').update({"config_json": new_conf}).eq("id", res.data[0]['id']).execute()
                        except: pass
                    st.session_state.platform_config = new_conf
                    st.success("✅ URL de roteamento atualizada!")
                    time.sleep(1)
                    st.rerun()
                
                st.markdown("---")
                st.write("### Status dos Serviços")
                if DB_CONNECTED:
                    st.info("🟢 Supabase Engine: Online e Sincronizado. Dados persistentes ativados.")
                else:
                    st.error("🔴 Supabase Engine: Offline. O sistema está rodando em cache temporário. Dados serão perdidos ao atualizar a página.")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("🚫 Acesso restrito a usuários do grupo Master.")

# ==============================================================================
# 6. TELA DE PESQUISA (FRONT-END DO COLABORADOR)
# ==============================================================================
def survey_screen():
    cod = st.query_params.get("cod")
    
    # 1. Busca a empresa de forma blindada (DB prioritário)
    comp = None
    if DB_CONNECTED:
        try:
            res = supabase.table('companies').select("*").eq('id', cod).execute()
            if res.data: comp = res.data[0]
        except: pass
    
    # Se nao achou no banco, tenta na memória local
    if not comp:
        comp = next((c for c in st.session_state.companies_db if c['id'] == cod), None)
    
    # 2. Bloqueio por URL invalida
    if not comp: 
        st.error("❌ Link de pesquisa inválido ou empresa não localizada na base de dados.")
        st.caption("Verifique com o RH se o link foi copiado corretamente.")
        return

    # 3. Validacao de Cotas e Validade
    if comp.get('valid_until'):
        try:
            if datetime.date.today() > datetime.date.fromisoformat(comp['valid_until']):
                st.error("⛔ Link de pesquisa expirado de acordo com o contrato vigente.")
                return
        except: pass
        
    limit_evals = comp.get('limit_evals', 999999)
    # Protecao contra null
    resp_count = comp.get('respondidas', 0) if comp.get('respondidas') is not None else 0
    if resp_count >= limit_evals:
        st.error("⚠️ O limite máximo de avaliações estabelecido para este pacote foi atingido.")
        st.caption("Por favor, contate o setor administrativo para expandir a cota.")
        return
    
    # 4. Renderizacao Visual do Formulario
    logo = get_logo_html(150)
    if comp.get('logo_b64'): logo = f"<img src='data:image/png;base64,{comp.get('logo_b64')}' width='180'>"
    
    st.markdown(f"<div style='text-align:center; margin-bottom: 20px;'>{logo}</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center; color: {COR_PRIMARIA};'>Diagnóstico de Riscos Psicossociais - {comp['razao']}</h3>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='security-alert'>
            <strong>🔒 AVALIAÇÃO SEGURA E CRIPTOGRAFADA</strong><br>
            A sua empresa NÃO tem acesso a respostas isoladas de forma alguma.<br>
            <ul>
                <li>Seu CPF será transformado em um código hash irreversível no momento do envio.</li>
                <li>As informações são tratadas apenas estatisticamente para criar melhorias no seu ambiente de trabalho.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("survey_form"):
        st.write("#### 1. Identificação Funcional")
        c1, c2 = st.columns(2)
        cpf_raw = c1.text_input("Seu CPF (Apenas números, sem pontos ou traços)")
        
        # Estrutura de Setor
        s_keys = ["Geral"] # Fallback seguro
        if 'org_structure' in comp and isinstance(comp['org_structure'], dict) and comp['org_structure']:
            s_keys = list(comp['org_structure'].keys())
             
        setor_colab = c2.selectbox("Selecione seu Setor de Atuação", s_keys)
        
        st.markdown("---")
        st.write("#### 2. Questionário de Percepção do Ambiente")
        st.caption("Responda o mais sinceramente possível. Baseie-se nas suas últimas 4 a 6 semanas de trabalho.")
        
        missing = False
        answers_dict = {}
        
        # Loop Dinâmico de Categorias e Perguntas - Agora em ABAS
        abas_categorias = list(st.session_state.hse_questions.keys())
        tabs = st.tabs(abas_categorias)
        
        for i, (category, questions) in enumerate(st.session_state.hse_questions.items()):
            with tabs[i]:
                st.markdown(f"<h5 style='color: {COR_SECUNDARIA}; margin-top:10px; margin-bottom: 20px;'>➡️ {category}</h5>", unsafe_allow_html=True)
                for q in questions:
                    # UX: Exibicao amigavel da pergunta e do exemplo
                    st.markdown(f"**{q['q']}**")
                    st.caption(f"💡 *{q.get('help', '')}*")
                    
                    # Sistema de Radio Buttons Obrigatorios
                    options = ["Nunca", "Raramente", "Às vezes", "Frequentemente", "Sempre"] if q['id'] <= 24 else ["Discordo", "Neutro", "Concordo"]
                    
                    response_value = st.radio(
                        "Resposta:", 
                        options, 
                        key=f"ans_q_{q['id']}", 
                        horizontal=True, 
                        index=None,
                        label_visibility="collapsed" # Esconde o label padrao para ficar mais limpo
                    )
                    
                    if response_value is None: 
                        missing = True
                    else: 
                        answers_dict[q['q']] = response_value
                    
                    st.markdown("<hr style='margin:15px 0; border: 0; border-top: 1px dashed #e0e0e0;'>", unsafe_allow_html=True)
        
        st.markdown("---")
        aceite_lgpd = st.checkbox("Declaro que li e concordo com a coleta e tratamento destes dados sensíveis de forma anônima e aglomerada para fins estatísticos de saúde ocupacional, conforme a legislação vigente.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("✅ Concluir e Enviar Minhas Respostas", type="primary", use_container_width=True)
        
        if submit_btn:
            if not cpf_raw or len(cpf_raw) < 11: 
                st.error("⚠️ Preenchimento de CPF obrigatório ou inválido.")
            elif not aceite_lgpd: 
                st.error("⚠️ O aceite do termo de confidencialidade é obrigatório para envio.")
            elif missing: 
                st.error("⚠️ Existem perguntas não respondidas nas abas acima. Navegue pelas categorias e responda todas por favor.")
            else:
                # Todos os critérios atendidos. Hora de salvar no Banco de Dados Real.
                hashed_cpf = hashlib.sha256(cpf_raw.encode()).hexdigest()
                cpf_already_exists = False
                
                if DB_CONNECTED:
                    # Verifica se o CPF já existe para essa empresa
                    try:
                        check_cpf = supabase.table('responses').select("id").eq("company_id", comp['id']).eq("cpf_hash", hashed_cpf).execute()
                        if len(check_cpf.data) > 0:
                            cpf_already_exists = True
                    except Exception as e:
                        pass # Continua se falhar a checagem
                        
                else:
                    # Verificação em memória local se offline
                    for r in st.session_state.local_responses_db:
                        if r['company_id'] == comp['id'] and r['cpf_hash'] == hashed_cpf:
                            cpf_already_exists = True
                            break

                if cpf_already_exists:
                    st.error("🚫 Identificamos que já existe uma resposta registrada para o seu CPF nesta avaliação. Para garantir a fidelidade dos dados, permitimos apenas uma resposta por colaborador.")
                else:
                    if DB_CONNECTED:
                        try:
                            # Insere o registro criptografado na tabela 'responses'
                            supabase.table('responses').insert({
                                "company_id": comp['id'], 
                                "cpf_hash": hashed_cpf,
                                "setor": setor_colab, 
                                "answers": answers_dict
                            }).execute()
                        except Exception as e: 
                            st.error(f"Erro de processamento no banco: {e}")
                    else:
                        st.session_state.local_responses_db.append({
                            "company_id": comp['id'], 
                            "cpf_hash": hashed_cpf,
                            "setor": setor_colab, 
                            "answers": answers_dict
                        })

                    st.success("🎉 Avaliação recebida com sucesso! Obrigado pela sua contribuição genuína.")
                    st.balloons()
                    time.sleep(3) # Tempo para ler a mensagem antes de atualizar a pagina
                    
                    # Reinicia a sessao para não permitir double-submit acidental
                    st.session_state.logged_in = False 
                    st.rerun()

# ==============================================================================
# 7. ROUTER CENTRAL (START DO APP)
# ==============================================================================
if not st.session_state.logged_in:
    # Se não há logado, e há cod na URL, joga pra pesquisa do colaborador. Se não, vai pro Login Master
    if "cod" in st.query_params: 
        survey_screen()
    else: 
        login_screen()
else:
    # Se está logado como admin, vai pro dashboard
    if st.session_state.user_role == 'admin': 
        admin_dashboard()
    else: 
        survey_screen()
