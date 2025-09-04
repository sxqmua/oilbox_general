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
    

# 1. 定义参数
excel_file = r"C:\Users\pc\Downloads\油箱建模算单.xlsx"
ReservedQuantity_OfModules = [2*2,2*2,10,12,20*7,20*5,6*7] # 模块预留数量
SerialNumber_KeyPoints = [1]
for i in range(len(ReservedQuantity_OfModules)):
    SerialNumber_KeyPoints.append(ReservedQuantity_OfModules[i]*4 + SerialNumber_KeyPoints[i])
SerialNumber_KeyPoint = SerialNumber_KeyPoints[0] # 全局变量，确定模块之间位置

# 2. 提取参数
data_table = table_extract(excel_file)
data_dict = dict(data_table) # 字典转化

# 定义模板初始段
OutputList = f"""FINISH              ! 结束当前模块 xin
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
KeyPoint(KeyPointList_TankWall) # 箱体坐标点语句输出
generate_box_area(data_dict["Box_Structure"]) # 生成箱体面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[1] # 修改全局变量，确定模块之间位置
# 箱盖沿坐标输出
KeyPointList_BoxCover = cal_point.generate_boxcover_edge_keypoint() 
KeyPoint(KeyPointList_BoxCover) # 箱盖沿坐标点语句输出
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
KeyPoint(KeyPointList_ReinforcingRib_BoxC) # 箱盖加强筋坐标点语句输出
generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[2],SerialNumber_KeyPoint,4) # 生成箱盖加强筋面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[3] # 修改全局变量，确定模块之间位置
OutputList = OutputList + """! 创建新组件箱盖加强筋\nCM, XDJIAQIANGJIN, AREA\nASEL, NONE\n"""

# 箱盖分区建立
KeyPointList_BoxC_6 , KeyPointList_BoxC_4 = cal_point.generate_BoxCover_keypoint(X_KeyPointList_ReinforcingRib_BoxC,rib_V_num)
if data_dict["Box_Structure"] == "八边形":
    KeyPoint(KeyPointList_BoxC_6)
    generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[3],SerialNumber_KeyPoint,6) # 生成箱盖加强筋面语句输出
    KeyPoint(KeyPointList_BoxC_4)
    generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[3]+12,SerialNumber_KeyPoint,4) # 生成箱盖加强筋面语句输出
elif data_dict["Box_Structure"] == "四边形":
    KeyPoint(KeyPointList_BoxC_4)
    generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[3],SerialNumber_KeyPoint,4) # 生成箱盖加强筋面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[4] # 修改全局变量，确定模块之间位置
OutputList = OutputList + """! 创建新组件箱盖\nCM, TOP, AREA\nASEL, NONE\n"""

# 长轴纵向加强筋建立
KeyPointList_ReinforcingRib_L_V , KeyPointList_ReinforceRib_V_L_UVReinforce= cal_point.generate_ReinforcingRib_Long_Vertical()
KeyPoint(KeyPointList_ReinforceRib_V_L_UVReinforce) # 加强筋（长轴竖向）底部加强筋坐标点语句输出
generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[4],SerialNumber_KeyPoint,4) # 生成加强筋（长轴竖向）底部加强筋面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[4]+40 # 修改全局变量，确定模块之间位置
OutputList = OutputList + """! 创建新组件长轴纵向加强筋底部加强筋\nCM, JIAQIANGLEI, AREA\nASEL, NONE\n"""

KeyPoint(KeyPointList_ReinforcingRib_L_V) # 加强筋（长轴竖向）坐标点语句输出
generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[4]+40,SerialNumber_KeyPoint,4) # 生成加强筋（长轴竖向）面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[5] # 修改全局变量，确定模块之间位置
OutputList = OutputList + """! 创建新组件长轴纵向加强筋\n"""

# 长轴横向加强筋建立
KeyPointList_ReinforcingRib_L_H= cal_point.generate_ReinforcingRib_Long_Horizontal()
KeyPoint(KeyPointList_ReinforcingRib_L_H) # 加强筋（短轴横向）坐标点语句输出
generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[5],SerialNumber_KeyPoint,4) # 生成加强筋（短轴横向）面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[6] # 修改全局变量，确定模块之间位置
OutputList = OutputList + """! 创建新组件长轴横向加强筋\n"""

# 短轴横向加强筋建立
# KeyPointList_ReinforcingRib_S_H= cal_point.generate_ReinforcingRib_Short_Horizontal()

# 短轴竖向加强筋建立
KeyPointList_ReinforcingRib_S_V , KeyPointList_ReinforceRib_V_S_UVReinforce= cal_point.generate_ReinforcingRib_Short_Vertical()
KeyPoint(KeyPointList_ReinforcingRib_S_V) # 加强筋（短轴竖向）坐标点语句输出
generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[6],SerialNumber_KeyPoint,4) # 生成加强筋（短轴竖向）面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[7]-12 # 修改全局变量，确定模块之间位置
OutputList = OutputList + """! 创建新组件短轴纵向加强筋\n"""
OutputList = OutputList + """! 创建新组件加强拱\nCM, JIAQIANGGONG, AREA\nASEL, NONE\n"""
KeyPoint(KeyPointList_ReinforceRib_V_S_UVReinforce) # 加强筋（短轴竖向）坐标点语句输出
generate_ReinforcRib_BoxC_Area(SerialNumber_KeyPoints[7]-12,SerialNumber_KeyPoint,4) # 生成加强筋（短轴竖向）面语句输出
SerialNumber_KeyPoint = SerialNumber_KeyPoints[7] # 修改全局变量，确定模块之间位置
OutputList = OutputList + """! 创建新组件短轴纵向加强筋底部加强筋\nCMSEL,A,JIAQIANGLEI\nCM, JIAQIANGLEI, AREA, APPEND\nASEL, NONE\n"""

OutputList = OutputList + f"""
! ========== 分配属性 ==========
! 箱盖
CMSEL, S, TOP
TYPE, 1
MAT, 1
REAL, 1
! 箱顶沿
CMSEL, S, TOP_RIM
TYPE, 1
MAT, 1
REAL, 2
! 箱底沿
CMSEL, S, BOTTOM_RIM
TYPE, 1
MAT, 1
REAL, 2
! 侧壁
CMSEL, S, CEBI
TYPE, 1
MAT, 1
REAL, 3
! 加强拱
CMSEL, S, JIAQIANGGONG
TYPE, 1
MAT, 1
REAL, 4
! 箱盖加强筋
CMSEL, S, XDJIAQIANGJIN
TYPE, 1
MAT, 1
REAL, 5
! 纵向加强拱下加强筋
CMSEL, S, JIAQIANGLEI
TYPE, 1
MAT, 1
REAL, 6
! 线面粘合
ASEL, ALL
AOVLAP, ALL
! 将侧壁面选择为一个组件
ASEL, NONE
ASEL, S, LOC, Y, {data_dict["Box_Width"]/2}  ! 选择Y=Box_Width/2的面
ASEL, A, LOC, Y, -{data_dict["Box_Width"]/2}  ! 选择Y=-Box_Width/2的面
ASEL, A, LOC, X, {data_dict["Box_Length"]/2}  ! 选择Y=Box_Length/2的面
ASEL, A, LOC, X, -{data_dict["Box_Length"]/2}  ! 选择Y=-Box_Length/2的面
CM, CEBI, AREA, APPEND 
! 将顶面选择为一个组件
ASEL, NONE
ASEL, S, LOC, Z, {data_dict["Box_Height"]}  ! 选择Z=Box_Height的面
CM, TOP, AREA, APPEND 
ASEL, ALL\nAPLOT\n/PNUM,AREA,1
! 设置网格参数
MSHAPE, 0, 2D     ! 首选四边形
MSHKEY, 0         ! 自由网格
ESIZE, {data_dict["ESIZE"]}           ! 设置单元尺寸
AMESH, ALL        ! 划分网格
! 完成所有网格划分
ASEL, ALL         ! 选择所有实体

! ============ 求解 ============
/SOLU

! 1. 施加约束 (使用节点组件)
! 选择Y=0平面上所有边并施加约束
LSEL,S,LOC,Z,0 
DL,ALL,,ALL                     ! 约束所有边上的所有自由度(123=UX,UY,UZ)


! 2. 施加压力 (0.1 MPa)

SF, CEBI, PRES, 0.1  ! 对节点组件施加0.1 MPa压力
SF, TOP, PRES, 0.1  ! 对节点组件施加0.1 MPa压力
! 3. 求解设置
! 2. 激活大挠曲选项
NLGEOM, ON        ! 关键命令：启用大挠曲

! 3. 设置分析类型
ANTYPE, STATIC    ! 静态分析（最常用）

! 4. 配置非线性求解选项
NROPT, AUTO       ! 自动选择牛顿-拉普森选项
AUTOTS, ON        ! 自动时间步长
TIME, 1           ! 总时间（伪时间）
NSUBST, 20, 100, 50 ! 子步设置(初始,最大,最小)
CNVTOL, F, , 0.05, 2 ! 力收敛容差(5%)
CNVTOL, U, , 0.05, 2    ! 位移收敛5%
ANTYPE, STATIC      ! 静态分析
OUTRES, ALL, NONE     ! 关闭所有结果输出
OUTRES,NSOL,LAST     ! 节点位移
OUTRES,STRS,LAST

SOLVE               ! 开始求解

! ============ 后处理输出云图 ============
/POST1
SET, LAST 
/SHOW, JPEG, , 0         ! 设置输出为 JPEG 格式
/GFILE, 1200             ! 设置图像质量（1200 像素）
 /VIEW, 1, 1, 1, 1   ! 等轴测视图（1,1,1方向）
PLNSOL, U, SUM           ! 此时会保存图像
PLESOL, S, EQV
/SHOW, CLOSE             ! 关闭文件输出


CDWRITE, 'ALL', str, 'cdb',

"""
OutputList = OutputList + """\nASEL, ALL\nAPLOT\n/PNUM,AREA,1"""
# OutputList = OutputList + """\n/PSYMB,ADIR,1"""

# print(data_table)
# print(SerialNumber_KeyPoints)
print(OutputList)
print(SerialNumber_KeyPoints)
outputtxt(OutputList,"output.txt","output")