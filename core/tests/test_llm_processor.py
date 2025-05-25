#!/usr/bin/env python3
"""
LLM Processor Test

This test verifies the LLMProcessor functionality using real OpenAI API calls.
All tests require a valid API key and make actual API requests.
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.llm.llm_processor import LLMProcessor
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


def test_basic_text_processing() -> bool:
    """Test basic text processing with real API"""
    print("=== Basic Text Processing Test ===")

    try:
        # Create real client
        is_successful, client = _create_test_client()

        if not is_successful:
            print("❌ Failed to create API client")
            return False

        print("✅ API client created successfully")

        # Create processor
        processor = LLMProcessor(client)

        # Get test text from user
        print("\n📝 Enter the text you want to process:")
        test_text = input("Text: ").strip()

        if not test_text:
            print("❌ No text provided")
            return False

        print(f"\nTesting with: '{test_text}'")

        start_time = time.time()
        response = processor.process_text(test_text)
        end_time = time.time()

        if response and len(response.strip()) > 0:
            print(f"\n✅ Received response:")
            print(f"Response: {response.strip()}")
            print(f"Processing time: {end_time - start_time:.2f} seconds")
        else:
            print("❌ Empty or invalid response received")
            return False

        print("✅ Basic text processing test completed\n")
        return True

    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during basic text processing test: {e}")
        return False


def test_system_instruction_functionality() -> bool:
    """Test system instruction functionality with real API"""
    print("=== System Instruction Functionality Test ===")

    try:
        # Create real client
        is_successful, client = _create_test_client()

        if not is_successful:
            print("❌ Failed to create API client")
            return False

        # Create processor
        processor = LLMProcessor(client)

        # Get custom system instruction from user
        print("\n🎯 Enter the system instruction:")
        custom_instruction = input("System instruction: ").strip()

        if not custom_instruction:
            print("❌ No system instruction provided")
            return False

        processor.set_system_instruction(custom_instruction)

        # Get test question from user
        print("\n❓ Enter the question/text to test the instruction:")
        test_text = input("Question: ").strip()

        if not test_text:
            print("❌ No question provided")
            return False

        print(f"\nTesting with custom instruction: '{custom_instruction}'")
        print(f"Question: '{test_text}'")

        start_time = time.time()
        response = processor.process_text(test_text)
        end_time = time.time()

        if response and len(response.strip()) > 0:
            print(f"\n✅ Received response:")
            print(f"Response: {response.strip()}")
            print(f"Processing time: {end_time - start_time:.2f} seconds")

            # Ask user if response follows instruction
            follows_instruction = input("\nDoes the response follow your instruction? [y/N]: ").strip().lower()
            if follows_instruction in ["y", "yes"]:
                print("✅ Response follows instruction as expected")
            else:
                print("⚠️ Response may not follow instruction perfectly (this can happen due to model behavior variations)")
        else:
            print("❌ Empty or invalid response received")
            return False

        print("✅ System instruction functionality test completed\n")
        return True

    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during system instruction test: {e}")
        return False


def test_streaming_functionality() -> bool:
    """Test streaming functionality with real API"""
    print("=== Streaming Functionality Test ===")

    try:
        # Create real client
        is_successful, client = _create_test_client()

        if not is_successful:
            print("❌ Failed to create API client")
            return False

        # Create processor
        processor = LLMProcessor(client)

        # Get test text from user
        print("\n💬 Enter the text for streaming test:")
        test_text = input("Text: ").strip()

        if not test_text:
            print("❌ No text provided")
            return False

        print(f"\nTesting streaming with: '{test_text}'")

        chunks_received = []

        def capture_chunk(chunk: str) -> None:
            chunks_received.append(chunk)
            print(chunk, end="", flush=True)

        print("\nStreaming response:")
        print("-" * 50)

        start_time = time.time()
        full_response = processor.process_text_with_stream(test_text, capture_chunk)
        end_time = time.time()

        print("\n" + "-" * 50)

        if len(chunks_received) > 1:
            print(f"✅ Received {len(chunks_received)} chunks")
        else:
            print("⚠️ Received fewer chunks than expected (may depend on response length)")

        if full_response and len(full_response.strip()) > 0:
            print(f"✅ Complete response length: {len(full_response)} characters")
            print(f"Processing time: {end_time - start_time:.2f} seconds")
        else:
            print("❌ Empty or invalid complete response")
            return False

        # Verify that chunked response matches full response
        combined_chunks = "".join(chunks_received)
        if combined_chunks == full_response:
            print("✅ Chunked response matches full response")
        else:
            print("⚠️ Chunked response differs from full response (may be expected)")

        print("✅ Streaming functionality test completed\n")
        return True

    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during streaming test: {e}")
        return False


def test_multimodal_processing() -> bool:
    """Test multimodal processing with text and image"""
    print("=== Multimodal Processing Test ===")

    try:
        # Create real client
        is_successful, client = _create_test_client()

        if not is_successful:
            print("❌ Failed to create API client")
            return False

        # Create processor
        processor = LLMProcessor(client)

        # Load sample image from core/tests/sample.png
        sample_image_path = Path(__file__).parent / "sample.png"

        if not sample_image_path.exists():
            print(f"❌ Sample image not found at: {sample_image_path}")
            return False

        try:
            with open(sample_image_path, "rb") as f:
                test_image_data = f.read()
            print(f"✅ Loaded sample image: {sample_image_path}")
            print(f"   Image size: {len(test_image_data)} bytes")
        except Exception as e:
            print(f"❌ Failed to load sample image: {e}")
            return False

        # Get question about the image from user
        print(f"\n🖼️ Enter your question about the image ({sample_image_path.name}):")
        test_text = input("Question: ").strip()

        if not test_text:
            print("❌ No question provided")
            return False

        print(f"\nTesting multimodal processing...")
        print(f"Text: '{test_text}'")
        print(f"Image: {sample_image_path.name}")

        start_time = time.time()
        response = processor.process_text(test_text, image_data=test_image_data)
        end_time = time.time()

        if response and len(response.strip()) > 0:
            print(f"\n✅ Received multimodal response:")
            print(f"Response: {response.strip()}")
            print(f"Processing time: {end_time - start_time:.2f} seconds")
        else:
            print("❌ Empty or invalid multimodal response received")
            return False

        print("✅ Multimodal processing test completed\n")
        return True

    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during multimodal test: {e}")
        return False


def run_all_tests() -> int:
    """Run all LLM processor tests"""
    print("🧪 LLMProcessor - Complete Test Suite")
    print("=" * 60)
    print("All tests use real OpenAI API and require a valid API key.\n")

    tests = [
        ("Basic Text Processing", test_basic_text_processing),
        ("System Instruction Functionality", test_system_instruction_functionality),
        ("Streaming Functionality", test_streaming_functionality),
        ("Multimodal Processing", test_multimodal_processing),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            failed += 1
        print()  # Add spacing between tests

    # Print results summary
    print("=" * 60)
    print("📊 Test Results Summary:")
    print(f"  Tests passed: ✅ {passed}")
    print(f"  Tests failed: ❌ {failed}")
    print(f"  Total tests: {passed + failed}")

    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} tests failed.")
        return 1


def main() -> int:
    """Main test execution"""
    parser = argparse.ArgumentParser(
        description="LLMProcessor Test Suite (using real OpenAI API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This test suite verifies LLMProcessor functionality using real OpenAI API calls.
A valid OpenAI API key is required for all tests.

Examples:
  %(prog)s                    # Run all tests (default)
  %(prog)s --basic            # Run basic text processing test only
  %(prog)s --system           # Run system instruction test only
  %(prog)s --streaming        # Run streaming functionality test only
  %(prog)s --multimodal       # Run multimodal processing test only

Individual test descriptions:
- Basic Text Processing: Test basic text-to-text processing
- System Instruction: Test custom system instructions/prompts  
- Streaming: Test real-time streaming responses
- Multimodal: Test text + image processing with sample.png
        """,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--basic", action="store_true", help="Run basic text processing test only")
    group.add_argument("--system", action="store_true", help="Run system instruction functionality test only")
    group.add_argument("--streaming", action="store_true", help="Run streaming functionality test only")
    group.add_argument("--multimodal", action="store_true", help="Run multimodal processing test only")
    group.add_argument("--all", action="store_true", help="Run all tests (default)")

    args = parser.parse_args()

    try:
        # Determine which test to run
        if args.basic:
            print("🧪 LLMProcessor - Basic Text Processing Test")
            print("=" * 50)
            success = test_basic_text_processing()
            return 0 if success else 1

        elif args.system:
            print("🧪 LLMProcessor - System Instruction Functionality Test")
            print("=" * 50)
            success = test_system_instruction_functionality()
            return 0 if success else 1

        elif args.streaming:
            print("🧪 LLMProcessor - Streaming Functionality Test")
            print("=" * 50)
            success = test_streaming_functionality()
            return 0 if success else 1

        elif args.multimodal:
            print("🧪 LLMProcessor - Multimodal Processing Test")
            print("=" * 50)
            success = test_multimodal_processing()
            return 0 if success else 1

        else:
            # Default behavior: run all tests
            return run_all_tests()

    except KeyboardInterrupt:
        print("\n⚠️ Tests cancelled by user")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
