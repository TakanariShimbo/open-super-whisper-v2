"""
Application Labels and Text

This module provides text labels for the application user interface.
"""


class AppLabels:
    """
    Application text labels.
    
    This class provides static text labels for the application user interface,
    allowing for easier localization and consistent wording.
    """
    # Application metadata
    APP_TITLE = "Open Super Whisper"
    
    # Button labels
    RECORD_START_BUTTON = "Start Recording"
    RECORD_STOP_BUTTON = "Stop Recording"
    API_KEY_SETTINGS = "API Key Settings"
    HOTKEY_SETTINGS = "Hotkey Settings"
    INSTRUCTION_SETS_BUTTON = "Instruction Sets"
    CHANGE_INSTRUCTION_SET = "Change Instruction Set"
    COPY_TO_CLIPBOARD = "Copy to Clipboard"
    AUTO_COPY_BUTTON = "Auto-Copy"
    SOUND_BUTTON = "Enable Sounds"
    INDICATOR_BUTTON = "Show Indicator"
    EXIT_APP = "Exit"
    
    # Instruction Set Display
    NO_INSTRUCTION_SET_ACTIVE = "No Instruction Set Active"
    
    # Language options
    LANGUAGE_LABEL = "Language:"
    AUTO_DETECT = "Auto-detect"
    LANGUAGE_ENGLISH = "English"
    LANGUAGE_SPANISH = "Spanish"
    LANGUAGE_FRENCH = "French"
    LANGUAGE_GERMAN = "German"
    LANGUAGE_ITALIAN = "Italian"
    LANGUAGE_PORTUGUESE = "Portuguese"
    LANGUAGE_JAPANESE = "Japanese"
    LANGUAGE_KOREAN = "Korean"
    LANGUAGE_CHINESE = "Chinese"
    LANGUAGE_RUSSIAN = "Russian"
    
    # Model options
    MODEL_LABEL = "Model:"
    
    # Transcription UI
    TRANSCRIPTION_TITLE = "Transcription"
    TRANSCRIPTION_PLACEHOLDER = "Transcription will appear here..."
    
    # Status messages
    STATUS_READY = "Ready"
    STATUS_RECORDING = "Recording..."
    STATUS_TRANSCRIBING = "Transcribing..."
    STATUS_TRANSCRIPTION_COMPLETE = "Transcription complete"
    STATUS_COPIED = "Copied to clipboard"
    STATUS_API_KEY_SAVED = "API key saved"
    STATUS_HOTKEY_SET = "Hotkey set to '{}'"
    STATUS_MODEL_CHANGED = "Model changed to {}"
    STATUS_AUTO_COPY_ENABLED = "Auto-copy enabled"
    STATUS_AUTO_COPY_DISABLED = "Auto-copy disabled"
    STATUS_SOUND_ENABLED = "Notification sounds enabled"
    STATUS_SOUND_DISABLED = "Notification sounds disabled"
    STATUS_INDICATOR_SHOWN = "Status indicator enabled"
    STATUS_INDICATOR_HIDDEN = "Status indicator disabled"
    STATUS_INSTRUCTION_SET_ACTIVE = "Instruction set '{}' activated"
    
    # Dialog titles
    DIALOG_API_KEY_TITLE = "API Key Settings"
    DIALOG_HOTKEY_TITLE = "Global Hotkey Settings"
    DIALOG_INSTRUCTION_SETS_TITLE = "Instruction Sets"
    
    # Error messages
    ERROR_TITLE = "Error"
    ERROR_API_KEY_MISSING = "API Key is missing or invalid"
    ERROR_API_KEY_REQUIRED = "API Key is required to use this feature"
    ERROR_TRANSCRIPTION = "Transcription error: {}"
    ERROR_SYSTEM_TRAY = "System tray is not supported on this system"
    ERROR_HOTKEY = "Failed to register hotkey: {}"
    
    # Info messages
    INFO_TITLE = "Information"
    INFO_TRAY_MINIMIZED = "Application is still running in the system tray"
    
    # Hotkey info
    HOTKEY_INFO_TITLE = "Hotkey Configuration"
    HOTKEY_INFO_MESSAGE = "You can start/stop recording by pressing {}.\nThis works even when the app is minimized or in the background."
    
    # Tray menu
    TRAY_SHOW = "Show Application"
    TRAY_RECORD = "Start/Stop Recording"
    TRAY_EXIT = "Exit"
