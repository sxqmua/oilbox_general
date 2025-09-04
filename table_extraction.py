from openpyxl import load_workbook

def table_extract(excel_file):
    
    sheet_name = "自动建模_导出xlsx"
    start_cell = "B2"
    end_cell = "C200"
    try:
        # 2. 加载工作簿
        wb = load_workbook(excel_file, data_only=True)
        
        # 3. 获取工作表
        if sheet_name not in wb.sheetnames:
            print(f"错误: 工作簿中不存在工作表 '{sheet_name}'")
            print(f"可选工作表: {', '.join(wb.sheetnames)}")
            exit(1)
        
        sheet = wb[sheet_name]
        
        # 4. 解析起始和结束单元格的行列号
        # 将"B2"转换为行号2，列号2（B是第2列）
        start_col = ord(start_cell[0]) - 64  # 'A'=65, 所以65-64=1
        start_row = int(start_cell[1:])
        
        end_col = ord(end_cell[0]) - 64
        end_row = int(end_cell[1:])
        
        # 5. 提取数据到二维数组
        data_table = []
        
        # 使用iter_rows正确遍历区域
        for row in sheet.iter_rows(min_row=start_row, max_row=end_row,
                                min_col=start_col, max_col=end_col,
                                values_only=True):
            row_data = []
            for cell in row:
                value = cell
                if value is None:
                    value = ""
                elif value == "": 
                    value = "<显式空白>"
                elif isinstance(value, str) and value.strip() == "": 
                    value = "<全空格>"
                row_data.append(value)
            
            data_table.append(row_data)
        
        # # 打印读取的数据
        print(f"成功读取 {len(data_table)} 行数据:")
        # for i, row in enumerate(data_table):
        #     print(f"行 {i+1}: {row}")

    except FileNotFoundError:
        print(f"错误: 文件 '{excel_file}' 未找到")
        print("请检查文件路径是否正确，并确保文件存在")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        print("请检查: 1) 文件格式 2) 是否被其他程序占用 3) 文件内容")

    finally:
        if 'wb' in locals():
            wb.close()
    
    return data_table
