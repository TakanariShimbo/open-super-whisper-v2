#!/usr/bin/env python3
"""
Key State Tracker Test

This test verifies the KeyStateTracker functionality including
simultaneous monitoring of current keys and last keys.
"""

import sys
import time
from pathlib import Path
from typing import Literal

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.key.key_state_tracker import KeyStateTracker


def test_key_detection_interactive() -> bool:
    """Interactive test for key detection with current and last key monitoring"""
    print("=== Interactive Key Detection Test ===")
    print("This test will monitor your keyboard input for 15 seconds.")
    print("🎯 Try these test cases to validate current/last key functionality:")
    print("  1. Press a single key (e.g., 'a') - observe current vs last")
    print("  2. Press Ctrl+Alt+1 combination - observe current vs last")
    print("  3. Release all keys - observe that current becomes empty but last remains")
    print("  4. Press a different key - observe last keys update to new combination")
    print("  5. Hold multiple keys simultaneously - observe both current and last")
    print("  6. Press and hold Ctrl, then add Alt - watch last keys update")
    print("  7. Release Ctrl but keep Alt - current should show 'alt', last should show 'ctrl+alt'")

    try:
        tracker = KeyStateTracker()
        tracker.start_monitoring()

        if not tracker.is_monitoring:
            print("❌ Failed to start monitoring")
            return False

        print("\n🎹 Starting key monitoring...")
        print("=" * 60)
        print(f"{'Current Keys':<25} | {'Last Keys':<25} | Status")
        print("=" * 60)

        # Monitor for 15 seconds
        test_duration = 15
        start_time = time.time()
        last_output = ""
        status_messages = {0: "Waiting for input...", 1: "Key detected!", 2: "Combination detected!", 3: "Keys released", 4: "New combination!"}

        while time.time() - start_time < test_duration:
            current_keys = tracker.get_current_keys()
            last_keys = tracker.get_last_keys()

            current_str = "+".join(current_keys) if current_keys else "<none>"
            last_str = "+".join(last_keys) if last_keys else "<none>"

            # Determine status
            status = 0  # waiting
            if current_keys and last_keys:
                if len(current_keys) > 1:
                    status = 2  # combination detected
                else:
                    status = 1  # key detected
            elif not current_keys and last_keys:
                status = 3  # keys released
            elif current_keys and not last_keys:
                status = 1  # first key detected

            remaining = int(test_duration - (time.time() - start_time))
            output = f"{current_str:<25} | {last_str:<25} | {status_messages[status]} ({remaining}s)"

            # Only print when output changes to reduce spam
            if output != last_output:
                print(f"\r{' ' * 80}", end="\r")  # Clear line
                print(output, flush=True)
                last_output = output

            time.sleep(0.1)  # Update 10 times per second

        # Stop monitoring
        tracker.stop_monitoring()

        print("\n" + "=" * 60)
        print("✅ Interactive test completed successfully")
        return True

    except Exception as e:
        print(f"❌ Error during interactive test: {e}")
        return False


def main() -> Literal[0, 1]:
    """Main test execution - Focus on Current/Last Key Tracking"""
    print("🎹 KeyStateTracker - Interactive Test Suite")
    print("=" * 50)
    print("🚀 This test focuses on validating current/last key simultaneous tracking!")
    print()

    # Run interactive test directly
    if test_key_detection_interactive():
        print("🎉 Interactive test completed!")
        return 0
    else:
        print("❌ Interactive test failed.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
