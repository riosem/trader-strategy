class InvalidSideException(Exception):
    def __init__(self, message):
        self.message = message
        self.code = 400
        super().__init__(self.message)


class SendAssistantMessageException(Exception):
    def __init__(self, message):
        self.message = message
        self.code = 500
        super().__init__(self.message)


class MaxMinDiffPctError(Exception):
    def __init__(self, message):
        self.message = message
        self.code = 400
        super().__init__(self.message)


class AnalyzeSellPricesException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.message = message
        self.code = 500

        self.profit_amt_dlrs = kwargs.get("profit_amt_dlrs")
        self.profit_pct = kwargs.get("profit_pct")
        self.current_amt = kwargs.get("current_amt")
        self.bought_amt = kwargs.get("bought_amt")

class AnalyzeBuyPricesException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.message = message
        self.code = 500

        self.profit_amt_dlrs = kwargs.get("profit_amt_dlrs")
        self.profit_pct = kwargs.get("profit_pct")
        self.current_amt = kwargs.get("current_amt")
        self.bought_amt = kwargs.get("bought_amt")


class GetProviderCandlesException(Exception):
    def __init__(self, message):
        self.message = message
        self.code = 500
        super().__init__(self.message)


class BuyRequirementsError(Exception):
    def __init__(self, message):
        self.message = message
        self.code = 500
        super().__init__(self.message)


class SellRequirementsError(Exception):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message)
        self.message = message
        self.code = 500


class RequestedSellNoPositions(Exception):
    def __init__(self, message):
        self.message = message
        self.code = 500
        super().__init__(self.message)