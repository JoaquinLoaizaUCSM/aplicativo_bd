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

    def __init__(
        self,
        parent: tk.Tk | tk.Toplevel,
        on_config_saved: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Prueba de Conexión a Base de Datos")
        self.window.geometry("900x700")
        self.window.minsize(800, 600)
        self.window.transient(parent)
        self.window.resizable(True, True)

        self._on_config_saved_callback = on_config_saved
        self.main_canvas: Optional[tk.Canvas] = None

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
        container = tk.Frame(self.window, bg="#f5f5f5")
        container.pack(fill="both", expand=True)

        self.main_canvas = tk.Canvas(container, bg="#f5f5f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        self.main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content_frame = tk.Frame(self.main_canvas, bg="#f5f5f5", padx=30, pady=30)
        self.main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

        def _refresh_scroll(event: tk.Event) -> None:  # noqa: ANN001 - evento de Tk
            if self.main_canvas is not None:
                self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

        content_frame.bind("<Configure>", _refresh_scroll)
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        header = tk.Label(
            content_frame,
            text="Configuración del servidor MySQL",
            font=("Segoe UI", 18, "bold"),
            bg="#f5f5f5",
            fg="#263238",
            pady=10,
        )
        header.pack(fill="x")

        self.status_indicator = tk.Label(
            content_frame,
            text="● Esperando prueba",
            font=("Segoe UI", 10, "bold"),
            bg="#f5f5f5",
            fg="#90a4ae",
            anchor="w",
        )
        self.status_indicator.pack(fill="x", pady=(0, 20))

        form_frame = tk.LabelFrame(
            content_frame,
            text="Parámetros de conexión",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#37474f",
            padx=20,
            pady=20,
        )
        form_frame.pack(fill="x")
        form_frame.columnconfigure(1, weight=1)

        self.host_entry = self._add_labeled_entry(form_frame, "Host", row=0)
        self.port_entry = self._add_labeled_entry(form_frame, "Puerto", row=1)
        self.user_entry = self._add_labeled_entry(form_frame, "Usuario", row=2)

        tk.Label(form_frame, text="Contraseña", font=("Segoe UI", 10), bg="#ffffff").grid(row=3, column=0, sticky="w", pady=5)
        password_container = tk.Frame(form_frame, bg="#ffffff")
        password_container.grid(row=3, column=1, sticky="ew", pady=5)
        password_container.columnconfigure(0, weight=1)
        self.password_entry = tk.Entry(password_container, font=("Segoe UI", 10), show="●")
        self.password_entry.grid(row=0, column=0, sticky="ew")
        self.show_pass_btn = tk.Button(
            password_container,
            text="👁️",
            command=self._toggle_password,
            relief="flat",
            bg="#ffffff",
            cursor="hand2",
        )
        self.show_pass_btn.grid(row=0, column=1, padx=(5, 0))

        self.database_entry = self._add_labeled_entry(form_frame, "Base de datos", row=4)

        tk.Button(
            form_frame,
            text="⟳ Cargar última configuración",
            command=self._load_last_config,
            font=("Segoe UI", 9),
            bg="#e3f2fd",
            fg="#1976d2",
            relief="flat",
            cursor="hand2",
            pady=6,
        ).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(15, 0))

        actions_frame = tk.Frame(content_frame, bg="#f5f5f5")
        actions_frame.pack(fill="x", pady=(25, 15))

        self.test_button = tk.Button(
            actions_frame,
            text="🚀 PROBAR CONEXIÓN",
            command=self._test_connection,
            font=("Segoe UI", 12, "bold"),
            bg="#4caf50",
            fg="#ffffff",
            activebackground="#43a047",
            activeforeground="#ffffff",
            relief="flat",
            padx=40,
            pady=15,
            cursor="hand2",
        )
        self.test_button.pack(fill="x", pady=(0, 10))

        self.progress_frame = tk.Frame(actions_frame, bg="#f5f5f5")
        self.progress_bar = tk.Canvas(self.progress_frame, height=8, bg="#e0e0e0", highlightthickness=0)
        self.progress_bar.pack(fill="x")
        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Segoe UI", 9),
            bg="#f5f5f5",
            fg="#546e7a",
        )
        self.progress_label.pack(fill="x", pady=(4, 0))
        self.progress_frame.pack(fill="x")
        self.progress_frame.pack_forget()

        secondary_actions = tk.Frame(actions_frame, bg="#f5f5f5")
        secondary_actions.pack(fill="x")

        tk.Button(
            secondary_actions,
            text="🗑️ Limpiar",
            command=self._clear_results,
            font=("Segoe UI", 9),
            bg="#fff3e0",
            fg="#ef6c00",
            relief="flat",
            cursor="hand2",
            pady=10,
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            secondary_actions,
            text="✖ Cerrar",
            command=self._on_closing,
            font=("Segoe UI", 9),
            bg="#ffebee",
            fg="#c62828",
            relief="flat",
            cursor="hand2",
            pady=10,
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

        results_frame = tk.LabelFrame(
            content_frame,
            text="Resultados",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#37474f",
            padx=20,
            pady=20,
        )
        results_frame.pack(fill="both", expand=True)

        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=18,
            font=("Consolas", 10),
            bg="#fafafa",
            fg="#263238",
            wrap=tk.WORD,
            relief="flat",
        )
        self.results_text.pack(fill="both", expand=True)

        self.results_text.tag_config("success", foreground="#4caf50", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("error", foreground="#e53935", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("info", foreground="#1e88e5", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("warning", foreground="#fb8c00", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("label", foreground="#607d8b", font=("Consolas", 10, "bold"))
        self.results_text.tag_config("highlight", background="#fff9c4", foreground="#263238")

        self._clear_results()

    def _add_labeled_entry(self, frame: tk.Misc, label: str, row: int) -> tk.Entry:
        tk.Label(frame, text=label, font=("Segoe UI", 10), bg="#ffffff").grid(row=row, column=0, sticky="w", pady=5)
        entry = tk.Entry(frame, font=("Segoe UI", 10))
        entry.grid(row=row, column=1, sticky="ew", pady=5)
        return entry

    # ------------------------------------------------------------------
    # Event helpers
    # ------------------------------------------------------------------
    def _on_mousewheel(self, event: tk.Event) -> None:  # noqa: ANN001 - evento de Tk
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
        except Exception as exc:  # pragma: no cover - depende del archivo local
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

        self._update_status("● Configuración cargada", "#4caf50")
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
        self.progress_bar.create_rectangle(0, 0, width, 8, fill="#4caf50", outline="")
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
        self.results_text.insert("end", "  ✓ Información básica del servidor\n")
        self.results_text.config(state="disabled")
        self._update_status("● Esperando prueba", "#90a4ae")
        self.progress_frame.pack_forget()

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------
    def _test_connection(self) -> None:
        self.test_button.config(state="disabled", text="⏳ Conectando...")
        self._update_status("● Conectando...", "#fb8c00")
        self._show_progress("Validando parámetros")

        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("end", f"PRUEBA EJECUTADA: {self._get_timestamp()}\n", "label")
        self.results_text.insert("end", "=" * 80 + "\n\n", "label")

        host = self.host_entry.get().strip()
        port_value = self.port_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.password_entry.get()
        database = self.database_entry.get().strip()

        if not host or not port_value or not user:
            self.results_text.insert("end", "❌ Complete host, puerto y usuario.\n", "error")
            self._update_status("● Falta información", "#e53935")
            self._finish_test()
            return

        try:
            port = int(port_value)
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            self.results_text.insert("end", "❌ Puerto inválido (1-65535).\n", "error")
            self._update_status("● Puerto inválido", "#e53935")
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
                self.results_text.insert("end", "Detalles:\n", "label")
                if result.get("version"):
                    self.results_text.insert("end", f"  • Versión: {result['version']}\n", "info")
                if result.get("user_name"):
                    self.results_text.insert("end", f"  • Usuario activo: {result['user_name']}\n", "info")
                if database:
                    self.results_text.insert("end", f"  • Base solicitada: {database}\n", "info")
                elif result.get("database"):
                    self.results_text.insert("end", f"  • Base activa: {result['database']}\n", "info")

                persisted = self._persist_config(config)
                self.results_text.insert("end", "\n💾 Configuración guardada.\n", "success")
                if persisted.get("database"):
                    self.results_text.insert("end", f"Base activa registrada: {persisted['database']}\n", "label")
                self._update_status("● Conectado", "#4caf50")
            else:
                self.results_text.insert("end", "❌ No fue posible establecer la conexión.\n", "error")
                self._update_status("● Conexión fallida", "#e53935")
        except Exception as exc:  # pragma: no cover - depende del servidor externo
            self.results_text.insert("end", f"❌ Error: {exc}\n", "error")
            lowered = str(exc).lower()
            if "unknown database" in lowered:
                self.results_text.insert("end", "Sugerencia: verifique el nombre de la base.\n", "warning")
            elif "access denied" in lowered:
                self.results_text.insert("end", "Sugerencia: revise usuario y contraseña.\n", "warning")
            else:
                self.results_text.insert("end", "Revise la red o el estado del servicio MySQL.\n", "warning")
            self._update_status("● Error en conexión", "#e53935")
        finally:
            self._finish_test()

    def _finish_test(self) -> None:
        self.progress_frame.pack_forget()
        self.results_text.insert("end", "\n" + "=" * 80 + "\n", "label")
        self.results_text.insert("end", f"Finalizado: {self._get_timestamp()}\n", "label")
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
            except Exception:  # pragma: no cover - callbacks externos
                pass
        return saved


__all__ = ["ConnectionTestWindow"]
