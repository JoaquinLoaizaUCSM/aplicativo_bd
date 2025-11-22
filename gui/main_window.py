"""
Ventana principal del aplicativo
Autor: Joaquin Armando Loaiza Cruz
Fecha: 2025-11-11
Descripción: Interfaz gráfica principal refactorizada.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import APP_CONFIG, get_db_config
from database.database import DatabaseConnection
from database.employee_service import EmployeeService
from database.attendance_service import AttendanceService
from database.report_service import ReportService
from database.reference_service import ReferenceService
from gui.connection_test_window import ConnectionTestWindow
from gui.employees_view import EmployeesView
from gui.attendance_view import AttendanceView
from gui.reports_view import ReportsView
from gui.import_view import ImportView
from gui.styles import configure_styles, COLORS
from gui.components import Sidebar, Header

class MainWindow:
    """
    Clase principal de la ventana de la aplicación.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_CONFIG['title'])
        self.root.geometry("1400x800")
        self.root.state('zoomed')
        self.root.configure(bg=COLORS['background'])
        
        # Configurar estilos globales
        self.style = configure_styles(self.root)
        
        # Estado
        self.db_connection: Optional[DatabaseConnection] = None
        self.db_config = get_db_config()
        self.current_view_name = "dashboard"
        
        # Servicios
        self.employee_service: Optional[EmployeeService] = None
        self.attendance_service: Optional[AttendanceService] = None
        self.report_service: Optional[ReportService] = None
        self.reference_service: Optional[ReferenceService] = None
        
        # Interfaz
        self._init_ui()
        
        # Conexión
        self.root.after(100, self._auto_connect)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _init_ui(self):
        """Inicializa la estructura de la interfaz."""
        # Contenedor principal (Layout horizontal)
        main_container = tk.Frame(self.root, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # 1. Sidebar (Izquierda)
        menu_items = [
            ("📊", "Dashboard", self._show_dashboard),
            ("👥", "Empleados", self._show_employees),
            ("📝", "Asistencias", self._show_attendance),
            ("📈", "Reportes", self._show_reports),
            ("📁", "Importar", self._import_csv),
        ]
        self.sidebar = Sidebar(main_container, APP_CONFIG.get('app_name', 'GDI System'), menu_items)
        self.sidebar.pack(side='left', fill='y')
        
        # 2. Área de Contenido (Derecha)
        content_wrapper = tk.Frame(main_container, bg=COLORS['background'])
        content_wrapper.pack(side='left', fill='both', expand=True)
        
        # 2.1 Header (Arriba)
        self.header = Header(content_wrapper, self._test_connection)
        self.header.pack(fill='x')
        
        # 2.2 Vista Dinámica (Centro)
        self.content_area = tk.Frame(content_wrapper, bg=COLORS['background'])
        self.content_area.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Mostrar dashboard inicial
        self._show_dashboard()

    def _auto_connect(self):
        """Intenta conectar a la BD."""
        try:
            self.db_config = get_db_config()
            if self.db_connection:
                try:
                    self.db_connection.disconnect()
                except: pass

            self.db_connection = DatabaseConnection(self.db_config)
            result = self.db_connection.test_connection()
            
            if result:
                self._initialize_services()
                server_id = result.get('connection_id', '?')
                version = result.get('version', 'MySQL')
                db_name = self.db_config.get('database', 'Unknown')
                
                # Actualizar Header (Visualmente verde)
                self.header.config(bg=COLORS['secondary'])
                for child in self.header.winfo_children():
                    child.config(bg=COLORS['secondary'])
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Label):
                            grandchild.config(bg=COLORS['secondary'], fg='white')
                
                self.header.status_var.set(f"Conectado: {self.db_config.get('host')}")
                self.header.info_var.set(f"DB: {db_name} | Ver: {version}")
                
                self._refresh_current_view()
            else:
                self._set_disconnected_state("No se pudo conectar al servidor")
                
        except Exception as e:
            self._set_disconnected_state(f"Error: {str(e)}")

    def _set_disconnected_state(self, message):
        self._reset_services()
        # Actualizar Header (Visualmente rojo)
        self.header.config(bg=COLORS['danger'])
        for child in self.header.winfo_children():
            child.config(bg=COLORS['danger'])
            for grandchild in child.winfo_children():
                if isinstance(grandchild, tk.Label):
                    grandchild.config(bg=COLORS['danger'], fg='white')
                    
        self.header.status_var.set("Desconectado")
        self.header.info_var.set(message)

    def _reset_services(self):
        self.employee_service = None
        self.attendance_service = None
        self.report_service = None
        self.reference_service = None

    def _initialize_services(self):
        if not self.db_connection: return
        self.employee_service = EmployeeService(self.db_connection)
        self.attendance_service = AttendanceService(self.db_connection)
        self.report_service = ReportService(self.db_connection)
        self.reference_service = ReferenceService(self.db_connection)

    def _refresh_current_view(self):
        if self.current_view_name == "employees": self._show_employees()
        elif self.current_view_name == "attendance": self._show_attendance()
        elif self.current_view_name == "reports": self._show_reports()
        elif self.current_view_name == "import": self._import_csv()
        else: self._show_dashboard()

    def _clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # --- VISTAS ---

    def _show_dashboard(self):
        self._clear_content()
        self.current_view_name = "dashboard"
        self.sidebar.set_active(0)
        
        # Título
        ttk.Label(self.content_area, text="Dashboard", style='Title.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Stats Grid
        stats_frame = tk.Frame(self.content_area, bg=COLORS['background'])
        stats_frame.pack(fill='x')
        
        # Obtener datos
        stats = {'asistencias': '0', 'faltas': '0', 'pendientes': '0', 'tardanzas': '0'}
        if self.report_service:
            try:
                data = self.report_service.get_statistics()
                if data:
                    stats['asistencias'] = str(data.get('asistencias_hoy', 0))
                    stats['faltas'] = str(data.get('faltas_hoy', 0))
                    stats['pendientes'] = str(data.get('incompletos_hoy', 0))
                    stats['tardanzas'] = str(data.get('tardanzas_hoy', 0))
            except: pass

        cards = [
            ("Asistencias Hoy", stats['asistencias'], "✅", COLORS['secondary']),
            ("Ausencias", stats['faltas'], "❌", COLORS['danger']),
            ("Sin Salida", stats['pendientes'], "⚠️", COLORS['warning']),
            ("Tardanzas", stats['tardanzas'], "⏰", COLORS['info']),
        ]
        
        for i, (title, value, icon, color) in enumerate(cards):
            self._create_stat_card(stats_frame, title, value, icon, color, i)

        # Welcome Message
        welcome_frame = ttk.Frame(self.content_area, style='Card.TFrame', padding=20)
        welcome_frame.pack(fill='both', expand=True, pady=20)
        
        ttk.Label(welcome_frame, text="Bienvenido al Sistema de Gestión", style='CardTitle.TLabel').pack(anchor='w')
        ttk.Label(welcome_frame, 
                text="Seleccione una opción del menú lateral para comenzar.\n\n"
                     "• Empleados: Gestión de personal.\n"
                     "• Asistencias: Registro y control de marcas.\n"
                     "• Reportes: Generación de informes y exportación.\n"
                     "• Importar: Carga masiva desde Excel.",
                style='CardBody.TLabel', justify='left').pack(anchor='w', pady=10)

    def _create_stat_card(self, parent, title, value, icon, color, col_idx):
        card = tk.Frame(parent, bg='white', relief='flat', bd=0)
        card.grid(row=0, column=col_idx, padx=10, sticky='ew')
        parent.columnconfigure(col_idx, weight=1)
        
        # Top color bar
        tk.Frame(card, bg=color, height=4).pack(fill='x')
        
        content = tk.Frame(card, bg='white', padx=20, pady=20)
        content.pack(fill='both')
        
        tk.Label(content, text=icon, font=('Segoe UI Emoji', 24), bg='white').pack(anchor='e')
        tk.Label(content, text=value, font=('Segoe UI', 32, 'bold'), fg=color, bg='white').pack(anchor='w')
        tk.Label(content, text=title, font=('Segoe UI', 10, 'bold'), fg='#7f8c8d', bg='white').pack(anchor='w')

    def _show_employees(self):
        self._clear_content()
        self.current_view_name = "employees"
        self.sidebar.set_active(1)
        EmployeesView(self.content_area, self.employee_service, self.reference_service, self._show_employees).render()

    def _show_attendance(self):
        self._clear_content()
        self.current_view_name = "attendance"
        self.sidebar.set_active(2)
        AttendanceView(self.content_area, self.attendance_service, self.employee_service, self.reference_service).render()

    def _show_reports(self):
        self._clear_content()
        self.current_view_name = "reports"
        self.sidebar.set_active(3)
        ReportsView(self.content_area, self.report_service, self.employee_service).render()

    def _import_csv(self):
        self._clear_content()
        self.current_view_name = "import"
        self.sidebar.set_active(4)
        ImportView(self.content_area, self.attendance_service, self.employee_service).render()

    def _test_connection(self):
        ConnectionTestWindow(self.root, on_config_saved=self._on_config_saved)

    def _on_config_saved(self, new_config):
        self.db_config = new_config
        self.root.after(100, self._auto_connect)

    def _on_closing(self):
        if messagebox.askokcancel("Salir", "¿Desea cerrar el sistema?"):
            if self.db_connection:
                try: self.db_connection.disconnect()
                except: pass
            self.root.destroy()

    def run(self):
        self.root.mainloop()
