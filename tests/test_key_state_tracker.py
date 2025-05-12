#!/usr/bin/env python3
"""
Command-line test for KeyStateTracker

This test verifies the functionality of the KeyStateTracker class
from the core.key module, with a focus on the get_last_keys_str method.
"""

import os
import sys
import argparse
import time
import threading

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.key.key_state_tracker import KeyStateTracker


def test_key_state_tracker(test_duration: int = 15, verbose: bool = False):
    """
    Test KeyStateTracker functionality
    
    Parameters
    ----------
    test_duration : int, optional
        Duration to run the test in seconds, by default 15
    verbose : bool, optional
        Whether to output verbose logging, by default False
    """
    print("Testing KeyStateTracker")
    
    try:
        # Initialize key state tracker
        tracker = KeyStateTracker()
        print("Initialized KeyStateTracker")
        
        # Start monitoring
        tracker.start()
        print("Started key monitoring")
        
        # Function to run in a separate thread to continuously print key states
        def monitor_keys():
            try:
                last_output = ""
                while tracker.is_monitoring:
                    current_keys = tracker.get_current_keys_str()
                    last_keys = tracker.get_last_keys_str()
                    
                    output = f"Current keys: {current_keys or '<none>'} | Last keys: {last_keys or '<none>'}"
                    
                    # Only print if the output changed to reduce console spam
                    if output != last_output:
                        print("\r" + " " * len(last_output), end="\r")  # Clear previous output
                        print(output, end="", flush=True)
                        last_output = output
                        
                    time.sleep(0.1)  # Update at 10 times per second
            except Exception as e:
                print(f"\nError in monitor thread: {e}")
        
        # Start the monitoring thread
        print("\nStarting key monitoring thread...")
        monitor_thread = threading.Thread(target=monitor_keys)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Instruct user
        print("\nTest running for", test_duration, "seconds.")
        print("Press key combinations and observe the difference between current and last keys.")
        print("Try these test cases:")
        print("  1. Press Ctrl+Shift+R, then release all keys - last keys should still show 'ctrl+shift+r'")
        print("  2. Press a key not in the last combo - last keys should update to the new key")
        print("  3. Press Alt, then Shift (while holding Alt) - both should be in current and last keys")
        print("  4. Release Alt but keep Shift pressed - current should show only 'shift', last should show 'alt+shift'")
        print("\nMonitoring keys...")
        
        # Wait for specified duration
        if verbose:
            for i in range(test_duration):
                time.sleep(1)
                remaining = test_duration - i - 1
                print(f"\nRemaining time: {remaining} seconds", end="\r")
        else:
            time.sleep(test_duration)
        
        # Stop key monitoring
        print("\n\nStopping key monitoring...")
        tracker.stop()
        
        # Wait for thread to complete
        monitor_thread.join(timeout=2)
        
        print("\nTesting completed successfully")
        return 0
            
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test KeyStateTracker functionality")
    
    parser.add_argument(
        "--duration", 
        type=int,
        default=15,
        help="Duration to run the test in seconds (default: 15)"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_key_state_tracker(args.duration, args.verbose)
    
    # Return the result code
    sys.exit(result)
