import os

def outputtxt(OutputList ,file_path_str,output_dir_str):
    """输出txt文档"""
    # 1. 获取当前程序所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. 获取上级目录路径 (os.pardir 表示父级目录)
    parent_dir = os.path.join(current_dir, os.pardir)

    # 3. 创建目标文件夹路径：上级目录下的 output 子文件夹
    
    output_dir = os.path.join(parent_dir, output_dir_str)

    # 4. 确保输出目录存在（不存在则自动创建）
    os.makedirs(output_dir, exist_ok=True)

    # 5. 构建输出文件路径
    file_path = os.path.join(output_dir, file_path_str)

    # 6. 写入文件内容（示例）
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(OutputList)