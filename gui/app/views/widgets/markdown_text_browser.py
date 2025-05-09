"""
Markdown Text Browser Widget

A specialized QTextBrowser widget for rendering Markdown content as HTML
with LaTeX support, while preserving the original markdown text.
"""

import re

import markdown
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import QSize, pyqtSignal, QObject
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel


class Document(QObject):
    """
    A QObject to hold the text content for communication with JavaScript.
    """
    content_changed = pyqtSignal(str)
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._content = ""
    
    def get_content(self) -> str:
        return self._content
    
    def set_content(self, content: str) -> None:
        if self._content == content:
            return
        
        self._content = content
        self.content_changed.emit(self._content)


class MarkdownTextBrowser(QWebEngineView):
    """
    A QWebEngineView for displaying Markdown content with LaTeX support.
    """
    markdown_text_changed = pyqtSignal(str)
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Create web channel
        self._channel = QWebChannel(self)
        self._document = Document(self)
        self._channel.registerObject("content", self._document)
        self.page().setWebChannel(self._channel)
        
        # Configure markdown extensions
        self.markdown_extensions = ['nl2br', 'fenced_code', 'tables']
        
        # Store original markdown text
        self._markdown_text = ""
        
        # Initialize HTML template
        self._initialize_html_template()
    
    def _initialize_html_template(self) -> None:
        """Initialize the HTML template with MathJax support."""
        self._html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <script type="text/javascript">
                window.MathJax = {
                    tex: {
                        inlineMath: [['$', '$']],
                        displayMath: [['$$', '$$']]
                    },
                    svg: {
                        fontCache: 'global'
                    }
                };
            </script>
            <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
            <script type="text/javascript">
                function typesetMath() {
                    if (typeof MathJax !== 'undefined' && typeof MathJax.typeset === 'function') {
                        MathJax.typeset([document.getElementById('content')]);
                    }
                }
                
                document.addEventListener('DOMContentLoaded', function() {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        var content = channel.objects.content;
                        content.content_changed.connect(function(new_content) {
                            document.getElementById('content').innerHTML = new_content;
                            typesetMath();
                        });
                    });
                });
            </script>
            <style>
                .placeholder {
                    color: #999;
                }
            </style>
        </head>
        <body>
            <div id="content"></div>
        </body>
        </html>
        """
        
        # Load the HTML template
        self.setHtml(self._html_template)
    
    def _preserve_latex(self, text: str) -> str:
        """Preserve LaTeX expressions in the markdown text."""
        if not text:
            return text
            
        # Preserve inline math: $...$
        text = re.sub(r'(\$)([^\$]+?)(\$)', r'\1\2\3', text)
        
        # Preserve display math: $$...$$
        text = re.sub(r'(\$\$)([^\$]+?)(\$\$)', r'\1\2\3', text)
        
        return text
    
    def markdown_text(self) -> str:
        """Get the original markdown text."""
        return self._markdown_text
    
    def set_markdown_text(self, text: str | None) -> None:
        """Set the text content as Markdown and render as HTML with LaTeX."""
        if text is None:
            text = ""
            
        # Store the original markdown text
        self._markdown_text = text
        
        if not text:
            self._document.set_content("")
            return
        
        # Preserve LaTeX expressions before markdown conversion
        preserved_text = self._preserve_latex(text)
        
        # Convert markdown to HTML
        html = markdown.markdown(preserved_text, extensions=self.markdown_extensions)
        
        # Set the HTML content
        self._document.set_content(html)
        
        # Emit signal for text change
        self.markdown_text_changed.emit(text)
    
    def clear(self) -> None:
        """Clear both the displayed HTML and stored markdown text."""
        self._markdown_text = ""
        self._document.set_content("")
    
    def append_markdown(self, text: str) -> None:
        """Append markdown text to the existing content."""
        if not text:
            return
            
        # Append to stored markdown text
        self._markdown_text += text
        
        # Preserve LaTeX expressions before markdown conversion
        preserved_text = self._preserve_latex(self._markdown_text)
        
        # Convert full markdown to HTML
        html = markdown.markdown(preserved_text, extensions=self.markdown_extensions)
        
        # Set the HTML content
        self._document.set_content(html)
        
        # Emit signal that markdown text has changed
        self.markdown_text_changed.emit(self._markdown_text)
        
        # Scroll to the bottom
        self.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")
    
    def setPlaceholderText(self, text: str) -> None:
        """Set placeholder text for the browser."""
        if not self._markdown_text:
            placeholder_html = f'<span class="placeholder">{text}</span>'
            self._document.set_content(placeholder_html)
    
    def sizeHint(self) -> QSize:
        """Provide a default size."""
        return QSize(600, 400)
    
    def setOpenExternalLinks(self, open: bool) -> None:
        """Set whether external links are opened in the default browser."""
        if open:
            self.page().linkClicked.connect(lambda url: QDesktopServices.openUrl(url))

