import os

def outputtxt(OutputList, file_path_str, output_dir_str="output"):
    """输出txt文档到当前目录下的output文件夹"""
    # 1. 获取当前程序所在目录的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 创建目标文件夹路径：当前目录下的指定子文件夹（默认为"output"）
    output_dir = os.path.join(current_dir, output_dir_str)
    
    # 3. 确保输出目录存在（不存在则自动创建）
    os.makedirs(output_dir, exist_ok=True)
    
    # 4. 构建输出文件路径
    file_path = os.path.join(output_dir, file_path_str)
    
    # 5. 写入文件内容
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(OutputList)
        
def outputmac(OutputList,file_path,file_name):
    """输出mac文档到指定路径"""
    with open(file_path+'/'+file_name+'.mac', "w", encoding="utf-8") as f:
        f.write(OutputList)