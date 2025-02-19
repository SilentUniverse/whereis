import pandas as pd
import json

def json_to_excel(json_file, excel_file):
    """
    将 JSON 文件中 '住宅信息' 转换为 Excel 文件
    
    :param json_file: 输入的 JSON 文件路径
    :param excel_file: 输出的 Excel 文件路径
    """
    try:
        # 读取 JSON 文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取 "qualified_residences" 中的 "住宅信息"
        residences = data.get("qualified_residences", [])
        housing_info = [residence.get("住宅信息", {}) for residence in residences]
        
        # 转换为 DataFrame
        df = pd.DataFrame(housing_info)
        
        # 将 DataFrame 保存为 Excel 文件
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"成功将 {json_file} 中的 '住宅信息' 转换为 {excel_file}")
    
    except Exception as e:
        print(f"发生错误：{e}")

# 示例用法
json_file_path = "data2.json"  # 替换为你的 JSON 文件路径
excel_file_path = "output2.xlsx"  # 替换为你希望保存的 Excel 文件路径
json_to_excel(json_file_path, excel_file_path)