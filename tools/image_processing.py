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

def stack_imgs(scale, img_array):
    """
    将图像堆叠在一起以便于显示
    scale: 缩放因子
    imgArray: 图像列表

    return: 堆叠后的图像
    """
    rows = len(img_array)
    cols = len(img_array[0])
    rows_available = isinstance(img_array[0], list)
    
    # 确定合适的尺寸以调整图像
    width = img_array[0][0].shape[1] * scale
    height = img_array[0][0].shape[0] * scale
    dim = (int(width), int(height))

    if rows_available:
        for x in range(rows):
            for y in range(cols):
                # 调整图像尺寸
                img_array[x][y] = cv2.resize(img_array[x][y], dim, interpolation=cv2.INTER_AREA)
                if len(img_array[x][y].shape) == 2:
                    img_array[x][y] = cv2.cvtColor(img_array[x][y], cv2.COLOR_GRAY2BGR)
        # 堆叠处理
        hor = [np.hstack(img_array[x]) for x in range(rows)]
        ver = np.vstack(hor)
    else:
        for x in range(rows):
            img_array[x] = cv2.resize(img_array[x], dim, interpolation=cv2.INTER_AREA)
            if len(img_array[x].shape) == 2:
                img_array[x] = cv2.cvtColor(img_array[x], cv2.COLOR_GRAY2BGR)
        ver = np.hstack(img_array)
    return ver