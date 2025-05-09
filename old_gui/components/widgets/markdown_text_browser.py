"""
Markdown Text Browser Widget

A specialized QTextBrowser widget for rendering Markdown content with
appropriate styling and formatting, with improved line break handling.
"""

from PyQt6.QtWidgets import QTextBrowser, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette

import markdown


class MarkdownTextBrowser(QTextBrowser):
    """
    A QTextBrowser subclass specialized for displaying Markdown content
    
    This widget enhances the standard QTextBrowser with custom styling
    and optimizations for rendering Markdown text in a readable format.
    It also supports automatic line breaks for newline characters.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the MarkdownTextBrowser
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget
        """
        super().__init__(parent)
        
        # Set read-only by default (it's a browser, not an editor)
        self.setReadOnly(True)
        
        # Allow both internal and external links (markdown often has links)
        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)
        
        # Set size policy to allow the widget to expand both ways
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Configure markdown extension options
        self.markdown_extensions = ['nl2br']  # nl2br converts newlines to <br> tags
                
    def setMarkdownText(self, text):
        """
        Set the text content as Markdown with improved line break handling
        
        Parameters
        ----------
        text : str
            The Markdown-formatted text to display
        """
        if not text:
            self.setHtml("")
            return
            
        # Method 1: Use the Python-Markdown library with nl2br extension for proper line breaks
        html = markdown.markdown(text, extensions=self.markdown_extensions)
        self.setHtml(html)
        
        # Alternative approach: Use the built-in setMarkdown method
        # This could be used if the Python-Markdown library is not available
        # self.setMarkdown(text)
    
    def setPlaceholderText(self, text):
        """
        Set placeholder text for the QTextBrowser
        
        Parameters
        ----------
        text : str
            The placeholder text to display when the browser is empty
        """
        # QTextBrowser doesn't have a built-in placeholder, so we implement it
        # by setting the HTML directly when empty
        if not self.toPlainText():
            self.setHtml(f'<span style="color: #999;">{text}</span>')
    
    def sizeHint(self):
        """
        Provide a reasonable default size
        
        Returns
        -------
        QSize
            The recommended size for the widget
        """
        return QSize(600, 400)
