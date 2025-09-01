import math
import copy
from table_extraction import table_extract

class calculate_keypoint:
    # 将类名改为更明确描述功能的名称
    def __init__(self, data_table):
        # 1. 一次性提取所有数据项，避免重复提取
        self.data_dict = dict(data_table)
        
        # 2. 只在需要时提取属性，避免初始化无关变量
        self.length = float(self.data_dict["Box_Length"])
        self.width = float(self.data_dict["Box_Width"])
        self.height = float(self.data_dict["Box_Height"])
        self.structure = self.data_dict["Box_Structure"]
        self.BoxCover_Width = float(self.data_dict["BoxCover_Width"])
        self.BoxEdge_Width = float(self.data_dict["BoxEdge_Width"])
        
        # 3. 动态计算参数，避免重复定义
        self.x_coords = [
            -self.length/2,
            -self.length/2 + float(self.data_dict.get("Box_HorizontalLengthHypotenuse", 0)),
            self.length/2 - float(self.data_dict.get("Box_HorizontalLengthHypotenuse", 0)),
            self.length/2
        ]
        self.y_coords = [
            self.width/2,
            self.width/2 - float(self.data_dict.get("Box_VerticalLengthHypotenuse", 0)),
            -self.width/2 + float(self.data_dict.get("Box_VerticalLengthHypotenuse", 0)),
            -self.width/2
        ]

    def generate_box_points(self):
        """
        1:箱体坐标二维数组输出\n
        可输出结构：八边形、四边形\n
        最终输出变量：箱体三维坐标\n
        占用：0-16
        """
        # 4. 避免重复创建局部变量
        if self.structure == "八边形":
            # 八边形点序列: 按顺时针方向连接各点
            #          ——————
            #        /        \
            # 这个↗ |         |开始
            #        \        /
            #          ——————
            base_points = [
                [self.x_coords[0], self.y_coords[1]],
                [self.x_coords[1], self.y_coords[0]],
                [self.x_coords[2], self.y_coords[0]],
                [self.x_coords[3], self.y_coords[1]],
                [self.x_coords[3], self.y_coords[2]],
                [self.x_coords[2], self.y_coords[3]],
                [self.x_coords[1], self.y_coords[3]],
                [self.x_coords[0], self.y_coords[2]]
            ]
        elif self.structure == "四边形":
            # 四边形点序列: 左上、右上、右下、左下
            base_points = [
                [self.x_coords[0], self.y_coords[0]],
                [self.x_coords[3], self.y_coords[0]],
                [self.x_coords[3], self.y_coords[3]],
                [self.x_coords[0], self.y_coords[3]]
            ]
        else:
            raise ValueError(f"不支持的箱体结构: {self.structure}")

        # 5. 统一处理底部和顶部坐标
        bottom_points = [point + [0] for point in base_points]
        top_points = [point + [self.height] for point in base_points]
        
        return bottom_points + top_points
    
    def generate_boxcover_edge_keypoint(self):
        """
        2:箱沿坐标二维数组输出\n
        可输出结构：八边形、四边形\n
        最终输出变量：箱沿三维坐标\n
        占用：17-32
        """
        if self.structure == "八边形":
            k = (self.y_coords[1]-self.y_coords[0])/(self.x_coords[0]-self.x_coords[1])
            b = (self.x_coords[0]*self.y_coords[0]-self.x_coords[1]*self.y_coords[1])/(self.x_coords[0]-self.x_coords[1])
            b_plus = -(-b/k*math.sin(math.atan(k))-self.BoxCover_Width)/math.sin(math.atan(k))*k
            
            base_points = [
                [self.x_coords[0]-self.BoxCover_Width, (self.x_coords[0]-self.BoxCover_Width)*k+ b_plus ],
                [(self.y_coords[0]+self.BoxCover_Width- b_plus )/k, self.y_coords[0]+self.BoxCover_Width],
                [-(self.y_coords[0]+self.BoxCover_Width- b_plus )/k, self.y_coords[0]+self.BoxCover_Width],
                [self.x_coords[3]+self.BoxCover_Width, (self.x_coords[0]-self.BoxCover_Width)*k+ b_plus ],
                [self.x_coords[3]+self.BoxCover_Width, -((self.x_coords[0]-self.BoxCover_Width)*k+ b_plus )],
                [-(self.y_coords[0]+self.BoxCover_Width- b_plus )/k, self.y_coords[3]-self.BoxCover_Width],
                [(self.y_coords[0]+self.BoxCover_Width- b_plus )/k, self.y_coords[3]-self.BoxCover_Width],
                [self.x_coords[0]-self.BoxCover_Width, -((self.x_coords[0]-self.BoxCover_Width)*k+ b_plus )]
            ]
        elif self.structure == "四边形":
            # 四边形点序列: 左上、右上、右下、左下
            base_points = [
                [self.x_coords[0]-self.BoxCover_Width, self.y_coords[0]+self.BoxCover_Width],
                [self.x_coords[3]+self.BoxCover_Width, self.y_coords[0]+self.BoxCover_Width],
                [self.x_coords[3]+self.BoxCover_Width, self.y_coords[3]-self.BoxCover_Width],
                [self.x_coords[0]-self.BoxCover_Width, self.y_coords[3]-self.BoxCover_Width]
            ]
        else:
            raise ValueError(f"不支持的箱体结构: {self.structure}")
        
        # 处理底部坐标
        bottom_points = [point + [0] for point in base_points]
        
        # 箱底沿坐标输出
        if self.structure == "八边形":
            k = (self.y_coords[1]-self.y_coords[0])/(self.x_coords[0]-self.x_coords[1])
            b = (self.x_coords[0]*self.y_coords[0]-self.x_coords[1]*self.y_coords[1])/(self.x_coords[0]-self.x_coords[1])
            b_plus = -(-b/k*math.sin(math.atan(k))-self.BoxEdge_Width)/math.sin(math.atan(k))*k
            
            base_points = [
                [self.x_coords[0]-self.BoxEdge_Width, (self.x_coords[0]-self.BoxEdge_Width)*k+ b_plus ],
                [(self.y_coords[0]+self.BoxEdge_Width- b_plus )/k, self.y_coords[0]+self.BoxEdge_Width],
                [-(self.y_coords[0]+self.BoxEdge_Width- b_plus )/k, self.y_coords[0]+self.BoxEdge_Width],
                [self.x_coords[3]+self.BoxEdge_Width, (self.x_coords[0]-self.BoxEdge_Width)*k+ b_plus ],
                [self.x_coords[3]+self.BoxEdge_Width, -((self.x_coords[0]-self.BoxEdge_Width)*k+ b_plus )],
                [-(self.y_coords[0]+self.BoxEdge_Width- b_plus )/k, self.y_coords[3]-self.BoxEdge_Width],
                [(self.y_coords[0]+self.BoxEdge_Width- b_plus )/k, self.y_coords[3]-self.BoxEdge_Width],
                [self.x_coords[0]-self.BoxEdge_Width, -((self.x_coords[0]-self.BoxEdge_Width)*k+ b_plus )]
            ]
        elif self.structure == "四边形":
            # 四边形点序列: 左上、右上、右下、左下
            base_points = [
                [self.x_coords[0]-self.BoxEdge_Width, self.y_coords[0]+self.BoxEdge_Width],
                [self.x_coords[3]+self.BoxEdge_Width, self.y_coords[0]+self.BoxEdge_Width],
                [self.x_coords[3]+self.BoxEdge_Width, self.y_coords[3]-self.BoxEdge_Width],
                [self.x_coords[0]-self.BoxEdge_Width, self.y_coords[3]-self.BoxEdge_Width]
            ]
        else:
            raise ValueError(f"不支持的箱体结构: {self.structure}")
        
        # 处理底部坐标
        top_points = [point + [self.height] for point in base_points]
        
        return bottom_points + top_points
    
    def generate_ReinforcingRib_BoxCover_keypoint(self):
        """
        3:箱盖加强筋坐标二维数组输出\n
        可输出结构：八边形、四边形\n
        最终输出变量：箱盖加强筋三维坐标\n
        支持最大数量为10\n
        占用：33-72
        """
        # 竖直
        ReinforceRib_BoxC_V_D_LToL = float(self.data_dict["ReinforcingRib_BoxCover_Vertical_Distance_LeftToLeft"]) # 箱盖加强筋（竖直）左侧与箱体左侧距离
        ReinforceRib_BoxC_V_RelativeD = float(self.data_dict["ReinforcingRib_BoxCover_Vertical_RelativeDistance"]) # 箱盖加强筋（竖直）多个加强筋相对距离
        ReinforceRib_BoxC_V_H = float(self.data_dict["ReinforcingRib_BoxCover_Vertical_High"]) # 箱盖加强筋（竖直）高度
        rib_V_num = int(self.data_dict["ReinforcingRib_BoxCover_Vertical_Number"]) # 箱盖加强筋（竖直）数量
        # 斜
        ReinforceRib_BoxC_Ob_D_LToL = float(self.data_dict["ReinforcingRib_BoxCover_Oblique_Distance_LeftToLeft"]) # 箱盖加强筋（斜）左侧与箱体左侧距离
        ReinforceRib_BoxC_Ob_D_RToL = float(self.data_dict["ReinforcingRib_BoxCover_Oblique_Distance_RightToLeft"]) # 箱盖加强筋（斜）左侧与箱体左侧距离
        ReinforceRib_BoxC_Ob_RelativeD = float(self.data_dict["ReinforcingRib_BoxCover_Oblique_RelativeDistance"]) # 箱盖加强筋（斜）多个加强筋相对距离
        ReinforceRib_BoxC_Ob_H = float(self.data_dict["ReinforcingRib_BoxCover_Oblique_High"]) # 箱盖加强筋（斜）高度
        rib_Ob_num = int(self.data_dict["ReinforcingRib_BoxCover_Oblique_Number"]) # 箱盖加强筋（斜）数量
        
        # 加强筋坐标计算
        # X坐标
        x_points = []
        if rib_V_num != 1:
            for i in range(rib_V_num):
                x_points.append(-self.length/2+ReinforceRib_BoxC_V_D_LToL+ReinforceRib_BoxC_V_RelativeD*i)
        if rib_Ob_num != 1:
            for i in range(rib_Ob_num):
                x_points.append(-self.length/2+ReinforceRib_BoxC_Ob_D_LToL+ReinforceRib_BoxC_Ob_RelativeD*i)
            for i in range(rib_Ob_num):
                x_points.append(-self.length/2+ReinforceRib_BoxC_Ob_D_RToL+ReinforceRib_BoxC_Ob_RelativeD*i)
        # Y坐标
        y_points = [
            self.width/2,
            -self.width/2
        ]
        # Z坐标
        z_points = [
            self.height,
            self.height+ReinforceRib_BoxC_V_H,
            self.height+ReinforceRib_BoxC_Ob_H
        ]
        
        # 生成加强筋坐标
        base_points = [
            [y_points[0],z_points[0]],
            [y_points[1],z_points[0]],
            [y_points[1],z_points[1]],
            [y_points[0],z_points[1]]
        ]
        copy_points = copy.deepcopy(base_points)
        output_points = []
        x_points_num = int(len(x_points))
        print(x_points)
        print(x_points_num)
        # 输出竖直的坐标，j(竖直数量)*i(4)
        for j in range(int(rib_V_num)):
            for i in copy_points:
                i.insert(0, x_points[j])
            output_points = output_points + copy_points
            copy_points = copy.deepcopy(base_points)
        copy_points = copy.deepcopy(base_points)
        # 输出斜的坐标，j(斜数量)*index(4)
        for j in range(int(rib_Ob_num)):
            for index, value in enumerate(copy_points):
                if index == 0 or index == 3:
                    value.insert(0, x_points[j+rib_V_num])
                else:
                    value.insert(0, x_points[int(j+rib_V_num+rib_Ob_num)])
            output_points = output_points + copy_points
            copy_points = copy.deepcopy(base_points)

        return output_points , x_points , rib_V_num
    
    def generate_BoxCover_keypoint(self,R_B_X_Points,rib_V_num):
        """
        4:箱盖坐标二维数组输出\n
        可输出结构：八边形、四边形\n
        最终输出变量：箱盖三维坐标\n
        支持最大数量为11\n
        占用：73-120\n
        R_B_X_Points：箱盖加强筋X坐标点\n
        rib_V_num:箱盖竖直加强筋数量
        """
        # 箱盖斜加强筋数量
        rib_Ob_num = int((len(R_B_X_Points) - rib_V_num)/2)
        # 确定箱盖加强筋最左和最右的两根
        Left_X_Point_1, Left_X_Point_index = min((value, index) for index, value in enumerate(R_B_X_Points))
        Right_X_Point_1, Right_X_Point_index = max((value, index) for index, value in enumerate(R_B_X_Points))
        # 左右加强筋x坐标点
        if Left_X_Point_index < rib_V_num:
            Left_X_Point_2 = Left_X_Point_1
        else:
            Left_X_Point_2 = R_B_X_Points[Left_X_Point_index+rib_Ob_num]
        if Right_X_Point_index < rib_V_num:
            Right_X_Point_2 = Right_X_Point_1
        else:
            Right_X_Point_2 = R_B_X_Points[Right_X_Point_index+rib_Ob_num]
        # Y坐标
        y_points = [
            self.width/2,
            -self.width/2
        ]
        # Z坐标
        z_points = [
            self.height
        ]
        base_points = [
            [y_points[0], z_points[0]],
            [y_points[1], z_points[0]],
            [y_points[1], z_points[0]],
            [y_points[0], z_points[0]]
        ]
        output_points_4 = []
        if self.structure == "八边形":
        # 第一部分：生成两端六边形坐标点，均为逆时针
            output_points_6 = [
                [self.x_coords[0],self.y_coords[1], z_points[0]],
                [self.x_coords[0],self.y_coords[2], z_points[0]],
                [self.x_coords[1],self.y_coords[3], z_points[0]],
                [Left_X_Point_2,self.y_coords[3], z_points[0]],
                [Left_X_Point_1,self.y_coords[0], z_points[0]],
                [self.x_coords[1],self.y_coords[0], z_points[0]],
                [Right_X_Point_1,self.y_coords[0], z_points[0]],
                [Right_X_Point_2,self.y_coords[3], z_points[0]],
                [self.x_coords[2],self.y_coords[3], z_points[0]],
                [self.x_coords[3],self.y_coords[2], z_points[0]],
                [self.x_coords[3],self.y_coords[1], z_points[0]],
                [self.x_coords[2],self.y_coords[0], z_points[0]]
            ]
        elif self.structure == "四边形":
            output_points_4 = [
                [self.x_coords[0], self.y_coords[0], z_points[0]],
                [self.x_coords[0], self.y_coords[3], z_points[0]],
                [Left_X_Point_2, self.y_coords[3], z_points[0]],
                [Left_X_Point_1, self.y_coords[0], z_points[0]],
                [Right_X_Point_1, self.y_coords[0], z_points[0]],
                [Right_X_Point_2, self.y_coords[3], z_points[0]],
                [self.x_coords[3], self.y_coords[3], z_points[0]],
                [self.x_coords[3], self.y_coords[0], z_points[0]]
            ]
            
        # 第二部分：生成中间四边形坐标点，均为逆时针
        # 将R_B_X_Points排序，分为上下两部分
        R_B_X_Points_up =  R_B_X_Points[:rib_V_num+rib_Ob_num]
        R_B_X_Points_up.sort()
        R_B_X_Points_down = R_B_X_Points[:rib_V_num]+R_B_X_Points[rib_V_num+rib_Ob_num:]
        R_B_X_Points_down.sort()
        for j in range(int(rib_V_num+rib_Ob_num-1)):
            copy_points = copy.deepcopy(base_points)
            for index, value in enumerate(copy_points):
                if index == 0:
                    value.insert(0,R_B_X_Points_up[j])
                elif index == 1:
                    value.insert(0,R_B_X_Points_down[j])
                elif index == 2:
                    value.insert(0,R_B_X_Points_down[j+1])
                elif index == 3:
                    value.insert(0,R_B_X_Points_up[j+1])
            output_points_4 = output_points_4 + copy_points
            
        return output_points_6 , output_points_4

    def generate_ReinforcingRib_Long_Vertical(self):
        """
        5:箱盖纵向加强筋坐标二维数组输出\n
        可输出结构：八边形、四边形\n
        最终输出变量：箱盖纵向加强筋三维坐标\n
        支持最大数量为20*5\n
        占用：121-520
        """
        # 自变量提取
        # 高压侧
        ReinforceRib_L_V_Symmetry_H = self.data_dict["ReinforcingRib_Long_Vertical_Number_High"] # 加强筋（长轴竖向）是否对称（默认为对称，不对称时未高压侧）
        ReinforceRib_L_V_Number_High = int(self.data_dict["ReinforcingRib_Long_Vertical_Number_High"]) # 加强筋（长轴竖向）数量
        ReinforceRib_L_V_LOfTheTB_High = float(self.data_dict["ReinforcingRib_Long_Vertical_LengthOfTheTopBase_High"]) # 加强筋（长轴竖向）上底总长
        ReinforceRib_L_V_LOfTheDB_High = float(self.data_dict["ReinforcingRib_Long_Vertical_LengthOfTheDownBase_High"]) # 加强筋（长轴竖向）下底总长
        ReinforceRib_L_V_Width_High = float(self.data_dict["ReinforcingRib_Long_Vertical_Width_High"]) # 加强筋（长轴竖向）宽度
        ReinforceRib_L_V_D_BottomAEdge_High = float(self.data_dict["ReinforcingRib_Long_Vertical_Distance_BottomAndEdge_High"]) # 加强筋（长轴竖向）底部与箱沿距离
        ReinforceRib_L_V_D_LToL_High = float(self.data_dict["ReinforcingRib_Long_Vertical_Distance_LeftToLeft_High"]) # 加强筋（长轴竖向）左侧与箱体左侧距离
        ReinforceRib_L_V_RelativeD_High = float(self.data_dict["ReinforcingRib_Long_Vertical_RelativeDistance_High"]) # 加强筋（长轴竖向）多个加强筋相对距离
        ReinforceRib_L_V_High_FromTW_High = float(self.data_dict["ReinforcingRib_Long_Vertical_High_FromTankWall_High"]) # 加强筋（长轴竖向）高度
        # 低压侧
        ReinforceRib_L_V_Number_Low = int(self.data_dict["ReinforcingRib_Long_Vertical_Number_Low"]) # 加强筋（长轴竖向）数量
        ReinforceRib_L_V_LOfTheTB_Low = float(self.data_dict["ReinforcingRib_Long_Vertical_LengthOfTheTopBase_Low"]) # 加强筋（长轴竖向）上底总长
        ReinforceRib_L_V_LOfTheDB_Low = float(self.data_dict["ReinforcingRib_Long_Vertical_LengthOfTheDownBase_Low"]) # 加强筋（长轴竖向）下底总长
        ReinforceRib_L_V_Width_Low = float(self.data_dict["ReinforcingRib_Long_Vertical_Width_Low"]) # 加强筋（长轴竖向）宽度
        ReinforceRib_L_V_D_BottomAEdge_Low = float(self.data_dict["ReinforcingRib_Long_Vertical_Distance_BottomAndEdge_Low"]) # 加强筋（长轴竖向）底部与箱沿距离
        ReinforceRib_L_V_D_LToL_Low = float(self.data_dict["ReinforcingRib_Long_Vertical_Distance_LeftToLeft_Low"]) # 加强筋（长轴竖向）左侧与箱体左侧距离
        ReinforceRib_L_V_RelativeD_Low = float(self.data_dict["ReinforcingRib_Long_Vertical_RelativeDistance_Low"]) # 加强筋（长轴竖向）多个加强筋相对距离
        ReinforceRib_L_V_High_FromTW_Low = float(self.data_dict["ReinforcingRib_Long_Vertical_High_FromTankWall_Low"]) # 加强筋（长轴竖向）高度
        
        # 加强筋坐标计算
        # X坐标
        x_points = [
            self.x_coords[0]+ReinforceRib_L_V_D_LToL_High,
            self.x_coords[0]+ReinforceRib_L_V_D_LToL_High+ReinforceRib_L_V_Width_High,
            self.x_coords[0]+ReinforceRib_L_V_D_LToL_Low,
            self.x_coords[0]+ReinforceRib_L_V_D_LToL_Low+ReinforceRib_L_V_Width_Low,
        ]
        # Y坐标
        y_points = [
            self.y_coords[0],
            self.y_coords[0]+ReinforceRib_L_V_High_FromTW_High,
            self.y_coords[0],
            self.y_coords[0]+ReinforceRib_L_V_High_FromTW_Low,
        ]
        # Z坐标
        z_points = [
            ReinforceRib_L_V_D_BottomAEdge_High,
            ReinforceRib_L_V_D_BottomAEdge_High+ReinforceRib_L_V_LOfTheDB_High/2-ReinforceRib_L_V_LOfTheTB_High/2,
            ReinforceRib_L_V_D_BottomAEdge_High+ReinforceRib_L_V_LOfTheDB_High/2+ReinforceRib_L_V_LOfTheTB_High/2,
            ReinforceRib_L_V_D_BottomAEdge_High+ReinforceRib_L_V_LOfTheDB_High,
            ReinforceRib_L_V_D_BottomAEdge_Low,
            ReinforceRib_L_V_D_BottomAEdge_Low+ReinforceRib_L_V_LOfTheDB_Low/2-ReinforceRib_L_V_LOfTheTB_Low/2,
            ReinforceRib_L_V_D_BottomAEdge_Low+ReinforceRib_L_V_LOfTheDB_Low/2+ReinforceRib_L_V_LOfTheTB_Low/2,
            ReinforceRib_L_V_D_BottomAEdge_Low+ReinforceRib_L_V_LOfTheDB_Low,
        ]
        # 生成加强筋坐标
        base_points = [
            [x_points[0],y_points[0], z_points[3]],
            [x_points[0],y_points[1], z_points[2]],
            [x_points[0],y_points[1], z_points[1]],
            [x_points[0],y_points[0], z_points[0]],
            [x_points[1],y_points[0], z_points[3]],
            [x_points[1],y_points[1], z_points[2]],
            [x_points[1],y_points[1], z_points[1]],
            [x_points[1],y_points[0], z_points[0]],
            [x_points[0],y_points[1], z_points[2]],
            [x_points[1],y_points[1], z_points[2]],
            [x_points[1],y_points[1], z_points[1]],
            [x_points[0],y_points[1], z_points[1]],
            [x_points[0],y_points[1], z_points[1]],
            [x_points[1],y_points[1], z_points[1]],
            [x_points[1],y_points[0], z_points[0]],
            [x_points[0],y_points[0], z_points[0]],
            [x_points[0],y_points[1], z_points[2]],
            [x_points[1],y_points[1], z_points[2]],
            [x_points[1],y_points[0], z_points[3]],
            [x_points[0],y_points[0], z_points[3]],
        ]
        output_points = []
        # 输出高压侧坐标
        for j in range(int(ReinforceRib_L_V_Number_High)):
            copy_points = copy.deepcopy(base_points)
            for i in copy_points:
                i[0] = i[0] + ReinforceRib_L_V_RelativeD_High*j
            output_points = output_points + copy_points
        # 输出低压侧坐标
        # 根据是否对称输出不同低压侧坐标点
        if ReinforceRib_L_V_Symmetry_H == "是":
            copy_points = copy.deepcopy(output_points)
            for i in copy_points:
                i[1] = -i[1]
            output_points = output_points + copy_points
        elif ReinforceRib_L_V_Symmetry_H == "否":
            for j in range(int(ReinforceRib_L_V_Number_Low)):
                copy_points = copy.deepcopy(base_points)
                for i in copy_points:
                    i[0] = i[0] + ReinforceRib_L_V_RelativeD_Low*j
                    i[1] = -i[1]
                output_points = output_points + copy_points
        
        return output_points

if __name__ == "__main__":
    excel_file = r"C:\Users\pc\Downloads\油箱建模算单.xlsx"
    data_table = table_extract(excel_file)
    # data_table = [
    #     ['Box_Structure', '八边形'],
    #     ['Box_Length', '5000'], 
    #     ['Box_Width', '2000'],
    #     ['Box_Height', '3000'],
    #     ['Box_VerticalLengthHypotenuse', '500'],
    #     ['Box_HorizontalLengthHypotenuse', '500'],
    #     ['ReinforcingRib_BoxCover_Vertical_Distance_LeftToLeft', '3107'],
    #     ['ReinforcingRib_BoxCover_Vertical_RelativeDistance', '500'],
    #     ['ReinforcingRib_BoxCover_Vertical_High', '200'],
    #     ['ReinforcingRib_BoxCover_Vertical_Number', '3'],
    #     ['BoxCover_Width', '200']
    # ]
    calculator = calculate_keypoint(data_table)
    points_3d = calculator.generate_box_points()
    points_boxcover = calculator.generate_boxcover_edge_keypoint()
    points_ReinforcingRib_BoxC_V = calculator.generate_ReinforcingRib_BoxCover_keypoint()
    # print(points_3d)
    # print(points_boxcover)
    print(points_ReinforcingRib_BoxC_V)