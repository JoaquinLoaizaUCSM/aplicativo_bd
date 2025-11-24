"""
Componentes reutilizables de la interfaz gráfica.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple
from gui.styles import COLORS, FONTS

class Sidebar(tk.Frame):
    """Barra lateral de navegación."""
    
    def __init__(self, parent, app_name: str, menu_items: List[Tuple[str, str, Callable]], **kwargs):
        super().__init__(parent, bg=COLORS['sidebar_bg'], width=250, **kwargs)
        self.pack_propagate(False)
        self.menu_buttons = []
        self.on_menu_click = None
        
        self._create_logo(app_name)
        self._create_menu(menu_items)
        
    def _create_logo(self, app_name: str):
        logo_frame = tk.Frame(self, bg='#1b262c', height=100)
        logo_frame.pack(fill='x')
        logo_frame.pack_propagate(False)
        
        tk.Label(
            logo_frame,
            text="🏢",
            font=('Segoe UI Emoji', 32),
            bg='#1b262c',
            fg='white'
        ).pack(pady=(15, 5))
        
        tk.Label(
            logo_frame,
            text=app_name,
            font=('Segoe UI', 12, 'bold'),
            bg='#1b262c',
            fg='white'
        ).pack()

    def _create_menu(self, items):
        menu_frame = tk.Frame(self, bg=COLORS['sidebar_bg'])
        menu_frame.pack(fill='both', expand=True, pady=20)
        
        for i, (icon, text, command) in enumerate(items):
            btn = self._create_menu_button(menu_frame, icon, text, command, i)
            self.menu_buttons.append(btn)
            
    def _create_menu_button(self, parent, icon, text, command, index):
        btn_frame = tk.Frame(parent, bg=COLORS['sidebar_bg'])
        btn_frame.pack(fill='x', pady=1)
        
        # Wrapper command to handle visual state
        def cmd_wrapper():
            self.set_active(index)
            command()
            
        btn = tk.Button(
            btn_frame,
            text=f"  {icon}   {text}",
            command=cmd_wrapper,
            font=FONTS['body'],
            bg=COLORS['sidebar_bg'],
            fg=COLORS['sidebar_fg'],
            activebackground=COLORS['sidebar_hover'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            anchor='w',
            padx=20,
            pady=12,
            bd=0
        )
        btn.pack(fill='x')
        
        # Hover effects
        btn.bind('<Enter>', lambda e, b=btn: self._on_hover(b, True))
        btn.bind('<Leave>', lambda e, b=btn: self._on_hover(b, False))
        
        return btn
        
    def _on_hover(self, btn, entering):
        if btn['bg'] != COLORS['primary']: # Don't change if active
            btn.config(bg=COLORS['sidebar_hover'] if entering else COLORS['sidebar_bg'])

    def set_active(self, index):
        for i, btn in enumerate(self.menu_buttons):
            if i == index:
                btn.config(bg=COLORS['primary'], fg='white')
            else:
                btn.config(bg=COLORS['sidebar_bg'], fg=COLORS['sidebar_fg'])


class Header(tk.Frame):
    """Encabezado superior con estado de conexión."""
    
    def __init__(self, parent, on_config_click: Callable, **kwargs):
        super().__init__(parent, bg=COLORS['header_bg'], height=70, **kwargs)
        self.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Desconectado")
        self.info_var = tk.StringVar(value="...")
        
        self._create_widgets(on_config_click)
        
    def _create_widgets(self, on_config_click):
        content = tk.Frame(self, bg=COLORS['header_bg'])
        content.pack(fill='both', expand=True, padx=20)
        
        # Left: Status
        info_frame = tk.Frame(content, bg=COLORS['header_bg'])
        info_frame.pack(side='left', pady=10)
        
        tk.Label(
            info_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['header_bg'],
            fg='white'
        ).pack(anchor='w')
        
        tk.Label(
            info_frame,
            textvariable=self.info_var,
            font=('Segoe UI', 8),
            bg=COLORS['header_bg'],
            fg='#e3f2fd'
        ).pack(anchor='w')
        
        #Right: Config Button
        btn = tk.Button(
            content,
            text="⚙️ Configuración",
            command=on_config_click,
            font=('Segoe UI', 9),
            bg='white',
            fg=COLORS['primary'],
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        btn.pack(side='right', pady=18)

    def update_status(self, connected: bool, host: str, details: str):
        if connected:
            self.config(bg=COLORS['secondary'])
            self.children['!frame'].config(bg=COLORS['secondary']) # Content frame
            # Recursive update background for labels... simplified for now
            self.status_var.set(f"Conectado: {host}")
        else:
            self.config(bg=COLORS['danger']) # Red for disconnected
            self.status_var.set("Desconectado")
            
        self.info_var.set(details)
