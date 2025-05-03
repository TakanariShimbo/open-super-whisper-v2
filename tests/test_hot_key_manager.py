#!/usr/bin/env python3
"""
Command-line test for HotKeyManager

This test verifies the functionality of the HotKeyManager class
from the core.ui module.
"""

import os
import sys
import argparse
import time
import threading

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ui.hot_key_manager import HotKeyManager


def test_callback(shortcut_name: str):
    """
    Test callback function for hotkey events
    
    Parameters
    ----------
    shortcut_name : str
        Name of the triggered shortcut
    """
    print(f"Hotkey triggered: {shortcut_name}")


def test_hot_key_manager(test_duration: int = 10, verbose: bool = False):
    """
    Test HotKeyManager functionality
    
    Parameters
    ----------
    test_duration : int, optional
        Duration to run the test in seconds, by default 10
    verbose : bool, optional
        Whether to output verbose logging, by default False
    """
    print("Testing HotKeyManager")
    
    try:
        # Initialize hot key manager
        manager = HotKeyManager()
        print("Initialized HotKeyManager")
        
        # Store hotkey names for reference
        hotkey_names = {}
        
        # Register some test hotkeys
        test_hotkeys = [
            ("ctrl+shift+d", "Debug Mode"),
            ("ctrl+alt+r", "Record Audio"),
            ("ctrl+alt+p", "Process Audio"),
            ("ctrl+alt+s", "Stop Recording")
        ]
        
        for shortcut, name in test_hotkeys:
            # Create a callback that closes over the hotkey name
            callback = lambda n=name: test_callback(n)
            
            try:
                # Register the hotkey
                manager.register_hotkey(shortcut, callback)
                
                # Store the name for display purposes
                hotkey_names[shortcut] = name
                print(f"Registered hotkey: {shortcut} -> {name}")
            except Exception as e:
                print(f"Failed to register hotkey: {shortcut} - Error: {e}")
        
        # Start listening
        print("\nStarting hotkey listener thread...")
        listener_thread = threading.Thread(target=manager.start_listening)
        listener_thread.daemon = True
        listener_thread.start()
        
        # Print active hotkeys
        print(f"\nActive hotkeys ({len(hotkey_names)}):")
        for shortcut, name in hotkey_names.items():
            print(f"  {shortcut}: {name}")
        
        # Instruct user
        print("\nTest running for", test_duration, "seconds.")
        print("You can press the registered hotkeys to test functionality.")
        print("Press the key combinations shown above to trigger callbacks.")
        
        # Wait for specified duration
        if verbose:
            for i in range(test_duration):
                time.sleep(1)
                print(f"Testing... {i+1}/{test_duration} seconds", end="\r")
            print("\nTest duration completed.")
        else:
            time.sleep(test_duration)

        # Stop the listener
        print("Stopping hotkey listener...")
        manager.stop_listening()
                
        # Wait for thread to complete
        listener_thread.join(timeout=2)
        
        print("\nTesting completed successfully")
        return 0
            
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test HotKeyManager functionality")
    
    parser.add_argument(
        "--duration", 
        type=int,
        default=10,
        help="Duration to run the test in seconds (default: 10)"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_hot_key_manager(args.duration, args.verbose)
    
    # Return the result code
    sys.exit(result)
