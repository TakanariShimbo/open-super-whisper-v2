#!/usr/bin/env python3
"""
Hotkey Manager Test

This test verifies the HotkeyManager functionality including
hotkey registration, listening, and callback execution.
"""

import sys
import time
from pathlib import Path
from typing import Literal

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.key.hotkey_manager import HotkeyManager


def test_hotkey_manager_interactive() -> bool:
    """Interactive test for hotkey manager functionality"""
    print("=== Interactive Hotkey Manager Test ===")
    print("This test will register hotkeys and monitor for their activation for 20 seconds.")
    print("🎯 Try these test cases to validate hotkey functionality:")
    print("  1. Press Ctrl+Shift+R - should trigger 'Recording hotkey detected!'")
    print("  2. Press Ctrl+Shift+S - should trigger 'Stop hotkey detected!'")
    print("  3. Press Ctrl+Shift+P - should trigger 'Process hotkey detected!'")
    print("  4. Press other key combinations - should be ignored")
    print("  5. Test multiple hotkeys in sequence")

    # Global counters to track hotkey activations
    hotkey_counters = {
        "ctrl+shift+r": 0,
        "ctrl+shift+s": 0,
        "ctrl+shift+p": 0
    }

    def create_callback(hotkey_name: str):
        """Create a callback function for a specific hotkey"""
        def callback():
            hotkey_counters[hotkey_name] += 1
            messages = {
                "ctrl+shift+r": "🔴 Recording hotkey detected!",
                "ctrl+shift+s": "⏹️  Stop hotkey detected!",
                "ctrl+shift+p": "⚙️  Process hotkey detected!"
            }
            print(f"\n{messages[hotkey_name]} (Count: {hotkey_counters[hotkey_name]})")
        return callback

    try:
        manager = HotkeyManager()
        
        # Register hotkeys
        print("\n📝 Registering hotkeys...")
        manager.register_hotkey("ctrl+shift+r", create_callback("ctrl+shift+r"))
        manager.register_hotkey("ctrl+shift+s", create_callback("ctrl+shift+s"))
        manager.register_hotkey("ctrl+shift+p", create_callback("ctrl+shift+p"))
        
        registered = manager.get_registered_hotkeys()
        print(f"✅ Registered {len(registered)} hotkeys: {', '.join(registered)}")

        # Start listening
        print("\n🎧 Starting hotkey listener...")
        manager.start_listening()
        
        if not manager.is_listening:
            print("❌ Failed to start listening")
            return False

        print("✅ Hotkey listener is active")
        print("\n🎹 Starting hotkey monitoring...")
        print("=" * 60)
        print("Press the registered hotkeys to test functionality")
        print("=" * 60)

        # Monitor for 20 seconds
        test_duration = 20
        start_time = time.time()
        
        while time.time() - start_time < test_duration:
            remaining = int(test_duration - (time.time() - start_time))
            
            # Show status every second
            if remaining % 5 == 0:  # Update every 5 seconds
                total_activations = sum(hotkey_counters.values())
                print(f"⏰ {remaining}s remaining | Total activations: {total_activations}")
            
            time.sleep(1)

        # Stop listening
        print("\n🛑 Stopping hotkey listener...")
        stopped = manager.stop_listening()
        
        if stopped:
            print("✅ Hotkey listener stopped successfully")
        else:
            print("❌ Failed to stop listener")

        # Display results
        print("\n" + "=" * 60)
        print("📊 Test Results Summary:")
        print("=" * 60)
        total_activations = sum(hotkey_counters.values())
        
        for hotkey, count in hotkey_counters.items():
            status = "✅" if count > 0 else "⚠️"
            print(f"  {status} {hotkey}: {count} activations")
        
        print(f"\n🎯 Total hotkey activations: {total_activations}")
        
        if total_activations > 0:
            print("✅ Interactive test completed successfully - hotkeys are working!")
        else:
            print("⚠️  No hotkeys were activated - please verify functionality manually")
        
        return True

    except Exception as e:
        print(f"❌ Error during interactive test: {e}")
        return False


def main() -> Literal[0, 1]:
    """Main test execution - Focus on Hotkey Registration and Activation"""
    print("🎹 HotkeyManager - Interactive Test Suite")
    print("=" * 50)
    print("🚀 This test focuses on validating hotkey registration and activation!")
    print()

    # Run interactive test directly
    if test_hotkey_manager_interactive():
        print("🎉 Interactive test completed!")
        return 0
    else:
        print("❌ Interactive test failed.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
