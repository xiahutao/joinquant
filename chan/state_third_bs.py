# -*- coding: utf-8 -*-
# @Time    : 2020/6/30 10:15
# @Author  : zhangfang
import pandas as pd


def PowerSetsRecursive(items):
    # 求集合的所有子集
    result = [[]]
    for x in items:
        result.extend([subset + [x] for subset in result])
    return result


if __name__ == "__main__":
    fold_path = 'e://Strategy//MT4//'
    df = pd.read_excel(fold_path + '蓝线三类买卖点0630.xlsx').dropna()
    print(df)

    method_name = ['开仓中枢过滤', '开仓确认', '平仓有无背离', 'symbol']  # ['模型', '开仓中枢过滤', '开仓确认', '平仓有无背离']
    method_name_all = PowerSetsRecursive(method_name)
    method_name_all = [i for i in method_name_all if len(i) != 0]
    # print(method_name_all)

    lst = []
    for method_name1 in method_name_all:
        for method, group in df.groupby(method_name1):

            rw = []
            rw.append(method)
            rw.append(group['胜率'].mean())
            rw.append(group['盈亏比'].mean())
            rw.append(group['trading_times'].mean())
            rw.append(len(group[group['盈亏平衡'] > 0])/len(group))
            rw.append(group['盈亏平衡'].mean())

            lst.append(rw)
    ret = pd.DataFrame(lst, columns=['模型', '平均胜率', '平均盈亏比', '平均交易次数', '盈利品种占比', '平均盈亏'])
    ret['盈亏平衡'] = ret['平均胜率'] * ret['平均盈亏比'] - (1 - ret['平均胜率'])
    ret.to_excel(fold_path + 'state_third_bs_' + '_'.join(method_name) + '.xlsx')

    symbol_max = df.groupby(['symbol'])['盈亏平衡'].max()
    print(symbol_max)
    symbol_max = []
    for code, group in df.groupby(['symbol']):
        symbol_max.append(group[group['盈亏平衡'] == group['盈亏平衡'].max()])
    symbol_max = pd.concat(symbol_max)
    print(symbol_max)
    symbol_max.to_excel(fold_path + 'symbol_max' + '.xlsx')

