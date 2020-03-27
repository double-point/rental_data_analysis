# encoding:utf-8
# FileName: explore_data
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/3/26 22:36
# Description: 对探索问题进行分析

import pandas as pd
import numpy as np

# 显示所有列
from tools import data_to_json

pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)


def save_result(df_data, station, area, type, max_price):
    """
    通过热力图探索数据
    @param df_data:
    @param station:
    @param area:
    @param type:
    @param max_price:
    @return:
    """
    # 筛选数据
    df_data_area = df_data.loc[(df_data.area.isin(area)) &
                               (df_data.house_rental_method == type) &
                               (df_data.house_rental_price < max_price),
                               ['house_rental_price', 'house_rental_area', 'house_longitude', 'house_latitude']]

    # 计算每平米的房屋价值当做权重
    df_data_area['weight'] = 1/df_data_area['house_rental_price']/df_data_area['house_rental_area']

    # 格式化数据并保存到本地，方便在echarts 官网可视化显示
    str_result = data_to_json(df_data_area)
    with open(r'C:\Users\wzg\Desktop\data_heatmap_'+station+type+'.txt', 'w') as f:
        f.write(str_result)
    # df_data_area.to_csv(r'C:\Users\wzg\Desktop\data_heatmap_'+station+type+'.csv')


def explore_area(df_data):
    """
    通过热力图探索数据
    @param df_data:
    @return:
    """
    longgang_area = ['坂田', '龙岗中心城']
    longhua_area = ['龙华中心', '民治', '红山']
    futian_area_zz = ['皇岗', '石厦', '梅林']
    futian_area_hz = ['梅林', '新洲', '景田']
    nanshan_area_zz = ['前海', '蛇口', '南山中心']
    nanshan_area_hz = ['前海', '蛇口', '南头']

    save_result(df_data, '龙岗区', longgang_area, '整租', 5000)
    save_result(df_data, '龙岗区', longgang_area, '合租', 1700)
    save_result(df_data, '龙华区', longhua_area, '整租', 7000)
    save_result(df_data, '龙华区', longhua_area, '合租', 2500)
    save_result(df_data, '福田区', futian_area_zz, '整租', 8500)
    save_result(df_data, '福田区', futian_area_hz, '合租', 2400)
    save_result(df_data, '南山区', nanshan_area_zz, '整租', 10000)
    save_result(df_data, '南山区', nanshan_area_hz, '合租', 3000)


if __name__ == '__main__':
    pass



