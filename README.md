# Trader Strategy Service

A microservice for managing and executing trading strategies in the trader ecosystem. This service provides a flexible framework for implementing, backtesting, and executing various trading algorithms.

## 🚀 Features

- **Strategy Management**: Create, update, and manage multiple trading strategies with version control
- **Backtesting Engine**: Test strategies against historical market data with detailed analytics
- **Real-time Execution**: Execute strategies in live trading environments with millisecond precision
- **Risk Management**: Built-in risk controls, position sizing, and portfolio-level protection
- **Performance Analytics**: Track strategy performance metrics, statistics, and risk-adjusted returns
- **Signal Generation**: Generate buy/sell signals based on sophisticated strategy logic
- **Multi-timeframe Support**: Support for various timeframes (1s, 1m, 5m, 15m, 1h, 4h, 1d, 1w)
- **Technical Indicators**: Integration with popular technical analysis indicators

## 🛠️ Technology Stack

- **Backend Language**: Python 3.9+ or Rust (depending on implementation)
- **Message Queue**: SQS
- **Testing**: pytest (Python) or cargo test (Rust)

## 🚀 Getting Started

### Prerequisites

**For Python Implementation:**
- Python 3.9 or higher
- pip or poetry for package management
- Virtual environment (recommended)

**For Rust Implementation:**
- Rust 1.70+ with Cargo
- System dependencies as required

### Quick Start

**Python Setup:**
```bash
# Clone the repository
git clone <repository-url> trader-strategy
cd trader-strategy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run tests
pytest
```

**Rust Setup:**
```bash
# Clone the repository
git clone <repository-url> trader-strategy
cd trader-strategy

# Build the project
cargo build

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run tests
cargo test

# Start development server
cargo run
```

## 📊 Strategy Development
### Creating a Custom Strategy
**Rust Implementation:**
```rust
use crate::strategies::BaseStrategy;
use crate::indicators::{SMA, RSI};
use crate::types::{MarketData, Signal, SignalType};
use async_trait::async_trait;

pub struct CustomStrategy {
    sma: SMA,
    rsi: RSI,
    rsi_overbought: f64,
    rsi_oversold: f64,
}

impl CustomStrategy {
    pub fn new(sma_period: usize, rsi_period: usize, 
               rsi_overbought: f64, rsi_oversold: f64) -> Self {
        Self {
            sma: SMA::new(sma_period),
            rsi: RSI::new(rsi_period),
            rsi_overbought,
            rsi_oversold,
        }
    }
}

#[async_trait]
impl BaseStrategy for CustomStrategy {
    async fn analyze(&mut self, market_data: &[MarketData]) -> Result<Signal, Box<dyn std::error::Error>> {
        let sma_value = self.sma.calculate(market_data)?;
        let rsi_value = self.rsi.calculate(market_data)?;
        let current_price = market_data.last().unwrap().close;

        let signal_type = if current_price > sma_value && rsi_value < self.rsi_oversold {
            SignalType::Buy
        } else if current_price < sma_value && rsi_value > self.rsi_overbought {
            SignalType::Sell
        } else {
            SignalType::Hold
        };

        Ok(Signal {
            signal_type,
            strength: if signal_type != SignalType::Hold { 0.8 } else { 0.0 },
            price: current_price,
            timestamp: chrono::Utc::now(),
            metadata: Some(format!("sma: {}, rsi: {}", sma_value, rsi_value)),
        })
    }
}
```

### Available Technical Indicators

#### Trend Indicators
- Simple Moving Average (SMA)

```
## 🧪 Testing

### Running Tests

**Python:**
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_strategies.py

# Run tests in watch mode
pytest-watch
```

**Rust:**
```bash
# Run all tests
cargo test

# Run unit tests only
cargo test --lib

# Run integration tests
cargo test --test integration

# Run with output
cargo test -- --nocapture

# Run specific test
cargo test test_moving_average_strategy

# Run tests with coverage (requires cargo-tarpaulin)
cargo tarpaulin --out Html
```

### Backtesting

**Python:**
```bash
# Run backtest for specific strategy
python scripts/backtest.py --strategy=ma_cross_v1 --start=2023-01-01 --end=2023-12-31

# Run backtest with custom parameters
python scripts/backtest.py --config=./config/backtest.json

# Generate performance report
python scripts/generate_report.py --backtest-id=backtest_123
```

**Rust:**
```bash
# Run backtest for specific strategy
cargo run --bin backtest -- --strategy=ma_cross_v1 --start=2023-01-01 --end=2023-12-31

# Run backtest with custom parameters
cargo run --bin backtest -- --config=./config/backtest.json
```

## 🚀 Future Enhancements

### Short-term (Next 3 months)
- **Future Indicators**:
    - Exponential Moving Average (EMA)
    - Weighted Moving Average (WMA)
    - Hull Moving Average (HMA)

    #### Momentum Indicators
    - Relative Strength Index (RSI)
    - Moving Average Convergence Divergence (MACD)
    - Stochastic Oscillator
    - Williams %R

    #### Volatility Indicators
    - Bollinger Bands
    - Average True Range (ATR)
    - Keltner Channels

    #### Volume Indicators
    - On-Balance Volume (OBV)
    - Volume Weighted Average Price (VWAP)
    - Money Flow Index (MFI)

- **Machine Learning Integration**: 
  - Support for ML-based strategy components using scikit-learn/PyTorch (Python) or Candle/SmartCore (Rust)
  - Feature engineering pipeline for market data
  - Model training and validation framework
  - AutoML for strategy parameter optimization

- **Strategy Optimization**: 
  - Genetic algorithm-based parameter optimization
  - Walk-forward analysis for robust backtesting
  - Multi-objective optimization (returns vs. risk)
  - Sensitivity analysis and parameter stability testing

- **Paper Trading Mode**: 
  - Risk-free strategy testing with live data
  - Realistic slippage and latency simulation
  - Performance comparison with live trading
  - Strategy validation before deployment

### Medium-term (3-6 months)
- **Multi-asset Strategies**: 
  - Support for cross-asset and pairs trading strategies
  - Portfolio construction and rebalancing algorithms
  - Currency hedging strategies
  - Commodity and fixed-income strategy support

- **Strategy Marketplace**: 
  - Platform for sharing and discovering strategies
  - Strategy rating and review system
  - Monetization framework for strategy creators
  - Community-driven strategy development

- **Advanced Backtesting**: 
  - Monte Carlo simulations for robustness testing
  - Custom benchmark comparisons
  - Attribution analysis (alpha vs. beta)
  - Regime-based backtesting

- **Social Trading Features**: 
  - Copy trading functionality
  - Strategy following and mirroring
  - Leaderboards and performance rankings
  - Social sentiment integration

- **Alternative Data Integration**: 
  - News sentiment analysis and scoring
  - Social media signal extraction
  - Economic calendar integration
  - Satellite and alternative data sources

### Long-term (6+ months)
- **Quantitative Research Platform**: 
  - Advanced statistical analysis tools using pandas/numpy (Python) or ndarray/polars (Rust)
  - Factor research and backtesting
  - Risk model development
  - Academic research collaboration tools

- **Strategy Composition Framework**: 
  - Meta-strategies combining multiple sub-strategies
  - Dynamic strategy allocation based on market regimes
  - Ensemble methods for signal aggregation
  - Strategy diversification optimization

- **Institutional Features**: 
  - Multi-client portfolio management
  - Prime brokerage integration
  - Institutional reporting and analytics
  - Custom fee structures and billing

### Technical Improvements
- **Performance Optimization**: 
  - Strategy execution speed improvements (sub-millisecond latency)
  - Memory usage optimization for large datasets
  - Database query optimization and indexing
  - Caching strategies for frequently accessed data
  - Rust async optimizations and Python asyncio enhancements

- **Scalability Enhancements**: 
  - Horizontal scaling for multiple strategy instances
  - Load balancing and auto-scaling capabilities
  - Distributed backtesting across multiple nodes
  - Event-driven architecture implementation

- **Security Enhancements**: 
  - Advanced authentication and authorization (OAuth2, SAML)
  - End-to-end encryption for sensitive data
  - Security audit logging and monitoring
  - Penetration testing and vulnerability assessments

- **Cloud Native Architecture**: 
  - Auto-scaling based on demand
  - Multi-cloud deployment support

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with appropriate tests
4. Ensure all tests pass (`pytest` or `cargo test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style and Standards

**Python:**
- Use Python 3.9+ features
- Follow PEP 8 style guide
- Use type hints throughout the codebase
- Format code with Black
- Lint with flake8/ruff
- Write comprehensive tests with pytest
- Update documentation for any new features

**Rust:**
- Follow Rust style guidelines (rustfmt)
- Use clippy for linting
- Write comprehensive tests and documentation
- Ensure code compiles without warnings
- Update API documentation for changes

## 🆘 Support

### Getting Help
- **Issues**: Create an issue in the repository for bug reports or feature requests
