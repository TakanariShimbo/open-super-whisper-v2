"""
Clipboard Utility Module

This module provides functions for extracting text and images from the clipboard.
It follows the single responsibility principle by focusing only on clipboard operations.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QBuffer, QIODevice

def extract_clipboard_text() -> str | None:
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

def extract_clipboard_image() -> bytes | None:
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

def get_clipboard_content() -> tuple[str | None, bytes | None]:
    """
    Get both text and image from clipboard.
    
    Returns
    -------
    tuple[str | None, bytes | None]
        A tuple containing (clipboard_text, clipboard_image), either may be None
    """
    return extract_clipboard_text(), extract_clipboard_image()

def is_clipboard_empty() -> bool:
    """
    Check if clipboard is empty (no text or image).
    
    Returns
    -------
    bool
        True if clipboard is empty, False otherwise
    """
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()
    
    return not (mime_data.hasText() or mime_data.hasImage())
