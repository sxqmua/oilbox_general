import math
import copy

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
    
    def generate_boxcover_upround_keypoint(self):
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
    
    def generate_ReinforcingRib_BoxCover_Vertical_keypoint(self):
        """
        3:箱盖加强筋坐标二维数组输出\n
        可输出结构：八边形、四边形\n
        最终输出变量：箱盖加强筋三维坐标\n
        支持最大数量为8\n
        占用：33-64
        """
        ReinforceRib_BoxC_V_D_LToL = float(self.data_dict["ReinforcingRib_BoxCover_Vertical_Distance_LeftToLeft"]) # 箱盖加强筋（竖直）左侧与箱体左侧距离
        ReinforceRib_BoxC_V_RelativeD = float(self.data_dict["ReinforcingRib_BoxCover_Vertical_RelativeDistance"]) # 箱盖加强筋（竖直）多个加强筋相对距离
        ReinforceRib_BoxC_V_H = float(self.data_dict["ReinforcingRib_BoxCover_Vertical_High"]) # 箱盖加强筋（竖直）高度
        rib_num = int(self.data_dict["ReinforcingRib_BoxCover_Vertical_Number"]) # 箱盖加强筋（竖直）数量
        
        # 加强筋坐标计算
        x_points = []
        if rib_num != 1:
            for i in range(rib_num):
                x_points.append(-self.length/2+ReinforceRib_BoxC_V_D_LToL+ReinforceRib_BoxC_V_RelativeD*i)
        y_points = [
            self.width/2,
            -self.width/2
        ]
        z_points = [
            self.height,
            self.height+ReinforceRib_BoxC_V_H
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
        for j in range(len(x_points)):
            for i in copy_points:
                i.insert(0, x_points[j])
            output_points = output_points + copy_points
            copy_points = copy.deepcopy(base_points)

        return output_points
    
    def KeyPoint(KeyPointList, num):
        """
        
        """

if __name__ == "__main__":
    data_table = [
        ['Box_Structure', '八边形'],
        ['Box_Length', '5000'], 
        ['Box_Width', '2000'],
        ['Box_Height', '3000'],
        ['Box_VerticalLengthHypotenuse', '500'],
        ['Box_HorizontalLengthHypotenuse', '500'],
        ['ReinforcingRib_BoxCover_Vertical_Distance_LeftToLeft', '3107'],
        ['ReinforcingRib_BoxCover_Vertical_RelativeDistance', '500'],
        ['ReinforcingRib_BoxCover_Vertical_High', '200'],
        ['ReinforcingRib_BoxCover_Vertical_Number', '3'],
        ['BoxCover_Width', '200']
    ]
    calculator = calculate_keypoint(data_table)
    points_3d = calculator.generate_box_points()
    points_boxcover = calculator.generate_boxcover_upround_keypoint()
    points_ReinforcingRib_BoxC_V = calculator.generate_ReinforcingRib_BoxCover_Vertical_keypoint()
    # print(points_3d)
    # print(points_boxcover)
    print(points_ReinforcingRib_BoxC_V)