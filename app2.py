import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Configuração da página
st.set_page_config(
    page_title="Sistema de Vacinas SUS",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    .stApp { background-color: #F5F5F5; }
    .css-1r6slb0, .css-1v3fvcr {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #D1C4E9;
    }
    h1, h2, h3 { color: #4A148C !important; }
    .stButton button {
        background-color: #6A1B9A;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    .stButton button:hover { background-color: #4A148C; }
    .stTextInput input, .stNumberInput input, .stDateInput input {
        border-radius: 8px;
        border: 1px solid #9C27B0;
    }
    .dataframe { border-radius: 10px; overflow: hidden; }
    .stAlert { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Constantes
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
    logs = logs[-1000:]  # Mantém últimos 1000 registros
    with open(ARQUIVO_LOGS, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def registrar_log(acao, vacina, lote, quantidade, observacao=""):
    logs = carregar_logs()
    logs.append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "acao": acao,
        "vacina": vacina,
        "lote": lote,
        "quantidade": quantidade,
        "observacao": observacao
    })
    salvar_logs(logs)

def verificar_validade(data_str):
    try:
        data_val = datetime.strptime(data_str, "%d/%m/%Y")
        dias = (data_val - datetime.now()).days
        if dias < 0:
            return "💀 VENCIDA", "#D32F2F"
        elif dias == 0:
            return "⚠️ VENCE HOJE!", "#F57C00"
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

def gerar_pdf_vacinas_em_uso(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=18, alignment=TA_CENTER, textColor=colors.HexColor('#4A148C'), spaceAfter=20)
    data_style = ParagraphStyle('Data', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=30)
    texto_style = ParagraphStyle('Texto', parent=styles['Normal'], fontSize=14, leading=20, textColor=colors.black)
    
    story.append(Paragraph("VACINAS EM USO", titulo_style))
    story.append(Paragraph(datetime.now().strftime("%d/%m/%Y - %H:%M"), data_style))
    
    em_uso = {k: v for k, v in dados.items() if v.get("em_uso", False)}
    for vacina in sorted(em_uso.values(), key=lambda x: x["nome"]):
        status, _ = verificar_validade(vacina.get("validade", ""))
        story.append(Paragraph(f"<b>{vacina['nome']}</b>", texto_style))
        story.append(Paragraph(f"Lote: {vacina['lote']} | Status: {status}", texto_style))
        story.append(Spacer(1, 0.3*cm))
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Total de vacinas em uso: {len(em_uso)}", texto_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def gerar_pdf_estoque(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=16, alignment=TA_CENTER, textColor=colors.HexColor('#4A148C'), spaceAfter=15)
    data_style = ParagraphStyle('Data', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=20)
    
    story.append(Paragraph("DEMONSTRATIVO DE ESTOQUE DE VACINAS", titulo_style))
    story.append(Paragraph("SAE LAPA", titulo_style))
    story.append(Paragraph(datetime.now().strftime("%d/%m/%Y - %H:%M"), data_style))
    
    tabela_dados = []
    cabecalho = ["Nome", "Lote", "Fabricante", "Fabricação", "Validade", "Recebimento", "Estoque", "Mínimo", "Status", "Em Uso"]
    tabela_dados.append(cabecalho)
    
    for vacina in dados.values():
        status, _ = verificar_validade(vacina.get("validade", ""))
        em_uso = "⭐ SIM" if vacina.get("em_uso", False) else "⚪ NÃO"
        tabela_dados.append([
            vacina.get("nome", ""),
            vacina.get("lote", ""),
            vacina.get("fabricante", ""),
            vacina.get("fabricacao", ""),
            vacina.get("validade", ""),
            vacina.get("recebimento", ""),
            str(vacina.get("quantidade", 0)),
            str(vacina.get("minimo", 30)),
            status,
            em_uso
        ])
    
    tabela = Table(tabela_dados, repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6A1B9A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(tabela)
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Total de lotes cadastrados: {len(dados)}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def gerar_pdf_eventos(eventos, mes, ano):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=16, alignment=TA_CENTER, textColor=colors.HexColor('#4A148C'), spaceAfter=10)
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=20)
    evento_style = ParagraphStyle('Evento', parent=styles['Normal'], fontSize=11, leading=18, spaceAfter=15)
    
    story.append(Paragraph("RELATÓRIO DE EVENTOS", titulo_style))
    story.append(Paragraph(f"SAE LAPA - {mes}/{ano}", subtitulo_style))
    
    eventos_filtrados = [e for e in eventos if e.get("data", "").startswith(f"{mes}/")]
    eventos_ordenados = sorted(eventos_filtrados, key=lambda x: x.get("data", ""), reverse=True)
    
    for evento in eventos_ordenados:
        story.append(Paragraph(f"<b>📌 {evento.get('data', '')}</b>", evento_style))
        story.append(Paragraph(f"Evento: {evento.get('evento', '')}", evento_style))
        story.append(Paragraph(f"Registrado por: {evento.get('quem', '')}", evento_style))
        story.append(Paragraph(f"Observação: {evento.get('obs', '')}", evento_style))
        story.append(Spacer(1, 0.3*cm))
    
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Total de eventos: {len(eventos_filtrados)}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ========== INICIALIZAÇÃO ==========
if "dados" not in st.session_state:
    dados_iniciais = carregar_dados()
    if not dados_iniciais:
        hoje = datetime.now()
        dados_iniciais = {
            "covid_a123": {"nome": "COVID-19", "lote": "A123", "fabricante": "Pfizer", "fabricacao": (hoje - timedelta(days=30)).strftime("%d/%m/%Y"), "validade": (hoje + timedelta(days=180)).strftime("%d/%m/%Y"), "recebimento": hoje.strftime("%d/%m/%Y"), "quantidade": 150, "minimo": 50, "em_uso": True},
            "covid_b456": {"nome": "COVID-19", "lote": "B456", "fabricante": "AstraZeneca", "fabricacao": (hoje - timedelta(days=15)).strftime("%d/%m/%Y"), "validade": (hoje + timedelta(days=90)).strftime("%d/%m/%Y"), "recebimento": (hoje - timedelta(days=10)).strftime("%d/%m/%Y"), "quantidade": 80, "minimo": 50, "em_uso": False},
            "influenza_b456": {"nome": "Influenza", "lote": "B456", "fabricante": "Butantan", "fabricacao": (hoje - timedelta(days=60)).strftime("%d/%m/%Y"), "validade": (hoje + timedelta(days=120)).strftime("%d/%m/%Y"), "recebimento": (hoje - timedelta(days=20)).strftime("%d/%m/%Y"), "quantidade": 200, "minimo": 80, "em_uso": True},
            "hepatite_c789": {"nome": "Hepatite B", "lote": "C789", "fabricante": "Fiocruz", "fabricacao": (hoje - timedelta(days=90)).strftime("%d/%m/%Y"), "validade": (hoje + timedelta(days=365)).strftime("%d/%m/%Y"), "recebimento": (hoje - timedelta(days=30)).strftime("%d/%m/%Y"), "quantidade": 100, "minimo": 30, "em_uso": True},
        }
    st.session_state.dados = dados_iniciais

if "eventos" not in st.session_state:
    st.session_state.eventos = carregar_eventos()

dados = st.session_state.dados
eventos = st.session_state.eventos

# ========== TÍTULO ==========
st.markdown("# 💉 SISTEMA DE ESTOQUE - VACINAS SUS")
st.markdown("---")

# ========== MENU ==========
menu = st.radio(
    "📋 MENU",
    ["💉 VACINAS EM USO", "📊 ESTOQUE", "📋 EVENTOS", "📜 LOGS", "ℹ️ SOBRE"],
    horizontal=True
)

# ========== TELA 1 - VACINAS EM USO ==========
if menu == "💉 VACINAS EM USO":
    st.subheader("💉 Vacinas em Uso")
    
    em_uso = {k: v for k, v in dados.items() if v.get("em_uso", False)}
    
    if em_uso:
        df_uso = []
        for vacina in em_uso.values():
            status, cor = verificar_validade(vacina.get("validade", ""))
            df_uso.append({
                "💊 Vacina": vacina["nome"],
                "🔢 Lote": vacina["lote"],
                "📅 Status": status
            })
        
        df = pd.DataFrame(df_uso)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🖨️ IMPRIMIR PDF", use_container_width=True):
                pdf = gerar_pdf_vacinas_em_uso(dados)
                st.download_button("📥 BAIXAR PDF", pdf, file_name=f"vacinas_em_uso_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔄 Atualizar Lote em Uso")
        
        with st.form("atualizar_lote"):
            vacina_selecionada = st.selectbox("Vacina", [v["nome"] for v in em_uso.values()])
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
                        hoje = datetime.now()
                        dados[novo_id] = {
                            "nome": vacina_selecionada,
                            "lote": novo_lote,
                            "fabricante": "",
                            "fabricacao": hoje.strftime("%d/%m/%Y"),
                            "validade": (hoje + timedelta(days=365)).strftime("%d/%m/%Y"),
                            "recebimento": hoje.strftime("%d/%m/%Y"),
                            "quantidade": 0,
                            "minimo": 30,
                            "em_uso": True
                        }
                    
                    salvar_dados(dados)
                    registrar_log("ALTERAÇÃO LOTE", vacina_selecionada, novo_lote, 0, f"Lote ativado")
                    st.success(f"✅ Lote alterado para '{novo_lote}'!")
                    st.rerun()
                else:
                    st.error("Digite um lote!")
    else:
        st.info("Nenhuma vacina em uso. Vá para 'ESTOQUE' e ative uma vacina.")

# ========== TELA 2 - ESTOQUE ==========
elif menu == "📊 ESTOQUE":
    st.subheader("📊 Controle de Estoque")
    
    # Botão PDF
    col_pdf1, col_pdf2 = st.columns([3, 1])
    with col_pdf2:
        if st.button("🖨️ IMPRIMIR PDF", use_container_width=True):
            pdf = gerar_pdf_estoque(dados)
            st.download_button("📥 BAIXAR PDF", pdf, file_name=f"estoque_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
    
    if dados:
        df_estoque = []
        for vacina in dados.values():
            status, _ = verificar_validade(vacina.get("validade", ""))
            em_uso = "⭐ EM USO" if vacina.get("em_uso", False) else "⚪"
            df_estoque.append({
                "💊 Vacina": vacina["nome"],
                "🔢 Lote": vacina["lote"],
                "🏭 Fabricante": vacina.get("fabricante", ""),
                "📅 Fabricação": vacina.get("fabricacao", ""),
                "📅 Validade": vacina.get("validade", ""),
                "📥 Recebimento": vacina.get("recebimento", ""),
                "📦 Estoque": vacina.get("quantidade", 0),
                "⚠️ Mínimo": vacina.get("minimo", 30),
                "📌 Status": status,
                "⭐ Em Uso": em_uso
            })
        
        df = pd.DataFrame(df_estoque)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("⚙️ Ações por Lote")
        
        opcoes = [f"{v['nome']} - Lote: {v['lote']}" for v in dados.values()]
        selecionado = st.selectbox("Selecione o lote:", opcoes)
        
        lote_selecionado = selecionado.split("Lote:")[1].strip()
        id_selecionado = None
        vacina_selecionada = None
        
        for id_lote, vacina in dados.items():
            if vacina["lote"] == lote_selecionado:
                id_selecionado = id_lote
                vacina_selecionada = vacina
                break
        
        if vacina_selecionada:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("⭐ ATIVAR", use_container_width=True):
                    for v in dados.values():
                        if v["nome"] == vacina_selecionada["nome"]:
                            v["em_uso"] = False
                    dados[id_selecionado]["em_uso"] = True
                    salvar_dados(dados)
                    registrar_log("ATIVAR LOTE", vacina_selecionada["nome"], vacina_selecionada["lote"], 0, "Lote ativado")
                    st.success(f"✅ Lote ativado!")
                    st.rerun()
            
            with col2:
                with st.expander("📤 DAR BAIXA"):
                    saida = st.number_input("Quantidade", min_value=1, step=1, key="saida")
                    obs_saida = st.text_area("Observação", placeholder="Ex: Aplicações do dia", key="obs_saida")
                    if st.button("CONFIRMAR BAIXA", use_container_width=True):
                        if saida <= vacina_selecionada.get("quantidade", 0):
                            dados[id_selecionado]["quantidade"] = vacina_selecionada.get("quantidade", 0) - saida
                            salvar_dados(dados)
                            registrar_log("BAIXA (SAÍDA)", vacina_selecionada["nome"], vacina_selecionada["lote"], saida, obs_saida)
                            
                            # Adiciona evento automático
                            evento_auto = f"Baixa de {saida} unidades do lote {vacina_selecionada['lote']}"
                            eventos.append({
                                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "evento": evento_auto,
                                "quem": "Sistema (automático)",
                                "obs": obs_saida if obs_saida else "Movimentação de estoque"
                            })
                            salvar_eventos(eventos)
                            
                            st.success(f"✅ -{saida} unidades!")
                            st.rerun()
                        else:
                            st.error("Estoque insuficiente!")
            
            with col3:
                if not vacina_selecionada.get("em_uso", False):
                    if st.button("🗑️ REMOVER", use_container_width=True):
                        registrar_log("REMOVER LOTE", vacina_selecionada["nome"], vacina_selecionada["lote"], 0, "Lote removido")
                        del dados[id_selecionado]
                        salvar_dados(dados)
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
                novo_fabricante = st.text_input("Fabricante")
                nova_fabricacao = st.text_input("Data de Fabricação (DD/MM/AAAA)", value=datetime.now().strftime("%d/%m/%Y"))
            with col_b:
                nova_validade = st.text_input("Data de Validade (DD/MM/AAAA)", value=(datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y"))
                novo_recebimento = st.text_input("Data de Recebimento (DD/MM/AAAA)", value=datetime.now().strftime("%d/%m/%Y"))
                nova_qtde = st.number_input("Quantidade Inicial", min_value=0, value=0)
                novo_minimo = st.number_input("Estoque Mínimo", min_value=0, value=30)
            
            if st.form_submit_button("➕ ADICIONAR", use_container_width=True):
                if novo_nome and novo_lote:
                    novo_id = gerar_id(novo_nome, novo_lote)
                    if novo_id not in dados:
                        dados[novo_id] = {
                            "nome": novo_nome,
                            "lote": novo_lote,
                            "fabricante": novo_fabricante,
                            "fabricacao": nova_fabricacao,
                            "validade": nova_validade,
                            "recebimento": novo_recebimento,
                            "quantidade": nova_qtde,
                            "minimo": novo_minimo,
                            "em_uso": False
                        }
                        salvar_dados(dados)
                        registrar_log("CADASTRO", novo_nome, novo_lote, nova_qtde, f"Fab: {nova_fabricacao}, Val: {nova_validade}")
                        
                        # Adiciona evento automático
                        evento_auto = f"Recebimento do lote {novo_lote} - {nova_qtde} unidades - Fabricante: {novo_fabricante}"
                        eventos.append({
                            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "evento": evento_auto,
                            "quem": "Sistema (automático)",
                            "obs": f"Nota fiscal de recebimento. Validade: {nova_validade}"
                        })
                        salvar_eventos(eventos)
                        
                        st.success(f"✅ Lote '{novo_lote}' adicionado!")
                        st.rerun()
                    else:
                        st.error("Lote já existe!")
                else:
                    st.error("Preencha nome e lote!")
    else:
        st.info("Nenhum lote cadastrado. Adicione o primeiro lote abaixo.")
        
        with st.form("primeiro_lote"):
            col_a, col_b = st.columns(2)
            with col_a:
                novo_nome = st.text_input("Nome da Vacina")
                novo_lote = st.text_input("Lote")
                novo_fabricante = st.text_input("Fabricante")
            with col_b:
                nova_validade = st.text_input("Validade (DD/MM/AAAA)", value=(datetime.now() + timedelta(days=365)).strftime("%d/%m/%Y"))
                nova_qtde = st.number_input("Quantidade Inicial", min_value=0, value=0)
            
            if st.form_submit_button("➕ ADICIONAR", use_container_width=True):
                if novo_nome and novo_lote:
                    novo_id = gerar_id(novo_nome, novo_lote)
                    hoje = datetime.now()
                    dados[novo_id] = {
                        "nome": novo_nome,
                        "lote": novo_lote,
                        "fabricante": novo_fabricante,
                        "fabricacao": hoje.strftime("%d/%m/%Y"),
                        "validade": nova_validade,
                        "recebimento": hoje.strftime("%d/%m/%Y"),
                        "quantidade": nova_qtde,
                        "minimo": 30,
                        "em_uso": True
                    }
                    salvar_dados(dados)
                    registrar_log("CADASTRO", novo_nome, novo_lote, nova_qtde, "Primeiro lote cadastrado")
                    st.success(f"✅ Primeiro lote adicionado!")
                    st.rerun()
                else:
                    st.error("Preencha nome e lote!")

# ========== TELA 3 - EVENTOS ==========
elif menu == "📋 EVENTOS":
    st.subheader("📋 Eventos")
    
    st.markdown("### 📝 Novo Evento")
    
    with st.form("novo_evento"):
        evento_nome = st.text_input("Evento", placeholder="Ex: Dia D de Vacinação, Falta de luz, Campanha...")
        evento_quem = st.text_input("Quem registrou", placeholder="Nome do profissional")
        evento_obs = st.text_area("Observação", height=100, placeholder="Descreva o ocorrido em detalhes...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 SALVAR EVENTO", use_container_width=True):
                if evento_nome and evento_quem:
                    eventos.append({
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "evento": evento_nome,
                        "quem": evento_quem,
                        "obs": evento_obs
                    })
                    salvar_eventos(eventos)
                    registrar_log("EVENTO", evento_nome, "-", 0, evento_obs)
                    st.success(f"✅ Evento registrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha pelo menos o Evento e Quem registrou!")
        with col2:
            if st.form_submit_button("🧹 LIMPAR", use_container_width=True):
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📜 Histórico de Eventos")
    
    if eventos:
        df_eventos = []
        for e in eventos[-50:]:  # Últimos 50 eventos
            df_eventos.append({
                "📅 Data/Hora": e.get("data", ""),
                "📌 Evento": e.get("evento", ""),
                "👤 Registrado por": e.get("quem", ""),
                "📝 Observação": e.get("obs", "")[:50] + ("..." if len(e.get("obs", "")) > 50 else "")
            })
        df = pd.DataFrame(df_eventos)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### 📄 Relatório Mensal PDF")
    
    mes_selecionado = st.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
    ano_selecionado = st.number_input("Ano", min_value=2020, max_value=2030, value=datetime.now().year)
    
    meses_num = {
        "Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04",
        "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08",
        "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"
    }
    
    if st.button("📄 EMITIR RELATÓRIO PDF", use_container_width=True):
        pdf = gerar_pdf_eventos(eventos, meses_num[mes_selecionado], ano_selecionado)
        st.download_button("📥 BAIXAR PDF", pdf, file_name=f"eventos_{mes_selecionado}_{ano_selecionado}.pdf", mime="application/pdf", use_container_width=True)

# ========== TELA 4 - LOGS ==========
elif menu == "📜 LOGS":
    st.subheader("📜 Histórico de Movimentações (Logs)")
    
    logs = carregar_logs()
    
    if logs:
        df_logs = []
        for log in logs[::-1][:500]:  # Últimos 500 registros, mais recentes primeiro
            df_logs.append({
                "📅 Data/Hora": log.get("data", ""),
                "⚡ Ação": log.get("acao", ""),
                "💊 Vacina": log.get("vacina", ""),
                "🔢 Lote": log.get("lote", ""),
                "📦 Quantidade": log.get("quantidade", 0),
                "📝 Observação": log.get("observacao", "")[:50] + ("..." if len(log.get("observacao", "")) > 50 else "")
            })
        df = pd.DataFrame(df_logs)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum registro encontrado ainda. Realize movimentações para gerar logs.")
    
    if st.button("🔄 ATUALIZAR", use_container_width=True):
        st.rerun()

# ========== TELA 5 - SOBRE ==========
else:
    st.subheader("ℹ️ Sobre o Sistema")
    st.markdown("""
    ---
    **💉 SISTEMA DE ESTOQUE - VACINAS SUS**
    
    **Versão Web 2.0** - Completa
    
    **Funcionalidades:**
    - ✅ Tela 1: Vacinas EM USO com PDF
    - ✅ Tela 2: Estoque completo (Fabricante, Fabricação, Recebimento) com PDF
    - ✅ Tela 3: Eventos com relatório mensal em PDF
    - ✅ Tela 4: Logs de todas as movimentações
    - ✅ Interface responsiva com cores personalizadas
    
    **Dados salvos em:**
    - `vacinas.json` - Cadastro de vacinas
    - `eventos.json` - Registro de eventos
    - `logs.json` - Histórico de movimentações
    
    ---
    """)

# Salva dados ao sair
def salvar_tudo():
    salvar_dados(dados)
    salvar_eventos(eventos)

import atexit
atexit.register(salvar_tudo)