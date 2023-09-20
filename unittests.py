import unittest
import pandas as pd
from price_chart import *

class TestPriceChartMethods(unittest.TestCase):

    def test_candles_parsing(self):
        # see test.csv
        cline_interval = 30
        candles = parse_csv('test.csv', cline_interval)
        # check candles amount
        self.assertEqual(len(candles), 2)
        # check candles values
        self.assertListEqual(candles.loc[0].to_list()[1:], [100, 105, 98, 101])
        self.assertListEqual(candles.loc[1].to_list()[1:], [200, 200, 200, 200])
        # too small candle interval
        with self.assertRaises(Exception):
            candles = parse_csv('test.csv', 5)


    def test_ema_calculating(self):
        prices = [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 148, 143, 144, 140, 139, 137, 135, 140]
        period = 5

        # Calculate the EMA with a period of 5 days using pandas
        df = pd.DataFrame({'close': prices})
        df['ema'] = df['close'].ewm(span=period, adjust=False, min_periods=period).mean()

        self.assertAlmostEqual(list(calc_ema(prices, period, 2/(period + 1)))[-1], df['ema'].to_list()[-1], delta=0.01)

if __name__ == '__main__':
    unittest.main()