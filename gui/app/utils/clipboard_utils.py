"""
Clipboard Utility Module

This module provides functions for clipboard operations including text and image handling.
It follows the single responsibility principle by focusing only on clipboard operations.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QBuffer, QIODevice


class ClipboardUtils:
    """
    Utility class for clipboard operations.

    This class provides static methods for extracting text and image from the clipboard.
    """

    @staticmethod
    def extract_text() -> str | None:
        """
        Extract text from the clipboard.

        Returns
        -------
        str | None
            The text from the clipboard, or None if no text is available
        """
        clipboard = QApplication.clipboard()

        # Check if clipboard has text
        if clipboard.mimeData().hasText():
            return clipboard.text()

        return None

    @staticmethod
    def extract_image() -> bytes | None:
        """
        Extract image from the clipboard.

        Returns
        -------
        bytes | None
            The image from the clipboard as bytes, or None if no image is available
        """
        clipboard = QApplication.clipboard()

        # Check if clipboard has an image
        if clipboard.mimeData().hasImage():
            # Get the image from clipboard
            image = clipboard.image()

            # Check if image is valid
            if not image.isNull():
                # Convert QImage to bytes (using JPEG format)
                buffer = QBuffer()
                buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                image.save(buffer, "JPEG")
                return buffer.data().data()  # Convert QByteArray to Python bytes

        return None

    @staticmethod
    def get_content() -> tuple[str | None, bytes | None]:
        """
        Get both text and image from clipboard.

        Returns
        -------
        tuple[str | None, bytes | None]
            A tuple containing (clipboard_text, clipboard_image), either may be None
        """
        return ClipboardUtils.extract_text(), ClipboardUtils.extract_image()

    @staticmethod
    def set_text(text: str) -> None:
        """
        Set text to the clipboard.

        Parameters
        ----------
        text : str
            The text to set to the clipboard
        """
        QApplication.clipboard().setText(text)
