import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Sistema de Vacinas SUS",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para parecer com Tkinter
st.markdown("""
<style>
    /* Fundo da página */
    .stApp {
        background-color: #F3E5F5;
    }
    
    /* Cards e containers */
    .css-1r6slb0, .css-1v3fvcr {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #E1BEE7;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #4A148C !important;
    }
    
    /* Botões */
    .stButton button {
        background-color: #6A1B9A;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
    }
    .stButton button:hover {
        background-color: #4A148C;
    }
    
    /* Botão de perigo (remover) */
    .stButton button[kind="secondary"] {
        background-color: #D81B60;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input {
        border-radius: 8px;
        border: 1px solid #9C27B0;
    }
    
    /* DataFrames */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #E1BEE7;
        border-radius: 8px;
        color: #4A148C;
        font-weight: bold;
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Arquivo de dados
ARQUIVO_DADOS = "vacinas.json"

# ========== FUNÇÕES ==========
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def verificar_validade(data_str):
    try:
        data_val = datetime.strptime(data_str, "%d/%m/%Y")
        dias = (data_val - datetime.now()).days
        if dias < 0:
            return "💀 VENCIDA", "#D32F2F"
        elif dias <= 30:
            return f"⚠️ VENCE em {dias} dias", "#F57C00"
        elif dias <= 90:
            return f"📅 Vence em {dias} dias", "#FFC107"
        else:
            return "✅ Válida", "#388E3C"
    except:
        return "❌ Data inválida", "#D32F2F"

def gerar_id(nome, lote):
    return f"{nome}_{lote}".replace(" ", "_").lower()

# ========== INICIALIZAÇÃO ==========
if "dados" not in st.session_state:
    hoje = datetime.now()
    dados_iniciais = carregar_dados()
    
    if not dados_iniciais:
        dados_iniciais = {
            "covid_a123": {"nome": "COVID-19", "lote": "A123", "quantidade": 150, "minimo": 50, "validade": (hoje + timedelta(days=180)).strftime("%d/%m/%Y"), "em_uso": True},
            "covid_b456": {"nome": "COVID-19", "lote": "B456", "quantidade": 80, "minimo": 50, "validade": (hoje + timedelta(days=90)).strftime("%d/%m/%Y"), "em_uso": False},
            "influenza_b456": {"nome": "Influenza", "lote": "B456", "quantidade": 200, "minimo": 80, "validade": (hoje + timedelta(days=120)).strftime("%d/%m/%Y"), "em_uso": True},
            "hepatite_c789": {"nome": "Hepatite B", "lote": "C789", "quantidade": 100, "minimo": 30, "validade": (hoje + timedelta(days=365)).strftime("%d/%m/%Y"), "em_uso": True},
            "febre_d012": {"nome": "Febre Amarela", "lote": "D012", "quantidade": 180, "minimo": 60, "validade": (hoje + timedelta(days=270)).strftime("%d/%m/%Y"), "em_uso": True},
        }
    
    st.session_state.dados = dados_iniciais

dados = st.session_state.dados

# ========== TÍTULO ==========
col_title1, col_title2, col_title3 = st.columns([1, 2, 1])
with col_title2:
    st.markdown("# 💉 SISTEMA DE ESTOQUE - VACINAS SUS")
    st.markdown("---")

# ========== MENU ==========
menu = st.radio(
    "📋 MENU",
    ["💉 VACINAS EM USO", "📊 CONTROLE DE ESTOQUE", "📜 HISTÓRICO", "ℹ️ SOBRE"],
    horizontal=True
)

# ========== VACINAS EM USO ==========
if menu == "💉 VACINAS EM USO":
    st.subheader("💉 Vacinas em Uso")
    
    # Filtra vacinas em uso
    em_uso = {k: v for k, v in dados.items() if v.get("em_uso", False)}
    
    if em_uso:
        # Cria DataFrame para mostrar como tabela
        df_uso = []
        for id_lote, vacina in em_uso.items():
            status, cor = verificar_validade(vacina.get("validade", ""))
            df_uso.append({
                "💊 Vacina": vacina["nome"],
                "🔢 Lote": vacina["lote"],
                "📦 Estoque": f"{vacina.get('quantidade', 0)} und",
                "📅 Validade": status
            })
        
        df = pd.DataFrame(df_uso)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Botão copiar lote
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            lote_selecionado = st.selectbox("Selecione a vacina para copiar o lote:", 
                                           [f"{v['nome']} - Lote: {v['lote']}" for v in em_uso.values()])
            if st.button("📋 COPIAR LOTE", use_container_width=True):
                lote = lote_selecionado.split("Lote:")[1].strip()
                st.toast(f"✅ Lote '{lote}' copiado!", icon="✅")
                st.code(lote)
        
        # Atualizar lote
        st.markdown("---")
        st.subheader("🔄 Atualizar Lote em Uso")
        
        with st.form("atualizar_lote"):
            col_a, col_b = st.columns(2)
            with col_a:
                vacina_selecionada = st.selectbox("Vacina", [v["nome"] for v in em_uso.values()])
            with col_b:
                novo_lote = st.text_input("Novo Lote", placeholder="Digite o novo lote")
            
            if st.form_submit_button("🔄 ATUALIZAR", use_container_width=True):
                if novo_lote:
                    for id_lote, v in dados.items():
                        if v["nome"] == vacina_selecionada:
                            dados[id_lote]["em_uso"] = False
                    
                    novo_id = gerar_id(vacina_selecionada, novo_lote)
                    if novo_id in dados:
                        dados[novo_id]["em_uso"] = True
                    else:
                        dados[novo_id] = {
                            "nome": vacina_selecionada,
                            "lote": novo_lote,
                            "quantidade": 0,
                            "minimo": 30,
                            "validade": (datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y"),
                            "em_uso": True
                        }
                    
                    salvar_dados(dados)
                    st.session_state.dados = dados
                    st.success(f"✅ Lote alterado para '{novo_lote}'!")
                    st.rerun()
                else:
                    st.error("Digite um lote!")
    else:
        st.info("Nenhuma vacina em uso. Vá para 'CONTROLE DE ESTOQUE' e ative uma vacina.")

# ========== CONTROLE DE ESTOQUE ==========
elif menu == "📊 CONTROLE DE ESTOQUE":
    st.subheader("📊 Controle de Estoque")
    
    # Lista de todos os lotes
    if dados:
        # DataFrame completo
        df_estoque = []
    for id_lote, vacina in dados.items():
        status, cor = verificar_validade(vacina.get("validade", ""))
        em_uso = "⭐ EM USO" if vacina.get("em_uso", False) else "⚪"
        
        # Calcula dias restantes
        try:
            data_val = datetime.strptime(vacina.get("validade", ""), "%d/%m/%Y")
            dias_restantes = (data_val - datetime.now()).days
            if dias_restantes < 0:
                info_validade = f"💀 VENCIDA em {vacina.get('validade', '')}"
            elif dias_restantes == 0:
                info_validade = f"⚠️ VENCE HOJE! ({vacina.get('validade', '')})"
            elif dias_restantes <= 30:
                info_validade = f"⚠️ VENCE em {dias_restantes} dias ({vacina.get('validade', '')})"
            else:
                info_validade = f"✅ Válida até {vacina.get('validade', '')}"
        except:
            info_validade = f"❌ Data inválida: {vacina.get('validade', '')}"
        
        df_estoque.append({
            "💊 Vacina": vacina["nome"],
            "🔢 Lote": vacina["lote"],
            "📦 Estoque": vacina.get("quantidade", 0),
            "⚠️ Mínimo": vacina.get("minimo", 30),
            "📅 Validade": info_validade,
            "📌 Status": em_uso
        })
        
        df = pd.DataFrame(df_estoque)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("⚙️ Ações por Lote")
        
        # Selecionar lote para ações
        opcoes = [f"{v['nome']} - Lote: {v['lote']}" for v in dados.values()]
        selecionado = st.selectbox("Selecione o lote:", opcoes)
        
        # Encontra o lote selecionado
        lote_selecionado = selecionado.split("Lote:")[1].strip()
        vacina_selecionada = None
        id_selecionado = None
        
        for id_lote, vacina in dados.items():
            if vacina["lote"] == lote_selecionado:
                vacina_selecionada = vacina
                id_selecionado = id_lote
                break
        
        if vacina_selecionada:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("⭐ ATIVAR", use_container_width=True):
                    for i, v in dados.items():
                        if v["nome"] == vacina_selecionada["nome"]:
                            dados[i]["em_uso"] = False
                    dados[id_selecionado]["em_uso"] = True
                    salvar_dados(dados)
                    st.session_state.dados = dados
                    st.success(f"✅ Lote ativado!")
                    st.rerun()
            
            with col2:
                entrada = st.number_input("Entrada", key="entrada", min_value=0, step=10)
                if st.button("📥 ENTRADA", use_container_width=True):
                    if entrada > 0:
                        dados[id_selecionado]["quantidade"] = dados[id_selecionado].get("quantidade", 0) + entrada
                        salvar_dados(dados)
                        st.session_state.dados = dados
                        st.success(f"✅ +{entrada} unidades!")
                        st.rerun()
            
            with col3:
                saida = st.number_input("Saída", key="saida", min_value=0, step=10)
                if st.button("📤 BAIXA", use_container_width=True):
                    if saida > 0:
                        if saida <= dados[id_selecionado].get("quantidade", 0):
                            dados[id_selecionado]["quantidade"] = dados[id_selecionado].get("quantidade", 0) - saida
                            salvar_dados(dados)
                            st.session_state.dados = dados
                            st.success(f"✅ -{saida} unidades!")
                            st.rerun()
                        else:
                            st.error("Estoque insuficiente!")
            
            with col4:
                if not vacina_selecionada.get("em_uso", False):
                    if st.button("🗑️ REMOVER", use_container_width=True):
                        del dados[id_selecionado]
                        salvar_dados(dados)
                        st.session_state.dados = dados
                        st.success(f"✅ Lote removido!")
                        st.rerun()
        
        # Adicionar novo lote
        st.markdown("---")
        st.subheader("➕ Adicionar Novo Lote")
        
        with st.form("novo_lote"):
            col_a, col_b = st.columns(2)
            with col_a:
                novo_nome = st.text_input("Nome da Vacina")
                novo_lote = st.text_input("Lote")
            with col_b:
                nova_validade = st.text_input("Validade (DD/MM/AAAA)", value=(datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y"))
                nova_qtde = st.number_input("Quantidade Inicial", min_value=0, value=0)
            
            if st.form_submit_button("➕ ADICIONAR", use_container_width=True):
                if novo_nome and novo_lote:
                    novo_id = gerar_id(novo_nome, novo_lote)
                    if novo_id not in dados:
                        dados[novo_id] = {
                            "nome": novo_nome,
                            "lote": novo_lote,
                            "quantidade": nova_qtde,
                            "minimo": 30,
                            "validade": nova_validade,
                            "em_uso": False
                        }
                        salvar_dados(dados)
                        st.session_state.dados = dados
                        st.success(f"✅ Lote '{novo_lote}' adicionado!")
                        st.rerun()
                    else:
                        st.error("Lote já existe!")
                else:
                    st.error("Preencha nome e lote!")
    else:
        st.info("Nenhum lote cadastrado.")

# ========== HISTÓRICO ==========
elif menu == "📜 HISTÓRICO":
    st.subheader("📜 Histórico de Movimentações")
    st.info("📝 Histórico será implementado na próxima versão!")
    st.markdown("""
    Funcionalidades planejadas:
    - Registro de todas as movimentações
    - Filtros por data
    - Relatórios de estoque
    """)

# ========== SOBRE ==========
else:
    st.subheader("ℹ️ Sobre o Sistema")
    st.markdown("""
    ---
    **💉 SISTEMA DE ESTOQUE - VACINAS SUS**
    
    **Versão Web 1.0** - Visual similar ao Tkinter
    
    **Funcionalidades:**
    - ✅ Vacinas EM USO na tela principal
    - ✅ Múltiplos lotes para mesma vacina
    - ✅ Controle de validade com alertas coloridos
    - ✅ Entrada e saída de estoque
    - ✅ Interface com cores roxas (igual ao seu tema)
    - ✅ Acesso de qualquer lugar com internet
    
    **Dados salvos em:** `vacinas.json` (na mesma pasta do app)
    
    ---
    """)

# Salva dados automaticamente
def salvar_ao_sair():
    salvar_dados(dados)

import atexit
atexit.register(salvar_ao_sair)