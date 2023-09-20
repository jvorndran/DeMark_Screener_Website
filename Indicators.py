import sys
import pandas as pd

def combo_strict(df):

    counts = pd.DataFrame(columns=["Buy Countdown", "Sell Countdown", "9_13_9_Buy", "9_13_9_Sell"])

    setup_count_buy = 0
    setup_count_sell = 0
    buy_count_started = False
    sell_count_started = False
    buy_countdown_count = 0
    sell_countdown_count = 0
    last_close_buy = 0.0
    last_close_sell = 0.0
    start_9_13_9_buy = False
    start_9_13_9_sell = False

    for i in range(4, len(df)):

        close = df['Close'].iloc[i]

        buy_9_13_9 = 0
        sell_9_13_9 = 0


        #Setup counts
        if close < df['Close'].iloc[i-4]:
            setup_count_buy += 1
        else:
            setup_count_buy = 0

        if close > df['Close'].iloc[i-4]:
            setup_count_sell += 1
        else:
            setup_count_sell = 0
        #Setup Counts


        # 9 - 13 - 9 Following a buy countdown, the market produces a bullish price flip then produces a buy setup

        if buy_countdown_count == 13 and close > df['Close'].iloc[i-4]:
            start_9_13_9_buy = True
        if start_9_13_9_buy and setup_count_buy == 9:
            buy_9_13_9 = 1
            start_9_13_9_buy = False

        if sell_countdown_count == 13 and close < df['Close'].iloc[i-4]:
            start_9_13_9_sell = True
        if start_9_13_9_sell and setup_count_sell == 9:
            sell_9_13_9 = 1
            start_9_13_9_sell = False

        # 9 - 13 - 9 Following a buy countdown, the market produces a bullish price flip then produces a buy setup



        if setup_count_buy != 0 and setup_count_buy % 9 == 0:
            last_close_buy = 0
            last_close_sell = 0
            buy_countdown_count = 0
            sell_countdown_count = 0
            buy_count_started = True
            sell_count_started = False
            setup_count_sell = 0
            setup_count_buy = 0
            start_9_13_9_sell = False
            for j in range(i - 8, i + 1):
                if df['Close'].iloc[j] <= df['Low'].iloc[j-2] and df['Low'].iloc[j] < df['Low'].iloc[j-1] and df['Close'].iloc[j] < df['Close'].iloc[j-1]:
                    if buy_countdown_count == 0:
                        buy_countdown_count += 1
                        last_close_buy = df['Close'].iloc[j]
                    elif df['Close'].iloc[j] < last_close_buy:
                        buy_countdown_count += 1
                        last_close_buy = df['Close'].iloc[j]


        if setup_count_sell != 0 and setup_count_sell % 9 == 0:
            last_close_buy = 0
            last_close_sell = 0
            buy_countdown_count = 0
            sell_countdown_count = 0
            sell_count_started = True
            buy_count_started = False
            setup_count_sell = 0
            setup_count_buy = 0
            start_9_13_9_buy = False
            for j in range(i - 8, i + 1):
                if df['Close'].iloc[j] >= df['High'].iloc[j-2] and df['High'].iloc[j] > df['High'].iloc[j-1] and df['Close'].iloc[j] > df['Close'].iloc[j-1]:
                    if sell_countdown_count == 0:
                        sell_countdown_count += 1
                        last_close_sell = df['Close'].iloc[j]
                    elif df['Close'].iloc[j] > last_close_sell:
                        sell_countdown_count += 1
                        last_close_sell = df['Close'].iloc[j]



        if buy_count_started and close <= df['Low'].iloc[i-2] and df['Low'].iloc[i] < df['Low'].iloc[i-1] and close < df['Close'].iloc[i-1] and buy_countdown_count < 13:
            if buy_countdown_count == 0:
                buy_countdown_count += 1
                last_close_buy = close
            elif close < last_close_buy:
                buy_countdown_count += 1
                last_close_buy = close


        if sell_count_started and close >= df['High'].iloc[i-2] and df['High'].iloc[i] > df['High'].iloc[i-1] and close > df['Close'].iloc[i-1] and sell_countdown_count < 13:
            if sell_countdown_count == 0:
                sell_countdown_count += 1
                last_close_sell = close
            elif close > last_close_sell:
                sell_countdown_count += 1
                last_close_sell = close


        #conservative countdown
        if buy_countdown_count == 13 and close > df['Close'].iloc[i-4]:
            buy_countdown_count = 14

        if sell_countdown_count == 13 and close < df['Close'].iloc[i-4]:
            sell_countdown_count = 14
        #conservative countdown

        new_row = pd.DataFrame({'Buy Countdown': [buy_countdown_count], 'Sell Countdown': [sell_countdown_count], '9_13_9_Buy': [buy_9_13_9], '9_13_9_Sell': [sell_9_13_9]})

        counts = pd.concat([counts, new_row], ignore_index=True)


    last_6_9_13_buy = counts['9_13_9_Buy'].tail(6)
    last_6_9_13_sell = counts['9_13_9_Sell'].tail(6)


    has_9_13_buy = 1 in last_6_9_13_buy.values
    has_9_13_sell = 1 in last_6_9_13_sell.values

    return buy_countdown_count, sell_countdown_count, has_9_13_buy, has_9_13_sell


def sequential(df):

    counts = pd.DataFrame(columns=["Buy Countdown", "Sell Countdown", "9_13_9_Buy", "9_13_9_Sell"])

    setup_count_buy = 0
    setup_count_sell = 0
    buy_count_started = False
    sell_count_started = False
    buy_countdown_count = 0
    sell_countdown_count = 0
    eight_bar = 0.0
    tdst_res = 0.0
    tdst_sup = sys.float_info.max
    start_9_13_9_buy = False
    start_9_13_9_sell = False

    for i in range(4, len(df)):

        close = df['Close'].iloc[i]

        buy_9_13_9 = 0
        sell_9_13_9 = 0

        #Setup counts
        if close < df['Close'].iloc[i-4]:
            setup_count_buy += 1
        else:
            setup_count_buy = 0

        if close > df['Close'].iloc[i-4]:
            setup_count_sell += 1
        else:
            setup_count_sell = 0
        #Setup Counts

        # 9 - 13 - 9 Following a buy countdown, the market produces a bullish price flip then produces a buy setup

        if buy_countdown_count == 13 and close > df['Close'].iloc[i-4]:
            start_9_13_9_buy = True
        if start_9_13_9_buy and setup_count_buy == 9:
            buy_9_13_9 = 1
            start_9_13_9_buy = False

        if sell_countdown_count == 13 and close < df['Close'].iloc[i-4]:
            start_9_13_9_sell = True
        if start_9_13_9_sell and setup_count_sell == 9:
            sell_9_13_9 = 1
            start_9_13_9_sell = False

        # 9 - 13 - 9 Following a buy countdown, the market produces a bullish price flip then produces a buy setup


        if setup_count_buy != 0 and setup_count_buy % 9 == 0:
            eight_bar = 0.0
            buy_countdown_count = 0
            sell_countdown_count = 0
            buy_count_started = True
            sell_count_started = False
            setup_count_sell = 0
            setup_count_buy = 0
            tdst_res = 0
            tdst_sup = sys.float_info.max
            start_9_13_9_sell = False
            for j in range(i, i - 9, -1):
                if df['High'].iloc[j] > tdst_res:
                    tdst_res = df['High'].iloc[j]


        if setup_count_sell != 0 and setup_count_sell % 9 == 0:
            eight_bar = 0.0
            buy_countdown_count = 0
            sell_countdown_count = 0
            sell_count_started = True
            buy_count_started = False
            setup_count_sell = 0
            setup_count_buy = 0
            tdst_res = 0
            tdst_sup = sys.float_info.max
            start_9_13_9_buy = False
            for j in range(i, i - 9, -1):
                if df['Low'].iloc[j] < tdst_sup:
                    tdst_sup = df['Low'].iloc[j]

        #Trades Above TDST
        if buy_count_started and df['High'].iloc[i] > tdst_res:
            buy_count_started = False
            buy_countdown_count = 0
        if sell_count_started and df['Low'].iloc[i] < tdst_sup:
            sell_count_started = False
            sell_countdown_count = 0
        #Trades Above TDST



        if buy_count_started and buy_countdown_count < 13:
            if close < df['Low'].iloc[i-2] and buy_countdown_count != 12:
                buy_countdown_count += 1
                if buy_countdown_count == 8:
                    eight_bar = close
            elif close < df['Low'].iloc[i-2] and buy_countdown_count == 12 and close < eight_bar:
                buy_count_started = False
                buy_countdown_count += 1


        if sell_count_started and sell_countdown_count < 13:
            if close > df['High'].iloc[i-2] and sell_countdown_count != 12:
                sell_countdown_count += 1
                if sell_countdown_count == 8:
                    eight_bar = close
            elif close > df['High'].iloc[i-2] and sell_countdown_count == 12 and close > eight_bar:
                sell_count_started = False
                sell_countdown_count += 1

        #conservative countdown
        if buy_countdown_count == 13 and close > df['Close'].iloc[i-4]:
            buy_countdown_count = 14

        if sell_countdown_count == 13 and close < df['Close'].iloc[i-4]:
            sell_countdown_count = 14
        #conservative countdown

        new_row = pd.DataFrame({'Buy Countdown': [buy_countdown_count], 'Sell Countdown': [sell_countdown_count], '9_13_9_Buy': [buy_9_13_9], '9_13_9_Sell': [sell_9_13_9]})

        counts = pd.concat([counts, new_row], ignore_index=True)


    last_6_9_13_buy = counts['9_13_9_Buy'].tail(6)
    last_6_9_13_sell = counts['9_13_9_Sell'].tail(6)

    has_9_13_buy = 1 in last_6_9_13_buy.values
    has_9_13_sell = 1 in last_6_9_13_sell.values

    return buy_countdown_count, sell_countdown_count, has_9_13_buy, has_9_13_sell