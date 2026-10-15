import argparse
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import subprocess
import time
from ctypes import HRESULT, POINTER, WinDLL
from ctypes.wintypes import HWND, DWORD, RECT

import win32api
import win32event
import win32gui
import win32process
from comtypes import IUnknown, GUID, COMMETHOD
import comtypes
import comtypes.client

get_shell_window = WinDLL("user32", use_last_error=True).GetShellWindow
get_shell_window.argtypes = []
get_shell_window.restype = HWND


class ITipInvocation(IUnknown):
    _iid_ = GUID("{37c994e7-432b-4834-a2f7-dce1f13b834b}")
    _methods_ = [COMMETHOD([], HRESULT, "Toggle", (['in'], HWND, "hwndDesktop"))]


class IFrameworkInputPane(IUnknown):
    _iid_ = GUID("{5752238B-24F0-495A-82F1-2FD593056796}")
    _methods_ = [
        COMMETHOD([], HRESULT, "Advise",
                  (['in'], POINTER(IUnknown), "window"),
                  (['in'], POINTER(IUnknown), "handler"),
                  (['out'], POINTER(DWORD), "cookie")),
        COMMETHOD([], HRESULT, "AdviseWithHWND",
                  (['in'], HWND, "window"),
                  (['in'], POINTER(IUnknown), "handler"),
                  (['out'], POINTER(DWORD), "cookie")),
        COMMETHOD([], HRESULT, "Unadvise", (['in'], DWORD, "cookie")),
        COMMETHOD([], HRESULT, "Location", (['out'], POINTER(RECT), "rect")),
    ]


def keyboard_visible(pane):
    rect = pane.Location()
    return rect.right > rect.left and rect.bottom > rect.top


def wait_for_visibility(pane, visible, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if keyboard_visible(pane) == visible:
            return
        time.sleep(0.05)
    raise TimeoutError(f"Touch keyboard did not become visible={visible}")


def pulse_keyboard(duration=0.5):
    comtypes.CoInitialize()
    try:
        pane = comtypes.client.CreateObject(
            "{D5120AA3-46BA-44C5-822D-CA8092C1FC72}", interface=IFrameworkInputPane)
        # Do not close a keyboard the user was already using.
        if keyboard_visible(pane):
            logging.info("Touch keyboard already visible; leaving it open")
            return
        try:
            invocation = comtypes.client.CreateObject(
                "{4ce576fa-83dc-4F88-951c-9d0782b4e376}", interface=ITipInvocation)
        except OSError:
            tabtip = Path(os.environ.get("CommonProgramW6432", os.environ["CommonProgramFiles"]))
            subprocess.Popen([str(tabtip / "microsoft shared/ink/TabTip.exe")])
            time.sleep(0.5)
            invocation = comtypes.client.CreateObject(
                "{4ce576fa-83dc-4F88-951c-9d0782b4e376}", interface=ITipInvocation)
        if not keyboard_visible(pane):
            invocation.Toggle(win32gui.GetDesktopWindow())
        wait_for_visibility(pane, True)
        shown_at = time.monotonic()
        time.sleep(duration)
        if keyboard_visible(pane):
            invocation.Toggle(win32gui.GetDesktopWindow())
        wait_for_visibility(pane, False)
        logging.info("Touch keyboard opened and closed; hold=%.3fs, elapsed=%.3fs",
                     duration, time.monotonic() - shown_at)
    finally:
        comtypes.CoUninitialize()


def shell_identity():
    hwnd = get_shell_window()
    if not hwnd:
        return None
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
    except win32api.error:
        return None  # The shell can exit between the two calls.
    return (hwnd, pid) if pid else None


class ExplorerWatcher:
    def __init__(self, pulse=pulse_keyboard):
        self.pulse = pulse
        self.completed = None
        self.pending = None
        self.ready_at = 0

    def tick(self, shell, now):
        if shell != self.pending:
            self.pending = shell
            self.ready_at = now + 2  # Allow the new shell to finish initialization.
        if shell is None or shell == self.completed or now < self.ready_at:
            return
        try:
            self.pulse()
        except Exception:
            logging.exception("Keyboard initialization failed for shell %s; retrying", shell)
            self.ready_at = now + 5
        else:
            self.completed = shell
            logging.info("Initialized shell hwnd=%s pid=%s", *shell)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Open and close once, then exit")
    args = parser.parse_args()
    log_dir = Path(os.environ["LOCALAPPDATA"]) / "ImeSavior"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[RotatingFileHandler(log_dir / "ImeSavior.log",
                                                      maxBytes=262144, backupCount=1,
                                                      encoding="utf-8")])
    mutex = win32event.CreateMutex(None, False, "Local\\ImeSavior.ExplorerWatcher")
    try:
        if win32api.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            logging.info("Another instance is already running")
            return
        logging.info("Started; mode=%s", "once" if args.once else "watch")
        if args.once:
            pulse_keyboard()
        else:
            watcher = ExplorerWatcher()
            while True:
                watcher.tick(shell_identity(), time.monotonic())
                time.sleep(0.5)
    finally:
        win32api.CloseHandle(mutex)


if __name__ == '__main__':
    main()
