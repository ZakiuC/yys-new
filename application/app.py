import os
import sys
import time
import json
import queue
import threading
import base64

import cv2
import numpy as np

from tools.grabscreen import GrabScreen
from tools.image_processing import create_error_img
from application.app_state import AppState
from tools.logger import LogManager
from tools.key_listener import KeyListener
from tools.window import set_window_style
from tools.config_loader import ConfigLoader
from application.detector import ImageDetector
from application.scene_context import SceneContext

class yysManager:
    def __init__(self):
        self.logger = LogManager(name="yysManager")
        self.scene_context = SceneContext()
        
    def scene_update(self, founds):
        """
        场景更新
        """
        self.scene_context.update(founds)

    def get_scene_name(self):
        """
        获取当前场景名
        """
        return self.scene_context.state.name_en
    
    def get_scene_targets(self):
        """
        获取当前场景目标
        """
        return self.scene_context.state.targets
        
                    
class Application:
    """
    应用类
    """
    def __init__(self, config_path):
        self.logger = LogManager(name="app")
        self.config_loader = ConfigLoader(config_path)
        self.grab = GrabScreen()
        self.key_listener = KeyListener(self)
        self.manager = yysManager()
        
        self.target_window_title = self.config_loader.get("target_window_title")
        self.hook_window_title = self.config_loader.get("hook_window_title")
        self.new_width = self.config_loader.get("new_width")
        self.new_height = self.config_loader.get("new_height")
        self.transparency = self.config_loader.get("transparency")
        self.logger.log_debug_filename = self.config_loader.get("log_debug_filename")
        self.logger.log_error_filename = self.config_loader.get("log_error_filename")
        self.save_img_name = self.config_loader.get("save_img_name")
        template_dir = self.config_loader.get("template_dir")
        template_config = self.config_loader.get("template_config")
        
        self.running = True
        self.style_set = False
        self.current_index = 0
        self.fps = 0
        self.fps_text = f'FPS: {self.fps}'
        self.scene_text = "unknown"
        self.frame_timestamps = queue.Queue()
        self.state = AppState.NOT_FOUND_WINDOW
        self.detector = ImageDetector(template_dir, template_config, self.new_width, self.new_height)
        self.setup_directories()

        self.logger.info("应用程序初始化，配置文件路径：%s", config_path)
    
    def run(self):
        """
        运行程序
        """
        listener_thread = threading.Thread(target=self.key_listener.listener_start)
        fps_thread = threading.Thread(target=self.cal_fps)
        scene_thread = threading.Thread(target=self.scene_update)
        
        listener_thread.start()
        fps_thread.start()
        scene_thread.start()
        
        try:
            while self.running:
                # 获取原始图像
                img_origin = self.grab.grab_window(self.target_window_title)
                
                if img_origin is None:
                    self.state = AppState.NOT_FOUND_WINDOW if self.state != AppState.NOT_FOUND_WINDOW else self.state
                    self.logger.log_error_once("未找到目标窗口")
                    img_origin = create_error_img(self.new_width, self.new_height, 'WINDOW NOT FOUND')
                    self.img_show = [img_origin]
                    self.current_index = 0
                else:
                    if self.state == AppState.NOT_FOUND_WINDOW:
                        self.state = AppState.RUNNING
                    self.logger.clear_error_message("未找到目标窗口")  # 重置error
                    if self.state == AppState.RUNNING:
                        self.img_show = self.detector.process(img_origin)
                        
                        founds = []
                        targets = self.manager.get_scene_targets()
                        # self.logger.debug(f"targets: {targets}")
                        for target in targets:
                            result = self.detector.detect(img_origin, target)
                            if result != None:
                                founds.append(target)
                                # 原始图像的尺寸
                                orig_width = img_origin.shape[1]
                                orig_height = img_origin.shape[0]

                                # 计算缩放因子
                                scale_x = self.new_width / orig_width
                                scale_y = self.new_height / orig_height

                                # 计算映射后的坐标
                                mapped_top_left = (int(result[0][0] * scale_x), int(result[0][1] * scale_y))
                                mapped_bottom_right = (int(result[1][0] * scale_x), int(result[1][1] * scale_y))

                                cv2.rectangle(self.img_show[self.current_index], mapped_top_left, mapped_bottom_right, (0, 0, 255), 1)
                               
                        self.manager.scene_update(founds)
                        self.scene_text = self.manager.get_scene_name()

                        # 轮廓检测
                        # contours, _ = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                        # for cnt in contours:
                        #     cv2.drawContours(img_contour, cnt, -1, (0,255,0), 1)
                    # 添加帧率信息
                    cv2.putText(self.img_show[self.current_index], self.fps_text, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    right_margin = 10
                    (text_width, text_height), _ = cv2.getTextSize(self.scene_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    start_x = self.img_show[self.current_index].shape[1] - text_width - right_margin
                    start_x = max(0, start_x)
                    # 在图片上绘制文本
                    cv2.putText(self.img_show[self.current_index], self.scene_text, (start_x, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # 创建并显示调试窗口，使用新的分辨率
                if not self.style_set:
                    cv2.namedWindow(self.hook_window_title, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(self.hook_window_title, self.new_width, self.new_height)
                    set_window_style(self.transparency, self.hook_window_title)
                    self.style_set = True
                
                cv2.imshow(self.hook_window_title, self.img_show[self.current_index])
                # 图片刷新后，向队列发送当前时间戳
                self.frame_timestamps.put(time.time())
                cv2.waitKey(1)
                
        except Exception as e:
            self.logger.error("主循环报错: %s", e)
            self.running = False
            
        listener_thread.join()
        fps_thread.join()
        scene_thread.join()
        cv2.destroyAllWindows()
        self.logger.info("程序退出")
    
    def find_root_path(self, current_dir):
        """
        通过main.py找根目录
        """
        while current_dir != os.path.dirname(current_dir):
            if os.path.exists(os.path.join(current_dir, 'main.py')):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        return None

    def setup_directories(self):
        """
        创建图片保存目录
        """
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        
        self.path_to_images = os.path.join(self.find_root_path(current_dir), "static", "images", "cap")
        if not os.path.exists(self.path_to_images):
            os.makedirs(self.path_to_images)
            self.logger.debug("创建图片保存目录：%s", self.path_to_images)
        else:
            self.logger.debug("图片保存目录已存在：%s", self.path_to_images)

    def cal_fps(self):
        """
        fps计算
        """
        last_frame_time = None
        while self.running:
            time.sleep(1)
            if self.state == AppState.NOT_FOUND_WINDOW or self.state == AppState.STOPPED:
                continue
            
            try:
                # 从队列中获取时间戳，最多等待一定时间
                current_frame_time = self.frame_timestamps.get(timeout=0.1)
                
                if last_frame_time is not None:
                    time_difference = current_frame_time - last_frame_time
                    if time_difference != 0:
                        self.fps = 1 / time_difference
                        self.fps_text = f'FPS: {self.fps:.2f}'
                last_frame_time = current_frame_time
                self.logger.clear_error_message("帧时间戳队列为空，无法计算 FPS。")
            except queue.Empty:
                self.logger.log_debug_once("帧时间戳队列为空，无法计算 FPS。")
                continue

    def scene_update(self):
        """
        更新场景
        """
        while self.running:
            time.sleep(1)
            if self.state == AppState.NOT_FOUND_WINDOW or self.state == AppState.STOPPED:
                continue
            try:
                self.scene_text = 'no-scene'
            except:
                continue
    
    def decrease_index(self):
        """
        减少索引
        """
        self.current_index = (self.current_index - 1) % len(self.img_show)
    
    def increase_index(self):
        """
        增加索引
        """
        self.current_index = (self.current_index + 1) % len(self.img_show)
        
    def save_current_image(self):
        """
        保存当前图片
        """
        img_origin = self.grab.grab_window(self.target_window_title)
        save_path = self.path_to_images + "\\" + self.save_img_name
        cv2.imwrite(save_path, img_origin)
        self.logger.info(f"截取图片保存至 {save_path}")
    
    def toggle_state(self):
        """
        切换运行状态
        """
        if self.state == AppState.NOT_FOUND_WINDOW:
            self.logger.warn("未找到目标窗口，无法开始运行")
        elif self.state == AppState.RUNNING:
            self.logger.info("停止运行")
            self.state = AppState.STOPPED
        elif self.state == AppState.STOPPED:
            self.logger.info("开始运行")
            self.state = AppState.RUNNING
    
    def stop(self):
        """
        停止程序
        """
        self.running = False
    
