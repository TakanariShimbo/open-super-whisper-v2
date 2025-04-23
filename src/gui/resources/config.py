"""
Application Default Configuration

This module defines default values used throughout the application.
Centralizing these settings makes it easier to update them when needed.
"""

class AppConfig:
    """Class that manages application-wide configuration settings"""
    
    # Application settings
    APP_NAME = "QtWhisperRemake"
    APP_ORGANIZATION = "QtWhisperRemake"
    
    # Authentication settings
    DEFAULT_API_KEY = ""
    
    # Feature settings
    DEFAULT_HOTKEY = "ctrl+shift+r"
    DEFAULT_AUTO_COPY = True
    DEFAULT_ENABLE_SOUND = True
    DEFAULT_SHOW_INDICATOR = True
    DEFAULT_MODEL = "gpt-4o-transcribe"
    
    # Language settings
    DEFAULT_LANGUAGE = ""  # Empty string means auto-detect
    
    # Sound file paths
    START_SOUND_PATH = "assets/start_sound.wav"
    STOP_SOUND_PATH = "assets/stop_sound.wav"
    COMPLETE_SOUND_PATH = "assets/complete_sound.wav"
    
    # InstructionSet settings
    DEFAULT_INSTRUCTION_SET_NAME = "Default"
    INSTRUCTION_SETS_SETTINGS_PREFIX = "InstructionSets"
