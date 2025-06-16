#!/usr/bin/env python3
"""
API Client Factory Test

This test verifies the API client factory functionality with user input.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.api.api_key_checker import APIKeyChecker


def test_openai_api_key_input() -> bool:
    """Test OpenAI API key input and validation"""
    print("🔑 OpenAI API Key Test")
    print("=" * 40)

    try:
        # Get API key from user
        openai_api_key = input("Enter your OpenAI API key: ").strip()

        if not openai_api_key:
            print("❌ Empty API key provided")
            return False

        print(f"Testing API key: {openai_api_key[:10]}...")

        # Test client creation
        is_valid = APIKeyChecker.check_openai_api_key(openai_api_key=openai_api_key)

        if is_valid:
            print("✅ API key is valid! Client created successfully.")
            return True
        else:
            print("❌ API key is invalid. Client creation failed.")
            return False

    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False


def test_anthropic_api_key_input() -> bool:
    """Test Anthropic API key input and validation"""
    print("🔑 Anthropic API Key Test")
    print("=" * 40)

    try:
        # Get API key from user
        anthropic_api_key = input("Enter your Anthropic API key: ").strip()

        if not anthropic_api_key:
            print("❌ Empty API key provided")
            return False

        print(f"Testing API key: {anthropic_api_key[:10]}...")

        # Test client creation
        is_valid = APIKeyChecker.check_anthropic_api_key(anthropic_api_key=anthropic_api_key)

        if is_valid:
            print("✅ API key is valid! Client created successfully.")
            return True
        else:
            print("❌ API key is invalid. Client creation failed.")
            return False

    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False


def test_gemini_api_key_input() -> bool:
    """Test Gemini API key input and validation"""
    print("🔑 Gemini API Key Test")
    print("=" * 40)

    try:
        # Get API key from user
        gemini_api_key = input("Enter your Gemini API key: ").strip()

        if not gemini_api_key:
            print("❌ Empty API key provided")
            return False

        print(f"Testing API key: {gemini_api_key[:10]}...")

        # Test client creation
        is_valid = APIKeyChecker.check_gemini_api_key(gemini_api_key=gemini_api_key)

        if is_valid:
            print("✅ API key is valid! Client created successfully.")
            return True
        else:
            print("❌ API key is invalid. Client creation failed.")
            return False

    except KeyboardInterrupt:
        print("\n⚠️ Test cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False


def main() -> None:
    """Main test execution"""
    print("Testing API Client Factory with user input")
    print("Press Ctrl+C to cancel\n")

    # Test all available APIs
    print("Choose which API to test:")
    print("1. OpenAI")
    print("2. Anthropic (Claude)")
    print("3. Gemini")
    print("4. All APIs")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        test_openai_api_key_input()
    elif choice == "2":
        test_anthropic_api_key_input()
    elif choice == "3":
        test_gemini_api_key_input()
    elif choice == "4":
        print("Testing all APIs...\n")
        test_openai_api_key_input()
        print()
        test_anthropic_api_key_input()
        print()
        test_gemini_api_key_input()
    else:
        print("Invalid choice. Defaulting to OpenAI test.")
        test_openai_api_key_input()

    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
