class modeling:
    def __init__(self, data_table):
        # 1. 一次性提取所有数据项，避免重复提取
        self.data_dict = dict(data_table)
        
        # 2. 只在需要时提取属性，避免初始化无关变量
        self.structure = self.data_dict["Box_Structure"]