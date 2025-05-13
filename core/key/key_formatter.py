"""
Format keys into human-readable strings.

This module provides a class for formatting keys into human-readable strings.
"""

from pynput import keyboard


class KeyFormatter:
    """
    Format keys into human-readable strings.
    """
    
    # Class constants for key mappings
    MODIFIER_KEYS: dict[str, str] = {
        'ctrl': '<ctrl>',
        'control': '<ctrl>',
        'alt': '<alt>',
        'option': '<alt>',  # for macOS
        'shift': '<shift>',
        'cmd': '<cmd>',
        'command': '<cmd>',
        'win': '<cmd>',
        'windows': '<cmd>',
        'meta': '<cmd>'
    }
    
    SPECIAL_KEYS: dict[str, str] = {
        'f1': '<f1>', 
        'f2': '<f2>', 
        'f3': '<f3>', 
        'f4': '<f4>',
        'f5': '<f5>', 
        'f6': '<f6>', 
        'f7': '<f7>', 
        'f8': '<f8>',
        'f9': '<f9>', 
        'f10': '<f10>', 
        'f11': '<f11>', 
        'f12': '<f12>',
        'esc': '<esc>', 
        'escape': '<esc>',
        'tab': '<tab>',
        'space': '<space>',
        'backspace': '<backspace>', 
        'bs': '<backspace>',
        'enter': '<enter>', 
        'return': '<enter>',
        'ins': '<insert>', 
        'insert': '<insert>',
        'del': '<delete>', 
        'delete': '<delete>',
        'home': '<home>',
        'end': '<end>',
        'pageup': '<page_up>', 
        'pgup': '<page_up>',
        'pagedown': '<page_down>', 
        'pgdn': '<page_down>',
        'up': '<up>', 
        'down': '<down>', 
        'left': '<left>', 
        'right': '<right>',
        'capslock': '<caps_lock>', 
        'caps': '<caps_lock>',
        'numlock': '<num_lock>', 
        'num': '<num_lock>',
        'scrolllock': '<scroll_lock>', 
        'scrl': '<scroll_lock>',
        'prtsc': '<print_screen>', 
        'printscreen': '<print_screen>'
    }
    
    # Reverse mapping for converting pynput key objects to human-readable strings
    REVERSE_KEY_MAPPING: dict[keyboard.Key, str] = {
        keyboard.Key.alt: 'alt',
        keyboard.Key.alt_l: 'alt_l',
        keyboard.Key.alt_r: 'alt_r',
        keyboard.Key.alt_gr: 'alt_gr',
        keyboard.Key.backspace: 'backspace',
        keyboard.Key.caps_lock: 'caps_lock',
        keyboard.Key.cmd: 'cmd',
        keyboard.Key.cmd_l: 'cmd_l',
        keyboard.Key.cmd_r: 'cmd_r',
        keyboard.Key.ctrl: 'ctrl',
        keyboard.Key.ctrl_l: 'ctrl_l',
        keyboard.Key.ctrl_r: 'ctrl_r',
        keyboard.Key.delete: 'delete',
        keyboard.Key.down: 'down',
        keyboard.Key.end: 'end',
        keyboard.Key.enter: 'enter',
        keyboard.Key.esc: 'esc',
        keyboard.Key.f1: 'f1',
        keyboard.Key.f2: 'f2',
        keyboard.Key.f3: 'f3',
        keyboard.Key.f4: 'f4',
        keyboard.Key.f5: 'f5',
        keyboard.Key.f6: 'f6',
        keyboard.Key.f7: 'f7',
        keyboard.Key.f8: 'f8',
        keyboard.Key.f9: 'f9',
        keyboard.Key.f10: 'f10',
        keyboard.Key.f11: 'f11',
        keyboard.Key.f12: 'f12',
        keyboard.Key.home: 'home',
        keyboard.Key.insert: 'insert',
        keyboard.Key.left: 'left',
        keyboard.Key.menu: 'menu',
        keyboard.Key.num_lock: 'num_lock',
        keyboard.Key.page_down: 'page_down',
        keyboard.Key.page_up: 'page_up',
        keyboard.Key.pause: 'pause',
        keyboard.Key.print_screen: 'print_screen',
        keyboard.Key.right: 'right',
        keyboard.Key.scroll_lock: 'scroll_lock',
        keyboard.Key.shift: 'shift',
        keyboard.Key.shift_l: 'shift_l',
        keyboard.Key.shift_r: 'shift_r',
        keyboard.Key.space: 'space',
        keyboard.Key.tab: 'tab',
        keyboard.Key.up: 'up'
    }
    
    # Map for control characters to more readable names (without 'ctrl+' prefix)
    CONTROL_CHAR_MAPPING: dict[str, str] = {
        '\x01': 'a', 
        '\x02': 'b', 
        '\x03': 'c', 
        '\x04': 'd',
        '\x05': 'e', 
        '\x06': 'f', 
        '\x07': 'g', 
        '\x08': 'h',
        '\x09': 'i', 
        '\x0A': 'j', 
        '\x0B': 'k', 
        '\x0C': 'l',
        '\x0D': 'm', 
        '\x0E': 'n', 
        '\x0F': 'o', 
        '\x10': 'p',
        '\x11': 'q', 
        '\x12': 'r', 
        '\x13': 's', 
        '\x14': 't',
        '\x15': 'u', 
        '\x16': 'v', 
        '\x17': 'w', 
        '\x18': 'x',
        '\x19': 'y', 
        '\x1A': 'z'
    }

    @classmethod
    def parse_hotkey_string(cls, hotkey_string: str) -> str | None:
        """
        Convert a user-friendly hotkey string to the format pynput expects.
        
        Parameters
        ----------
        hotkey_string : str
            User-friendly hotkey string (e.g., "ctrl+shift+r").
            
        Returns
        -------
        str | None
            Pynput format hotkey string (e.g., "<ctrl>+<shift>+r"), or None if invalid.
            
        Examples
        --------
        >>> HotkeyCommon.parse_hotkey_string("ctrl+shift+r")
        '<ctrl>+<shift>+r'
        >>> HotkeyCommon.parse_hotkey_string("alt+f4")
        '<alt>+<f4>'
        >>> HotkeyCommon.parse_hotkey_string("command+option+space")
        '<cmd>+<alt>+<space>'
        >>> HotkeyCommon.parse_hotkey_string("")
        None
        """
        # Handle empty input
        if not hotkey_string:
            return None
        
        # Normalize and split input
        parts = cls._normalize_hotkey_parts(hotkey_string)
        if not parts:
            return None
            
        # Process each part
        processed_parts = cls._process_hotkey_parts(parts)
        if not processed_parts:
            return None
            
        # Join parts with '+' and return
        return '+'.join(processed_parts)
    
    @classmethod
    def _normalize_hotkey_parts(cls, hotkey_string: str) -> list[str]:
        """Normalize hotkey string and split into parts."""
        # Normalize to lowercase and split by '+'
        parts = [part.strip() for part in hotkey_string.lower().split('+')]
        return [part for part in parts if part]  # Filter out empty parts
    
    @classmethod
    def _process_hotkey_parts(cls, parts: list[str]) -> list[str]:
        """Process each part of a hotkey string."""
        processed_parts = []
        
        for part in parts:
            if part in cls.MODIFIER_KEYS:
                # Handle modifier keys (ctrl, alt, shift, etc.)
                processed_parts.append(cls.MODIFIER_KEYS[part])
            elif part in cls.SPECIAL_KEYS:
                # Handle special keys (f1, esc, etc.)
                processed_parts.append(cls.SPECIAL_KEYS[part])
            elif len(part) == 1:
                # Handle single character keys (a-z, 0-9, etc.)
                processed_parts.append(part)
            else:
                # Handle unknown parts
                processed_parts.append(part)
        
        return processed_parts
    
    @classmethod
    def format_key(cls, key: keyboard.Key | keyboard.KeyCode) -> str:
        """
        Format a key object into a human-readable string.
        
        Parameters
        ----------
        key : pynput.keyboard.Key or pynput.keyboard.KeyCode
            The key to format.
            
        Returns
        -------
        str
            A human-readable string representation of the key.
        """
        # Handle special keys (like shift, ctrl, etc.)
        if isinstance(key, keyboard.Key):
            return cls.REVERSE_KEY_MAPPING.get(key, str(key))
            
        # Handle character keys
        if not hasattr(key, 'char') or not key.char:
            return str(key)
            
        # Regular character - return as is
        if not cls._is_control_character(key.char):
            return key.char
            
        # Handle control characters (Ctrl+Key combinations)
        return cls._format_control_character(key.char)
    
    @classmethod
    def _is_control_character(cls, char: str) -> bool:
        """Check if a character is a control character (ASCII < 32)."""
        return len(char) == 1 and ord(char) < 32
    
    @classmethod
    def _format_control_character(cls, char: str) -> str:
        """Format a control character to a readable representation."""
        # Use our mapping if available
        if char in cls.CONTROL_CHAR_MAPPING:
            return cls.CONTROL_CHAR_MAPPING[char]
            
        # Default: convert control character to corresponding letter (e.g., Ctrl+C -> 'c')
        control_char = chr(ord(char) + 64)
        return control_char.lower()
            
    @classmethod
    def format_keys_set(cls, keys: set[keyboard.Key | keyboard.KeyCode]) -> list[str]:
        """
        Format a set of keys into a sorted string representation.
        
        Parameters
        ----------
        keys : set[keyboard.Key | keyboard.KeyCode]
            Set of keys to format
            
        Returns
        -------
        list[str]
            A list of strings containing all keys formatted and sorted (modifiers first). 
            Empty list if no keys are provided.
        """
        # Return early if no keys
        if not keys:
            return []
        
        # Check for control/modifier keys presence
        has_ctrl = cls._has_ctrl_key(keys)
            
        # Get formatted key strings
        key_strings = cls._get_formatted_key_strings(keys)
        
        # Separate and sort keys
        modifier_keys, regular_keys = cls._separate_keys(key_strings, has_ctrl)
        
        # Combine and join with '+'
        sorted_keys = modifier_keys + regular_keys
        return sorted_keys if sorted_keys else []
    
    @classmethod
    def _has_ctrl_key(cls, keys: set[keyboard.Key | keyboard.KeyCode]) -> bool:
        """Check if Ctrl key (any variant) is present in the key set."""
        return any(
            isinstance(k, keyboard.Key) and (
                k == keyboard.Key.ctrl or 
                k == keyboard.Key.ctrl_l or 
                k == keyboard.Key.ctrl_r
            ) for k in keys
        )
    
    @classmethod
    def _get_formatted_key_strings(cls, keys: set[keyboard.Key | keyboard.KeyCode]) -> list[str]:
        """Convert all keys to formatted strings, filtering out empty ones."""
        key_strings = []
        
        for key in keys:
            key_str = cls.format_key(key)
            if key_str:  # Only add non-empty strings
                key_strings.append(key_str)
                
        return key_strings
    
    @classmethod
    def _separate_keys(cls, key_strings: list[str], has_ctrl: bool) -> tuple[list[str], list[str]]:
        """Separate keys into modifiers and regular keys."""
        modifier_keys = []
        regular_keys = []
        
        # List of all modifier key names
        modifiers = ('ctrl', 'ctrl_l', 'ctrl_r', 'alt', 'alt_l', 'alt_r', 
                    'shift', 'shift_l', 'shift_r', 'cmd', 'cmd_l', 'cmd_r')
        
        # Letters that might be control characters
        ctrl_letters = set("abcdefghijklmnopqrstuvwxyz")
        
        for key_str in key_strings:
            if key_str in modifiers:
                modifier_keys.append(key_str)
            elif has_ctrl and key_str in ctrl_letters:
                # If this is a plain letter and we have Ctrl pressed, combine them
                regular_keys.append(key_str)
            else:
                regular_keys.append(key_str)
                
        # Sort both lists
        modifier_keys.sort()
        regular_keys.sort()
        
        return modifier_keys, regular_keys