"""
Whisper Core Module

This module provides core functionality for audio recording and transcription.
"""

from whisper_core.transcriber import WhisperTranscriber
from whisper_core.recorder import AudioRecorder
from whisper_core.instructions import InstructionSet, InstructionSetManager
from whisper_core.hotkeys import HotkeyManager

__all__ = [
    'WhisperTranscriber',
    'AudioRecorder',
    'InstructionSet',
    'InstructionSetManager',
    'HotkeyManager'
]
