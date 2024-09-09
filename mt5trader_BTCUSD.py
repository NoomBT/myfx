import MetaTrader5 as mt5
import os, math, time, datetime, bisect


print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)




if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()



def run(side,comment,symbol,deviation,upperbound,lowerbound,ORDER_DIST,ORDER_UNIT):
    while True:

        # สร้างโซนเทรด ขอบบน-ล่าง
        def CreateInventory(upperbound, lowerbound, order_dist):
            inventory = list()
            inventory_size = int((upperbound - lowerbound) / order_dist)

            for idx in range(0, inventory_size):
                inventory.append(lowerbound + (idx * order_dist))

            return inventory

        # ส่วนแรกคือการ Request ขอ Order ที่เราเปิดไว้ และ Trades หรือออเดอร์ที่เปิดอยู่
        inventory = CreateInventory(upperbound, lowerbound, ORDER_DIST)
        open_trades = mt5.positions_get(symbol=symbol)  # get open positions
        open_orders = mt5.orders_get(symbol=symbol)  # list of orders

        # จากนั้นเอาราคาที่เปิดของทั้ง Orders และ Trades มารวมกัน และแสดงผลออกมาเป็น ระดับราคาที่เรามี Orders หรือ Trades อยู่
        open_trades_price = [float(position.price_open) for position in open_trades if position.comment == comment]
        open_orders_price = [float(position.price_open) for position in open_orders if position.comment == comment]
        placed_prices = open_trades_price + open_orders_price
        placed_prices = sorted(placed_prices)
        print(f'[{datetime.datetime.now()}] '
              f'Open Orders {len(open_orders_price)} '
              f'and Open Trades {len(open_trades_price)}.')
        # print(placed_prices)

        # ส่วนที่สองคือการ Request ขอราคาของ Instrument ที่เรากำหนดไว้ จาก code อ้างอิงราคาตาม ask price
        mt5.symbol_select(symbol, True)
        symbol_info_tick = mt5.symbol_info_tick(symbol)
        point = mt5.symbol_info(symbol).point
        current_price = (symbol_info_tick.bid + symbol_info_tick.ask) / 2

        # เมื่อเราได้ข้อมูลที่เพียงพอกับการทำงานแล้ว เราจะเริ่มให้ระบบทำงานโดยการไล่เช็คทุกๆราคาที่เราสนใจ
        # (ราคาที่ได้มาจาก CreateInventory) ว่า ณ ราคานั้น เรามี Orders หรือ Trades เปิดไว้หรือเปล่า
        # ถ้าไม่มี Trades หรือ Orders อยู่ที่ราคานั้น แปลได้ว่า
        # 1) อาจจะไม่เคยเปิด Order ตรงนี้เลย
        # หรือ 2) Order ที่เคยเปิดไว้ตรงนี้ได้ Take Profit ไปแล้ว
        # เราก็จะทำการเติม Order ที่ราคานี้เข้าไปใหม่
        # ส่วนกรณีที่เราเจอว่ามี Trades หรือ Orders อยู่ในบริเวณระดับราคานี้ เราก็จะไม่เปิด Order เพิ่ม ตาม Requirement ของเรา

        # วนเช็คทุกราคาที่เราสนใจ (inventory price)
        for idx, price in enumerate(inventory):
            # ทำการคำนวณช่วงราคาที่จะตรวจสอบ ตัวอย่างคือ
            # ถ้าราคาอยู่ที่ 100 และตั้งค่าไว้ว่าแต่ละ order ต้องห่างกัน 10
            # เราจะทำการค้นหาว่ามี Orders หรือ Trades ที่ช่วงราคาตั้งแต่ 95-105
            lower = price - (ORDER_DIST / 2)
            upper = price + (ORDER_DIST / 2)
            # print(lower,upper)
            lower_i = bisect.bisect_left(placed_prices, lower)
            # print(lower_i)

            upper_i = bisect.bisect_right(placed_prices, upper, lo=lower_i)
            # print(upper_i)

            nearest_price = placed_prices[lower_i:upper_i]
            print(f"current_price {current_price}, idx {idx}, price {price}, nearest_price {nearest_price}")

            # ถ้าไม่มี Order หรือ Trades อยู่ในช่วงราคานี้ เราจะทำการ เปิด Order
            if not nearest_price:
                # ถ้าราคาที่เราจะเปิด Order อยู่สูงกว่าราคาปัจจุบัน เราจะเปิด STOP ORDER (สำหรับกรณี Buy)
                if side == "BUY" or side == "BUY AND SELL":
                    if price > current_price:
                        # ทำการจัดเตรียมข้อมูลที่ใช้ในการเปิด Order
                        request = {
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": symbol,
                            "type": mt5.ORDER_TYPE_BUY_STOP,
                            # "tp": float(price + ORDER_DIST),
                            "price": float(price),
                            "volume": float(ORDER_UNIT),
                            "comment": "BUY",
                            "deviation": deviation,
                            "magic": 4289,
                            "type_filling": mt5.ORDER_FILLING_IOC
                        }

                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print('place STOP_ORDER @{} TP[{}]'.format(price, price + ORDER_DIST))


                    # ถ้าราคาที่เราจะเปิด Order อยู่ต่ำกว่าราคาปัจจุบัน เราจะเปิด LIMIT ORDER (สำหรับกรณี Buy)
                    else:
                        # ทำการจัดเตรียมข้อมูลที่ใช้ในการเปิด Order
                        # print('buylimit')
                        request = {
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": symbol,
                            "type": mt5.ORDER_TYPE_BUY_LIMIT,
                            # "tp": float(price + ORDER_DIST),
                            "price": float(price),
                            "volume": float(ORDER_UNIT),
                            "comment": "BUY",
                            "deviation": deviation,
                            "magic": 4289,
                            "type_filling": mt5.ORDER_FILLING_IOC

                        }

                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print('place LIMIT_ORDER @{} TP[{}]'.format(price, price + ORDER_DIST))

                if side == "SELL" or side == "BUY AND SELL":
                    if price < current_price:
                        # ทำการจัดเตรียมข้อมูลที่ใช้ในการเปิด Order
                        request = {
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": symbol,
                            "type": mt5.ORDER_TYPE_SELL_STOP,
                            # "tp": float(price - ORDER_DIST),
                            "price": float(price),
                            "volume": float(ORDER_UNIT),
                            "comment": "SELL",
                            "deviation": deviation,
                            "magic": 4289,
                            "type_filling": mt5.ORDER_FILLING_IOC
                        }

                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f'place Sell STOP_ORDER @{price} TP[{price - ORDER_DIST}]')


                    # ถ้าราคาที่เราจะเปิด Order อยู่ต่ำกว่าราคาปัจจุบัน เราจะเปิด LIMIT ORDER (สำหรับกรณี Buy)
                    else:
                        # ทำการจัดเตรียมข้อมูลที่ใช้ในการเปิด Order
                        print('SELL Limit')
                        request = {
                            "action": mt5.TRADE_ACTION_PENDING,
                            "symbol": symbol,
                            "type": mt5.ORDER_TYPE_SELL_LIMIT,
                            # "tp": float(price - ORDER_DIST),
                            "price": float(price),
                            "volume": float(ORDER_UNIT),
                            "comment": "SELL",
                            "deviation": deviation,
                            "magic": 4289,
                            "type_filling": mt5.ORDER_FILLING_IOC

                        }

                        result = mt5.order_send(request)
                        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                            print(f'place Sell LIMIT_ORDER @{price} TP[{price - ORDER_DIST}]')

            # จะเห็นว่าหากมี Orders หรือ Trades อยู่ในช่วงที่เราสนใจเราจะข้าม Code ในส่วนด้านบนมายังจุดนี้
            # และเลื่อนไปยังจุดราคาอื่นเพื่อเช็คต่อไป
        print("==========================================================================")
        time.sleep(5)

if __name__ == "__main__":
    account_info = mt5.account_info()
    login_number = account_info.login
    balance = account_info.balance
    equity = account_info.equity
    print('login: ', login_number)
    print('balance: ', balance)
    print('equity: ', equity)
    run(side="SELL",comment = "SELL", symbol = "USDJPYm", deviation = 20,  upperbound = 142.350,  lowerbound = 142.250,
        ORDER_DIST = 0.005, ORDER_UNIT=0.5)
