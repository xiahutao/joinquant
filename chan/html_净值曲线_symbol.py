# -*- coding: utf-8 -*-
# @Time    : 2020/6/30 10:15
# @Author  : zhangfang
import pandas as pd
import html5lib
from trading_future.future_singleton import Future
from backtest_func import yearsharpRatio, maxRetrace, annROR, annROR_signal
import matplotlib.pyplot as plt
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
    fold_ini_path = 'e://Strategy//MT4//'
    # fold_ini_path = 'G://缠论//回测报告//'
    porfolio = Future()
    period_ini_lst = [15, 30, 60, 240, 1440]
    period_ini_lst = [5, 15, 30, 60, 240, 1440]
    period_lst_all = PowerSetsRecursive(period_ini_lst)
    period_lst_all = [i for i in period_lst_all if len(i)>0]

    code_lst = ['ap', 'ag', 'al', 'cf', 'cu', 'fu', 'i', 'j', 'ni', 'pb', 'pp', 'rb', 'sc', 'tf', 'v', 'zc', 'zn', 'c',
                'if', 'sf', 'p', 'hc', 'au', 'jm', 'sm', 'ru', 'bu', 'oi', 'sr', 'ta', 'm', 'ma']  # 所有品种32个
    # code_lst = ['ap', 'ag', 'al', 'cu', 'i', 'j', 'ni', 'pb', 'pp', 'rb', 'sc', 'v', 'zc', 'zn', 'c',
    #             'if', 'sf', 'p', 'hc', 'au', 'sm', 'ru', 'bu', 'sr', 'ta', 'ma']   # sharp>0的品种17个
    # code_lst = ['ma', 'ta', 'c', 'bu', 'sf', 'v', 'sm', 'hc', 'rb', 'pp', 'p', 'zc', 'ag', 'al', 'i',
    #             'pb', 'ap', 'zn']  # 保证金<10000的品种18个
    # code_lst = ['ma', 'ta', 'c', 'bu', 'sf', 'v', 'sm', 'hc', 'rb', 'pp', 'p']  # 保证金<5000的品种11个
    ret = {}
    ret['symbol'] = []
    ret['tm'] = []
    ret['start_time'] = []
    ret['end_time'] = []
    ret['复盘模型'] = []
    ret['K线数量'] = []
    ret['盈利比'] = []
    ret['trading_times'] = []
    ret['盈利次数'] = []
    ret['平均盈利'] = []
    ret['平均亏损'] = []
    ret['点差'] = []
    ret['sharp'] = []
    ret['ann_return'] = []
    ret['max_drawdown'] = []
    ret['level'] = []
    porfolio_lst = []

    signal_lst = []

    for period_lst in period_lst_all:
        print(period_lst)
        chg_df_all = pd.DataFrame(columns=['date_time'])
        for code in code_lst:
            print(code)
            profit_lst = []
            for period in period_lst:

                mode = '蓝线笔_蓝线反转确认_蓝线反转平仓_200627_' + str(period) + '分钟'
                fold_path = fold_ini_path + mode + '//'
                html = pd.read_html(fold_path + code + '.htm', encoding='gbk')
                state = html[0]
                html = pd.read_html(fold_path + code + '.htm', encoding='gbk', header=0, index_col=0)
                trade = html[1]
                profit_lst.append(trade[['时间', '获利']])
            profit_df_all = pd.concat(profit_lst).rename(columns={'时间': 'date_time', '获利': 'profit'}).fillna(value=0)
            profit_df_all['date_time'] = profit_df_all['date_time'].apply(lambda x: x[:4] + '-' + x[5:7] + '-' + x[8:10])
            profit_df_all = profit_df_all.groupby(['date_time'])
            profit_df = profit_df_all.sum()
            profit_df['count'] = profit_df_all.count()
            # trade_times_everyday = count_df.profit.mean()
            profit_df['date_time'] = profit_df.index
            profit_df = profit_df.assign(date_time=lambda df: df.date_time.apply(lambda x: str(x)[:10]))
            profit_df = profit_df.reset_index(drop=True)
            hq = pd.read_csv('e:/data/future_index/' + code.upper() + '_' + 'daily' + '_index.csv')[
                ['date_time', 'close']].assign(date_time=lambda df: df.date_time.apply(lambda x: str(x)[:10]))

            hq = hq[(hq['date_time'] > s_date) & (hq['date_time'] < e_date)]
            contract_lst = [code.upper()]
            VolumeMultiple = porfolio.get_VolumeMultiple(contract_lst)[code.upper()]['VolumeMultiple']

            aum_ini = hq.close.tolist()[0] * VolumeMultiple * 2 * level
            profit_df = hq.merge(profit_df, on=['date_time'], how='left').sort_values(['date_time'])
            # profit_df = profit_df.fillna(0)
            profit_df['chg'] = (profit_df['profit'] - profit_df['close'].shift(1) * profit_df['count'] * VolumeMultiple * fee) * level / \
                               (profit_df['close'].shift(1) * VolumeMultiple * 2 * len(period_lst))
            profit_df = profit_df.fillna(0)
            profit_df['net'] = 1 + profit_df['chg'].cumsum()
            # print(profit_df)

            net_lst = profit_df.net.tolist()
            try:
                sharpe_ratio = yearsharpRatio(net_lst, 1)
            except:
                sharpe_ratio = -1
            try:
                ann_return = annROR_signal(net_lst, 1)
            except:
                ann_return = -1
            try:
                max_drawdown = maxRetrace(net_lst, 1)
            except:
                max_drawdown = 1

            signal_row = []
            signal_row.append(code)
            signal_row.append('_'.join([str(i) for i in period_lst]))
            signal_row.append(fee)
            signal_row.append(sharpe_ratio)
            signal_row.append(ann_return)
            signal_row.append(max_drawdown)
            signal_row.append(s_date)
            signal_row.append(e_date)
            signal_lst.append(signal_row)
            title_str = '%s 周期%sm sharp %.2f annRet %.2f maxRetrace %.2f' % (
                code, '_'.join([str(i) for i in period_lst]), sharpe_ratio, 100 * ann_return, 100 * max_drawdown)
            profit_df.set_index(['date_time']).ix[:, ['net']].plot()
            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.title(title_str)
            plt.savefig(fold_ini_path + 'fig/' + code + '_' + '_'.join([str(i) for i in period_lst]) + '_fee_' +
                        str(int(np.around(fee * 100000, 0))) + '.png')
            plt.show()

            chg_df_ = profit_df.reset_index(drop=False)[['date_time', 'chg']]
            chg_df_ = chg_df_.rename(columns={'chg': 'chg_' + code})
            chg_df_all = chg_df_all.merge(chg_df_, on=['date_time'], how='outer')
        chg_df_all = chg_df_all.fillna(value=0)
        chg_df = chg_df_all.sort_values(['date_time']).set_index(['date_time'])
        chg_name = ['chg_' + code for code in code_lst]
        chg_df['chg'] = chg_df[chg_name].sum(axis=1) / len(code_lst)
        chg_df['net'] = 1 + chg_df['chg'].cumsum()
        chg_df = chg_df.reset_index(drop=False)
        chg_df['date_time'] = pd.to_datetime(chg_df['date_time'])
        chg_df = chg_df.set_index(['date_time'])
        sharpe_ratio = yearsharpRatio(chg_df['net'].tolist(), 1)
        ann_return = annROR(chg_df['net'].tolist(), 1)
        max_drawdown = maxRetrace(chg_df['net'].tolist(), 1)
        porfolio_row = []
        porfolio_row.append(len(code_lst))
        porfolio_row.append('_'.join([str(i) for i in period_lst]))
        porfolio_row.append(fee)
        porfolio_row.append(sharpe_ratio)
        porfolio_row.append(ann_return)
        porfolio_row.append(max_drawdown)
        porfolio_row.append(s_date)
        porfolio_row.append(e_date)
        porfolio_lst.append(porfolio_row)

        chg_df.ix[:, ['net']].plot()
        title_str = '品种%s个 周期%sm sharp %.2f annRet %.2f maxRetrace %.2f' % (
            str(len(code_lst)),  '_'.join([str(i) for i in period_lst]), sharpe_ratio, 100 * ann_return,
            100 * max_drawdown)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.title(title_str)
        plt.savefig(fold_ini_path + 'fig/' + str(len(code_lst)) + '_' + str(period) + 'm' + '_fee_' +
                    str(int(np.around(fee*100000, 0))) + '.png')
        plt.show()

    porfolio_state = pd.DataFrame(porfolio_lst, columns=['品种数', 'period', 'fee', 'sharpe_ratio', 'ann_return',
                                                         'max_drawdown', 's_date', 'e_date'])
    porfolio_state.to_excel(fold_ini_path + 'state_blue_line//state_porfolio_all_period' + '.xlsx', encoding='gbk')

    signal_state = pd.DataFrame(signal_lst, columns=['品种', 'period', 'fee', 'sharpe_ratio', 'ann_return',
                                                         'max_drawdown', 's_date', 'e_date'])
    signal_state.to_excel(
        fold_ini_path + 'state_blue_line//state_signal_all_period_' + '.xlsx',
        encoding='gbk')


