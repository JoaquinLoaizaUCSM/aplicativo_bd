"""
Vista del módulo de Asistencias
Autor: Joaquin Armando Loaiza Cruz
Fecha: 2025-11-11
Descripción: Gestión de registros de asistencia con CRUD usando procedimientos almacenados
"""

import calendar
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional
from datetime import date, datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.attendance_service import AttendanceService
from database.employee_service import EmployeeService
from database.reference_service import ReferenceService
from database.operation_result import OperationResult, OperationStatus


class AttendanceView:
    """Vista para gestionar asistencias"""

    SEARCH_PLACEHOLDER = "Código empleado o nombre..."
    MONTH_PLACEHOLDER = "Seleccione mes"
    DEFAULT_RANGE_DAYS = 30
    DAYS_OF_WEEK = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    MONTH_OPTIONS = [
        ("01", "Enero"),
        ("02", "Febrero"),
        ("03", "Marzo"),
        ("04", "Abril"),
        ("05", "Mayo"),
        ("06", "Junio"),
        ("07", "Julio"),
        ("08", "Agosto"),
        ("09", "Septiembre"),
        ("10", "Octubre"),
        ("11", "Noviembre"),
        ("12", "Diciembre"),
    ]
    MONTH_NAME_TO_NUM = {name: num for num, name in MONTH_OPTIONS}
    
    def __init__(self, parent_frame: tk.Frame,
                 attendance_service: Optional[AttendanceService],
                 employee_service: Optional[EmployeeService],
                 reference_service: Optional[ReferenceService] = None):
        """
        Inicializa la vista de asistencias.
        
        Args:
            parent_frame: Frame contenedor principal
            attendance_service: Servicio de asistencias
            employee_service: Servicio de empleados
        """
        self.parent_frame = parent_frame
        self.attendance_service = attendance_service
        self.employee_service = employee_service
        self.reference_service = reference_service
        self.container = None
        
    def render(self):
        """Renderiza la vista completa de asistencias"""
        # Limpiar frame padre
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Verificar conexión
        if not self.attendance_service:
            self._show_no_connection()
            return
        
        # Título y botón nuevo
        self._create_header()
        
        # Contenedor principal
        main_container = tk.Frame(self.parent_frame, bg='#f5f5f5')
        main_container.pack(fill='both', expand=True, padx=30, pady=(0, 30))
        
        # Filtros
        self._create_filters(main_container)
        
        # Tabla de asistencias
        self.container = tk.Frame(main_container, bg='#f5f5f5')
        self.container.pack(fill='both', expand=True, pady=(0, 10))
        
        # Cargar datos
        self._load_attendance_table()
    
    def _show_no_connection(self):
        """Muestra mensaje de sin conexión"""
        error_frame = tk.Frame(self.parent_frame, bg='#ffebee', relief='solid', borderwidth=1)
        error_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(
            error_frame,
            text="⚠️ Sin Conexión a Base de Datos",
            font=('Segoe UI', 16, 'bold'),
            bg='#ffebee',
            fg='#c62828'
        ).pack(pady=(50, 10))
        
        tk.Label(
            error_frame,
            text="Por favor, conecte a la base de datos usando el botón 'Configurar'.",
            font=('Segoe UI', 11),
            bg='#ffebee',
            fg='#d32f2f'
        ).pack(pady=(0, 50))
    
    def _create_header(self):
        """Crea el encabezado"""
        title_frame = tk.Frame(self.parent_frame, bg='white', height=80)
        title_frame.pack(fill='x', padx=30, pady=(30, 20))
        title_frame.pack_propagate(False)
        
        title_content = tk.Frame(title_frame, bg='white')
        title_content.pack(side='left', expand=True)
        
        tk.Label(
            title_content,
            text="📝",
            font=('Segoe UI', 28),
            bg='white'
        ).pack(side='left', padx=(0, 15))
        
        tk.Label(
            title_content,
            text="Gestión de Asistencias",
            font=('Segoe UI', 20, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side='left')
        
        # Botón Nueva Asistencia
        tk.Button(
            title_frame,
            text="➕ Nueva Asistencia",
            command=self._create_attendance_dialog,
            font=('Segoe UI', 10, 'bold'),
            bg='#4caf50',
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side='right')

    def _get_shift_records(self) -> List[Dict[str, Any]]:
        if not self.attendance_service:
            return []
        if self.reference_service:
            return self.reference_service.get_shifts() or []
        try:
            temp_reference = ReferenceService(self.attendance_service.db)  # type: ignore[arg-type]
            return temp_reference.get_shifts() or []
        except Exception:
            return []

    def _get_day_name(self, date_value: datetime) -> str:
        return self.DAYS_OF_WEEK[date_value.weekday()]

    @staticmethod
    def _format_time(value: Any) -> str:
        if isinstance(value, datetime):
            return value.strftime('%H:%M')
        if isinstance(value, timedelta):
            total_seconds = int(value.total_seconds())
            hours = (total_seconds // 3600) % 24
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        return '' if value in (None, '') else str(value)
    
    def _create_filters(self, parent):
        """Crea los filtros de búsqueda"""
        filter_frame = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)
        filter_frame.pack(fill='x', pady=(0, 20))
        
        filter_content = tk.Frame(filter_frame, bg='white', padx=20, pady=15)
        filter_content.pack(fill='x')
        
        tk.Label(
            filter_content,
            text="🔍 Filtrar Asistencias",
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(anchor='w')

        # Modo de filtro: por rango de fechas o por Año/Mes
        self._filter_mode_var = tk.StringVar(value='range')
        mode_frame = tk.Frame(filter_content, bg='white')
        mode_frame.pack(fill='x', pady=(5, 10))
        tk.Radiobutton(
            mode_frame,
            text='Rango fechas',
            variable=self._filter_mode_var,
            value='range',
            bg='white',
            command=self._toggle_filter_mode
        ).pack(side='left', padx=(0, 20))
        tk.Radiobutton(
            mode_frame,
            text='Por Año/Mes',
            variable=self._filter_mode_var,
            value='year_month',
            bg='white',
            command=self._toggle_filter_mode
        ).pack(side='left')

        # Controles de rango
        range_frame = tk.LabelFrame(filter_content, text='Rango de fechas', bg='white')
        range_frame.pack(fill='x', pady=(0, 10))
        range_frame.columnconfigure(1, weight=1)
        range_frame.columnconfigure(3, weight=1)
        tk.Label(range_frame, text="Inicio:", font=('Segoe UI', 9), bg='white').grid(row=0, column=0, sticky='w', padx=(0,5), pady=5)
        fecha_inicio = tk.Entry(range_frame, font=('Segoe UI', 9), width=15)
        fecha_inicio.insert(0, (datetime.now() - timedelta(days=self.DEFAULT_RANGE_DAYS)).strftime('%Y-%m-%d'))
        fecha_inicio.grid(row=0, column=1, sticky='ew', padx=(0,15), pady=5)
        tk.Label(range_frame, text="Fin:", font=('Segoe UI', 9), bg='white').grid(row=0, column=2, sticky='w', padx=(0,5), pady=5)
        fecha_fin = tk.Entry(range_frame, font=('Segoe UI', 9), width=15)
        fecha_fin.insert(0, datetime.now().strftime('%Y-%m-%d'))
        fecha_fin.grid(row=0, column=3, sticky='ew', padx=(0,15), pady=5)

        # Controles Año/Mes
        month_frame = tk.LabelFrame(filter_content, text='Filtro por Año/Mes', bg='white')
        month_frame.pack(fill='x', pady=(0, 10))
        month_frame.columnconfigure(1, weight=1)
        month_frame.columnconfigure(3, weight=1)
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year, current_year - 6, -1)]
        tk.Label(month_frame, text="Año:", font=('Segoe UI', 9), bg='white').grid(row=0, column=0, sticky='w', padx=(0,5), pady=5)
        year_combo = ttk.Combobox(month_frame, values=years, state='readonly', width=15)
        year_combo.grid(row=0, column=1, sticky='ew', padx=(0,15), pady=5)
        year_combo.current(0)
        tk.Label(month_frame, text="Mes:", font=('Segoe UI', 9), bg='white').grid(row=0, column=2, sticky='w', padx=(0,5), pady=5)
        month_values = [self.MONTH_PLACEHOLDER] + [name for _, name in self.MONTH_OPTIONS]
        month_combo = ttk.Combobox(month_frame, values=month_values, state='readonly', width=20)
        month_combo.grid(row=0, column=3, sticky='ew', padx=(0,15), pady=5)
        month_combo.current(0)

        # Búsqueda por término
        search_frame = tk.Frame(filter_content, bg='white')
        search_frame.pack(fill='x', pady=(5, 0))
        tk.Label(search_frame, text="Búsqueda:", font=('Segoe UI', 9), bg='white').pack(side='left')
        search_entry = tk.Entry(search_frame, font=('Segoe UI', 9))
        search_entry.insert(0, self.SEARCH_PLACEHOLDER)
        search_entry.config(fg='#90a4ae')
        search_entry.pack(side='left', fill='x', expand=True, padx=(5, 10))
        
        def on_focus_in(e):
            if search_entry.get() == self.SEARCH_PLACEHOLDER:
                search_entry.delete(0, tk.END)
                search_entry.config(fg='#2c3e50')
        
        def on_focus_out(e):
            if not search_entry.get():
                search_entry.insert(0, self.SEARCH_PLACEHOLDER)
                search_entry.config(fg='#90a4ae')
        
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        
        # Botones
        btn_frame = tk.Frame(filter_content, bg='white')
        btn_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(
            btn_frame,
            text="Filtrar",
            command=self._apply_filters,
            font=('Segoe UI', 9, 'bold'),
            bg='#2196f3',
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=6
        ).pack(side='left', padx=(0, 5))
        
        tk.Button(
            btn_frame,
            text="🔄 Limpiar",
            command=self._reset_filters,
            font=('Segoe UI', 9),
            bg='#4caf50',
            fg='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=6
        ).pack(side='left')

        self._filter_controls = {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'year_combo': year_combo,
            'month_combo': month_combo,
            'search_entry': search_entry,
            'range_frame': range_frame,
            'month_frame': month_frame,
        }
        self._toggle_filter_mode()

    def _toggle_filter_mode(self):
        controls = getattr(self, '_filter_controls', None)
        if not controls:
            return
        range_active = self._filter_mode_var.get() == 'range'
        range_state = 'normal' if range_active else 'disabled'
        month_state = 'disabled' if range_active else 'readonly'
        controls['fecha_inicio'].config(state=range_state)
        controls['fecha_fin'].config(state=range_state)
        controls['year_combo'].configure(state=month_state)
        controls['month_combo'].configure(state=month_state)

    def _collect_filter_values(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        controls = getattr(self, '_filter_controls', {})
        if not controls:
            return None, None, None
        term = controls['search_entry'].get().strip()
        if term == self.SEARCH_PLACEHOLDER:
            term = None

        mode = self._filter_mode_var.get()
        if mode == 'range':
            return (
                term,
                controls['fecha_inicio'].get().strip() or None,
                controls['fecha_fin'].get().strip() or None,
            )

        year_value = controls['year_combo'].get().strip()
        month_name = controls['month_combo'].get().strip()
        if not year_value or month_name in ('', self.MONTH_PLACEHOLDER):
            raise ValueError('Seleccione año y mes')
        month_num = self.MONTH_NAME_TO_NUM.get(month_name)
        if not month_num:
            raise ValueError('Mes inválido')
        start, end = self._calculate_month_boundaries(int(year_value), int(month_num))
        return term, start, end

    def _calculate_month_boundaries(self, year: int, month: int) -> tuple[str, str]:
        last_day = calendar.monthrange(year, month)[1]
        return (f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day:02d}")

    def _apply_filters(self):
        try:
            term, start_date, end_date = self._collect_filter_values()
        except ValueError as exc:
            messagebox.showwarning('Filtro', str(exc))
            return
        self._load_attendance_table(term, start_date, end_date)

    def _reset_filters(self):
        controls = getattr(self, '_filter_controls', {})
        if not controls:
            return
        today = datetime.now()
        start = (today - timedelta(days=self.DEFAULT_RANGE_DAYS)).strftime('%Y-%m-%d')
        controls['fecha_inicio'].delete(0, tk.END)
        controls['fecha_inicio'].insert(0, start)
        controls['fecha_fin'].delete(0, tk.END)
        controls['fecha_fin'].insert(0, today.strftime('%Y-%m-%d'))
        controls['year_combo'].current(0)
        controls['month_combo'].current(0)
        controls['search_entry'].delete(0, tk.END)
        controls['search_entry'].insert(0, self.SEARCH_PLACEHOLDER)
        controls['search_entry'].config(fg='#90a4ae')
        self._filter_mode_var.set('range')
        self._toggle_filter_mode()
        self._load_attendance_table()
    
    def _load_attendance_table(self, search_term=None, fecha_inicio=None, fecha_fin=None):
        """Carga la tabla de asistencias"""
        # Limpiar contenedor
        if self.container is None:
            return
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Mostrar indicador de carga
        loading_label = tk.Label(
            self.container,
            text="⏳ Cargando asistencias...",
            font=('Segoe UI', 12),
            bg='#f5f5f5',
            fg='#546e7a'
        )
        loading_label.pack(pady=50)
        self.container.update()

        assert self.attendance_service is not None
        
        # Ejecutar carga de datos (simulada asíncrona para UI)
        self.container.after(50, lambda: self._render_attendance_table(search_term, fecha_inicio, fecha_fin))

    def _render_attendance_table(self, search_term, fecha_inicio, fecha_fin):
        """Renderiza la tabla de asistencias después de cargar"""
        if self.container is None or self.attendance_service is None:
            return

        # Limpiar loading
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Frame con scroll
        canvas = tk.Canvas(self.container, bg='#f5f5f5', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.container, orient="vertical", command=canvas.yview)
        table_frame = tk.Frame(canvas, bg='white', relief='solid', borderwidth=1)
        
        table_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=table_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Hacer que el table_frame se expanda al ancho del canvas
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Header
        header_frame = tk.Frame(table_frame, bg='#37474f', height=45)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        headers = [
            ("FECHA", 0.10),
            ("EMPLEADO", 0.24),
            ("TURNO E/S", 0.13),
            ("MARCA E/S", 0.13),
            ("HORAS TRAB.", 0.10),
            ("TURNO", 0.10),
            ("ACCIONES", 0.20)
        ]
        
        for header_text, width in headers:
            tk.Label(
                header_frame,
                text=header_text,
                font=('Segoe UI', 9, 'bold'),
                bg='#37474f',
                fg='white',
                anchor='w',
                padx=10
            ).place(relx=sum([h[1] for h in headers[:headers.index((header_text, width))]]),
                   rely=0, relwidth=width, relheight=1)
        
        # Obtener datos
        try:
            if search_term or fecha_inicio or fecha_fin:
                attendances = self.attendance_service.filter_attendance(
                    search_term, fecha_inicio, fecha_fin, None
                )
            else:
                attendances = self.attendance_service.get_all_attendance()
            
            if not attendances:
                tk.Label(
                    table_frame,
                    text="No se encontraron registros de asistencia",
                    font=('Segoe UI', 12),
                    bg='white',
                    fg='#546e7a'
                ).pack(pady=50)
            else:
                # Renderizar filas
                for idx, att in enumerate(attendances):
                    row_bg = '#f8f9fa' if idx % 2 == 0 else 'white'
                    
                    row_frame = tk.Frame(table_frame, bg=row_bg, height=45)
                    row_frame.pack(fill='x')
                    row_frame.pack_propagate(False)
                    
                    entrada_marca_str = self._format_time(att.get('marca_entrada'))
                    salida_marca_str = self._format_time(att.get('marca_salida'))
                    entrada_turno_str = self._format_time(att.get('turno_entrada'))
                    salida_turno_str = self._format_time(att.get('turno_salida'))
                    
                    # Formato combinado para turno y marca
                    turno_horario = f"{entrada_turno_str} - {salida_turno_str}" if entrada_turno_str or salida_turno_str else ''
                    marca_horario = f"{entrada_marca_str} - {salida_marca_str}" if entrada_marca_str or salida_marca_str else ''
                    
                    fecha_valor = att.get('fecha_asistencia')
                    if isinstance(fecha_valor, (datetime, date)):
                        fecha_valor = fecha_valor.strftime('%Y-%m-%d')
                    fecha_display = fecha_valor or ''
                    
                    # Datos simplificados
                    data = [
                        fecha_display,
                        f"{att.get('codigo_empleado', '')} - {att.get('nombre_empleado', '')}",
                        turno_horario,
                        marca_horario,
                        f"{att.get('horas_trabajadas', 0):.1f}h",
                        att.get('codigo_turno', '')
                    ]
                    
                    for i, (text, width) in enumerate(zip(data, [h[1] for h in headers[:-1]])):
                        tk.Label(
                            row_frame,
                            text=str(text),
                            font=('Segoe UI', 9),
                            bg=row_bg,
                            fg='#2c3e50',
                            anchor='w',
                            padx=10
                        ).place(relx=sum([h[1] for h in headers[:i]]),
                               rely=0, relwidth=width, relheight=1)
                    
                    # Botones
                    actions_frame = tk.Frame(row_frame, bg=row_bg)
                    actions_frame.place(relx=0.90, rely=0.5, anchor='center')
                    
                    tk.Button(
                        actions_frame,
                        text="✏️ Editar",
                        command=lambda a=att: self._edit_attendance_dialog(a),
                        font=('Segoe UI', 9, 'bold'),
                        bg='#ff9800',
                        fg='white',
                        activebackground='#f57c00',
                        activeforeground='white',
                        relief='flat',
                        cursor='hand2',
                        padx=12,
                        pady=4,
                        bd=0
                    ).pack(side='left', padx=4)
                    
                    tk.Button(
                        actions_frame,
                        text="🗑️ Eliminar",
                        command=lambda a=att: self._delete_attendance(a),
                        font=('Segoe UI', 9, 'bold'),
                        bg='#f44336',
                        fg='white',
                        activebackground='#d32f2f',
                        activeforeground='white',
                        relief='flat',
                        cursor='hand2',
                        padx=12,
                        pady=4,
                        bd=0
                    ).pack(side='left', padx=4)
        
        except Exception as e:
            tk.Label(
                table_frame,
                text=f"Error al cargar datos: {str(e)}",
                font=('Segoe UI', 12),
                bg='white',
                fg='#e53935'
            ).pack(pady=50)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_attendance_dialog(self):
        """Diálogo para crear nueva asistencia"""
        if not self.attendance_service or not self.employee_service:
            messagebox.showerror("Error", "No hay conexión a la base de datos")
            return
        
        assert self.attendance_service is not None
        assert self.employee_service is not None
        
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Nueva Asistencia")
        dialog.geometry("500x550")
        dialog.transient(self.parent_frame.winfo_toplevel())
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 275
        dialog.geometry(f'500x550+{x}+{y}')
        
        # Contenido
        main_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        tk.Label(
            main_frame,
            text="➕ Registrar Nueva Asistencia",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(0, 20))
        
        # Preparar datos auxiliares
        shift_records = self._get_shift_records()

        # Empleado
        tk.Label(main_frame, text="Empleado:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        empleado_combo = ttk.Combobox(main_frame, font=('Segoe UI', 10), state='readonly')
        employees = self.employee_service.get_all_employees() or []
        empleado_combo['values'] = [f"{e['codigo']} - {e['nombre']}" for e in employees]
        empleado_combo.pack(fill='x', pady=(0,10))
        if empleado_combo['values']:
            empleado_combo.current(0)
        
        # Turno
        tk.Label(main_frame, text="Turno:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        turno_combo = ttk.Combobox(main_frame, font=('Segoe UI', 10), state='readonly')
        turno_combo['values'] = [
            f"{t['codigo_turno']} - {str(t.get('hora_entrada'))} / {str(t.get('hora_salida'))}"
            for t in shift_records
        ]
        turno_combo.pack(fill='x', pady=(0,10))
        if turno_combo['values']:
            turno_combo.current(0)

        # Fecha
        tk.Label(main_frame, text="Fecha:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        fecha_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        fecha_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        fecha_entry.pack(fill='x', pady=(0,10))
        
        # Hora Entrada
        tk.Label(main_frame, text="Hora Entrada (HH:MM):*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        entrada_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        entrada_entry.insert(0, "08:00")
        entrada_entry.pack(fill='x', pady=(0,10))
        
        # Hora Salida
        tk.Label(main_frame, text="Hora Salida (HH:MM):*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        salida_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        salida_entry.insert(0, "17:00")
        salida_entry.pack(fill='x', pady=(0,10))
        tk.Label(main_frame, text="", bg='white').pack(pady=(0,10))
        
        def save_attendance():
            empleado = empleado_combo.get()
            fecha = fecha_entry.get().strip()
            entrada = entrada_entry.get().strip()
            salida = salida_entry.get().strip()
            turno_seleccionado = turno_combo.get()
            
            if not all([empleado, turno_seleccionado, fecha, entrada, salida]):
                messagebox.showerror("Error", "Complete todos los campos obligatorios (*)")
                return
            
            codigo_emp = empleado.split(' - ')[0]
            codigo_turno = turno_seleccionado.split(' - ')[0]
            
            # Convertir a datetime para validar y extraer información
            try:
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                datetime.strptime(f"{fecha} {entrada}", '%Y-%m-%d %H:%M')
                datetime.strptime(f"{fecha} {salida}", '%Y-%m-%d %H:%M')
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha/hora inválido")
                return
            
            dia = self._get_day_name(fecha_dt)
            
            assert self.attendance_service is not None
            result = self.attendance_service.create_attendance(
                fecha, codigo_emp, codigo_turno, dia, entrada, salida
            )

            if self._show_operation_result(result, title="Registrar asistencia"):
                dialog.destroy()
                self._load_attendance_table()
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(fill='x')
        
        tk.Button(
            btn_frame,
            text="Guardar",
            command=save_attendance,
            font=('Segoe UI', 10, 'bold'),
            bg='#4caf50',
            fg='white',
            cursor='hand2',
            padx=30,
            pady=10
        ).pack(side='left', expand=True, padx=(0,5))
        
        tk.Button(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            font=('Segoe UI', 10),
            bg='#f44336',
            fg='white',
            cursor='hand2',
            padx=30,
            pady=10
        ).pack(side='left', expand=True, padx=(5,0))
    
    def _edit_attendance_dialog(self, attendance):
        """Diálogo para editar asistencia"""
        if not self.attendance_service or not self.employee_service:
            messagebox.showerror("Error", "No hay conexión a la base de datos")
            return

        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Editar Asistencia")
        dialog.geometry("500x550")
        dialog.transient(self.parent_frame.winfo_toplevel())
        dialog.grab_set()

        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 275
        dialog.geometry(f'500x550+{x}+{y}')

        main_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)

        tk.Label(
            main_frame,
            text="✏️ Editar Asistencia",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(0, 20))

        # Cargar empleados y turnos
        employees = self.employee_service.get_all_employees() or []
        empleado_combo = ttk.Combobox(main_frame, font=('Segoe UI', 10), state='readonly')
        empleado_combo['values'] = [f"{e['codigo']} - {e['nombre']}" for e in employees]
        empleado_combo.pack(fill='x', pady=(0,10))

        shift_records = self._get_shift_records()

        turno_combo = ttk.Combobox(main_frame, font=('Segoe UI', 10), state='readonly')
        turno_combo['values'] = [f"{t['codigo_turno']} - {str(t.get('hora_entrada'))} / {str(t.get('hora_salida'))}" for t in shift_records]
        turno_combo.pack(fill='x', pady=(0,10))

        # Fecha
        tk.Label(main_frame, text="Fecha:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        fecha_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        fecha_entry.pack(fill='x', pady=(0,10))

        # Hora Entrada
        tk.Label(main_frame, text="Hora Entrada (HH:MM):*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        entrada_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        entrada_entry.pack(fill='x', pady=(0,10))

        # Hora Salida
        tk.Label(main_frame, text="Hora Salida (HH:MM):*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        salida_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        salida_entry.pack(fill='x', pady=(0,10))

        # Prefill values
        # attendance uses keys like 'fecha_asistencia', 'codigo_empleado', 'codigo_turno', 'marca_entrada', 'marca_salida'
        fecha_val = attendance.get('fecha_asistencia') or ''
        if isinstance(fecha_val, (datetime, date)):
            fecha_val = fecha_val.strftime('%Y-%m-%d')
        fecha_entry.delete(0, tk.END)
        fecha_entry.insert(0, fecha_val)

        entrada = attendance.get('marca_entrada') or ''
        salida = attendance.get('marca_salida') or ''
        # Formatear si son datetime
        def _time_to_str(v):
            if isinstance(v, datetime):
                return v.strftime('%H:%M')
            if v is None:
                return ''
            return str(v)

        entrada_entry.insert(0, _time_to_str(entrada))
        salida_entry.insert(0, _time_to_str(salida))

        # Seleccionar empleado en combo
        codigo_emp = attendance.get('codigo_empleado') or ''
        if empleado_combo['values']:
            for i, val in enumerate(empleado_combo['values']):
                if val.startswith(str(codigo_emp)):
                    empleado_combo.current(i)
                    break

        # Seleccionar turno en combo
        codigo_turno = attendance.get('codigo_turno') or ''
        if turno_combo['values']:
            for i, val in enumerate(turno_combo['values']):
                if val.startswith(str(codigo_turno)):
                    turno_combo.current(i)
                    break

        def save_edit():
            empleado = empleado_combo.get()
            fecha = fecha_entry.get().strip()
            entrada_val = entrada_entry.get().strip()
            salida_val = salida_entry.get().strip()
            turno_sel = turno_combo.get()

            if not all([empleado, fecha, entrada_val, salida_val, turno_sel]):
                messagebox.showerror('Error', 'Complete todos los campos obligatorios (*)')
                return

            codigo_emp_new = empleado.split(' - ')[0]
            codigo_turno_new = turno_sel.split(' - ')[0]

            try:
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                datetime.strptime(f"{fecha} {entrada_val}", '%Y-%m-%d %H:%M')
                datetime.strptime(f"{fecha} {salida_val}", '%Y-%m-%d %H:%M')
            except ValueError:
                messagebox.showerror('Error', 'Formato de fecha/hora inválido')
                return

            dia = self._get_day_name(fecha_dt)

            # Llamar al servicio de actualización
            assert self.attendance_service is not None
            try:
                result = self.attendance_service.update_attendance(
                    fecha,
                    codigo_emp_new,
                    codigo_turno_new,
                    dia,
                    entrada_val,
                    salida_val,
                    0.0,
                    0.0,
                    0.0,
                )
            except Exception as exc:
                messagebox.showerror('Error', f'Error actualizando: {exc}')
                return

            if self._show_operation_result(result, title='Actualizar asistencia'):
                dialog.destroy()
                self._load_attendance_table()

        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(fill='x')

        tk.Button(
            btn_frame,
            text='Guardar',
            command=save_edit,
            font=('Segoe UI', 10, 'bold'),
            bg='#4caf50',
            fg='white',
            cursor='hand2',
            padx=30,
            pady=10
        ).pack(side='left', expand=True, padx=(0,5))

        tk.Button(
            btn_frame,
            text='Cancelar',
            command=dialog.destroy,
            font=('Segoe UI', 10),
            bg='#f44336',
            fg='white',
            cursor='hand2',
            padx=30,
            pady=10
        ).pack(side='left', expand=True, padx=(5,0))
    
    def _delete_attendance(self, attendance):
        """Elimina una asistencia"""
        if not self.attendance_service:
            messagebox.showerror("Error", "No hay conexión")
            return
        
        assert self.attendance_service is not None
        
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar registro de asistencia?\n\n"
            f"Empleado: {attendance.get('nombre_empleado')}\n"
            f"Fecha: {attendance.get('fecha_asistencia')}"
        )
        
        if result:
            result = self.attendance_service.delete_attendance(
                attendance.get('fecha_asistencia'),
                attendance.get('codigo_empleado')
            )

            if self._show_operation_result(result, title='Eliminar asistencia'):
                self._load_attendance_table()

    def _show_operation_result(self, result: OperationResult, title: str = 'Asistencias') -> bool:
        """Muestra retroalimentación consistente según el estado del resultado."""
        if result.ok:
            messagebox.showinfo(title, result.message)
            return True
        if result.status in (
            OperationStatus.NOT_FOUND,
            OperationStatus.DUPLICATE,
            OperationStatus.VALIDATION_ERROR,
        ):
            messagebox.showwarning(title, result.message)
        else:
            messagebox.showerror(title, result.message)
        return False
