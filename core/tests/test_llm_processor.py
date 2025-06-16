#!/usr/bin/env python3
"""
LLM Processor Test

This test verifies the LLMProcessor functionality using real OpenAI API calls.
The test allows interactive configuration of model and system instructions.
"""

import sys
import time
from pathlib import Path
import asyncio

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.llm.llm_processor import LLMProcessor
from core.api.api_key_checker import APIKeyChecker


def _get_test_api_keys() -> tuple[str | None, str | None, str | None]:
    """Get API keys from user input for testing"""
    try:
        print("Enter API keys for testing:")
        openai_api_key = input("OpenAI API key (required): ").strip()
        print("Optional API keys (press Enter to skip):")
        anthropic_api_key = input("Anthropic API key: ").strip()
        gemini_api_key = input("Gemini API key: ").strip()
        
        return (
            openai_api_key if openai_api_key else None,
            anthropic_api_key if anthropic_api_key else None,
            gemini_api_key if gemini_api_key else None
        )
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return None, None, None


def _get_valid_api_keys() -> tuple[bool, str | None, str | None, str | None]:
    """Get valid API keys from user input"""
    openai_api_key, anthropic_api_key, gemini_api_key = _get_test_api_keys()

    # OpenAI API key is required
    if not openai_api_key:
        print("❌ OpenAI API key is required")
        return False, None, None, None

    valid_keys = []
    
    # Validate OpenAI API key (required)
    print(f"Validating OpenAI API key: {openai_api_key[:10]}...")
    if APIKeyChecker.check_openai_api_key(openai_api_key=openai_api_key):
        print("✅ OpenAI API key is valid")
        valid_keys.append("OpenAI")
    else:
        print("❌ OpenAI API key is invalid")
        return False, None, None, None
    
    # Validate Anthropic API key if provided (optional)
    if anthropic_api_key:
        print(f"Validating Anthropic API key: {anthropic_api_key[:10]}...")
        if APIKeyChecker.check_anthropic_api_key(anthropic_api_key=anthropic_api_key):
            print("✅ Anthropic API key is valid")
            valid_keys.append("Anthropic")
        else:
            print("❌ Anthropic API key is invalid, skipping")
            anthropic_api_key = None
    
    # Validate Gemini API key if provided (optional)
    if gemini_api_key:
        print(f"Validating Gemini API key: {gemini_api_key[:10]}...")
        if APIKeyChecker.check_gemini_api_key(gemini_api_key=gemini_api_key):
            print("✅ Gemini API key is valid")
            valid_keys.append("Gemini")
        else:
            print("❌ Gemini API key is invalid, skipping")
            gemini_api_key = None
    
    print(f"✅ Valid API keys found for: {', '.join(valid_keys)}")
    return True, openai_api_key, anthropic_api_key, gemini_api_key


def _select_model(processor: LLMProcessor) -> str:
    """Allow user to select LLM model"""
    available_models = processor.AVAILABLE_MODELS

    print("\n🤖 Available LLM Models:")
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


def _configure_system_instruction(processor: LLMProcessor) -> str | None:
    """Allow user to configure system instruction"""
    print("\n🎯 System Instruction Configuration:")
    print("You can provide instructions to control the LLM behavior.")
    print("Examples: 'You are a helpful coding assistant' or 'Respond in Japanese'")

    try:
        instruction = input("Enter system instruction (or press Enter to skip): ").strip()

        if instruction:
            processor.set_system_instruction(instruction)
            print(f"✅ System instruction set: {instruction}")
            return instruction
        else:
            print("✅ Using default system instruction")
            return None
    except KeyboardInterrupt:
        print("\n⚠️ Using default system instruction")
        return None


def _get_test_input() -> tuple[str, bytes | None]:
    """Get test input (text and optional image)"""
    print("\n📝 Test Input Configuration:")

    # Get text input
    try:
        text = input("Enter your text prompt: ").strip()
        if not text:
            print("❌ No text provided")
            return "", None
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled")
        return "", None

    # Ask about image input
    try:
        use_image = input("Include an image? [y/N]: ").strip().lower()
        image_data = None

        if use_image in ["y", "yes"]:
            print("\n🖼️ Image Options:")
            print("1. Use programmer.png (default test image)")
            print("2. Specify custom image path")

            while True:
                try:
                    image_choice = input("Select image option (1-2) or press Enter for default: ").strip()

                    if not image_choice or image_choice == "1":
                        # Use default programmer.png
                        image_path = Path(__file__).parent / "sample_data" / "programmer.png"
                        if image_path.exists():
                            try:
                                with open(image_path, "rb") as f:
                                    image_data = f.read()
                                print(f"✅ Image loaded: {image_path.name} ({len(image_data)} bytes)")
                                break
                            except Exception as e:
                                print(f"❌ Failed to load image: {e}")
                                break
                        else:
                            print(f"❌ Default image file not found: {image_path}")
                            break

                    elif image_choice == "2":
                        # Get custom image path
                        custom_path = input("Enter image file path: ").strip()
                        if custom_path:
                            image_path = Path(custom_path)
                            if image_path.exists():
                                try:
                                    with open(image_path, "rb") as f:
                                        image_data = f.read()
                                    print(f"✅ Image loaded: {image_path.name} ({len(image_data)} bytes)")
                                    break
                                except Exception as e:
                                    print(f"❌ Failed to load image: {e}")
                                    # Ask if user wants to try again
                                    retry = input("Try again? [y/N]: ").strip().lower()
                                    if retry not in ["y", "yes"]:
                                        break
                            else:
                                print(f"❌ Image file not found: {image_path}")
                                # Ask if user wants to try again
                                retry = input("Try again? [y/N]: ").strip().lower()
                                if retry not in ["y", "yes"]:
                                    break
                        else:
                            print("❌ No path provided")
                            break
                    else:
                        print("❌ Invalid selection. Please try again.")

                except KeyboardInterrupt:
                    print("\n⚠️ Skipping image input")
                    break
        else:
            print("✅ Text-only processing")

    except KeyboardInterrupt:
        print("\n⚠️ Using text-only processing")
        image_data = None

    return text, image_data


def _select_processing_mode() -> str:
    """Allow user to select processing mode"""
    print("\n⚡ Processing Mode:")
    print("1. Standard processing")
    print("2. Streaming processing")

    while True:
        try:
            choice = input("Select processing mode (1-2) or press Enter for standard: ").strip()

            if not choice or choice == "1":
                return "standard"
            elif choice == "2":
                return "streaming"
            else:
                print("❌ Invalid selection. Please try again.")
        except KeyboardInterrupt:
            print("\n⚠️ Using standard processing")
            return "standard"


def test_llm_processor() -> bool:
    """Main LLM processor test with interactive configuration"""
    print("🧪 LLMProcessor - Interactive Test Suite")
    print("=" * 60)
    print("This test requires a valid OpenAI API key. Other APIs are optional.\n")

    try:
        # Get valid API keys
        is_valid, openai_api_key, anthropic_api_key, gemini_api_key = _get_valid_api_keys()

        if not is_valid:
            print("❌ Failed to get valid OpenAI API key")
            return False

        print("✅ API keys validated successfully")

        # Create processor with OpenAI (required) and optional API keys
        processor = LLMProcessor(
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key or "",
            gemini_api_key=gemini_api_key or ""
        )

        # Interactive configuration
        print("\n" + "=" * 60)
        print("🔧 Interactive Configuration")
        print("=" * 60)

        # Model selection
        selected_model = _select_model(processor)

        # System instruction configuration
        instruction = _configure_system_instruction(processor)

        # Get test input
        text_input, image_data = _get_test_input()

        if not text_input:
            print("❌ No text input provided")
            return False

        # Processing mode selection
        processing_mode = _select_processing_mode()

        # Summary of configuration
        print("\n" + "=" * 60)
        print("📋 Configuration Summary")
        print("=" * 60)
        print(f"🤖 Model: {selected_model}")
        print(f"🎯 System Instruction: {instruction or 'Default (helpful assistant)'}")
        print(f"📝 Text Input: {text_input[:50]}{'...' if len(text_input) > 50 else ''}")
        print(f"🖼️ Image Input: {'Yes' if image_data else 'No'}")
        print(f"⚡ Processing Mode: {processing_mode.capitalize()}")

        # Confirm to proceed
        print("\n" + "=" * 60)
        try:
            proceed = input("🚀 Start processing? [Y/n]: ").strip().lower()
            if proceed and proceed not in ["y", "yes"]:
                print("⚠️ Test cancelled by user")
                return False
        except KeyboardInterrupt:
            print("\n⚠️ Test cancelled by user")
            return False

        # Process the input
        print("\n" + "=" * 60)
        print("🔄 Processing Input")
        print("=" * 60)

        start_time = time.time()

        if processing_mode == "streaming":
            print("Starting streaming processing...\n")
            print("-" * 60)

            def print_chunk(chunk: str) -> None:
                print(chunk, end="", flush=True)

            response = asyncio.run(processor.process_text_with_stream(text_input, print_chunk, image_data=image_data))
            print("\n" + "-" * 60)

        else:
            print("Starting standard processing...")
            response = asyncio.run(processor.process_text(text_input, image_data=image_data))

        end_time = time.time()

        # Display results
        print("\n" + "=" * 60)
        print("📊 Processing Results")
        print("=" * 60)

        if response and len(response.strip()) > 0:
            print(f"✅ Processing completed successfully!")
            print(f"⏱️ Processing time: {end_time - start_time:.2f} seconds")
            print(f"📊 Response length: {len(response)} characters")
            print(f"📝 Word count: {len(response.split())} words")

            if processing_mode == "standard":
                print("\n" + "-" * 60)
                print("📄 Response:")
                print("-" * 60)
                print(response.strip())
                print("-" * 60)

        else:
            print("❌ Empty or invalid response received")
            return False

        print("\n✅ LLM Processor test completed successfully!")
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
        success = test_llm_processor()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
