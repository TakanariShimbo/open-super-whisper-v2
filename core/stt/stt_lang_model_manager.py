"""
Speech-to-Text Language Model Manager

This module provides functionality for managing language options for
speech-to-text processing, including language selection, validation,
and information retrieval.
"""

from typing import ClassVar

from .stt_lang_model import STTLangModel


class STTLangModelManager:
    """
    Manager for speech-to-text language data.

    This class provides methods to access and manage language options
    for speech-to-text processing. It maintains a list of supported
    languages and provides utilities for lookup and validation.
    """

    # Define supported languages
    # This list includes commonly supported languages by transcription services
    _SUPPORTED_LANGUAGES: ClassVar[list[STTLangModel]] = [
        STTLangModel(code="", name="Auto-detect"),
        STTLangModel(code="af", name="Afrikaans"),
        STTLangModel(code="ar", name="Arabic"),
        STTLangModel(code="hy", name="Armenian"),
        STTLangModel(code="az", name="Azerbaijani"),
        STTLangModel(code="be", name="Belarusian"),
        STTLangModel(code="bs", name="Bosnian"),
        STTLangModel(code="bg", name="Bulgarian"),
        STTLangModel(code="ca", name="Catalan"),
        STTLangModel(code="zh", name="Chinese"),
        STTLangModel(code="hr", name="Croatian"),
        STTLangModel(code="cs", name="Czech"),
        STTLangModel(code="da", name="Danish"),
        STTLangModel(code="nl", name="Dutch"),
        STTLangModel(code="en", name="English"),
        STTLangModel(code="et", name="Estonian"),
        STTLangModel(code="fi", name="Finnish"),
        STTLangModel(code="fr", name="French"),
        STTLangModel(code="gl", name="Galician"),
        STTLangModel(code="de", name="German"),
        STTLangModel(code="el", name="Greek"),
        STTLangModel(code="he", name="Hebrew"),
        STTLangModel(code="hi", name="Hindi"),
        STTLangModel(code="hu", name="Hungarian"),
        STTLangModel(code="is", name="Icelandic"),
        STTLangModel(code="id", name="Indonesian"),
        STTLangModel(code="it", name="Italian"),
        STTLangModel(code="ja", name="Japanese"),
        STTLangModel(code="kn", name="Kannada"),
        STTLangModel(code="kk", name="Kazakh"),
        STTLangModel(code="ko", name="Korean"),
        STTLangModel(code="lv", name="Latvian"),
        STTLangModel(code="lt", name="Lithuanian"),
        STTLangModel(code="mk", name="Macedonian"),
        STTLangModel(code="ms", name="Malay"),
        STTLangModel(code="mr", name="Marathi"),
        STTLangModel(code="mi", name="Maori"),
        STTLangModel(code="ne", name="Nepali"),
        STTLangModel(code="no", name="Norwegian"),
        STTLangModel(code="fa", name="Persian"),
        STTLangModel(code="pl", name="Polish"),
        STTLangModel(code="pt", name="Portuguese"),
        STTLangModel(code="ro", name="Romanian"),
        STTLangModel(code="ru", name="Russian"),
        STTLangModel(code="sr", name="Serbian"),
        STTLangModel(code="sk", name="Slovak"),
        STTLangModel(code="sl", name="Slovenian"),
        STTLangModel(code="es", name="Spanish"),
        STTLangModel(code="sw", name="Swahili"),
        STTLangModel(code="sv", name="Swedish"),
        STTLangModel(code="tl", name="Tagalog"),
        STTLangModel(code="ta", name="Tamil"),
        STTLangModel(code="th", name="Thai"),
        STTLangModel(code="tr", name="Turkish"),
        STTLangModel(code="uk", name="Ukrainian"),
        STTLangModel(code="ur", name="Urdu"),
        STTLangModel(code="vi", name="Vietnamese"),
        STTLangModel(code="cy", name="Welsh"),
    ]

    # Create a lookup dictionary for efficient access by code
    _LANGUAGE_CODE_MAP: ClassVar[dict[str, STTLangModel]] = {lang.code: lang for lang in _SUPPORTED_LANGUAGES}

    @classmethod
    def get_available_languages(cls) -> list[STTLangModel]:
        """
        Get all supported languages.

        Returns
        -------
        list[STTLangModel]
            List of all supported language objects.
            The first element is always the auto-detect option.
        """
        return cls._SUPPORTED_LANGUAGES.copy()

    @classmethod
    def get_language_by_code(cls, code: str) -> STTLangModel:
        """
        Get a language by its code.

        Parameters
        ----------
        code : str
            The ISO 639-1 language code to look up.

        Returns
        -------
        STTLangModel
            The language object matching the code.
            Returns the auto-detect language if the code is not found.
        """
        return cls._LANGUAGE_CODE_MAP.get(code, cls._SUPPORTED_LANGUAGES[0])

    @classmethod
    def to_api_format(cls) -> list[dict[str, str]]:
        """
        Convert languages to API format.

        Returns
        -------
        list[dict[str, str]]
            List of dictionaries with language information (code, name).
        """
        return [
            {
                "code": lang.code,
                "name": lang.name,
            }
            for lang in cls._SUPPORTED_LANGUAGES
        ]
