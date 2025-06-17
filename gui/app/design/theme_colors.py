"""
Theme Colors for PyQtDarkTheme Integration

Centralized color definitions for the application.
"""


class ThemeColors:
    """
    Provides theme-appropriate colors based on current theme.

    This class provides theme-appropriate colors based on current theme.
    It is used to get the colors for the application.   
    """
    
    # Dark theme colors
    DARK = {
        # Background colors
        "background": "#202124",
        "background_elevated": "#303134",
        "background_transparent": (48, 49, 52, 220),  # RGBA tuple for QColor
        
        # Text colors
        "text_primary": "#e8eaed",
        "text_secondary": "#9aa0a6",
        "text_placeholder": "#9aa0a6",
        
        # Accent colors
        "primary": "#8ab4f7",        # Blue
        "error": "#f28b82",          # Red
        "success": "#8ab4f7",        # Blue (same as primary)
        "warning": "#fdd663",        # Yellow
        "info": "#9aa0a6",           # Gray
        
        # HTML background (for text editor)
        "html_background": "#303134",
        "html_text": "#e8eaed",
        "html_placeholder": "#9aa0a6",
    }
    
    # Light theme colors
    LIGHT = {
        # Background colors
        "background": "#f8f9fa",
        "background_elevated": "#ffffff",
        "background_transparent": (248, 249, 250, 220),  # RGBA tuple for QColor
        
        # Text colors
        "text_primary": "#3c4043",
        "text_secondary": "#5f6368",
        "text_placeholder": "#80868b",
        
        # Accent colors
        "primary": "#1a73e8",        # Blue
        "error": "#ea4335",          # Red
        "success": "#1a73e8",        # Blue (same as primary)
        "warning": "#fbbc04",        # Yellow
        "info": "#5f6368",           # Gray
        
        # HTML background (for text editor)
        "html_background": "#ffffff",
        "html_text": "#3c4043",
        "html_placeholder": "#80868b",
    }
    
    @classmethod
    def get_color(cls, color_name: str, is_dark: bool) -> str:
        """
        Get a color value by name for the current theme.
        
        Parameters
        ----------
        color_name : str
            Name of the color (e.g., 'primary', 'error', 'text_primary')
        is_dark : bool
            Whether dark theme is active
            
        Returns
        -------
        str
            Hex color value
        """
        theme_colors = cls.DARK if is_dark else cls.LIGHT
        return theme_colors.get(color_name, "#000000")
    
    @classmethod
    def get_rgba_color(cls, color_name: str, is_dark: bool) -> tuple:
        """
        Get an RGBA color tuple by name for the current theme.
        
        Parameters
        ----------
        color_name : str
            Name of the color (must end with '_transparent')
        is_dark : bool
            Whether dark theme is active
            
        Returns
        -------
        tuple
            RGBA color tuple (r, g, b, a)
        """
        theme_colors = cls.DARK if is_dark else cls.LIGHT
        return theme_colors.get(color_name, (0, 0, 0, 255))