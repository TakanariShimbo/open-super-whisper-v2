#!/usr/bin/env python3
"""
Command-line test for AudioRecorder

This test verifies the functionality of the AudioRecorder class
from the new_core.recorder module.
"""

import os
import sys
import argparse
import time
import threading

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from new_core.recorder.audio_recorder import AudioRecorder


def test_list_devices():
    """
    List all available microphone devices without running a recording test
    
    Returns
    -------
    int
        Exit code (0 for success, 1 for failure)
    """
    print("Listing available microphone devices")
    
    try:
        # Check microphone availability
        is_mic_available = AudioRecorder.check_microphone_availability()
        print(f"Microphone availability: {is_mic_available}")
        
        # List available microphones
        devices = AudioRecorder.get_available_microphones()
        print(f"\nFound {len(devices)} microphone devices:")
        
        if len(devices) == 0:
            print("  No microphone devices found.")
            return 0
            
        for i, device in enumerate(devices):
            print(f"  {i+1}. {device['name']}")
            print(f"     Input channels: {device['max_input_channels']}")
            print(f"     Default sample rate: {device['default_samplerate']} Hz")
            
            # Display additional device information if available
            if 'hostapi' in device:
                print(f"     Host API: {device['hostapi']}")
            if 'index' in device:
                print(f"     Device index: {device['index']}")
                
            print()
            
        return 0
        
    except Exception as e:
        print(f"Error listing devices: {str(e)}")
        return 1


def test_recorder(duration: int = 5, sample_rate: int = 16000, channels: int = 1, check_devices: bool = False):
    """
    Test AudioRecorder functionality
    
    Parameters
    ----------
    duration : int, optional
        Recording duration in seconds, by default 5
    sample_rate : int, optional
        Sample rate for recording, by default 16000
    channels : int, optional
        Number of audio channels, by default 1
    check_devices : bool, optional
        Whether to check and list available microphone devices, by default False
    """
    print("Testing AudioRecorder")
    
    try:
        # First check microphone availability
        is_mic_available = AudioRecorder.check_microphone_availability()
        print(f"Microphone availability: {is_mic_available}")
        
        if not is_mic_available:
            print("Error: No microphones available for recording")
            return 1
        
        # If requested, list available microphones
        if check_devices:
            devices = AudioRecorder.get_available_microphones()
            print(f"\nFound {len(devices)} microphone devices:")
            
            for i, device in enumerate(devices):
                print(f"  {i+1}. {device['name']}")
                print(f"     Input channels: {device['max_input_channels']}")
                print(f"     Default sample rate: {device['default_samplerate']} Hz")
                print()
        
        # Initialize recorder
        recorder = AudioRecorder(sample_rate=sample_rate, channels=channels)
        
        print(f"\nInitialized recorder with settings:")
        print(f"  Sample Rate: {sample_rate} Hz")
        print(f"  Channels: {channels}")
        
        # Start recording
        print(f"\nStarting {duration} second test recording...")
        recorder.start_recording()
        
        # Check if recording is active
        if recorder.is_recording_active():
            print("Recording is now active!")
        else:
            print("Error: Recording failed to start")
            return 1
        
        # Wait for specified duration
        for i in range(duration):
            time.sleep(1)
            print(f"Recording... {i+1}/{duration} seconds", end="\r")
        
        print("\nStopping recording...")
        result_path = recorder.stop_recording()
        
        # Check result
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path) / 1024  # Size in KB
            print(f"Recording saved successfully:")
            print(f"  Path: {result_path}")
            print(f"  Size: {file_size:.2f} KB")
            print(f"  Located in temporary directory: {os.path.dirname(result_path)}")
            
            print("\nTesting completed successfully")
            return 0
        else:
            print(f"Error: Recording file not found or not created")
            return 1
            
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return 1


def test_recorder_with_threading(duration: int = 5, sample_rate: int = 16000, channels: int = 1):
    """
    Advanced test that demonstrates using AudioRecorder in a threaded environment
    
    Parameters
    ----------
    duration : int, optional
        Recording duration in seconds, by default 5
    sample_rate : int, optional
        Sample rate for recording, by default 16000
    channels : int, optional
        Number of audio channels, by default 1
    """
    print("Testing AudioRecorder with threading")
    
    stop_event = threading.Event()
    result_path = [None]  # Use list to store result from thread
    
    def recording_thread():
        try:
            recorder = AudioRecorder(sample_rate=sample_rate, channels=channels)
            print("Recording thread started")
            
            recorder.start_recording()
            print("Recording started")
            
            # Wait until signaled to stop
            while not stop_event.is_set():
                time.sleep(0.1)
            
            # Stop recording and get path
            path = recorder.stop_recording()
            result_path[0] = path
            print(f"Recording stopped, file saved to: {path}")
            
        except Exception as e:
            print(f"Error in recording thread: {e}")
    
    # Create and start thread
    thread = threading.Thread(target=recording_thread)
    thread.daemon = True
    thread.start()
    
    # Wait for specified duration
    for i in range(duration):
        time.sleep(1)
        print(f"Main thread: Recording in progress... {i+1}/{duration} seconds")
    
    # Signal thread to stop recording
    print("Main thread: Signaling to stop recording")
    stop_event.set()
    
    # Wait for thread to finish
    thread.join(timeout=5)
    
    # Check result
    path = result_path[0]
    if path and os.path.exists(path):
        file_size = os.path.getsize(path) / 1024  # Size in KB
        print(f"\nThreaded recording saved successfully:")
        print(f"  Path: {path}")
        print(f"  Size: {file_size:.2f} KB")
        print("\nThreading test completed successfully")
        return 0
    else:
        print("\nError: Threaded recording file not found or not created")
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test AudioRecorder functionality")
    
    parser.add_argument(
        "--duration", 
        type=int,
        default=5,
        help="Recording duration in seconds (default: 5)"
    )
    
    parser.add_argument(
        "--sample-rate", 
        type=int,
        default=16000,
        help="Sample rate for recording in Hz (default: 16000)"
    )
    
    parser.add_argument(
        "--channels", 
        type=int,
        default=1,
        help="Number of audio channels (default: 1)"
    )
    
    parser.add_argument(
        "--list-devices", 
        action="store_true",
        help="List available microphone devices"
    )
    
    parser.add_argument(
        "--threading-test", 
        action="store_true",
        help="Run advanced test with threading"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate test
    if args.list_devices and not args.threading_test:
        # Only list devices when --list-devices is specified alone
        result = test_list_devices()
    elif args.threading_test:
        result = test_recorder_with_threading(
            args.duration,
            args.sample_rate,
            args.channels
        )
    else:
        result = test_recorder(
            args.duration,
            args.sample_rate,
            args.channels,
            args.list_devices  # Still pass list_devices flag for regular test
        )
    
    # Return the result code
    sys.exit(result)
