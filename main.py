import itertools
import os
import tkinter as tk
from tkinter import filedialog
import copy
from openpyxl import load_workbook
from table_extraction import table_extract
from calculate_keypoint import calculate_keypoint
from output import outputtxt
from output import outputmac
from post_processing import PostProcessing

def KeyPoint(OutputList,SerialNumber_KeyPoint,INputDataList):
    """点语句输出\n
    可输出结构：八边形、四边形\n
    INputDataList:三维点坐标List
    """
    num_point = len(INputDataList)
    for i in range(num_point):
        KeyPoints = f"K , {SerialNumber_KeyPoint} , {INputDataList[i][0]} , {INputDataList[i][1]} , {INputDataList[i][2]}"
        OutputList = OutputList + KeyPoints + "\n"
        SerialNumber_KeyPoint += 1
    return OutputList,SerialNumber_KeyPoint

def generate_box_area(OutputList,SerialNumber_KeyPoint,SerialNumber_KeyPoints,Box_Structure):
    """箱体面语句输出\n
    可输出结构：八边形、四边形\n
    Box_Structure:箱体结构"""
    if Box_Structure == "八边形":
        OutputList = OutputList + """A , 9 , 10 , 2 , 1\nA , 10 , 11 , 3 , 2\nA , 11 , 12 , 4 , 3
A , 12 , 13 , 5 , 4\nA , 13 , 14 , 6 , 5\nA , 14 , 15 , 7 , 6
A , 15 , 16 , 8 , 7\nA , 16 , 9 , 1 , 8\n"""
    elif Box_Structure == "四边形":
        OutputList = OutputList + """A , 5 , 6 , 2 , 1\nA , 6 , 7 , 3 , 2\nA , 7 , 8 , 4 , 3\nA , 8 , 5 , 1 , 4\n"""
    else:
        raise ValueError(f"不支持的箱体结构: {Box_Structure}")
    OutputList = OutputList + """ASEL, ALL\n! 创建新组件侧壁\nCM, CEBI, AREA\nASEL, NONE\n"""
    return OutputList,SerialNumber_KeyPoint,SerialNumber_KeyPoints

def generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoint_in,SerialNumber_KeyPoint,side_num):
    """箱盖加强筋面语句输出\n
    可输出结构：八边形、四边形\n
    num_module:模块序号
    SerialNumber_KeyPoint：SerialNumber_KeyPoint
    """
    for i in range(int((SerialNumber_KeyPoint-SerialNumber_KeyPoint_in)/side_num)):
        Area_Basic = "A , "
        Area_Add = "{Knums}"
        Knums = []
        for j in range(side_num):
            Knums.append(SerialNumber_KeyPoint_in + j)
        Area_Add = Area_Add.format(Knums=' , '.join(map(str, Knums)))
        Area_Basic = Area_Basic + Area_Add
        OutputList = OutputList + Area_Basic + "\n"
        SerialNumber_KeyPoint_in += side_num
    return OutputList,SerialNumber_KeyPoint
    
def oilbox_main(ReservedQuantity_OfModules, data_table,row_index):
    # 1. 定义参数
    SerialNumber_KeyPoints = [1]
    for i in range(len(ReservedQuantity_OfModules)):
        SerialNumber_KeyPoints.append(ReservedQuantity_OfModules[i]*4 + SerialNumber_KeyPoints[i])
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[0] # 全局变量，确定模块之间位置

    data_dict = dict(data_table) # 字典转化

    # 定义模板初始段
    OutputList = f"""FINISH              ! 结束当前模块 xin
/CLEAR , START       ! 清除数据库，开始新的分析
!========== 定义参数 (Preprocessor) ==========
str = 'test{row_index}'
! ===== 1. 设置工作目录和文件名 =====
/MKDIR, 'D:/result/test{row_index}'     ! 创建项目目录（如不存在）
/CWD,'D:/result/test{row_index}'        ! 设置工作目录
/FILNAME,str, 1     ! 设置文件名前缀
/CONFIG,NRES,8
! ========== 前处理 (Preprocessor) ==========
/PREP7              ! 进入前处理器
! 1. 定义材料属性 (钢)
MP, EX, 1, 210000   ! 杨氏模量 (Pa)
MP, PRXY, 1, 0.3    ! 泊松比
MP, DENS, 1, 7.85e-9   ! 密度 (kg/m³)

! 2. 定义单元类型 (壳单元SHELL181)
ET, 1, SHELL181     ! 选择壳单元类型
KEYOPT, 1, 8, 2     ! 设置存储应力和应变

! 3. 定义不同厚度的实常
! 箱顶厚度
R, 1, {data_dict["BoxCover_Thickness"]}
! 箱沿及箱顶箱沿厚度 
R, 2, {data_dict["BoxEdge_Thickness"]}
! 侧壁厚度
R, 3, {data_dict["Box_ShortAxisThickness"]}
! 加强拱厚度
R, 4, {data_dict["ReinforcingRib_Long_Vertical_Thickness_High"]}
! 箱顶加强筋厚度
R, 5, {data_dict["ReinforcingRib_BoxCover_Vertical_Thickness"]}
! 竖向加强槽下加强筋厚度
R, 6, {data_dict["ReinforcingRib_Vertical_UnderVerticalReinforcement_Thickness"]}
    """

    # 3. 计算坐标
    cal_point = calculate_keypoint(data_table) # 加载计算模块
    # 3.1. 箱体
    # 箱体坐标输出
    KeyPointList_TankWall = cal_point.generate_box_points() 
    OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_TankWall) # 箱体坐标点语句输出
    OutputList,SerialNumber_KeyPoint,SerialNumber_KeyPoints = generate_box_area(OutputList,SerialNumber_KeyPoint,SerialNumber_KeyPoints,data_dict["Box_Structure"]) # 生成箱体面语句输出
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[1] # 修改全局变量，确定模块之间位置````
    # 箱盖沿坐标输出
    KeyPointList_BoxCover = cal_point.generate_boxcover_edge_keypoint() 
    OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_BoxCover) # 箱盖沿坐标点语句输出
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[2] # 修改全局变量，确定模块之间位置


    if data_dict["Box_Structure"] == "八边形":
        OutputList = OutputList + """A , 1, 2, 3, 4, 5, 6, 7, 8\nBOTTOM_AREA = _RETURN
A , 17,18,19,20,21,22,23,24\nRIM_AREA = _RETURN\nASBA, RIM_AREA, BOTTOM_AREA
! 创建新组件箱底沿\nCM, BOTTOM_RIM, AREA\nASEL, NONE\nA , 16,15,14,13,12,11,10,9\nUP_AREA = _RETURN
A , 32,31,30,29,28,27,26,25\nUP_RIM_AREA = _RETURN\nASBA, UP_RIM_AREA, UP_AREA
! 创建新组件箱盖沿\nCM, TOP_RIM, AREA\nASEL, NONE
"""
    elif data_dict["Box_Structure"] == "四边形":
        OutputList = OutputList + """A , 1, 2, 3, 4\nBOTTOM_AREA = _RETURN
A , 17,18,19,20\nRIM_AREA = _RETURN\nASBA, RIM_AREA, BOTTOM_AREA
! 创建新组件箱底沿\nCM, BOTTOM_RIM, AREA\nASEL, NONE\nA , 8,7,6,5\nUP_AREA = _RETURN
A , 24,23,22,21\nUP_RIM_AREA = _RETURN\nASBA, UP_RIM_AREA, UP_AREA
! 创建新组件箱盖沿\nCM, TOP_RIM, AREA\nASEL, NONE
"""

    # 箱盖加强筋坐标输出
    KeyPointList_ReinforcingRib_BoxC , X_KeyPointList_ReinforcingRib_BoxC, rib_V_num = cal_point.generate_ReinforcingRib_BoxCover_keypoint() 
    OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_ReinforcingRib_BoxC) # 箱盖加强筋坐标点语句输出
    OutputList,SerialNumber_KeyPoint = generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoints[2],SerialNumber_KeyPoint,4) # 生成箱盖加强筋面语句输出
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[3] # 修改全局变量，确定模块之间位置
    OutputList = OutputList + """! 创建新组件箱盖加强筋\nCM, XDJIAQIANGJIN, AREA\nASEL, NONE\n"""

    # 箱盖分区建立
    KeyPointList_BoxC_6 , KeyPointList_BoxC_4 = cal_point.generate_BoxCover_keypoint(X_KeyPointList_ReinforcingRib_BoxC,rib_V_num)
    if data_dict["Box_Structure"] == "八边形":
        OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_BoxC_6)
        OutputList,SerialNumber_KeyPoint = generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoints[3],SerialNumber_KeyPoint,6) # 生成箱盖加强筋面语句输出
        OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_BoxC_4)
        OutputList,SerialNumber_KeyPoint = generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoints[3]+12,SerialNumber_KeyPoint,4) # 生成箱盖加强筋面语句输出
    elif data_dict["Box_Structure"] == "四边形":
        OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_BoxC_4)
        OutputList,SerialNumber_KeyPoint = generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoints[3],SerialNumber_KeyPoint,4) # 生成箱盖加强筋面语句输出
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[4] # 修改全局变量，确定模块之间位置
    OutputList = OutputList + """! 创建新组件箱盖\nCM, TOP, AREA\nASEL, NONE\n"""

    # 长轴纵向加强筋建立
    KeyPointList_ReinforcingRib_L_V , KeyPointList_ReinforceRib_V_L_UVReinforce= cal_point.generate_ReinforcingRib_Long_Vertical()
    OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_ReinforceRib_V_L_UVReinforce) # 加强筋（长轴竖向）底部加强筋坐标点语句输出
    OutputList,SerialNumber_KeyPoint = generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoints[4],SerialNumber_KeyPoint,4) # 生成加强筋（长轴竖向）底部加强筋面语句输出
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[4]+40 # 修改全局变量，确定模块之间位置
    OutputList = OutputList + """! 创建新组件长轴纵向加强筋底部加强筋\nCM, JIAQIANGLEI, AREA\nASEL, NONE\n"""

    OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_ReinforcingRib_L_V) # 加强筋（长轴竖向）坐标点语句输出
    OutputList,SerialNumber_KeyPoint = generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoints[4]+40,SerialNumber_KeyPoint,4) # 生成加强筋（长轴竖向）面语句输出
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[5] # 修改全局变量，确定模块之间位置
    OutputList = OutputList + """! 创建新组件长轴纵向加强筋\n"""

    # 长轴横向加强筋建立
    KeyPointList_ReinforcingRib_L_H= cal_point.generate_ReinforcingRib_Long_Horizontal()
    OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_ReinforcingRib_L_H) # 加强筋（短轴横向）坐标点语句输出
    OutputList,SerialNumber_KeyPoint = generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoints[5],SerialNumber_KeyPoint,4) # 生成加强筋（短轴横向）面语句输出
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[6] # 修改全局变量，确定模块之间位置
    OutputList = OutputList + """! 创建新组件长轴横向加强筋\n"""

    # 短轴横向加强筋建立
    # KeyPointList_ReinforcingRib_S_H= cal_point.generate_ReinforcingRib_Short_Horizontal()

    # 短轴竖向加强筋建立
    KeyPointList_ReinforcingRib_S_V , KeyPointList_ReinforceRib_V_S_UVReinforce= cal_point.generate_ReinforcingRib_Short_Vertical()
    OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_ReinforcingRib_S_V) # 加强筋（短轴竖向）坐标点语句输出
    OutputList,SerialNumber_KeyPoint = generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoints[6],SerialNumber_KeyPoint,4) # 生成加强筋（短轴竖向）面语句输出
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[7]-12 # 修改全局变量，确定模块之间位置
    OutputList = OutputList + """! 创建新组件短轴纵向加强筋\n"""
    OutputList = OutputList + """! 创建新组件加强拱\nCM, JIAQIANGGONG, AREA\nASEL, NONE\n"""
    OutputList,SerialNumber_KeyPoint = KeyPoint(OutputList,SerialNumber_KeyPoint,KeyPointList_ReinforceRib_V_S_UVReinforce) # 加强筋（短轴竖向）坐标点语句输出
    OutputList,SerialNumber_KeyPoint = generate_ReinforcRib_BoxC_Area(OutputList,SerialNumber_KeyPoints[7]-12,SerialNumber_KeyPoint,4) # 生成加强筋（短轴竖向）面语句输出
    SerialNumber_KeyPoint = SerialNumber_KeyPoints[7] # 修改全局变量，确定模块之间位置
    OutputList = OutputList + """! 创建新组件短轴纵向加强筋底部加强筋\nCMSEL,A,JIAQIANGLEI\nCM, JIAQIANGLEI, AREA, APPEND\nASEL, NONE\n"""

    # 后处理
    OutputList = PostProcessing.post_processing(OutputList , data_table , 1 , 1)
    return OutputList
    # OutputList = OutputList + """\n/PSYMB,ADIR,1"""

    # print(data_table)
    # print(SerialNumber_KeyPoints)
    # print(OutputList)
    # print(SerialNumber_KeyPoints)
    # outputtxt(OutputList,"output.txt","output")
    # outputmac(OutputList,"D:/result/model","test2")
    
try:
    excel_file = r"C:\Users\pc\Downloads\油箱建模算单.xlsx"
    ReservedQuantity_OfModules = [2*2,2*2,10,12,20*7,20*5,6*7] # 模块预留数量
    # 设定提取范围参数
    data_table = table_extract(excel_file,"自动建模_导出xlsx","B2","C200")
    data_table_1 = table_extract(excel_file,"采样列表","C2","F5")
    variable_table = copy.deepcopy(data_table_1) # 自变量列表
    for i in variable_table:
        i = i[:1]
    variable_table_1 = [row[0] for row in variable_table]
    InputList = []
    for i in data_table_1:
        i.pop(0)
        row_list = []
        for j in range(int(i[2])):
            row_list.append(i[0]+(i[1]-i[0])/(int(i[2])-1)*j)
        InputList.append(row_list)
        
    # print(data_table_1)
    all_combinations = list(itertools.product(*InputList))
    # 存储所有新数组的列表
    all_new_arrays = []
    # 遍历替换数据中的每一行
    for row_index, replacement_row in enumerate(all_combinations):
        # 创建基础数组的深拷贝（避免修改原始数据）
        new_array = copy.deepcopy(data_table)
        
        # 遍历查找值数组中的每个值
        for value_index, lookup_value in enumerate(variable_table_1):
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
        # all_new_arrays.append(new_array)
        OutputList = oilbox_main(ReservedQuantity_OfModules,data_table,row_index)
        outputmac(OutputList,"D:/result/model","test"+f"{row_index}")
    print(f"完成全部mac文件输出共计{row_index+1}个")
except ValueError as e:
    print(f"发生错误: {e}") 