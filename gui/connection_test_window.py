"""Ventana para probar la conexión a MySQL desde la interfaz gráfica."""

from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import Any, Callable, Dict, Optional

# Permite ejecutar el módulo directamente sin problemas de ruta
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.config import get_db_config, save_db_config
from database.database import DatabaseConnection


class ConnectionTestWindow:
    """Ventana modal para validar y guardar credenciales de MySQL."""

    # Colores y estilos
    COLORS = {
        "bg_main": "#f0f2f5",  # Gris muy claro para el fondo
        "bg_card": "#ffffff",  # Blanco para las tarjetas
        "primary": "#2196f3",  # Azul principal
        "primary_dark": "#1976d2",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "text_header": "#1a237e",
        "text_body": "#37474f",
        "text_muted": "#78909c",
        "border": "#e0e0e0",
    }

    def __init__(
        self,
        parent: tk.Tk | tk.Toplevel,
        on_config_saved: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Prueba de Conexión a Base de Datos")
        self.window.geometry("950x750")
        self.window.minsize(850, 650)
        self.window.transient(parent)
        self.window.configure(bg=self.COLORS["bg_main"])

        self._on_config_saved_callback = on_config_saved
        self.main_canvas: Optional[tk.Canvas] = None
        self.canvas_window_id: Optional[int] = None

        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._center_window()
        self._create_widgets()
        self._load_last_config()

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def _center_window(self) -> None:
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x_coord = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y_coord = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x_coord}+{y_coord}")

    def _on_closing(self) -> None:
        if self.main_canvas is not None:
            self.main_canvas.unbind_all("<MouseWheel>")
        self.window.destroy()

    def _create_widgets(self) -> None:
        # Contenedor principal con scroll
        container = tk.Frame(self.window, bg=self.COLORS["bg_main"])
        container.pack(fill="both", expand=True)

        self.main_canvas = tk.Canvas(
            container, bg=self.COLORS["bg_main"], highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=self.main_canvas.yview
        )
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame interno que contendrá todo (el "papel")
        self.content_frame = tk.Frame(
            self.main_canvas, bg=self.COLORS["bg_main"], padx=40, pady=40
        )

        # Crear la ventana dentro del canvas y guardar su ID
        self.canvas_window_id = self.main_canvas.create_window(
            (0, 0), window=self.content_frame, anchor="nw"
        )

        # Configurar eventos de redimensionamiento
        self.content_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            ),
        )
        self.main_canvas.bind("<Configure>", self._on_canvas_configure)
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # --- HEADER ---
        header_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg_main"])
        header_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            header_frame,
            text="Configuración de Conexión",
            font=("Segoe UI", 24, "bold"),
            bg=self.COLORS["bg_main"],
            fg=self.COLORS["text_header"],
        ).pack(anchor="w")

        self.status_indicator = tk.Label(
            header_frame,
            text="● Esperando prueba",
            font=("Segoe UI", 11),
            bg=self.COLORS["bg_main"],
            fg=self.COLORS["text_muted"],
        )
        self.status_indicator.pack(anchor="w", pady=(5, 0))

        # --- TARJETA DE PARÁMETROS ---
        self._create_params_card()

        # --- BOTONES DE ACCIÓN ---
        self._create_action_buttons()

        # --- TARJETA DE RESULTADOS ---
        self._create_results_card()

    def _on_canvas_configure(self, event: tk.Event) -> None:
        # Ajustar el ancho del frame interno al ancho del canvas
        if self.canvas_window_id:
            self.main_canvas.itemconfig(self.canvas_window_id, width=event.width)

    def _create_params_card(self) -> None:
        card = tk.Frame(
            self.content_frame,
            bg=self.COLORS["bg_card"],
            padx=30,
            pady=25,
            highlightbackground=self.COLORS["border"],
            highlightthickness=1,
        )
        card.pack(fill="x", pady=(0, 20))

        tk.Label(
            card,
            text="Parámetros del Servidor",
            font=("Segoe UI", 14, "bold"),
            bg=self.COLORS["bg_card"],
            fg=self.COLORS["text_body"],
        ).pack(fill="x", pady=(0, 20))

        grid_frame = tk.Frame(card, bg=self.COLORS["bg_card"])
        grid_frame.pack(fill="x")
        grid_frame.columnconfigure(1, weight=1)

        self.host_entry = self._add_labeled_entry(grid_frame, "Host:", 0)
        self.port_entry = self._add_labeled_entry(grid_frame, "Puerto:", 1)
        self.user_entry = self._add_labeled_entry(grid_frame, "Usuario:", 2)

        # Password field custom
        tk.Label(
            grid_frame,
            text="Contraseña:",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLORS["bg_card"],
            fg=self.COLORS["text_body"],
        ).grid(row=3, column=0, sticky="w", pady=10)

        pass_container = tk.Frame(
            grid_frame, bg=self.COLORS["bg_card"], highlightbackground="#ccc", highlightthickness=1
        )
        pass_container.grid(row=3, column=1, sticky="ew", pady=10)
        pass_container.columnconfigure(0, weight=1)

        self.password_entry = tk.Entry(
            pass_container,
            font=("Segoe UI", 10),
            show="●",
            bd=0,
            bg=self.COLORS["bg_card"],
        )
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        self.show_pass_btn = tk.Button(
            pass_container,
            text="👁️",
            command=self._toggle_password,
            relief="flat",
            bg=self.COLORS["bg_card"],
            cursor="hand2",
            activebackground=self.COLORS["bg_card"],
        )
        self.show_pass_btn.grid(row=0, column=1, padx=5)

        self.database_entry = self._add_labeled_entry(grid_frame, "Base de datos:", 4)

        # Botón cargar config
        tk.Button(
            card,
            text="⟳ Cargar última configuración guardada",
            command=self._load_last_config,
            font=("Segoe UI", 9),
            bg="#e3f2fd",
            fg="#1565c0",
            relief="flat",
            cursor="hand2",
            pady=8,
            padx=15,
        ).pack(anchor="e", pady=(15, 0))

    def _create_action_buttons(self) -> None:
        actions_frame = tk.Frame(self.content_frame, bg=self.COLORS["bg_main"])
        actions_frame.pack(fill="x", pady=(0, 20))

        self.test_button = tk.Button(
            actions_frame,
            text="🚀 PROBAR CONEXIÓN",
            command=self._test_connection,
            font=("Segoe UI", 11, "bold"),
            bg=self.COLORS["success"],
            fg="white",
            activebackground="#43a047",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            pady=12,
        )
        self.test_button.pack(fill="x", pady=(0, 15))

        # Barra de progreso
        self.progress_frame = tk.Frame(actions_frame, bg=self.COLORS["bg_main"])
        self.progress_bar = tk.Canvas(
            self.progress_frame, height=6, bg="#e0e0e0", highlightthickness=0
        )
        self.progress_bar.pack(fill="x")
        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Segoe UI", 9),
            bg=self.COLORS["bg_main"],
            fg=self.COLORS["text_muted"],
        )
        self.progress_label.pack(fill="x", pady=(5, 0))
        self.progress_frame.pack_forget()

    def _create_results_card(self) -> None:
        card = tk.Frame(
            self.content_frame,
            bg=self.COLORS["bg_card"],
            padx=30,
            pady=25,
            highlightbackground=self.COLORS["border"],
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True)

        header = tk.Frame(card, bg=self.COLORS["bg_card"])
        header.pack(fill="x", pady=(0, 15))

        tk.Label(
            header,
            text="Resultados de la Prueba",
            font=("Segoe UI", 14, "bold"),
            bg=self.COLORS["bg_card"],
            fg=self.COLORS["text_body"],
        ).pack(side="left")

        # Botones secundarios pequeños
        btn_frame = tk.Frame(header, bg=self.COLORS["bg_card"])
        btn_frame.pack(side="right")

        tk.Button(
            btn_frame,
            text="Limpiar",
            command=self._clear_results,
            font=("Segoe UI", 9),
            bg="#fff3e0",
            fg="#ef6c00",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btn_frame,
            text="Cerrar",
            command=self._on_closing,
            font=("Segoe UI", 9),
            bg="#ffebee",
            fg="#c62828",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
        ).pack(side="left")

        self.results_text = scrolledtext.ScrolledText(
            card,
            height=12,
            font=("Consolas", 10),
            bg="#fafafa",
            fg=self.COLORS["text_body"],
            wrap=tk.WORD,
            relief="flat",
            padx=10,
            pady=10,
            bd=1,
        )
        self.results_text.pack(fill="both", expand=True)

        # Tags de estilo para el texto
        self.results_text.tag_config("success", foreground=self.COLORS["success"], font=("Consolas", 10, "bold"))
        self.results_text.tag_config("error", foreground=self.COLORS["error"], font=("Consolas", 10, "bold"))
        self.results_text.tag_config("info", foreground=self.COLORS["primary"], font=("Consolas", 10, "bold"))
        self.results_text.tag_config("warning", foreground=self.COLORS["warning"], font=("Consolas", 10, "bold"))
        self.results_text.tag_config("label", foreground=self.COLORS["text_muted"], font=("Consolas", 10, "bold"))
        self.results_text.tag_config("highlight", background="#fff9c4", foreground="#000000")

        self._clear_results()

    def _add_labeled_entry(self, frame: tk.Misc, label: str, row: int) -> tk.Entry:
        tk.Label(
            frame,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg=self.COLORS["bg_card"],
            fg=self.COLORS["text_body"],
        ).grid(row=row, column=0, sticky="w", pady=10)

        entry = tk.Entry(
            frame,
            font=("Segoe UI", 10),
            relief="flat",
            bg="#fafafa",
            highlightbackground="#ccc",
            highlightthickness=1,
        )
        entry.grid(row=row, column=1, sticky="ew", pady=10, ipady=4)
        return entry

    # ------------------------------------------------------------------
    # Event helpers
    # ------------------------------------------------------------------
    def _on_mousewheel(self, event: tk.Event) -> None:
        if self.main_canvas is not None:
            delta = int(-1 * (event.delta / 120))
            self.main_canvas.yview_scroll(delta, "units")

    def _toggle_password(self) -> None:
        hidden = self.password_entry.cget("show") == "●"
        self.password_entry.config(show="" if hidden else "●")
        self.show_pass_btn.config(text="🙈" if hidden else "👁️")

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _load_last_config(self) -> None:
        try:
            cfg = get_db_config()
        except Exception as exc:
            messagebox.showwarning("Configuración", f"No fue posible leer la configuración: {exc}")
            return

        self.host_entry.delete(0, tk.END)
        self.host_entry.insert(0, cfg.get("host", "localhost"))

        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, str(cfg.get("port", 3306)))

        self.user_entry.delete(0, tk.END)
        self.user_entry.insert(0, cfg.get("user", "root"))

        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, cfg.get("password", ""))

        self.database_entry.delete(0, tk.END)
        self.database_entry.insert(0, cfg.get("database", ""))

        self._update_status("● Configuración cargada", self.COLORS["success"])
        self._show_message("Configuración cargada desde config/db_config.json", "info")

    def _update_status(self, text: str, color: str) -> None:
        self.status_indicator.config(text=text, fg=color)

    def _show_message(self, message: str, tag: str = "label") -> None:
        self.results_text.config(state="normal")
        self.results_text.insert("end", f"{message}\n", tag)
        self.results_text.see("end")
        self.results_text.config(state="disabled")

    def _show_progress(self, message: str) -> None:
        self.progress_frame.pack(fill="x")
        width = self.progress_bar.winfo_width() or 600
        self.progress_bar.delete("all")
        self.progress_bar.create_rectangle(
            0, 0, width, 6, fill=self.COLORS["success"], outline=""
        )
        self.progress_label.config(text=message)
        self.window.update_idletasks()

    def _clear_results(self) -> None:
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", "💡 Complete los campos y presione 'PROBAR CONEXIÓN'.\n\n")
        self.results_text.insert("end", "Este sistema verificará:\n")
        self.results_text.insert("end", "  ✓ Conectividad con MySQL\n")
        self.results_text.insert("end", "  ✓ Credenciales y permisos\n")
        self.results_text.insert("end", "  ✓ Existencia de la base de datos\n")
        self.results_text.config(state="disabled")
        self._update_status("● Esperando prueba", self.COLORS["text_muted"])
        self.progress_frame.pack_forget()

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------
    def _test_connection(self) -> None:
        self.test_button.config(state="disabled", text="⏳ Conectando...")
        self._update_status("● Conectando...", self.COLORS["warning"])
        self._show_progress("Validando parámetros")

        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("end", f"PRUEBA EJECUTADA: {self._get_timestamp()}\n", "label")
        self.results_text.insert("end", "=" * 60 + "\n\n", "label")

        host = self.host_entry.get().strip()
        port_value = self.port_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.password_entry.get()
        database = self.database_entry.get().strip()

        if not host or not port_value or not user:
            self.results_text.insert("end", "❌ Complete host, puerto y usuario.\n", "error")
            self._update_status("● Falta información", self.COLORS["error"])
            self._finish_test()
            return

        try:
            port = int(port_value)
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            self.results_text.insert("end", "❌ Puerto inválido (1-65535).\n", "error")
            self._update_status("● Puerto inválido", self.COLORS["error"])
            self._finish_test()
            return

        config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database or None,
        }

        try:
            self._show_progress("Contactando al servidor")
            db = DatabaseConnection(config)
            result = db.test_connection()

            if result:
                self.results_text.insert("end", "✅ Conexión exitosa\n\n", "success")
                self.results_text.insert("end", "Detalles de la conexión:\n", "label")
                if result.get("version"):
                    self.results_text.insert("end", f"  • Versión: {result['version']}\n", "info")
                if result.get("user_name"):
                    self.results_text.insert("end", f"  • Usuario: {result['user_name']}\n", "info")
                if database:
                    self.results_text.insert("end", f"  • Base solicitada: {database}\n", "info")
                elif result.get("database"):
                    self.results_text.insert("end", f"  • Base activa: {result['database']}\n", "info")

                persisted = self._persist_config(config)
                self.results_text.insert("end", "\n💾 Configuración guardada automáticamente.\n", "success")
                self._update_status("● Conectado", self.COLORS["success"])
            else:
                self.results_text.insert("end", "❌ No fue posible establecer la conexión.\n", "error")
                self._update_status("● Conexión fallida", self.COLORS["error"])
        except Exception as exc:
            self.results_text.insert("end", f"❌ Error: {exc}\n", "error")
            lowered = str(exc).lower()
            if "unknown database" in lowered:
                self.results_text.insert("end", "Sugerencia: verifique el nombre de la base de datos.\n", "warning")
            elif "access denied" in lowered:
                self.results_text.insert("end", "Sugerencia: revise usuario y contraseña.\n", "warning")
            else:
                self.results_text.insert("end", "Revise la red o el estado del servicio MySQL.\n", "warning")
            self._update_status("● Error en conexión", self.COLORS["error"])
        finally:
            self._finish_test()

    def _finish_test(self) -> None:
        self.progress_frame.pack_forget()
        self.results_text.insert("end", "\n" + "=" * 60 + "\n", "label")
        self.results_text.config(state="disabled")
        self.test_button.config(state="normal", text="🚀 PROBAR CONEXIÓN")
        self.results_text.see("end")

    def _persist_config(self, new_values: Dict[str, Any]) -> Dict[str, Any]:
        current = get_db_config()
        current.update({k: v for k, v in new_values.items() if v is not None})
        saved = save_db_config(current)
        if self._on_config_saved_callback:
            try:
                self._on_config_saved_callback(saved.copy())
            except Exception:
                pass
        return saved


__all__ = ["ConnectionTestWindow"]
