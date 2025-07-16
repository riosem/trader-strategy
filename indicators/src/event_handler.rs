use lambda_runtime::{ LambdaEvent, Error};
use serde_json::{Value, json};
use lambda_runtime::tracing::info;
use crate::historical_data::BTC_DATA;
// import from historical_data.rs
use crate::types::Candle;


use ta::indicators::SimpleMovingAverage;
// use ta::indicators::MovingAverageConvergenceDivergence as Macd;
//  RelativeStrengthIndex, BollingerBands};
use ta::{Next};
use serde::Deserialize;




#[derive(Debug, Deserialize)]
struct Position {
    global_product_id: String,
    component_id: String,
    position_id: String,
    ttl: Option<i64>,
    strategy_term: Option<String>,

    // Order data
    order_id: String,
    product_id: String,
    user_id: String,
    client_order_id: String,
    order_configuration: Option<serde_json::Value>,
    edit_history: Option<Vec<serde_json::Value>>,
    leverage: String,
    margin_type: String,
    retail_portfolio_id: String,
    originating_order_id: String,
    attached_order_id: String,
    attached_order_configuration: Option<String>,
    side: String,

    status: String,
    time_in_force: String,
    created_time: String,
    completion_percentage: String,
    filled_size: String,
    average_filled_price: String,
    fee: String,
    number_of_fills: String,
    filled_value: String,
    pending_cancel: bool,
    size_in_quote: bool,
    total_fees: String,
    size_inclusive_of_fees: bool,
    total_value_after_fees: String,
    trigger_status: String,
    order_type: String,
    reject_reason: String,
    settled: bool,
    product_type: String,
    reject_message: String,
    cancel_message: String,
    order_placement_source: String,
    outstanding_hold_amount: String,
    is_liquidation: bool,
    last_fill_time: Option<String>,
}

fn sma_cross_strategy(data: &[Candle], n1: usize, n2: usize) -> Vec<String> {
    let mut sma1 = SimpleMovingAverage::new(n1).unwrap();
    let mut sma2 = SimpleMovingAverage::new(n2).unwrap();
    let mut position = 0; // 0 = flat, 1 = long, -1 = short
    let mut signals = Vec::new();

    for candle in data {
        let price = candle.close.parse::<f64>().unwrap_or(0.0);
        let sma1_val = sma1.next(price);
        let sma2_val = sma2.next(price);
        // println!("sma1: {}, sma2: {}", sma1.next(price), sma2.next(price));

        if sma1_val > sma2_val && position <= 0 {
            println!("Buy at price: {}", price);
            signals.push(format!("Buy at price: {}", price));
            position = 1;
        } else if sma1_val < sma2_val && position >= 0 {
            println!("Sell at price: {}", price);
            signals.push(format!("Sell at price: {}", price));
            position = -1;
        }
    }

    signals
}

fn sma_cross_strategy_with_positions(
    data: &[Candle],
    n1: usize,
    n2: usize,
    positions: &[Position],
) -> Vec<String> {
    let mut sma1 = SimpleMovingAverage::new(n1).unwrap();
    let mut sma2 = SimpleMovingAverage::new(n2).unwrap();
    let mut open_positions: Vec<(f64, f64)> = positions.iter()
        .filter_map(|p| {
            let price = p.average_filled_price.parse::<f64>().ok()?;
            let size = p.filled_size.parse::<f64>().ok()?;
            Some((price, size))
        })
        .collect();
    let mut signals = Vec::new();

    let mut prev_sma1 = None;
    let mut prev_sma2 = None;

    for candle in data {
        let price = candle.close.parse::<f64>().unwrap_or(0.0);
        let curr_sma1 = sma1.next(price);
        let curr_sma2 = sma2.next(price);

        if let (Some(p_sma1), Some(p_sma2)) = (prev_sma1, prev_sma2) {
            // Bullish crossover: Buy signal
            if p_sma1 <= p_sma2 && curr_sma1 > curr_sma2 {
                let size = 0.001;
                signals.push(format!("Buy at price: {} size: {}", price, size));
                open_positions.push((price, size));
            }
            // Bearish crossover: Sell signal (close oldest position)
            else if p_sma1 >= p_sma2 && curr_sma1 < curr_sma2 && !open_positions.is_empty() {
                let (entry_price, size) = open_positions.remove(0);
                signals.push(format!("Sell at price: {} size: {} entry: {}", price, size, entry_price));
            }
        }

        // Stop-loss/take-profit for all open positions
        open_positions.retain(|(entry, size)| {
            if price <= entry * 0.95 {
                signals.push(format!("Stop-loss sell at price: {} size: {} entry: {}", price, size, entry));
                false
            } else if price >= entry * 1.10 {
                signals.push(format!("Take-profit sell at price: {} size: {} entry: {}", price, size, entry));
                false
            } else {
                true
            }
        });

        prev_sma1 = Some(curr_sma1);
        prev_sma2 = Some(curr_sma2);
    }

    signals
}

fn backtest_sma_strategy(
    data: &[Candle],
    n1: usize,
    n2: usize,
    positions: &[Position],
    initial_balance: f64,
) -> serde_json::Value {
    let mut balance = initial_balance;
    let mut in_position = false;
    let mut trade_count = 0;
    let mut entry_price = 0.0;
    let mut open_position_entry = None;

    let signals = sma_cross_strategy_with_positions(&data, n1, n2, &positions);

    if !positions.is_empty() {
        in_position = true; // Assume we start with an open position
    }
        

    for (i, signal) in signals.iter().enumerate() {
        let price = data.get(i).map(|c| c.close.parse::<f64>().unwrap_or(0.0)).unwrap_or(0.0);

        if signal.contains("Buy at price") && !in_position {
            entry_price = price;
            in_position = true;
            open_position_entry = Some(price);
        } else if signal.contains("Sell at price") && in_position {
            // Simple PnL calculation: sell - buy
            balance += price - entry_price;
            in_position = false;
            trade_count += 1;
            open_position_entry = None;
        }
    }

    // If still in position, report it as open, with unrealized PnL
    let (open_position, unrealized_pnl) = if in_position {
        let last_price = data.last().map(|c| c.close.parse::<f64>().unwrap_or(0.0)).unwrap_or(0.0);
        let entry = open_position_entry.unwrap_or(0.0);
        (true, last_price - entry)
    } else {
        (false, 0.0)
    };

    json!({ 
        "Final Balance": balance,
        "Initial Balance": initial_balance,
        "Profit/Loss": balance - initial_balance,
        "Number of Trades": trade_count,
        // "Number of Winning Trades": signals.iter().filter(|s| s.contains("Sell at price")).count(),
        // "Number of Losing Trades": signals.iter().filter(|s| s.contains("Buy at price")).count(),
        // "Winning Percentage": signals.iter().filter(|s| s.contains("Sell at price")).count() as f64 / signals.len().max(1) as f64 * 100.0,
        "Open Position": open_position,
        "Open Position Entry Price": open_position_entry,
        "Unrealized PnL": unrealized_pnl,
        "Signals": signals,
    })
}

fn macd_strategy(data: &[Candle], short_period: usize, long_period: usize, signal_period: usize) -> Vec<String> {
    let mut macd = Macd::new(short_period, long_period, signal_period).unwrap();
    let mut position = 0; // 0 = flat, 1 = long, -1 = short
    let mut signals = Vec::new();

    for candle in data {
        let price = candle.close.parse::<f64>().unwrap_or(0.0);
        let macd_val = macd.next(price);

        if macd_val > 0.0 && position <= 0 {
            info!("Buy at price: {}", price);
            signals.push(format!("Buy at price: {}", price));
            position = 1;
        } else if macd_val < 0.0 && position >= 0 {
            info!("Sell at price: {}", price);
            signals.push(format!("Sell at price: {}", price));
            position = -1;
        }
        
    }

    signals
}


pub async fn function_handler(event: LambdaEvent<Value>) -> Result<Value, Error> {
    // Access the event payload with event.payload
    info!("Received event: {:?}", event.payload);

    /*
    PARAMS
    historical_data: A JSON array of candle data, where each candle is an object with a "close" field.
    Example:
    [
        {"close": 1.0},
        {"close": 2.0},
        {"close": 3.0}
    ]
    
    n1: The period for the first Simple Moving Average (SMA).
    n2: The period for the second Simple Moving Average (SMA).
    */

    let data: Vec<Candle> = serde_json::from_value(event.payload["historical_data"].clone())
        .map_err(|e| Error::from(e))?;
    let n1: usize = event.payload["n1"].as_u64().unwrap_or(30) as usize;
    let n2: usize = event.payload["n2"].as_u64().unwrap_or(60) as usize;
    // let positions: Vec<Position> = serde_json::from_value(event.payload["positions"].clone())
    //     .map_err(|e| Error::from(e))?;

    if data.len() < n2 {
        return Err(Error::from("Insufficient data for the specified SMA periods"));
    }

    if n1 >= n2 {
        return Err(Error::from("n1 must be less than n2"));
    }

    let sma_signals = sma_cross_strategy(&data, n1, n2)
        .into_iter()
        .map(|s| format!("SMA Signal: {}", s))
        .collect::<Vec<String>>();
    // let macd_signals = macd_strategy(&data, 12, 26, 9, &positions)
    //     .into_iter()
    //     .map(|s| format!("MACD Signal: {}", s))
    //     .collect::<Vec<String>>();
    // let signals = [sma_signals, macd_signals].concat();
    let signals = sma_signals; // For now, only using SMA signals
    for signal in signals {
        println!("{}", signal);
    }

    Ok(json!({ "message": "Invoked directly!", "input": event.payload }))
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::historical_data::BTC_DATA;

    #[test]
    fn test_sma_cross_strategy_buy_and_sell_signal() {
        // This data will cause SMA(2) to cross above SMA(3) (buy), then below (sell)
        let data = BTC_DATA.clone();
        let signals = sma_cross_strategy(&data, 2, 3);
        assert!(signals.iter().any(|s| s.contains("Buy at price")), "Should generate a buy signal");
        assert!(signals.iter().any(|s| s.contains("Sell at price")), "Should generate a sell signal");
    }

    #[test]
    fn test_sma_cross_strategy_buy_and_sell_signal_with_positions() {
        // This data will cause SMA(2) to cross above SMA(3) (buy), then below (sell)
        let data = BTC_DATA.clone();
        let positions = vec![
            Position {
                global_product_id: "prod1".to_string(),
                component_id: "comp1".to_string(),
                position_id: "pos1".to_string(),
                ttl: None,
                strategy_term: None,
                order_id: "order1".to_string(),
                product_id: "prod1".to_string(),
                user_id: "user1".to_string(),
                client_order_id: "client1".to_string(),
                order_configuration: None,
                edit_history: None,
                leverage: "1x".to_string(),
                margin_type: "isolated".to_string(),
                retail_portfolio_id: "portfolio1".to_string(),
                originating_order_id: "orig_order1".to_string(),
                attached_order_id: "attached_order1".to_string(),
                attached_order_configuration: None,
                side: "buy".to_string(),
                status: "filled".to_string(),
                time_in_force: "GTC".to_string(),
                created_time: "2023-10-01T00:00:00Z".to_string(),
                completion_percentage: "100%".to_string(),
                filled_size: "10.0".to_string(),
                average_filled_price: "1.0".to_string(),
                fee: "0.1".to_string(),
                number_of_fills: "1".to_string(),
                filled_value: "10.0".to_string(),
                pending_cancel: false,
                size_in_quote: true,
                total_fees: "0.1".to_string(),
                size_inclusive_of_fees: true,
                total_value_after_fees: "9.9".to_string(),
                trigger_status: "none".to_string(),
                order_type: "market".to_string(),
                reject_reason: "".to_string(),
                settled: true,
                product_type: "spot".to_string(),
                reject_message: "".to_string(),
                cancel_message: "".to_string(),
                order_placement_source: "api".to_string(),
                outstanding_hold_amount: "0.0".to_string(),
                is_liquidation: false,
                last_fill_time: None,
            }
        ];
        let signals = sma_cross_strategy_with_positions(&data, 2, 3, &positions);
    }

    #[test]
    fn test_sma_windows(){
        let mut balance = 20000.0;
        let data: Vec<Candle> = BTC_DATA.clone();
        let reversed_data: Vec<_> = BTC_DATA.iter().rev().cloned().collect();
        let n1s_fast: Vec<usize> = vec![5, 7, 9, 10, 12, 14, 20];
        let n2s_slow: Vec<usize> = vec![20, 30, 50, 100, 200];
        let positions = vec![
            Position {
                global_product_id: "COINBASE.BTC.USD".to_string(),
                component_id: "01JVWS6123454K4284GCHABRS8.ENTRY".to_string(),
                position_id: "01JVWS6XYJS19MECX98765VXJ".to_string(),
                ttl: None,
                strategy_term: None,
                order_id: "c3d3d39e-6697-496b-9d8e-10131dd12345".to_string(),
                product_id: "BTC-USD".to_string(),
                user_id: "user1".to_string(),
                client_order_id: "client1".to_string(),
                order_configuration: None,
                edit_history: None,
                leverage: "1x".to_string(),
                margin_type: "isolated".to_string(),
                retail_portfolio_id: "portfolio1".to_string(),
                originating_order_id: "orig_order1".to_string(),
                attached_order_id: "attached_order1".to_string(),
                attached_order_configuration: None,
                side: "buy".to_string(),
                status: "filled".to_string(),
                time_in_force: "GTC".to_string(),
                created_time: "2023-10-01T00:00:00Z".to_string(),
                completion_percentage: "100%".to_string(),
                filled_size: "0.00187398".to_string(),
                average_filled_price: "111095.09".to_string(),
                fee: "0.5".to_string(),
                number_of_fills: "1".to_string(),
                filled_value: "208.1899767582".to_string(),
                pending_cancel: false,
                size_in_quote: true,
                total_fees: "0.8327599070328".to_string(),
                size_inclusive_of_fees: true,
                total_value_after_fees: "999.5".to_string(),
                trigger_status: "none".to_string(),
                order_type: "market".to_string(),
                reject_reason: "".to_string(),
                settled: true,
                product_type: "spot".to_string(),
                reject_message: "".to_string(),
                cancel_message: "".to_string(),
                order_placement_source: "api".to_string(),
                outstanding_hold_amount: "0.0".to_string(),
                is_liquidation:false,
                last_fill_time : None
            }
        ];

        for n1 in &n1s_fast {
            for n2 in &n2s_slow {
                if n1 >= n2 {
                    continue; // Skip invalid SMA periods
                }
                println!("Testing SMA with n1: {}, n2: {}", n1, n2);
                
                let results = backtest_sma_strategy(&reversed_data, *n1, *n2, &positions, balance);
                println!("Backtest Results: {:?}", results);
            }
        }

        info!("Backtest Results: {:?}", results);
        println!("Backtest Results: {:?}", results);
        assert!(results["Final Balance"].as_f64().unwrap() > balance, "Final balance should be greater than initial balance");
    }

    
}
