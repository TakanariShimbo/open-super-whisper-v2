"""
Dialog components for the Whisper GUI application.
"""

from gui.dialogs.api_key_dialog import APIKeyDialog
from gui.dialogs.hotkey_dialog import HotkeyDialog
from gui.dialogs.instruction_sets_dialog import InstructionSetsDialog, GUIInstructionSetManager
from gui.dialogs.simple_message_dialog import SimpleMessageDialog

__all__ = [
    'APIKeyDialog',
    'HotkeyDialog',
    'InstructionSetsDialog',
    'GUIInstructionSetManager',
    'SimpleMessageDialog'
]
