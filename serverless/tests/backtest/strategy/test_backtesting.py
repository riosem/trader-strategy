# from backtesting import Backtest
# from backtesting.test import GOOG

# from functions.backtesting import (
#     SmaCross,
#     MacdStrategy,
#     BollingerBandsStrategy,
#     RsiStrategy,
# )
import pytest
import requests

# import pandas as pd
from decimal import Decimal


# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.metrics import mean_squared_error


def fit_quadratic(data):
    x = np.arange(len(data))
    coefficients = np.polyfit(x, data, deg=2)
    return coefficients


def compare_trends(coeff1, coeff2):
    return mean_squared_error(coeff1, coeff2)


def find_similar_trends(current_data, historical_data, window_size):
    current_coeff = fit_quadratic(current_data)
    similarities = []

    for i in range(len(historical_data) - window_size + 1):
        segment = historical_data[i : i + window_size]
        segment_coeff = fit_quadratic(segment)
        similarity = compare_trends(current_coeff, segment_coeff)
        similarities.append((i, similarity))

    similarities.sort(key=lambda x: x[1])
    return similarities


# similarities = find_similar_trends(current_data, historical_data, window_size)

data_to_test_monthly = [
    {"start": 1696827600, "end": 1699333200, "granularity": 8},
    {"start": 1699333200, "end": 1701838800, "granularity": 8},
    {"start": 1701838800, "end": 1704344400, "granularity": 8},
    {"start": 1704344400, "end": 1706850000, "granularity": 8},
    {"start": 1706850000, "end": 1709355600, "granularity": 8},
    {"start": 1709355600, "end": 1711861200, "granularity": 8},
    {"start": 1711861200, "end": 1714366800, "granularity": 8},
    {"start": 1714366800, "end": 1716872400, "granularity": 8},
    {"start": 1716872400, "end": 1719378000, "granularity": 8},
    {"start": 1719378000, "end": 1721883600, "granularity": 8},
    {"start": 1706835600, "end": 1709341200, "granularity": 8},
    {"start": 1709341200, "end": 1711846800, "granularity": 8},
    {"start": 1711846800, "end": 1714352400, "granularity": 8},
    {"start": 1714352400, "end": 1716858000, "granularity": 8},
    {"start": 1716858000, "end": 1719363600, "granularity": 8},
]


CASH_AMOUNT = 100_000


@pytest.fixture()
def get_historical_data_optimize():
    def wrapper(product_id, **kwargs):
        # dat = yf.Ticker(product_id)
        # df = dat.history(period="1d", interval="1m")

        url = f"https://api.coinbase.com/api/v3/brokerage/market/products/{product_id}/candles"

        data = []
        for params in data_to_test_monthly:
            response = requests.get(url, params=params)
            data.extend(response.json()["candles"])

        df = pd.DataFrame(
            data,
            columns=["start", "low", "high", "open", "close", "volume"],
        )
        df.columns = [col.capitalize() for col in df.columns]

        df["Start"] = pd.to_datetime(df["Start"], unit="s")
        for col in df.columns:
            if col != "Start":
                df[col] = df[col].apply(lambda x: float(Decimal(x)))

        # Sort the DataFrame by the 'Start' column
        df = df.sort_values(by="Start")

        return df

    return wrapper


@pytest.fixture()
def get_historical_data_run():
    def wrapper(product_id, **kwargs):
        # dat = yf.Ticker(product_id)
        # df = dat.history(period="1d", interval="1m")

        url = f"https://api.coinbase.com/api/v3/brokerage/market/products/{product_id}/candles"

        response = requests.get(url, params=kwargs)

        df = pd.DataFrame(
            response.json()["candles"],
            columns=["start", "low", "high", "open", "close", "volume"],
        )
        df.columns = [col.capitalize() for col in df.columns]

        df["Start"] = pd.to_datetime(df["Start"], unit="s")
        for col in df.columns:
            if col != "Start":
                df[col] = df[col].apply(lambda x: float(Decimal(x)))

        # Sort the DataFrame by the 'Start' column
        df = df.sort_values(by="Start")

        return df

    return wrapper


@pytest.mark.parametrize("product_id", ["BTC-USD"])
class TestStrategyOptimize:
    CASH_AMOUNT = 100_000

    @pytest.mark.backtest
    def test_sma_optimize(self, get_historical_data_optimize, product_id):
        data = get_historical_data_optimize(product_id)

        sma_backtest = Backtest(data, SmaCross, cash=self.CASH_AMOUNT, commission=0.01)
        sma_results = sma_backtest.optimize(
            n1=range(5, 30, 5),
            n2=range(10, 70, 5),
            maximize="Equity Final [$]",
            constraint=lambda param: param.n1 < param.n2,
        )

        # assert sma_results["Equity Final [$]"] > 0
        print(sma_results["Equity Final [$]"])
        print(sma_results["_strategy"])

    @pytest.mark.backtest
    def test_macd_optimize(self, get_historical_data_optimize, product_id):
        data = get_historical_data_optimize(product_id)

        macd_backtest = Backtest(
            data, MacdStrategy, cash=self.CASH_AMOUNT, commission=0.01
        )

        macd_results = macd_backtest.optimize(
            nslow=range(20, 50, 5),
            nfast=range(5, 20, 5),
            signal=range(5, 20, 5),
            maximize="Equity Final [$]",
            constraint=lambda param: param.nslow > param.nfast,
        )

        # assert macd_results["Equity Final [$]"] > 0
        print(macd_results["Equity Final [$]"])
        print(macd_results["_strategy"])

    @pytest.mark.backtest
    def test_bband_optimize(self, get_historical_data_optimize, product_id):
        data = get_historical_data_optimize(product_id)

        bband_backtest = Backtest(
            data, BollingerBandsStrategy, cash=self.CASH_AMOUNT, commission=0.01
        )

        bband_results = bband_backtest.optimize(
            n=range(20, 50, 5), k=range(1, 3), maximize="Equity Final [$]"
        )

        assert bband_results["Equity Final [$]"] > 0
        print(bband_results)
        print(bband_results["_strategy"])

    @pytest.mark.backtest
    def test_rsi_optimize(self, get_historical_data_optimize, product_id):
        data = get_historical_data_optimize(product_id)
        rsi_backtest = Backtest(
            data, RsiStrategy, cash=self.CASH_AMOUNT, commission=0.01
        )

        rsi_results = rsi_backtest.optimize(
            rsi_period=range(14, 31, 1),
            rsi_overbought=range(70, 81, 1),
            rsi_oversold=range(20, 31, 1),
            maximize="Equity Final [$]",
        )

        assert rsi_results["Equity Final [$]"] > 0
        print(rsi_results)
        print(rsi_results["_strategy"])


@pytest.mark.parametrize("product_id", ["BTC-USD"])
@pytest.mark.parametrize("params", data_to_test_monthly)
class TestStrategyRun:
    @pytest.mark.backtest
    def test_run_sma_strategy(self, get_historical_data_run, product_id, params):
        data = get_historical_data_run(product_id, **params)

        sma_backtest = Backtest(data, SmaCross, cash=CASH_AMOUNT, commission=0.01)
        sma_results = sma_backtest.run()

        # assert sma_results["Equity Final [$]"] > CASH_AMOUNT
        print(sma_results["Equity Final [$]"])
        # print(sma_results["_trades"])

    @pytest.mark.backtest
    def test_run_macd_strategy(self, get_historical_data_run, product_id, params):
        data = get_historical_data_run(product_id, **params)

        macd_backtest = Backtest(data, MacdStrategy, cash=CASH_AMOUNT, commission=0.01)
        macd_results = macd_backtest.run()

        # assert macd_results["Equity Final [$]"] > CASH_AMOUNT
        print(macd_results["Equity Final [$]"])
        # print(macd_results["_trades"])

    @pytest.mark.backtest
    def test_run_bband_strategy(self, get_historical_data_run, product_id, params):
        data = get_historical_data_run(product_id, **params)

        bband_backtest = Backtest(
            data, BollingerBandsStrategy, cash=CASH_AMOUNT, commission=0.01
        )
        bband_results = bband_backtest.run()

        # assert bband_results["Equity Final [$]"] > CASH_AMOUNT
        print(bband_results["Equity Final [$]"])
        # print(bband_results["_trades"])

    @pytest.mark.backtest
    def test_run_rsi_strategy(self, get_historical_data_run, product_id, params):
        data = get_historical_data_run(product_id, **params)

        rsi_backtest = Backtest(data, RsiStrategy, cash=CASH_AMOUNT, commission=0.01)
        rsi_results = rsi_backtest.run()

        # assert rsi_results["Equity Final [$]"] > CASH_AMOUNT
        print(rsi_results["Equity Final [$]"])
        # print(rsi_results["_trades"])
