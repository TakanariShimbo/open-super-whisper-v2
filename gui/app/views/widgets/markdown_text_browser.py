"""
Markdown Text Browser Widget

A specialized QTextBrowser widget for rendering Markdown content as HTML
while preserving the original markdown text for clipboard operations.
"""

from PyQt6.QtWidgets import QTextBrowser, QSizePolicy
from PyQt6.QtCore import QSize, pyqtSignal

import markdown


class MarkdownTextBrowser(QTextBrowser):
    """
    A QTextBrowser subclass for displaying Markdown content as rendered HTML
    
    This widget enhances the standard QTextBrowser with custom styling
    and markdown rendering capabilities. It stores both the HTML and the
    original markdown text to support different clipboard operations.
    
    Attributes
    ----------
    markdown_text : str
        The original markdown text content
    """
    
    # Signal emitted when the markdown text is updated
    markdown_text_changed = pyqtSignal(str)
    
    def __init__(self, parent=None) -> None:
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
        self.markdown_extensions = ['nl2br', 'fenced_code', 'tables']
        
        # Store the original markdown text
        self._markdown_text = ""
    
    def markdown_text(self) -> str:
        """
        Get the original markdown text
        
        Returns
        -------
        str
            The original markdown text
        """
        return self._markdown_text
    
    def set_markdown_text(self, text: str | None) -> None:
        """
        Set the text content as Markdown and render as HTML
        
        Parameters
        ----------
        text : str | None
            The Markdown-formatted text to display
        """
        if text is None:
            text = ""
            
        # Store the original markdown text
        self._markdown_text = text
        
        if not text:
            self.setHtml("")
            return
            
        # Convert markdown to HTML using Python-Markdown
        html = markdown.markdown(text, extensions=self.markdown_extensions)
        self.setHtml(html)
        
        # Emit signal that markdown text has changed
        self.markdown_text_changed.emit(text)
    
    def clear(self) -> None:
        """
        Clear both the displayed HTML and stored markdown text
        """
        super().clear()
        self._markdown_text = ""
    
    def append_markdown(self, text: str) -> None:
        """
        Append markdown text to the existing content
        
        Parameters
        ----------
        text : str
            The markdown text to append
        """
        if not text:
            return
            
        # Append to stored markdown text
        self._markdown_text += text
        
        # Convert full markdown to HTML
        html = markdown.markdown(self._markdown_text, extensions=self.markdown_extensions)
        self.setHtml(html)
        
        # Emit signal that markdown text has changed
        self.markdown_text_changed.emit(self._markdown_text)
        
        # Scroll to the bottom
        self.moveCursor(self.textCursor().MoveOperation.End)
    
    def setPlaceholderText(self, text: str) -> None:
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
    
    def sizeHint(self) -> QSize:
        """
        Provide a reasonable default size
        
        Returns
        -------
        QSize
            The recommended size for the widget
        """
        return QSize(600, 400)
