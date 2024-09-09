import MetaTrader5 as mt5


ea_magic_number = 9986989 # if you want to give every bot a unique identifier

def get_info(symbol):
    mt5.initialize()
    info=mt5.symbol_info(symbol)
    return info

def open_trade(action, symbol, lot, sl_points, tp_points, deviation,comment):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5ordersend_py
    '''
    # prepare the buy request structure
    symbol_info = get_info(symbol)
    # mt5.initialize()
    if action.lower() == 'buy':
        trade_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    elif action.lower() =='sell':
        trade_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    point = mt5.symbol_info(symbol).point

    buy_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "price": price,
        # "sl": price - sl_points * point,
        # "tp": price + tp_points * point,
        "deviation": deviation,
        "magic": ea_magic_number,
        "comment": comment,
        # "type_time": mt5.ORDER_TIME_GTC, # good till cancelled
        # "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    # send a trading request
    result = mt5.order_send(buy_request)
    return result, buy_request

def close_trade(action, symbol, position_id):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5ordersend_py
    '''
    # create a close request
    mt5.initialize()
    # symbol = buy_request['symbol']
    if action == 'buy':
        trade_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    elif action =='sell':
        trade_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    # position_id=result.order
    lot = 1.0
    open_orders = mt5.orders_get(symbol=symbol)
    open_trades = mt5.positions_get()
    his = mt5.history_deals_get(position=817062966)
    for i in his:
        print(str(i))
    # for i in open_orders:
    #     print("Order :" + i)
    # for j in open_trades:
    #     print("trade :" + str(j))
    close_request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "position": position_id,
        "price": price,
        # "deviation": deviation,
        "magic": ea_magic_number,
        # "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC, # good till cancelled
        # "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    # send a close request
    result = mt5.order_send(close_request)
    return  result


# This is how I would execute the order

# result, buy_request = open_trade('BUY', 'USDCADm', 1.0, 0, 0, 20,'125942024')
# print(result, buy_request)
# close_trade(action, buy_request, position_id, deviation, comment)
result = close_trade('sell','USDCADm', 817062967)
# print(result)
