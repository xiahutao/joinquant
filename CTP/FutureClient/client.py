# -*- coding: utf-8 -*-
# @Time    : 2020/6/30 10:15
# @Author  : zhangfang
from CTP.FutureClient.jz_FutureApi_lib import JzStrategy

if __name__ == "__main__":
    ip = '127.0.0.1:1114'
    api = JzStrategy('ZhangFang', ip)

    ### 查询
    fund_df = api.req_fund()
    print(fund_df)

    hold_df = api.req_hold()

    trades_df = api.req_trades()

    orders_df = api.req_orders()

    cancelable_df = api.req_cancelable()

    ### 交易部分：
    #### 1、开启enable_trade后才会交易（api.enable_trade=True）
    #### 2、交易：配置期货代码ocde、价格price、成交量vol、多空long/short、开平open/close/closetoday、策略id(如'test_001','test002')
    #### 3、撤单：需要从req_orders()中获取FrontID、SessionID、orderRef加上期货代码才可以撤单

    # api.enable_trade = True
    ### 下单代码
    code = 'rb2101'
    # 价格
    price = 3325
    # 成交量
    vol = 1
    # 多空 long short
    direction = 'long'
    # 开平 open close
    open_close = 'open'
    strategy_name = ''
    # return_order = api.send_order(code,price,vol,direction,open_close)
    return_order = api.send_order(code, price, vol, direction, open_close, strategy_name=strategy_name)
    ### 下单
    # 全撤
    api.enable_trade = True
    cancelable_df = api.req_cancelable()
    for i, cancel_orders in cancelable_df.iterrows():
        FrontID = cancel_orders['FrontID']
        SessionID = cancel_orders['SessionID']
        orderRef = cancel_orders['报单引用']
        code = cancel_orders['合约']
        api.order_cancel(FrontID, SessionID, orderRef, code)
