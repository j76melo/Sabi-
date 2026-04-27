import streamlit as st
import json
import os
import pandas as pd
import time
from datetime import datetime, timedelta
from supabase import create_client

os.environ['TZ'] = 'America/Sao_Paulo'
time.tzset()

st.set_page_config(page_title="Sistema de Vacinas SUS", page_icon="💉", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #F5F5F5; }
    h1, h2, h3 { color: #4A148C !important; }
    .stButton button { background-color: #6A1B9A; color: white; font-weight: bold; border-radius: 8px; border: none; }
    .stButton button:hover { background-color: #4A148C; }
</style>
""", unsafe_allow_html=True)

# ========== CONEXÃO SUPABASE ==========
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== FUNÇÕES DE BANCO DE DADOS ==========
def carregar_dados():
    """Carrega todos os lotes do Supabase"""
    try:
        response = supabase.table("vacinas").select("*").execute()
        dados = {}
        for row in response.data:
            key = f"{row['nome']}_{row['lote']}".replace(" ", "_").upper()
            dados[key] = row
        return dados
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")
        return {}

def salvar_lote(item):
    """Insere ou atualiza UM lote no Supabase"""
    try:
        # Remove 'id' se existir (não deve ser enviado no UPDATE)
        item_para_salvar = {k: v for k, v in item.items() if k != 'id'}
        
        # Verifica se já existe
        existing = supabase.table("vacinas").select("id").eq("nome", item["nome"]).eq("lote", item["lote"]).execute()
        
        if existing.data:
            # Atualiza
            supabase.table("vacinas").update(item_para_salvar).eq("id", existing.data[0]["id"]).execute()
        else:
            # Insere
            supabase.table("vacinas").insert(item_para_salvar).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar lote {item.get('lote', 'desconhecido')}: {e}")
        return False

def remover_lote(nome, lote):
    """Remove UM lote do Supabase"""
    try:
        supabase.table("vacinas").delete().eq("nome", nome).eq("lote", lote).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao remover lote {lote}: {e}")
        return False

# ========== FUNÇÕES AUXILIARES ==========
def registrar_log(acao, vacina, lote, quantidade, obs=""):
    try:
        supabase.table("logs").insert({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "acao": acao,
            "vacina": vacina,
            "lote": lote,
            "quantidade": quantidade,
            "observacao": obs
        }).execute()
    except:
        pass

def registrar_evento_auto(evento, observacao=""):
    try:
        supabase.table("eventos").insert({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "evento": evento,
            "quem": "Sistema (automático)",
            "obs": observacao
        }).execute()
    except:
        pass

def verificar_validade(data_str):
    try:
        data_val = datetime.strptime(data_str, "%d/%m/%Y")
        dias = (data_val - datetime.now()).days
        if dias < 0: return "💀 VENCIDA", "#D32F2F"
        elif dias == 0: return "⚠️ VENCE HOJE!", "#F57C00"
        elif dias <= 30: return f"⚠️ VENCE em {dias} dias", "#F57C00"
        elif dias <= 90: return f"📅 Vence em {dias} dias", "#FFC107"
        else: return "✅ Válida", "#388E3C"
    except:
        return "❌ Data inválida", "#D32F2F"

def gerar_id(nome, lote):
    return f"{nome}_{lote}".replace(" ", "_").upper()

def gerar_html_tabela(dados, titulo):
    if not dados: return "<html><body><p>Nenhum dado</p></body></html>"
    html = f"<html><head><meta charset='UTF-8'><title>{titulo}</title><style>body{{font-family:Arial;margin:40px;}} h1{{color:#4A148C;text-align:center;}} table{{width:100%;border-collapse:collapse;}} th{{background:#6A1B9A;color:white;padding:8px;}} td{{padding:6px;border:1px solid #ddd;text-align:center;}} .data{{text-align:center;color:gray;margin-bottom:20px;}}</style></head><body><h1>{titulo}</h1><div class='data'>{datetime.now().strftime('%d/%m/%Y %H:%M')}</div><table><tr>" + "".join([f"<th>{c}</th>" for c in dados[0].keys()]) + "</tr>" + "".join(["<tr>" + "".join([f"<td>{v}</td>" for v in row.values()]) + "</tr>" for row in dados]) + "</table></body></html>"
    return html

# ========== INICIALIZAÇÃO ==========
if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

dados = st.session_state.dados

# ========== MENU ==========
st.markdown("# 💉 SISTEMA DE ESTOQUE - VACINAS SUS")
st.markdown("---")
menu = st.radio("📋 MENU", ["💉 VACINAS EM USO", "📊 ESTOQUE", "📋 EVENTOS", "📜 LOGS", "ℹ️ SOBRE"], horizontal=True)

# ========== TELA 1 ==========
if menu == "💉 VACINAS EM USO":
    st.subheader("💉 Vacinas em Uso")
    em_uso = {k:v for k,v in dados.items() if v.get("em_uso")}
    if em_uso:
        em_uso_ordenado = sorted(em_uso.values(), key=lambda x: x["nome"])
        df = [{"Vacina": v["nome"], "Lote": v["lote"], "Status": verificar_validade(v.get("validade",""))[0]} for v in em_uso_ordenado]
        st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)
        
        if st.button("🖨️ GERAR RELATÓRIO", use_container_width=True):
            if df:
                html = gerar_html_tabela(df, "VACINAS EM USO")
                st.download_button("📥 BAIXAR HTML", html, file_name=f"vacinas_uso_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html")
                st.info("💡 Abra o arquivo e use Ctrl+P para imprimir como PDF")
        
        st.markdown("---")
        st.subheader("🔄 Atualizar Lote")
        with st.form("att"):
            vac = st.selectbox("Vacina", [v["nome"] for v in em_uso.values()])
            novo = st.text_input("Novo Lote")
            if st.form_submit_button("ATUALIZAR"):
                if novo:
                    # Desativa o lote atual
                    for idl, v in dados.items():
                        if v["nome"] == vac and v.get("em_uso"):
                            v["em_uso"] = False
                            salvar_lote(v)
                    
                    # Verifica se o novo lote já existe
                    novo_id = gerar_id(vac, novo)
                    if novo_id in dados:
                        dados[novo_id]["em_uso"] = True
                        salvar_lote(dados[novo_id])
                    else:
                        novo_lote = {"nome": vac, "lote": novo, "fabricante": "", "fabricacao": datetime.now().strftime("%d/%m/%Y"), "validade": (datetime.now()+timedelta(days=365)).strftime("%d/%m/%Y"), "recebimento": datetime.now().strftime("%d/%m/%Y"), "quantidade": 0, "minimo": 30, "em_uso": True}
                        dados[novo_id] = novo_lote
                        salvar_lote(novo_lote)
                    
                    registrar_log("ALTERAÇÃO LOTE", vac, novo, 0, "")
                    st.session_state.dados = carregar_dados()
                    st.success(f"✅ Lote alterado para {novo}!")
                    st.rerun()
    else:
        st.info("Nenhuma vacina em uso.")

# ========== TELA 2 ==========
elif menu == "📊 ESTOQUE":
    st.subheader("📊 Estoque")
    
    if dados:
        df = []
        for v in dados.values():
            s, _ = verificar_validade(v.get("validade",""))
            df.append({"Nome": v["nome"], "Lote": v["lote"], "Fabricante": v.get("fabricante",""), "Fabricação": v.get("fabricacao",""), "Validade": v.get("validade",""), "Recebimento": v.get("recebimento",""), "Estoque": v.get("quantidade",0), "Mínimo": v.get("minimo",30), "Status": s, "Situação": "EM USO" if v.get("em_uso") else "ESTOQUE"})
        st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)
        
        if st.button("🖨️ GERAR RELATÓRIO COMPLETO", use_container_width=True):
            if df:
                html = gerar_html_tabela(df, "DEMONSTRATIVO DE ESTOQUE - SAE LAPA")
                st.download_button("📥 BAIXAR HTML", html, file_name=f"estoque_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html")
                st.info("💡 Abra o arquivo e use Ctrl+P para imprimir como PDF")
        
        st.markdown("---")
        st.subheader("⚙️ Ações")
        opcoes = [f"{v['nome']} - {v['lote']}" for v in dados.values()]
        sel = st.selectbox("Selecione o lote", opcoes)
        lote_sel = sel.split(" - ")[1]
        vid = None
        vsel = None
        for idl, v in dados.items():
            if v["lote"] == lote_sel:
                vid = idl
                vsel = v
                break
        
        if vsel:
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("⭐ ATIVAR"):
                    # Desativa todos da mesma vacina
                    for v in dados.values():
                        if v["nome"] == vsel["nome"] and v.get("em_uso"):
                            v["em_uso"] = False
                            salvar_lote(v)
                    # Ativa o selecionado
                    dados[vid]["em_uso"] = True
                    salvar_lote(dados[vid])
                    registrar_log("ATIVAR", vsel["nome"], vsel["lote"], 0, "")
                    st.session_state.dados = carregar_dados()
                    st.success("✅ Ativado!")
                    st.rerun()
            with c2:
                with st.popover("📤 BAIXA"):
                    q = st.number_input("Quantidade", min_value=1, step=1)
                    obs = st.text_area("Observação")
                    if st.button("CONFIRMAR"):
                        if q <= vsel.get("quantidade", 0):
                            dados[vid]["quantidade"] = vsel.get("quantidade", 0) - q
                            salvar_lote(dados[vid])
                            registrar_log("BAIXA", vsel["nome"], vsel["lote"], q, obs)
                            registrar_evento_auto(f"Baixa de {q} und - {vsel['lote']}", obs)
                            st.session_state.dados = carregar_dados()
                            st.success(f"✅ -{q} unidades!")
                            st.rerun()
                        else:
                            st.error("Estoque insuficiente!")
            with c3:
                if st.button("🗑️ REMOVER", use_container_width=True):
                    if vsel.get("em_uso", False):
                        st.warning(f"⚠️ '{vsel['nome']}' está EM USO! Removendo mesmo assim...")
                    remover_lote(vsel["nome"], vsel["lote"])
                    registrar_log("REMOVER LOTE", vsel["nome"], vsel["lote"], 0, "Removido" + (" (estava em uso)" if vsel.get("em_uso") else ""))
                    st.session_state.dados = carregar_dados()
                    st.success(f"✅ Lote '{vsel['lote']}' removido!")
                    st.rerun()
    
    st.markdown("---")
    st.subheader("➕ Novo Lote")
    with st.form("novo"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Vacina")
            lote = st.text_input("Lote")
            fab = st.text_input("Fabricante")
            dfab = st.text_input("Fabricação", value=datetime.now().strftime("%d/%m/%Y"))
        with c2:
            dval = st.text_input("Validade", value=(datetime.now()+timedelta(days=365)).strftime("%d/%m/%Y"))
            drec = st.text_input("Recebimento", value=datetime.now().strftime("%d/%m/%Y"))
            qtde = st.number_input("Quantidade", min_value=0, value=0)
            min_val = st.number_input("Mínimo", min_value=0, value=30)
        if st.form_submit_button("ADICIONAR"):
            if nome and lote:
                novo_lote = {
                    "nome": nome,
                    "lote": lote,
                    "fabricante": fab,
                    "fabricacao": dfab,
                    "validade": dval,
                    "recebimento": drec,
                    "quantidade": qtde,
                    "minimo": min_val,
                    "em_uso": False
                }
                if salvar_lote(novo_lote):
                    registrar_log("CADASTRO", nome, lote, qtde, "")
                    registrar_evento_auto(f"Recebimento lote {lote} - {qtde} und", f"Fabricante: {fab}")
                    st.session_state.dados = carregar_dados()
                    st.success(f"✅ Lote {lote} adicionado!")
                    st.rerun()
                else:
                    st.error("Erro ao salvar!")
            else:
                st.error("Preencha nome e lote!")

# ========== TELA 3 ==========
elif menu == "📋 EVENTOS":
    st.subheader("📋 Eventos")
    try:
        response = supabase.table("eventos").select("*").order("data", desc=True).limit(50).execute()
        if response.data:
            df = [{"Data": e["data"], "Evento": e["evento"], "Registrado por": e["quem"], "Obs": e["obs"][:50]} for e in response.data]
            st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum evento registrado.")
    except:
        st.info("Tabela de eventos não configurada.")

# ========== TELA 4 ==========
elif menu == "📜 LOGS":
    st.subheader("📜 Logs")
    try:
        response = supabase.table("logs").select("*").order("data", desc=True).limit(200).execute()
        if response.data:
            df = [{"Data": l["data"], "Ação": l["acao"], "Vacina": l["vacina"], "Lote": l["lote"], "Qtd": l["quantidade"]} for l in response.data]
            st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum log encontrado.")
    except:
        st.info("Tabela de logs não configurada.")
    if st.button("ATUALIZAR"):
        st.rerun()

# ========== TELA 5 ==========
else:
    st.subheader("ℹ️ Sobre")
    st.markdown(f"""
    **Sistema de Estoque - Vacinas SUS**
    
    - Tela 1: Vacinas em uso
    - Tela 2: Estoque completo
    - Tela 3: Eventos
    - Tela 4: Logs
    
    **Desenvolvido por:** Jairo Marcos Melo  
    **Técnico em Enfermagem | Desenvolvedor Autodidata**  
    **Data:** {datetime.now().strftime("%d/%m/%Y")}
    
    ---
    
    *"A prevenção é a vacina contra o amanhã incerto."*
    
    ---
    
    **Versão Supabase - Dados persistentes na nuvem**
    """)