"""
Whisper Core Module

This module provides core functionality for audio recording and transcription.
"""

from old_core.transcriber import OpenAIWhisperTranscriber
from old_core.recorder import AudioInputRecorder, MicrophoneError, NoMicrophoneError, MicrophoneAccessError
from old_core.instructions import InstructionSet, InstructionSetManager
from old_core.hotkeys import HotkeyManager

__all__ = [
    'OpenAIWhisperTranscriber',
    'AudioInputRecorder',
    'MicrophoneError',
    'NoMicrophoneError',
    'MicrophoneAccessError',
    'InstructionSet',
    'InstructionSetManager',
    'HotkeyManager'
]
