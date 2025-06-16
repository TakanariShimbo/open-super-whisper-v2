#!/usr/bin/env python3
"""
Pipeline Test

This test verifies the Pipeline functionality using real OpenAI API calls.
The test allows interactive configuration of instruction sets and processing options.
"""

import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.pipelines.pipeline import Pipeline
from core.pipelines.instruction_set import InstructionSet


def _get_test_openai_api_key() -> str | None:
    """Get API key from user input for testing"""
    try:
        openai_api_key = input("Enter your OpenAI API key for testing: ").strip()
        return openai_api_key if openai_api_key else None
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return None


def _create_test_pipeline() -> Pipeline | None:
    """Create a pipeline with real API key for testing"""
    openai_api_key = _get_test_openai_api_key()

    if not openai_api_key:
        print("❌ No API key provided")
        return None

    try:
        print(f"Creating pipeline with API key: {openai_api_key[:10]}...")
        pipeline = Pipeline(openai_api_key=openai_api_key)
        print("✅ Pipeline created successfully")
        return pipeline
    except ValueError as e:
        print(f"❌ Failed to create pipeline: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error creating pipeline: {e}")
        return None


def _get_test_audio_file() -> Path:
    """Get the test audio file path with user selection"""
    print("\n🎵 Audio File Options:")
    print("1. Use toeic.mp3 (default test audio)")
    print("2. Specify custom audio file path")
    print("3. Record live audio")

    while True:
        try:
            choice = input("Select audio option (1-3) or press Enter for default: ").strip()

            if not choice or choice == "1":
                # Use default toeic.mp3
                test_audio_path = Path(__file__).parent / "sample_data" / "toeic.mp3"
                if test_audio_path.exists():
                    file_size_mb = test_audio_path.stat().st_size / (1024 * 1024)
                    print(f"✅ Audio file loaded: {test_audio_path.name} ({file_size_mb:.2f}MB)")
                    return test_audio_path
                else:
                    raise FileNotFoundError(f"Default audio file not found: {test_audio_path}")

            elif choice == "2":
                # Get custom audio file path
                custom_path = input("Enter audio file path: ").strip()
                if custom_path:
                    audio_path = Path(custom_path)
                    if audio_path.exists():
                        # Check if it's likely an audio file
                        audio_extensions = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".mp4", ".mov"}
                        if audio_path.suffix.lower() in audio_extensions:
                            file_size_mb = audio_path.stat().st_size / (1024 * 1024)
                            print(f"✅ Audio file loaded: {audio_path.name} ({file_size_mb:.2f}MB)")
                            return audio_path
                        else:
                            print(f"⚠️ Warning: {audio_path.suffix} might not be a supported audio format")
                            proceed = input("Continue anyway? [y/N]: ").strip().lower()
                            if proceed in ["y", "yes"]:
                                file_size_mb = audio_path.stat().st_size / (1024 * 1024)
                                print(f"✅ Audio file loaded: {audio_path.name} ({file_size_mb:.2f}MB)")
                                return audio_path
                            else:
                                print("❌ Audio file selection cancelled")
                    else:
                        print(f"❌ Audio file not found: {audio_path}")
                else:
                    print("❌ No path provided")

            elif choice == "3":
                # Live recording will be handled in the main test
                print("✅ Live recording selected")
                return Path("live_recording")

            else:
                print("❌ Invalid selection. Please try again.")

        except KeyboardInterrupt:
            print("\n⚠️ Using default audio file")
            test_audio_path = Path(__file__).parent / "sample_data" / "toeic.mp3"
            if test_audio_path.exists():
                return test_audio_path
            else:
                raise FileNotFoundError(f"Default audio file not found: {test_audio_path}")


def _create_test_instruction_set() -> InstructionSet:
    """Create and configure a test instruction set"""
    print("\n🎯 Instruction Set Configuration:")
    print("Configure custom settings for the pipeline processing.")
    
    try:
        # Get name
        name = input("Enter instruction set name (or press Enter for 'Test Set'): ").strip()
        if not name:
            name = "Test Set"
        
        # STT Configuration
        print(f"\n📝 STT Configuration for '{name}':")
        stt_vocabulary = input("Enter STT custom vocabulary (or press Enter to skip): ").strip()
        stt_instructions = input("Enter STT system instructions (or press Enter to skip): ").strip()
        
        # Language selection
        print("\n🌍 Language Options:")
        print("Examples: 'en' (English), 'ja' (Japanese), 'es' (Spanish), 'fr' (French)")
        stt_language = input("Enter language code (or press Enter for auto-detection): ").strip()
        if not stt_language:
            stt_language = None
        
        # LLM Configuration
        print(f"\n🤖 LLM Configuration for '{name}':")
        llm_enabled_input = input("Enable LLM processing? [y/N]: ").strip().lower()
        llm_enabled = llm_enabled_input in ["y", "yes"]
        
        llm_instructions = ""
        llm_mcp_servers_json_str = r"{}"
        llm_clipboard_text_enabled = False
        llm_clipboard_image_enabled = False
        
        if llm_enabled:
            llm_instructions = input("Enter LLM system instructions (or press Enter to skip): ").strip()

            llm_mcp_servers_json_str = input("Enter MCP servers JSON string (or press Enter to skip): ").strip()

            clipboard_text_input = input("Include clipboard text in LLM processing? [y/N]: ").strip().lower()
            llm_clipboard_text_enabled = clipboard_text_input in ["y", "yes"]
            
            clipboard_image_input = input("Include clipboard images in LLM processing? [y/N]: ").strip().lower()
            llm_clipboard_image_enabled = clipboard_image_input in ["y", "yes"]

            web_search_input = input("Enable web search in LLM? [y/N]: ").strip().lower()
            llm_web_search_enabled = web_search_input in ["y", "yes"]
        
        # Create instruction set
        instruction_set = InstructionSet(
            name=name,
            stt_vocabulary=stt_vocabulary,
            stt_instructions=stt_instructions,
            stt_language=stt_language,
            llm_enabled=llm_enabled,
            llm_instructions=llm_instructions,
            llm_mcp_servers_json_str=llm_mcp_servers_json_str,
            llm_web_search_enabled=llm_web_search_enabled,
            llm_clipboard_text_enabled=llm_clipboard_text_enabled,
            llm_clipboard_image_enabled=llm_clipboard_image_enabled,
        )
        
        print(f"✅ Instruction set '{name}' created successfully")
        return instruction_set
        
    except KeyboardInterrupt:
        print("\n⚠️ Using default instruction set")
        return InstructionSet.get_default()


def _get_clipboard_content() -> tuple[str | None, bytes | None]:
    """Get clipboard content for testing"""
    print("\n📋 Clipboard Content Options:")
    print("1. No clipboard content")
    print("2. Add text content")
    print("3. Add image content")
    print("4. Add both text and image content")
    
    clipboard_text = None
    clipboard_image = None
    
    try:
        choice = input("Select clipboard option (1-4) or press Enter for none: ").strip()
        
        if not choice or choice == "1":
            print("✅ No clipboard content will be used")
            return None, None
            
        elif choice == "2" or choice == "4":
            # Get text content
            text_content = input("Enter clipboard text content: ").strip()
            if text_content:
                clipboard_text = text_content
                print(f"✅ Clipboard text set: {text_content[:50]}{'...' if len(text_content) > 50 else ''}")
        
        if choice == "3" or choice == "4":
            # Get image content
            print("\n🖼️ Image Options:")
            print("1. Use programmer.png (default test image)")
            print("2. Specify custom image path")
            
            img_choice = input("Select image option (1-2) or press Enter for default: ").strip()
            
            if not img_choice or img_choice == "1":
                # Use default programmer.png
                image_path = Path(__file__).parent / "sample_data" / "programmer.png"
                if image_path.exists():
                    try:
                        with open(image_path, "rb") as f:
                            clipboard_image = f.read()
                        print(f"✅ Image loaded: {image_path.name} ({len(clipboard_image)} bytes)")
                    except Exception as e:
                        print(f"❌ Failed to load image: {e}")
                else:
                    print(f"❌ Default image file not found: {image_path}")
                    
            elif img_choice == "2":
                # Get custom image path
                custom_path = input("Enter image file path: ").strip()
                if custom_path:
                    image_path = Path(custom_path)
                    if image_path.exists():
                        try:
                            with open(image_path, "rb") as f:
                                clipboard_image = f.read()
                            print(f"✅ Image loaded: {image_path.name} ({len(clipboard_image)} bytes)")
                        except Exception as e:
                            print(f"❌ Failed to load image: {e}")
                    else:
                        print(f"❌ Image file not found: {image_path}")
        
        return clipboard_text, clipboard_image
        
    except KeyboardInterrupt:
        print("\n⚠️ No clipboard content will be used")
        return None, None


def _select_processing_mode() -> str:
    """Allow user to select processing mode"""
    print("\n⚡ Processing Mode:")
    print("1. Standard processing")
    print("2. Streaming processing (if LLM enabled)")

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


def _handle_live_recording(pipeline: Pipeline) -> str | None:
    """Handle live audio recording"""
    print("\n🎙️ Live Recording Session")
    print("=" * 40)
    
    try:
        print("Press Enter to start recording...")
        input()
        
        print("🔴 Recording started! Speak now...")
        pipeline.start_recording()
        
        print("Press Enter to stop recording...")
        input()
        
        print("⏹️ Stopping recording...")
        audio_file_path = pipeline.stop_recording()
        
        print(f"✅ Recording saved to: {audio_file_path}")
        return audio_file_path
        
    except KeyboardInterrupt:
        print("\n⚠️ Recording cancelled by user")
        if pipeline.is_recording:
            pipeline.stop_recording()
        return None
    except Exception as e:
        print(f"❌ Recording error: {e}")
        if pipeline.is_recording:
            pipeline.stop_recording()
        return None


def test_pipeline() -> bool:
    """Main pipeline test with interactive configuration"""
    print("🧪 Pipeline - Interactive Test Suite")
    print("=" * 60)
    print("This test uses real OpenAI API and requires a valid API key.\n")

    try:
        # Create pipeline
        pipeline = _create_test_pipeline()
        if not pipeline:
            return False

        # Test basic properties
        print(f"\n📊 Pipeline State:")
        print(f"🎙️ Recording status: {'Recording' if pipeline.is_recording else 'Not recording'}")

        # Interactive configuration
        print("\n" + "=" * 60)
        print("🔧 Interactive Configuration")
        print("=" * 60)

        # Create instruction set
        instruction_set = _create_test_instruction_set()

        # Apply instruction set
        print(f"\n⚙️ Applying instruction set '{instruction_set.name}'...")
        pipeline.apply_instruction_set(instruction_set)
        print("✅ Instruction set applied successfully")

        # Get audio file or handle live recording
        audio_path = _get_test_audio_file()
        
        # Get clipboard content
        clipboard_text, clipboard_image = _get_clipboard_content()

        # Processing mode selection
        processing_mode = _select_processing_mode()

        # Summary of configuration
        print("\n" + "=" * 60)
        print("📋 Configuration Summary")
        print("=" * 60)
        print(f"🎯 Instruction Set: {instruction_set.name}")
        print(f"📝 STT Vocabulary: {instruction_set.stt_vocabulary or 'None'}")
        print(f"🎯 STT Instructions: {instruction_set.stt_instructions or 'None'}")
        print(f"🌍 Language: {instruction_set.stt_language or 'Auto-detection'}")
        print(f"🤖 LLM Enabled: {'Yes' if instruction_set.llm_enabled else 'No'}")
        if instruction_set.llm_enabled:
            print(f"🎯 LLM Instructions: {instruction_set.llm_instructions or 'None'}")
            print(f"🔍 MCP Servers: {instruction_set.llm_mcp_servers_json_str}")
        print(f"📋 Clipboard Text: {'Yes' if clipboard_text else 'No'}")
        print(f"🖼️ Clipboard Image: {'Yes' if clipboard_image else 'No'}")
        print(f"🔍 Web Search: {'Yes' if instruction_set.llm_web_search_enabled else 'No'}")
        print(f"⚡ Processing Mode: {processing_mode.capitalize()}")
        
        if audio_path.name == "live_recording":
            print(f"🎵 Audio Source: Live Recording")
        else:
            print(f"🎵 Audio File: {audio_path.name}")

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

        # Handle live recording if selected
        if audio_path.name == "live_recording":
            audio_file_path = _handle_live_recording(pipeline)
            if not audio_file_path:
                return False
        else:
            audio_file_path = str(audio_path)

        # Process the input
        print("\n" + "=" * 60)
        print("🔄 Processing Pipeline")
        print("=" * 60)

        start_time = time.time()

        if processing_mode == "streaming" and instruction_set.llm_enabled:
            print("Starting streaming processing...\n")
            print("-" * 60)

            def print_chunk(chunk: str) -> None:
                print(chunk, end="", flush=True)

            result = pipeline.process(
                audio_file_path=audio_file_path,
                clipboard_text=clipboard_text,
                clipboard_image=clipboard_image,
                stream_callback=print_chunk,
            )
            print("\n" + "-" * 60)

        else:
            print("Starting standard processing...")
            result = pipeline.process(
                audio_file_path=audio_file_path,
                clipboard_text=clipboard_text,
                clipboard_image=clipboard_image,
            )

        end_time = time.time()

        # Display results
        print("\n" + "=" * 60)
        print("📊 Processing Results")
        print("=" * 60)

        if result and result.stt_output:
            print(f"✅ Processing completed successfully!")
            print(f"⏱️ Processing time: {end_time - start_time:.2f} seconds")
            print(f"📊 STT length: {len(result.stt_output)} characters")
            print(f"📝 STT word count: {len(result.stt_output.split())} words")
            print(f"🤖 LLM processed: {'Yes' if result.is_llm_processed else 'No'}")
            
            if result.is_llm_processed and result.llm_output:
                print(f"📊 LLM length: {len(result.llm_output)} characters")
                print(f"📝 LLM word count: {len(result.llm_output.split())} words")

            print("\n" + "-" * 60)
            print("📄 STT Output:")
            print("-" * 60)
            print(result.stt_output.strip())
            print("-" * 60)

            if result.is_llm_processed and result.llm_output and processing_mode == "standard":
                print("\n" + "-" * 60)
                print("🤖 LLM Output:")
                print("-" * 60)
                print(result.llm_output.strip())
                print("-" * 60)

        else:
            print("❌ Empty or invalid result received")
            return False

        print("\n✅ Pipeline test completed successfully!")
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
        success = test_pipeline()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
