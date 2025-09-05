import copy

# 示例基础数组（被查找数组）
base_data = [
    [101, "A", "X"],
    [102, "B", "Y"],
    [103, "C", "Z"],
    [104, "D", "W"],
    [105, "E", "V"]
]

# 查找值数组（5个值）
lookup_values = [101, 102, 103, 104, 105]

# 替换值数组（100行×5列）
# 这里用随机数据生成示例，实际使用您的数据
import random
replacement_data = [
    [f"New_{i}_{j}" for j in range(5)] 
    for i in range(100)
]

# 存储所有新数组的列表
all_new_arrays = []

# 遍历替换数据中的每一行
for row_index, replacement_row in enumerate(replacement_data):
    # 创建基础数组的深拷贝（避免修改原始数据）
    new_array = copy.deepcopy(base_data)
    
    # 遍历查找值数组中的每个值
    for value_index, lookup_value in enumerate(lookup_values):
        # 在基础数组的第一列中查找匹配项
        for item in new_array:
            # 检查第一列是否匹配
            if item[0] == lookup_value:
                # 确保数组足够长（至少有2个元素）
                if len(item) >= 2:
                    # 用当前替换行中的对应值替换第二位
                    # value_index 对应替换行中的位置
                    item[1] = replacement_row[value_index]
                else:
                    print(f"警告：数组 {item} 长度不足")
                # 找到匹配后跳出内层循环（假设每个值只出现一次）
                break
        else:
            # 如果没找到匹配项
            print(f"未找到值 {lookup_value} 在行 {row_index}")
    
    # 将新数组添加到结果列表
    all_new_arrays.append(new_array)

# 示例：查看第一个新数组
print("\n第一个新数组:")
for item in all_new_arrays[1]:
    print(item)