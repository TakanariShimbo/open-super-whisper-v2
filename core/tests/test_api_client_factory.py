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

from core.api.api_client_factory import APIClientFactory


def test_api_key_input() -> bool:
    """Test API key input and validation"""
    print("🔑 API Client Factory Test")
    print("=" * 40)

    try:
        # Get API key from user
        api_key = input("Enter your API key: ").strip()

        if not api_key:
            print("❌ Empty API key provided")
            return False

        print(f"Testing API key: {api_key[:10]}...")

        # Test client creation
        is_successful, client = APIClientFactory.create_client(api_key)

        if is_successful:
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

    test_api_key_input()

    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
