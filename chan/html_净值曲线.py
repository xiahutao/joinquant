# -*- coding: utf-8 -*-
# @Time    : 2020/6/30 10:15
# @Author  : zhangfang
import pandas as pd
import html5lib
from trading_future.future_singleton import Future
from backtest_func import yearsharpRatio, maxRetrace, annROR
import matplotlib.pyplot as plt


def PowerSetsRecursive(items):
    # 求集合的所有子集
    result = [[]]
    for x in items:
        result.extend([subset + [x] for subset in result])
    return result


if __name__ == "__main__":
    level = 1
    s_date = '2015-01-01'
    mode = '蓝线笔_蓝线反转确认_蓝线反转平仓_200627_15分钟'
    fee = 0.00015
    fold_path = 'G://缠论//回测报告//' + mode + '//'
    # fold_path = 'e://Strategy//MT4//' + mode + '//'
    code_lst = ['ap', 'ag', 'al', 'cf', 'cu', 'fu', 'i', 'j', 'ni', 'pb', 'pp', 'rb', 'sc', 'tf', 'v', 'zc', 'zn', 'c',
                'if', 'sf', 'p', 'hc', 'au', 'jm', 'sm', 'ru', 'bu', 'oi', 'sr', 'ta', 'm', 'ma']  # 所有品种32个
    # code_lst = ['ap', 'ag', 'al', 'cu', 'i', 'j', 'ni', 'pb', 'pp', 'rb', 'sc', 'v', 'zc', 'zn', 'c',
    #             'if', 'sf', 'p', 'hc', 'au', 'sm', 'ru', 'bu', 'sr', 'ta', 'ma']   # sharp>0的品种17个
    # code_lst = ['ma', 'ta', 'c', 'bu', 'sf', 'v', 'sm', 'hc', 'rb', 'pp', 'p', 'zc', 'ag', 'al', 'i',
    #             'pb', 'ap', 'zn']  # 保证金<10000的品种18个
    # code_lst = ['ma', 'ta', 'c', 'bu', 'sf', 'v', 'sm', 'hc', 'rb', 'pp', 'p']  # 保证金<5000的品种11个
    porfolio = Future()
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
    chg_df_all = pd.DataFrame(columns=['date_time'])
    for code in code_lst:
        html = pd.read_html(fold_path + code + '.htm', encoding='gbk')
        state = html[0]
        print(state)
        html = pd.read_html(fold_path + code + '.htm', encoding='gbk', header=0, index_col=0)
        trade = html[1]
        profit_df_all = trade[['时间', '获利']].rename(columns={'时间': 'date_time', '获利': 'profit'}).fillna(value=0)
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
        print(code)
        hq = hq[hq['date_time'] > s_date]
        contract_lst = [code.upper()]
        VolumeMultiple = porfolio.get_VolumeMultiple(contract_lst)[code.upper()]['VolumeMultiple']
        print(VolumeMultiple)
        aum_ini = hq.close.tolist()[0] * VolumeMultiple * 2 * level
        profit_df = hq.merge(profit_df, on=['date_time'], how='left').sort_values(['date_time'])
        # profit_df = profit_df.fillna(0)
        profit_df['chg'] = (profit_df['profit'] - profit_df['close'].shift(1) * profit_df['count'] * VolumeMultiple * fee) * level / profit_df['close'].shift(1) / (VolumeMultiple * 2)
        profit_df = profit_df.fillna(0)

        profit_df['net'] = (1 + profit_df['chg']).cumprod()
        net_lst = profit_df.net.tolist()
        sharpe_ratio = yearsharpRatio(net_lst, 1)
        ann_return = annROR(net_lst, 1)
        max_drawdown = maxRetrace(net_lst, 1)

        ret['symbol'].append(state.iloc[0, 2].split('.')[0])
        ret['tm'].append(state.iloc[1, 2].split()[0] + state.iloc[1, 2].split()[1])
        ret['start_time'].append(state.iloc[1, 2].split()[2])
        ret['end_time'].append(state.iloc[1, 2].split()[5])
        ret['复盘模型'].append(state.iloc[2, 2])
        ret['K线数量'].append(state.iloc[5, 1])
        ret['盈利比'].append(state.iloc[10, 1])
        ret['trading_times'].append(int(state.iloc[13, 1]))
        ret['盈利次数'].append(int(state.iloc[14, 3].split()[0]))
        ret['平均盈利'].append(float(state.iloc[16, 3]))
        ret['平均亏损'].append(float(state.iloc[16, 5]))
        ret['点差'].append(state.iloc[8, 5])
        ret['sharp'].append(sharpe_ratio)
        ret['ann_return'].append(ann_return)
        ret['max_drawdown'].append(max_drawdown)
        ret['level'].append(level)

        chg_df_ = profit_df.reset_index(drop=False)[['date_time', 'chg']].rename(columns={'chg': 'chg_' + code})
        chg_df_all = chg_df_all.merge(chg_df_, on=['date_time'], how='outer')
    chg_df_all = chg_df_all.fillna(value=0)
    chg_df = chg_df_all.sort_values(['date_time']).set_index(['date_time'])
    chg_name = ['chg_' + m for m in code_lst]
    chg_df['chg'] = chg_df[chg_name].sum(axis=1) / len(code_lst)
    chg_df['net'] = (1 + chg_df['chg']).cumprod()
    chg_df = chg_df.reset_index(drop=False)
    chg_df['date_time'] = pd.to_datetime(chg_df['date_time'])
    chg_df = chg_df.set_index(['date_time'])
    chg_df.ix[:, ['net']].plot()
    sharpe_ratio = yearsharpRatio(chg_df['net'].tolist(), 1)
    ann_return = annROR(chg_df['net'].tolist(), 1)
    max_drawdown = maxRetrace(chg_df['net'].tolist(), 1)
    title_str = 'profolio sharpe %.2f ann_return %.2f max_drawdown %.2f' % (
        sharpe_ratio, 100 * ann_return, 100 * max_drawdown)
    plt.title(title_str)
    plt.savefig(fold_path + 'fig/' + 'profolio.png')
    plt.show()

    state_df = pd.DataFrame(ret)
    print(state_df)
    state_df['胜率'] = state_df['盈利次数'] / state_df['trading_times']
    state_df['盈亏比'] = -state_df['平均盈利'] / state_df['平均亏损']
    state_df['开仓中枢过滤'] = '无中枢过滤'
    state_df['开仓确认'] = '蓝线反转'
    state_df['平仓有无背离'] = '无背离'
    state_df['模型'] = mode
    state_df.to_excel(fold_path + 'state_singal_symbol_' + str(fee) + '.xlsx', encoding='gbk')



        # state_df.append(ret)
    # state_df = pd.concat(state_df)
    # state_df['胜率'] = state_df['盈利次数'] / state_df['trading_times']
    # state_df['盈亏比'] = -state_df['平均盈利'] / state_df['平均亏损']
    # state_df['开仓中枢过滤'] = '无中枢过滤'
    # state_df['开仓确认'] = '蓝线反转'
    # state_df['平仓有无背离'] = '无背离'
    # state_df['模型'] = mode
    # print(state_df)
    #
    # state_df.to_excel(fold_path + 'state_winR_odd.xlsx', encoding='gbk')

