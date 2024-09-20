import os
import sys
import time
import queue
import threading
from ctypes import windll

import cv2
import numpy as np
import win32gui
import win32con

from tools.grabscreen import grab_window



def createErrImg(width, height, message):
    """
    创建一个显示错误信息的图像
    width: 图像宽度
    height: 图像高度
    message: 错误信息
    """
    img = np.zeros((height, width, 3), np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (0, 0, 255)
    font_thickness = 2

    # 获取文本大小
    text_size = cv2.getTextSize(message, font, font_scale, font_thickness)[0]

    # 计算文本在图像中的位置（居中）
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2

    # 将文本放置在图像中央
    cv2.putText(img, message, (text_x, text_y), font, font_scale, font_color, font_thickness)
    return img

def stackImgs(scale, imgArray):
    """
    将图像堆叠在一起以便于显示
    scale: 缩放因子
    imgArray: 图像列表

    return: 堆叠后的图像
    """
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)

    # 在这里，我们需要确定合适的尺寸以调整图像
    width = imgArray[0][0].shape[1] * scale
    height = imgArray[0][0].shape[0] * scale
    dim = (int(width), int(height))

    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                # 调整图像尺寸
                imgArray[x][y] = cv2.resize(imgArray[x][y], dim, interpolation=cv2.INTER_AREA)
                if len(imgArray[x][y].shape) == 2:
                    imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        # 堆叠处理
        hor = [np.hstack(imgArray[x]) for x in range(0, rows)]
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], dim, interpolation=cv2.INTER_AREA)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        ver = np.hstack(imgArray)

    return ver

def calFps():
    """
    fps计算
    """
    global fps_text, running, frame_timestamps
    last_frame_time = None
    while running:
        try:
            # 从队列中获取时间戳，最多等待一定时间
            current_frame_time = frame_timestamps.get(timeout=0.1)
            if last_frame_time is not None:
                time_difference = current_frame_time - last_frame_time
                if time_difference != 0:
                    fps = 1 / time_difference
                    fps_text = f'FPS: {fps:.2f}'
            last_frame_time = current_frame_time
        except queue.Empty:
            continue

def sceneUpdate():
    """
    更新场景
    """
    global scene_text
    while running:
        try:
            scene_text = 'no-scene'
            time.sleep(0.1)
        except:
            continue
        
        
def useAdminRun():
    """
    用管理员运行程序
    """
    if not windll.shell32.IsUserAnAdmin():
        # 不是管理员就提权
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)  # 退出当前实例

state = 99

if __name__ == "__main__":
    # useAdminRun()
    
    target_window_title = "阴阳师-网易游戏"
    hook_window_title = "hook"
    new_width, new_height = 640, 361
    current_index = 0

    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    path_to_images = os.path.join(current_dir, "static", "images")
    save_path = path_to_images
    
    # 初始化帧率相关的变量
    fps = 0
    frame_time = time.time()
    fps_text = f'FPS: {fps}'
    running = True
    # 初始化场景显示的变量
    scene_text = "unknown"

    # 创建一个线程安全的队列
    frame_timestamps = queue.Queue()

    # 创建并启动 FPS 计算线程
    fps_thread = threading.Thread(target=calFps)
    fps_thread.start()

    # 创建并启动场景更新线程
    scene_thread = threading.Thread(target=sceneUpdate)
    scene_thread.start()

    # 获取窗口句柄
    handle = windll.user32.FindWindowW(None, target_window_title)
    
    while True:
        img_origin = grab_window(target_window_title)

        if img_origin is None:
            img_origin = createErrImg(new_width, new_height, 'WINDOW NOT FOUND')

        # 调整图像大小以适应新的分辨率
        img_resize = cv2.resize(img_origin, (new_width, new_height))

        # 图像处理
        img_gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (7,7), 1)
        img_canny = cv2.Canny(img_blur, 50, 50)
        img_blank = np.zeros_like(img_resize)
        img_contour = img_resize.copy()
        img_stack = stackImgs(0.6, ([img_resize, img_gray, img_blur],
                                    [img_canny, img_contour, img_blank]))
  
        img_show = [img_resize, img_gray, img_blur, img_canny, img_contour, img_stack]
        
        # 轮廓检测
        contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            cv2.drawContours(img_contour, cnt, -1, (0,255,0), 1)
        
        # 添加帧率信息
        cv2.putText(img_show[current_index], fps_text, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        right_margin = 10
        (text_width, text_height), baseline = cv2.getTextSize(scene_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        start_x = img_show[current_index].shape[1] - text_width - right_margin
        start_x = max(0, start_x)
        # 在图片上绘制文本
        cv2.putText(img_show[current_index], scene_text, (start_x, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # 创建并显示窗口，使用新的分辨率
        cv2.namedWindow(hook_window_title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(hook_window_title, new_width, new_height)
        cv2.imshow(hook_window_title, img_show[current_index])

        # 图片刷新后，向队列发送当前时间戳
        frame_timestamps.put(time.time())

        hwnd = win32gui.FindWindow(None, hook_window_title)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        # 设置 WS_EX_LAYERED 扩展样式
        exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle | win32con.WS_EX_LAYERED)

        # 设置窗口透明度 0(完全透明) 到 255(完全不透明)
        transparency = 255
        win32gui.SetLayeredWindowAttributes(hwnd, 0, transparency, win32con.LWA_ALPHA)

        # 获取一次键盘输入
        key = cv2.waitKey(1) & 0xFF

        # 根据键盘输入更新当前显示的图像索引
        if key == ord('a') or key == ord('A'):
            current_index = (current_index - 1) % len(img_show)  # 循环显示
        elif key == ord('d') or key == ord('D'):
            current_index = (current_index + 1) % len(img_show)  # 循环显示
        elif key == ord('j') or key == ord('J'):
            # 保存当前显示的图像
            cv2.imwrite(save_path + "/image.png", img_show[current_index])
            print(f"Image saved at {save_path}")
        elif key == ord('s') or key == ord('S'):
            if state != 99:
                state = 99
                print("Stop script.")
            else:
                state = 0
                print("Start script.")
        elif key == ord('q') or key == ord('Q'):
            running = False
            print("Exiting...")
            break
            
        if state == 100:
            running = False
            print("Exiting...")
            break
        
    # 线程和窗口清理
    fps_thread.join()
    scene_thread.join()
    cv2.destroyAllWindows()