# -*- coding: utf-8 -*-
# @Time    : 2020/6/30 10:15
# @Author  : zhangfang
import pandas as pd
import numpy as np


def PowerSetsRecursive(items):
    # 求集合的所有子集
    result = [[]]
    for x in items:
        result.extend([subset + [x] for subset in result])
    return result


if __name__ == "__main__":
    level = 1
    s_date = '2015-01-01'
    e_date = '2020-01-01'
    fee = np.float(0.00015)
    fold_ini_path = 'e://Strategy//MT4//state_blue_line//'
    state_singal = pd.read_excel(fold_ini_path + 'state_signal_1515_30_60_240_1440' + '.xlsx', encoding='gbk',
                                 index_col=0)
    print(state_singal)
    method_name = ['品种', 'period']  # ['品种', 'period']
    method_name_all = PowerSetsRecursive(method_name)
    method_name_all = [i for i in method_name_all if len(i) != 0]
    # print(method_name_all)

    lst = []
    for method_name1 in method_name_all:
        for method, group in state_singal.groupby(method_name1):

            rw = []
            rw.append(method)
            rw.append(group['sharpe_ratio'].mean())
            rw.append(group['ann_return'].mean())
            rw.append(group['max_drawdown'].mean())
            rw.append(len(group[group['sharpe_ratio'] > 0])/len(group))
            lst.append(rw)
    ret = pd.DataFrame(lst, columns=['模型', 'sharp', 'ann_return', 'max_drawdown', '盈利品种占比'])
    print(ret)
    ret.to_excel(fold_ini_path + 'state_symbol' + '_'.join(method_name) + '.xlsx')

    symbol_max = state_singal.groupby(['品种'])['sharpe_ratio'].max()
    print(symbol_max)
    symbol_max = []
    for code, group in state_singal.groupby(['品种']):
        symbol_max.append(group[group['sharpe_ratio'] == group['sharpe_ratio'].max()])
    symbol_max = pd.concat(symbol_max)
    print(symbol_max)
    symbol_max.to_excel(fold_ini_path + 'symbol_max_tm' + '.xlsx')

