"""
Módulo de configuración de estilos y tema de la aplicación.
Centraliza los colores, fuentes y configuración de widgets.
"""

import tkinter as tk
from tkinter import ttk

# Paleta de colores (Tema Profesional/Moderno)
COLORS = {
    'primary': '#1976d2',       # Azul principal
    'primary_dark': '#1565c0',  # Azul oscuro
    'secondary': '#4caf50',     # Verde (acciones positivas)
    'secondary_dark': '#388e3c',
    'danger': '#f44336',        # Rojo (errores, eliminar)
    'warning': '#ff9800',       # Naranja (alertas)
    'info': '#2196f3',          # Azul claro (info)
    'background': '#f5f5f5',    # Fondo gris claro
    'surface': '#ffffff',       # Fondo blanco (tarjetas)
    'text_primary': '#2c3e50',  # Texto principal (gris oscuro)
    'text_secondary': '#546e7a',# Texto secundario
    'sidebar_bg': '#263238',    # Fondo sidebar
    'sidebar_fg': '#eceff1',    # Texto sidebar
    'sidebar_hover': '#37474f', # Hover sidebar
    'header_bg': '#1976d2',     # Header default
}

# Fuentes
FONTS = {
    'h1': ('Segoe UI', 24, 'bold'),
    'h2': ('Segoe UI', 20, 'bold'),
    'h3': ('Segoe UI', 16, 'bold'),
    'body': ('Segoe UI', 10),
    'body_bold': ('Segoe UI', 10, 'bold'),
    'small': ('Segoe UI', 9),
    'icon_large': ('Segoe UI Emoji', 24),
    'icon_medium': ('Segoe UI Emoji', 18),
}

def configure_styles(root):
    """
    Configura los estilos globales de ttk para la aplicación.
    """
    style = ttk.Style(root)
    style.theme_use('clam')  # Base theme that allows more customization
    
    # Configuración general
    style.configure('.', 
                   background=COLORS['background'], 
                   foreground=COLORS['text_primary'], 
                   font=FONTS['body'])
    
    # Frames
    style.configure('TFrame', background=COLORS['background'])
    style.configure('Card.TFrame', background=COLORS['surface'], relief='flat')
    style.configure('Header.TFrame', background=COLORS['header_bg'])
    
    # Labels
    style.configure('TLabel', background=COLORS['background'], foreground=COLORS['text_primary'])
    style.configure('Title.TLabel', font=FONTS['h1'], foreground=COLORS['primary_dark'])
    style.configure('Subtitle.TLabel', font=FONTS['body'], foreground=COLORS['text_secondary'])
    style.configure('CardTitle.TLabel', font=FONTS['h3'], background=COLORS['surface'], foreground=COLORS['text_primary'])
    style.configure('CardBody.TLabel', font=FONTS['body'], background=COLORS['surface'], foreground=COLORS['text_secondary'])
    
    # Botones Primarios
    style.configure('Primary.TButton',
                   font=FONTS['body_bold'],
                   background=COLORS['primary'],
                   foreground='white',
                   borderwidth=0,
                   focuscolor='none',
                   padding=(15, 8))
    style.map('Primary.TButton',
              background=[('active', COLORS['primary_dark']), ('disabled', '#bdc3c7')])
              
    # Botones Secundarios (Acción positiva)
    style.configure('Success.TButton',
                   font=FONTS['body_bold'],
                   background=COLORS['secondary'],
                   foreground='white',
                   borderwidth=0,
                   focuscolor='none',
                   padding=(15, 8))
    style.map('Success.TButton',
              background=[('active', COLORS['secondary_dark'])])
              
    # Botones de Peligro
    style.configure('Danger.TButton',
                   font=FONTS['body_bold'],
                   background=COLORS['danger'],
                   foreground='white',
                   borderwidth=0,
                   focuscolor='none',
                   padding=(15, 8))
    style.map('Danger.TButton',
              background=[('active', '#d32f2f')])

    # Treeview (Tablas)
    style.configure('Treeview',
                   background=COLORS['surface'],
                   fieldbackground=COLORS['surface'],
                   foreground=COLORS['text_primary'],
                   rowheight=30,
                   font=FONTS['body'])
    style.configure('Treeview.Heading',
                   background='#e0e0e0',
                   foreground=COLORS['text_primary'],
                   font=FONTS['body_bold'],
                   relief='flat')
    style.map('Treeview',
              background=[('selected', COLORS['primary_dark'])],
              foreground=[('selected', 'white')])
              
    # Entradas de texto
    style.configure('TEntry', padding=5, relief='flat', borderwidth=1)
    
    return style
