"""
Dialog components for the Whisper GUI application.
"""

from old_gui.dialogs.api_key_dialog import APIKeyDialog
from old_gui.dialogs.hotkey_dialog import HotkeyDialog
from old_gui.dialogs.instruction_sets_dialog import InstructionSetsDialog, GUIInstructionSetManager
from old_gui.dialogs.simple_message_dialog import SimpleMessageDialog

__all__ = [
    'APIKeyDialog',
    'HotkeyDialog',
    'InstructionSetsDialog',
    'GUIInstructionSetManager',
    'SimpleMessageDialog'
]
