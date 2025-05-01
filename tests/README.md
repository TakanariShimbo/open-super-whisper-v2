# Test Tools for Open Super Whisper v2

This directory contains command-line test tools for the various components of the Open Super Whisper v2 project.

## Overview

Each test file corresponds to a specific component in the `core` directory and provides a way to test the functionality from the command line. The tests are written in Python and can be run directly.

## Requirements

- Python 3.8+
- Dependencies from the main project

## Running Tests

All tests can be run directly from the command line. Each test provides its own command-line options and help information.

### Basic Usage

```bash
# Run a test
python tests/test_stt_model.py

# Get help for a specific test
python tests/test_stt_processor.py --help
```

## Available Tests

### STT Module Tests

- `test_audio_chunker.py` - Tests the audio chunking functionality
- `test_stt_model.py` - Tests the STT model class
- `test_stt_model_manager.py` - Tests the STT model manager
- `test_stt_processor.py` - Tests the STT processor for transcribing audio files

### LLM Module Tests

- `test_llm_model.py` - Tests the LLM model class
- `test_llm_model_manager.py` - Tests the LLM model manager
- `test_llm_processor.py` - Tests the LLM processor for processing text

### Pipeline Module Tests

- `test_pipeline_result.py` - Tests the pipeline result data class
- `test_stt_llm_pipeline.py` - Tests the unified STT-LLM processing pipeline

### Recorder Module Tests

- `test_audio_recorder.py` - Tests the audio recording functionality

### UI Module Tests

- `test_hot_key_manager.py` - Tests the hotkey management system

### Utils Module Tests

- `test_instruction_set.py` - Tests the instruction set class
- `test_instruction_manager.py` - Tests the instruction set manager

## Examples

### STT Module Tests

#### Testing Audio Chunker

```bash
# Basic test with an audio file
python tests/test_audio_chunker.py /path/to/audio/file.mp3

# Customize maximum chunk size
python tests/test_audio_chunker.py /path/to/audio/file.mp3 --max-size 10.0

# Enable verbose output
python tests/test_audio_chunker.py /path/to/audio/file.mp3 -v
```

#### Testing STT Model

```bash
# Basic test of STT model functionality
python tests/test_stt_model.py

# With verbose output to show all model details
python tests/test_stt_model.py -v
```

#### Testing STT Model Manager

```bash
# Test the STT model manager functionality
python tests/test_stt_model_manager.py

# With verbose output to show detailed model information
python tests/test_stt_model_manager.py -v
```

#### Testing STT Processor

```bash
# Basic transcription test
python tests/test_stt_processor.py /path/to/audio/file.mp3

# Specify language and custom vocabulary
python tests/test_stt_processor.py /path/to/audio/file.mp3 --language en --vocabulary "OpenAI, GPT, Whisper"

# Use a specific model and add transcription instructions
python tests/test_stt_processor.py /path/to/audio/file.mp3 --model whisper-1 --instruction "Transcribe with proper punctuation"
```

### LLM Module Tests

#### Testing LLM Model

```bash
# Test the LLM model functionality
python tests/test_llm_model.py

# With verbose output to show detailed model information
python tests/test_llm_model.py -v
```

#### Testing LLM Model Manager

```bash
# Test the LLM model manager functionality
python tests/test_llm_model_manager.py

# With verbose output to show all model details
python tests/test_llm_model_manager.py -v
```

#### Testing LLM Processor

```bash
# Basic text processing test
python tests/test_llm_processor.py "Please summarize this text."

# Using streaming API with an image
python tests/test_llm_processor.py "Analyze this image." --image /path/to/image.jpg --stream

# Using a specific model with custom instructions
python tests/test_llm_processor.py "Explain quantum computing." --model gpt-4o --instruction "Respond like a university professor"
```

### Pipeline Module Tests

#### Testing Pipeline Result

```bash
# Test the pipeline result functionality
python tests/test_pipeline_result.py

# With verbose output to show detailed result properties
python tests/test_pipeline_result.py -v
```

#### Testing STT-LLM Pipeline

```bash
# Basic pipeline test (STT + LLM)
python tests/test_stt_llm_pipeline.py /path/to/audio/file.mp3

# Transcription only (no LLM)
python tests/test_stt_llm_pipeline.py /path/to/audio/file.mp3 --no-llm

# With streaming LLM responses
python tests/test_stt_llm_pipeline.py /path/to/audio/file.mp3 --stream

# Specify language and models
python tests/test_stt_llm_pipeline.py /path/to/audio/file.mp3 --language ja --stt-model gpt-4o-transcribe --llm-model gpt-4o

# Test with an image file
python tests/test_stt_llm_pipeline.py /path/to/audio/file.mp3 --image-file /path/to/image.jpg
```

### Recorder Module Tests

#### Testing Audio Recorder

```bash
# Basic test with default settings (5-second recording)
python tests/test_audio_recorder.py

# Set recording duration and audio parameters
python tests/test_audio_recorder.py --duration 10 --sample-rate 48000 --channels 2

# List available microphone devices
python tests/test_audio_recorder.py --list-devices

# Run advanced test with threading
python tests/test_audio_recorder.py --threading-test
```

### UI Module Tests

#### Testing Hot Key Manager

```bash
# Basic test for 10 seconds
python tests/test_hot_key_manager.py

# Longer test duration with verbose output
python tests/test_hot_key_manager.py --duration 30 -v
```

### Utils Module Tests

#### Testing Instruction Set

```bash
# Test the instruction set functionality
python tests/test_instruction_set.py

# With verbose output to show detailed instruction information
python tests/test_instruction_set.py -v
```

#### Testing Instruction Manager

```bash
# Test with a temporary config file (default)
python tests/test_instruction_manager.py

# Provide a specific file path for saving/loading
python tests/test_instruction_manager.py --file-path ./my-config.json

# With verbose output to show detailed instruction information
python tests/test_instruction_manager.py -v

# Using an existing file without creating a temporary one
python tests/test_instruction_manager.py --file-path ./my-config.json --no-temp-file
```

## Notes

- Most tests require an OpenAI API key set in the environment variable `OPENAI_API_KEY` or passed via the `--api-key` parameter.
- Tests that involve audio recording or hotkeys require appropriate system permissions.
- The test results are displayed in the console.
