"""
Whisper Core Module

This module provides core functionality for audio recording and transcription.
"""

from core.transcriber import OpenAIWhisperTranscriber
from core.recorder import AudioInputRecorder, MicrophoneError, NoMicrophoneError, MicrophoneAccessError
from core.instructions import InstructionSet, InstructionSetManager
from core.hotkeys import HotkeyManager

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
