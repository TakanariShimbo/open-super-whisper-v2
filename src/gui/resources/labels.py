"""
Application UI Text Labels

This module defines the text labels used throughout the application UI.
Centralizing the text makes it easier to maintain consistency and to
support internationalization in the future.
"""

class AppLabels:
    """Class that manages application-wide UI text labels"""
    
    # Application basic information
    APP_TITLE = "Qt Whisper Remake"
    
    # Main window
    RECORD_START_BUTTON = "Start Recording"
    RECORD_STOP_BUTTON = "Stop Recording"
    LANGUAGE_LABEL = "Language:"
    MODEL_LABEL = "Model:"
    AUTO_DETECT = "Auto-detect"
    TRANSCRIPTION_TITLE = "Transcription Results"
    TRANSCRIPTION_PLACEHOLDER = "Transcription will appear here..."
    STATUS_READY = "Ready"
    
    # Toolbar items
    API_KEY_SETTINGS = "API Key Settings"
    INSTRUCTION_SETS = "Instruction Sets"
    INSTRUCTION_SETS_BUTTON = "Instruction Sets"
    COPY_TO_CLIPBOARD = "Copy to Clipboard"
    HOTKEY_SETTINGS = "Hotkey Settings"
    AUTO_COPY = "Auto Copy"
    AUTO_COPY_BUTTON = "Auto Copy"
    SOUND_NOTIFICATION = "Sound Notifications"
    SOUND_BUTTON = "Sound"
    STATUS_INDICATOR = "Status Indicator"
    INDICATOR_BUTTON = "Indicator"
    EXIT_APP = "Exit Application"
    
    # Status messages
    STATUS_RECORDING = "Recording..."
    STATUS_TRANSCRIBING = "Transcribing..."
    STATUS_TRANSCRIBED = "Transcription completed"
    STATUS_TRANSCRIBED_COPIED = "Transcription completed and copied to clipboard"
    STATUS_COPIED = "Copied to clipboard"
    STATUS_API_KEY_SAVED = "API key saved"
    STATUS_HOTKEY_SET = "Hotkey set to {0}"
    STATUS_AUTO_COPY_ENABLED = "Auto copy enabled"
    STATUS_AUTO_COPY_DISABLED = "Auto copy disabled"
    STATUS_SOUND_ENABLED = "Sound notifications enabled"
    STATUS_SOUND_DISABLED = "Sound notifications disabled"
    STATUS_INDICATOR_SHOWN = "Status indicator enabled"
    STATUS_INDICATOR_HIDDEN = "Status indicator disabled"
    STATUS_VOCABULARY_ADDED = "Added {0} vocabulary items"
    STATUS_INSTRUCTIONS_SET = "Set {0} system instructions"
    STATUS_MODEL_CHANGED = "Changed transcription model to '{0}'"
    STATUS_INSTRUCTION_SET_ACTIVE = "Activated instruction set '{0}'"
    STATUS_TRANSCRIPTION_COMPLETE = "Transcription completed"
    
    # API key dialog
    API_KEY_DIALOG_TITLE = "OpenAI API Key"
    API_KEY_LABEL = "API Key:"
    API_KEY_INFO = "An OpenAI API key is required to use this application. You can get one from https://platform.openai.com/api-keys."
    SAVE_BUTTON = "Save"
    CANCEL_BUTTON = "Cancel"
    
    # Warning messages
    WARNING_TITLE = "Warning"
    APIKEY_EMPTY_WARNING = "Please enter an API key."
    APIKEY_TOO_SHORT_WARNING = "The API key format appears to be invalid."
    
    # Common button labels
    OK_BUTTON = "OK"
    APPLY_BUTTON = "Apply"
    YES_BUTTON = "Yes"
    NO_BUTTON = "No"
    
    # Vocabulary and system instructions labels
    VOCABULARY_DIALOG_TITLE = "Custom Vocabulary"
    VOCABULARY_SECTION_TITLE = "Custom Vocabulary Words"
    VOCABULARY_PLACEHOLDER = "Enter one word or short phrase per line..."
    SYSTEM_INSTRUCTIONS_DIALOG_TITLE = "System Instructions"
    INSTRUCTIONS_INFO = "Set special instructions for transcription here. Examples:\n" \
                      "- \"Ignore filler words like um, uh, er\"\n" \
                      "- \"Add proper punctuation\"\n" \
                      "- \"Format text into paragraphs\""
    SYSTEM_INSTRUCTIONS_DIALOG_PLACEHOLDER = "Enter one instruction per line..."
    
    # Instruction sets dialog
    INSTRUCTION_SETS_DIALOG_TITLE = "Instruction Set Management"
    INSTRUCTION_SETS_LIST_LABEL = "Saved Sets:"
    INSTRUCTION_SETS_ADD_BUTTON = "Create New"
    INSTRUCTION_SETS_RENAME_BUTTON = "Rename"
    INSTRUCTION_SETS_REMOVE_BUTTON = "Delete"
    INSTRUCTION_SETS_NEW_TITLE = "New Set"
    INSTRUCTION_SETS_NEW_PROMPT = "Enter a name for the new set:"
    INSTRUCTION_SETS_RENAME_TITLE = "Rename Set"
    INSTRUCTION_SETS_RENAME_PROMPT = "Enter a new name:"
    INSTRUCTION_SETS_REMOVE_TITLE = "Delete Set"
    INSTRUCTION_SETS_REMOVE_CONFIRM = "Are you sure you want to delete the set '{0}'?"
    INSTRUCTION_SETS_LAST_SET_ERROR = "Cannot delete the last set."
    INSTRUCTION_SETS_UPDATED_TITLE = "Set Updated"
    INSTRUCTION_SETS_UPDATED_MESSAGE = "Instruction set has been updated and activated."
    INSTRUCTION_SETS_VIEW_MODE_BUTTON = "List View"
    INSTRUCTION_SETS_EDIT_MODE_BUTTON = "Edit Mode"
    INSTRUCTION_SETS_TABLE_MODE_TITLE = "Instruction Sets List"
    INSTRUCTION_SETS_TABLE_NAME_COLUMN = "Set Name"
    INSTRUCTION_SETS_TABLE_VOCABULARY_COLUMN = "Vocabulary"
    INSTRUCTION_SETS_TABLE_INSTRUCTIONS_COLUMN = "Instructions"
    INSTRUCTION_SETS_ACTIVE_MARK = "(Active)"
    
    # Instruction set actions
    INSTRUCTION_SETS_ACTIVATE_BUTTON = "Activate This Set"
    INSTRUCTION_SETS_CURRENTLY_ACTIVE = "Currently Active Set"
    INSTRUCTION_SETS_EDIT_SECTION_TITLE = "Edit Selected Set"
    INSTRUCTION_SETS_UPDATED_SUCCESS = "Set updated"
    
    # Global hotkey dialog
    HOTKEY_DIALOG_TITLE = "Global Hotkey Settings"
    HOTKEY_LABEL = "Hotkey:"
    HOTKEY_PLACEHOLDER = "Example: ctrl+shift+r"
    HOTKEY_INFO = "Set a global hotkey to start/stop recording. Examples: ctrl+shift+r, alt+w, etc."
    
    # Hotkey information dialog
    HOTKEY_INFO_TITLE = "Hotkey Information"
    HOTKEY_INFO_MESSAGE = "Qt Whisper Remake is always running in the background.\n" \
                        "Global hotkey: {0} to start/stop recording.\n" \
                        "This setting can be changed in the toolbar under 'Hotkey Settings'."
    
    # Status indicator
    INDICATOR_RECORDING = "Recording"
    INDICATOR_TRANSCRIBING = "Transcribing"
    INDICATOR_TRANSCRIBED = "Transcription Complete"
    
    # System tray menu
    TRAY_SHOW = "Show"
    TRAY_RECORD = "Start/Stop Recording"
    TRAY_EXIT = "Exit"
    
    # Error messages
    ERROR_TITLE = "Error"
    ERROR_API_KEY_REQUIRED = "Please set an API key first"
    ERROR_SYSTEM_TRAY = "System tray is not supported on this system."
    ERROR_HOTKEY = "Hotkey setup error: {0}"
    ERROR_TRANSCRIPTION = "Transcription error: {0}"
    ERROR_API_KEY_MISSING = "OpenAI API key is required. Either enter it directly or set the OPENAI_API_KEY environment variable."
    
    # Information messages
    INFO_TITLE = "Information"
    INFO_TRAY_MINIMIZED = "The application is still running in the system tray.\n" \
                        "To exit completely, select 'Exit' from the tray icon menu or\n" \
                        "click 'Exit Application' in the toolbar."
    
    # Language names
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
