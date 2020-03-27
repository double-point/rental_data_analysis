# encoding:utf-8
# FileName: preprocess_data
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/3/16 10:11
# Description: 数据预处理
import re
from collections import Counter

import pandas as pd
import numpy as np

from read_data import read_data

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)


def preprocess_data(df_data):
    """
    数据清洗
    @param df_data:
    """
    print(df_data.info())
    """
    一共21个字段，其中house_note 全部为空，经纬度数据有一条为空，其他全部不为空
    """
    # 先拿出经纬度为空的瞅一眼
    print(df_data[df_data['house_longitude'].isnull()])

    # 其他数据都正常，经纬度缺失，手动查地图补一下，要是觉得麻烦直接丢掉也行
    # 通过经纬度查找确定该点的经纬度信息，进行填充
    df_data.loc[df_data.house_longitude.isnull(), 'house_longitude'] = 114.018609
    df_data.loc[df_data.house_latitude.isnull(), 'house_latitude'] = 22.604297
    print(df_data.info())

    """
    房屋数据一共22个字段，
    其中房源编号是区分房源的、房屋备注均为空数据，
    房源维护时间和创建时间都是时间维度，在本次分析中唯一的用处是租房者可以用来找出最近更新的房源数据。
    如果我们多爬取几次数据，那时间维度就是一个重要指标，本次就不做分析
    另外，深圳是个南方城市，供暖这个字段也可以删除
    """
    # 即删除房源编号、供暖、房屋备注、房源维护时间和创建时间字段
    df_data.drop(columns=['city', 'house_id', 'house_update_time', 'create_time', 'house_heating', 'house_note'],
                 axis=1, inplace=True)

    """
    再来看剩下的数据
    1. 房租出租方式应该有：整租/合租/不限 这三种，如果不是的话需要处理【需要处理】
    2. 房屋地址中的：城市/行政区/小区/地址 可以划分为行政区+小的地理板块+详细地址【需要处理】
    3. 经度&纬度：应该是float 类型，如果不是的话转换一下即可 【需要处理】
    4. 房屋户型：标准应该是xx室xx厅xx卫，如果不是的话进行合理处理 【需要处理】
    5. 房屋出租面积：应该是一个float 类型的数值，如果再严格点应该是int 类型 【需要处理】
    6. 房租价格：应该是int 类型的数值 【需要处理】
    7. 房屋标签：官方核验、近地铁、精装等标签都比较有用 【需要处理】
    8. 房屋楼层：高中低+楼层 【需要处理】
    9. 是否有电梯：是|否  【需要处理】
    10. 房屋车位：这个字段小一我一直不好确定，感觉租房的人大多不会主动购买车，所以这个字段我们先放着 【暂不处理】
    11. 房屋用水、房屋用电：民水民电和商水商电，这两个字段可以确定小区的性质 【需要处理】
    12. 房屋燃气：【暂不处理】
    通过12条，我们需要处理的数据还挺多的，一步步来吧
    """
    print(df_data.info())
    """1. 房租出租方式中可以看到并没有我们预料的不限字段出现，我们应该是受到了网页提示的影响，ok，不需要处理，直接往下"""
    print(df_data['house_rental_method'].value_counts())

    """2. 房屋地址的数据格式是行政区-区域-详细地址，直接通过split进行划分，划分为行政区、区域、小区地址三列"""
    df_data.loc[df_data.house_address == '--', 'house_address'] = '龙岗区-龙岗中心城-金地龙城中央一期'
    # 或者直接删除
    # df_data.drop(df_data[df_data.house_address == '--'].index, axis=0)
    df_data['station'] = df_data['house_address'].apply(lambda str: str.split('-')[0])
    df_data['area'] = df_data['house_address'].apply(lambda str: str.split('-')[1])
    df_data['address'] = df_data['house_address'].apply(lambda str: str.split('-')[2])
    # 区域为空的我们通过小区名查询同名小区的区域进行填充
    df_data.loc[df_data.area == '', 'area'] = df_data.loc[df_data.area == '', 'address'].\
        apply(lambda str: get_mode_address(str, df_data))
    # 只有一条记录“南山区--聚宁山庄”没有区域，我们手动填充一下。
    df_data.loc[df_data.id == 10909, 'area'] = '西丽'

    """3. 经度&纬度：数据默认读进来已经转换为float类型，ok，不需要处理。（如果这里不是float，可以使用astype进行转换）"""
    print("房屋经度数据类型为：{0}，纬度数据类型为：{1}".format(
        df_data['house_longitude'].dtype, df_data['house_latitude'].dtype))

    """4. 房屋出租面积：剔除m²，并将数据转换成int"""
    df_data['house_rental_area'] = df_data['house_rental_area'].str.replace('㎡', '').astype(dtype='int')
    print("房屋出租面积数据类型为：{0}".format(df_data['house_rental_area'].dtype))

    """5. 房屋户型：房屋数据是很规整的xx室xx厅xx卫的格式"""
    # # 以下代码报错，说明不符合格式要求。
    # print("数据共{0}条，其中符合【xx室xx厅xx卫】格式的数据共{1}条".format(
    #     df_data.shape[0],
    #     df_data['house_layout'].map(lambda str: re.findall(r'^\d+室\d厅\d卫', str)[0]).shape[0]))
    # 存在未知室的情况，我们直接通过房屋面积、价钱和出租类型为它指定卧室的情况
    print(df_data.house_layout.value_counts())
    # 通过同小区的数据进行填充
    df_data.loc[df_data.house_layout.str.contains('未知'), 'house_layout'] = \
        df_data.loc[df_data.house_layout.str.contains('未知'), ['house_rental_area', 'address']].\
            apply(lambda str: get_mode_layout(str[0], str[1], df_data), axis=1)

    """6. 房租价格：只保留价格数据，' 元/月'需要删除，注意空格，这里使用正则搞定：\d+表示至少为一个0-9的数字"""
    df_data['house_rental_price'] = \
        df_data['house_rental_price'].map(lambda str: re.findall(r'\d+', str)[0]).astype(dtype='int')
    print("房租价格数据类型为：{0}".format(df_data['house_rental_price'].dtype))

    """7. 房屋标签：统计每个标签出现的频率"""
    # 去掉房屋标签的头尾 /
    df_data['house_tag'] = df_data['house_tag'].str.slice(1, -1)
    # 对房屋标签进行汇总统计
    print("房屋标签共有{0}个".format(
        pd.Series(np.concatenate(df_data['house_tag'].str.split('/'))).value_counts().shape[0]))

    """8. 房屋楼层：这个数据很有迷惑性，前面的高中低楼层是根据后面的具体楼层来看的，比如40层楼的中楼层和8层楼的中楼层并不能比较，直接保留前面的楼层范围而不保留具体的楼层"""
    # 切割字符
    df_data.loc[~df_data.house_floor.str.contains('未知'), 'house_floor'] = \
        df_data.loc[~df_data.house_floor.str.contains('未知'), 'house_floor'].apply(lambda str: str.split('（')[0])
    # > 其中未知楼层范围的有22个，其中存在楼层高度的未知范围我们可以通过楼层高度进行填充
    # > 这里小一想到两种填充方式，一种是10层以下为低楼层，10-30位中楼层，>30为高楼层
    # > 另一种是根据所在小区去填充，例如西城上筑花园小区的众数是中楼层，则采用中楼层填充。
    # 利用所在楼层小区的众数进行填充
    df_data.loc[df_data.house_floor.str.contains('未知'), 'house_floor'] = \
        df_data.loc[df_data.house_floor.str.contains('未知'), 'address'].apply(lambda str: get_mode_floor(str, df_data))

    """9. 是否有电梯：同样存在缺失数据，可以使用和楼层同样的处理方式进行处理"""
    df_data.loc[df_data.house_elevator == '暂无数据', ['house_elevator']] = \
        df_data.loc[df_data.house_elevator == '暂无数据', 'address'].apply(lambda str: get_mode_elevator(str, df_data))
    # 这里我们继续填充，这次根据前面的楼层范围字段进行填充，若是中高楼层则填充为有电梯，否则填充为无
    df_data.loc[df_data.house_elevator == '无法填充', 'house_elevator'] = \
        df_data.loc[df_data.house_elevator == '无法填充', 'house_floor'].apply(lambda str: get_like_elevator(str))

    """ 10.房屋车位：暂无数据记录占比高于50%，我们前面也说了，不用进行处理"""
    print(df_data['house_parking'].value_counts())
    """11.房屋用水、房屋用电：通过这个字段区分小区性质"""
    # 通过水电字段分为普通住宅、商业住宅、商住两用三种（欢迎补充，这个领域真不了解，补课也没查到多少）
    df_data['cell_info'] = '暂无数据'
    df_data.loc[(df_data['house_water'] == '民水') & (df_data['house_electricity'] == '民电'), 'cell_info'] = '普通住宅'
    df_data.loc[(df_data['house_water'] == '商水') & (df_data['house_electricity'] == '商电'), 'cell_info'] = '商业住宅'
    df_data.loc[((df_data['house_water'] == '民水') & ~(df_data['house_electricity'] == '民电') |
                 ~(df_data['house_water'] == '民水') & (df_data['house_electricity'] == '民电')), 'cell_info'] = '商住两用'
    print(df_data['cell_info'].value_counts())

    """12. 房屋燃气：这个字段好像对于需要燃气做饭的人有用，不过现在用电也行。这个字段我们了解就行。 """
    print(df_data['house_gas'].value_counts())

    return df_data


def get_mode_address(str_address, data):
    """
    通过同名小区的区域进行填充
    @param str_address:
    @param data:
    @return:
    """
    # 确定同名的小区，且区域不为空
    data = data[(data.address == str_address) & ~(data.area == '')]
    # 利用地址进行填充
    str_address = data.area
    if len(str_address) == 0:
        return ''
    else:
        return str_address.iloc[0]


def get_mode_layout(str_area, str_address, data):
    """
    根据近似户型+普遍标准进行填充
    @param str_area:
    @param str_address:
    @param data:
    @return:
    """
    # 确定同名的小区，且楼层数据不为未知
    data = data[(data.address == str_address) & ~(data.house_layout.str.contains('未知'))]
    # 在20m²范围内波动，则默认是同一个户型
    data_like = data.loc[abs(data.house_rental_area-str_area) <= 20, 'house_layout']

    # 如果无法根据近似户型判断，则根据面积普遍标准进行判断
    if data_like.size < 1:
        if str_area < 45:
            return "1室0厅0卫"
        elif str_area < 90:
            return "2室0厅0卫"
        elif str_area < 150:
            return "3室0厅0卫"
        else:
            return "4室0厅0卫"

    return data_like.mode()[0]


def get_mode_floor(str_address,  data):
    """
    根据众数进行填充
    @param str_address:
    @param data:
    @return:
    """
    # 确定同名的小区，且楼层数据不为未知
    data = data.loc[(data.address == str_address) & ~(data.house_floor.str.contains('未知'))]
    # 利用众数进行填充
    mode_floor = data.loc[data.address == str_address, 'house_floor'].mode()[0]
    if len(mode_floor) == 0:
        return '无法填充'
    else:
        return mode_floor


def get_mode_elevator(str_address,  data):
    """
    根据众数进行填充
    @param str_address:
    @param data:
    @return:
    """
    # 确定同名的小区，且电梯数据不为暂无数据
    data = data.loc[(data.address == str_address) & ~(data.house_elevator == '暂无数据')]
    # 利用众数进行填充
    mode_elevvator = data.loc[data.address == str_address, 'house_elevator'].mode()
    if len(mode_elevvator) == 0:
        return '无法填充'
    else:
        return mode_elevvator[0]


def get_like_elevator(str):
    """
    根据楼层字段填充电梯字段
    @param str:
    @return:
    """
    if '低' in str:
        return '无'

    return '有'


if __name__ == '__main__':
    pass