"""
Language Data Model

This module provides data structures and utilities for managing language data
throughout the application. It centralizes language definitions and provides
a consistent interface for accessing language information.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, ClassVar


@dataclass
class Language:
    """
    Language data model.
    
    This class represents a language with its properties like code, name,
    and other metadata.
    
    Attributes
    ----------
    code : str
        ISO 639-1 language code (e.g., "en", "ja").
    name : str
        Display name in English (e.g., "English", "Japanese").
    native_name : str
        Name in the native language (e.g., "English", "日本語").
    is_right_to_left : bool
        Whether the language is written right-to-left, by default False.
    """
    code: str
    name: str
    native_name: str
    is_right_to_left: bool = False
    
    def __str__(self) -> str:
        """Return the display name of the language."""
        return self.name
    
    def __repr__(self) -> str:
        """Return a string representation of the language."""
        return f"Language(code='{self.code}', name='{self.name}')"


class LanguageManager:
    """
    Manager for language data.
    
    This class provides methods to access and manage language data.
    It maintains a list of supported languages and provides utilities
    for lookup and validation.
    """
    
    # Define supported languages
    # The list includes commonly supported languages by transcription services
    _LANGUAGES: ClassVar[List[Language]] = [
        Language(code="", name="Auto-detect", native_name="Auto-detect"),
        Language(code="en", name="English", native_name="English"),
        Language(code="es", name="Spanish", native_name="Español"),
        Language(code="fr", name="French", native_name="Français"),
        Language(code="de", name="German", native_name="Deutsch"),
        Language(code="it", name="Italian", native_name="Italiano"),
        Language(code="pt", name="Portuguese", native_name="Português"),
        Language(code="nl", name="Dutch", native_name="Nederlands"),
        Language(code="ja", name="Japanese", native_name="日本語"),
        Language(code="ko", name="Korean", native_name="한국어"),
        Language(code="zh", name="Chinese", native_name="中文"),
        Language(code="ru", name="Russian", native_name="Русский"),
        Language(code="ar", name="Arabic", native_name="العربية", is_right_to_left=True),
        Language(code="hi", name="Hindi", native_name="हिन्दी"),
        Language(code="tr", name="Turkish", native_name="Türkçe"),
        Language(code="pl", name="Polish", native_name="Polski"),
        Language(code="th", name="Thai", native_name="ไทย"),
        Language(code="vi", name="Vietnamese", native_name="Tiếng Việt"),
        Language(code="id", name="Indonesian", native_name="Bahasa Indonesia"),
        Language(code="sv", name="Swedish", native_name="Svenska"),
        Language(code="fi", name="Finnish", native_name="Suomi"),
        Language(code="no", name="Norwegian", native_name="Norsk"),
        Language(code="da", name="Danish", native_name="Dansk"),
        Language(code="cs", name="Czech", native_name="Čeština"),
        Language(code="hu", name="Hungarian", native_name="Magyar"),
        Language(code="ro", name="Romanian", native_name="Română"),
        Language(code="uk", name="Ukrainian", native_name="Українська"),
        Language(code="el", name="Greek", native_name="Ελληνικά"),
        Language(code="bg", name="Bulgarian", native_name="Български"),
        Language(code="he", name="Hebrew", native_name="עברית", is_right_to_left=True),
        Language(code="fa", name="Persian", native_name="فارسی", is_right_to_left=True),
    ]
    
    # Create a lookup dictionary for efficient access by code
    _LANGUAGE_DICT: ClassVar[Dict[str, Language]] = {
        lang.code: lang for lang in _LANGUAGES
    }
    
    @classmethod
    def get_languages(cls) -> List[Language]:
        """
        Get all supported languages.
        
        Returns
        -------
        List[Language]
            List of all supported languages.
        """
        return cls._LANGUAGES.copy()
    
    @classmethod
    def get_language_by_code(cls, code: str) -> Optional[Language]:
        """
        Get a language by its code.
        
        Parameters
        ----------
        code : str
            Language code to look up.
            
        Returns
        -------
        Optional[Language]
            Language object if found, None otherwise.
        """
        return cls._LANGUAGE_DICT.get(code)
    
    @classmethod
    def get_default_language(cls) -> Language:
        """
        Get the default language (Auto-detect).
        
        Returns
        -------
        Language
            Default language object.
        """
        return cls._LANGUAGES[0]  # Auto-detect is the first item
    
    @classmethod
    def is_valid_code(cls, code: str) -> bool:
        """
        Check if a language code is valid.
        
        Parameters
        ----------
        code : str
            Language code to validate.
            
        Returns
        -------
        bool
            True if the code is valid, False otherwise.
            Empty string is considered valid (auto-detect).
        """
        return code in cls._LANGUAGE_DICT
    
    @classmethod
    def get_language_display_name(cls, code: str) -> str:
        """
        Get the display name for a language code.
        
        Parameters
        ----------
        code : str
            Language code.
            
        Returns
        -------
        str
            Display name of the language, or "Unknown" if not found.
        """
        language = cls.get_language_by_code(code)
        return language.name if language else "Unknown"
