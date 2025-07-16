from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from ulid import ULID



class Candle(BaseModel):
    id: ULID = Field(default_factory=ULID)
    symbol: str
    open_time: int
    close_time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class Price(BaseModel):
    id: ULID = Field(default_factory=ULID)
    symbol: str
    price: Decimal
    timestamp: int


class Position(BaseModel):
    global_product_id: str = Field(..., alias="global_product_id")
    component_id: str = Field(..., alias="component_id")

    position_id: str = Field(..., alias="position_id")
    ttl: Optional[int] = Field(..., alias="ttl")
    strategy_term: Optional[str] = Field(default="MEDIUM_TERM", alias="strategy_term")

    # Order data
    order_id: str = Field(..., alias="order_id")
    product_id: str = Field(..., alias="product_id")
    user_id: str = Field(..., alias="user_id")
    client_order_id: str = Field(..., alias="client_order_id")
    order_configuration: Optional[dict] = Field(..., alias="order_configuration")
    edit_history: Optional[list] = Field(..., alias="edit_history")
    leverage: str = Field(..., alias="leverage")
    margin_type: str = Field(..., alias="margin_type")
    retail_portfolio_id: str = Field(..., alias="retail_portfolio_id")
    originating_order_id: str = Field(..., alias="originating_order_id")
    attached_order_id: str = Field(..., alias="attached_order_id")
    attached_order_configuration: Optional[str] = Field(
        ..., alias="attached_order_configuration"
    )
    side: str = Field(..., alias="side")

    status: str = Field(..., alias="status")
    time_in_force: str = Field(..., alias="time_in_force")
    created_time: str = Field(..., alias="created_time")
    completion_percentage: str = Field(..., alias="completion_percentage")
    filled_size: Decimal = Field(..., alias="filled_size")
    average_filled_price: Decimal = Field(..., alias="average_filled_price")
    fee: str = Field(..., alias="fee")
    number_of_fills: str = Field(..., alias="number_of_fills")
    filled_value: str = Field(..., alias="filled_value")
    pending_cancel: bool = Field(..., alias="pending_cancel")
    size_in_quote: bool = Field(..., alias="size_in_quote")
    total_fees: Decimal = Field(..., alias="total_fees")
    size_inclusive_of_fees: bool = Field(..., alias="size_inclusive_of_fees")
    total_value_after_fees: Decimal = Field(..., alias="total_value_after_fees")
    trigger_status: str = Field(..., alias="trigger_status")
    order_type: str = Field(..., alias="order_type")
    reject_reason: str = Field(..., alias="reject_reason")
    settled: bool = Field(..., alias="settled")
    product_type: str = Field(..., alias="product_type")
    reject_message: str = Field(..., alias="reject_message")
    cancel_message: str = Field(..., alias="cancel_message")
    order_placement_source: str = Field(..., alias="order_placement_source")
    outstanding_hold_amount: str = Field(..., alias="outstanding_hold_amount")
    is_liquidation: bool = Field(..., alias="is_liquidation")
    last_fill_time: Optional[str] = Field(..., alias="last_fill_time")
