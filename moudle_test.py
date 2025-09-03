import itertools
import os
import tkinter as tk
from tkinter import filedialog
import copy
from openpyxl import load_workbook
from table_extraction import table_extract
from calculate_keypoint import calculate_keypoint
from output import outputtxt

def KeyPoint(INputDataList):
    """点语句输出\n
    可输出结构：八边形、四边形\n
    INputDataList:三维点坐标List
    """
    global SerialNumber_KeyPoint
    global OutputList
    num_point = len(INputDataList)
    for i in range(num_point):
        KeyPoints = f"K , {SerialNumber_KeyPoint} , {INputDataList[i][0]} , {INputDataList[i][1]} , {INputDataList[i][2]}"
        OutputList = OutputList + KeyPoints + "\n"
        SerialNumber_KeyPoint += 1
    # return 

def generate_box_area(Box_Structure):
    """箱体面语句输出\n
    可输出结构：八边形、四边形\n
    Box_Structure:箱体结构"""
    global SerialNumber_KeyPoint
    global SerialNumber_KeyPoints
    global OutputList
    if Box_Structure == "八边形":
        OutputList = OutputList + """A , 9 , 10 , 2 , 1\nA , 10 , 11 , 3 , 2\nA , 11 , 12 , 4 , 3
A , 12 , 13 , 5 , 4\nA , 13 , 14 , 6 , 5\nA , 14 , 15 , 7 , 6
A , 15 , 16 , 8 , 7\nA , 16 , 9 , 1 , 8\n"""
    elif Box_Structure == "四边形":
        OutputList = OutputList + """A , 5 , 6 , 2 , 1\nA , 6 , 7 , 3 , 2\nA , 7 , 8 , 4 , 3\nA , 8 , 5 , 1 , 4\n"""
    else:
        raise ValueError(f"不支持的箱体结构: {Box_Structure}")
    OutputList = OutputList + """ASEL, ALL\n! 创建新组件侧壁\nCM, CEBI, AREA\nASEL, NONE\n"""

def generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoint_in,SerialNumber_KeyPoint,side_num):
    """箱盖加强筋面语句输出\n
    可输出结构：八边形、四边形\n
    num_module:模块序号
    SerialNumber_KeyPoint：SerialNumber_KeyPoint
    """
    global OutputList
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
    return SerialNumber_KeyPoint
    

# 定义模板初始段
OutputList = """FINISH              ! 结束当前模块 xin
/CLEAR , START       ! 清除数据库，开始新的分析
!========== 定义参数 (Preprocessor) ==========
str = '%z%h=%h%T1=%T1%T2=%T2%'
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
excel_file = r"C:\Users\pc\Downloads\油箱建模算单.xlsx"
ReservedQuantity_OfModules = [2*2,2*2,10,12,20*5,20*5,6*5] # 模块预留数量
SerialNumber_KeyPoints = [1]
for i in range(len(ReservedQuantity_OfModules)):
    SerialNumber_KeyPoints.append(ReservedQuantity_OfModules[i]*4 + SerialNumber_KeyPoints[i])
SerialNumber_KeyPoint = SerialNumber_KeyPoints[0] # 全局变量，确定模块之间位置

# 2. 提取参数
data_table = table_extract(excel_file)
data_dict = dict(data_table) # 字典转化

# 3. 计算坐标

cal_point = calculate_keypoint(data_table) # 加载计算模块
SerialNumber_KeyPoint = SerialNumber_KeyPoints[4]

# 长轴纵向加强筋建立
KeyPointList_ReinforcingRib_L_V= cal_point.generate_ReinforcingRib_Long_Vertical()
KeyPoint(KeyPointList_ReinforcingRib_L_V) # 加强筋（长轴竖向）坐标点语句输出
generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[4],SerialNumber_KeyPoint,4) # 生成加强筋（长轴竖向）面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[5] # 修改全局变量，确定模块之间位置
OutputList = OutputList + """! 创建新组件长轴纵向加强筋\n"""


OutputList = OutputList + """! 创建新组件加强筋\nCM, JIAQIANGGONG, AREA\nASEL, NONE\n"""
OutputList = OutputList + """\nASEL, ALL\nAPLOT\n/PSYMB,ADIR,1"""

# print(data_table)
# print(SerialNumber_KeyPoints)
print(OutputList)
print(SerialNumber_KeyPoints)
outputtxt(OutputList,"output_test.txt","output")