# Trading Data Plotting and Visualization

This directory contains utilities for generating, processing, and visualizing candlestick trading data for backtesting and analysis purposes.

## Structure

```
plotting/
├── candle_stick_data.py          # Core candlestick data processing logic
├── historical_data_generator.py  # Historical trading data generation utilities
├── requirements.in               # Source Python dependencies
├── requirements.txt              # Compiled Python dependencies
└── README.md                     # This documentation
```

## Key Components

### **candle_stick_data.py**
- **Purpose**: Core module for processing and manipulating candlestick trading data
- **Features**:
  - Candlestick data structure definitions
  - OHLCV (Open, High, Low, Close, Volume) data processing
  - Data validation and normalization
  - Integration with trading strategy algorithms

### **historical_data_generator.py**
- **Purpose**: Generates historical trading data for backtesting and analysis
- **Features**:
  - Historical data fetching from trading APIs
  - Data aggregation and time-series processing
  - Sample data generation for testing
  - Export capabilities for strategy backtesting

## Usage

### Install Dependencies

```sh
# Install from compiled requirements
pip install -r requirements.txt

# Or install from source requirements
pip install -r requirements.in
pip-compile requirements.in  # to update requirements.txt
```

### Generate Historical Data

```python
from historical_data_generator import HistoricalDataGenerator

# Initialize generator
generator = HistoricalDataGenerator(
    product_id="BTC-USD",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Generate historical candlestick data
historical_data = generator.generate_data()
```

### Process Candlestick Data

```python
from candle_stick_data import CandlestickProcessor

# Initialize processor
processor = CandlestickProcessor()

# Process raw trading data into candlestick format
candlesticks = processor.process_data(raw_data)

# Validate and clean data
cleaned_data = processor.validate_and_clean(candlesticks)
```

## Integration with Strategy System

This plotting directory integrates with the broader **#trader-strategy** system:

- **Data Source**: Provides clean, validated data for strategy backtesting
- **Visualization**: Supports strategy performance analysis and pattern visualization
- **Testing**: Generates sample data for unit tests and strategy validation
- **Analysis**: Enables technical analysis and pattern recognition

## Dependencies

The module uses standard Python libraries for data processing and visualization:
- `pandas` for data manipulation
- `numpy` for numerical computations
- `matplotlib`/`plotly` for visualization (likely)
- Trading-specific libraries for market data processing

## Example Workflow

```python
# 1. Generate historical data
generator = HistoricalDataGenerator("BTC-USD", "2024-01-01", "2024-06-30")
data = generator.fetch_historical_data()

# 2. Process into candlestick format
processor = CandlestickProcessor()
candlesticks = processor.process_data(data)

# 3. Use with trading strategies
from serverless.functions.strategies import MomentumStrategy
strategy = MomentumStrategy(product_id="BTC-USD")
results = strategy.backtest(candlesticks)

# 4. Visualize results
processor.plot_candlesticks(candlesticks, results)
```

## Related Components

- **[../serverless/functions/strategies.py](../serverless/functions/strategies.py)**: Uses this data for strategy backtesting
- **[../indicators/](../indicators/)**: Rust-based technical indicators that process this data
- **[../../trader-data](../../trader-data)**: Real-time data collection that feeds into this system

## Testing

This module supports the broader testing framework:

```sh
# Run backtests using plotting data
./run back-tests

# Run unit tests for data processing
./run unit-tests
```

## Notes

- This directory provides the foundation for all data visualization and backtesting in the strategy system
- Generated data can be exported for use in other components of the trader ecosystem
- Supports both real historical data and synthetic data generation for testing

---

**For more information on the overall strategy system, see the main