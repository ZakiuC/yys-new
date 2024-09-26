import os
import pyperclip

def generate_directory_tree(path, indent=""):
    """
    递归生成目录树字符串。
    """
    items = os.listdir(path)
    items = [item for item in items if not item.startswith('.')]  # 忽略隐藏文件
    content = ""
    len_items = len(items)
    for index, item in enumerate(sorted(items, key=lambda s: s.lower())):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            if index == len_items - 1:
                content += f"{indent}└── {item}/\n"
                new_indent = indent + "    "
            else:
                content += f"{indent}├── {item}/\n"
                new_indent = indent + "│   "
            content += generate_directory_tree(item_path, new_indent)
        else:
            if index == len_items - 1:
                content += f"{indent}└── {item}\n"
            else:
                content += f"{indent}├── {item}\n"
    return content

def export_directory_structure_to_file(path):
    """
    将目录结构导出到文件，并复制到剪贴板。
    """
    tree = generate_directory_tree(path)
    
    # 获取脚本的目录路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'out')
    
    # 检查是否存在输出目录，如果不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 定义输出文件路径
    output_file_path = os.path.join(output_dir, 'output.txt')
    
    # 写入到文件
    with open(output_file_path, 'w') as file:
        file.write(tree)
    
    # 复制到剪贴板
    pyperclip.copy(tree)
    print(f"Directory tree of '{path}' has been saved to '{output_file_path}' and copied to clipboard.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py [path_to_directory]")
    else:
        directory_path = sys.argv[1]
        export_directory_structure_to_file(directory_path)
