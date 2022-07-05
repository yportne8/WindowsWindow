# http://stackoverflow.com/questions/13564851/generate-keyboard-events
# Modified to include keyboard map and auto-release of press & shortcut function
# @yportne8
import ctypes
from ctypes import wintypes


user32 = ctypes.WinDLL('user32', use_last_error=True) # [TODO] user_last_error???

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0 # const
wintypes.ULONG_PTR = wintypes.WPARAM # struc defs

KEYMAP = {
    'LBUTTON': 1, 'RBUTTON': 2, 'MBUTTON': 4,
    'XBUTTON1': 5, 'XBUTTON2': 6, 'CANCEL': 3,
    'BACK': 8, 'TAB': 9, 'CLEAR': 12, 'RETURN': 13,
    'SHIFT': 16, 'CONTROL': 17, 'MENU': 18, 'PAUSE': 19,
    'CAPITAL': 20, 'ESCAPE': 27, 'SPACE': 32, 'PRIOR': 33,
    'NEXT': 34, 'END': 35, 'HOME': 36, 'LEFT': 37, 'UP': 85,
    'RIGHT': 39, 'DOWN': 40, 'SELECT': 41, 'PRINT': 42,
    'EXECUTE': 43, 'SNAPSHOT': 44,'INSERT': 45, 'DELETE': 46,
    'HELP': 47, '0': 48, '1': 49, '2': 50, '3': 51, '4': 52,
    '5': 53, '6': 54, '7': 55, '8': 56, '9': 57, 'A': 65,
    'B': 66, 'C': 67, 'D': 68, 'E': 69, 'F': 70, 'G': 71,
    'H': 72, 'I': 73, 'j': 74, 'K': 75, 'L': 76, 'M': 77,
    'N': 78, 'O': 79, 'P': 80, 'Q': 81, 'R': 82, 'S': 83,
    'T': 84, 'V': 86, 'W': 87, 'X': 88, 'Y': 89, 'Z': 90,
    'LWIN': 91, 'RWIN': 92, 'APPS': 93, 'SLEEP': 95,
    'NUMPAD0': 96, 'NUMPAD1': 97, 'NUMPAD2': 98,
    'NUMPAD3': 99, 'NUMPAD4': 100, 'NUMPAD5': 101,
    'NUMPAD6': 102, 'NUMPAD7': 103, 'NUMPAD8': 104,
    'NUMPAD9': 105, 'MULTIPLY': 106, 'ADD': 107,
    'SEPARATOR': 108, 'SUBTRACT': 109, 'DECIMAL': 110,
    'DIVIDE': 111, 'F1': 112, 'F2': 113, 'F3': 114,
    'F4': 115, 'F5': 116, 'F6': 117, 'F7': 118,
    'F8': 119, 'F9': 120, 'F10': 121, 'F11': 122,
    'F12': 123, 'F13': 124, 'F14': 125, 'F15': 126,
    'F16': 127, 'F17': 128, 'F18': 129, 'F19': 130,
    'F20': 131, 'F21': 132, 'F22': 133, 'F23': 134,
    'F24': 135, 'NUMLOCK': 144, 'SCROLL': 145,
    'LSHIFT': 160, 'RSHIFT': 161, 'LCONTROL': 162,
    'LCTRL': 162, 'RCONTROL': 163, 'RCTRL': 163, 
    'LMENU': 164, 'RMENU': 165, 'BROWSER_BACK': 166,
    'BROWSER_FORWARD': 167, 'BROWSER_REFRESH': 168,
    'BROWSER_STOP': 169, 'BROWSER_SEARCH': 170,
    'BROWSER_FAVORITES': 171, 'BROWSER_HOME': 172,
    'VOLUME_MUTE': 173, 'VOLUME_DOWN': 174, 'VOLUME_UP': 175,
    'MEDIA_NEXT_TRACK': 176, 'MEDIA_PREV_TRACK': 177,
    'MEDIA_STOP': 178, 'MEDIA_PLAY_PAUSE': 179,
    'LAUNCH_MAIL': 180, 'LAUNCH_MEDIA_SELECT': 181,
    'LAUNCH_APP1': 182, 'LAUNCH_APP2': 183,
    '?': 191, '~': 192, '{': 219, '|': 220, '}': 221, '"': 222,
    'ATTN': 246, 'CRSEL': 247, 'EXSEL': 248, 'PLAY': 250, 'ZOOM': 251}


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

def _key(key):
    global KEYMAP
    if type(key) != int:
        if not KEYMAP.get(key):
            return False
        key = KEYMAP[key]
    return key 

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize


def shortcut(downkeys, presskeys):
    if type(downkeys) != list:
        downkeys = [downkeys]
    if type(presskeys) != list:
        presskeys = [presskeys]
    for key in downkeys:
        hold(key)
    for key in presskeys:
        press(key)
    for key in downkeys:
        release(key)


def hold(key):
    inp = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=_key(key)))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))


def press(key):
    inp = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=_key(key)))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    return release(key)


def release(key):
    inp = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=_key(key),
                dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))