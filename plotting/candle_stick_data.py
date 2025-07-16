import pandas as pd
import plotly.graph_objects as go
import requests

def plot_btc_candlestick():
    # Load the exported CSV
    df = pd.read_csv("btc_data.csv")

    # Convert timestamp to datetime (if it's a UNIX timestamp string)
    df['start'] = pd.to_datetime(df['timestamp'], unit='s')

    fig = go.Figure(data=[go.Candlestick(
        x=df['start'],
        open=df['open'].astype(float),
        high=df['high'].astype(float),
        low=df['low'].astype(float),
        close=df['close'].astype(float)
    )])

    fig.update_layout(title="BTC Candlestick Chart", xaxis_title="Time", yaxis_title="Price")
    fig.write_image("btc_candlestick.png")  # Save as PNG
    fig.show()  # Show interactive chart


def generate_candlestick_csv(product_id, start, end, interval):
    url = f"https://api.coinbase.com/api/v3/brokerage/market/products/{product_id}/candles"
    query_params = {
        'start': start,
        'end': end,
        'granularity': interval
    }
    response = requests.get(url, params=query_params)
    data = response.json()["candles"]
    print(f"Data received: {data}")  # Print first 5 entries for debugging
    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=[
        'open', 'high', 'low', 'close', 'volume', 'start'
    ])

    # Convert timestamp to datetime
    df['start'] = pd.to_datetime(df['start'], unit='ms')
    print(df.shape)  # Print the first few rows for debugging
    # Save to CSV
    df.to_csv("btc_data.csv", index=False)
