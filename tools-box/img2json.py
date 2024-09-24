import cv2
import os
import json
import base64
import argparse

def save_img_to_json(x, y, img_path, out_dir):
    if not os.path.exists(img_path):
        raise FileNotFoundError("指定的文件不存在: " + img_path)
    else:
        print("尝试读取的图像路径:", img_path)
    icon = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if icon is None:
        raise FileNotFoundError("无法加载图像，请检查路径是否正确和文件是否完整: " + img_path)

    _, buffer = cv2.imencode('.png', icon)
    icon_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # 构建输出 JSON 文件的完整路径
    base_name = os.path.splitext(os.path.basename(img_path))[0]  # 提取文件名，去掉扩展名
    out_path = os.path.join(out_dir, f"{base_name}.json")


    # 封装数据和元数据
    data = {
        'lt_x': x,
        'lt_y': y,
        'width': icon.shape[1],
        'height': icon.shape[0],
        'data': icon_base64
    }

    # 写入 JSON 文件
    with open(out_path , 'w') as file:
        json.dump(data, file, indent=4)
        file.close()
    
    print(f"已保存至{out_path}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="启动应用程序并指定配置文件")
    parser.add_argument('-x', '--lt_x', type=int, default=0, help='目标匹配区域左上角x坐标')
    parser.add_argument('-y', '--lt_y', type=int, default=0, help='目标匹配区域左上角y坐标')
    parser.add_argument('-img', '--img_path', type=str, required=True, help='待转换的图片路径(绝对路径)')
    parser.add_argument('-out', '--out_dir', type=str, default='static/data/template', help='数据文件输出路径(绝对路径)')
    args = parser.parse_args()
    
    save_img_to_json(args.lt_x, args.lt_y, args.img_path, args.out_dir)