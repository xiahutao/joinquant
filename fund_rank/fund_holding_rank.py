# -*- coding: utf-8 -*-
# @Time    : 2020/6/1 11:03
# @Author  : zhangfang
import pandas as pd
import numpy as np
import datetime

if __name__ == '__main__':
    today = datetime.datetime.today()
    today = str(today)[:10]
    fund_holding = pd.read_csv('g://lfp//result//fund_holding.csv')\
        .assign(code=lambda df: df.code.apply(lambda x: int(x)))
    rank = pd.read_csv('g://lfp//result//fund_rank_position_chg_zf2020-07-01.csv', encoding='gbk')[['code', 'topsis', 'stars']]\
        .assign(code=lambda df: df.code.apply(lambda x: int(x)))
    print(rank)
    rank_48 = pd.read_csv('g://lfp//result//fund_rank_position_chg_482020-07-01.csv', encoding='gbk')[['code', 'name', 'topsis', 'stars']]\
        .assign(code=lambda df: df.code.apply(lambda x: int(x)))
    print(rank_48)
    df_rank_60 = fund_holding.merge(rank, on='code', how='left').rename(columns={'topsis': 'topsis5', 'stars': 'stars5'})
    df_rank_48 = fund_holding.merge(rank_48, on='code', how='left').rename(columns={'topsis': 'topsis3', 'stars': 'stars3'})
    ret = df_rank_48.merge(df_rank_60, on=['code'], how='inner')
    print(ret)
    ret.to_csv('g://lfp//result//fund_holding_rank_' + today + '.csv', encoding='gbk')
