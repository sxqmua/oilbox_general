class PostProcessing():    
    
    def post_processing( InputList , data_table , grid = 1 , solve = 1):
        data_dict = dict(data_table)
        # 后处理
        OutputList = InputList + f"""
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
"""
        # 是否网格划分
        if grid == 1:
            OutputList = OutputList + f"""
ASEL,ALL
! 设置网格参数
MSHAPE, 0, 2D     ! 首选四边形
MSHKEY, 0         ! 自由网格
ESIZE, {data_dict["ESIZE"]}           ! 设置单元尺寸
AMESH, ALL        ! 划分网格
! 完成所有网格划分
ASEL, ALL         ! 选择所有实体
"""
        # 是否求解
        if solve == 1:
            OutputList = OutputList + f"""
! ============ 求解 ============
/SOLU

! 1. 施加约束 (使用节点组件)
! 选择Z=0平面上所有边并施加约束
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
/exit, ALL
"""

#         OutputList = OutputList + """
# ASEL, ALL\nAPLOT\n/PNUM,AREA,1
# """
        return OutputList