from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
import MetaTrader5 as mt5

# connect to MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# request 1000 ticks
symbolsticks = mt5.copy_ticks_from("BTCUSDm", datetime(2024,9,6), 1000, mt5.COPY_TICKS_ALL)

# PLOT
# create DataFrame out of the obtained data
ticks_frame = pd.DataFrame(symbolsticks)
# print(ticks_frame)

# convert time in seconds into the datetime format
ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

# display ticks on the chart
plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
plt.plot(ticks_frame['time'], ticks_frame['bid'], 'b-', label='bid')

# display the legends
plt.legend(loc='upper left')

# add the header
plt.title('BTCUSD ticks')

# display the chart
plt.show()