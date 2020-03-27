# encoding:utf-8
# FileName: main
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/3/27 16:09
# Description: 

import pandas as pd
import numpy as np

# 显示所有列
from explore_data import explore_area
from preprocess_data import preprocess_data
from read_data import read_data
from view_data import view_data

pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)


if __name__ == '__main__':
    # 为避免我们频繁的读取数据库，可将数据保存到本地文件
    df_data = read_data()

    """数据预处理"""
    df_data = preprocess_data(df_data)

    """可视化分析"""
    df_data = view_data(df_data)

    """热力图探索"""
    explore_area(df_data)