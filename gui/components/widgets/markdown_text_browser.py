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
        
        # Set up styling
        self.setup_styling()
        
        # Set size policy to allow the widget to expand both ways
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Configure markdown extension options
        self.markdown_extensions = ['nl2br']  # nl2br converts newlines to <br> tags
        
    def setup_styling(self):
        """Configure styling for better Markdown rendering"""
        # Use a nicer font for content display
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Set margins for better readability
        document = self.document()
        document.setDocumentMargin(10)
        
        # Setup color scheme for light background/dark text
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(252, 252, 252))
        palette.setColor(QPalette.ColorRole.Text, QColor(34, 34, 34))
        self.setPalette(palette)
        
        # Improve code block presentation
        css = """
        pre {
            background-color: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 3px;
            padding: 8px;
            font-family: 'Courier New', monospace;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        blockquote {
            border-left: 4px solid #e0e0e0;
            padding-left: 16px;
            color: #444;
            margin-left: 0;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 20px;
            margin-bottom: 10px;
            font-weight: 600;
        }
        a {
            color: #0366d6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        ul, ol {
            margin-left: 15px;
        }
        p {
            margin-top: 0;
            margin-bottom: 10px;
            line-height: 1.5;
        }
        """
        document.setDefaultStyleSheet(css)
        
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
