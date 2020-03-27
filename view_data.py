# encoding:utf-8
# FileName: plot_data
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/3/16 10:12
# Description: 数据可视化
import re

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from preprocess_data import preprocess_data
from tools import sns_set

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)


def view_data(df_data):
    """
    数据可视化探索
    @param df_data:
    @return:
    """
    # 声明使用 Seaborn 样式
    sns = sns_set()
    print(df_data.info())
    print(df_data.describe())
    print('*'*50)
    """"
    --接数据清洗部分--
    
    1. 前面已经完成了数据的清洗，再来看看我们清洗后的数据特征
    一共有：房屋行政区、区域、详细地址、经纬度、出租方式、房屋布局、房屋面积、房租、楼层、电梯、标签、是够有停车位、水电情况、燃气情况、房屋属性等特征
    2. 对数值型数据进行描述性统计，包括均值，中位数，众数，方差，标准差，最大值，最小值等
    在我们数据集中有房租价格、经纬度、房屋面积是数值型数据
    你能看出什么吗？房屋面积最大1223m²，最小5m²；房租价格最大25w元，最小880元，平均值6398。
    这个值，怎么说呢，小一认为数据统计肯定有点不合理。考虑涉及到整租和合租，我们分开再来统计
    """
    # 上面的极大值都出现在整租房屋中，ok，暂时先放着，在可视化步骤中我们深入分析它
    print(df_data.loc[df_data.house_rental_method == '整租'].describe())
    # 相比整租房租价格，合租房价最大10000，最小980，均值1992，应该是正常数据
    print(df_data.loc[df_data.house_rental_method == '合租'].describe())

    """
    3. 数据可视化探索
    在探索之前我们再来看一下我们提出的问题，带着问题去探索才不会跑偏。针对问题再来细分一下步骤：
    3.1 单特征分析
    房屋出租方式、房租价格分布区间（分合租和整租）、行政区房屋数量分布
    楼层、标签、车位、水电、燃气、房屋属性等字段频率分布
    3.2 多特征分析
    主要字段是出租方式、行政区域、房租价格
    次要字段是面积、楼层、是否有车位、水电、燃气等
    目的：分析特征之间的相关性
    3.3 数据探索
    经纬度打点形成热力地图、各行政区的价值洼地
    """

    """房租价格"""
    # seaborn 可以直接通过hue 字段对所有的数据进行分箱展示，但是由于合租和整租的数据分布差别太大，可视化效果不佳，这里分开处理
    fig, axs = plt.subplots(nrows=1, ncols=2)
    sns.boxenplot(x=np.ones(df_data[df_data.house_rental_method == '整租'].shape[0]), y='house_rental_price',
                  data=df_data[df_data.house_rental_method == '整租'], ax=axs[0])
    sns.boxenplot(x=np.ones(df_data[df_data.house_rental_method == '合租'].shape[0]),  y='house_rental_price',
                  data=df_data[df_data.house_rental_method == '合租'], ax=axs[1])
    # 添加标题及相关
    axs[0].set_title('整租方式', fontsize=13)
    axs[1].set_title('合租方式', fontsize=13)
    fig.suptitle('出租方式与房租的箱型分布    『by:小一』', fontsize=16)
    axs[0].set_ylabel('房租价格(元)', fontsize=12)
    axs[1].set_ylabel('')
    plt.show()

    # 确定面积大于45㎡、房租超过4500元、户型是两室及以上，注意是合租房！合租房！合租房！基本都是整租房
    print(df_data[df_data.house_rental_method == '整租'].sort_values('house_rental_price', ascending=False).head(3))
    """根据规则进行数据的二次清洗①"""
    df_data.loc[(df_data.house_rental_method == '合租') &
                (df_data.house_rental_price > 4500) &
                (df_data.house_rental_area > 45) &
                ~(df_data.house_layout.str.startswith('一')), 'house_rental_method'] = '整租'

    # 确定了价钱低于3800、面积超过55㎡的非一室的整租房基本都是合租房
    print(df_data[df_data.house_rental_method == '合租'].sort_values('house_rental_price', ascending=False).head(3))
    df_data.loc[(df_data.house_rental_method == '整租') &
                (df_data.house_rental_price < 2800) &
                (df_data.house_rental_area > 55) &
                ~(df_data.house_layout.str.startswith('一')), 'house_rental_method'] = '合租'

    """再次进行房租价格的探索"""
    fig, axs = plt.subplots(nrows=1, ncols=2)
    sns.boxenplot(x=np.ones(df_data[df_data.house_rental_method == '整租'].shape[0]), y='house_rental_price',
                  data=df_data[df_data.house_rental_method == '整租'], ax=axs[0])
    sns.boxenplot(x=np.ones(df_data[df_data.house_rental_method == '合租'].shape[0]), y='house_rental_price',
                  data=df_data[df_data.house_rental_method == '合租'], ax=axs[1])

    # 添加标题及相关
    axs[0].set_title('整租方式', fontsize=13)
    axs[1].set_title('合租方式', fontsize=13)
    fig.suptitle('出租方式与房租的箱型分布    『by:小一』', fontsize=16)
    axs[0].set_ylabel('房租价格(元)', fontsize=12)
    axs[1].set_ylabel('')
    plt.show()

    """出租方式"""
    """统计方法：用饼图显示比较合适"""
    house_rental_method = df_data.house_rental_method.value_counts()
    plt.pie(house_rental_method, labels=house_rental_method.index.tolist(), autopct='%.2f%%', startangle=90, shadow=True)
    plt.title('房屋出租方式统计    『by:小一』', fontsize=14)
    plt.show()

    """多子图的饼图绘制"""
    # 同样适合用饼图表示的特征还有：楼层、电梯、是否有停车位、水电情况、燃气情况、房屋属性等
    fig, axs = plt.subplots(nrows=2, ncols=3)
    # 饼图的数据统计
    house_floor = df_data.house_floor.value_counts()
    house_elevator = df_data.house_elevator.value_counts()
    house_parking = df_data.house_parking.value_counts()
    house_gas = df_data.house_gas.value_counts()
    cell_info = df_data.cell_info.value_counts()
    # 饼图的子图显示
    axs[0, 0].pie(house_rental_method, labels=house_rental_method.index.tolist(), autopct='%.2f%%', startangle=90, shadow=True)
    axs[0, 1].pie(house_floor, labels=house_floor.index.tolist(), autopct='%.2f%%', startangle=90, shadow=True)
    axs[0, 2].pie(house_elevator, labels=house_elevator.index.tolist(), autopct='%.2f%%', startangle=90, shadow=True)
    axs[1, 0].pie(house_parking, labels=house_parking.index.tolist(), autopct='%.2f%%', startangle=90, shadow=True)
    # 数字显示有重叠，可以通过设置偏移解决，但最好的解决方式引出一条直线。另外，使用pyecharts可以很大程度避免重叠的问题
    axs[1, 1].pie(house_gas, labels=house_gas.index.tolist(), autopct='%.2f%%', startangle=90, shadow=True,
                  explode=(0, 0, 0.1))
    axs[1, 2].pie(cell_info, labels=cell_info.index.tolist(), autopct='%.2f%%', startangle=90, shadow=True,
                  explode=(0, 0, 0, 0.1))
    # 设置标题相关
    axs[0, 0].set_title('出租方式', fontsize=13)
    axs[0, 1].set_title('楼层高度', fontsize=13)
    axs[0, 2].set_title('是否有电梯', fontsize=13)
    axs[1, 0].set_title('是否提供停车位', fontsize=13)
    axs[1, 1].set_title('是否提供燃气', fontsize=13)
    axs[1, 2].set_title('房源性质', fontsize=13)
    fig.suptitle('房源特征统计    『by:小一』', fontsize=16)
    plt.show()

    """行政区房屋数量"""
    """统计方法：这里我们直接基于sz的行政区域进行统计"""
    # 数据汇总统计
    house_station = df_data.station.value_counts(ascending=True)
    # 绘制条形图
    ax_station = sns.barplot(x=house_station.index.tolist(),
                             y=house_station, palette="Spectral_r",)
    # 添加标题及相关
    ax_station.set_title('各行政区房源出租数量统计    『by:小一』', fontsize=16)
    ax_station.set_xlabel('行政区', fontsize=12)
    ax_station.set_ylabel('出租房源数量', fontsize=12)
    # 设置坐标轴刻度的字体大小
    ax_station.tick_params(axis='x', labelsize=8)
    # 显示数据的具体数值
    for x, y in zip(range(0, len(house_station.index.tolist())), house_station):
        ax_station.text(x - 0.2, y + 0.3, '%d' % y, color='black')
    plt.show()

    """房屋标签"""
    """统计方法：方法同区域统计"""
    # 数据汇总统计
    df_data['house_tag'] = df_data['house_tag'].str.split('/')
    house_tag = pd.Series(np.concatenate(df_data['house_tag'])).value_counts(ascending=True)
    # 绘制条形图
    ax_tag = sns.barplot(x=house_tag.index.tolist(), y=house_tag, palette="Spectral_r")
    # 添加标题及相关
    ax_tag.set_title('出租房源标签统计    『by:小一』', fontsize=16)
    ax_tag.set_xlabel('房源标签', fontsize=12)
    ax_tag.set_ylabel('标签频次', fontsize=12)
    # 设置坐标轴刻度的字体大小
    ax_tag.tick_params(axis='x', labelsize=8)
    # 显示数据的具体数值
    for x, y in zip(range(0, len(house_tag.index.tolist())), house_tag):
        ax_tag.text(x - 0.3, y + 0.3, '%d' % y, color='black')
    plt.show()

    """房屋户型"""
    """统计方法：只统计卧室的数量"""
    df_data['house_layout'] = df_data['house_layout'].map(lambda str: re.findall(r'\d+', str)[0]).astype(dtype='int')
    # 通过卧室数量进行排序
    house_layout_zz = df_data.loc[df_data.house_rental_method == '整租', 'house_layout'].value_counts().sort_index()
    house_layout_hz = df_data.loc[df_data.house_rental_method == '合租', 'house_layout'].value_counts().sort_index()
    # 绘制多条形图
    fig, axs = plt.subplots(nrows=1, ncols=2)
    sns.barplot(x=house_layout_zz.index.tolist(), y=house_layout_zz, palette="Spectral_r", ax=axs[0])
    sns.barplot(x=house_layout_hz.index.tolist(), y=house_layout_hz, palette="Spectral_r", ax=axs[1])
    # 添加标题及相关
    axs[0].set_title('整租', fontsize=13)
    axs[1].set_title('合租', fontsize=13)
    axs[0].set_xlabel('卧室个数', fontsize=12)
    axs[1].set_xlabel('卧室个数', fontsize=12)
    axs[0].set_ylabel('房源数量', fontsize=12)
    axs[1].set_ylabel('')
    # 设置坐标轴刻度的字体大小
    axs[0].tick_params(axis='x', labelsize=10)
    axs[1].tick_params(axis='x', labelsize=10)
    fig.suptitle('房源卧室数量统计    『by:小一』', fontsize=16)
    # 显示数据的具体数值
    for x, y in zip(range(0, len(house_layout_zz.index.tolist())), house_layout_zz):
        axs[0].text(x - 0.3, y + 0.3, '%d' % y, color='black')
    for x, y in zip(range(0, len(house_layout_hz.index.tolist())), house_layout_hz):
        axs[1].text(x - 0.3, y + 0.3, '%d' % y, color='black')
    plt.show()

    """
    通过单一特征的可视化探索，我们可以得到下面这些结论
    总样本数27150.

    1. 深圳市出租房屋信息如下：
        其中整租房屋记录21146个，占比77.34%远高于合租的22.66%
        出租房屋中高中低楼层的房屋分布均匀，有5个房屋出租地下室，占总房屋记录数的0.01%
        出租房屋中有78.98%的房屋带有电梯
        另外，房屋性质为普通住宅的占比86.45%，提供燃气的房屋占比90.60%，有3.85%的房屋提供免费车位
    2. 深圳市房屋出租方式的价格分布
        整租的价格范围是在880-14000范围内，均价为5600，大于14000的房屋占比较少
        合租的价格范围是在980-3400范围内，均值为1900，大于3400的房屋占比较少
    3. 深圳市房屋出租数量前三的分别是龙岗区、南山区和福田区，分别占比24.90%、24.22%、18.90%，为房屋出租的主要区域
    4. 房屋标签数量前三的分别是近地铁、随时看房、官方核验，看来机构已经牢牢把握住租房用户的心思了
    5. 房屋卧室数量：整租类型的出租房卧室数量前三分别是1居室、3居室和2居室；合租类型的前三分别是4居室、5居室和3居室。其中整租的一居室数量最多
    """

    """
    分析完了单一维度的特征，接下来需要进行特征组合分析，但也不是说所有的特征都需要去研究。
    举个例子：我们前面提出的假设--楼层、车位、燃气、电梯等会对房租有影响吗？在分析的时候它们只和房租有关，属于两个特征的相关分析，不需要其他特征支撑
    但是像区域分布、房屋面积、房租等是可以互相影响的，需要联立特征分析，比如福田区的房屋面积和房租的关系、福田区整租的房租分布等等这些
    下面我们一起来组合一下
    """
    """行政区的房价分布"""
    df_data_select = df_data.loc[(df_data.house_rental_method == '整租') & (df_data.house_rental_price < 15000), :]
    # 筛选特征
    ax_station_price = sns.violinplot(x='station', y='house_rental_price', data=df_data_select)
    # ax_station_price = sns.stripplot(x='station', y='house_rental_price', data=df_data_select)
    # 添加标题及相关
    ax_station_price.set_title('各行政区整租房租价格分布(<15000)    『by:小一』', fontsize=16)
    ax_station_price.set_xlabel('行政区', fontsize=12)
    ax_station_price.set_ylabel('房租', fontsize=12)
    # 设置坐标轴刻度的字体大小
    ax_station_price.tick_params(axis='x', labelsize=8)
    plt.show()

    df_data_select = df_data.loc[(df_data.house_rental_method == '合租') & (df_data.house_rental_price<4000), :]
    ax_station_price = sns.violinplot(x='station', y='house_rental_price', data=df_data_select)
    # 添加标题及相关
    ax_station_price.set_title('各行政区合租房租价格分布(<4000)    『by:小一』', fontsize=16)
    ax_station_price.set_xlabel('行政区', fontsize=12)
    ax_station_price.set_ylabel('房租', fontsize=12)
    # 设置坐标轴刻度的字体大小
    ax_station_price.tick_params(axis='x', labelsize=8)
    plt.show()

    """
    从整体来说福田、南山和罗湖的房租最低价在1600，而其他区域最低房价在1000
    从房价的分布来看，龙岗和龙华的房价较低，罗湖、福田和南山的房价较高
    综合前面我们也提到，房源最多的三个区分别是龙岗、南山和福田。
    可以初步确定：便宜的房源->龙岗区最佳、龙华次之，不在乎价格的房源->福田和南山最佳
    既然确定了区域，那我们针对这几个区域再进行分析
    """
    """看一下龙岗、龙华、福田、南山、罗湖的房源分布"""
    # 分为合租和整租，另外我们稍加限定房租的价格，使得范围更精确。比如：合租的房租小于3800元，整租的房租小于12000元
    plot_station_data(df_data, '龙岗区', 2)
    plot_station_data(df_data, '龙华区', 2)
    plot_station_data(df_data, '福田区', 1)
    plot_station_data(df_data, '南山区', 2)
    plot_station_data(df_data, '罗湖区', 2)

    """楼层、车位、燃气、电梯、小区性质"""
    fig, axs = plt.subplots(nrows=2, ncols=3)
    sns.stripplot(x='house_floor', y='house_rental_price', data=df_data, ax=axs[0, 0])
    sns.stripplot(x='house_parking', y='house_rental_price', data=df_data, ax=axs[0, 1])
    sns.stripplot(x='house_elevator', y='house_rental_price', data=df_data, ax=axs[0, 2])
    sns.stripplot(x='house_gas', y='house_rental_price', data=df_data, ax=axs[1, 0])
    sns.stripplot(x='cell_info', y='house_rental_price', data=df_data, ax=axs[1, 1])
    # 添加标题及相关
    axs[0, 0].set_title('楼层与房租分布', fontsize=13)
    axs[0, 1].set_title('停车位与房租分布', fontsize=13)
    axs[0, 2].set_title('有无电梯与房租分布', fontsize=13)
    axs[1, 0].set_title('有无燃气与房租分布', fontsize=13)
    axs[1, 1].set_title('小区性质与房租分布', fontsize=13)
    axs[0, 0].set_xlabel('', fontsize=12)
    axs[0, 1].set_xlabel('', fontsize=12)
    axs[0, 2].set_xlabel('', fontsize=12)
    axs[1, 0].set_xlabel('', fontsize=12)
    axs[1, 1].set_xlabel('', fontsize=12)
    axs[0, 0].set_ylabel('房租（元）', fontsize=12)
    axs[0, 1].set_ylabel('', fontsize=12)
    axs[0, 2].set_ylabel('', fontsize=12)
    axs[1, 0].set_ylabel('房租（元）', fontsize=12)
    axs[1, 1].set_ylabel('', fontsize=12)
    fig.suptitle('不同特征下房租价格分布    『by:小一』', fontsize=16)

    plt.show()

    return df_data


def plot_station_data(df_data, area, tag):
    """
    绘制各个行政区的区域房源数据图
    @param df_data:
    @param area:
    @param tag:
    @return:
    """
    # 分离出整租和合租的房源数据
    df_data_zz = df_data.loc[(df_data.station == area) & (df_data.house_rental_method == '整租') &
                             (df_data.house_rental_price < 12000), :].sort_values('area')
    df_data_hz = df_data.loc[(df_data.station == area) & (df_data.house_rental_method == '合租') &
                             (df_data.house_rental_price < 3800), :].sort_values('area')
    # 对区域进行汇总统计
    zz_count = df_data_zz.area.value_counts().sort_index()
    hz_count = df_data_hz.area.value_counts().sort_index()

    fig, axs = plt.subplots(nrows=2, ncols=2)
    if tag == 1:
        sns.boxenplot(x='area', y='house_rental_price', data=df_data_zz, ax=axs[0, 0])
        sns.boxenplot(x='area', y='house_rental_price', data=df_data_hz, ax=axs[1, 0])
    else:
        sns.violinplot(x='area', y='house_rental_price', data=df_data_zz, ax=axs[0, 0])
        sns.violinplot(x='area', y='house_rental_price', data=df_data_hz, ax=axs[1, 0])
    # 绘制多条形图
    sns.barplot(x=zz_count.index.tolist(), y=zz_count, palette="Spectral_r", ax=axs[0, 1])
    sns.barplot(x=hz_count.index.tolist(), y=hz_count, palette="Spectral_r", ax=axs[1, 1])

    # 设置坐标轴刻度的字体大小
    axs[0, 0].set_title('整租房租价格分布', fontsize=13)
    axs[0, 1].set_title('整租房源数量统计', fontsize=13)
    axs[1, 0].set_title('合租房租价格分布', fontsize=13)
    axs[1, 1].set_title('合租数量统计', fontsize=13)
    axs[0, 0].set_xlabel('')
    axs[0, 1].set_xlabel('')
    axs[1, 0].set_xlabel('')
    axs[1, 1].set_xlabel('')
    axs[0, 0].set_ylabel('房租价格（元）', fontsize=12)
    axs[0, 1].set_ylabel('房源数量', fontsize=12)
    axs[1, 0].set_ylabel('房租价格（元）', fontsize=12)
    axs[1, 1].set_ylabel('房源数量', fontsize=12)
    # 设置x 轴标签文字的方向
    axs[0, 0].set_xticklabels(axs[0, 0].get_xticklabels(), rotation=30)
    axs[0, 1].set_xticklabels(axs[0, 1].get_xticklabels(), rotation=30)
    axs[1, 0].set_xticklabels(axs[1, 0].get_xticklabels(), rotation=30)
    axs[1, 1].set_xticklabels(axs[1, 1].get_xticklabels(), rotation=30)
    # 设置x 轴文字大小
    axs[0, 0].tick_params(axis='x', labelsize=8)
    axs[0, 1].tick_params(axis='x', labelsize=8)
    axs[1, 0].tick_params(axis='x', labelsize=8)
    axs[1, 1].tick_params(axis='x', labelsize=8)
    fig.suptitle(area+'各区域房源价格和数量分布统计    『by:小一』', fontsize=16)

    # 条形图的数值显示
    for x, y in zip(range(0, len(zz_count.index.tolist())), zz_count):
        axs[0, 1].text(x - 0.3, y + 0.3, '%d' % y, color='black')
    for x, y in zip(range(0, len(hz_count.index.tolist())), hz_count):
        axs[1, 1].text(x - 0.3, y + 0.3, '%d' % y, color='black')

    plt.show()


if __name__ == '__main__':
    pass