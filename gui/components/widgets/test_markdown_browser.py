"""
Simple test script for the MarkdownTextBrowser widget.

This script creates a simple window with the MarkdownTextBrowser widget
to test the improved line break handling.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PyQt6.QtCore import Qt

from markdown_text_browser import MarkdownTextBrowser


class TestWindow(QMainWindow):
    """Test window for the MarkdownTextBrowser widget."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MarkdownTextBrowser Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create the input text editor
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Type Markdown here with single line breaks...")
        
        # Create the MarkdownTextBrowser
        self.markdown_browser = MarkdownTextBrowser()
        self.markdown_browser.setPlaceholderText("Rendered Markdown will appear here")
        
        # Create the update button
        self.update_button = QPushButton("Update Markdown Preview")
        self.update_button.clicked.connect(self.update_preview)
        
        # Add widgets to the layout
        layout.addWidget(self.input_text)
        layout.addWidget(self.update_button)
        layout.addWidget(self.markdown_browser)
        
        # Set the central widget
        self.setCentralWidget(central_widget)
        
        # Add some example Markdown text
        self.input_text.setText(self.get_example_markdown())
        self.update_preview()
    
    def update_preview(self):
        """Update the Markdown preview with the input text."""
        markdown_text = self.input_text.toPlainText()
        self.markdown_browser.setMarkdownText(markdown_text)
    
    def get_example_markdown(self):
        """Return example Markdown text with various formatting and line breaks."""
        return """# Markdown Test

## Paragraph with line breaks
This is a paragraph with 
a single line break.
It should render with the line break visible.

## Standard markdown paragraph
This is a standard markdown paragraph.
It has a line break, which normally would be ignored.

But this line has a blank line above it, so it's a new paragraph.

## List with line breaks
- Item 1
- Item 2
  with a continuation on a new line
- Item 3

## Code block
```python
def hello_world():
    print("Hello, world!")
    return True
```

## Blockquote
> This is a blockquote
> with multiple lines
> that should preserve line breaks

## Table
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

## Links and emphasis
[This is a link](https://example.com)
*Italic text* and **bold text**

## Single line break test
Line 1
Line 2
Line 3

## Line break with two spaces test
Line 1  
Line 2  
Line 3

## Empty lines test

Line 1

Line 2

Line 3

## Multi-line paragraph
LLMの出力結果は、Markdown 形式のテキストなので、
見やすいようにしてあげたい！
できれば、pyqt6の機能で markdown のまま、
いい感じにしてあげたい。
"""


def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
