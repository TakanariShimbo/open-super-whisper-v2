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
    COPY_TO_CLIPBOARD = "Copy to Clipboard"
    AUTO_COPY_BUTTON = "Auto-Copy"
    SOUND_BUTTON = "Enable Sounds"
    INDICATOR_BUTTON = "Show Indicator"
    EXIT_APP = "Exit"
    
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
    STATUS_AUTO_COPY_ENABLED = "Auto-copy enabled"
    STATUS_AUTO_COPY_DISABLED = "Auto-copy disabled"
    STATUS_SOUND_ENABLED = "Notification sounds enabled"
    STATUS_SOUND_DISABLED = "Notification sounds disabled"
    STATUS_INDICATOR_SHOWN = "Status indicator enabled"
    STATUS_INDICATOR_HIDDEN = "Status indicator disabled"
    STATUS_INSTRUCTION_SET_ACTIVE = "Instruction set '{}' activated"
    
    # UI Elements
    UI_RECORDING_INDICATOR = "●"
    STATUS_TIMER_INITIAL = "00:00"
    
    # Dialog titles
    DIALOG_API_KEY_TITLE = "API Key Settings"
    DIALOG_HOTKEY_TITLE = "Global Hotkey Settings"
    DIALOG_INSTRUCTION_SETS_TITLE = "Instruction Sets"
    
    # Instruction Sets Dialog
    INSTRUCTION_SETS_LIST_LABEL = "Instruction Sets:"
    INSTRUCTION_SET_ADD_BUTTON = "New"
    INSTRUCTION_SET_RENAME_BUTTON = "Rename"
    INSTRUCTION_SET_DELETE_BUTTON = "Delete"
    INSTRUCTION_SET_ACTIVATE_BUTTON = "Activate"
    INSTRUCTION_SET_SAVE_BUTTON = "Save"
    
    ## Vocabulary Tab
    VOCABULARY_LABEL = "Custom Vocabulary:"
    VOCABULARY_HELP = "Enter words or phrases to improve transcription accuracy. One item per line."
    VOCABULARY_TAB_NAME = "Vocabulary"
    
    ## Instructions Tab
    INSTRUCTIONS_LABEL = "System Instructions:"
    INSTRUCTIONS_HELP = "Enter system instructions to control transcription behavior. One instruction per line."
    INSTRUCTIONS_TAB_NAME = "Instructions"
    
    ## Settings Tab
    SETTINGS_HELP = "Configure language and model settings for this instruction set. These settings will be used when this instruction set is active."
    LANGUAGE_AND_MODEL_TAB_NAME = "Language & Model"
    LANGUAGE_LABEL = "Language:"
    MODEL_LABEL = "Transcription Model:"
    
    ## Instruction Set Dialogs
    NEW_INSTRUCTION_SET_TITLE = "New Instruction Set"
    NEW_INSTRUCTION_SET_PROMPT = "Enter a name for the new instruction set:"
    RENAME_INSTRUCTION_SET_TITLE = "Rename Instruction Set"
    RENAME_INSTRUCTION_SET_PROMPT = "Enter a new name for the instruction set:"
    NAME_EXISTS_TITLE = "Name Exists"
    NAME_EXISTS_MESSAGE = "An instruction set with the name '{}' already exists."
    CONFIRM_DELETION_TITLE = "Confirm Deletion"
    CONFIRM_DELETION_MESSAGE = "Are you sure you want to delete the instruction set '{}'?"
    CHANGES_SAVED_TITLE = "Changes Saved"
    CHANGES_SAVED_MESSAGE = "Changes to instruction set '{}' have been saved."
    SET_ACTIVATED_TITLE = "Set Activated"
    SET_ACTIVATED_MESSAGE = "Instruction set '{}' has been activated."
    
    # API Key Dialog
    API_KEY_DESCRIPTION = "Enter your OpenAI API key to use transcription services. The key will be stored locally on your device."
    API_KEY_LABEL = "API Key:"
    API_KEY_PLACEHOLDER = "Enter your OpenAI API key..."
    API_KEY_SHOW_BUTTON = "Show"
    API_KEY_HIDE_BUTTON = "Hide"
    API_KEY_VALIDATE_BUTTON = "Validate Key"
    API_KEY_VALIDATION_ERROR_TITLE = "Validation Error"
    API_KEY_EMPTY_ERROR = "API key cannot be empty."
    API_KEY_VALID_TITLE = "API Key Valid"
    API_KEY_VALID_MESSAGE = "The API key is valid and has been verified."
    API_KEY_VALIDATION_ERROR_MESSAGE = "Failed to validate API key: {}"
    
    # Hotkey Dialog
    HOTKEY_DESCRIPTION = "Set a global hotkey combination for starting and stopping recording. Press the desired key combination in the input field below."
    HOTKEY_LABEL = "Hotkey:"
    HOTKEY_PLACEHOLDER = "Click here and press hotkey combination..."
    HOTKEY_CLEAR_BUTTON = "Clear"
    HOTKEY_EXAMPLES = "Examples: ctrl+shift+r, alt+w, ctrl+alt+s"
    HOTKEY_VALIDATION_ERROR = "Please set a hotkey combination."
    
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
    HOTKEY_INFO_MESSAGE = "You can start/stop recording by pressing {}.\\nThis works even when the app is minimized or in the background."
    
    # Tray menu
    TRAY_SHOW = "Show Application"
    TRAY_RECORD = "Start/Stop Recording"
    TRAY_EXIT = "Exit"
