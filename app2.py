import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client

# Configuração da página
st.set_page_config(page_title="Sistema de Vacinas SUS", page_icon="💉", layout="wide")

# Conexão Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inicializa dados na sessão
if "dados" not in st.session_state:
    st.session_state.dados = {}

# ========== FUNÇÕES ==========
def carregar_dados():
    """Carrega os dados do Supabase"""
    try:
        response = supabase.table("vacinas").select("*").execute()
        dados = {f"{row['nome']}_{row['lote']}": row for row in response.data}
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")
        return {}

def salvar_dados(dados):
    """Salva os dados no Supabase"""
    try:
        supabase.table("vacinas").delete().neq("id", 0).execute()
        for item in dados.values():
            supabase.table("vacinas").insert(item).execute()
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

def verificar_validade(data_str):
    try:
        data_val = datetime.strptime(data_str, "%d/%m/%Y")
        dias = (data_val - datetime.now()).days
        if dias < 0: return "💀 VENCIDA", "#D32F2F"
        elif dias <= 30: return f"⚠️ VENCE em {dias} dias", "#F57C00"
        elif dias <= 90: return f"📅 Vence em {dias} dias", "#FFC107"
        else: return "✅ Válida", "#388E3C"
    except:
        return "❌ Data inválida", "#D32F2F"

def gerar_id(nome, lote):
    return f"{nome}_{lote}".replace(" ", "_").lower()

# ========== CARREGA DADOS INICIAIS ==========
if not st.session_state.dados:
    st.session_state.dados = carregar_dados()

# ========== INTERFACE (igual ao seu layout atual) ==========
st.markdown("# 💉 SISTEMA DE ESTOQUE - VACINAS SUS")
st.markdown("---")

menu = st.radio(
    "📋 MENU",
    ["💉 VACINAS EM USO", "📊 CONTROLE DE ESTOQUE", "📜 HISTÓRICO", "ℹ️ SOBRE"],
    horizontal=True
)

# ========== VACINAS EM USO ==========
if menu == "💉 VACINAS EM USO":
    st.subheader("💉 Vacinas em Uso")
    dados = st.session_state.dados
    em_uso = {k: v for k, v in dados.items() if v.get("em_uso", False)}
    if em_uso:
        df_uso = []
        for vacina in em_uso.values():
            status, _ = verificar_validade(vacina.get("validade", ""))
            df_uso.append({
                "💊 Vacina": vacina["nome"],
                "🔢 Lote": vacina["lote"],
                "📦 Estoque": f"{vacina.get('quantidade', 0)} und",
                "📅 Validade": status
            })
        st.dataframe(pd.DataFrame(df_uso), use_container_width=True)
    else:
        st.info("Nenhuma vacina em uso.")

# ========== CONTROLE DE ESTOQUE ==========
elif menu == "📊 CONTROLE DE ESTOQUE":
    st.subheader("📊 Controle de Estoque")
    dados = st.session_state.dados

    if dados:
        # DataFrame completo
        df_estoque = []
        for vacina in dados.values():
            status, _ = verificar_validade(vacina.get("validade", ""))
            em_uso = "⭐ EM USO" if vacina.get("em_uso", False) else "⚪"
            df_estoque.append({
                "💊 Vacina": vacina["nome"],
                "🔢 Lote": vacina["lote"],
                "📦 Estoque": vacina.get("quantidade", 0),
                "⚠️ Mínimo": vacina.get("minimo", 30),
                "📅 Validade": status,
                "📌 Status": em_uso
            })

        st.dataframe(pd.DataFrame(df_estoque), use_container_width=True)

        # Formulário para adicionar/editar (exemplo de adição)
        with st.expander("➕ Adicionar / Editar Lote"):
            with st.form("novo_lote"):
                nome = st.text_input("Nome da Vacina")
                lote = st.text_input("Lote")
                fabricante = st.text_input("Fabricante")
                fabricacao = st.text_input("Fabricação", value=datetime.now().strftime("%d/%m/%Y"))
                validade = st.text_input("Validade", value=(datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y"))
                recebimento = st.text_input("Recebimento", value=datetime.now().strftime("%d/%m/%Y"))
                quantidade = st.number_input("Quantidade", min_value=0, value=0)
                minimo = st.number_input("Mínimo", min_value=0, value=30)
                em_uso = st.checkbox("Em uso?")

                if st.form_submit_button("Salvar Lote"):
                    if nome and lote:
                        novo_id = gerar_id(nome, lote)
                        dados[novo_id] = {
                            "nome": nome,
                            "lote": lote,
                            "fabricante": fabricante,
                            "fabricacao": fabricacao,
                            "validade": validade,
                            "recebimento": recebimento,
                            "quantidade": quantidade,
                            "minimo": minimo,
                            "em_uso": em_uso
                        }
                        salvar_dados(dados)
                        st.session_state.dados = dados
                        st.success(f"Lote {lote} salvo com sucesso!")
                        st.rerun()
                    else:
                        st.error("Nome e lote são obrigatórios.")
    else:
        st.info("Nenhum lote cadastrado.")

# ========== HISTÓRICO ==========
elif menu == "📜 HISTÓRICO":
    st.subheader("📜 Histórico de Movimentações")
    st.info("Histórico será implementado com Supabase também em breve.")

# ========== SOBRE ==========
else:
    st.subheader("ℹ️ Sobre o Sistema")
    st.markdown("**Versão Supabase** - Dados permanentes na nuvem ☁️")