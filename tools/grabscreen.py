import cv2
import numpy as np
from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND


class GrabScreen:
    """类用于捕获指定窗口的截图。"""

    # 定义 Windows API 函数
    GetDC = windll.user32.GetDC
    CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
    GetClientRect = windll.user32.GetClientRect
    CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
    SelectObject = windll.gdi32.SelectObject
    BitBlt = windll.gdi32.BitBlt
    SRCCOPY = 0x00CC0020
    GetBitmapBits = windll.gdi32.GetBitmapBits
    DeleteObject = windll.gdi32.DeleteObject
    ReleaseDC = windll.user32.ReleaseDC

    def __init__(self):
        """初始化类并设置DPI识别。"""
        windll.user32.SetProcessDPIAware()

    def capture(self, handle: HWND):
        """捕获窗口客户区截图。"""
        r = RECT()
        self.GetClientRect(handle, byref(r))
        width, height = r.right, r.bottom

        dc = self.GetDC(handle)
        cdc = self.CreateCompatibleDC(dc)
        bitmap = self.CreateCompatibleBitmap(dc, width, height)
        self.SelectObject(cdc, bitmap)
        self.BitBlt(cdc, 0, 0, width, height, dc, 0, 0, self.SRCCOPY)

        total_bytes = width * height * 4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte * total_bytes
        self.GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))

        self.DeleteObject(bitmap)
        self.DeleteObject(cdc)
        self.ReleaseDC(handle, dc)

        return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)

    def grab_window(self, window_name: str):
        """根据窗口名捕获窗口截图。"""
        try:
            hwnd = windll.user32.FindWindowW(None, window_name)
            if hwnd == 0:
                raise Exception('未找到窗口')

            # 使用新的截图方法
            img = self.capture(hwnd)

            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        except Exception as e:
            return None