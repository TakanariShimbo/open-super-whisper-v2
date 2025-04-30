"""
Data Models Package

This package contains data models and managers for different types of data
used throughout the application, such as language and whisper model definitions.
"""

from core.models.language import Language, LanguageManager
from core.models.whisper import OpenAIWhisperModel, OpenAIWhisperModelManager

# Re-export core classes for easier imports
__all__ = [
    'Language',
    'LanguageManager',
    'OpenAIWhisperModel',
    'OpenAIWhisperModelManager',
]
