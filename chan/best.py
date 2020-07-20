# -*- coding: utf-8 -*-
# @Time    : 2020/7/15 14:19
# @Author  : zhangfang
import pandas as pd


if __name__ == "__main__":
    fold_ini_path = 'e://Strategy//MT4//'
    signal_state = pd.read_excel(fold_ini_path + 'state_blue_line//state_signal_all_period' + '0717opt.xlsx',
        encoding='gbk', index_col=0)
    print(signal_state)
    signal_state = signal_state.drop_duplicates(['品种', 'period', 's_date', 'e_date'], keep='first')
    print(signal_state)

    signal_state.to_excel(
        fold_ini_path + 'state_blue_line//state_signal_all_period' + '0717dropduplicate.xlsx',
        encoding='gbk')