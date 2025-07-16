from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from enum import Enum

from ulid import ULID


class BaseConfiguration(BaseModel):
    provider: str = Field(..., alias="provider")
    product_id: str = Field(..., alias="product_id")
    config_id: Optional[str] = Field(default=str(ULID()), alias="config_id")
    config_name: Optional[str] = Field(default=f"{config_id}", alias="config_name")
    toggle: Optional[bool] = Field(default=True, alias="toggle")


class OrderConfigurationType(str, Enum):
    market_market_ioc = "market_market_ioc"
    sor_limit_ioc = "sor_limit_ioc"
    limit_limit_gtc = "limit_limit_gtc"
    limit_limit_gtd = "limit_limit_gtd"
    limit_limit_fok = "limit_limit_fok"
    stop_limit_stop_limit_gtc = "stop_limit_stop_limit_gtc"
    stop_limit_stop_limit_gtd = "stop_limit_stop_limit_gtd"
    trigger_bracket_gtc = "trigger_bracket_gtc"


class StrategyConfiguration(BaseConfiguration):
    strategy_type: Optional[str] = Field(default="momentum", alias="strategy_type")
    profit_target: Decimal = Field(default=Decimal("5.0"), alias="profit_target")
    config_quote_min_size: Decimal = Field(
        default=Decimal("5.0"), alias="config_quote_min_size"
    )
    config_quote_max_size: Decimal = Field(
        default=Decimal("5.0"), alias="config_quote_max_size"
    )
    maxmin_pct_threshold: Decimal = Field(
        default=Decimal("1.5"), alias="maxmin_pct_threshold"
    )
    buy: Optional[OrderConfigurationType] = Field(
        default=OrderConfigurationType.market_market_ioc.value,
        alias="buy",
    )
    sell: Optional[OrderConfigurationType] = Field(
        default=OrderConfigurationType.market_market_ioc.value,
        alias="sell",
    )

    # model_dump but without global_product_id and service_id
    def model_dump(self):
        return {
            "strategy_type": self.strategy_type,
            "profit_target": self.profit_target,
            "config_quote_min_size": self.config_quote_min_size,
            "config_quote_max_size": self.config_quote_max_size,
            "maxmin_pct_threshold": self.maxmin_pct_threshold,
            "buy": self.buy,
            "sell": self.sell,
        }


class ProductConfiguration(StrategyConfiguration):
    base_increment: Decimal = Field(default=Decimal("0.01"))
    quote_increment: Decimal = Field(default=Decimal("0.01"))
    quote_min_size: Decimal = Field(default=Decimal("0.01"))
    quote_max_size: Decimal = Field(default=Decimal("10000000.0"))
    base_min_size: Decimal = Field(default=Decimal("0.01"))
    base_max_size: Decimal = Field(default=Decimal("10000000.0"))
    status: str = Field(default="online")
    cancel_only: bool = Field(default=False)
    limit_only: bool = Field(default=False)
    post_only: bool = Field(default=False)
    trading_disabled: bool = Field(default=False)
    view_only: bool = Field(default=False)
    is_disabled: bool = Field(default=False)

    # model_dump but without global_product_id and service_id
    def model_dump(self):
        return {
            "base_increment": self.base_increment,
            "quote_increment": self.quote_increment,
            "quote_min_size": self.quote_min_size,
            "quote_max_size": self.quote_max_size,
            "base_min_size": self.base_min_size,
            "base_max_size": self.base_max_size,
            "status": self.status,
            "cancel_only": self.cancel_only,
            "limit_only": self.limit_only,
            "post_only": self.post_only,
            "trading_disabled": self.trading_disabled,
            "view_only": self.view_only,
            "is_disabled": self.is_disabled,
        }
