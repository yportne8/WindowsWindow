import ctypes
from ctypes import wintypes
from collections import namedtuple

from win32gui import (
    IsWindowVisible, GetWindowRect, 
    CloseWindow, FindWindow)


class Window:
    
    # [NOTE] Partial titles can be passed,
    # will return the first intrastring match.
    def __init__(self, title: str):
        super().__init__()
        self.title = title
        
    def __list_windows(self):
        windows = dict()
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        WindowInfo = namedtuple('WindowInfo', 'pid title')
        WNDENUMPROC = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HWND,
            wintypes.LPARAM,)
        @WNDENUMPROC
        def enum_proc(hWnd, lParam):
            if user32.IsWindowVisible(hWnd):
                pid = wintypes.DWORD()
                tid = user32.GetWindowThreadProcessId(
                    hWnd, ctypes.byref(pid))
                length = user32.GetWindowTextLengthW(hWnd) + 1
                title = ctypes.create_unicode_buffer(length)
                user32.GetWindowTextW(hWnd, title, length)
                windows[WindowInfo(pid.value, title.value).title] = \
                    WindowInfo(pid.value, title.value).pid
            return True
        user32.EnumWindows(enum_proc, 0)
        return windows
    
    def _get_windows(self):
        windows = dict()
        titles = self.__list_windows()
        for title in titles:
            try:
                windows[title] = FindWindow(None, title)
                assert windows[title] # [TODO] necessary?
            except:
                msg = f"{title} is not listed, possibly closed."
                print(msg)
        return windows
    
    def _get_window_title(self, partial_title):
        windows = self._get_windows()
        return [
            title for title in windows.keys() \
                if partial_title in title][0]

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        windows = self._get_windows()
        if not title in windows.keys():
            partial_title = title
            title = self._get_window_title(partial_title)
        self._title = title
            
    def close(self):
        # [TODO] CloseWindow throws an exception, priviledged action
        # close via os.kill(pid)
        try:
            return CloseWindow(self.hwnd)
        except Exception as e:
            # [TODO]
            # get list of pids and match window hwnd to process pid, -> os.kill(pid)
            print("Failed to close Window.")
            return str(e)
        
    @property
    def pid(self):
        pass
        
    @property
    def hwnd(self):
        return  FindWindow(None, self.title)


    @property
    def isvisible(self):
        return IsWindowVisible(self.hwnd)

    @property
    def position(self):
        rect = GetWindowRect(self.hwnd)
        x = rect[0]+7
        y = rect[1]
        return (x, y)
    
    @property
    def size(self):
        rect = GetWindowRect(self.hwnd)
        w = rect[2] - self.position[0] - 7
        h = rect[3] - self.position[1] - 7
        return (w, h)
