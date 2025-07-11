"""
Gestor de temas - Responsabilidad única de gestión de temas
"""

from PySide6.QtWidgets import QMainWindow
from .light_theme import LightThemeStyles
from .dark_theme import DarkThemeStyles

class ThemeManager:
    """
    Gestor de temas con responsabilidad única
    Aplica el patrón Strategy para alternar entre temas
    """
    
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.is_dark_theme = False
        self.light_theme = LightThemeStyles()
        self.dark_theme = DarkThemeStyles()
    
    def toggle_theme(self) -> None:
        """Alterna entre tema claro y oscuro"""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_current_theme()
        self._notify_theme_change()
    
    def apply_current_theme(self) -> None:
        """Aplica el tema actual"""
        if self.is_dark_theme:
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_light_theme(self) -> None:
        """Aplica tema claro"""
        stylesheet = self.light_theme.get_complete_stylesheet()
        self.main_window.setStyleSheet(stylesheet)
    
    def _apply_dark_theme(self) -> None:
        """Aplica tema oscuro"""
        stylesheet = self.dark_theme.get_complete_stylesheet()
        self.main_window.setStyleSheet(stylesheet)
    
    def _notify_theme_change(self) -> None:
        """Notifica cambio de tema"""
        theme_name = "Oscuro" if self.is_dark_theme else "Claro"
        if hasattr(self.main_window, 'status_bar'):
            self.main_window.status_bar.showMessage(f"🎨 Tema cambiado a: {theme_name}")
    
    def get_current_theme_name(self) -> str:
        """Retorna el nombre del tema actual"""
        return "Oscuro" if self.is_dark_theme else "Claro"