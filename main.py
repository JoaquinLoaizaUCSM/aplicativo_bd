"""
Aplicativo de Gestión de Base de Datos - Entrega 5
Autor: Joaquin Armando Loaiza Cruz
Fecha: 2025-11-07
Descripción: Punto de entrada principal del aplicativo.
             Este aplicativo NO utiliza frameworks, solo conexión nativa a MySQL.
             Interfaz gráfica desarrollada con Tkinter (librería estándar de Python).
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    """
    Función principal que inicia la aplicación.
    """
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        import tkinter.messagebox
        # Si la ventana principal no se pudo crear, creamos una temporal oculta para el popup
        try:
            root = tkinter.Tk()
            root.withdraw()
        except:
            pass
            
        tkinter.messagebox.showerror("Error Fatal", f"Se ha producido un error inesperado:\n{str(e)}")
        print(f"Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
