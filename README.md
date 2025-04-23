# Open Super Whisper - Qt Remake

A PyQt6-based GUI application for audio transcription using OpenAI's Whisper API. This application allows for recording audio, sending it to Whisper for transcription, and displaying the results.

## Features

- Complete PyQt6-based GUI implementation 
- Global hotkey support for starting/stopping recording
- Custom vocabulary and instruction sets management
- System tray integration
- Multiple language and model support
- Clipboard integration
- Status indicator window
- Settings management

## Project Structure

- `main.py` - Application entry point
- `src/` - Source code directory
  - `core/` - Core functionality interfaces
    - `audio_recorder.py` - Audio recording interface (needs implementation)
    - `hotkeys.py` - Global hotkey management (needs implementation)
    - `instruction_sets.py` - Custom vocabulary and instructions
    - `whisper_api.py` - Transcription API interface (needs implementation)
  - `gui/` - UI implementation
    - `components/` - Reusable UI components
      - `dialogs/` - Dialog windows
        - `api_key_dialog.py` - Dialog for managing API keys
        - `hotkey_dialog.py` - Dialog for setting global hotkeys
        - `instruction_sets_dialog.py` - Dialog for managing instruction sets
        - `simple_message_dialog.py` - Generic message dialog
      - `widgets/` - Custom widgets
        - `status_indicator.py` - Status indicator widget
    - `resources/` - Application resources
      - `config.py` - Configuration settings
      - `labels.py` - UI text labels
    - `utils/` - Utility functions
      - `resource_helper.py` - Resource path resolver
    - `windows/` - Main application windows
      - `main_window.py` - Main application window
    - `main.py` - GUI entry point
- `assets/` - Application assets (icons, sounds)
  - `complete_sound.wav` - Sound played when transcription is complete
  - `icon.ico` - Application icon (Windows)
  - `icon.png` - Application icon (cross-platform)
  - `start_sound.wav` - Sound played when recording starts
  - `stop_sound.wav` - Sound played when recording stops

## How to Run

To run the application:

```bash
python main.py
```

