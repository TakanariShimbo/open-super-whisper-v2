#!/usr/bin/env python3
"""
Command-line test for InstructionManager

This test verifies the functionality of the InstructionManager class
from the core.utils module.
"""

import os
import sys
import argparse
import json
import tempfile

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipelines.instruction_manager import InstructionSetsManager
from core.pipelines.instruction_set import InstructionSet


def test_instruction_manager(use_temp_file: bool = True, file_path: str = None, verbose: bool = False):
    """
    Test InstructionManager functionality
    
    Parameters
    ----------
    use_temp_file : bool, optional
        Whether to use a temporary file for testing, by default True
    file_path : str, optional
        Path to a file to use for saving/loading, by default None
    verbose : bool, optional
        Whether to output detailed instruction information, by default False
    """
    print("Testing InstructionManager creation and methods")
    
    # Create a temporary file if requested
    temp_file = None
    if use_temp_file:
        temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        file_path = temp_file.name
        temp_file.close()
        print(f"Created temporary config file: {file_path}")
    
    try:
        # Initialize manager (no config path parameter in constructor)
        manager = InstructionSetsManager()
        print("Initialized InstructionManager")
        
        # Check initial instruction sets
        sets = manager.get_all_sets()
        print(f"Found {len(sets)} initial instruction sets")
        
        if verbose and sets:
            print("Initial instruction sets:")
            for i, s in enumerate(sets):
                print(f"  {i+1}. {s.name}")
        
        # Create and add test instruction sets
        test_sets = [
            InstructionSet(
                name="Meeting Notes",
                stt_instructions="Transcribe accurately with speaker attribution.",
                llm_instructions="Summarize the key points from the meeting."
            ),
            InstructionSet(
                name="Code Analysis",
                stt_instructions="Transcribe accurately, preserving technical terminology.",
                llm_instructions="Analyze the code being discussed and suggest improvements."
            ),
            InstructionSet(
                name="Interview Helper",
                stt_instructions="Transcribe accurately with speaker attribution.",
                llm_instructions="Analyze the interview for key qualifications and areas of concern."
            )
        ]
        
        print(f"\nAdding {len(test_sets)} test instruction sets")
        for instruction_set in test_sets:
            success = manager.add_set(instruction_set)
            print(f"  Added: {instruction_set.name} (Success: {success})")
        
        # Save to config file if specified
        if file_path:
            # Export the configuration to dict
            config_data = manager.export_to_dict()
            
            # Manually save to file
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print(f"Saved instruction sets to file: {file_path}")
            
            # Check file content
            file_size = os.path.getsize(file_path)
            print(f"Config file size: {file_size} bytes")
            
            if verbose:
                with open(file_path, 'r') as f:
                    file_content = json.load(f)
                print("Config file content:")
                print(json.dumps(file_content, indent=2))
        
        # Test operations on instruction sets
        test_name = test_sets[0].name
        
        # Check if set exists using direct dictionary access
        found_set = manager.sets.get(test_name)
        
        if found_set:
            print(f"\nSuccessfully retrieved instruction set with name '{test_name}':")
            print(f"  Name: {found_set.name}")
            if verbose:
                print(f"  STT Instructions: '{found_set.stt_instructions}'")
                print(f"  LLM Instructions: '{found_set.llm_instructions}'")
        else:
            print(f"\nFailed to retrieve instruction set with name '{test_name}'")
        
        # Test removing an instruction set
        success = manager.delete_set(test_name)
        print(f"\nRemoved instruction set with name '{test_name}': {success}")
        
        # Verify it was removed
        remaining_sets = manager.get_all_sets()
        print(f"Remaining instruction sets: {len(remaining_sets)}")
        
        # Test loading from file
        if file_path:
            print("\nTesting loading from file")
            
            # Create a new manager instance
            new_manager = InstructionSetsManager()
            
            # Manually load from file
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Import the data
            new_manager.import_from_dict(config_data)
            
            loaded_sets = new_manager.get_all_sets()
            print(f"Loaded {len(loaded_sets)} instruction sets from file")
            
            if verbose and loaded_sets:
                print("Loaded instruction sets:")
                for i, s in enumerate(loaded_sets):
                    print(f"  {i+1}. {s.name}")
        
        print("\nTesting completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Clean up temporary file if created
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
            print(f"Removed temporary config file: {temp_file.name}")


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test InstructionManager functionality")
    
    parser.add_argument(
        "--file-path", 
        help="Path to a file to use for saving/loading (will create a temporary file if not provided)"
    )
    
    parser.add_argument(
        "--no-temp-file", 
        action="store_true",
        help="Don't use a temporary file (requires --file-path to be set)"
    )
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output with detailed instruction information"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check arguments
    if args.no_temp_file and not args.file_path:
        parser.error("--no-temp-file requires --file-path to be set")
    
    # Run the test
    result = test_instruction_manager(
        not args.no_temp_file,
        args.file_path,
        args.verbose
    )
    
    # Return the result code
    sys.exit(result)
