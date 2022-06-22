import os
import time
import ctypes
from ctypes import wintypes
from collections import (
    namedtuple, defaultdict)

from win32api import (
    SetWindowPos, GetSystemMetrics)
from win32con import (
    SW_SHOWNORMAL, SW_HIDE, SW_SHOW, HWND_TOPMOST,
    SW_MINIMIZE, SW_MAXIMIZE)
from win32gui import (
    ShowWindow, SetWindowText, BringWindowToTop,
    SetForegroundWindow, IsWindowVisible,
    GetWindowRect, FindWindow)


class Window:
    
    # [NOTE] Partial titles can be passed,
    # will return the first intrastring match.
    def __init__(self, title: str, new_title: str=None):
        super().__init__()
        self.title = title
        if new_title:
            try:
                self._change_window_title(self.hwnd, new_title)
                time.sleep(3)
                self.title = new_title
            except:
                print("Failed to change Window title...\n")
                print(f"Current Title: {self.title}")
        
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

    def _get_processes(self):
        processes = defaultdict(list)
        cmd = 'wmic process get description, processid'
        process_list = os.popen(cmd).read()
        processes_items = process_list.split("\n\n")
        for item in processes_items:
            name_pid = item.split(" ")
            try:
                name = name_pid[0].strip()
                pid = [v for v in name_pid[1:] if v != ""][0]
                processes[name].append(pid)
            except:
                pass
        for name, pids in processes.items():
            processes[name] = sorted(pids)
        return processes
    
    def _get_xy(self, w, h, quadrant: int = None):
        if not quadrant:
            isaftermid = x > self.screenw//2
            isabovemid = y < self.screenh//2
            if isaftermid and isabovemid:
                quadrant = 2
            elif isaftermid and not isabovemid:
                quadrant = 3
            elif not isaftermid and isabovemid:
                quadrant = 1
            elif not isaftermid and not isabovemid:
                quadrant = 4
        if quadrant == 1:
            x = self.hoverx
            y = self.hoverx
        elif quadrant == 2:
            x = self.screenw - w - self.hoverx
            y = self.hoverx
        elif quadrant == 3:
            x = self.screenw - w - self.hoverx
            y = self.screenh - h - self.hovery
        elif quadrant == 4:
            x = self.hoverx
            y = self.screenh - h - self.hovery
        return (x, y)

    def _change_window_title(self, new_title):
        SetWindowText(self.hwnd, new_title)
    
    def _get_window_title(self, partial_title):
        windows = self._get_windows()
        return [
            title for title in windows.keys() \
                if partial_title in title][0]
        
    @property
    def hwnd(self):
        return FindWindow(None, self.title)

    @property
    def pid(self):
        pass
        
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
    
    def ontop(self):
        BringWindowToTop(self.hwnd)
        ShowWindow(self.hwnd, SW_SHOWNORMAL)
    
    def focus(self):
        BringWindowToTop(self.hwnd)
        ShowWindow(self.hwnd, SW_SHOWNORMAL)
        SetForegroundWindow(self.hwnd)

    def hide(self):
        ShowWindow(self.hwnd, SW_HIDE)

    def show(self):
        ShowWindow(self.hwnd, SW_SHOW)

    def move(self, x: int, y: int):
        SetWindowPos(self.hwnd, HWND_TOPMOST,
            x, y, self.size[0], self.size[1], 0)

    def resize(self, w: int, h: int):
        SetWindowPos(self.hwnd, HWND_TOPMOST,
            self.position[0], self.position[1],
            w, h, 0)

    def resize_and_move(self, resizepct: float):
        x, y = self.position
        w, h = self.size
        if resizepct > 1:
            deltaw = (w * resizepct)-w
            deltah = (h * resizepct)-h
        else:
            deltaw = -(w-(w * resizepct))
            deltah = -(h-(h * resizepct))
        w += deltaw
        h += deltah
        print(f"Current Size: {(w, h)}")
        self.resize(w, h)
        print(f"New Size: {self.size}")
        x, y = self._get_xy(w, h, None)
        return self.move(x, y)

    def move_to_quadrant(self, quadrant: int=None):
        w, h = self.size
        x, y = self._get_xy(w, h, quadrant)
        return self.move(x, y)
        
    def minimize(self):
        return ShowWindow(self.hwnd, SW_MINIMIZE)

    def maximize(self):
        return ShowWindow(self.hwnd, SW_MAXIMIZE)

    def center(self):
        x = GetSystemMetrics(0)
        x = x/2-self.size[0]/2
        y = GetSystemMetrics(1)
        y = y/2-self.size[1]/2
        return self.move(x, y)

    def refresh(self):
        self.focus()
        # send CTRL+F5
    
    def close(self):
        retcode = os.system(f'taskkill /PID {self.pid} /f')
        return retcode == 128