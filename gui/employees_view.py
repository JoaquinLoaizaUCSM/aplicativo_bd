"""
Vista del módulo de Empleados
Autor: Joaquin Armando Loaiza Cruz
Fecha: 2025-11-11
Descripción: Gestión completa de empleados con CRUD usando procedimientos almacenados
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.employee_service import EmployeeService
from database.reference_service import ReferenceService
from database.operation_result import OperationResult, OperationStatus


class EmployeesView:
    """Vista para gestionar empleados"""
    
    def __init__(self, parent_frame: tk.Frame, 
                 employee_service: Optional[EmployeeService],
                 reference_service: Optional[ReferenceService],
                 refresh_callback: Optional[Callable] = None):
        """
        Inicializa la vista de empleados.
        
        Args:
            parent_frame: Frame contenedor principal
            employee_service: Servicio de empleados
            reference_service: Servicio de referencias
            refresh_callback: Callback para refrescar la vista
        """
        self.parent_frame = parent_frame
        self.employee_service = employee_service
        self.reference_service = reference_service
        self.refresh_callback = refresh_callback
        self.container = None
        
    def render(self):
        """Renderiza la vista completa de empleados"""
        # Limpiar frame padre
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Verificar conexión
        if not self.employee_service:
            self._show_no_connection()
            return
        
        # Título y botón nuevo
        self._create_header()
        
        # Contenedor principal
        main_container = tk.Frame(self.parent_frame, bg='#f5f5f5')
        main_container.pack(fill='both', expand=True, padx=30, pady=(0, 30))
        
        # Búsqueda
        self._create_search_bar(main_container)
        
        # Tabla de empleados
        self.container = tk.Frame(main_container, bg='#f5f5f5')
        self.container.pack(fill='both', expand=True, pady=(0, 10))
        
        # Cargar datos
        self._load_employees_table()
    
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
            text="Por favor, conecte a la base de datos usando el botón 'Configurar' en la barra superior.",
            font=('Segoe UI', 11),
            bg='#ffebee',
            fg='#d32f2f'
        ).pack(pady=(0, 50))
    
    def _create_header(self):
        """Crea el encabezado con título y botón nuevo"""
        title_frame = tk.Frame(self.parent_frame, bg='white', height=80)
        title_frame.pack(fill='x', padx=30, pady=(30, 20))
        title_frame.pack_propagate(False)
        
        title_content = tk.Frame(title_frame, bg='white')
        title_content.pack(side='left', expand=True)
        
        tk.Label(
            title_content,
            text="👥",
            font=('Segoe UI', 28),
            bg='white'
        ).pack(side='left', padx=(0, 15))
        
        tk.Label(
            title_content,
            text="Gestión de Empleados",
            font=('Segoe UI', 20, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side='left')
        
        # Botón Nuevo Empleado
        tk.Button(
            title_frame,
            text="➕ Nuevo Empleado",
            command=self._create_employee_dialog,
            font=('Segoe UI', 10, 'bold'),
            bg='#2196f3',
            fg='white',
            activebackground='#1976d2',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side='right')
    
    def _create_search_bar(self, parent):
        """Crea la barra de búsqueda"""
        search_frame = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)
        search_frame.pack(fill='x', pady=(0, 20))
        
        search_content = tk.Frame(search_frame, bg='white', padx=20, pady=15)
        search_content.pack(fill='x')
        
        tk.Label(
            search_content,
            text="🔍",
            font=('Segoe UI', 14),
            bg='white'
        ).pack(side='left', padx=(0, 10))
        
        tk.Label(
            search_content,
            text="Buscar Empleado",
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(side='left')
        
        search_entry = tk.Entry(
            search_content,
            font=('Segoe UI', 10),
            relief='solid',
            borderwidth=1,
            width=40
        )
        search_entry.pack(side='left', padx=(20, 10))
        search_entry.insert(0, "Código, nombre o DNI...")
        search_entry.config(fg='#90a4ae')
        
        def on_focus_in(e):
            if search_entry.get() == "Código, nombre o DNI...":
                search_entry.delete(0, tk.END)
                search_entry.config(fg='#2c3e50')
        
        def on_focus_out(e):
            if not search_entry.get():
                search_entry.insert(0, "Código, nombre o DNI...")
                search_entry.config(fg='#90a4ae')
        
        def do_search():
            term = search_entry.get().strip()
            if term and term != "Código, nombre o DNI...":
                self._load_employees_table(term)
            else:
                self._load_employees_table()
        
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        search_entry.bind('<Return>', lambda e: do_search())
        
        tk.Button(
            search_content,
            text="Buscar",
            command=do_search,
            font=('Segoe UI', 9, 'bold'),
            bg='#2196f3',
            fg='white',
            activebackground='#1976d2',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        ).pack(side='left')
        
        tk.Button(
            search_content,
            text="🔄 Todos",
            command=lambda: self._load_employees_table(),
            font=('Segoe UI', 9),
            bg='#4caf50',
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        ).pack(side='left', padx=(5, 0))
    
    def _load_employees_table(self, search_term=None):
        """Carga la tabla de empleados desde la base de datos"""
        # Limpiar contenedor
        if self.container is None:
            return
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Mostrar indicador de carga
        loading_label = tk.Label(
            self.container,
            text="⏳ Cargando empleados...",
            font=('Segoe UI', 12),
            bg='#f5f5f5',
            fg='#546e7a'
        )
        loading_label.pack(pady=50)
        self.container.update()

        # Verificar servicio
        assert self.employee_service is not None
        
        # Ejecutar carga de datos (simulada asíncrona para UI)
        self.container.after(50, lambda: self._render_table_data(search_term))

    def _render_table_data(self, search_term):
        """Renderiza los datos de la tabla después de cargar"""
        if self.container is None or self.employee_service is None:
            return

        # Limpiar loading
        for widget in self.container.winfo_children():
            widget.destroy()

        # Frame de tabla con scroll
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
            ("CÓDIGO", 0.08),
            ("NOMBRE", 0.20),
            ("DNI", 0.10),
            ("PUESTO", 0.16),
            ("UNIDAD ORGANIZATIVA", 0.16),
            ("CENTRO DE COSTE", 0.14),
            ("ACCIONES", 0.16)
        ]
        
        for header_text, width in headers:
            tk.Label(
                header_frame,
                text=header_text,
                font=('Segoe UI', 9, 'bold'),
                bg='#37474f',
                fg='white',
                anchor='w',
                padx=15
            ).place(relx=sum([h[1] for h in headers[:headers.index((header_text, width))]]), 
                   rely=0, relwidth=width, relheight=1)
        
        # Obtener datos
        try:
            if search_term:
                employees = self.employee_service.search_employees(search_term)
            else:
                employees = self.employee_service.get_all_employees()
            
            if not employees:
                tk.Label(
                    table_frame,
                    text="No se encontraron empleados" if search_term else "No hay empleados registrados",
                    font=('Segoe UI', 12),
                    bg='white',
                    fg='#546e7a'
                ).pack(pady=50)
            else:
                # Renderizar filas
                for idx, employee in enumerate(employees):
                    row_bg = '#f8f9fa' if idx % 2 == 0 else 'white'
                    
                    row_frame = tk.Frame(table_frame, bg=row_bg, height=50)
                    row_frame.pack(fill='x')
                    row_frame.pack_propagate(False)
                    
                    # Datos
                    data = [
                        employee.get('codigo', ''),
                        employee.get('nombre', ''),
                        employee.get('dni', ''),
                        employee.get('puesto', ''),
                        employee.get('unidad_organizativa', ''),
                        employee.get('centro_coste', '')
                    ]
                    
                    for i, (text, width) in enumerate(zip(data, [h[1] for h in headers[:-1]])):
                        tk.Label(
                            row_frame,
                            text=str(text),
                            font=('Segoe UI', 9),
                            bg=row_bg,
                            fg='#2c3e50',
                            anchor='w',
                            padx=15
                        ).place(relx=sum([h[1] for h in headers[:i]]), 
                               rely=0, relwidth=width, relheight=1)
                    
                    # Botones de acción
                    actions_frame = tk.Frame(row_frame, bg=row_bg)
                    actions_frame.place(relx=0.92, rely=0.5, anchor='center')
                    
                    tk.Button(
                        actions_frame,
                        text="✏️ Editar",
                        command=lambda e=employee: self._edit_employee_dialog(e),
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
                        command=lambda e=employee: self._delete_employee(e),
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
        
        # SIEMPRE empaquetar el canvas y scrollbar al final
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_employee_dialog(self):
        """Diálogo para crear nuevo empleado"""
        if not self.employee_service or not self.reference_service:
            messagebox.showerror("Error", "No hay conexión a la base de datos")
            return
        
        assert self.employee_service is not None
        assert self.reference_service is not None
        
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Nuevo Empleado")
        dialog.geometry("500x650")
        dialog.transient(self.parent_frame.winfo_toplevel())
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 325
        dialog.geometry(f'500x650+{x}+{y}')
        
        # Contenido
        main_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        tk.Label(
            main_frame,
            text="➕ Crear Nuevo Empleado",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(0, 20))
        
        # Generar código
        new_code = self.employee_service.generate_employee_code() or "E00000"
        
        # Código (readonly)
        tk.Label(main_frame, text="Código:", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        code_entry = tk.Entry(main_frame, font=('Segoe UI', 10), state='readonly')
        code_entry.pack(fill='x', pady=(0,10))
        code_entry.config(state='normal')
        code_entry.insert(0, new_code)
        code_entry.config(state='readonly')
        
        # Nombre
        tk.Label(main_frame, text="Nombre Completo:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        name_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        name_entry.pack(fill='x', pady=(0,10))
        
        # DNI
        tk.Label(main_frame, text="DNI (8 dígitos):*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        dni_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        dni_entry.pack(fill='x', pady=(0,10))
        
        # Puesto
        tk.Label(main_frame, text="Puesto:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        puesto_combo = ttk.Combobox(main_frame, font=('Segoe UI', 10), state='readonly')
        
        # Intentar obtener áreas, forzando refresco si está vacío
        areas = self.reference_service.get_areas()
        if not areas:
            areas = self.reference_service.get_areas(force_refresh=True) or []
            
        puesto_combo['values'] = [a['puesto'] for a in areas]
        puesto_combo.pack(fill='x', pady=(0,10))
        if puesto_combo['values']:
            puesto_combo.current(0)
        
        # Centro de Coste
        tk.Label(main_frame, text="Centro de Coste:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        cc_combo = ttk.Combobox(main_frame, font=('Segoe UI', 10), state='readonly')
        
        # Intentar obtener centros, forzando refresco si está vacío
        centros = self.reference_service.get_cost_centers()
        if not centros:
            centros = self.reference_service.get_cost_centers(force_refresh=True) or []
            
        cc_combo['values'] = [f"{c['codigo']} - {c['nombre']}" for c in centros]
        cc_combo.pack(fill='x', pady=(0,10))
        if cc_combo['values']:
            cc_combo.current(0)
        
        # Subdivisión 
        tk.Label(main_frame, text="Subdivisión:", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        subdiv_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        subdiv_entry.pack(fill='x', pady=(0,20))
        
        def save_employee():
            nombre = name_entry.get().strip()
            dni = dni_entry.get().strip()
            puesto = puesto_combo.get()
            cc = cc_combo.get()
            subdiv = subdiv_entry.get().strip() or None
            
            if not all([nombre, dni, puesto, cc]):
                messagebox.showerror("Error", "Complete todos los campos obligatorios (*)")
                return
            
            if len(dni) != 8 or not dni.isdigit():
                messagebox.showerror("Error", "El DNI debe tener 8 dígitos")
                return
            
            assert self.employee_service is not None
            codigo_cc = cc.split(' - ')[0]
            
            result = self.employee_service.create_employee(
                new_code, nombre, dni, puesto, codigo_cc, subdiv
            )

            if self._show_employee_operation_result(result, title="Crear empleado"):
                dialog.destroy()
                self._load_employees_table()
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(fill='x', pady=(10,0))
        
        tk.Button(
            btn_frame,
            text="Guardar",
            command=save_employee,
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
    
    def _edit_employee_dialog(self, employee):
        """Diálogo para editar empleado"""
        if not self.employee_service or not self.reference_service:
            messagebox.showerror("Error", "No hay conexión a la base de datos")
            return
        
        assert self.employee_service is not None
        assert self.reference_service is not None
        
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title(f"Editar - {employee.get('codigo')}")
        dialog.geometry("500x650")
        dialog.transient(self.parent_frame.winfo_toplevel())
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 325
        dialog.geometry(f'500x650+{x}+{y}')
        
        # Contenido
        main_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        tk.Label(
            main_frame,
            text=f"✏️ Editar Empleado - {employee.get('codigo')}",
            font=('Segoe UI', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=(0, 20))
        
        # Código (readonly)
        tk.Label(main_frame, text="Código:", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        code_entry = tk.Entry(main_frame, font=('Segoe UI', 10), state='readonly')
        code_entry.pack(fill='x', pady=(0,10))
        code_entry.config(state='normal')
        code_entry.insert(0, employee.get('codigo'))
        code_entry.config(state='readonly')
        
        # Nombre
        tk.Label(main_frame, text="Nombre Completo:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        name_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        name_entry.insert(0, employee.get('nombre', ''))
        name_entry.pack(fill='x', pady=(0,10))
        
        # DNI
        tk.Label(main_frame, text="DNI (8 dígitos):*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        dni_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        dni_entry.insert(0, employee.get('dni', ''))
        dni_entry.pack(fill='x', pady=(0,10))
        
        # Puesto
        tk.Label(main_frame, text="Puesto:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        puesto_combo = ttk.Combobox(main_frame, font=('Segoe UI', 10), state='readonly')
        
        # Intentar obtener áreas, forzando refresco si está vacío
        areas = self.reference_service.get_areas()
        if not areas:
            areas = self.reference_service.get_areas(force_refresh=True) or []
            
        puesto_combo['values'] = [a['puesto'] for a in areas]
        puesto_combo.pack(fill='x', pady=(0,10))
        current_puesto = employee.get('puesto', '')
        if current_puesto in puesto_combo['values']:
            puesto_combo.set(current_puesto)
        elif puesto_combo['values']:
            puesto_combo.current(0)
        
        # Centro de Coste
        tk.Label(main_frame, text="Centro de Coste:*", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        cc_combo = ttk.Combobox(main_frame, font=('Segoe UI', 10), state='readonly')
        
        # Intentar obtener centros, forzando refresco si está vacío
        centros = self.reference_service.get_cost_centers()
        if not centros:
            centros = self.reference_service.get_cost_centers(force_refresh=True) or []
            
        cc_combo['values'] = [f"{c['codigo']} - {c['nombre']}" for c in centros]
        cc_combo.pack(fill='x', pady=(0,10))
        current_cc = employee.get('centro_coste', '')
        for val in cc_combo['values']:
            if current_cc in val:
                cc_combo.set(val)
                break
        else:
            if cc_combo['values']:
                cc_combo.current(0)
        
        # Subdivisión
        tk.Label(main_frame, text="Subdivisión (Opcional):", font=('Segoe UI', 10), bg='white', anchor='w').pack(fill='x', pady=(5,2))
        subdiv_entry = tk.Entry(main_frame, font=('Segoe UI', 10))
        subdiv_entry.insert(0, employee.get('subdivision', '') or '')
        subdiv_entry.pack(fill='x', pady=(0,20))
        
        def update_employee():
            nombre = name_entry.get().strip()
            dni = dni_entry.get().strip()
            puesto = puesto_combo.get()
            cc = cc_combo.get()
            subdiv = subdiv_entry.get().strip() or None
            
            if not all([nombre, dni, puesto, cc]):
                messagebox.showerror("Error", "Complete todos los campos obligatorios (*)")
                return
            
            if len(dni) != 8 or not dni.isdigit():
                messagebox.showerror("Error", "El DNI debe tener 8 dígitos")
                return
            
            assert self.employee_service is not None
            codigo_cc = cc.split(' - ')[0]
            
            result = self.employee_service.update_employee(
                employee.get('codigo'), nombre, dni, puesto, codigo_cc, subdiv
            )

            if self._show_employee_operation_result(result, title="Actualizar empleado"):
                dialog.destroy()
                self._load_employees_table()
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(fill='x', pady=(10,0))
        
        tk.Button(
            btn_frame,
            text="Actualizar",
            command=update_employee,
            font=('Segoe UI', 10, 'bold'),
            bg='#ff9800',
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
    
    def _delete_employee(self, employee):
        """Elimina un empleado"""
        if not self.employee_service:
            messagebox.showerror("Error", "No hay conexión a la base de datos")
            return
        
        assert self.employee_service is not None
        
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar al empleado?\n\n"
            f"Código: {employee.get('codigo')}\n"
            f"Nombre: {employee.get('nombre')}\n\n"
            f"⚠️ Se eliminarán todos sus registros de asistencia."
        )
        
        if result:
            result = self.employee_service.delete_employee(employee.get('codigo'))

            if self._show_employee_operation_result(result, title="Eliminar empleado"):
                self._load_employees_table()

    def _show_employee_operation_result(self, result: OperationResult, title: str) -> bool:
        """Muestra mensajes consistentes en función del estado del resultado."""
        if result.ok:
            messagebox.showinfo(title, result.message)
            return True
        if result.status in (
            OperationStatus.NOT_FOUND,
            OperationStatus.VALIDATION_ERROR,
            OperationStatus.DUPLICATE,
        ):
            messagebox.showwarning(title, result.message)
        else:
            messagebox.showerror(title, result.message)
        return False
