import cv2
import numpy as np
import json
import base64
import os

from tools.logger import LogManager
from tools.image_processing import stack_images

class ImageDetector:
    """
    图像处理类，用于处理和转换图像。
    """
    def __init__(self, template_dir, config_path, new_width, new_height):
        self.logger = LogManager(name="detector")
        self.new_width = new_width
        self.new_height = new_height
        self.template_dir = template_dir
        self.templates = self.load_config(config_path)

    def load_config(self, config_path):
        """
        加载配置文件中的模板信息。
        """
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        return config['templates']

    def process(self, img_origin):
        """
        图像处理
        参数:
            img_origin: 原始图像
        返回:
            处理后的图像组
        """
        # 调整图像大小以适应新的分辨率
        img_resize = cv2.resize(img_origin, (self.new_width, self.new_height))
        # 图像处理
        img_gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (7,7), 1)
        img_canny = cv2.Canny(img_blur, 50, 50)
        img_blank = np.zeros_like(img_resize)
        img_contour = img_resize.copy()
        img_stack = stack_images(0.6, ([img_resize, img_gray, img_blur], [img_canny, img_contour, img_blank]))

        self.img_show = [img_resize, img_gray, img_blur, img_canny, img_contour, img_stack]
        return self.img_show
        
    def detect(self, img_origin, template_name):
        """
        匹配指定模板。

        Args:
            img_origin (_type_): 原始图像
            template_name (_type_): 指定的模板名称
        """
        template_file = self.find_template_by_name(template_name)
        if template_file:
            return self.match(img_origin, template_file)
        else:
            self.logger.error(f"未找到[{template_name}]")
            raise ValueError(f"未找到[{template_name}]")

    def find_template_by_name(self, name):
        """
        根据模板名称找到对应的文件路径。
        """
        for template in self.templates:
            if template['name'] == name:
                return template['file']
        return None
    
    def match(self, img, json_filename):
        """
        执行模板匹配。

        Args:
            img (_type_): 图像
            target_path (_type_): 模板匹配的JSON文件路径

        Returns:
            _type_: 匹配结果
        """
        target_path = os.path.join(self.template_dir, json_filename)
        # 读取目标图片
        if img is None:
            self.logger.error("无法加载图像")
            return None
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
        is_all_scan = data['is_all_scan']
        extra_width, extra_height = 20, 20
            
        # 截取目标可能在的区域
        if is_all_scan:
            # 根据x, y的值调整起始点和截取的宽度、高度
            start_x = 0 if x == 0 else x
            start_y = 0 if y == 0 else y
            end_x = img.shape[1] if x == 0 else x + width + extra_width
            end_y = img.shape[0] if y == 0 else y + height + extra_height

            # 确保不超过图像边界
            end_x = min(end_x, img.shape[1])
            end_y = min(end_y, img.shape[0])

            # 截取图像
            roi = img[start_y:end_y, start_x:end_x]
        else:
            # 直接截取指定区域，确保不超过图像边界
            start_x = x
            start_y = y
            end_x = min(x + width + extra_width, img.shape[1])
            end_y = min(y + height + extra_height, img.shape[0])

            roi = img[start_y:end_y, start_x:end_x]

        if roi.size == 0:
            self.logger.error("截取的区域无效，请检查提供的坐标和图像尺寸")
            return None
        
        # cv2.imshow('debug', roi)
        # 进行模板匹配
        result = cv2.matchTemplate(roi, target, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 检查匹配得分是否足够高
        if max_val < 0.8:
            # self.logger.error("未能找到匹配目标，最高匹配得分：{}".format(max_val))
            return None

        # 计算匹配区域的左上角和右下角坐标
        top_left = (max_loc[0] + x, max_loc[1] + y)
        bottom_right = (top_left[0] + width, top_left[1] + height)
        
        # self.logger.info(f"找到目标，匹配度：{max_val:.1f}, 结果坐标：{str(top_left)}到{str(bottom_right)}")
        return top_left, bottom_right
