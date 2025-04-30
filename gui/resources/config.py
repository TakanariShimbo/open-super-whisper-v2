"""
Application Configuration

This module provides configuration constants for the application.
"""


class AppConfig:
    """
    Application configuration constants.
    
    This class provides static configuration values for the application,
    such as default settings, file paths, and application metadata.
    """
    # Application metadata
    APP_NAME = "OpenSuperWhisper"
    APP_ORGANIZATION = "OpenSuperWhisper"
    
    # Default settings
    DEFAULT_API_KEY = ""
    DEFAULT_AUTO_COPY = True
    DEFAULT_ENABLE_SOUND = True
    DEFAULT_SHOW_INDICATOR = True
    
    # Asset paths
    ICON_PATH = "assets/icon.png"
    START_SOUND_PATH = "assets/start_sound.wav"
    STOP_SOUND_PATH = "assets/stop_sound.wav"
    COMPLETE_SOUND_PATH = "assets/complete_sound.wav"
    
    # UI settings
    DEFAULT_INDICATOR_DISPLAY_TIME = 3000  # 3 seconds
