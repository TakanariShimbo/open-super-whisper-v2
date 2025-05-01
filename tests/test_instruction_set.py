#!/usr/bin/env python3
"""
Command-line test for InstructionSet

This test verifies the functionality of the InstructionSet class
from the core.utils module.
"""

import os
import sys
import argparse
import json

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils.instruction_set import InstructionSet


def test_instruction_set(verbose: bool = False):
    """
    Test InstructionSet functionality
    
    Parameters
    ----------
    verbose : bool, optional
        Whether to output detailed instruction information, by default False
    """
    print("Testing InstructionSet creation and methods")
    
    try:
        # Create instruction set with minimal values
        default_set = InstructionSet(name="Default Instruction Set")
        print(f"Created default instruction set:")
        print(f"  Name: {default_set.name}")
        print(f"  STT Instructions: '{default_set.stt_instructions}'")
        print(f"  LLM Instructions: '{default_set.llm_instructions}'")
        
        # Create custom instruction set
        custom_set = InstructionSet(
            name="Meeting Notes Processor",
            stt_instructions="Transcribe accurately with proper speaker attribution and timestamps.",
            llm_instructions="Summarize the meeting transcript, focusing on key decisions, action items, and responsibilities.",
            stt_language="en",
            llm_enabled=True
        )
        
        print(f"\nCreated custom instruction set:")
        print(f"  Name: {custom_set.name}")
        
        if verbose:
            print(f"  STT Instructions: '{custom_set.stt_instructions}'")
            print(f"  LLM Instructions: '{custom_set.llm_instructions}'")
            print(f"  STT Language: '{custom_set.stt_language}'")
            print(f"  LLM Enabled: {custom_set.llm_enabled}")
        
        # Test to_dict method
        instr_dict = custom_set.to_dict()
        print(f"\nInstruction dictionary has {len(instr_dict)} keys")
        
        if verbose:
            print("Dictionary content:")
            print(json.dumps(instr_dict, indent=2))
        
        # Test from_dict method
        new_set = InstructionSet.from_dict(instr_dict)
        print(f"\nCreated new instruction set from dictionary:")
        print(f"  Name: {new_set.name}")
        
        if verbose:
            print(f"  STT Instructions: '{new_set.stt_instructions}'")
            print(f"  LLM Instructions: '{new_set.llm_instructions}'")
            print(f"  STT Language: '{new_set.stt_language}'")
            print(f"  LLM Enabled: {new_set.llm_enabled}")
        
        # Test equality (dataclass implements __eq__ automatically)
        print(f"\nTesting equality check:")
        print(f"  Original set == New set from dict: {custom_set == new_set}")
        print(f"  Original set == Default set: {custom_set == default_set}")
        
        # Test update method
        print(f"\nTesting update method:")
        original_stt_instructions = custom_set.stt_instructions
        custom_set.update(stt_instructions="Updated STT instructions")
        print(f"  STT Instructions before: '{original_stt_instructions}'")
        print(f"  STT Instructions after: '{custom_set.stt_instructions}'")
            
        print("\nTesting completed successfully")
        return 0
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Test InstructionSet functionality")
    
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output with detailed instruction information"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the test
    result = test_instruction_set(args.verbose)
    
    # Return the result code
    sys.exit(result)
