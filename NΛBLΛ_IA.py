import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

# Importações do seu projeto existente
from config import DEFAULT_D_MAX, DEFAULT_EXCEL_PATH, DEFAULT_V_MAX
from src.orquestrador import AgenteNablaOrchestrator


class NablaGUI:

    def __init__(self, root):
        self.root = root
        self.root.title(
            "NΛBLΛ IA")
        self.root.geometry("900x700")
        self.root.minsize(750, 550)

        self.orquestrador = None

        # Estilo geral da aplicação
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self._build_ui()

    def _build_ui(self):
        # --- PAINEL LATERAL DE CONFIGURAÇÃO ---
        sidebar = ttk.Frame(self.root, padding=12)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(
            sidebar, text="⚙️ Parâmetros de Entrada", font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 10))

        # Categoria Excel
        ttk.Label(sidebar, text="Caminho do Arquivo Excel:").pack(
            anchor="w", pady=(5, 2)
        )
        self.excel_entry = ttk.Entry(sidebar, width=32)
        self.excel_entry.insert(0, str(DEFAULT_EXCEL_PATH))
        self.excel_entry.pack(anchor="w", pady=(0, 10))

        # Categoria Limite D_max
        ttk.Label(sidebar, text="Limite Deslocamento D_max (mm):").pack(
            anchor="w", pady=(5, 2)
        )
        self.dmax_entry = ttk.Entry(sidebar, width=32)
        self.dmax_entry.insert(0, str(DEFAULT_D_MAX))
        self.dmax_entry.pack(anchor="w", pady=(0, 10))

        # Categoria Limite V_max
        ttk.Label(sidebar, text="Limite Velocidade V_max (mm/s):").pack(
            anchor="w", pady=(5, 2)
        )
        self.vmax_entry = ttk.Entry(sidebar, width=32)
        self.vmax_entry.insert(0, str(DEFAULT_V_MAX))
        self.vmax_entry.pack(anchor="w", pady=(0, 15))

        # Botão de Inicialização
        self.btn_init = ttk.Button(
            sidebar,
            text="🚀 Inicializar Orquestrador",
            command=self._start_initialization,
        )
        self.btn_init.pack(fill=tk.X, ipady=4)

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=20)

        # Indicador de Status
        self.status_label = ttk.Label(
            sidebar,
            text="Status: Aguardando inicialização...",
            foreground="#6B7280",
            wraplength=220,
        )
        self.status_label.pack(anchor="w")

        # --- PAINEL PRINCIPAL DE CONVERSA ---
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(
            main_frame,
            text="NΛBLΛ IΛ",
            font=("TimesNewRoman", 20, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        # Área de visualização do chat
        self.chat_display = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, font=("Consolas", 10), state="disabled"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Estilização do texto
        self.chat_display.tag_config(
            "user", foreground="#1E40AF", font=("Consolas", 10, "bold")
        )
        self.chat_display.tag_config(
            "nabla", foreground="#07065F", font=("Consolas", 10)
        )
        self.chat_display.tag_config(
            "system", foreground="#4B5563", font=("Consolas", 9, "italic")
        )

        # Entrada de texto e botão
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X)

        self.query_entry = ttk.Entry(
            input_frame, font=("Arial", 10), state="disabled"
        )
        self.query_entry.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=4
        )
        self.query_entry.bind("<Return>", lambda event: self.send_query())

        self.btn_send = ttk.Button(
            input_frame, text="Enviar", command=self.send_query, state="disabled"
        )
        self.btn_send.pack(side=tk.RIGHT, ipady=2)

        self._append_text(
            "Sistema",
            # "Ajuste os parâmetros no painel à esquerda e clique em 'Inicializar"
            " Orquestrador'.",
            "system",
        )

    def _append_text(self, sender, message, tag):
        """Auxiliar para inserir mensagens no histórico."""
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"[{sender}]\n{message}\n\n", tag)
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)

    def _start_initialization(self):
        """Valida os dados de entrada e inicia a thread de carregamento."""
        excel_path = self.excel_entry.get().strip()
        try:
            d_max = float(self.dmax_entry.get().strip())
            v_max = float(self.vmax_entry.get().strip())
        except ValueError:
            messagebox.showerror(
                "Erro de Validação", "D_max e V_max devem ser valores numéricos."
            )
            return

        # Atualizar estado da UI
        self.btn_init.config(state="disabled")
        self.status_label.config(
            text="Status: Processando Excel e Base RAG...", foreground="#D97706"
        )
        self._append_text(
            "Sistema",
            "Inicializando Orquestrador Multi-Agente e Base RAG...",
            "system",
        )

        # Executa o orquestrador em thread paralela para não congelar a GUI
        threading.Thread(
            target=self._init_orchestrator_thread,
            args=(excel_path, d_max, v_max),
            daemon=True,
        ).start()

    def _init_orchestrator_thread(self, excel_path, d_max, v_max):
        try:
            # Instancia o orquestrador
            self.orquestrador = AgenteNablaOrchestrator(
                excel_path, d_max=d_max, v_max=v_max
            )

            # Consulta executiva inicial automática
            primeira_consulta = "Gere o relatório executivo formal com a análise estrutural e enquadramento normativo."
            resposta_inicial = self.orquestrador.responder_consulta(
                primeira_consulta)

            # Atualiza UI no fluxo principal
            self.root.after(
                0, self._on_init_success, primeira_consulta, resposta_inicial
            )
        except Exception as e:
            self.root.after(0, self._on_init_error, str(e))

    def _on_init_success(self, primeira_consulta, resposta_inicial):
        self.status_label.config(
            text="Status: Orquestrador Ativo", foreground="#059669"
        )
        self.query_entry.config(state="normal")
        self.btn_send.config(state="normal")

        self._append_text("Usuário", primeira_consulta, "user")
        self._append_text("Agente NΛBLΛ", resposta_inicial, "nabla")

    def _on_init_error(self, err_msg):
        self.btn_init.config(state="normal")
        self.status_label.config(
            text="Status: Erro na inicialização", foreground="#DC2626"
        )
        messagebox.showerror(
            "Erro de Inicialização", f"Falha ao carregar orquestrador:\n{err_msg}"
        )

    def send_query(self):
        query = self.query_entry.get().strip()
        if not query or not self.orquestrador:
            return

        self.query_entry.delete(0, tk.END)
        self.query_entry.config(state="disabled")
        self.btn_send.config(state="disabled")

        self._append_text("Usuário", query, "user")
        self.status_label.config(
            text="Status: NΛBLΛ processando...", foreground="#D97706"
        )

        # Processa a resposta em thread separada
        threading.Thread(
            target=self._process_query_thread, args=(query,), daemon=True
        ).start()

    def _process_query_thread(self, query):
        try:
            resposta = self.orquestrador.responder_consulta(query)
            self.root.after(0, self._on_query_success, resposta)
        except Exception as e:
            self.root.after(0, self._on_query_error, str(e))

    def _on_query_success(self, resposta):
        self._append_text("Agente NΛBLΛ", resposta, "nabla")
        self.status_label.config(
            text="Status: Orquestrador Ativo", foreground="#059669"
        )
        self.query_entry.config(state="normal")
        self.btn_send.config(state="normal")
        self.query_entry.focus()

    def _on_query_error(self, err_msg):
        self._append_text(
            "Sistema", f"Erro ao processar consulta: {err_msg}", "system")
        self.status_label.config(
            text="Status: Erro na consulta", foreground="#DC2626"
        )
        self.query_entry.config(state="normal")
        self.btn_send.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = NablaGUI(root)
    root.mainloop()
