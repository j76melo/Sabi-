import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# Configuração
st.set_page_config(page_title="Sistema de Vacinas SUS", page_icon="💉", layout="wide", initial_sidebar_state="collapsed")

# CSS
st.markdown("""
<style>
    .stApp { background-color: #F5F5F5; }
    h1, h2, h3 { color: #4A148C !important; }
    .stButton button { background-color: #6A1B9A; color: white; font-weight: bold; border-radius: 8px; border: none; }
    .stButton button:hover { background-color: #4A148C; }
</style>
""", unsafe_allow_html=True)

# Arquivos
ARQUIVO_DADOS = "vacinas.json"
ARQUIVO_EVENTOS = "eventos.json"
ARQUIVO_LOGS = "logs.json"

# ========== FUNÇÕES ==========
def carregar_dados():
    try:
        if os.path.exists(ARQUIVO_DADOS):
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def carregar_eventos():
    try:
        if os.path.exists(ARQUIVO_EVENTOS):
            with open(ARQUIVO_EVENTOS, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []

def salvar_eventos(eventos):
    with open(ARQUIVO_EVENTOS, "w", encoding="utf-8") as f:
        json.dump(eventos, f, ensure_ascii=False, indent=2)

def carregar_logs():
    try:
        if os.path.exists(ARQUIVO_LOGS):
            with open(ARQUIVO_LOGS, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []

def salvar_logs(logs):
    with open(ARQUIVO_LOGS, "w", encoding="utf-8") as f:
        json.dump(logs[-1000:], f, ensure_ascii=False, indent=2)

def registrar_log(acao, vacina, lote, quantidade, obs=""):
    logs = carregar_logs()
    logs.append({"data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "acao": acao, "vacina": vacina, "lote": lote, "quantidade": quantidade, "observacao": obs})
    salvar_logs(logs)

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
    return f"{nome}_{lote}".replace(" ", "_").upper()  # upper() força maiúsculo

def gerar_html_tabela(dados, titulo):
    html = f"<html><head><meta charset='UTF-8'><title>{titulo}</title><style>"
    html += "body{font-family:Arial;margin:40px;} h1{color:#4A148C;text-align:center;}"
    html += "table{width:100%;border-collapse:collapse;} th{background:#6A1B9A;color:white;padding:8px;}"
    html += "td{padding:6px;border:1px solid #ddd;text-align:center;} .data{text-align:center;color:gray;margin-bottom:20px;}"
    html += "</style></head><body>"
    html += f"<h1>{titulo}</h1><div class='data'>{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>"
    html += "<table><tr>" + "".join([f"<th>{c}</th>" for c in dados[0].keys()]) + "</tr>"
    for row in dados:
        html += "<tr>" + "".join([f"<td>{v}</td>" for v in row.values()]) + "</tr>"
    html += "</table></body></html>"
    return html

# ========== INICIALIZAÇÃO ==========
if "dados" not in st.session_state:
    d = carregar_dados()
    if not d:
        hoje = datetime.now()
        d = {}
    st.session_state.dados = d
    st.session_state.eventos = carregar_eventos()

dados = st.session_state.dados
eventos = st.session_state.eventos

# ========== MENU ==========
st.markdown("# 💉 SISTEMA DE ESTOQUE - VACINAS SUS")
st.markdown("---")
menu = st.radio("📋 MENU", ["💉 VACINAS EM USO", "📊 ESTOQUE", "📋 EVENTOS", "📜 LOGS", "ℹ️ SOBRE"], horizontal=True)

# ========== TELA 1 ==========
if menu == "💉 VACINAS EM USO":
    st.subheader("💉 Vacinas em Uso")
    em_uso = {k:v for k,v in dados.items() if v.get("em_uso")}
    if em_uso:
        df = [{"Vacina": v["nome"], "Lote": v["lote"], "Status": verificar_validade(v.get("validade",""))[0]} for v in em_uso.values()]
        st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)
        
        if st.button("🖨️ GERAR RELATÓRIO", use_container_width=True):
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
                    for idl, v in dados.items():
                        if v["nome"] == vac: dados[idl]["em_uso"] = False
                    nid = gerar_id(vac, novo)
                    if nid in dados:
                        dados[nid]["em_uso"] = True
                    else:
                        dados[nid] = {"nome": vac, "lote": novo, "fabricante": "", "fabricacao": datetime.now().strftime("%d/%m/%Y"), "validade": (datetime.now()+timedelta(days=365)).strftime("%d/%m/%Y"), "recebimento": datetime.now().strftime("%d/%m/%Y"), "quantidade": 0, "minimo": 30, "em_uso": True}
                    salvar_dados(dados)
                    registrar_log("ALTERAÇÃO LOTE", vac, novo, 0, "")
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
            df.append({"Nome": v["nome"], "Lote": v["lote"], "Fabricante": v.get("fabricante",""), "Fabricação": v.get("fabricacao",""), "Validade": v.get("validade",""), "Recebimento": v.get("recebimento",""), "Estoque": v.get("quantidade",0), "Mínimo": v.get("minimo",30), "Status": s, "Em Uso": "⭐" if v.get("em_uso") else "⚪"})
        st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)
        
        if st.button("🖨️ GERAR RELATÓRIO COMPLETO", use_container_width=True):
            html = gerar_html_tabela(df, "DEMONSTRATIVO DE ESTOQUE - SAE LAPA")
            st.download_button("📥 BAIXAR HTML", html, file_name=f"estoque_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html")
            st.info("💡 Abra o arquivo e use Ctrl+P para imprimir como PDF")
        
        st.markdown("---")
        st.subheader("⚙️ Ações")
        opcoes = [f"{v['nome']} - {v['lote']}" for v in dados.values()]
        sel = st.selectbox("Selecione o lote", opcoes)
        lote_sel = sel.split(" - ")[1]
        for idl, v in dados.items():
            if v["lote"] == lote_sel:
                vid = idl
                vsel = v
                break
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⭐ ATIVAR"):
                for v in dados.values():
                    if v["nome"] == vsel["nome"]: v["em_uso"] = False
                dados[vid]["em_uso"] = True
                salvar_dados(dados)
                registrar_log("ATIVAR", vsel["nome"], vsel["lote"], 0, "")
                st.success("✅ Ativado!")
                st.rerun()
        with c2:
            with st.popover("📤 BAIXA"):
                q = st.number_input("Quantidade", min_value=1, step=1)
                obs = st.text_area("Observação")
                if st.button("CONFIRMAR"):
                    if q <= vsel.get("quantidade",0):
                        dados[vid]["quantidade"] = vsel.get("quantidade",0) - q
                        salvar_dados(dados)
                        registrar_log("BAIXA", vsel["nome"], vsel["lote"], q, obs)
                        eventos.append({"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "evento": f"Baixa de {q} und - {vsel['lote']}", "quem": "Sistema", "obs": obs})
                        salvar_eventos(eventos)
                        st.success(f"✅ -{q} unidades!")
                        st.rerun()
                    else:
                        st.error("Estoque insuficiente!")
                with c3:
            # BOTÃO REMOVER FORÇADO - SEM CHECKBOX
                if st.button("🗑️ REMOVER", use_container_width=True):
                    # Usa vsel e vid que já existem no código
                    if vsel.get("em_uso", False):
                        st.warning(f"⚠️ '{vsel['nome']}' está EM USO! Removendo mesmo assim...")
                    
                    registrar_log("REMOVER LOTE", vsel["nome"], vsel["lote"], 0, 
                                "Removido" + (" (estava em uso)" if vsel.get("em_uso") else ""))
                    del dados[vid]
                    salvar_dados(dados)
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
                min = st.number_input("Mínimo", min_value=0, value=30)
            if st.form_submit_button("ADICIONAR"):
                if nome and lote:
                    nid = gerar_id(nome, lote)
                    if nid not in dados:
                        dados[nid] = {"nome": nome, "lote": lote, "fabricante": fab, "fabricacao": dfab, "validade": dval, "recebimento": drec, "quantidade": qtde, "minimo": min, "em_uso": False}
                        salvar_dados(dados)
                        registrar_log("CADASTRO", nome, lote, qtde, "")
                        eventos.append({"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "evento": f"Recebimento lote {lote} - {qtde} und", "quem": "Sistema", "obs": f"Fabricante: {fab}"})
                        salvar_eventos(eventos)
                        st.success(f"✅ Lote {lote} adicionado!")
                        st.rerun()
                    else:
                        st.error("Lote já existe!")

# ========== TELA 3 ==========
elif menu == "📋 EVENTOS":
    st.subheader("📋 Eventos")
    with st.form("ev"):
        ev = st.text_input("Evento")
        quem = st.text_input("Quem registrou")
        obs = st.text_area("Observação", height=100)
        if st.form_submit_button("SALVAR"):
            if ev and quem:
                eventos.append({"data": datetime.now().strftime("%d/%m/%Y %H:%M"), "evento": ev, "quem": quem, "obs": obs})
                salvar_eventos(eventos)
                registrar_log("EVENTO", ev, "-", 0, obs)
                st.success("✅ Registrado!")
                st.rerun()
    
    if eventos:
        df = [{"Data": e["data"], "Evento": e["evento"], "Registrado por": e["quem"], "Obs": e["obs"][:50]} for e in eventos[-50:][::-1]]
        st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)

# ========== TELA 4 ==========
elif menu == "📜 LOGS":
    st.subheader("📜 Logs")
    logs = carregar_logs()
    if logs:
        df = [{"Data": l["data"], "Ação": l["acao"], "Vacina": l["vacina"], "Lote": l["lote"], "Qtd": l["quantidade"]} for l in logs[-200:][::-1]]
        st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)
    if st.button("ATUALIZAR"):
        st.rerun()

# ========== TELA 5 ==========
else:
    st.subheader("ℹ️ Sobre")
    st.markdown("**Sistema de Estoque - Vacinas SUS**\n\n- Tela 1: Vacinas em uso\n- Tela 2: Estoque completo\n- Tela 3: Eventos\n- Tela 4: Logs\n\nVersão Web")

# ========== SALVAR ==========
def salvar_tudo():
    salvar_dados(dados)
    salvar_eventos(eventos)

import atexit
atexit.register(salvar_tudo)