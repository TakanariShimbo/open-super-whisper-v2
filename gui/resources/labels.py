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
    
    # Main
    MAIN_SYSTEM_TRAY_ERROR_TITLE  = "System Tray Error"
    MAIN_SYSTEM_TRAY_ERROR_MESSAGE = "System tray is not supported on this system"
    
    MAIN_HOTKEY_INFO_TITLE = "Hotkey Configuration"
    MAIN_HOTKEY_INFO_MESSAGE = "You can start/stop recording by pressing {}. This works even when the app is minimized or in the background."
    
    # Main Window
    MAIN_WIN_RECORD_START_BUTTON = "Start Recording"
    MAIN_WIN_RECORD_STOP_BUTTON = "Stop Recording"
    MAIN_WIN_API_KEY_SETTINGS = "API Key Settings"
    MAIN_WIN_HOTKEY_SETTINGS = "Hotkey Settings"
    MAIN_WIN_INSTRUCTION_SETS_BUTTON = "Instruction Sets"
    MAIN_WIN_COPY_TO_CLIPBOARD = "Copy to Clipboard"
    MAIN_WIN_COPY_TRANSCRIPTION = "Copy Transcription"
    MAIN_WIN_COPY_LLM = "Copy LLM Analysis"
    MAIN_WIN_COPY_ALL = "Copy All"
    MAIN_WIN_AUTO_COPY_BUTTON = "Auto-Copy"
    MAIN_WIN_SOUND_BUTTON = "Enable Sounds"
    MAIN_WIN_INDICATOR_BUTTON = "Show Indicator"
    MAIN_WIN_EXIT_APP = "Exit"
    
    # LLM Related
    MAIN_WIN_LLM_ENABLED = "Enable LLM Processing"
    MAIN_WIN_LLM_TAB_TITLE = "LLM Analysis"
    MAIN_WIN_LLM_PLACEHOLDER = "LLM analysis will appear here when enabled..."
    MAIN_WIN_PROCESSING_ERROR = "Processing error"
    MAIN_WIN_TRANSCRIPTION_TAB_TITLE = "Transcription"
    MAIN_WIN_TRANSCRIPTION_OUTPUT_LABEL = "Transcription Output"
    MAIN_WIN_LLM_OUTPUT_LABEL = "LLM Analysis Output"
    
    MAIN_WIN_TRANSCRIPTION_TITLE = "Transcription"
    MAIN_WIN_TRANSCRIPTION_PLACEHOLDER = "Transcription will appear here..."

    MAIN_WIN_API_KEY_ERROR_TITLE = "API Key Error"
    MAIN_WIN_API_KEY_ERROR_MISSING = "API Key is missing or invalid"
    MAIN_WIN_API_KEY_ERROR_REQUIRED = "API Key is required to use this feature"
    
    MAIN_WIN_TRANSCRIPTION_ERROR_TITLE = "Transcription Error"
    MAIN_WIN_TRANSCRIPTION_ERROR = "Transcription error: {}"

    MAIN_WIN_INFO_TRAY_TITLE = "Tray Information"
    MAIN_WIN_INFO_TRAY_MESSAGE = "Application is still running in the system tray"

    # Status messages
    STATUS_READY = "Ready"
    STATUS_RECORDING = "Recording..."
    STATUS_TRANSCRIBING = "Transcribing..."
    STATUS_COMPLETE = "Complete!"
    STATUS_COPIED = "Copied to clipboard"
    STATUS_TRANSCRIPTION_COPIED = "Transcription copied to clipboard"
    STATUS_LLM_COPIED = "LLM analysis copied to clipboard"
    STATUS_ALL_COPIED = "All content copied to clipboard"
    STATUS_API_KEY_SAVED = "API key saved"
    STATUS_HOTKEY_SET = "Hotkey set to '{}'"
    STATUS_AUTO_COPY_ENABLED = "Auto-copy enabled"
    STATUS_AUTO_COPY_DISABLED = "Auto-copy disabled"
    STATUS_LLM_ENABLED = "LLM processing enabled"
    STATUS_LLM_DISABLED = "LLM processing disabled"
    STATUS_SOUND_ENABLED = "Notification sounds enabled"
    STATUS_SOUND_DISABLED = "Notification sounds disabled"
    STATUS_INDICATOR_SHOWN = "Status indicator enabled"
    STATUS_INDICATOR_HIDDEN = "Status indicator disabled"
    STATUS_INSTRUCTION_SET_ACTIVE = "Instruction set '{}' activated"
    STATUS_RECORDING_INDICATOR = "●"
    STATUS_TIMER_INITIAL = "00:00"
    
    # Indicator
    INDICATOR_TIMER_INITIAL = "00:00"
    INDICATOR_RECORDING = "Recording..."
    INDICATOR_TRANSCRIBING = "Transcribing..."
    INDICATOR_COMPLETE = "Complete!"

    # Tray menu
    TRAY_SHOW = "Show Application"
    TRAY_RECORD = "Start/Stop Recording"
    TRAY_EXIT = "Exit"

    # Instruction Sets Dialog
    INSTRUCTION_SETS_TITLE = "Instruction Sets Settings"
    INSTRUCTION_SETS_LIST_LABEL = "Instruction Sets:"
    INSTRUCTION_SETS_ADD_BUTTON = "New"
    INSTRUCTION_SETS_RENAME_BUTTON = "Rename"
    INSTRUCTION_SETS_DELETE_BUTTON = "Delete"
    INSTRUCTION_SETS_ACTIVATE_BUTTON = "Activate"
    INSTRUCTION_SETS_SAVE_BUTTON = "Save"
    
    ## Vocabulary Tab
    INSTRUCTION_SETS_VOCABULARY_TAB_NAME = "Vocabulary"
    INSTRUCTION_SETS_VOCABULARY_HELP = "Enter words or phrases to improve transcription accuracy. One item per line."
    INSTRUCTION_SETS_VOCABULARY_LABEL = "Custom Vocabulary:"
    
    ## Transcription Instructions Tab
    INSTRUCTION_SETS_INSTRUCTIONS_TAB_NAME = "Transcription Instructions"
    INSTRUCTION_SETS_INSTRUCTIONS_HELP = "Enter system instructions to control transcription behavior. One instruction per line."
    INSTRUCTION_SETS_INSTRUCTIONS_LABEL = "System Instructions:"
    
    ## LLM Instructions Tab
    INSTRUCTION_SETS_LLM_TAB_NAME = "LLM Instructions"
    INSTRUCTION_SETS_LLM_HELP = "Enter system instructions for the Large Language Model to guide how it processes the transcription."
    
    ## Language & Model Tab
    INSTRUCTION_SETS_LANGUAGE_AND_MODEL_TAB_NAME = "Language & Model"
    INSTRUCTION_SETS_SETTINGS_HELP = "Configure language and model settings for this instruction set. These settings will be used when this instruction set is active."
    INSTRUCTION_SETS_LANGUAGE_LABEL = "Language:"
    INSTRUCTION_SETS_MODEL_LABEL = "Transcription Model:"
    INSTRUCTION_SETS_LLM_MODEL_SECTION_LABEL = "LLM Settings:"
    INSTRUCTION_SETS_LLM_TOGGLE_LABEL = "Enable LLM Processing"
    INSTRUCTION_SETS_LLM_MODEL_LABEL = "LLM Model:"

    ## Instruction Set Dialogs
    INSTRUCTION_SETS_NEW_INSTRUCTION_SET_TITLE = "New Instruction Set"
    INSTRUCTION_SETS_NEW_INSTRUCTION_SET_PROMPT = "Enter a name for the new instruction set:"

    INSTRUCTION_SETS_RENAME_INSTRUCTION_SET_TITLE = "Rename Instruction Set"
    INSTRUCTION_SETS_RENAME_INSTRUCTION_SET_PROMPT = "Enter a new name for the instruction set:"

    INSTRUCTION_SETS_NAME_EXISTS_TITLE = "Name Exists"
    INSTRUCTION_SETS_NAME_EXISTS_MESSAGE = "An instruction set with the name '{}' already exists."

    INSTRUCTION_SETS_CONFIRM_DELETION_TITLE = "Confirm Deletion"
    INSTRUCTION_SETS_CONFIRM_DELETION_MESSAGE = "Are you sure you want to delete the instruction set '{}'?"

    INSTRUCTION_SETS_CHANGES_SAVED_TITLE = "Changes Saved"
    INSTRUCTION_SETS_CHANGES_SAVED_MESSAGE = "Changes to instruction set '{}' have been saved."

    INSTRUCTION_SETS_SET_ACTIVATED_TITLE = "Set Activated"
    INSTRUCTION_SETS_SET_ACTIVATED_MESSAGE = "Instruction set '{}' has been activated."
    
    # API Key Dialog
    API_KEY_TITLE = "API Key Settings"
    API_KEY_DESCRIPTION = "Enter your OpenAI API key to use transcription services. The key will be stored locally on your device."
    API_KEY_LABEL = "API Key:"
    API_KEY_PLACEHOLDER = "Enter your OpenAI API key..."
    API_KEY_SHOW_BUTTON = "Show"
    API_KEY_HIDE_BUTTON = "Hide"
    API_KEY_VALIDATE_BUTTON = "Validate Key"

    API_KEY_EMPTY_ERROR_TITLE = "API Key Empty"
    API_KEY_EMPTY_ERROR_MESSAGE = "API key cannot be empty."
    
    API_KEY_VALID_TITLE = "API Key Valid"
    API_KEY_VALID_MESSAGE = "The API key is valid and has been verified."
    
    API_KEY_VALIDATION_ERROR_TITLE = "Validation Error"
    API_KEY_VALIDATION_ERROR_MESSAGE = "Failed to validate API key: {}"
    
    # Hotkey Dialog
    HOTKEY_TITLE = "Global Hotkey Settings"
    HOTKEY_DESCRIPTION = "Set a global hotkey combination for starting and stopping recording. Press the desired key combination in the input field below."
    HOTKEY_LABEL = "Hotkey:"
    HOTKEY_PLACEHOLDER = "Click here and press hotkey combination..."
    HOTKEY_CLEAR_BUTTON = "Clear"
    HOTKEY_EXAMPLES = "Examples: ctrl+shift+r, alt+w, ctrl+alt+s"

    HOTKEY_VALIDATION_ERROR_TITLE = "Hotkey Error"
    HOTKEY_VALIDATION_ERROR_MESSAGE = "Please set a valid hotkey combination."
   
    