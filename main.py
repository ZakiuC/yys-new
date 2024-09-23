import os
import sys
import time
import queue
import threading
import json
import logging
from logging.handlers import RotatingFileHandler
from ctypes import windll

import cv2
import numpy as np
import win32gui
import win32con
from enum import Enum, auto
from pynput.keyboard import Key, Listener

from tools.grabscreen import GrabScreen
from tools.image_processing import create_error_img, stack_imgs
from application.app_state import AppState

    
class Application:
    """
    应用类
    """
    def __init__(self, config_path):
        config = self.load_config(config_path)
            
        self.target_window_title = config["target_window_title"]
        self.hook_window_title = config["hook_window_title"]
        self.new_width = config["new_width"]
        self.new_height = config["new_height"]
        self.transparency = config["transparency"]
        self.log_debug_filename = config["log_debug_filename"]
        self.log_error_filename = config["log_error_filename"]
        self.save_img_name = config["save_img_name"]
        
        self.running = True
        self.style_set = False
        self.current_index = 0
        self.fps = 0
        self.fps_text = f'FPS: {self.fps}'
        self.scene_text = "unknown"
        self.frame_timestamps = queue.Queue()
        self.state = AppState.NOT_FOUND_WINDOW
        self.error_messages_logged = {}  # 字典用于跟踪已记录的错误信息
        self.debug_messages_logged = {}  # 字典用于跟踪已记录的调试信息
        self.grab = GrabScreen()
        self.setup_directories()
        
        # 设置日志记录配置，分别记录调试和错误信息
        self.setup_logging()

        logging.info("应用程序初始化，配置文件路径：%s", config_path)

    def setup_logging(self):
        """
        设置日志记录配置
        """
        # 创建 logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # 设置最低的日志级别

        # 创建调试日志处理器，使用 RotatingFileHandler
        debug_handler = RotatingFileHandler(
            self.log_debug_filename, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)

        # 创建错误日志处理器，使用 RotatingFileHandler
        error_handler = RotatingFileHandler(
            self.log_error_filename, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        debug_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)

        # 添加处理器到 logger
        logger.addHandler(debug_handler)
        logger.addHandler(error_handler)
        
    def load_config(self, config_path):
        """
        加载配置文件
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as config_file:
                config = json.load(config_file)
            return config
        except Exception as e:
            logging.error("加载配置文件失败：%s", e)
            raise
    
    def log_error_once(self, message):
        """
        记录一条错误消息，如果这条消息之前没有被记录过。
        """
        if message not in self.error_messages_logged:
            logging.error(message)
            self.error_messages_logged[message] = True
    
    def clear_error_message(self, message):
        """
        清除已记录的错误消息，允许这条消息在未来被重新记录。
        """
        if message in self.debug_messages_logged:
            del self.debug_messages_logged[message]
    
    def log_debug_once(self, message):
        """
        记录一条调试消息，如果这条消息之前没有被记录过。
        """
        if message not in self.debug_messages_logged:
            logging.error(message)
            self.debug_messages_logged[message] = True
            
    def clear_debug_message(self, message):
        """
        清除已记录的调试消息，允许这条消息在未来被重新记录。
        """
        if message in self.error_messages_logged:
            del self.error_messages_logged[message]
    
    def setup_directories(self):
        """
        创建图片保存目录
        """
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        self.path_to_images = os.path.join(current_dir, "static", "images")
        if not os.path.exists(self.path_to_images):
            os.makedirs(self.path_to_images)
            logging.debug("创建图片保存目录：%s", self.path_to_images)
        else:
            logging.debug("图片保存目录已存在：%s", self.path_to_images)

    def cal_fps(self):
        """
        fps计算
        """
        last_frame_time = None
        while self.running:
            if self.state == AppState.NOT_FOUND_WINDOW or self.state == AppState.STOPPED:
                break
            try:
                # 从队列中获取时间戳，最多等待一定时间
                current_frame_time = self.frame_timestamps.get(timeout=0.1)
                if last_frame_time is not None:
                    time_difference = current_frame_time - last_frame_time
                    if time_difference != 0:
                        self.fps = 1 / time_difference
                        self.fps_text = f'FPS: {self.fps:.2f}'
                last_frame_time = current_frame_time
                self.clear_error_message("帧时间戳队列为空，无法计算 FPS。")
            except queue.Empty:
                self.log_debug_once("帧时间戳队列为空，无法计算 FPS。")
                continue

    def scene_update(self):
        """
        更新场景
        """
        while self.running:
            if self.state == AppState.NOT_FOUND_WINDOW or self.state == AppState.STOPPED:
                break
            try:
                self.scene_text = 'no-scene'
                time.sleep(0.1)
            except:
                continue

    def on_press(self, key):
        """
        按键监听器
        """
        try:
            char = key.char.lower()
        except AttributeError:
            char = key
        try:
            if char == 'a':
                self.current_index = (self.current_index - 1) % len(self.img_show)
            elif char == 'd':
                self.current_index = (self.current_index + 1) % len(self.img_show)
            elif char == 'j':
                img_origin = self.grab.grab_window(self.target_window_title)
                save_path = self.path_to_images + "/" + self.save_img_name
                cv2.imwrite(save_path, img_origin)
                logging.info(f"截取图片保存至 {save_path}")
            elif char == 's':
                if self.state == AppState.NOT_FOUND_WINDOW:
                    logging.warning("未找到目标窗口，无法开始运行")
                elif self.state == AppState.RUNNING:
                    logging.info("停止运行")
                    self.state = AppState.STOPPED
                elif self.state == AppState.STOPPED:
                    logging.info("开始运行")
                    self.state = AppState.RUNNING
            elif char == Key.esc:  # 使用特殊的 Key 类来检测 Esc
                self.running = False
                return False  # 返回 False 来停止监听器
        except Exception as e:
            logging.error("按键处理错误: %s", e)

    def start_listener(self):
        """
        启动按键监听
        """
        with Listener(on_press=self.on_press) as listener:
            listener.join()
    

    def set_window_style(self, window_title):
        """
        设置窗口样式，透明度
        """
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

            # 设置 WS_EX_LAYERED 扩展样式
            exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle | win32con.WS_EX_LAYERED)

            win32gui.SetLayeredWindowAttributes(hwnd, 0, self.transparency, win32con.LWA_ALPHA)
        except Exception as e:
            logging.error("设置窗口 %s 样式出错, 错误: %s", window_title, e)
    
    def run(self):
        """
        运行程序
        """
        fps_thread = threading.Thread(target=self.cal_fps)
        scene_thread = threading.Thread(target=self.scene_update)
        listener_thread = threading.Thread(target=self.start_listener)

        fps_thread.start()
        scene_thread.start()
        listener_thread.start()
        
        try:
            while self.running:
                # 获取原始图像
                img_origin = self.grab.grab_window(self.target_window_title)

                if img_origin is None:
                    self.state = AppState.NOT_FOUND_WINDOW
                    self.log_error_once("未找到目标窗口")
                    img_origin = create_error_img(self.new_width, self.new_height, 'WINDOW NOT FOUND')
                    self.img_show = [img_origin]
                    cv2.namedWindow(self.hook_window_title, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(self.hook_window_title, self.new_width, self.new_height)
                    cv2.imshow(self.hook_window_title, self.img_show[self.current_index])
                else:
                    if self.state == AppState.NOT_FOUND_WINDOW:
                        self.state = AppState.RUNNING
                    self.clear_error_message("未找到目标窗口")  # 重置error
                    # 调整图像大小以适应新的分辨率
                    img_resize = cv2.resize(img_origin, (self.new_width, self.new_height))
                    # 图像处理
                    img_gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
                    img_blur = cv2.GaussianBlur(img_gray, (7,7), 1)
                    img_canny = cv2.Canny(img_blur, 50, 50)
                    img_blank = np.zeros_like(img_resize)
                    img_contour = img_resize.copy()
                    img_stack = stack_imgs(0.6, ([img_resize, img_gray, img_blur], [img_canny, img_contour, img_blank]))

                    self.img_show = [img_resize, img_gray, img_blur, img_canny, img_contour, img_stack]
                    
                    # 轮廓检测
                    contours, _ = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    for cnt in contours:
                        cv2.drawContours(img_contour, cnt, -1, (0,255,0), 1)
                    # 添加帧率信息
                    cv2.putText(self.img_show[self.current_index], self.fps_text, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    right_margin = 10
                    (text_width, text_height), _ = cv2.getTextSize(self.scene_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    start_x = self.img_show[self.current_index].shape[1] - text_width - right_margin
                    start_x = max(0, start_x)
                    # 在图片上绘制文本
                    cv2.putText(self.img_show[self.current_index], self.scene_text, (start_x, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    # 创建并显示调试窗口，使用新的分辨率
                    cv2.namedWindow(self.hook_window_title, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(self.hook_window_title, self.new_width, self.new_height)
                    cv2.imshow(self.hook_window_title, self.img_show[self.current_index])
                    
                    if not self.style_set:
                        self.set_window_style(self.hook_window_title)
                        self.style_set = True

                    # 图片刷新后，向队列发送当前时间戳
                    self.frame_timestamps.put(time.time())
                    
                cv2.waitKey(1)
                
        except Exception as e:
            logging.error("主循环报错: %s", e)
            
        listener_thread.join()
        fps_thread.join()
        scene_thread.join()
        cv2.destroyAllWindows()

        
if __name__ == "__main__":
    # useAdminRun()

    app = Application("config.json")
    app.run()
    logging.info("程序退出")
