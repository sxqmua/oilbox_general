import itertools
import os
import tkinter as tk
from tkinter import filedialog
import copy
from openpyxl import load_workbook
from table_extraction import table_extract
from calculate_keypoint import calculate_keypoint
from output import outputtxt

def KeyPoint(INputDataList,num_point):
    global SerialNumber_KeyPoint
    global OutputList
    for i in range(num_point):
        KeyPoints = f"K , {SerialNumber_KeyPoint} , {INputDataList[i][0]} , {INputDataList[i][1]} , {INputDataList[i][2]}"
        OutputList = OutputList + KeyPoints + "\n"
        SerialNumber_KeyPoint += 1
    # return 

def generate_box_area(Box_Structure):
    global SerialNumber_KeyPoint
    global SerialNumber_KeyPoints
    global OutputList
    if Box_Structure == "八边形":
        OutputList = OutputList + """A,9,10,2,1\nA,10,11,3,2\nA,11,12,4,3
A,12,13,5,4\nA,13,14,6,5\nA,14,15,7,6
A,15,16,8,7\nA,16,9,1,8\n"""
    elif Box_Structure == "四边形":
        OutputList = OutputList + """A,A,9,10,2,1\nA,10,11,3,2\nA,11,12,4,3\nA,12,9,1,4\n"""
    else:
        raise ValueError(f"不支持的箱体结构: {Box_Structure}")
    OutputList = OutputList + """ASEL, ALL\n! 创建新组件侧壁\nCM, CEBI, AREA\nASEL, NONE\n"""

def generate_ReinforcRib_BoxC_V_Area(num_module):
    """箱盖加强筋面语句输出\n
    可输出结构：八边形、四边形\n"""
    global SerialNumber_KeyPoint
    global SerialNumber_KeyPoints
    global OutputList
    num_module -= 1 # 模块编号从0开始
    SerialNumber_KeyPoint_in = SerialNumber_KeyPoints[num_module]
    # print((SerialNumber_KeyPoint-SerialNumber_KeyPoints[num_module])/4)
    for i in range(int((SerialNumber_KeyPoint-SerialNumber_KeyPoints[num_module])/4)):
        Area_Basic = "A ,"
        Area_Add = "{Knums}"
        Knums = []
        for j in range(4):
            Knums.append(SerialNumber_KeyPoint_in + j)
        Area_Add = Area_Add.format(Knums=','.join(map(str, Knums)))
        Area_Basic = Area_Basic + Area_Add
        OutputList = OutputList + Area_Basic + "\n"
        SerialNumber_KeyPoint_in += 4
    OutputList = OutputList + """ASEL, ALL\n! 创建新组件箱盖加强筋
CMSEL, S, CEBI\nCMSEL, A, TOP_RIM\nCMSEL, A, BOTTOM_RIM
ASEL, INVE\nCM, XDJIAQIANGJINs, AREA\nASEL, NONE\n"""
    # return
    

# 定义模板初始段
OutputList = """FINISH              ! 结束当前模块 xin
/CLEAR, START       ! 清除数据库，开始新的分析
!========== 定义参数 (Preprocessor) ==========
str='%z%h=%h%T1=%T1%T2=%T2%'
! ===== 1. 设置工作目录和文件名 =====
/MKDIR, 'D:/result/z =%z% h=%h% T1=%T1% T2=%T2%'     ! 创建项目目录（如不存在）
/CWD,'D:/result/z =%z% h=%h% T1=%T1% T2=%T2%'        ! 设置工作目录
/FILNAME,str, 1     ! 设置文件名前缀
! ========== 前处理 (Preprocessor) ==========
/PREP7              ! 进入前处理器
! 1. 定义材料属性 (钢)
MP, EX, 1, 210000   ! 杨氏模量 (Pa)
MP, PRXY, 1, 0.3    ! 泊松比
MP, DENS, 1, 7.85e-9   ! 密度 (kg/m³)

! 2. 定义单元类型 (壳单元SHELL181)
ET, 1, SHELL181     ! 选择壳单元类型
KEYOPT, 1, 8, 2     ! 设置存储应力和应变
"""

# 1. 定义参数
excel_file = r"C:\Users\zengqingbo\Downloads\油箱建模算单.xlsx"
ReservedQuantity_OfModules = [2*2,2*2,8] # 模块预留数量
SerialNumber_KeyPoints = [1]
for i in range(len(ReservedQuantity_OfModules)):
    SerialNumber_KeyPoints.append(ReservedQuantity_OfModules[i]*4 + SerialNumber_KeyPoints[i])
SerialNumber_KeyPoint = SerialNumber_KeyPoints[0] # 全局变量，确定模块之间位置

# 2. 提取参数
data_table = table_extract(excel_file)
data_dict = dict(data_table) # 字典转化

# 3. 计算坐标
# 3.1. 箱体
cal_point = calculate_keypoint(data_table) # 加载计算模块
# 箱体坐标输出
KeyPointList_TankWall = cal_point.generate_box_points() 
KeyPoint(KeyPointList_TankWall,len(KeyPointList_TankWall)) # 箱体坐标点语句输出
generate_box_area(data_dict["Box_Structure"]) # 生成箱体面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[1] # 修改全局变量，确定模块之间位置
# 箱盖沿坐标输出
KeyPointList_BoxCover = cal_point.generate_boxcover_upround_keypoint() 
KeyPoint(KeyPointList_BoxCover,len(KeyPointList_BoxCover)) # 箱盖沿坐标点语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[2] # 修改全局变量，确定模块之间位置


if data_dict["Box_Structure"] == "八边形":
    OutputList = OutputList + """A, 1, 2, 3, 4, 5, 6, 7, 8\nBOTTOM_AREA = _RETURN
A, 17,18,19,20,21,22,23,24\nRIM_AREA = _RETURN\nASBA, RIM_AREA, BOTTOM_AREA
! 创建新组件箱底沿\nCM, BOTTOM_RIM, AREA\nASEL, NONE\nA, 16,15,14,13,12,11,10,9\nUP_AREA = _RETURN
A, 32,31,30,29,28,27,26,25\nUP_RIM_AREA = _RETURN\nASBA, UP_RIM_AREA, UP_AREA
! 创建新组件箱盖沿\nCM, TOP_RIM, AREA\nASEL, NONE
"""
elif data_dict["Box_Structure"] == "四边形":
    OutputList = OutputList + """A, 1, 2, 3, 4\nBOTTOM_AREA = _RETURN
A, 17,18,19,20\nRIM_AREA = _RETURN\nASBA, RIM_AREA, BOTTOM_AREA
! 创建新组件箱底沿\nCM, BOTTOM_RIM, AREA\nASEL, NONE\nA, 12,11,10,9\nUP_AREA = _RETURN
A, 28,27,26,25\nUP_RIM_AREA = _RETURN\nASBA, UP_RIM_AREA, UP_AREA
! 创建新组件箱盖沿\nCM, TOP_RIM, AREA\nASEL, NONE
"""

# 箱盖加强筋坐标输出
KeyPointList_ReinforcingRib_BoxC_V = cal_point.generate_ReinforcingRib_BoxCover_Vertical_keypoint() 
KeyPoint(KeyPointList_ReinforcingRib_BoxC_V,len(KeyPointList_ReinforcingRib_BoxC_V)) # 箱盖加强筋坐标点语句输出
generate_ReinforcRib_BoxC_V_Area(3) # 生成箱盖加强筋面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[3] # 修改全局变量，确定模块之间位置

# 

# print(data_table)
# print(SerialNumber_KeyPoints)
print(OutputList)
outputtxt(OutputList,"output.txt","output")