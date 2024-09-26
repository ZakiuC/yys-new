from cv2 import imread, imencode, IMREAD_UNCHANGED
import os
import base64
import json
import sys

import flet as ft


# 获取当前执行文件的绝对路径，确保配置文件与 exe 在同一目录
if getattr(sys, 'frozen', False):
    # 被 PyInstaller 打包后的程序
    directory = os.path.dirname(sys.executable)
else:
    # 正常的 Python 脚本
    directory = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(directory, 'config.json')

def load_config():
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        # 如果配置文件不存在，返回默认配置
        return {
            'img_input': 'D:/zakiu/Code/python/yys/static/images/template',
            'out_dir_input': 'static/data/template',
            'template_json_path_input': 'static/data/template.json',
            'window_width': 600,
            'window_height': 500,
            'full_width': 1136,
            'full_height': 640,
            'is_full_scan': False,
            'is_inverse': True,
            'is_dark': False
        }

def save_config(config):
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4)
        
        
def save_img_to_json(x, y, img_path, out_dir, is_all_scan):
    if not os.path.exists(img_path):
        raise FileNotFoundError("指定的文件不存在: " + img_path)
    icon = imread(img_path, IMREAD_UNCHANGED)
    if icon is None:
        raise FileNotFoundError("无法加载图像，请检查路径是否正确和文件是否完整: " + img_path)

    _, buffer = imencode('.png', icon)
    icon_base64 = base64.b64encode(buffer).decode('utf-8')
    
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    out_path = os.path.join(out_dir, f"{base_name}.json")

    data = {
        'lt_x': x,
        'lt_y': y,
        'width': icon.shape[1],
        'height': icon.shape[0],
        'is_all_scan': is_all_scan,
        'data': icon_base64
    }

    with open(out_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    
    return base_name

def update_template_json(template_json_path, template_name, json_filename, description):
    if os.path.exists(template_json_path):
        with open(template_json_path, 'r', encoding='utf-8') as file:
            template_data = json.load(file)
    else:
        template_data = {"templates": []}

    new_template = {
        "name": template_name,
        "file": json_filename,
        "description": description
    }

    template_data['templates'].append(new_template)

    with open(template_json_path, 'w', encoding='utf-8') as file:
        json.dump(template_data, file, indent=4, ensure_ascii=False)


def main(page: ft.Page):
    config = load_config()
    
    # 获取图标文件的路径
    if getattr(sys, 'frozen', False):
        directory = os.path.dirname(sys.executable)
    else:
        # 如果是正常的 Python 脚本
        directory = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(directory, 'img.ico')  # 替换为您的图标文件名
    
    # 设置窗口大小和位置
    page.window.width = config.get('window_width', 600)  # 使用配置中的值或默认值
    page.window.height = config.get('window_height', 500)
    if config['is_dark']:
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
    page.window.center()  # 使窗口居中
    page.title = "工具"
    page.window.icon = icon_path  # 设置窗口图标

    input_width = page.window.width - 40
    input_num_width = (page.window.width - 50) / 2
    x_input = ft.TextField(label="左上角X坐标", value="", width=input_num_width)
    y_input = ft.TextField(label="左上角Y坐标", value="", width=input_num_width)
    img_input = ft.TextField(label="图片路径", value=config['img_input'], width=input_width)
    out_dir_input = ft.TextField(label="输出路径", value=config['out_dir_input'], width=input_width)
    template_json_path_input = ft.TextField(label="Template JSON 路径", value=config['template_json_path_input'], width=input_width)
    desc_input = ft.TextField(label="模板描述", value="", width=input_width)
    full_scan_checkbox = ft.Checkbox(label="全区域扫描", value=config['is_full_scan'])
    inverse_checkbox = ft.Checkbox(label="反向解析坐标", value=config['is_inverse'])
    is_dark = ft.Checkbox(label="启用深色模式", value=config['is_dark'])
    message_text = ft.Text("", color="green")

    coordinate_row = ft.Row(controls=[x_input, y_input])
    checkbox_row = ft.Row(controls=[full_scan_checkbox, inverse_checkbox, is_dark])
    
    # 窗口大小调整时更新配置
    def on_resize(e):
        config['window_width'] = page.window.width
        config['window_height'] = page.window.height
        save_config(config)

    def on_data_change(e):
        if is_dark.value:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        # 更新配置
        img_path = img_input.value
        out_dir = out_dir_input.value
        template_json_path = template_json_path_input.value
        config['img_input'] = img_path
        config['out_dir_input'] = out_dir
        config['template_json_path_input'] = template_json_path
        config['is_full_scan'] = full_scan_checkbox.value
        config['is_inverse'] = inverse_checkbox.value
        config['is_dark'] = is_dark.value
        save_config(config)
        page.update()  # 刷新页面以应用更改
        
    def on_convert(e):
        try:
            x = int(x_input.value)
            y = int(y_input.value)
            img_path = img_input.value
            out_dir = out_dir_input.value
            description = desc_input.value
            template_json_path = template_json_path_input.value
            
            
            if inverse_checkbox.value:
                target_x = config['full_width'] - x
                target_y = config['full_height'] - y
            else:
                target_x = x
                target_y = y
                
            name = save_img_to_json(target_x, target_y, img_path, out_dir, full_scan_checkbox.value)
            update_template_json(template_json_path, name, f"{name}.json", description)
            message_text.value = f"转换成功: {name}.json"
            message_text.color = "green"
            
            
        except Exception as ex:
            message_text.value = f"发生错误: {ex}"
            message_text.color = "red"
        page.update(message_text)

    convert_button = ft.ElevatedButton(text="转换", on_click=on_convert)
    page.window.on_resize = on_resize
    # 添加 on_change 事件处理函数
    x_input.on_change = on_data_change
    y_input.on_change = on_data_change
    img_input.on_change = on_data_change
    out_dir_input.on_change = on_data_change
    template_json_path_input.on_change = on_data_change
    desc_input.on_change = on_data_change
    full_scan_checkbox.on_change = on_data_change
    inverse_checkbox.on_change = on_data_change
    is_dark.on_change = on_data_change
    
    page.add(coordinate_row, img_input, out_dir_input, desc_input, template_json_path_input, checkbox_row, convert_button, message_text)

    # 添加文件选择器
    def on_file_pick(e):
        img_input.value = e.files[0]  # 将选中的文件路径填入文本框
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_pick)
    page.add(file_picker)

    def on_close(e):
        print("窗口已关闭")

    page.on_close = on_close

if __name__ == "__main__":
    ft.app(target=main)
