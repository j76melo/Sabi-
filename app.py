import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Sistema de Vacinas SUS",
    page_icon="💉",
    layout="wide"
)

# Arquivo de dados
ARQUIVO_DADOS = "vacinas.json"

# ========== FUNÇÕES (aproveitadas do seu código) ==========
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
            return "❌ VENCIDA", "#D32F2F"
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
    # Dados iniciais
    hoje = datetime.now()
    st.session_state.dados = {
        "covid_a123": {"nome": "COVID-19", "lote": "A123", "quantidade": 150, "minimo": 50, "validade": (hoje + timedelta(days=180)).strftime("%d/%m/%Y"), "em_uso": True},
        "influenza_b456": {"nome": "Influenza", "lote": "B456", "quantidade": 200, "minimo": 80, "validade": (hoje + timedelta(days=120)).strftime("%d/%m/%Y"), "em_uso": True},
        "hepatite_c789": {"nome": "Hepatite B", "lote": "C789", "quantidade": 100, "minimo": 30, "validade": (hoje + timedelta(days=365)).strftime("%d/%m/%Y"), "em_uso": True},
    }
    
    # Tenta carregar dados existentes
    dados_existente = carregar_dados()
    if dados_existente:
        st.session_state.dados = dados_existente

dados = st.session_state.dados

# ========== INTERFACE ==========
st.title("💉 SISTEMA DE ESTOQUE - VACINAS SUS")
st.markdown("---")

# Menu lateral
menu = st.sidebar.radio(
    "📋 MENU",
    ["💉 Vacinas em Uso", "📊 Controle de Estoque", "ℹ️ Sobre"]
)

# ========== VACINAS EM USO ==========
if menu == "💉 Vacinas em Uso":
    st.header("💉 Vacinas em Uso")
    
    # Filtra vacinas em uso
    em_uso = {k: v for k, v in dados.items() if v.get("em_uso", False)}
    
    if em_uso:
        # Mostra em cards
        col1, col2, col3 = st.columns(3)
        colunas = [col1, col2, col3]
        
        for i, (id_lote, vacina) in enumerate(em_uso.items()):
            with colunas[i % 3]:
                with st.container(border=True):
                    st.markdown(f"### {vacina['nome']}")
                    st.markdown(f"**Lote:** `{vacina['lote']}`")
                    st.markdown(f"**Estoque:** {vacina.get('quantidade', 0)} unidades")
                    
                    status, cor = verificar_validade(vacina.get('validade', ''))
                    st.markdown(f"**Validade:** {status}")
                    
                    if st.button(f"📋 Copiar Lote", key=f"copy_{id_lote}"):
                        st.toast(f"✅ Lote '{vacina['lote']}' copiado!", icon="✅")
                        st.code(vacina['lote'])
    else:
        st.info("Nenhuma vacina em uso. Vá para 'Controle de Estoque' e ative uma vacina.")
    
    # Atualizar lote
    st.markdown("---")
    st.subheader("🔄 Atualizar Lote em Uso")
    
    if em_uso:
        with st.form("atualizar_lote"):
            vacina_selecionada = st.selectbox("Vacina", [v["nome"] for v in em_uso.values()])
            novo_lote = st.text_input("Novo Lote")
            
            if st.form_submit_button("🔄 ATUALIZAR"):
                if novo_lote:
                    # Desativa lote atual
                    for id_lote, v in dados.items():
                        if v["nome"] == vacina_selecionada:
                            dados[id_lote]["em_uso"] = False
                    
                    # Cria ou ativa novo lote
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
        st.warning("Nenhuma vacina cadastrada.")

# ========== CONTROLE DE ESTOQUE ==========
elif menu == "📊 Controle de Estoque":
    st.header("📊 Controle de Estoque")
    
    # Abas dentro do estoque
    tab1, tab2 = st.tabs(["📋 Lista de Lotes", "➕ Adicionar Lote"])
    
    with tab1:
        if dados:
            for id_lote, vacina in dados.items():
                with st.expander(f"💉 {vacina['nome']} - Lote: {vacina['lote']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Quantidade", f"{vacina.get('quantidade', 0)} und")
                        st.metric("Mínimo", f"{vacina.get('minimo', 30)} und")
                    
                    with col2:
                        status, _ = verificar_validade(vacina.get('validade', ''))
                        st.metric("Validade", vacina.get('validade', 'N/A'))
                        st.metric("Status", status)
                    
                    with col3:
                        if vacina.get("em_uso", False):
                            st.success("⭐ EM USO")
                        else:
                            st.warning("⚪ Inativo")
                    
                    # Botões
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        if st.button(f"⭐ Ativar", key=f"ativar_{id_lote}"):
                            for i, v in dados.items():
                                if v["nome"] == vacina["nome"]:
                                    dados[i]["em_uso"] = False
                            dados[id_lote]["em_uso"] = True
                            salvar_dados(dados)
                            st.session_state.dados = dados
                            st.success(f"✅ {vacina['nome']} ativada!")
                            st.rerun()
                    
                    with col_b:
                        entrada = st.number_input("+", key=f"ent_{id_lote}", min_value=0, step=10, label_visibility="collapsed")
                        if st.button(f"📥 Entrada", key=f"add_{id_lote}"):
                            if entrada > 0:
                                dados[id_lote]["quantidade"] = dados[id_lote].get("quantidade", 0) + entrada
                                salvar_dados(dados)
                                st.session_state.dados = dados
                                st.success(f"✅ +{entrada} unidades!")
                                st.rerun()
                    
                    with col_c:
                        saida = st.number_input("-", key=f"sai_{id_lote}", min_value=0, step=10, label_visibility="collapsed")
                        if st.button(f"📤 Baixa", key=f"rem_{id_lote}"):
                            if saida > 0:
                                if saida <= dados[id_lote].get("quantidade", 0):
                                    dados[id_lote]["quantidade"] = dados[id_lote].get("quantidade", 0) - saida
                                    salvar_dados(dados)
                                    st.session_state.dados = dados
                                    st.success(f"✅ -{saida} unidades!")
                                    st.rerun()
                                else:
                                    st.error("Estoque insuficiente!")
                    
                    with col_d:
                        if not vacina.get("em_uso", False):
                            if st.button(f"🗑️ Remover", key=f"del_{id_lote}"):
                                del dados[id_lote]
                                salvar_dados(dados)
                                st.session_state.dados = dados
                                st.success(f"✅ Lote removido!")
                                st.rerun()
        else:
            st.info("Nenhum lote cadastrado.")
    
    with tab2:
        with st.form("novo_lote"):
            st.subheader("➕ Adicionar Novo Lote")
            col1, col2 = st.columns(2)
            with col1:
                novo_nome = st.text_input("Nome da Vacina")
                novo_lote = st.text_input("Lote")
            with col2:
                nova_validade = st.text_input("Validade (DD/MM/AAAA)", value=(datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y"))
                nova_qtde = st.number_input("Quantidade Inicial", min_value=0, value=0)
            
            if st.form_submit_button("➕ ADICIONAR"):
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

# ========== SOBRE ==========
else:
    st.header("ℹ️ Sobre o Sistema")
    st.markdown("""
    **💉 SISTEMA DE ESTOQUE - VACINAS SUS**
    
    Versão Web 1.0
    
    **Funcionalidades:**
    - ✅ Vacinas EM USO na tela principal
    - ✅ Múltiplos lotes para mesma vacina
    - ✅ Controle de validade com alertas
    - ✅ Entrada e saída de estoque
    - ✅ Interface web responsiva
    
    **Acesse de qualquer lugar com internet!**
    """)

# Salva dados automaticamente ao sair
def salvar_ao_sair():
    salvar_dados(dados)

import atexit
atexit.register(salvar_ao_sair)