import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import sys
from datetime import datetime, timedelta

# Configuração
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_data_file(filename):
    if getattr(sys, 'frozen', False):
        data_dir = os.path.join(os.path.expanduser("~"), "SistemaVacinas")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return os.path.join(data_dir, filename)
    return filename

ARQUIVO = get_data_file("vacinas.json")
HISTORICO_ARQUIVO = get_data_file("historico_vacinas.json")
TEMA_ARQUIVO = get_data_file("tema.json")

class ControleVacinas:
    
    # ========== BIBLIOTECA DE TEMAS ==========
    TEMAS = {
        "Roxo/Lilás": {
            "bg_janela": "#F3E5F5",
            "bg_titulo": "#4A148C",
            "fg_titulo": "#FFFFFF",
            "bg_aba1": "#E1BEE7",
            "bg_aba2": "#F8BBD0",
            "bg_resumo": "#D1C4E9",
            "fg_resumo": "#000000",
            "bg_lista": "#F3E5F5",
            "fg_lista": "#000000",
            "bg_campos": "#FFFFFF",
            "botao_principal": "#6A1B9A",
            "botao_sucesso": "#AD1457",
            "botao_alerta": "#D81B60",
            "botao_info": "#9C27B0",
            "botao_entrada": "#4A148C",
            "botao_saida": "#AD1457",
        },
    }
    
    tema_atual = "Roxo/Lilás"
    
    def __init__(self):
        self.vacinas = self.carregar_dados()
        self.historico = self.carregar_historico()
        
        self.janela = tk.Tk()
        self.janela.title("Sistema de Estoque - Vacinas SUS")
        
        # Janela ocupa MEIA TELA
        largura = self.janela.winfo_screenwidth() // 2
        altura = int(self.janela.winfo_screenheight() // 1.5)
        x = (self.janela.winfo_screenwidth() - largura) // 2
        y = int((self.janela.winfo_screenheight() - altura) // 2)
        self.janela.geometry(f"{int(largura)}x{int(altura)}+{int(x)}+{int(y)}")
        self.janela.minsize(500, 600)
        
        try:
            icon_path = resource_path("vacina.ico")
            if os.path.exists(icon_path):
                self.janela.iconbitmap(icon_path)
        except:
            pass
        
        self.criar_interface()
        self.atualizar_lista_principal()
        self.atualizar_lista_estoque()
        self.carregar_tema_salvo()
    
    def carregar_tema_salvo(self):
        try:
            if os.path.exists(TEMA_ARQUIVO):
                with open(TEMA_ARQUIVO, "r", encoding="utf-8") as f:
                    tema_salvo = json.load(f)
                    if tema_salvo.get("tema") in self.TEMAS:
                        self.tema_atual = tema_salvo["tema"]
                        self.janela.after(100, lambda: self.aplicar_tema(self.tema_atual))
        except:
            pass
    
    def aplicar_tema(self, tema_nome):
        if tema_nome not in self.TEMAS:
            return
        tema = self.TEMAS[tema_nome]
        self.tema_atual = tema_nome
        self.janela.configure(bg=tema["bg_janela"])
        
        # Atualiza título
        for widget in self.janela.winfo_children():
            if isinstance(widget, tk.Frame):
                for sub in widget.winfo_children():
                    if isinstance(sub, tk.Label) and "SISTEMA DE ESTOQUE" in sub.cget("text"):
                        sub.configure(bg=tema["bg_titulo"], fg=tema["fg_titulo"])
                        widget.configure(bg=tema["bg_titulo"])
        
        # Atualiza abas
        for widget in self.janela.winfo_children():
            if isinstance(widget, ttk.Notebook):
                # Aba 1
                aba1 = widget.children.get("!frame")
                if aba1:
                    aba1.configure(bg=tema["bg_aba1"])
                    for frame in aba1.winfo_children():
                        if isinstance(frame, tk.Frame):
                            if frame.cget("relief") == "ridge":
                                frame.configure(bg=tema["bg_resumo"])
                                for label in frame.winfo_children():
                                    if isinstance(label, tk.Label):
                                        label.configure(bg=tema["bg_resumo"], fg=tema["fg_resumo"])
                            elif frame.cget("relief") == "groove":
                                frame.configure(bg=tema["bg_campos"])
                                for campo in frame.winfo_children():
                                    if isinstance(campo, tk.Label):
                                        campo.configure(bg=tema["bg_campos"], fg="#000000")
                                    elif isinstance(campo, tk.Frame):
                                        campo.configure(bg=tema["bg_campos"])
                                        for btn in campo.winfo_children():
                                            if isinstance(btn, tk.Button):
                                                texto = btn.cget("text")
                                                if "COPIAR" in texto:
                                                    btn.configure(bg=tema["botao_principal"])
                                                elif "ATUALIZAR" in texto:
                                                    btn.configure(bg=tema["botao_info"])
                                                elif "LIMPAR" in texto:
                                                    btn.configure(bg=tema["botao_alerta"])
                            else:
                                frame.configure(bg=tema["bg_lista"])
                                for lista in frame.winfo_children():
                                    if isinstance(lista, tk.Listbox):
                                        lista.configure(bg=tema["bg_lista"], fg=tema["fg_lista"])
                
                # Aba 2
                aba2 = widget.children.get("!frame2")
                if aba2:
                    aba2.configure(bg=tema["bg_aba2"])
                    for frame in aba2.winfo_children():
                        if isinstance(frame, tk.Frame):
                            if frame.cget("relief") == "groove":
                                frame.configure(bg=tema["bg_campos"])
                                for campo in frame.winfo_children():
                                    if isinstance(campo, tk.Label):
                                        campo.configure(bg=tema["bg_campos"], fg="#000000")
                                    elif isinstance(campo, tk.Frame):
                                        campo.configure(bg=tema["bg_campos"])
                                        for linha in campo.winfo_children():
                                            if isinstance(linha, tk.Frame):
                                                linha.configure(bg=tema["bg_campos"])
                                                for btn in linha.winfo_children():
                                                    if isinstance(btn, tk.Button):
                                                        texto = btn.cget("text")
                                                        if "ADICIONAR" in texto:
                                                            btn.configure(bg=tema["botao_sucesso"])
                                                        elif "REMOVER" in texto:
                                                            btn.configure(bg=tema["botao_alerta"])
                                                        elif "ATIVAR" in texto:
                                                            btn.configure(bg=tema["botao_principal"])
                                                        elif "ENTRADA" in texto:
                                                            btn.configure(bg=tema["botao_entrada"])
                                                        elif "BAIXA" in texto:
                                                            btn.configure(bg=tema["botao_saida"])
                                                        elif "ATUALIZAR DADOS" in texto:
                                                            btn.configure(bg=tema["botao_info"])
        
        try:
            with open(TEMA_ARQUIVO, "w", encoding="utf-8") as f:
                json.dump({"tema": tema_nome}, f)
        except:
            pass
        
        if hasattr(self, 'tema_combo'):
            self.tema_combo.set(tema_nome)
    
    def carregar_dados(self):
        try:
            if os.path.exists(ARQUIVO):
                with open(ARQUIVO, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                if dados and isinstance(dados, dict):
                    return dados
        except:
            pass
        
        hoje = datetime.now()
        return {
            "covid_a123": {
                "nome": "COVID-19", 
                "lote": "A123", 
                "quantidade": 150, 
                "minimo": 50, 
                "fabricacao": (hoje - timedelta(days=30)).strftime("%d/%m/%Y"),
                "validade": (hoje + timedelta(days=180)).strftime("%d/%m/%Y"), 
                "em_uso": True
            },
            "influenza_b456": {
                "nome": "Influenza", 
                "lote": "B456", 
                "quantidade": 200, 
                "minimo": 80, 
                "fabricacao": (hoje - timedelta(days=15)).strftime("%d/%m/%Y"),
                "validade": (hoje + timedelta(days=120)).strftime("%d/%m/%Y"), 
                "em_uso": True
            },
            "hepatite_c789": {
                "nome": "Hepatite B", 
                "lote": "C789", 
                "quantidade": 100, 
                "minimo": 30, 
                "fabricacao": (hoje - timedelta(days=60)).strftime("%d/%m/%Y"),
                "validade": (hoje + timedelta(days=365)).strftime("%d/%m/%Y"), 
                "em_uso": True
            },
        }
    
    def carregar_historico(self):
        try:
            if os.path.exists(HISTORICO_ARQUIVO):
                with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def salvar_dados(self):
        try:
            with open(ARQUIVO, "w", encoding="utf-8") as f:
                json.dump(self.vacinas, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
            return False
    
    def salvar_historico(self, acao, nome, lote, quantidade, obs=""):
        registro = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "acao": acao,
            "vacina": nome,
            "lote": lote,
            "quantidade": quantidade,
            "observacao": obs
        }
        self.historico.append(registro)
        if len(self.historico) > 100:
            self.historico = self.historico[-100:]
        try:
            with open(HISTORICO_ARQUIVO, "w", encoding="utf-8") as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def gerar_id(self, nome, lote):
        return f"{nome}_{lote}".replace(" ", "_").lower()
    
    def verificar_validade(self, data_str):
        try:
            data_val = datetime.strptime(data_str, "%d/%m/%Y")
            hoje = datetime.now()
            dias = (data_val - hoje).days
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
    
    def get_vacinas_em_uso(self):
        return [dados for dados in self.vacinas.values() if isinstance(dados, dict) and dados.get("em_uso", False)]
    
    def get_nomes_em_uso(self):
        return list(set([dados["nome"] for dados in self.vacinas.values() if isinstance(dados, dict) and dados.get("em_uso", False)]))
    
    # ========== AUTOCOMPLETE ==========
    def criar_autocomplete(self, entry, lista_completa, is_principal=True):
        listbox = tk.Listbox(self.janela, font=("Arial", 11), bg="white", fg="black", selectbackground="#9C27B0", height=6)
        
        def atualizar(event=None):
            texto = entry.get().upper()
            if not texto:
                listbox.place_forget()
                return
            sugestoes = [item for item in lista_completa if texto in item.upper()]
            if sugestoes:
                listbox.delete(0, tk.END)
                for item in sugestoes[:8]:
                    listbox.insert(tk.END, item)
                x = entry.winfo_rootx() - self.janela.winfo_rootx()
                y = entry.winfo_rooty() - self.janela.winfo_rooty()
                listbox.place(x=x, y=y + entry.winfo_height(), width=entry.winfo_width())
            else:
                listbox.place_forget()
        
        def selecionar(event=None):
            if listbox.curselection():
                nome = listbox.get(listbox.curselection())
                entry.delete(0, tk.END)
                entry.insert(0, nome)
                listbox.place_forget()
                
                if is_principal:
                    for dados in self.vacinas.values():
                        if isinstance(dados, dict) and dados.get("em_uso", False):
                            if dados["nome"].upper() == nome.upper():
                                self.entrada_lote_principal.delete(0, tk.END)
                                self.entrada_lote_principal.insert(0, dados["lote"])
                                break
                entry.focus()
        
        def fechar(event=None):
            listbox.place_forget()
        
        entry.bind("<KeyRelease>", atualizar)
        entry.bind("<FocusOut>", fechar)
        listbox.bind("<ButtonRelease-1>", selecionar)
        entry.bind("<Down>", lambda e: listbox.focus_set() if listbox.winfo_ismapped() else None)
        listbox.bind("<Return>", selecionar)
        listbox.bind("<Escape>", lambda e: listbox.place_forget())
        return listbox
    
    def atualizar_sugestoes_principal(self):
        if hasattr(self, 'lista_sugestoes_principal'):
            self.lista_sugestoes_principal = self.criar_autocomplete(self.entrada_nome_principal, self.get_nomes_em_uso(), True)
    
    # ========== INTERFACE ==========
    def criar_interface(self):
        tema = self.TEMAS[self.tema_atual]
        
        # Título
        titulo = tk.Frame(self.janela, bg=tema["bg_titulo"])
        titulo.pack(fill="x")
        tk.Label(titulo, text="💉 SISTEMA DE ESTOQUE - VACINAS SUS", font=("Arial", 18, "bold"), bg=tema["bg_titulo"], fg=tema["fg_titulo"], pady=15).pack()
        
        if getattr(sys, 'frozen', False):
            tk.Label(titulo, text=f"Dados: {os.path.expanduser('~')}\\SistemaVacinas", font=("Arial", 8), bg=tema["bg_titulo"], fg="#E1BEE7").pack()
        
        # Abas
        notebook = ttk.Notebook(self.janela)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        frame_principal = tk.Frame(notebook, bg=tema["bg_aba1"])
        notebook.add(frame_principal, text="💉 VACINAS EM USO")
        
        frame_estoque = tk.Frame(notebook, bg=tema["bg_aba2"])
        notebook.add(frame_estoque, text="📊 ESTOQUE")
        
        frame_historico = tk.Frame(notebook, bg="white")
        notebook.add(frame_historico, text="📜 HISTÓRICO")
        
        frame_sobre = tk.Frame(notebook, bg="white")
        notebook.add(frame_sobre, text="ℹ️ SOBRE")
        
        # ========== ABA PRINCIPAL ==========
        resumo = tk.Frame(frame_principal, bg=tema["bg_resumo"], relief="ridge", bd=2)
        resumo.pack(fill="x", padx=10, pady=10)
        
        self.total_label = tk.Label(resumo, text="Total: 0 vacinas em uso", font=("Arial", 11, "bold"), bg=tema["bg_resumo"], fg=tema["fg_resumo"])
        self.total_label.pack(side="left", padx=10, pady=5)
        
        self.estoque_total_label = tk.Label(resumo, text="Estoque Total: 0 und", font=("Arial", 11, "bold"), bg=tema["bg_resumo"], fg=tema["fg_resumo"])
        self.estoque_total_label.pack(side="right", padx=10, pady=5)
        
        list_frame = tk.Frame(frame_principal, bg=tema["bg_lista"])
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scroll = tk.Scrollbar(list_frame)
        scroll.pack(side="right", fill="y")
        
        self.lista_principal = tk.Listbox(list_frame, font=("Arial", 14, "bold"), bg=tema["bg_lista"], fg=tema["fg_lista"], yscrollcommand=scroll.set, selectmode=tk.SINGLE, activestyle="none", height=10)
        self.lista_principal.pack(fill="both", expand=True, side="left")
        scroll.config(command=self.lista_principal.yview)
        
        self.lista_principal.bind("<<ListboxSelect>>", self.preencher_campos_principal)
        self.lista_principal.bind("<Double-Button-1>", lambda e: self.copiar_lote_principal())
        
        campos = tk.Frame(frame_principal, bg=tema["bg_campos"], relief="groove", bd=2)
        campos.pack(fill="x", padx=10, pady=10)
        
        tk.Label(campos, text="💊 Nome da Vacina:", font=("Arial", 11, "bold"), bg=tema["bg_campos"], fg="#000000").pack(anchor="w", padx=5)
        self.entrada_nome_principal = tk.Entry(campos, font=("Arial", 13), relief="solid", bd=1)
        self.entrada_nome_principal.pack(fill="x", padx=5, pady=(0, 8))
        self.lista_sugestoes_principal = self.criar_autocomplete(self.entrada_nome_principal, self.get_nomes_em_uso(), True)
        
        tk.Label(campos, text="🔢 Lote:", font=("Arial", 11, "bold"), bg=tema["bg_campos"], fg="#000000").pack(anchor="w", padx=5)
        self.entrada_lote_principal = tk.Entry(campos, font=("Arial", 13), relief="solid", bd=1)
        self.entrada_lote_principal.pack(fill="x", padx=5, pady=(0, 8))
        
        botoes = tk.Frame(campos, bg=tema["bg_campos"])
        botoes.pack(fill="x", padx=5, pady=10)
        
        botoes_config = [
            ("📋 COPIAR LOTE", tema["botao_principal"], self.copiar_lote_principal),
            ("🔄 ATUALIZAR", tema["botao_info"], self.atualizar_lote_principal),
            ("🧹 LIMPAR", tema["botao_alerta"], self.limpar_campos_principal),
        ]
        
        for texto, cor, cmd in botoes_config:
            btn = tk.Button(botoes, text=texto, font=("Arial", 11, "bold"), bg=cor, fg="white", command=cmd, height=2, padx=10)
            btn.pack(side="left", expand=True, fill="both", padx=2, pady=2)
        
        # ========== ABA ESTOQUE ==========
        estoque_frame = tk.Frame(frame_estoque, bg=tema["bg_campos"])
        estoque_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        list_estoque_frame = tk.Frame(estoque_frame, bg=tema["bg_lista"])
        list_estoque_frame.pack(fill="both", expand=True, pady=5)
        
        scroll_est = tk.Scrollbar(list_estoque_frame)
        scroll_est.pack(side="right", fill="y")
        
        self.lista_estoque = tk.Listbox(list_estoque_frame, font=("Arial", 11), bg=tema["bg_lista"], fg=tema["fg_lista"], yscrollcommand=scroll_est.set, selectmode=tk.SINGLE, height=12)
        self.lista_estoque.pack(fill="both", expand=True, side="left")
        scroll_est.config(command=self.lista_estoque.yview)
        
        self.lista_estoque.bind("<<ListboxSelect>>", self.preencher_campos_estoque)
        
        campos_est = tk.Frame(estoque_frame, bg=tema["bg_campos"], relief="groove", bd=2)
        campos_est.pack(fill="x", pady=10)
        
        tk.Label(campos_est, text="💊 Vacina:", font=("Arial", 10, "bold"), bg=tema["bg_campos"], fg="#000000").pack(anchor="w", padx=5)
        self.entrada_nome_est = tk.Entry(campos_est, font=("Arial", 12), relief="solid", bd=1)
        self.entrada_nome_est.pack(fill="x", padx=5, pady=(0, 5))
        
        tk.Label(campos_est, text="🔢 Lote:", font=("Arial", 10, "bold"), bg=tema["bg_campos"], fg="#000000").pack(anchor="w", padx=5)
        self.entrada_lote_est = tk.Entry(campos_est, font=("Arial", 12), relief="solid", bd=1)
        self.entrada_lote_est.pack(fill="x", padx=5, pady=(0, 5))
        
        # DATA DE FABRICAÇÃO
        tk.Label(campos_est, text="🏭 Data de Fabricação (DD/MM/AAAA):", font=("Arial", 10, "bold"), bg=tema["bg_campos"], fg="#000000").pack(anchor="w", padx=5)
        self.entrada_fabricacao_est = tk.Entry(campos_est, font=("Arial", 12), relief="solid", bd=1)
        self.entrada_fabricacao_est.pack(fill="x", padx=5, pady=(0, 5))
        
        # DATA DE VALIDADE
        tk.Label(campos_est, text="📅 Data de Validade (DD/MM/AAAA):", font=("Arial", 10, "bold"), bg=tema["bg_campos"], fg="#000000").pack(anchor="w", padx=5)
        self.entrada_validade_est = tk.Entry(campos_est, font=("Arial", 12), relief="solid", bd=1)
        self.entrada_validade_est.pack(fill="x", padx=5, pady=(0, 5))
        
        qtde_frame = tk.Frame(campos_est, bg=tema["bg_campos"])
        qtde_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(qtde_frame, text="📊 Quantidade:", font=("Arial", 10, "bold"), bg=tema["bg_campos"], fg="#000000").pack(side="left")
        self.entrada_quantidade_est = tk.Entry(qtde_frame, font=("Arial", 12), relief="solid", bd=1, width=10)
        self.entrada_quantidade_est.pack(side="left", padx=(10, 0))
        
        tk.Label(qtde_frame, text="⚠️ Mínimo:", font=("Arial", 10, "bold"), bg=tema["bg_campos"], fg="#000000").pack(side="left", padx=(20, 0))
        self.entrada_minimo_est = tk.Entry(qtde_frame, font=("Arial", 12), relief="solid", bd=1, width=10)
        self.entrada_minimo_est.pack(side="left", padx=(10, 0))
        
        botoes_est = tk.Frame(campos_est, bg=tema["bg_campos"])
        botoes_est.pack(fill="x", padx=5, pady=10)
        
        linha1 = tk.Frame(botoes_est, bg=tema["bg_campos"])
        linha1.pack(fill="x", pady=2)
        
        tk.Button(linha1, text="➕ ADICIONAR", font=("Arial", 10, "bold"), bg=tema["botao_sucesso"], fg="white", command=self.adicionar_lote, height=1).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(linha1, text="🗑️ REMOVER", font=("Arial", 10, "bold"), bg=tema["botao_alerta"], fg="white", command=self.remover_lote, height=1).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(linha1, text="⭐ ATIVAR", font=("Arial", 10, "bold"), bg=tema["botao_principal"], fg="white", command=self.ativar_lote, height=1).pack(side="left", expand=True, fill="x", padx=2)
        
        linha2 = tk.Frame(botoes_est, bg=tema["bg_campos"])
        linha2.pack(fill="x", pady=2)
        
        tk.Button(linha2, text="📥 ENTRADA", font=("Arial", 10, "bold"), bg=tema["botao_entrada"], fg="white", command=self.entrada_estoque, height=1).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(linha2, text="📤 BAIXA", font=("Arial", 10, "bold"), bg=tema["botao_saida"], fg="white", command=self.dar_baixa, height=1).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(linha2, text="🔄 ATUALIZAR DADOS", font=("Arial", 10, "bold"), bg=tema["botao_info"], fg="white", command=self.atualizar_dados_lote, height=1).pack(side="left", expand=True, fill="x", padx=2)
        
        # ========== ABA HISTÓRICO ==========
        hist_frame = tk.Frame(frame_historico)
        hist_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        hist_scroll = tk.Scrollbar(hist_frame)
        hist_scroll.pack(side="right", fill="y")
        
        self.lista_historico = tk.Listbox(hist_frame, font=("Arial", 10), yscrollcommand=hist_scroll.set, height=20)
        self.lista_historico.pack(fill="both", expand=True, side="left")
        hist_scroll.config(command=self.lista_historico.yview)
        
        tk.Button(frame_historico, text="🔄 ATUALIZAR HISTÓRICO", font=("Arial", 11, "bold"), bg=tema["botao_principal"], fg="white", command=self.atualizar_historico).pack(pady=10)
        
        # ========== ABA SOBRE ==========
        info = """
💉 SISTEMA DE ESTOQUE - VACINAS SUS

Versão: 5.0

Funcionalidades:
✅ Vacinas EM USO na primeira tela
✅ Múltiplos lotes para mesma vacina
✅ Ativar lote para uso
✅ Controle de validade
✅ Controle de fabricação
✅ Entrada e saída de estoque
✅ Histórico completo
✅ Sistema de Temas

Dados salvos em:
📁 Usuário > SistemaVacinas
        """
        tk.Label(frame_sobre, text=info, font=("Consolas", 10), bg="white", justify="left", padx=20, pady=20).pack()
        
        # Seletor de temas
        tk.Label(frame_sobre, text="🎨 ESCOLHA UM TEMA:", font=("Arial", 12, "bold"), bg="white", fg="#000000").pack(pady=(10, 5))
        
        self.tema_combo = ttk.Combobox(frame_sobre, textvariable=tk.StringVar(value=self.tema_atual), values=list(self.TEMAS.keys()), font=("Arial", 11), state="readonly", width=20)
        self.tema_combo.pack(pady=5)
        
        def mudar_tema():
            self.aplicar_tema(self.tema_combo.get())
        
        tk.Button(frame_sobre, text="🎨 APLICAR TEMA", font=("Arial", 11, "bold"), bg="#1976D2", fg="white", command=mudar_tema, height=1, padx=20).pack(pady=10)
        
        # Rodapé alertas
        alerta_frame = tk.Frame(self.janela, bg="#FFF3E0", relief="ridge", bd=2)
        alerta_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.alerta_label = tk.Label(alerta_frame, text="✅ Sistema OK", font=("Arial", 10), bg="#FFF3E0", fg="#000000", wraplength=550)
        self.alerta_label.pack(pady=5)
    
    # ========== MÉTODOS PRIMEIRA TELA ==========
    def atualizar_lista_principal(self):
        self.lista_principal.delete(0, tk.END)
        em_uso = self.get_vacinas_em_uso()
        
        for i, dados in enumerate(sorted(em_uso, key=lambda x: x["nome"])):
            texto = f"{dados['nome']}   |   Lote: {dados['lote']}"
            self.lista_principal.insert(tk.END, texto)
            cor_fundo = "#FFFFFF" if i % 2 == 0 else "#E3F2FD"
            self.lista_principal.itemconfig(i, bg=cor_fundo, fg="#000000")
        
        total = len(em_uso)
        total_estoque = sum(d.get("quantidade", 0) for d in em_uso if isinstance(d, dict))
        self.total_label.config(text=f"Total: {total} vacinas em uso")
        self.estoque_total_label.config(text=f"Estoque Total: {total_estoque} und")
        
        self.atualizar_sugestoes_principal()
        self.verificar_alertas()
    
    def preencher_campos_principal(self, event=None):
        sel = self.lista_principal.curselection()
        if sel:
            texto = self.lista_principal.get(sel[0])
            nome = texto.split("|")[0].strip()
            
            for dados in self.vacinas.values():
                if isinstance(dados, dict) and dados["nome"] == nome and dados.get("em_uso", False):
                    self.entrada_nome_principal.delete(0, tk.END)
                    self.entrada_nome_principal.insert(0, nome)
                    self.entrada_lote_principal.delete(0, tk.END)
                    self.entrada_lote_principal.insert(0, dados["lote"])
                    break
    
    def copiar_lote_principal(self):
        sel = self.lista_principal.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma vacina!")
            return
        texto = self.lista_principal.get(sel[0])
        lote = texto.split("Lote:")[1].strip()
        self.janela.clipboard_clear()
        self.janela.clipboard_append(lote)
        messagebox.showinfo("Sucesso", f"Lote '{lote}' copiado!")
    
    def atualizar_lote_principal(self):
        nome = self.entrada_nome_principal.get().strip().upper()
        novo_lote = self.entrada_lote_principal.get().strip().upper()
        
        if not nome or not novo_lote:
            messagebox.showerror("Erro", "Preencha nome e lote!")
            return
        
        id_atual = None
        for id_lote, dados in self.vacinas.items():
            if isinstance(dados, dict) and dados.get("em_uso", False):
                if dados["nome"].upper() == nome:
                    id_atual = id_lote
                    break
        
        if not id_atual:
            disponiveis = []
            for dados in self.vacinas.values():
                if isinstance(dados, dict) and dados.get("em_uso", False):
                    disponiveis.append(f"{dados['nome']} (Lote: {dados['lote']})")
            msg = f"Vacina '{nome}' não encontrada em uso!\n\nVacinas disponíveis:\n" + "\n".join(disponiveis)
            messagebox.showerror("Erro", msg)
            return
        
        novo_id = self.gerar_id(nome, novo_lote)
        hoje = datetime.now()
        
        if novo_id in self.vacinas:
            self.vacinas[novo_id]["em_uso"] = True
            self.vacinas[id_atual]["em_uso"] = False
            messagebox.showinfo("Sucesso", f"Lote alterado para '{novo_lote}'!")
        else:
            self.vacinas[novo_id] = {
                "nome": nome,
                "lote": novo_lote,
                "quantidade": 0,
                "minimo": 30,
                "fabricacao": hoje.strftime("%d/%m/%Y"),
                "validade": (hoje + timedelta(days=365)).strftime("%d/%m/%Y"),
                "em_uso": True
            }
            self.vacinas[id_atual]["em_uso"] = False
            messagebox.showinfo("Sucesso", f"Novo lote '{novo_lote}' criado e ativado!")
        
        self.salvar_dados()
        self.salvar_historico("ALTERAÇÃO LOTE", nome, novo_lote, 0, f"Lote ativado: {novo_lote}")
        self.atualizar_lista_principal()
        self.atualizar_lista_estoque()
        self.limpar_campos_principal()
    
    def limpar_campos_principal(self):
        self.entrada_nome_principal.delete(0, tk.END)
        self.entrada_lote_principal.delete(0, tk.END)
        self.entrada_nome_principal.focus_force()
        self.lista_principal.selection_clear(0, tk.END)
    
    # ========== MÉTODOS ABA ESTOQUE ==========
    def atualizar_lista_estoque(self):
        self.lista_estoque.delete(0, tk.END)
        itens_validos = [(id_lote, dados) for id_lote, dados in self.vacinas.items() if isinstance(dados, dict)]
        
        for i, (id_lote, dados) in enumerate(sorted(itens_validos, key=lambda x: x[1]["nome"])):
            status = "⭐ EM USO" if dados.get("em_uso", False) else "⚪"
            fabricacao = dados.get("fabricacao", "N/A")
            validade = dados.get("validade", "N/A")
            validade_status, _ = self.verificar_validade(validade)
            
            texto = f"{dados['nome']}   |   Lote: {dados['lote']}   |   Estoque: {dados['quantidade']}   |   Fab: {fabricacao}   |   Val: {validade}   |   {validade_status}   |   {status}"
            self.lista_estoque.insert(tk.END, texto)
            
            if "VENCIDA" in validade_status:
                self.lista_estoque.itemconfig(i, fg="#D32F2F")
            elif dados.get("em_uso", False):
                self.lista_estoque.itemconfig(i, fg="#0000CD")
            else:
                self.lista_estoque.itemconfig(i, fg="#666666")
    
    def preencher_campos_estoque(self, event=None):
        sel = self.lista_estoque.curselection()
        if sel:
            texto = self.lista_estoque.get(sel[0])
            partes = texto.split("|")
            nome = partes[0].strip()
            lote = partes[1].split("Lote:")[1].strip()
            
            for id_lote, dados in self.vacinas.items():
                if isinstance(dados, dict) and dados["nome"] == nome and dados["lote"] == lote:
                    self.entrada_nome_est.delete(0, tk.END)
                    self.entrada_nome_est.insert(0, nome)
                    self.entrada_lote_est.delete(0, tk.END)
                    self.entrada_lote_est.insert(0, lote)
                    self.entrada_fabricacao_est.delete(0, tk.END)
                    self.entrada_fabricacao_est.insert(0, dados.get("fabricacao", ""))
                    self.entrada_validade_est.delete(0, tk.END)
                    self.entrada_validade_est.insert(0, dados.get("validade", ""))
                    self.entrada_quantidade_est.delete(0, tk.END)
                    self.entrada_quantidade_est.insert(0, dados.get("quantidade", 0))
                    self.entrada_minimo_est.delete(0, tk.END)
                    self.entrada_minimo_est.insert(0, dados.get("minimo", 30))
                    self.id_selecionado = id_lote
                    break
    
    def adicionar_lote(self):
        nome = self.entrada_nome_est.get().strip().upper()
        lote = self.entrada_lote_est.get().strip().upper()
        fabricacao = self.entrada_fabricacao_est.get().strip()
        validade = self.entrada_validade_est.get().strip()
        
        try:
            quantidade = int(self.entrada_quantidade_est.get().strip())
            minimo = int(self.entrada_minimo_est.get().strip()) if self.entrada_minimo_est.get().strip() else 30
        except:
            messagebox.showerror("Erro", "Quantidade deve ser número!")
            return
        
        if not nome or not lote:
            messagebox.showerror("Erro", "Preencha nome e lote!")
            return
        
        if not fabricacao:
            messagebox.showerror("Erro", "Preencha a data de fabricação!")
            return
        
        if not validade:
            messagebox.showerror("Erro", "Preencha a data de validade!")
            return
        
        try:
            datetime.strptime(fabricacao, "%d/%m/%Y")
            datetime.strptime(validade, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Datas inválidas! Use DD/MM/AAAA")
            return
        
        novo_id = self.gerar_id(nome, lote)
        
        if novo_id in self.vacinas:
            messagebox.showerror("Erro", f"Lote '{lote}' já existe para vacina '{nome}'!")
            return
        
        self.vacinas[novo_id] = {
            "nome": nome,
            "lote": lote,
            "quantidade": quantidade,
            "minimo": minimo,
            "fabricacao": fabricacao,
            "validade": validade,
            "em_uso": False
        }
        
        self.salvar_historico("ADICIONAR LOTE", nome, lote, quantidade, f"Fab: {fabricacao}, Val: {validade}")
        self.salvar_dados()
        self.atualizar_lista_estoque()
        self.limpar_campos_estoque()
        messagebox.showinfo("Sucesso", f"Lote '{lote}' adicionado!")
    
    def remover_lote(self):
        if not hasattr(self, 'id_selecionado') or not self.id_selecionado:
            messagebox.showwarning("Aviso", "Selecione um lote na lista!")
            return
        
        dados = self.vacinas[self.id_selecionado]
        
        if dados.get("em_uso", False):
            messagebox.showerror("Erro", "Não é possível remover um lote que está EM USO!\nAtive outro lote primeiro.")
            return
        
        if messagebox.askyesno("Confirmar", f"Remover lote '{dados['lote']}' da vacina '{dados['nome']}'?"):
            self.salvar_historico("REMOVER LOTE", dados["nome"], dados["lote"], 0, "Lote removido")
            del self.vacinas[self.id_selecionado]
            self.salvar_dados()
            self.atualizar_lista_estoque()
            self.limpar_campos_estoque()
            messagebox.showinfo("Sucesso", "Lote removido!")
    
    def ativar_lote(self):
        if not hasattr(self, 'id_selecionado') or not self.id_selecionado:
            messagebox.showwarning("Aviso", "Selecione um lote na lista!")
            return
        
        dados = self.vacinas[self.id_selecionado]
        nome = dados["nome"]
        
        for id_lote, info in self.vacinas.items():
            if isinstance(info, dict) and info["nome"] == nome:
                info["em_uso"] = False
        
        self.vacinas[self.id_selecionado]["em_uso"] = True
        
        self.salvar_historico("ATIVAR LOTE", nome, dados["lote"], 0, "Lote ativado para uso")
        self.salvar_dados()
        self.atualizar_lista_principal()
        self.atualizar_lista_estoque()
        messagebox.showinfo("Sucesso", f"Lote '{dados['lote']}' da vacina '{nome}' está agora EM USO!")
    
    def entrada_estoque(self):
        self._movimentar_estoque('entrada')
    
    def dar_baixa(self):
        self._movimentar_estoque('saida')
    
    def _movimentar_estoque(self, tipo):
        if not hasattr(self, 'id_selecionado') or not self.id_selecionado:
            messagebox.showwarning("Aviso", "Selecione um lote na lista!")
            return
        
        dados = self.vacinas[self.id_selecionado]
        estoque_atual = dados["quantidade"]
        
        if tipo == 'saida' and estoque_atual <= 0:
            messagebox.showerror("Erro", "Estoque zerado!")
            return
        
        titulo = "ENTRADA" if tipo == 'entrada' else "BAIXA"
        cor = "#1565C0" if tipo == 'entrada' else "#F57C00"
        
        dialog = tk.Toplevel(self.janela)
        dialog.title(f"{titulo} - {dados['nome']} - Lote: {dados['lote']}")
        dialog.geometry("400x300")
        dialog.transient(self.janela)
        dialog.grab_set()
        
        main = tk.Frame(dialog, bg="white", padx=20, pady=20)
        main.pack(fill="both", expand=True)
        
        tk.Label(main, text=f"💉 {dados['nome']}", font=("Arial", 14, "bold"), bg="white", fg=cor).pack()
        tk.Label(main, text=f"Lote: {dados['lote']}", font=("Arial", 12), bg="white").pack()
        tk.Label(main, text=f"Estoque atual: {estoque_atual} und", font=("Arial", 12), bg="white").pack(pady=10)
        
        tk.Label(main, text=f"Quantidade a {'adicionar' if tipo == 'entrada' else 'retirar'}:", font=("Arial", 12)).pack(pady=10)
        entrada = tk.Entry(main, font=("Arial", 16), justify="center", width=10)
        entrada.pack(pady=5)
        entrada.focus()
        
        def confirmar():
            try:
                qtde = int(entrada.get())
                if qtde <= 0:
                    messagebox.showerror("Erro", "Quantidade positiva!")
                    return
                if tipo == 'saida' and qtde > estoque_atual:
                    messagebox.showerror("Erro", f"Quantidade insuficiente! Estoque: {estoque_atual}")
                    return
                
                if tipo == 'entrada':
                    dados["quantidade"] += qtde
                    acao = "ENTRADA"
                    msg = f"Adicionado {qtde} unidades"
                else:
                    dados["quantidade"] -= qtde
                    acao = "BAIXA"
                    msg = f"Retirado {qtde} unidades"
                
                self.salvar_historico(acao, dados["nome"], dados["lote"], qtde, msg)
                self.salvar_dados()
                self.atualizar_lista_principal()
                self.atualizar_lista_estoque()
                messagebox.showinfo("Sucesso", f"{qtde} unidades movimentadas!\nNovo estoque: {dados['quantidade']}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Digite um número!")
        
        tk.Button(main, text=f"CONFIRMAR {titulo}", bg=cor, fg="white", font=("Arial", 12, "bold"), command=confirmar, height=2).pack(fill="x", pady=15)
        tk.Button(main, text="CANCELAR", bg="#CCC", command=dialog.destroy, height=1).pack(fill="x")
    
    def atualizar_dados_lote(self):
        if not hasattr(self, 'id_selecionado') or not self.id_selecionado:
            messagebox.showwarning("Aviso", "Selecione um lote na lista!")
            return
        
        dados = self.vacinas[self.id_selecionado]
        
        try:
            nova_qtde = int(self.entrada_quantidade_est.get().strip())
            novo_minimo = int(self.entrada_minimo_est.get().strip())
            nova_fabricacao = self.entrada_fabricacao_est.get().strip()
            nova_validade = self.entrada_validade_est.get().strip()
        except:
            messagebox.showerror("Erro", "Quantidade deve ser número!")
            return
        
        try:
            datetime.strptime(nova_fabricacao, "%d/%m/%Y")
            datetime.strptime(nova_validade, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Datas inválidas! Use DD/MM/AAAA")
            return
        
        dados["quantidade"] = nova_qtde
        dados["minimo"] = novo_minimo
        dados["fabricacao"] = nova_fabricacao
        dados["validade"] = nova_validade
        
        self.salvar_historico("ATUALIZAR DADOS", dados["nome"], dados["lote"], nova_qtde, f"Fab: {nova_fabricacao}, Val: {nova_validade}")
        self.salvar_dados()
        self.atualizar_lista_principal()
        self.atualizar_lista_estoque()
        messagebox.showinfo("Sucesso", "Dados atualizados!")
    
    def limpar_campos_estoque(self):
        self.entrada_nome_est.delete(0, tk.END)
        self.entrada_lote_est.delete(0, tk.END)
        self.entrada_fabricacao_est.delete(0, tk.END)
        self.entrada_validade_est.delete(0, tk.END)
        self.entrada_quantidade_est.delete(0, tk.END)
        self.entrada_minimo_est.delete(0, tk.END)
        self.id_selecionado = None
        self.lista_estoque.selection_clear(0, tk.END)
    
    # ========== MÉTODOS GERAIS ==========
    def verificar_alertas(self):
        alertas = []
        for dados in self.vacinas.values():
            if isinstance(dados, dict):
                q = dados.get("quantidade", 0)
                m = dados.get("minimo", 0)
                validade = dados.get("validade", "")
                
                if q <= m and q > 0:
                    alertas.append(f"⚠️ Estoque baixo - {dados['nome']} ({dados['lote']}): {q} und")
                elif q <= 0:
                    alertas.append(f"❌ ESGOTADO - {dados['nome']} ({dados['lote']})")
                
                status_val, _ = self.verificar_validade(validade)
                if "VENCE" in status_val or "VENCIDA" in status_val:
                    alertas.append(f"{status_val} - {dados['nome']} ({dados['lote']})")
        
        if alertas:
            texto = "🔔 ALERTAS:\n" + "\n".join(alertas[:4])
            if len(alertas) > 4:
                texto += f"\n... e mais {len(alertas)-4}"
            self.alerta_label.config(text=texto, fg="#D32F2F")
        else:
            self.alerta_label.config(text="✅ Sistema OK", fg="#2E7D32")
    
    def atualizar_historico(self):
        self.lista_historico.delete(0, tk.END)
        for reg in reversed(self.historico):
            texto = f"[{reg['data']}] {reg['acao']}: {reg['vacina']} - Lote: {reg['lote']} - {reg['quantidade']} und"
            if reg.get('observacao'):
                texto += f" ({reg['observacao']})"
            self.lista_historico.insert(tk.END, texto)
    
    def executar(self):
        self.atualizar_historico()
        self.janela.mainloop()

if __name__ == "__main__":
    app = ControleVacinas()
    app.executar()