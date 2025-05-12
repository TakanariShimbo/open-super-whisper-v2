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
        if not hotkey_string:
            return None
        
        # Normalize to lowercase and split by '+'
        parts = [part.strip() for part in hotkey_string.lower().split('+')]
        
        # Ensure we have valid parts
        if not parts:
            return None
            
        processed_parts = []
        
        for part in parts:
            # Skip empty parts
            if not part:
                continue
                
            # Check for modifier keys first
            if part in cls.MODIFIER_KEYS:
                processed_parts.append(cls.MODIFIER_KEYS[part])
            # Then check for special keys
            elif part in cls.SPECIAL_KEYS:
                processed_parts.append(cls.SPECIAL_KEYS[part])
            # Single character keys (a-z, 0-9, etc.)
            elif len(part) == 1:
                processed_parts.append(part)
            # Unknown part - pass it through as-is with a warning comment
            else:
                processed_parts.append(part)
        
        # Return None if no valid parts were found
        if not processed_parts:
            return None
            
        # Join all parts with '+' to create the final hotkey string
        return '+'.join(processed_parts)
    
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
        try:
            # Handle special keys
            if isinstance(key, keyboard.Key):
                return cls.REVERSE_KEY_MAPPING.get(key, str(key))
            # Handle character keys
            if hasattr(key, 'char') and key.char:
                return key.char
            # Fall back to string representation
            return str(key)
        except Exception:
            # If anything goes wrong, return a safe string
            return str(key)
