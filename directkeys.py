# http://stackoverflow.com/questions/13564851/generate-keyboard-events
# Modified to include keyboard map and auto-release of press @yportne8

import ctypes
from ctypes import wintypes


user32 = ctypes.WinDLL('user32', use_last_error=True) # [TODO] user_last_error???

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001 # [TODO] test int params 
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0 # const
wintypes.ULONG_PTR = wintypes.WPARAM # struc defs
# [TODO] Rest of keys
KEYMAP = {
    # [NOTE] Possibily for a os manager?
    #   'mute': 173,
    #   'voldown': 174,
    #   'volup': 175,
    'f9': 120, # [TODO] add function keys as loadable functions?
    # [NOTE] Browser
    'brefresh': 168,
    'bstop': 169, #[TODO] check to see if this will stop media playback
    'bsearch': 170,
    # [NOTE] ctrl+esc = search
    'ctrl': 17,
    # [NOTE] media controls
    'prev': 000000,
    'next': 176,
    'play': 179,
     # [NOTE] alt+tab = show all windows
     # win+tab = show all desktops
    'tab': 9,
    # [NOTE] alt+esc = go back to last app
    'esc': 27,
    # [NOTE] Close active window
    'alt': 18,
    'space': 32,
    'C': 00000,
    # [NOTE] a backup window tiler can be implmented
    # using Windows native win-key shortcuts
    'win': 91,
    'left': 37,
    'up': 38,
    'right': 39,
    'down': 40,
    # Letters
    
    
    # Numbers
    
    
    # Special
    
    # Other System ???
}


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))
LPINPUT = ctypes.POINTER(INPUT)


def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize


# [NOTE] Exposed functions
def hold(key):
    global KEYMAP
    if type(key) != int:
        if not KEYMAP.get(key):
            return False
        key = KEYMAP[key]    
    inp = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=key))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def press(key):
    global KEYMAP
    if type(key) != int:
        if not KEYMAP.get(key):
            return False
        key = KEYMAP[key]
    inp = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=key))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    return release(key)


def release(key):
    global KEYMAP
    if type(key) != int:
        if not KEYMAP.get(key):
            return False
        key = KEYMAP[key]
    inp = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=key,
                dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))