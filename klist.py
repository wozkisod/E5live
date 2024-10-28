def sort_data(data_list, ascending=True):
    """
    排序数据列表。
    
    参数:
    - data_list (list): 待排序的列表。
    - ascending (bool): 是否为升序排序，默认为 True。设置为 False 将降序排列。
    
    返回:
    - list: 排序后的数据列表。
    """
    # 检查是否是列表
    if not isinstance(data_list, list):
        raise TypeError("输入的数据必须是列表")
    
    # 排序列表
    sorted_list = sorted(data_list, reverse=not ascending)
    
    return sorted_list

# 测试数据列表
data = [34, 7, 23, 32, 5, 62]

# 调用函数进行升序排序
sorted_data_ascending = sort_data(data, ascending=True)
print("升序排序结果:", sorted_data_ascending)

# 调用函数进行降序排序
sorted_data_descending = sort_data(data, ascending=False)
print("降序排序结果:", sorted_data_descending)
