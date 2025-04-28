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
    MAIN_HOTKEY_INFO_MESSAGE = "Use instruction set hotkeys for recording. Each instruction set can have its own hotkey - press once to start recording, press the same key again to stop. This works even when the app is minimized or in the background."
    
    # Main Window
    MAIN_WIN_RECORD_START_BUTTON = "Start Recording"
    MAIN_WIN_RECORD_STOP_BUTTON = "Stop Recording"
    MAIN_WIN_API_KEY_SETTINGS = "API Key Settings"
    MAIN_WIN_HOTKEY_SETTINGS = "Legacy Hotkey Settings"
    MAIN_WIN_INSTRUCTION_SETS_BUTTON = "Instruction Sets"
    MAIN_WIN_INSTRUCTION_SET_LABEL = "Instruction Set:"
    MAIN_WIN_COPY_TO_CLIPBOARD = "Copy to Clipboard"
    MAIN_WIN_COPY_TRANSCRIPTION = "Copy Transcription"
    MAIN_WIN_COPY_LLM = "Copy LLM Analysis"
    MAIN_WIN_COPY_ALL = "Copy All"
    MAIN_WIN_AUTO_COPY_BUTTON = "Auto-Copy"
    MAIN_WIN_SOUND_BUTTON = "Enable Sounds"
    MAIN_WIN_INDICATOR_BUTTON = "Show Indicator"
    MAIN_WIN_EXIT_APP = "Exit"
    
    # Microphone Error Messages
    MAIN_WIN_MIC_ERROR_TITLE = "Microphone Error"
    MAIN_WIN_NO_MIC_ERROR = "No microphone detected. Please connect a microphone and try again."
    MAIN_WIN_MIC_ACCESS_ERROR = "Could not access microphone. Please check your device permissions."
    
    # LLM Related
    MAIN_WIN_TRANSCRIPTION_TITLE = "Transcription"
    MAIN_WIN_LLM_ENABLED = "Enable LLM Processing"
    MAIN_WIN_PROCESSING_ERROR = "Processing error"

    MAIN_WIN_TRANSCRIPTION_TAB_TITLE = "Transcription"
    MAIN_WIN_TRANSCRIPTION_OUTPUT_LABEL = "Transcription Output"
    MAIN_WIN_TRANSCRIPTION_PLACEHOLDER = "Transcription will appear here..."

    MAIN_WIN_LLM_TAB_TITLE = "Raw LLM"
    MAIN_WIN_LLM_PLACEHOLDER = "Raw LLM content will appear here when LLM Processing is enabled..."
    MAIN_WIN_LLM_OUTPUT_LABEL = "Raw LLM Output"
    
    MAIN_WIN_MARKDOWN_TAB_TITLE = "Formatted LLM"
    MAIN_WIN_MARKDOWN_OUTPUT_LABEL = "Formatted LLM Output"
    MAIN_WIN_MARKDOWN_PLACEHOLDER = "Formatted LLM content will appear here when LLM Processing is enabled..." 

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
    STATUS_TRANSCRIBING = "Processing..."
    STATUS_COMPLETE = "Complete!"
    STATUS_COPIED = "Copied to clipboard"
    STATUS_TRANSCRIPTION_COPIED = "Transcription copied to clipboard"
    STATUS_LLM_COPIED = "LLM analysis copied to clipboard"
    STATUS_ALL_COPIED = "All content copied to clipboard"
    STATUS_API_KEY_SAVED = "API key saved"
    STATUS_HOTKEY_SET = "Legacy hotkey set to '{}' (Note: This is not used for recording)"
    STATUS_AUTO_COPY_ENABLED = "Auto-copy enabled"
    STATUS_AUTO_COPY_DISABLED = "Auto-copy disabled"
    STATUS_LLM_ENABLED = "LLM processing enabled"
    STATUS_LLM_DISABLED = "LLM processing disabled"
    STATUS_SOUND_ENABLED = "Notification sounds enabled"
    STATUS_SOUND_DISABLED = "Notification sounds disabled"
    STATUS_INDICATOR_SHOWN = "Status indicator enabled"
    STATUS_INDICATOR_HIDDEN = "Status indicator disabled"
    STATUS_INSTRUCTION_SET_ACTIVE = "Instruction set '{}' activated"
    STATUS_INSTRUCTION_SET_ACTIVATED_BY_HOTKEY = "Instruction set '{}' activated and recording started"
    STATUS_RECORDING_INDICATOR_RECORDING = "●REC"
    STATUS_RECORDING_INDICATOR_STOPPED = "■STOP"
    STATUS_TIMER_INITIAL = "00:00"
    
    # Indicator
    INDICATOR_TIMER_INITIAL = "00:00"
    INDICATOR_RECORDING = "Recording..."
    INDICATOR_PROCESSING = "Processing..."
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
    
    ## Settings Tab
    INSTRUCTION_SETS_SETTINGS_TAB_NAME = "Settings"
    INSTRUCTION_SETS_SETTINGS_HELP = "Configure language and model settings for this instruction set. These settings will be used when this instruction set is active.\n\nYou can assign a hotkey to start and stop recording with this instruction set. Press the assigned hotkey once to activate the set and start recording, then press the same hotkey again to stop recording."
    INSTRUCTION_SETS_LANGUAGE_LABEL = "Language:"
    INSTRUCTION_SETS_MODEL_LABEL = "Transcription Model:"
    INSTRUCTION_SETS_LLM_TOGGLE_LABEL = "LLM Processing:"
    INSTRUCTION_SETS_LLM_MODEL_LABEL = "LLM Model:"
    INSTRUCTION_SETS_LLM_CONTEXT_LABEL = "LLM Context: "
    INSTRUCTION_SETS_LLM_CLIPBOARD_TEXT_LABEL = "Include clipboard text"
    INSTRUCTION_SETS_LLM_CLIPBOARD_TEXT_TOOLTIP = "When enabled, text from clipboard will be included in LLM input"
    INSTRUCTION_SETS_LLM_CLIPBOARD_IMAGE_LABEL = "Include clipboard images"
    INSTRUCTION_SETS_LLM_CLIPBOARD_IMAGE_TOOLTIP = "When enabled, images from clipboard will be included in LLM input"
    INSTRUCTION_SETS_HOTKEY_LABEL = "Recording Hotkey:"
    INSTRUCTION_SETS_HOTKEY_PLACEHOLDER = "No hotkey set"
    INSTRUCTION_SETS_SET_HOTKEY_BUTTON = "Set Hotkey"
    INSTRUCTION_SETS_HOTKEY_CONFLICT_TITLE = "Hotkey Conflict"
    INSTRUCTION_SETS_HOTKEY_CONFLICT_MESSAGE = "This hotkey is already assigned to '{}'."

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
    
    INSTRUCTION_SETS_LAST_SET_ERROR_TITLE = "Cannot Delete Last Set"
    INSTRUCTION_SETS_LAST_SET_ERROR_MESSAGE = "The last instruction set cannot be deleted. At least one set must remain."
    
    INSTRUCTION_SETS_DELETION_FAILED_TITLE = "Deletion Failed"
    INSTRUCTION_SETS_DELETION_FAILED_MESSAGE = "Could not delete the instruction set '{}'."
    
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
    HOTKEY_TITLE = "Recording Hotkey Settings"
    HOTKEY_DESCRIPTION = "Note: Each instruction set can have its own hotkey assigned for starting and stopping recording. Use the Instruction Sets dialog to configure these hotkeys.\n\nThis dialog is kept for compatibility with old settings. The global hotkey below is no longer used."
    HOTKEY_LABEL = "Legacy Hotkey:"
    HOTKEY_PLACEHOLDER = "Click here and press hotkey combination..."
    HOTKEY_CLEAR_BUTTON = "Clear"
    HOTKEY_EXAMPLES = "Examples: ctrl+shift+r, alt+w, ctrl+alt+s"

    HOTKEY_VALIDATION_ERROR_TITLE = "Hotkey Error"
    HOTKEY_VALIDATION_ERROR_MESSAGE = "Please set a valid hotkey combination."
   
    