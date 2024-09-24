import sys
import os
from ctypes import windll
import logging

def useAdminRun():
    """
    用管理员运行程序
    """
    if not windll.shell32.IsUserAnAdmin():
        logging.error("非管理员启动，尝试提权")
        
        # 获取当前执行的脚本完整路径
        script = sys.argv[0]  # 可能需要根据实际情况调整
        if not os.path.isabs(script):
            script = os.path.abspath(script)

        # 获得当前脚本的参数，转换为命令行形式
        params = ' '.join(sys.argv[1:])

        # 提权重启
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit(0)  # 退出当前实例
