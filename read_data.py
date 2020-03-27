# encoding:utf-8
# FileName: read_data
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/3/16 10:11
# Description: 读取数据

import pandas as pd
import numpy as np

from sqlalchemy import create_engine

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)


def read_data():
    """
    数据库中读取数据
    @return:
    """
    # 连接数据库
    connect = create_engine('mysql+mysqlconnector://username:passwd@localhost:3306/db_name')

    # 获取所有数据
    sql_city = 'select * from t_lianjia_rent_info'
    df_rent_house_data = pd.read_sql_query(sql_city, connect)

    return df_rent_house_data


if __name__ == '__main__':
    df_data = read_data()
    print(df_data)