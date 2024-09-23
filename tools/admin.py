import sys
from ctypes import windll
import logging

def useAdminRun():
    """
    用管理员运行程序
    """
    if not windll.shell32.IsUserAnAdmin():
        logging.error("非管理员启动，尝试提权")
        # 不是管理员就提权
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)  # 退出当前实例