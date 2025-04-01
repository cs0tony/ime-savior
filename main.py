import subprocess
import time
import win32gui
from ctypes import HRESULT
from ctypes.wintypes import HWND
from comtypes import IUnknown, GUID, COMMETHOD
import comtypes.client


class ITipInvocation(IUnknown):
    _iid_ = GUID("{37c994e7-432b-4834-a2f7-dce1f13b834b}")
    _methods_ = [COMMETHOD([], HRESULT, "Toggle", (['in'], HWND, "hwndDesktop"))]


def close_tabtip():
    global success
    while not success:
        try:
            dtwin = win32gui.GetDesktopWindow()
            comtypes.CoInitialize()
            ctsdk = comtypes.client.CreateObject("{4ce576fa-83dc-4F88-951c-9d0782b4e376}", interface=ITipInvocation)
            ctsdk.Toggle(dtwin)
            success = True
        except OSError as e:
            time.sleep(0.5)
        finally:
            comtypes.CoUninitialize()


def open_tabtip():
    try:
        dtwin = win32gui.GetDesktopWindow()
        comtypes.CoInitialize()
        ctsdk = comtypes.client.CreateObject("{4ce576fa-83dc-4F88-951c-9d0782b4e376}", interface=ITipInvocation)
        ctsdk.Toggle(dtwin)
    except OSError as e:
        # os.system("C:\\PROGRA~1\\COMMON~1\\MICROS~1\\ink\\tabtip.exe")
        # 使用 subprocess 替换 os.system
        subprocess.Popen(["start", "C:\\PROGRA~1\\COMMON~1\\MICROS~1\\ink\\tabtip.exe"], shell=True)
    finally:
        comtypes.CoUninitialize()


if __name__ == '__main__':
    success = False
    open_tabtip()
    time.sleep(1)
    close_tabtip()
