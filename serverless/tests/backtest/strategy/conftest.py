import json
import pytest

from http import HTTPStatus
from utils.common import Env


@pytest.fixture
def last_buy_positions():
    return [
        {
            "order_id": "order-uuid",
            "product_id": "BTC-USD",
            "user_id": "user-uuid",
            "order_configuration": {
                "market_market_ioc": {
                    "quote_size": "1.5",
                    "rfq_enabled": False,
                    "rfq_disabled": False,
                }
            },
            "side": "BUY",
            "client_order_id": "client-order-uuid",
            "status": "FILLED",
            "time_in_force": "IMMEDIATE_OR_CANCEL",
            "created_time": "2024-10-29T18:26:03.426421Z",
            "completion_percentage": "100",
            "filled_size": "0.0000203165253428",
            "average_filled_price": "72956.049999980014299",
            "fee": "",
            "number_of_fills": "2",
            "filled_value": "1.4822134387351779",
            "pending_cancel": False,
            "size_in_quote": True,
            "total_fees": "0.0177865612648221",
            "size_inclusive_of_fees": True,
            "total_value_after_fees": "1.5",
            "trigger_status": "INVALID_ORDER_TYPE",
            "order_type": "MARKET",
            "reject_reason": "REJECT_REASON_UNSPECIFIED",
            "settled": True,
            "product_type": "SPOT",
            "reject_message": "",
            "cancel_message": "",
            "order_placement_source": "RETAIL_ADVANCED",
            "outstanding_hold_amount": "0",
            "is_liquidation": False,
            "last_fill_time": "2024-10-29T18:26:03.533549546Z",
            "edit_history": [],
            "leverage": "",
            "margin_type": "UNKNOWN_MARGIN_TYPE",
            "retail_portfolio_id": "retail-portfolio-uuid",
            "originating_order_id": "",
            "attached_order_id": "",
            "attached_order_configuration": None,
        }
    ]


@pytest.fixture
def last_sell_positions():
    return [
        {
            "order_id": "order-uuid",
            "product_id": "BTC-USD",
            "user_id": "user-uuid",
            "order_configuration": {
                "market_market_ioc": {
                    "base_size": "1.5",
                    "rfq_enabled": False,
                    "rfq_disabled": False,
                }
            },
            "side": "SELL",
            "client_order_id": "client-order-uuid",
            "status": "FILLED",
            "time_in_force": "IMMEDIATE_OR_CANCEL",
            "created_time": "2024-10-29T18:26:03.426421Z",
            "completion_percentage": "100",
            "filled_size": "0.0000203165253428",
            "average_filled_price": "72956.049999980014299",
            "fee": "",
            "number_of_fills": "2",
            "filled_value": "1.4822134387351779",
            "pending_cancel": False,
            "size_in_quote": True,
            "total_fees": "0.0177865612648221",
            "size_inclusive_of_fees": True,
            "total_value_after_fees": "1.5",
            "trigger_status": "INVALID_ORDER_TYPE",
            "order_type": "MARKET",
            "reject_reason": "REJECT_REASON_UNSPECIFIED",
            "settled": True,
            "product_type": "SPOT",
            "reject_message": "",
            "cancel_message": "",
            "order_placement_source": "RETAIL_ADVANCED",
            "outstanding_hold_amount": "0",
            "is_liquidation": False,
            "last_fill_time": "2024-10-29T18:26:03.533549546Z",
            "edit_history": [],
            "leverage": "",
            "margin_type": "UNKNOWN_MARGIN_TYPE",
            "retail_portfolio_id": "retail-portfolio-uuid",
            "originating_order_id": "",
            "attached_order_id": "",
            "attached_order_configuration": None,
        }
    ]


@pytest.fixture
def sqs_strategy_sell_event(last_sell_positions):
    return {
        "Records": [
            {
                "messageId": "c80e8021-a70a-42c7-a470-796e1186f753",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": json.dumps(
                    {
                        "correlation_id": "01D9GQZ2R1T0Z6ZQ0X6W0M1Z4Z",
                        "provider": "COINBASE",
                        "product_id": "BTC-USD",
                        "portfolio": {
                            "portfolio": {
                                "name": "test",
                                "uuid": "portfolio-uuid",
                                "type": "CONSUMER",
                                "deleted": False,
                            },
                            "portfolio_balances": {
                                "total_balance": {
                                    "value": "10000.23",
                                    "currency": "USD",
                                },
                                "total_futures_balance": {
                                    "value": "0",
                                    "currency": "USD",
                                },
                                "total_cash_equivalent_balance": {
                                    "value": "14.45",
                                    "currency": "USD",
                                },
                                "total_crypto_balance": {
                                    "value": "19.78",
                                    "currency": "USD",
                                },
                                "futures_unrealized_pnl": {
                                    "value": "0",
                                    "currency": "USD",
                                },
                                "perp_unrealized_pnl": {
                                    "value": "0",
                                    "currency": "USD",
                                },
                            },
                            "spot_positions": [
                                {
                                    "asset": "USD",
                                    "account_uuid": "account-uuid",
                                    "total_balance_fiat": 14.451879,
                                    "total_balance_crypto": 14.451879,
                                    "available_to_trade_fiat": 14.451879,
                                    "allocation": 0.42210168,
                                    "cost_basis": {
                                        "value": "14.4518782",
                                        "currency": "USD",
                                    },
                                    "asset_img_url": "",
                                    "is_cash": True,
                                    "average_entry_price": {
                                        "value": "1",
                                        "currency": "USD",
                                    },
                                    "asset_uuid": "",
                                    "available_to_trade_crypto": 14.451879,
                                    "unrealized_pnl": 0,
                                    "available_to_transfer_fiat": 14.451879,
                                    "available_to_transfer_crypto": 14.451879,
                                    "asset_color": "",
                                    "account_type": "ACCOUNT_TYPE_FIAT",
                                },
                                {
                                    "asset": "BTC",
                                    "account_uuid": "account-uuid",
                                    "total_balance_fiat": 17.957708,
                                    "total_balance_crypto": 0.00019549,
                                    "available_to_trade_fiat": 17.957708,
                                    "allocation": 0.5244978,
                                    "cost_basis": {
                                        "value": "13.50000000000684847199999829645944",
                                        "currency": "USD",
                                    },
                                    "asset_img_url": "https://dynamic-assets.coinbase.com/e785e0181f1a23a30d9476038d9be91e9f6c63959b538eabbc51a1abc8898940383291eede695c3b8dfaa1829a9b57f5a2d0a16b0523580346c6b8fab67af14b/asset_icons/b57ac673f06a4b0338a596817eb0a50ce16e2059f327dc117744449a47915cb2.png",
                                    "is_cash": False,
                                    "average_entry_price": {
                                        "value": "68237.5635980966492348",
                                        "currency": "USD",
                                    },
                                    "asset_uuid": "asset-uuid",
                                    "available_to_trade_crypto": 0.00019549,
                                    "unrealized_pnl": 4.4577074,
                                    "available_to_transfer_fiat": 17.957708,
                                    "available_to_transfer_crypto": 0.00019549,
                                    "asset_color": "#F7931A",
                                    "account_type": "ACCOUNT_TYPE_WALLET",
                                },
                                {
                                    "asset": "RPL",
                                    "account_uuid": "a37d36a4-7279-5d65-b709-fc7385451a49",
                                    "total_balance_fiat": 1.8283211,
                                    "total_balance_crypto": 0.18965986,
                                    "available_to_trade_fiat": 1.8283211,
                                    "allocation": 0.05340049,
                                    "cost_basis": {
                                        "value": "1.99530884476868382055978618631603",
                                        "currency": "USD",
                                    },
                                    "asset_img_url": "https://dynamic-assets.coinbase.com/72e5ba829999c87e8ae53eaa31a6553272e796c0dfefe263319b62585abffdd3ff730550e3db1f3a549dfa4a93bb5b76f10036d4cdfd7b3ac63ac2e4e9546fd3/asset_icons/04c6e3d4d94d09fef38322551bdebb0865eb3e0d910d0a89a02d2a207f1ace68.png",
                                    "is_cash": False,
                                    "average_entry_price": {
                                        "value": "10.4420939925424786",
                                        "currency": "USD",
                                    },
                                    "asset_uuid": "asset-uuid",
                                    "available_to_trade_crypto": 0.18965986,
                                    "unrealized_pnl": -0.16698779,
                                    "available_to_transfer_fiat": 1.8283211,
                                    "available_to_transfer_crypto": 0.18965986,
                                    "asset_color": "#FF9774",
                                    "account_type": "ACCOUNT_TYPE_WALLET",
                                },
                            ],
                            "perp_positions": [],
                            "futures_positions": [],
                        },
                        "positions": last_sell_positions,
                        "product": {"product_id": "BTC-USD"},
                        "config": {
                            "config_id": "01D9GQZ2R1T0Z6ZQ0X6W0M1Z4Z",
                            "config_name": "BTC-USD",
                            "toggle": True,
                            "profit_target": 1.01,
                            "config_quote_min_size": 10,
                            "config_quote_max_size": 100,
                            "buy": "market_market_ioc",
                            "sell": "market_market_ioc",
                            "base_increment": 0.000001,
                            "quote_increment": 0.01,
                            "base_min_size": 0.00001,
                            "base_max_size": 100,
                            "status": "online",
                            "cancel_only": False,
                            "limit_only": False,
                            "post_only": False,
                            "trading_disabled": False,
                            "strategy_type": "momentum",
                        },
                    }
                ),
            }
        ]
    }


@pytest.fixture
def sqs_strategy_buy_event(last_buy_positions):
    return {
        "Records": [
            {
                "messageId": "c80e8021-a70a-42c7-a470-796e1186f753",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy0a...",
                "body": json.dumps(
                    {
                        "correlation_id": "01D9GQZ2R1T0Z6ZQ0X6W0M1Z4Z",
                        "provider": "COINBASE",
                        "product_id": "BTC-USD",
                        "portfolio": {
                            "portfolio": {
                                "name": "test",
                                "uuid": "portfolio-uuid",
                                "type": "CONSUMER",
                                "deleted": False,
                            },
                            "portfolio_balances": {
                                "total_balance": {
                                    "value": "10000.23",
                                    "currency": "USD",
                                },
                                "total_futures_balance": {
                                    "value": "0",
                                    "currency": "USD",
                                },
                                "total_cash_equivalent_balance": {
                                    "value": "14.45",
                                    "currency": "USD",
                                },
                                "total_crypto_balance": {
                                    "value": "19.78",
                                    "currency": "USD",
                                },
                                "futures_unrealized_pnl": {
                                    "value": "0",
                                    "currency": "USD",
                                },
                                "perp_unrealized_pnl": {
                                    "value": "0",
                                    "currency": "USD",
                                },
                            },
                            "spot_positions": [
                                {
                                    "asset": "USD",
                                    "account_uuid": "account-uuid",
                                    "total_balance_fiat": 14.451879,
                                    "total_balance_crypto": 14.451879,
                                    "available_to_trade_fiat": 14.451879,
                                    "allocation": 0.42210168,
                                    "cost_basis": {
                                        "value": "14.4518782",
                                        "currency": "USD",
                                    },
                                    "asset_img_url": "",
                                    "is_cash": True,
                                    "average_entry_price": {
                                        "value": "1",
                                        "currency": "USD",
                                    },
                                    "asset_uuid": "",
                                    "available_to_trade_crypto": 14.451879,
                                    "unrealized_pnl": 0,
                                    "available_to_transfer_fiat": 14.451879,
                                    "available_to_transfer_crypto": 14.451879,
                                    "asset_color": "",
                                    "account_type": "ACCOUNT_TYPE_FIAT",
                                },
                                {
                                    "asset": "BTC",
                                    "account_uuid": "account-uuid",
                                    "total_balance_fiat": 17.957708,
                                    "total_balance_crypto": 0.00019549,
                                    "available_to_trade_fiat": 17.957708,
                                    "allocation": 0.5244978,
                                    "cost_basis": {
                                        "value": "13.50000000000684847199999829645944",
                                        "currency": "USD",
                                    },
                                    "asset_img_url": "https://dynamic-assets.coinbase.com/e785e0181f1a23a30d9476038d9be91e9f6c63959b538eabbc51a1abc8898940383291eede695c3b8dfaa1829a9b57f5a2d0a16b0523580346c6b8fab67af14b/asset_icons/b57ac673f06a4b0338a596817eb0a50ce16e2059f327dc117744449a47915cb2.png",
                                    "is_cash": False,
                                    "average_entry_price": {
                                        "value": "68237.5635980966492348",
                                        "currency": "USD",
                                    },
                                    "asset_uuid": "asset-uuid",
                                    "available_to_trade_crypto": 0.00019549,
                                    "unrealized_pnl": 4.4577074,
                                    "available_to_transfer_fiat": 17.957708,
                                    "available_to_transfer_crypto": 0.00019549,
                                    "asset_color": "#F7931A",
                                    "account_type": "ACCOUNT_TYPE_WALLET",
                                },
                                {
                                    "asset": "RPL",
                                    "account_uuid": "a37d36a4-7279-5d65-b709-fc7385451a49",
                                    "total_balance_fiat": 1.8283211,
                                    "total_balance_crypto": 0.18965986,
                                    "available_to_trade_fiat": 1.8283211,
                                    "allocation": 0.05340049,
                                    "cost_basis": {
                                        "value": "1.99530884476868382055978618631603",
                                        "currency": "USD",
                                    },
                                    "asset_img_url": "https://dynamic-assets.coinbase.com/72e5ba829999c87e8ae53eaa31a6553272e796c0dfefe263319b62585abffdd3ff730550e3db1f3a549dfa4a93bb5b76f10036d4cdfd7b3ac63ac2e4e9546fd3/asset_icons/04c6e3d4d94d09fef38322551bdebb0865eb3e0d910d0a89a02d2a207f1ace68.png",
                                    "is_cash": False,
                                    "average_entry_price": {
                                        "value": "10.4420939925424786",
                                        "currency": "USD",
                                    },
                                    "asset_uuid": "asset-uuid",
                                    "available_to_trade_crypto": 0.18965986,
                                    "unrealized_pnl": -0.16698779,
                                    "available_to_transfer_fiat": 1.8283211,
                                    "available_to_transfer_crypto": 0.18965986,
                                    "asset_color": "#FF9774",
                                    "account_type": "ACCOUNT_TYPE_WALLET",
                                },
                            ],
                            "perp_positions": [],
                            "futures_positions": [],
                        },
                        "positions": last_buy_positions,
                        "product": {"product_id": "BTC-USD"},
                        "config": {
                            "config_id": "01D9GQZ2R1T0Z6ZQ0X6W0M1Z4Z",
                            "config_name": "BTC-USD",
                            "toggle": True,
                            "profit_target": 1.01,
                            "config_quote_min_size": 10,
                            "config_quote_max_size": 100,
                            "buy": "market_market_ioc",
                            "sell": "market_market_ioc",
                            "base_increment": 0.000001,
                            "quote_increment": 0.01,
                            "base_min_size": 0.00001,
                            "base_max_size": 100,
                            "status": "online",
                            "cancel_only": False,
                            "limit_only": False,
                            "post_only": False,
                            "trading_disabled": False,
                            "strategy_type": "momentum",
                        },
                    }
                ),
            }
        ]
    }


@pytest.fixture
def mock_get_provider_product_ticker(requests_mock, product_id, get_ticker_response):
    return requests_mock.get(
        f"{Env.PROVIDER_URL}/api/v3/brokerage/products/{product_id}/ticker",
        json=get_ticker_response,
        status_code=HTTPStatus.OK,
    )
