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
    r"""
    A QWebEngineView for displaying Markdown content with LaTeX support.
    
    This widget renders Markdown text as HTML and uses MathJax to render
    mathematical expressions written in LaTeX syntax. It supports both
    inline and display math with the following delimiters:
    
    Inline math:
    - $...$ (standard LaTeX inline math)
    - \(...\) (LaTeX alternative syntax)
    
    Display math:
    - $$...$$ (common display math)
    - \[...\] (standard LaTeX display math)
    
    The class preserves the original Markdown text and provides methods
    for setting and appending content, as well as clearing the display.
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
        
        # Store placeholder text
        self._placeholder_text = ""
        
        # Initialize HTML template
        self._initialize_html_template()
        
        # Connect loadFinished signal to apply placeholder
        self.loadFinished.connect(self._on_load_finished)
    
    def _initialize_html_template(self) -> None:
        r"""
        Initialize the HTML template with MathJax support.
        
        The HTML template includes:
        1. MathJax configuration for LaTeX rendering
        2. Support for both inline math ($...$, \(...\)) and display math ($$...$$, \[...\])
        3. JavaScript for handling content updates via Qt web channel
        4. Basic styling for placeholder text
        """
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
                        inlineMath: [['$', '$'], ['\\(', '\\)']],
                        displayMath: [['$$', '$$'], ['\\[', '\\]']]
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
                            var contentElement = document.getElementById('content');
                            if (contentElement) {
                                contentElement.innerHTML = new_content;
                                typesetMath();
                            }
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
        r"""
        Preserve LaTeX expressions in the markdown text.
        
        This method prevents Markdown parser from interfering with LaTeX expressions
        by temporarily preserving them during markdown processing.
        
        Supported LaTeX delimiters:
        - $...$ for inline math
        - \(...\) for inline math (LaTeX alternative syntax)
        - $$...$$ for block/display math
        - \[...\] for block/display math (LaTeX standard)
        
        Parameters
        ----------
        text : str
            The markdown text to preserve
            
        Returns
        -------
        str: Text with preserved LaTeX expressions
        """
        if not text:
            return text
            
        # Preserve inline math: $...$
        # Matches a single dollar sign followed by non-dollar content and ending with a dollar sign
        text = re.sub(r'(\$)([^\$]+?)(\$)', r'\1\2\3', text)
        
        # Preserve inline math: \(...\)
        # Matches inline math with parentheses delimiters
        # with flags=re.DOTALL to allow matching across multiple lines
        text = re.sub(r'(\\\\?\()(.*?)(\\\\?\))', r'\1\2\3', text, flags=re.DOTALL)
        
        # Preserve display math: $$...$$
        # Matches double dollar signs with content between them
        text = re.sub(r'(\$\$)([^\$]+?)(\$\$)', r'\1\2\3', text)
        
        # Preserve display math: \[...\]
        # The pattern handles both escaped and non-escaped square brackets
        # with flags=re.DOTALL to allow matching across multiple lines
        text = re.sub(r'(\\\\?\[)(.*?)(\\\\?\])', r'\1\2\3', text, flags=re.DOTALL)
        
        return text
    
    def _apply_placeholder(self):
        """
        Apply placeholder text if available and content is empty.
        This is a helper method to avoid code duplication.
        """
        if self._placeholder_text and not self._markdown_text:
            placeholder_html = f'<span class="placeholder">{self._placeholder_text}</span>'
            self._document.set_content(placeholder_html)
            
            # Ensure placeholder is visible with direct JavaScript injection
            # Added error handling to avoid JavaScript errors
            js_code = """
            (function() {
                setTimeout(function() {
                    var contentElement = document.getElementById('content');
                    if (contentElement) {
                        contentElement.innerHTML = '<span class="placeholder">""" + self._placeholder_text + """</span>';
                    }
                }, 200);
            })();
            """
            self.page().runJavaScript(js_code)
            return True
        return False
    
    def markdown_text(self) -> str:
        """
        Get the original markdown text.
        
        Returns
        -------
        str: The original markdown text
        """
        return self._markdown_text
    
    def set_markdown_text(self, text: str | None) -> None:
        """
        Set the text content as Markdown and render as HTML with LaTeX.
        
        Parameters
        ----------
        text : str | None
            The markdown text to set
        """
        if text is None:
            text = ""
            
        # Store the original markdown text
        self._markdown_text = text
        
        if not text:
            # If text is empty, show placeholder or clear
            if not self._apply_placeholder():
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
        """
        Clear both the displayed HTML and stored markdown text.
        Shows placeholder text if set.
        """
        self._markdown_text = ""
        
        # Show placeholder if set, otherwise clear content
        if not self._apply_placeholder():
            self._document.set_content("")
    
    def append_markdown(self, text: str) -> None:
        """
        Append markdown text to the existing content.
        
        Parameters
        ----------
        text : str
            The markdown text to append
        """
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
        """
        Set placeholder text for the browser.
        """
        # Store the placeholder text for later use
        self._placeholder_text = text
        
        # Apply placeholder if content is empty
        self._apply_placeholder()
    
    def _on_load_finished(self, success):
        """
        Handler for the loadFinished signal.
        Ensures that placeholder text is applied after the page is fully loaded.
        
        Parameters
        ----------
        success : bool
            Whether the page was loaded successfully
        """
        if success:
            # Use a timer to ensure the DOM is fully ready
            self.page().runJavaScript("""
            setTimeout(function() {
                // Signal that the page is truly ready for content
                if (document.readyState === 'complete') {
                    console.log('Page fully loaded');
                }
            }, 100);
            """)
            # Apply placeholder after a short delay
            self._apply_placeholder()
    
    def sizeHint(self) -> QSize:
        """
        Provide a default size.
        """
        return QSize(600, 400)
        
    def setOpenExternalLinks(self, open: bool) -> None:
        """
        Set whether external links are opened in the default browser.
        """
        if open:
            self.page().linkClicked.connect(lambda url: QDesktopServices.openUrl(url))
