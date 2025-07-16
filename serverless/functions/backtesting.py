import json

import talib

from serverless.functions.backtesting import Strategy
from backtesting.lib import crossover

from utils.logger import logger


def get_config():
    # retrieve config from generated file
    with open("config.json") as f:
        result = json.load(f)
    return result


class BaseStrategy(Strategy):
    config = get_config()


class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 30
    n2 = 60

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(talib.SMA, self.data.Close, self.n1)
        self.sma2 = self.I(talib.SMA, self.data.Close, self.n2)

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            if self._broker._cash > 0:
                self.buy(size=int(self._broker._cash * 0.01))

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


class MacdStrategy(Strategy):
    nslow = 40
    nfast = 15
    signal = 15

    def init(self):
        self.macd, self.signal, _ = self.I(
            talib.MACD, self.data.Close, self.nslow, self.nfast, self.signal
        )

    def next(self):
        if crossover(self.macd, self.signal):
            self.position.close()
            if self._broker._cash > 0:
                self.buy(size=int(self._broker._cash * 0.01))
        elif crossover(self.signal, self.macd):
            self.position.close()
            self.sell()


class BollingerBandsStrategy(Strategy):
    n = 20
    k = 2

    def init(self):
        self.upper, self.middle, self.lower = self.I(
            talib.BBANDS, self.data.Close, self.n, self.k
        )

    def next(self):
        if self.data.Close[-1] < self.lower[-1]:
            self.position.close()
            if self._broker._cash > 0:
                self.buy(size=int(self._broker._cash * 0.01))
        elif self.data.Close[-1] > self.upper[-1]:
            self.position.close()
            self.sell()


class RsiStrategy(Strategy):
    # Define the RSI period as a class variable for later optimization
    rsi_period = 18
    rsi_overbought = 78
    rsi_oversold = 25

    def init(self):
        # Precompute the RSI
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)

    def next(self):
        # If RSI crosses above the oversold threshold, buy the asset
        if self.rsi[-1] < self.rsi_oversold and self.rsi[-2] >= self.rsi_oversold:
            self.position.close()
            if self._broker._cash > 0:
                self.buy(size=int(self._broker._cash * 0.01))

        # If RSI crosses below the overbought threshold, sell the asset
        elif self.rsi[-1] > self.rsi_overbought and self.rsi[-2] <= self.rsi_overbought:
            self.position.close()
            self.sell()


def handler(event, context):
    logger.info("handle backtesting")

    # for any given product_id i want to run all the strategies
    # for the past 15 minutes

    # get historical data
    # for product_id

    return {"statusCode": 200}
