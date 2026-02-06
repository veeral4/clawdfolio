# Portfolio Monitor

[![PyPI version](https://badge.fury.io/py/portfolio-monitor.svg)](https://badge.fury.io/py/portfolio-monitor)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Multi-broker portfolio monitoring with professional risk analytics.**

A comprehensive Python library and CLI tool for monitoring investment portfolios across multiple brokers, calculating risk metrics, and generating intelligent alerts.

## Features

- **Multi-Broker Support**: Aggregate portfolios from Longport (Longbridge), Moomoo/Futu, or demo mode
- **Risk Analytics**: Volatility, Beta, Sharpe Ratio, Value at Risk, Max Drawdown
- **Technical Analysis**: RSI, SMA, EMA, Bollinger Bands, MACD
- **Concentration Analysis**: HHI index, sector exposure, correlation warnings
- **Smart Alerts**: Price movement alerts, RSI extremes, P&L thresholds
- **Earnings Calendar**: Track upcoming earnings for portfolio holdings
- **DCA Analysis**: Dollar-cost averaging signals and performance tracking

## Installation

```bash
# Basic installation
pip install portfolio-monitor

# With Longport broker support
pip install portfolio-monitor[longport]

# With Moomoo/Futu broker support
pip install portfolio-monitor[futu]

# All brokers
pip install portfolio-monitor[all]

# Development dependencies
pip install portfolio-monitor[dev]
```

## Quick Start

### CLI Usage

```bash
# Show portfolio summary (uses demo broker by default)
portfolio-monitor summary

# Use specific broker
portfolio-monitor --broker longport summary

# Get real-time quotes
portfolio-monitor quotes AAPL MSFT NVDA

# Show risk metrics
portfolio-monitor risk

# Check alerts
portfolio-monitor alerts

# View upcoming earnings
portfolio-monitor earnings

# DCA analysis
portfolio-monitor dca AAPL --months 12 --amount 1000

# Output as JSON
portfolio-monitor --output json summary
```

### Python API

```python
from portfolio_monitor import Config, load_config
from portfolio_monitor.brokers import get_broker
from portfolio_monitor.analysis import analyze_risk, calculate_concentration
from portfolio_monitor.monitors import PriceMonitor, EarningsMonitor

# Load configuration
config = load_config()

# Connect to broker
broker = get_broker("demo")  # or "longport", "futu"
broker.connect()

# Get portfolio
portfolio = broker.get_portfolio()
print(f"Net Assets: ${portfolio.net_assets:,.2f}")
print(f"Day P&L: ${portfolio.day_pnl:,.2f}")

# Analyze risk
metrics = analyze_risk(portfolio)
print(f"Volatility: {metrics.volatility_annualized*100:.1f}%")
print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
print(f"Beta (SPY): {metrics.beta_spy:.2f}")

# Check for alerts
price_monitor = PriceMonitor()
alerts = price_monitor.check_portfolio(portfolio)
for alert in alerts:
    print(alert)

# Clean up
broker.disconnect()
```

## Configuration

Create `config.yaml` in your working directory:

```yaml
brokers:
  longport:
    enabled: true
  futu:
    enabled: true
    extra:
      host: "127.0.0.1"
      port: 11111
  demo:
    enabled: true

alerts:
  pnl_trigger: 500.0
  pnl_step: 500.0
  rsi_high: 80
  rsi_low: 20
  single_stock_threshold_top10: 0.05
  single_stock_threshold_other: 0.10

currency: USD
timezone: America/New_York
output_format: console
```

### Environment Variables

**Longport:**
```bash
export LONGPORT_APP_KEY=your_app_key
export LONGPORT_APP_SECRET=your_app_secret
export LONGPORT_ACCESS_TOKEN=your_access_token
export LONGPORT_REGION=us
```

**Moomoo/Futu:**
- Requires moomoo OpenD running locally (default: `127.0.0.1:11111`)

## Supported Brokers

| Broker | Status | Notes |
|--------|--------|-------|
| Demo | Built-in | Simulated portfolio for testing |
| Longport | Optional | Requires `longport` SDK |
| Moomoo/Futu | Optional | Requires OpenD running locally |

## Risk Metrics

| Metric | Description |
|--------|-------------|
| Volatility | 20-day and 60-day annualized volatility |
| Beta | Correlation with SPY and QQQ benchmarks |
| Sharpe Ratio | Risk-adjusted return measure |
| VaR | Value at Risk at 95% and 99% confidence |
| Max Drawdown | Largest peak-to-trough decline |
| HHI | Herfindahl-Hirschman concentration index |

## Project Structure

```
portfolio-monitor/
├── src/portfolio_monitor/
│   ├── core/           # Core types and config
│   ├── brokers/        # Broker integrations
│   ├── market/         # Market data utilities
│   ├── analysis/       # Risk and technical analysis
│   ├── monitors/       # Alert monitors
│   ├── strategies/     # Investment strategies
│   ├── output/         # Output formatters
│   └── cli/            # Command-line interface
├── tests/              # Unit tests
├── examples/           # Usage examples
├── SKILL.md            # Clawdbot skill definition
└── pyproject.toml      # Package configuration
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) for market data
- [Longport](https://longportapp.com/) for broker API
- [Futu](https://www.futunn.com/) for Moomoo integration
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
