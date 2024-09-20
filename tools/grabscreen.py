# -*- coding: utf-8 -*-
'''
Author       : ZakiuC
Date         : 2024-01-04 10:55:32
LastEditors  : ZakiuC z2337070680@163.com
LastEditTime : 2024-01-04 10:58:55
FilePath     : \yys\grabscreen.py
Description  : 
Copyright (c) 2024 by ZakiuC z2337070680@163.com, All Rights Reserved. 
'''
import cv2
import numpy as np
from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND


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


def capture(handle: HWND):
    """
        窗口客户区截图
        handle: 窗口句柄
        return: numpy.ndarray
    """
    r = RECT()
    GetClientRect(handle, byref(r))
    width, height = r.right, r.bottom

    dc = GetDC(handle)
    cdc = CreateCompatibleDC(dc)
    bitmap = CreateCompatibleBitmap(dc, width, height)
    SelectObject(cdc, bitmap)
    BitBlt(cdc, 0, 0, width, height, dc, 0, 0, SRCCOPY)

    total_bytes = width * height * 4
    buffer = bytearray(total_bytes)
    byte_array = c_ubyte * total_bytes
    GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))

    DeleteObject(bitmap)
    DeleteObject(cdc)
    ReleaseDC(handle, dc)

    return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)


def grab_window(window_name):
    """
    根据窗口名捕获窗口
    window_name: 窗口名
    """
    # 设置进程 DPI 识别
    windll.user32.SetProcessDPIAware()

    try:
        # 找到窗口句柄
        hwnd = windll.user32.FindWindowW(None, window_name)
        if hwnd == 0:
            raise Exception(f'未找到窗口: {window_name}')

        # 使用新的截图方法
        img = capture(hwnd)

        # 转换图像格式
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    except Exception as e:
        print(f'窗口句柄捕获抛出异常：{e}')
        return None