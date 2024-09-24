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
from tools.image_processing import create_error_img, stack_imgs
from application.app_state import AppState
from tools.logger import LogManager
from tools.key_listener import KeyListener
from tools.window import set_window_style
from tools.config_loader import ConfigLoader


class Application:
    """
    应用类
    """
    def __init__(self, config_path):
        self.logger = LogManager(name="app")
        self.config_loader = ConfigLoader(config_path)
        self.grab = GrabScreen()
        self.key_listener = KeyListener(self)
            
        self.target_window_title = self.config_loader.get("target_window_title")
        self.hook_window_title = self.config_loader.get("hook_window_title")
        self.new_width = self.config_loader.get("new_width")
        self.new_height = self.config_loader.get("new_height")
        self.transparency = self.config_loader.get("transparency")
        self.logger.log_debug_filename = self.config_loader.get("log_debug_filename")
        self.logger.log_error_filename = self.config_loader.get("log_error_filename")
        self.save_img_name = self.config_loader.get("save_img_name")
        
        self.running = True
        self.style_set = False
        self.current_index = 0
        self.fps = 0
        self.fps_text = f'FPS: {self.fps}'
        self.scene_text = "unknown"
        self.frame_timestamps = queue.Queue()
        self.state = AppState.NOT_FOUND_WINDOW
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
                        
                        result = self.match(img_origin, "static/data/template/login_tag.json")
                        
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
    
    def match(self, img, target_path):
        # 读取目标图片
        if img is None:
            self.logger.error("无法加载图像")
            return False
        img = cv2.resize(img, (1136, 640))
            
        # 读取 JSON 数据
        with open(target_path, 'r') as file:
            data = json.load(file)
            target_data = base64.b64decode(data['data'])
            target_array = np.frombuffer(target_data, dtype=np.uint8)
            target = cv2.imdecode(target_array, cv2.IMREAD_COLOR)

        # 读取左上角坐标，并增加额外的宽度和高度范围
        x, y = data['lt_x'], data['lt_y']
        width, height = data['width'], data['height']
        extra_width, extra_height = 10, 10
            
        # 截取目标可能在的区域
        roi = img[y: y + height + extra_height, x: x + width + extra_width]
        if roi.size == 0:
            self.logger.error("截取的区域无效，请检查提供的坐标和图像尺寸")
            return False

        # 进行模板匹配
        result = cv2.matchTemplate(roi, target, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 检查匹配得分是否足够高
        if max_val < 0.8:
            self.logger.error("未能找到匹配目标，最高匹配得分：{}".format(max_val))
            return False

        # 计算匹配区域的左上角和右下角坐标
        top_left = (max_loc[0] + x, max_loc[1] + y)
        bottom_right = (top_left[0] + width, top_left[1] + height)
        
        self.logger.info(f"找到目标，匹配度：{max_val:.1f}, 结果坐标：{str(top_left)}到{str(bottom_right)}")
        return True
