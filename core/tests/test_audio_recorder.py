#!/usr/bin/env python3
"""
AudioRecorder Test

This test verifies the main AudioRecorder functionality.
"""

import os
import sys
import time
import argparse
from typing import Literal
from pathlib import Path

import sounddevice as sd
import soundfile as sf

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.recorder.audio_recorder import AudioRecorder


def test_microphone_availability() -> bool:
    """Test microphone availability"""
    print("=== Microphone Availability Check ===")

    is_available = AudioRecorder.check_microphone_availability()
    print(f"Microphone available: {is_available}")

    if not is_available:
        print("❌ No microphone available. Skipping test.")
        return False

    devices = AudioRecorder.get_available_microphones()
    print(f"Available microphones: {len(devices)}")

    if devices:
        print("Available microphones:")
        for i, device in enumerate(devices[:3]):  # Show first 3 only
            print(f"  {i+1}. {device['name']}")

    print("✅ Microphone availability check completed\n")
    return True


def test_recording_basic() -> None | str:
    """Test basic recording functionality"""
    print("=== Basic Recording Test ===")

    try:
        recorder = AudioRecorder()
        duration = 3  # Record for 3 seconds

        print(f"Starting recording ({duration} seconds)...")
        recorder.start_recording()

        # Check recording status
        if not recorder.is_recording:
            print("❌ Recording failed to start")
            return None

        print("🎤 Recording...")
        for i in range(duration):
            time.sleep(1)
            print(f"  {i+1}/{duration} seconds")

        print("Stopping recording...")
        file_path = recorder.stop_recording()

        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ Recording completed")
            print(f"  File: {file_path}")
            print(f"  Size: {file_size} bytes")
            return file_path
        else:
            print("❌ Recording file was not created")
            return None

    except Exception as e:
        print(f"❌ Error during recording: {e}")
        return None


def test_audio_playback(file_path) -> bool:
    """Playback recorded audio"""
    print("\n=== Audio Playback Test ===")

    if not file_path or not os.path.exists(file_path):
        print("❌ No file available for playback")
        return False

    try:
        # Load audio file
        data, samplerate = sf.read(file_path)
        duration = len(data) / samplerate

        print(f"Audio file info:")
        print(f"  Sample rate: {samplerate} Hz")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Data size: {len(data)}")

        print("🔊 Playing audio...")
        sd.play(data, samplerate)

        # Wait for playback to complete
        time.sleep(duration + 0.5)
        sd.wait()  # Wait for playback completion

        print("✅ Audio playback completed")
        return True

    except Exception as e:
        print(f"❌ Error during audio playback: {e}")
        return False


def test_error_handling() -> bool:
    """Basic error handling test"""
    print("\n=== Error Handling Test ===")

    try:
        recorder = AudioRecorder()

        # Try to stop recording when not recording
        result = recorder.stop_recording()
        if result is None:
            print("✅ Correctly handled stop request when not recording")
        else:
            print("❌ Stop request succeeded when not recording")
            return False

        # Test duplicate recording start
        if AudioRecorder.check_microphone_availability():
            recorder.start_recording()
            try:
                recorder.start_recording()  # Duplicate start
                print("❌ Duplicate recording start was allowed")
                recorder.stop_recording()
                return False
            except RuntimeError:
                print("✅ Correctly rejected duplicate recording start")
                recorder.stop_recording()

        return True

    except Exception as e:
        print(f"❌ Error during error handling test: {e}")
        return False


def cleanup_test_file(file_path) -> None:
    """Clean up test file"""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"🗑️  Deleted test file: {file_path}")
        except Exception as e:
            print(f"⚠️  Failed to delete test file: {e}")


def run_mic_test() -> Literal[0, 1]:
    """Run microphone availability test only"""
    print("🎵 AudioRecorder - Microphone Test")
    print("=" * 50)

    success = test_microphone_availability()
    return 0 if success else 1


def run_recording_and_playback_test() -> Literal[0, 1]:
    """Run recording + playback test"""
    print("🎵 AudioRecorder - Playback Test")
    print("=" * 50)

    if not test_microphone_availability():
        print("No microphone available, ending test.")
        return 1

    recorded_file = test_recording_basic()
    if not recorded_file:
        print("Recording failed, cannot test playback.")
        return 1

    playback_success = test_audio_playback(recorded_file)
    cleanup_test_file(recorded_file)

    return 0 if playback_success else 1


def run_error_test() -> Literal[0, 1]:
    """Run error handling test only"""
    print("🎵 AudioRecorder - Error Handling Test")
    print("=" * 50)

    success = test_error_handling()
    return 0 if success else 1


def run_all_tests() -> Literal[0, 1]:
    """Run all tests (original behavior)"""
    print("🎵 AudioRecorder - All Tests")
    print("=" * 50)

    # Check microphone availability
    if not test_microphone_availability():
        print("No microphone available, ending test.")
        return 1

    # Basic recording test
    recorded_file = test_recording_basic()
    if not recorded_file:
        print("Recording test failed, ending test.")
        return 1

    # Audio playback test
    playback_success = test_audio_playback(recorded_file)

    # Error handling test
    error_handling_success = test_error_handling()

    # Cleanup
    cleanup_test_file(recorded_file)

    # Results summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"  Recording test: {'✅ Success' if recorded_file else '❌ Failed'}")
    print(f"  Playback test: {'✅ Success' if playback_success else '❌ Failed'}")
    print(f"  Error handling: {'✅ Success' if error_handling_success else '❌ Failed'}")

    if recorded_file and playback_success and error_handling_success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1


def main() -> Literal[0, 1]:
    """Main test execution with argument parsing"""
    parser = argparse.ArgumentParser(
        description="AudioRecorder Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            %(prog)s                    # Run all tests
            %(prog)s --mic              # Test microphone availability only
            %(prog)s --recording         # Test recording + playback
            %(prog)s --error            # Test error handling only
        """,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--mic", action="store_true", help="Test microphone availability only")
    group.add_argument("--recording", action="store_true", help="Test recording + playback functionality")
    group.add_argument("--error", action="store_true", help="Test error handling only")
    group.add_argument("--all", action="store_true", help="Run all tests (default behavior)")

    args = parser.parse_args()

    # Determine which test to run
    if args.mic:
        return run_mic_test()
    elif args.recording:
        return run_recording_and_playback_test()
    elif args.error:
        return run_error_test()
    else:
        # Default behavior: run all tests
        return run_all_tests()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
