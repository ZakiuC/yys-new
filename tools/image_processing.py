import cv2
import numpy as np



def create_error_img(width, height, message):
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

def stack_images(scale, img_array):
    """
    将多个图像叠加在一起显示。
    参数:
        scale: 图像缩放比例
        img_array: 需要叠加的图像数组
    返回:
        叠加后的图像
    """
    rows = len(img_array)
    cols = len(img_array[0])
    rows_available = isinstance(img_array[0], list)
    width = img_array[0][0].shape[1]
    height = img_array[0][0].shape[0]
    if rows_available:
        for x in range(0, rows):
            for y in range(0, cols):
                if img_array[x][y].shape[:2] == img_array[0][0].shape[:2]:
                    img_array[x][y] = cv2.resize(img_array[x][y], (0, 0), None, scale, scale)
                else:
                    img_array[x][y] = cv2.resize(img_array[x][y], (img_array[0][0].shape[1], img_array[0][0].shape[0]), None, scale, scale)
                if len(img_array[x][y].shape) == 2:
                    img_array[x][y] = cv2.cvtColor(img_array[x][y], cv2.COLOR_GRAY2BGR)
        image_blank = np.zeros((height, width, 3), np.uint8)
        hor = [image_blank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(img_array[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if img_array[x].shape[:2] == img_array[0].shape[:2]:
                img_array[x] = cv2.resize(img_array[x], (0, 0), None, scale, scale)
            else:
                img_array[x] = cv2.resize(img_array[x], (img_array[0].shape[1], img_array[0].shape[0]), None, scale, scale)
            if len(img_array[x].shape) == 2:
                img_array[x] = cv2.cvtColor(img_array[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(img_array)
        ver = hor
    return ver