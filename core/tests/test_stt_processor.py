#!/usr/bin/env python3
"""
STT Processor Test

This test verifies the STTProcessor functionality using real OpenAI API calls.
The test allows interactive configuration of model, vocabulary, and instructions.
"""

import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.stt.stt_processor import STTProcessor
from core.api.api_client_factory import APIClientFactory


def _get_test_api_key() -> str | None:
    """Get API key from user input for testing"""
    try:
        api_key = input("Enter your OpenAI API key for testing: ").strip()
        return api_key if api_key else None
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return None


def _create_test_client() -> tuple[bool, Any]:
    """Create a real OpenAI client for testing"""
    api_key = _get_test_api_key()

    if not api_key:
        print("❌ No API key provided")
        return False, None

    print(f"Creating client with API key: {api_key[:10]}...")
    return APIClientFactory.create_client(api_key)


def _get_test_audio_file() -> Path:
    """Get the test audio file path"""
    test_audio_path = Path(__file__).parent / "toeic.mp3"

    if not test_audio_path.exists():
        raise FileNotFoundError(f"Test audio file not found: {test_audio_path}")

    return test_audio_path


def _select_model(processor: STTProcessor) -> str:
    """Allow user to select STT model"""
    available_models = processor.AVAILABLE_MODELS

    print("\n🤖 Available STT Models:")
    for i, model in enumerate(available_models, 1):
        default_marker = " (default)" if model["id"] == processor.DEFAULT_MODEL_ID else ""
        print(f"  {i}. {model['name']}{default_marker}")
        print(f"     ID: {model['id']}")
        print(f"     Description: {model['description'][:80]}...")
        print()

    while True:
        try:
            choice = input(f"Select model (1-{len(available_models)}) or press Enter for default: ").strip()

            if not choice:
                # Use default model
                return processor.DEFAULT_MODEL_ID

            model_index = int(choice) - 1
            if 0 <= model_index < len(available_models):
                selected_model = available_models[model_index]
                processor.set_model(selected_model["id"])
                print(f"✅ Model set to: {selected_model['name']}")
                return selected_model["id"]
            else:
                print("❌ Invalid selection. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n⚠️ Using default model")
            return processor.DEFAULT_MODEL_ID


def _configure_vocabulary(processor: STTProcessor) -> str | None:
    """Allow user to configure custom vocabulary"""
    print("\n📝 Custom Vocabulary Configuration:")
    print("You can specify custom vocabulary to improve transcription accuracy.")
    print("Examples: 'TOEIC, listening, comprehension' or 'PyTorch, TensorFlow, AI'")

    try:
        vocabulary = input("Enter custom vocabulary (or press Enter to skip): ").strip()

        if vocabulary:
            processor.set_custom_vocabulary(vocabulary)
            print(f"✅ Custom vocabulary set: {vocabulary}")
            return vocabulary
        else:
            print("✅ No custom vocabulary set")
            return None
    except KeyboardInterrupt:
        print("\n⚠️ Skipping custom vocabulary")
        return None


def _configure_system_instruction(processor: STTProcessor) -> str | None:
    """Allow user to configure system instruction"""
    print("\n🎯 System Instruction Configuration:")
    print("You can provide instructions to control transcription behavior.")
    print("Examples: 'Add punctuation and proper capitalization' or 'Format as bullet points'")

    try:
        instruction = input("Enter system instruction (or press Enter to skip): ").strip()

        if instruction:
            processor.set_system_instruction(instruction)
            print(f"✅ System instruction set: {instruction}")
            return instruction
        else:
            print("✅ No system instruction set")
            return None
    except KeyboardInterrupt:
        print("\n⚠️ Skipping system instruction")
        return None


def _configure_language() -> str | None:
    """Allow user to configure language parameter"""
    print("\n🌍 Language Configuration:")
    print("You can specify the language for transcription.")
    print("Examples: 'en' (English), 'ja' (Japanese), 'es' (Spanish), 'fr' (French)")

    try:
        language = input("Enter language code (or press Enter for auto-detection): ").strip()

        if language:
            print(f"✅ Language set to: {language}")
            return language
        else:
            print("✅ Using auto-detection")
            return None
    except KeyboardInterrupt:
        print("\n⚠️ Using auto-detection")
        return None


def test_stt_processor() -> bool:
    """Main STT processor test with interactive configuration"""
    print("🧪 STTProcessor - Interactive Test Suite")
    print("=" * 60)
    print("This test uses real OpenAI API and requires a valid API key.\n")

    try:
        # Create real client
        is_successful, client = _create_test_client()

        if not is_successful:
            print("❌ Failed to create API client")
            return False

        print("✅ API client created successfully")

        # Create processor
        processor = STTProcessor(client)

        # Get test audio file
        test_audio_path = _get_test_audio_file()
        print(f"✅ Using test audio file: {test_audio_path.name}")

        # Get file size for logging
        file_size_mb = test_audio_path.stat().st_size / (1024 * 1024)
        print(f"📁 File size: {file_size_mb:.2f}MB")

        # Interactive configuration
        print("\n" + "=" * 60)
        print("🔧 Interactive Configuration")
        print("=" * 60)

        # Model selection
        selected_model = _select_model(processor)

        # Vocabulary configuration
        vocabulary = _configure_vocabulary(processor)

        # System instruction configuration
        instruction = _configure_system_instruction(processor)

        # Language configuration
        language = _configure_language()

        # Summary of configuration
        print("\n" + "=" * 60)
        print("📋 Configuration Summary")
        print("=" * 60)
        print(f"🤖 Model: {selected_model}")
        print(f"📝 Custom Vocabulary: {vocabulary or 'None'}")
        print(f"🎯 System Instruction: {instruction or 'None'}")
        print(f"🌍 Language: {language or 'Auto-detection'}")
        print(f"🎵 Audio File: {test_audio_path.name} ({file_size_mb:.2f}MB)")

        # Confirm to proceed
        print("\n" + "=" * 60)
        try:
            proceed = input("🚀 Start transcription? [Y/n]: ").strip().lower()
            if proceed and proceed not in ["y", "yes"]:
                print("⚠️ Test cancelled by user")
                return False
        except KeyboardInterrupt:
            print("\n⚠️ Test cancelled by user")
            return False

        # Process the audio file
        print("\n" + "=" * 60)
        print("🎵 Processing Audio")
        print("=" * 60)
        print("Starting transcription...")

        start_time = time.time()
        transcription = processor.transcribe_file_with_chunks(str(test_audio_path), language=language)
        end_time = time.time()

        # Display results
        print("\n" + "=" * 60)
        print("📊 Transcription Results")
        print("=" * 60)

        if transcription and len(transcription.strip()) > 0:
            print(f"✅ Transcription completed successfully!")
            print(f"⏱️ Processing time: {end_time - start_time:.2f} seconds")
            print(f"📊 Result length: {len(transcription)} characters")
            print(f"📝 Word count: {len(transcription.split())} words")

            print("\n" + "-" * 60)
            print("📄 Transcription Result:")
            print("-" * 60)
            print(transcription.strip())
            print("-" * 60)

        else:
            print("❌ Empty or invalid transcription received")
            return False

        print("\n✅ STT Processor test completed successfully!")
        return True

    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False


def main() -> int:
    """Main test execution"""
    try:
        success = test_stt_processor()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
