import asyncio
import cv2
import os
import json
import base64
import flet as ft

def save_img_to_json(x, y, img_path, out_dir, is_all_scan):
    if not os.path.exists(img_path):
        raise FileNotFoundError("指定的文件不存在: " + img_path)
    icon = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if icon is None:
        raise FileNotFoundError("无法加载图像，请检查路径是否正确和文件是否完整: " + img_path)

    _, buffer = cv2.imencode('.png', icon)
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

async def cleanup():
    pass

def main(page: ft.Page):
    # 设置窗口大小和位置
    window_width = 440
    window_height = 500
    page.window.width = window_width
    page.window.height = window_height
    page.window.center()  # 使窗口居中
    page.title = "工具"

    x_input = ft.TextField(label="左上角X坐标", value="0", width=195)
    y_input = ft.TextField(label="左上角Y坐标", value="0", width=195)
    img_input = ft.TextField(label="图片路径", value="static/images/template/", width=400)
    out_dir_input = ft.TextField(label="输出路径", value="static/data/template", width=400)
    desc_input = ft.TextField(label="模板描述", value="No description provided", width=400)
    template_json_path_input = ft.TextField(label="Template JSON 路径", value="static/data/template.json", width=400)
    full_scan_checkbox = ft.Checkbox(label="全区域扫描", value=False)
    message_text = ft.Text("", color="green")

    coordinate_row = ft.Row(controls=[x_input, y_input])
    
    def on_convert(e):
        try:
            x = int(x_input.value)
            y = int(y_input.value)
            img_path = img_input.value
            out_dir = out_dir_input.value
            description = desc_input.value
            template_json_path = template_json_path_input.value
            
            name = save_img_to_json(x, y, img_path, out_dir, full_scan_checkbox.value)
            update_template_json(template_json_path, name, f"{name}.json", description)
            message_text.value = f"转换成功: {name}.json"
            message_text.color = "green"
        except Exception as ex:
            message_text.value = f"发生错误: {ex}"
            message_text.color = "red"
        page.update(message_text)

    convert_button = ft.ElevatedButton(text="转换", on_click=on_convert)

    page.add(coordinate_row, img_input, out_dir_input, desc_input, template_json_path_input, full_scan_checkbox, convert_button, message_text)

    # 添加文件选择器
    def on_file_pick(e):
        img_input.value = e.files[0]  # 将选中的文件路径填入文本框
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_pick)
    page.add(file_picker)

    def on_close(e):
        asyncio.run(cleanup())
        print("窗口已关闭")

    page.on_close = on_close

if __name__ == "__main__":
    ft.app(target=main)
