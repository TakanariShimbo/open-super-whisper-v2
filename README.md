# Open Super Whisper V2

**The Ultimate Audio Transcription & AI Analysis Tool**

Transform your voice into intelligent, actionable text with this powerful PyQt6-based desktop application. Seamlessly combine OpenAI's cutting-edge Whisper speech recognition with advanced Large Language Models to not just transcribe, but analyze, summarize, and enhance your audio content.

## Features

### 🎯 **Smart Recording & Transcription**

- **One-click recording** with instant audio capture
- **Global hotkey support** - Start/stop recording from anywhere on your system
- **Multi-language support** with automatic language detection
- **High-quality transcription** powered by OpenAI's Whisper API
- **Large file handling** with intelligent audio chunking

### 🧠 **AI-Powered Content Processing**

- **LLM integration** - Process transcriptions with GPT-4, Claude, and other models
- **Intelligent analysis** - Summarize, translate, or transform your content
- **Custom AI instructions** - Tailor AI responses to your specific needs
- **Streaming responses** - See AI analysis in real-time as it's generated
- **MCP server support** - Connect to external tools and data sources via Model Context Protocol

### ⚡ **Advanced Workflow Management**

- **Instruction Sets** - Create and switch between different processing profiles
- **Custom vocabularies** - Improve accuracy for technical terms and specialized content
- **Clipboard integration** - Automatically include clipboard content in AI processing
- **Profile-based hotkeys** - Assign keyboard shortcuts to different workflows

### 💼 **Professional User Experience**

- **Clean, modern interface** built with PyQt6
- **System tray integration** - Keep the app running in the background
- **Visual status indicators** - Always know what's happening
- **Sound notifications** - Audio feedback for recording states
- **Auto-clipboard** - Automatically copy results when processing completes

### 🔧 **Flexible & Customizable**

- **Multiple AI models** - Choose the best model for your task
- **Configurable settings** - Customize every aspect of the application
- **Markdown support** - Rich text rendering with LaTeX math support
- **Cross-platform compatibility** - Works on Windows, macOS, and Linux

## Project Structure

```
.
├── run_open_super_whisper.py                      # Application entry point
├── README.md                                      # Project description
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

1. Ensure you have UV installed.

2. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/open-super-whisper-v2.git
   cd open-super-whisper-v2
   ```

3. Install dependencies:

   ```bash
   uv sync
   ```

4. Set up FFmpeg:

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

This project is licensed under the MIT License. See the LICENSE file for more details.
