from PyQt6.QtWidgets import QApplication
import qdarktheme

from .theme_colors import ThemeColors


class DesignSystemIntegration:
    """
    Design system integration with PyQtDarkTheme.

    This class is used to integrate the design system with PyQtDarkTheme.
    It is used to detect the theme state and set the theme accordingly.
    """
    
    _initialized = False
    _is_dark_theme = True
    
    @classmethod
    def initialize(cls, app: QApplication) -> None:
        """
        Initialize the design system integration.

        This method is used to initialize the design system integration.
        It is used to set the theme to auto.

        Parameters
        ----------
        app : QApplication
            The application instance
        """
        if cls._initialized:
            return
        
        try:
            # set theme to auto
            qdarktheme.setup_theme("auto")
            
            # detect theme state and save it
            cls._detect_theme_state(app)
            
            cls._initialized = True
        except Exception:
            cls._initialized = True
    
    @classmethod
    def _detect_theme_state(cls, app: QApplication) -> None:
        """
        Detect the theme state from the application palette.

        This method is used to detect the theme state from the application palette.
        It is used to set the theme state accordingly.

        Parameters
        ----------
        app : QApplication
            The application instance
        """
        try:
            palette = app.palette()
            bg = palette.color(palette.ColorRole.Window)
            cls._is_dark_theme = (bg.red() + bg.green() + bg.blue()) / 3 < 128
        except:
            cls._is_dark_theme = True
    
    @classmethod
    def is_dark_theme(cls) -> bool:
        """
        Check if the current theme is dark.

        This method is used to check if the current theme is dark.
        It is used to return the theme state accordingly.

        Returns
        -------
        bool
            True if the current theme is dark, False otherwise
        """
        return cls._is_dark_theme
    
    @classmethod
    def get_color(cls, color_name: str) -> str:
        """
        Get a color value by name for the current theme.
        
        Parameters
        ----------
        color_name : str
            Name of the color (e.g., 'primary', 'error', 'text_primary')
            
        Returns
        -------
        str
            Hex color value
        """
        return ThemeColors.get_color(color_name, cls._is_dark_theme)
    
    @classmethod
    def get_rgba_color(cls, color_name: str) -> tuple:
        """
        Get an RGBA color tuple by name for the current theme.
        
        Parameters
        ----------
        color_name : str
            Name of the color (must end with '_transparent')
            
        Returns
        -------
        tuple
            RGBA color tuple (r, g, b, a)
        """
        return ThemeColors.get_rgba_color(color_name, cls._is_dark_theme)