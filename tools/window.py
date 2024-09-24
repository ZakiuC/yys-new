import win32gui
import win32con
from tools.logger import LogManager

logger = LogManager(name="window")
def set_window_style(transparency, window_title):
        """
        设置窗口样式，透明度
        """
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

            # 设置 WS_EX_LAYERED 扩展样式
            exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle | win32con.WS_EX_LAYERED)

            win32gui.SetLayeredWindowAttributes(hwnd, 0, transparency, win32con.LWA_ALPHA)
        except Exception as e:
            logger.error("设置窗口 %s 样式出错, 错误: %s", window_title, e)