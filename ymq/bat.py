import os
import glob
import pandas as pd
import re

def is_valid_line(line):
    # 检查行是否符合格式要求
    # pattern = r'^-?\d+\.\d+E[+-]\d+\s+-?\d+\.\d+E[+-]\d+\s+-?\d+\.\d+E[+-]\d+\s+-?\d+\.\d+E[+-]\d+$'
    pattern = r'^-?\d+\.\d+E[+-]\d+\s+-?\d+\.\d+E[+-]\d+\s+-?\d+\.\d+E[+-]\d+$'
    return bool(re.match(pattern, line))

def process_dat_files(folder_path):
    # 获取所有dat文件
    dat_files = glob.glob(os.path.join(folder_path, "*.dat"))
    
    if not dat_files:
        print("错误：当前文件夹中没有找到.dat文件")
        return
        
    data_dict = {}
    
    # 处理每个文件
    for file_path in dat_files:
        file_name = os.path.basename(file_path)
        fourth_column_data = []
        
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if is_valid_line(line):
                    values = line.split()
                    if len(values) >= 3:
                        # 直接保存原始字符串，保持科学计数法格式
                        fourth_column_data.append(values[2])
        
        if fourth_column_data:  # 只有当有数据时才添加到字典中
            data_dict[file_name] = fourth_column_data
    
    if not data_dict:
        print("错误：没有在任何文件中找到符合格式要求的数据")
        return
        
    # 找到最长的数据列的长度
    max_length = max(len(data) for data in data_dict.values())
    
    # 将所有列填充到相同长度
    for key in data_dict:
        while len(data_dict[key]) < max_length:
            data_dict[key].append(None)
    
    # 创建DataFrame并保存为Excel
    df = pd.DataFrame(data_dict)
    output_path = os.path.join(folder_path, 'output.xlsx')
    df.to_excel(output_path, index=False)
    print(f"Excel文件已保存到: {output_path}")
    print(f"成功处理的文件数量: {len(data_dict)}")

if __name__ == "__main__":
    # 获取脚本所在文件夹的路径
    script_folder = os.path.dirname(os.path.abspath(__file__))
    print(f"当前文件夹: {script_folder}")
    process_dat_files(script_folder)
