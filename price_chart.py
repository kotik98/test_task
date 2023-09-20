import pandas as pd
import numpy as np
import plotly.graph_objects as go

def update_candle(open, high, low, row):
    """Utility function for updating the candle

    Keyword arguments:

    open -- open value for current candle

    high -- current high value

    low -- current low value

    row -- new row with price for updating
    """
    if open == -1:
        open = row['PRICE']
    if row['PRICE'] > high:
        high = row['PRICE']
    if row['PRICE'] < low:
        low = row['PRICE']

    return open, high, low 

def parse_csv(path, interval):
    """Parse data from csv file to pandas Dataframe with candles

    Keyword arguments:

    path -- path to csv file

    interval -- candles interval in minutes
    """
    df = pd.DataFrame(pd.read_csv(path))
    df['TS'] = pd.to_datetime(df['TS'])
    candles = pd.DataFrame(columns=[ 'Time', 'Open', 'High', 'Low', 'Close' ])
    curr_interval_end = df.iloc[0]['TS'] + pd.Timedelta(minutes=interval)
    open = high = -1
    low = float("inf")

    for index, row in df.iterrows():
        # for last row we will close current candle anyway
        if index == len(df) - 1:
            close = row['PRICE']
            open, high, low = update_candle(open, high, low, row)
            candles.loc[len(candles)] = { 'Time': row['TS'], 'Open': open, 'High': high, 'Low': low, 'Close': close }

        elif row['TS'] > curr_interval_end:
            close = df.iloc[index - 1]['PRICE']
            candles.loc[len(candles)] = { 'Time': df.iloc[index - 1]['TS'], 'Open': open, 'High': high, 'Low': low, 'Close': close }
            curr_interval_end += pd.Timedelta(minutes=interval)
            
            # because leaky charts are useless
            if row['TS'] > curr_interval_end:
                raise Exception('too small interval for candles')

            open, high, low = update_candle(-1, -1, float("inf"), row)

        else:
            open, high, low = update_candle(open, high, low, row)

    return candles

def calc_ema(prices, period, weighting_factor=0.2):
    """Calculating ema following the formula: EMA = (Price(t) * k) + (EMA(y) * (1 – k))

        Where:

        Price(t) is the price at time (t)

        EMA(y) is the previous period’s EMA

        k is the smoothing constant, which is typically set at 2/(n+1) where n is the number of periods for the EMA
    """
    ema = np.zeros(len(prices))

    # initial nonzero value
    sma = np.mean(prices[:period])
    ema[period - 1] = sma

    # using the formula
    for i in range(period, len(prices)):
        ema[i] = (prices[i] * weighting_factor) + (ema[i - 1] * (1 - weighting_factor))
    return ema


if __name__ == "__main__":

    period = 14
    cline_interval = 600
    candles = parse_csv('prices.csv', cline_interval)
    ema = calc_ema(candles['Close'], period)
    # some visualization
    fig = go.Figure(data=[go.Candlestick(x=candles['Time'],
                    open=candles['Open'],
                    high=candles['High'],
                    low=candles['Low'],
                    close=candles['Close'])])

    fig.add_trace(go.Scatter(
            x=candles['Time'][period:],
            y=ema[period:],
            fill=None,
            mode='lines',
            line_color='blue',
            name='ema'))

    fig.show()