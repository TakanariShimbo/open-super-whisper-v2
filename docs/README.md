[English](README.md) | [日本語](README_ja.md)

# Open Super Whisper V2

<div align="center">
  <img src="../assets/icon.png" alt="Open Super Whisper V2 Icon" width="128" height="128">
</div>

**Conversational AI Agent - Transform Your Voice into Action**

Just speak, and AI agents understand your intent and autonomously execute tasks. This powerful PyQt6-based desktop application seamlessly integrates OpenAI's cutting-edge Whisper speech recognition with advanced Large Language Models. From voice commands to document creation, information search, and web automation - revolutionize your daily workflow efficiency.

## Features

### Processing Flow

Open Super Whisper V2 operates through the following 4 steps:

```
🎙️ Voice Input → 📝 Transcription → 🤖 Agent Processing → 📋 Result Output
```

### 🎙️ **Voice Input**

- **Global hotkeys** - Launch instantly from any application
- **One-click recording** - Simple recording start/stop with UI buttons
- **Background operation** - Always available via system tray

### 📝 **Transcription**

- **OpenAI Whisper powered** - Industry-leading speech recognition accuracy
- **Multi-language support** - Auto-detection and 125+ language support
- **Custom vocabulary** - Enhanced accuracy for technical terms and proper nouns

### 🤖 **Agent Processing**

- **Instruction sets** - Pre-defined AI agents specialized for different purposes
- **External tool integration** - Extensibility via MCP (Model Context Protocol)
- **Multi-context** - Processing that combines clipboard text, images, and web search

### 📋 **Result Output**

- **Markdown rendering** - Rich text display including LaTeX math formulas
- **Auto-clipboard** - Automatic copying of results to clipboard upon completion
- **Immediate use** - Results ready for instant use in other applications

## Project Structure

```
.
├── run_open_super_whisper.py                      # Application entry point
├── pyproject.toml                                 # Project configuration and dependencies for uv
├── uv.lock                                        # Project configuration and dependencies for uv
├── assets/                                        # Assets (icons, audio files, etc.)
│   ├── cancel_processing.wav                      # Sound played when processing completed
│   ├── complete_processing.wav                    # Sound played when processing canceled
│   ├── icon.icns                                  # Application icon (macOS)
│   ├── icon.ico                                   # Application icon (Windows)
│   ├── icon.png                                   # Application icon (cross-platform)
│   ├── start_recording.wav                        # Sound played when recording started
│   └── stop_recording.wav                         # Sound played when recording stoped
├── ffmpeg/                                        # FFmpeg executables and libraries
│   ├── bin/                                       # FFmpeg binary files (executables, DLLs)
│   ├── lib/                                       # Library files
│   ├── include/                                   # Include files
│   └── doc/                                       # Documentation
├── docs/                                          # Documentation and sample files
│   ├── README.md                                  # Project documentation (English)
│   ├── README_ja.md                               # Project documentation (Japanese)
│   ├── settings_sample_en.json                    # Sample settings file (English)
│   └── settings_sample_ja.json                    # Sample settings file (Japanese)
├── core/                                          # Core functionality (GUI-independent, fully implemented)
│   ├── __init__.py
│   ├── api/                                       # API client factory and utilities
│   │   ├── __init__.py
│   │   └── api_client_factory.py
│   ├── key/                                       # Keyboard and hotkey management
│   │   ├── __init__.py
│   │   ├── hotkey_manager.py                      # Global hotkey management
│   │   ├── key_formatter.py                       # Key formatting utilities
│   │   └── key_state_tracker.py                   # Key state tracking
│   ├── llm/                                       # Large Language Model processing
│   │   ├── __init__.py
│   │   ├── llm_model.py                           # LLM model data structures
│   │   ├── llm_model_manager.py                   # LLM model management
│   │   └── llm_processor.py                       # LLM processing implementation
│   ├── pipelines/                                 # Processing pipelines and instruction sets
│   │   ├── __init__.py
│   │   ├── instruction_set.py                     # Instruction set data model
│   │   ├── instruction_sets_manager.py            # Instruction set management
│   │   ├── pipeline.py                            # Unified processing pipeline
│   │   └── pipeline_result.py                     # Pipeline result data model
│   ├── recorder/                                  # Audio recording functionality
│   │   ├── __init__.py
│   │   └── audio_recorder.py                      # Audio recording implementation
│   └── stt/                                       # Speech-to-text functionality
│       ├── __init__.py
│       ├── audio_chunker.py                       # Audio file chunking for large files
│       ├── stt_lang_model.py                      # Language model data structures
│       ├── stt_lang_model_manager.py              # Language model management
│       ├── stt_model.py                           # STT model data structures
│       ├── stt_model_manager.py                   # STT model management
│       └── stt_processor.py                       # Speech-to-text processing implementation
└── gui/                                           # GUI-related functionality (Qt-dependent)
    ├── __init__.py
    ├── main.py                                    # GUI entry point
    └── app/                                       # Main application components
        ├── __init__.py
        ├── controllers/                           # MVC Controllers
        │   ├── __init__.py
        │   ├── main_controller.py                 # Main application controller
        │   ├── dialogs/                           # Dialog controllers
        │   │   ├── __init__.py
        │   │   ├── api_key_dialog_controller.py
        │   │   ├── hotkey_dialog_controller.py
        │   │   ├── instruction_dialog_controller.py
        │   │   └── settings_dialog_controller.py
        │   └── widgets/                           # Widget controllers
        │       ├── __init__.py
        │       └── status_indicator_controller.py
        ├── managers/                              # Application managers
        │   ├── __init__.py
        │   ├── audio_manager.py                   # Audio notification management
        │   ├── icon_manager.py                    # Application icon management
        │   ├── instruction_sets_manager.py        # GUI instruction set management
        │   ├── keyboard_manager.py                # GUI keyboard management
        │   └── settings_manager.py                # Application settings management
        ├── models/                                # MVC Models
        │   ├── __init__.py
        │   ├── main_model.py                      # Main application model
        │   ├── dialogs/                           # Dialog models
        │   │   ├── __init__.py
        │   │   ├── api_key_dialog_model.py
        │   │   ├── hotkey_dialog_model.py
        │   │   ├── instruction_dialog_model.py
        │   │   └── settings_dialog_model.py
        │   └── widgets/                           # Widget models
        │       ├── __init__.py
        │       └── status_indicator_model.py
        ├── utils/                                 # GUI utility functions
        │   ├── __init__.py
        │   ├── clipboard_utils.py                 # Clipboard operations
        │   └── pyinstaller_utils.py               # Resource path resolution
        └── views/                                 # MVC Views
            ├── __init__.py
            ├── main_window.py                     # Main application window
            ├── dialogs/                           # Dialog windows
            │   ├── __init__.py
            │   ├── api_key_dialog.py
            │   ├── hotkey_dialog.py
            │   ├── instruction_dialog.py
            │   └── settings_dialog.py
            ├── factories/                         # View factories
            │   ├── __init__.py
            │   ├── api_key_dialog_factory.py
            │   ├── hotkey_dialog_factory.py
            │   ├── instruction_dialog_factory.py
            │   ├── main_window_factory.py
            │   ├── settings_dialog_factory.py
            │   └── status_indicator_factory.py
            ├── tray/                              # System tray functionality
            │   ├── __init__.py
            │   └── system_tray.py
            └── widgets/                           # Custom widgets
                ├── __init__.py
                ├── markdown_text_browser.py       # Markdown rendering widget
                └── status_indicator.py            # Status indicator window
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/TakanariShimbo/open-super-whisper-v2.git
   cd open-super-whisper-v2
   ```

   Note: This requires Git to be installed on your system.

2. Install dependencies:

   ```bash
   uv sync
   ```

   Note: This requires UV to be installed on your system.

3. Set up FFmpeg:

   The application requires FFmpeg.

   **For Windows:**

   You need to create an `ffmpeg` directory in the project root with a `bin` subdirectory containing FFmpeg executables.

   ```bash
   # 1. Download FFmpeg from https://ffmpeg.org/download.html
   #    - Recommended: "ffmpeg-release-essentials.zip" (Windows version)

   # 2. Extract the downloaded ZIP file

   # 3. Copy the entire extracted folder to the ffmpeg directory in the project root
   #    Example: Extracted "ffmpeg-x.x.x-win64-static/" → Project's "ffmpeg/"
   ```

   The application will automatically add the `ffmpeg/bin` directory to the PATH when started.

## Configuration

### Sample Settings Usage

Sample configuration files are provided in the `docs/` directory:

- `settings_sample_en.json` - English version with pre-configured instruction sets
- `settings_sample_ja.json` - Japanese version with the same functionality

To use a sample file:

1. Create the settings directory in your user home directory:

   ```bash
   mkdir ~/.open_super_whisper
   ```

2. Copy the desired sample file to the settings directory:

   ```bash
   # For English settings
   cp docs/settings_sample_en.json ~/.open_super_whisper/settings.json

   # For Japanese settings
   cp docs/settings_sample_ja.json ~/.open_super_whisper/settings.json
   ```

**Note:** The application expects the settings file to be located at `~/.open_super_whisper/settings.json` (where `~` represents your user home directory).

### Sample Settings Content

Both sample files include the following instruction sets:

- **Transcription Agent** (Ctrl+Shift+1) - Basic speech-to-text conversion
- **Document Creation Agent** (Ctrl+Shift+2) - Automatically convert speech to formal written documents
- **Search Keywords Agent** (Ctrl+Shift+3) - Auto-generate optimal search keywords from speech
- **Text Q&A Agent** (Ctrl+Shift+4) - Analyze clipboard text and answer questions (with web search)
- **Image Q&A Agent** (Ctrl+Shift+5) - Analyze clipboard images and answer questions (with web search)
- **Web Automation Agent** (Ctrl+Shift+6) - Autonomous web interactions using Playwright

## How to Run

To start the application, run:

```bash
python run_open_super_whisper.py
```

Command line options:

- `--minimized` or `-m`: Start the application minimized to the system tray

## Packaging

To package the application into a standalone executable:

```bash
# Windows
python -m PyInstaller --onefile --icon assets/icon.ico --name "OpenSuperWhisper" --add-data "assets;assets" --add-data "ffmpeg;ffmpeg" run_open_super_whisper.py

# For macOS
# python -m PyInstaller --onefile --icon assets/icon.icns --name "OpenSuperWhisper" --add-data "assets:assets" run_open_super_whisper.py

# For Linux
# python -m PyInstaller --onefile --icon assets/icon.png --name "OpenSuperWhisper" --add-data "assets:assets" run_open_super_whisper.py
```

The Windows command does the following:

- `--onefile`: Creates a single executable file
- `--icon assets/icon.ico`: Sets the application icon
- `--name "OpenSuperWhisper"`: Specifies the output filename
- `--add-data "assets;assets"`: Includes the entire assets directory in the executable
- `--add-data "ffmpeg;ffmpeg"`: Includes the entire ffmpeg directory in the executable

Once the build is complete, you'll find `OpenSuperWhisper.exe` in the `dist` folder on Windows, `OpenSuperWhisper.app` in the `dist` folder on macOS, or `OpenSuperWhisper` in the `dist` folder on Linux.

## License

This project is licensed under the MIT License.
